"""Phrase-level burned-in captions from narration text + TTS word boundaries -> captions.json."""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
TL = json.loads((ROOT / "timeline.json").read_text())
NAR = {s["id"]: s["text"] for s in json.loads((ROOT / "narration.json").read_text())["shots"]}
FPS = TL["fps"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
out = []
for shot in TL["shots"]:
    base = shot["start"] / FPS
    words = NAR[shot["id"]].split()
    toks = shot["words"]
    # align every text word to a boundary token (a token can hold several words, e.g. "In 2017")
    times, ti, acc = [], 0, ""
    for wd in words:
        target = norm(toks[ti]["text"]) if ti < len(toks) else ""
        times.append((toks[min(ti, len(toks) - 1)]["t"], toks[min(ti, len(toks) - 1)]["t"] + toks[min(ti, len(toks) - 1)]["d"]))
        acc += norm(wd)
        if acc == target or len(acc) >= len(target):
            ti += 1
            acc = ""
    # sentences, then commas, then balanced splits so no line exceeds 8 words or ends in an orphan
    sentences, cur = [], []
    for i, wd in enumerate(words):
        cur.append(i)
        if wd.endswith((".", "?", "!")):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    phrases = []
    for sen in sentences:
        if len(sen) <= 8:
            phrases.append(sen)
            continue
        parts, cur = [], []
        for i in sen:
            cur.append(i)
            if words[i].endswith(",") and len(cur) >= 3:
                parts.append(cur)
                cur = []
        if cur:
            if parts and len(cur) < 3:
                parts[-1] += cur
            else:
                parts.append(cur)
        for part in parts:
            k = -(-len(part) // 8)
            size = -(-len(part) // k)
            for j in range(0, len(part), size):
                phrases.append(part[j:j + size])
    for ph in phrases:
        s = base + times[ph[0]][0]
        e = base + times[ph[-1]][1] + 0.3
        out.append({"start": round(s, 3), "end": round(e, 3), "text": " ".join(words[i] for i in ph)})
for a, b in zip(out, out[1:]):
    a["end"] = min(a["end"], b["start"] - 0.04)
(ROOT / "captions.json").write_text(json.dumps(out, indent=1))
print(len(out), "captions")
for c in out[:6]:
    print(c)
