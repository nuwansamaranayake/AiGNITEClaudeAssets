"""Objective gates for the finished film. Exit code 0 only if every gate passes.
usage: qa_video.py <film.mp4>"""
import json, re, subprocess, sys, pathlib
import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
src = sys.argv[1]
EV = json.loads((ROOT / "events.json").read_text())
want_dur = EV["total_frames"] / EV["fps"]
res = {}


def run(args):
    return subprocess.run([FF, "-hide_banner", "-nostats"] + args, capture_output=True, text=True).stderr


info = run(["-i", src])
v = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?, ([\d.]+) fps", info)
a = re.search(r"Audio: (\w+).*?, (\d+) Hz, (\w+)", info)
d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))
res["video"] = {"codec": v.group(1), "size": f"{v.group(2)}x{v.group(3)}", "fps": float(v.group(4))}
res["audio"] = {"codec": a.group(1) if a else None, "rate": int(a.group(2)) if a else None, "layout": a.group(3) if a else None}
res["duration"] = round(dur, 2)
ebu = run(["-i", src, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", ebu)[-1])
TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", ebu)[-1])
res["loudness_lufs"], res["true_peak_dbfs"] = I, TP
blk = run(["-i", src, "-vf", "blackdetect=d=0.6:pix_th=0.04", "-an", "-f", "null", "-"])
blacks = [(float(s), float(e)) for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", blk)]
frz = run(["-i", src, "-vf", "freezedetect=n=0.0008:d=1.5", "-an", "-f", "null", "-"])
freezes = re.findall(r"freeze_start: ([\d.]+)", frz)
res["black_segments"] = blacks
res["freeze_starts"] = freezes

gates = {
    "resolution 1920x1080": res["video"]["size"] == "1920x1080",
    "fps 24": abs(res["video"]["fps"] - 24) < 0.01,
    "h264 video": res["video"]["codec"] == "h264",
    "aac stereo audio": res["audio"]["codec"] == "aac" and res["audio"]["layout"] == "stereo",
    f"duration {want_dur:.2f}s +-0.25": abs(dur - want_dur) <= 0.25,
    "loudness -16 +-1 LUFS": abs(I + 16) <= 1.0,
    "true peak <= -1.0 dBFS": TP <= -1.0,
    # the only black allowed is the fade-in / fade-out at the ends
    "no black gaps mid-film": all(s < 0.8 or e > dur - 2.0 for s, e in blacks),
    "no frozen picture > 1.5s": len(freezes) == 0,
}
res["gates"] = gates
print(json.dumps(res, indent=1))
bad = [k for k, ok in gates.items() if not ok]
print("PASS" if not bad else "FAIL: " + "; ".join(bad))
sys.exit(1 if bad else 0)
