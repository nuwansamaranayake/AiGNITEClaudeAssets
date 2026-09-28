"""Generate per-shot narration with edge-tts and record word-boundary timings.
Writes audio/<id>.mp3 and audio/timings.json {id: {duration, words:[{t,d,text}]}}."""
import asyncio, json, subprocess, sys, pathlib
import edge_tts, imageio_ffmpeg
ROOT = pathlib.Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "narration.json").read_text())
FF = imageio_ffmpeg.get_ffmpeg_exe()

def duration(path):
    out = subprocess.run([FF, "-i", str(path), "-f", "null", "-"], capture_output=True, text=True).stderr
    t = [l for l in out.splitlines() if "time=" in l][-1]
    hh, mm, ss = t.split("time=")[1].split()[0].split(":")
    return int(hh) * 3600 + int(mm) * 60 + float(ss)

async def one(shot):
    c = edge_tts.Communicate(shot["text"], cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"], boundary="WordBoundary")
    words, audio = [], bytearray()
    async for ch in c.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            words.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "text": ch["text"]})
    out = ROOT / "audio" / f"{shot['id']}.mp3"
    out.write_bytes(audio)
    return shot["id"], {"duration": duration(out), "words": words, "text": shot["text"]}

async def main():
    res = {}
    for s in cfg["shots"]:
        k, v = await one(s)
        if not v["words"] or v["duration"] < 1:
            sys.exit(f"TTS failed for {k}")
        res[k] = v
        print(f"{k}: {v['duration']:.2f}s, {len(v['words'])} words")
    (ROOT / "audio" / "timings.json").write_text(json.dumps(res, indent=1))
    print("TOTAL", round(sum(v["duration"] for v in res.values()), 2))
asyncio.run(main())
