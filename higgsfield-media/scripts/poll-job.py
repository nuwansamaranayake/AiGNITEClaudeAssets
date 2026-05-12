"""
Polling helper for asynchronous Higgsfield video jobs.

This module is a library, not a standalone script. The orchestrating Claude
session imports `poll_job` and uses it to wait on a video generation job
without burning the session's attention budget on busy-wait loops.

Usage from Python:

    from poll_job import poll_job

    url = poll_job(job_handle="abc123", check_status_fn=mcp_get_status, max_seconds=300)

If the job stays in 'processing' past max_seconds, raises TimeoutError with
the job handle so the caller can surface it to the user.

Usage from PowerShell or another shell:

    python poll-job.py --job-handle abc123 --dry-run

The CLI form is for diagnostic use only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Callable


@dataclass
class PollResult:
    job_handle: str
    status: str
    url: str | None
    error: str | None
    elapsed_seconds: float


def poll_job(
    job_handle: str,
    check_status_fn: Callable[[str], dict],
    poll_interval_seconds: int = 8,
    max_seconds: int = 300,
) -> PollResult:
    """Poll a Higgsfield video job until completion or timeout.

    Parameters
    ----------
    job_handle : str
        The handle returned by the video generation call.
    check_status_fn : callable
        A function that takes a job handle and returns a dict with at least
        the keys 'status' (one of 'processing', 'completed', 'failed') and
        optionally 'url' (on completed) or 'error' (on failed).
    poll_interval_seconds : int
        Sleep between polls. Default 8 seconds.
    max_seconds : int
        Cap polling at this many seconds. Default 300 (5 minutes).

    Returns
    -------
    PollResult

    Raises
    ------
    TimeoutError
        If the job stays in 'processing' past max_seconds.
    """
    start = time.monotonic()
    while True:
        elapsed = time.monotonic() - start
        if elapsed > max_seconds:
            raise TimeoutError(
                f"Job {job_handle} still processing after {max_seconds} seconds. "
                f"Surface the handle to the user and stop polling."
            )

        response = check_status_fn(job_handle)
        status = response.get("status", "unknown")

        if status == "completed":
            return PollResult(
                job_handle=job_handle,
                status=status,
                url=response.get("url"),
                error=None,
                elapsed_seconds=elapsed,
            )

        if status == "failed":
            return PollResult(
                job_handle=job_handle,
                status=status,
                url=None,
                error=response.get("error", "unknown error"),
                elapsed_seconds=elapsed,
            )

        # status is 'processing' or unknown; sleep and retry
        time.sleep(poll_interval_seconds)


def _diagnostic_cli() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostic CLI for the higgsfield-media polling helper."
    )
    parser.add_argument("--job-handle", required=True, help="Job handle to poll")
    parser.add_argument(
        "--max-seconds", type=int, default=300, help="Polling cap in seconds"
    )
    parser.add_argument(
        "--interval", type=int, default=8, help="Poll interval in seconds"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without polling",
    )
    args = parser.parse_args()

    if args.dry_run:
        print(
            f"DRY  would poll job {args.job_handle} every {args.interval}s "
            f"up to {args.max_seconds}s."
        )
        print(
            "     This CLI is diagnostic only. The skill imports poll_job() as a library."
        )
        return 0

    print(
        "This CLI does not call the MCP directly. Use it from within Python where "
        "you have a check_status_fn that wraps the MCP tool call."
    )
    print(
        "Example:\n"
        "    from poll_job import poll_job\n"
        "    result = poll_job('abc123', mcp_get_status_fn)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(_diagnostic_cli())
