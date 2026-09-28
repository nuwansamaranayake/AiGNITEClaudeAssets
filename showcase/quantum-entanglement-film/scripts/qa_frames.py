"""Frames + transcript for the beginner comprehension test.
Extracts one frame every STEP seconds (960x540) and a timestamped transcript of the narration."""
import json, subprocess, sys, pathlib
import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
src, out = sys.argv[1], pathlib.Path(sys.argv[2])
STEP = float(sys.argv[3]) if len(sys.argv) > 3 else 2.5
out.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([FF, "-v", "error", "-y", "-i", src, "-vf", f"fps=1/{STEP},scale=960:540", "-q:v", "3", str(out / "f_%03d.jpg")], check=True)
frames = sorted(out.glob("f_*.jpg"))
for i, f in enumerate(frames):
    t = i * STEP + STEP / 2
    f.rename(out / f"frame_{i:03d}_t{t:06.1f}s.jpg")
caps = json.loads((ROOT / "captions.json").read_text())
(out / "transcript.txt").write_text("\n".join(f"[{c['start']:6.1f}s] {c['text']}" for c in caps))
print(len(frames), "frames to", out)
