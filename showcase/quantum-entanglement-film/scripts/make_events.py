"""Single source of truth for every timed beat (shot-local seconds and absolute seconds).
Read by the Remotion overlays and by the soundtrack builder."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
TL = json.loads((ROOT / "timeline.json").read_text())
FPS = TL["fps"]
S = {s["id"]: s for s in TL["shots"]}


def w(sid, word, n=0):
    hits = [x["t"] for x in S[sid]["words"] if x["text"].lower().strip(".,?") == word.lower()]
    return hits[n]


def absT(sid, t):
    return round(S[sid]["start"] / FPS + t, 4)


ev = {"fps": FPS, "total_frames": TL["total_frames"], "shots": {k: {"start": v["start"], "frames": v["frames"]} for k, v in S.items()}}

# S01 birth
t_born = w("s01_birth", "together") - 0.12
ev["s01"] = {"t_in": t_born - 0.75, "t_born": t_born}

# S02 labels
ev["s02"] = {"entangled": w("s02_pair", "entangled"), "blue": w("s02_pair", "blue"), "gold": w("s02_pair", "gold"),
             "spin": w("s02_pair", "spin"), "neither": w("s02_pair", "neither"), "undecided": w("s02_pair", "undecided")}

# S03 cuts
ev["s03"] = {"cut_ab": 3.05, "cut_bc": 4.5, "a_from": 0.0, "b_from": 2.85, "c_from": 4.3,
             "apart": w("s03_apart", "apart"), "meter": w("s03_apart", "meter"), "earth": w("s03_apart", "earth"),
             "galaxy": w("s03_apart", "galaxy"), "link": w("s03_apart", "link")}

# S04 measurement with slow-motion replay (must match blender/s04_common.py)
T_C = w("s04_measure", "blue") - 0.12
R0, R1 = 7.0, 11.9
S0, S1 = T_C - 1.3, T_C + 0.3
rate = (S1 - S0) / (R1 - R0)
ev["s04"] = {"T_C": T_C, "R0": R0, "R1": R1, "S0": S0, "S1": S1, "replay_collapse": R0 + (T_C - S0) / rate,
             "measures": w("s04_measure", "measures"), "gold": w("s04_measure", "gold"),
             "always": w("s04_measure", "always"), "chance": w("s04_measure", "chance")}

# S05 repeated trials: results look random on each side, always opposite across
L = ["B", "G", "G", "B", "G", "B", "B", "G", "B", "G"]
collapse = [0.95, 1.8, 2.5, 3.05, 3.55, 4.0, 4.4, 4.8, 5.2, 5.6]
ev["s05"] = {"trials": [{"t": t, "left": l, "right": "G" if l == "B" else "B"} for t, l in zip(collapse, L)],
             "each": w("s05_repeat", "each"), "random": w("s05_repeat", "random"), "flips": w("s05_repeat", "flips"),
             "compare": w("s05_repeat", "compare"), "every": w("s05_repeat", "every"), "opposite": w("s05_repeat", "opposite"),
             "every2": w("s05_repeat", "every", 1)}

# S06 boxes
ev["s06"] = {"blue": w("s06_boxes", "blue"), "gold": w("s06_boxes", "gold"), "no": w("s06_boxes", "no"),
             "set": w("s06_boxes", "set"), "start": w("s06_boxes", "start"), "entangled": w("s06_boxes", "entangled"),
             "hidden": w("s06_boxes", "hidden"), "nobel": w("s06_boxes", "nobel"), "that": w("s06_boxes", "that", 1)}

# S07 no faster-than-light messages
ev["s07"] = {"messages": w("s07_nosignal", "messages"), "no": w("s07_nosignal", "no"), "each": w("s07_nosignal", "each"),
             "random": w("s07_nosignal", "random"), "pattern": w("s07_nosignal", "pattern"), "compare": w("s07_nosignal", "compare"),
             "notes": w("s07_nosignal", "notes", 1), "travel": w("s07_nosignal", "travel"), "light": w("s07_nosignal", "light", 1)}
ev["s07"]["send_t"] = ev["s07"]["compare"] - 0.2
ev["s07"]["arrive_t"] = S["s07_nosignal"]["frames"] / FPS - 1.6

# S08 satellite (must match blender/shot_s08_real.py)
t_sent = w("s08_real", "sent")
ev["s08"] = {"real": w("s08_real", "real"), "year": w("s08_real", "in 2017"), "satellite": w("s08_real", "satellite"),
             "sent": t_sent, "two": w("s08_real", "two"), "kilometers": w("s08_real", "kilometers"),
             "today": w("s08_real", "today"), "computers": w("s08_real", "computers"), "secure": w("s08_real", "secure"),
             "arrivals": [round(t_sent + 0.2 + m * 0.75 + 0.55, 3) for m in range(40) if t_sent + 0.75 + m * 0.75 < S["s08_real"]["frames"] / FPS]}

# S09 outro
ev["s09"] = {"beats": [w("s09_outro", "still") + 0.1, w("s09_outro", "one") + 0.05], "that": w("s09_outro", "that"),
             "entanglement": w("s09_outro", "entanglement")}

(ROOT / "events.json").write_text(json.dumps(ev, indent=1))
print(json.dumps({k: v for k, v in ev.items() if k.startswith("s0")}, indent=0)[:1500])
