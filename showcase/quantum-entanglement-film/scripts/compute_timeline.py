"""Shot lengths from narration timings plus pads. Shared by Blender and Remotion."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
FPS = 24
PADS = {"s01_birth": (2.2, 0.7), "s02_pair": (0.4, 0.6), "s03_apart": (0.3, 0.8), "s04_measure": (0.5, 1.0),
        "s05_repeat": (0.4, 0.9), "s06_boxes": (0.5, 0.9), "s07_nosignal": (0.4, 0.9), "s08_real": (0.5, 0.9),
        "s09_outro": (0.4, 3.9)}
t = json.loads((ROOT / "audio" / "timings.json").read_text())
out, start = {"fps": FPS, "shots": []}, 0
for k, (pre, post) in PADS.items():
    n = round((pre + t[k]["duration"] + post) * FPS)
    words = [{"text": w["text"], "t": round(pre + w["t"], 3), "d": w["d"]} for w in t[k]["words"]]
    out["shots"].append({"id": k, "pre": pre, "frames": n, "start": start, "voice": t[k]["duration"], "words": words})
    start += n
out["total_frames"] = start
(ROOT / "timeline.json").write_text(json.dumps(out, indent=1))
print({s["id"]: s["frames"] for s in out["shots"]}, "total", start, "=", round(start / FPS, 2), "s")
