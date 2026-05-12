"""
Batch generation orchestrator for higgsfield-media.

This module coordinates a multi-asset Higgsfield batch:

- Chunks the batch to respect Plus parallel-job caps (8 image, 6 video).
- Tracks each generation in the project manifest.
- Updates the credit ledger as each generation completes.
- Writes the manifest atomically (temp file plus rename) so a mid-batch
  crash leaves a readable record.

Like poll-job.py, this is a library the orchestrating Claude session
imports. The session supplies the function that actually calls the
Higgsfield MCP tool. This file owns the policy: chunking, manifest
discipline, credit accounting, error handling.

Usage from Python:

    from batch_generate import BatchOrchestrator, BatchItem

    orchestrator = BatchOrchestrator(
        project_dir="output/2026-05-12/floodpulse-demo-may",
        image_call_fn=mcp_generate_image,
        video_call_fn=mcp_generate_video,
    )

    items = [
        BatchItem(type="image", model="nano-banana-pro", prompt="...", params={...}),
        BatchItem(type="video", model="kling-3-0",       prompt="...", params={...}),
    ]

    orchestrator.run(items)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

IMAGE_PARALLEL_CAP = 8
VIDEO_PARALLEL_CAP = 6


@dataclass
class BatchItem:
    type: str  # 'image' or 'video'
    model: str
    prompt: str
    params: dict = field(default_factory=dict)
    expected_credits: int = 0


@dataclass
class BatchResult:
    seq: int
    type: str
    model: str
    prompt: str
    params: dict
    credits: int
    url: str | None
    local_path: str | None
    duration_seconds: float
    status: str
    error: str | None = None


class BatchOrchestrator:
    def __init__(
        self,
        project_dir: str | Path,
        image_call_fn: Callable[[str, dict], dict],
        video_call_fn: Callable[[str, dict], dict],
        balance_before: int = 0,
    ) -> None:
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "images").mkdir(exist_ok=True)
        (self.project_dir / "videos").mkdir(exist_ok=True)

        self.image_call_fn = image_call_fn
        self.video_call_fn = video_call_fn

        self.manifest_path = self.project_dir / "manifest.json"
        self.manifest_backup_path = self.project_dir / ".manifest.json.backup"
        self.ledger_path = self.project_dir.parent.parent / "credit-ledger.csv"

        self.manifest = self._load_or_init_manifest(balance_before)

    def _load_or_init_manifest(self, balance_before: int) -> dict:
        if self.manifest_path.exists():
            try:
                with self.manifest_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Restore from backup if the main file is corrupt
                if self.manifest_backup_path.exists():
                    shutil.copy2(self.manifest_backup_path, self.manifest_path)
                    with self.manifest_path.open("r", encoding="utf-8") as f:
                        return json.load(f)
                # Fall through to fresh init

        return {
            "project_slug": self.project_dir.name,
            "brief": "",
            "started_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "balance_before": balance_before,
            "balance_after": balance_before,
            "characters": {},
            "generations": [],
            "pending_jobs": [],
            "totals": {
                "image_count": 0,
                "video_count": 0,
                "credits_spent": 0,
                "credits_free_pool_used": 0,
            },
        }

    def _write_manifest(self) -> None:
        # Atomic write: backup, temp file, rename
        if self.manifest_path.exists():
            shutil.copy2(self.manifest_path, self.manifest_backup_path)
        tmp_path = self.manifest_path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)
        tmp_path.replace(self.manifest_path)

    def _append_ledger(self, result: BatchResult) -> None:
        is_new_file = not self.ledger_path.exists()
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow([
                    "timestamp",
                    "project",
                    "model",
                    "type",
                    "credits",
                    "balance_after",
                    "prompt_hash",
                    "local_path",
                ])
            prompt_hash = hashlib.sha256(result.prompt.encode("utf-8")).hexdigest()[:12]
            writer.writerow([
                datetime.now(timezone.utc).astimezone().isoformat(),
                self.manifest["project_slug"],
                result.model,
                result.type,
                result.credits,
                self.manifest["balance_after"],
                prompt_hash,
                result.local_path or "",
            ])

    def _record(self, result: BatchResult) -> None:
        self.manifest["generations"].append({
            "seq": result.seq,
            "type": result.type,
            "model": result.model,
            "prompt": result.prompt,
            "params": result.params,
            "credits": result.credits,
            "url": result.url,
            "local_path": result.local_path,
            "duration_seconds": result.duration_seconds,
            "status": result.status,
            "error": result.error,
        })
        self.manifest["balance_after"] = max(0, self.manifest["balance_after"] - result.credits)
        if result.type == "image":
            self.manifest["totals"]["image_count"] += 1
        else:
            self.manifest["totals"]["video_count"] += 1
        self.manifest["totals"]["credits_spent"] += result.credits
        self._write_manifest()
        self._append_ledger(result)

    def run(self, items: list[BatchItem]) -> list[BatchResult]:
        results: list[BatchResult] = []
        next_seq = len(self.manifest["generations"]) + 1

        image_items = [i for i in items if i.type == "image"]
        video_items = [i for i in items if i.type == "video"]

        for chunk in self._chunked(image_items, IMAGE_PARALLEL_CAP):
            for item in chunk:
                results.append(self._run_one(item, next_seq))
                next_seq += 1

        for chunk in self._chunked(video_items, VIDEO_PARALLEL_CAP):
            for item in chunk:
                results.append(self._run_one(item, next_seq))
                next_seq += 1

        return results

    def _run_one(self, item: BatchItem, seq: int) -> BatchResult:
        start = time.monotonic()
        try:
            call_fn = self.image_call_fn if item.type == "image" else self.video_call_fn
            response = call_fn(item.model, {"prompt": item.prompt, **item.params})
            elapsed = time.monotonic() - start

            credits = response.get("credits", item.expected_credits)
            url = response.get("url")
            local_path = response.get("local_path")

            if not url:
                raise RuntimeError(f"No URL returned for {item.model}")

            result = BatchResult(
                seq=seq,
                type=item.type,
                model=item.model,
                prompt=item.prompt,
                params=item.params,
                credits=credits,
                url=url,
                local_path=local_path,
                duration_seconds=elapsed,
                status="completed",
            )
        except Exception as e:
            result = BatchResult(
                seq=seq,
                type=item.type,
                model=item.model,
                prompt=item.prompt,
                params=item.params,
                credits=0,
                url=None,
                local_path=None,
                duration_seconds=time.monotonic() - start,
                status="failed",
                error=str(e),
            )
        self._record(result)
        return result

    @staticmethod
    def _chunked(items: list, size: int) -> list[list]:
        return [items[i : i + size] for i in range(0, len(items), size)]


def _diagnostic_cli() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostic CLI for the batch generate orchestrator."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without running.",
    )
    args = parser.parse_args()

    if args.dry_run:
        print(
            "DRY  batch-generate.py is a library. Import BatchOrchestrator from this module."
        )
        print(
            "     Image parallel cap: " + str(IMAGE_PARALLEL_CAP)
            + ". Video parallel cap: " + str(VIDEO_PARALLEL_CAP) + "."
        )
        return 0

    print("This module is a library. See the docstring at the top of the file.")
    return 0


if __name__ == "__main__":
    sys.exit(_diagnostic_cli())
