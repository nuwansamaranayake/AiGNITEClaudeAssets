"""Particle sprites over black for the 'repeat it many times' sequence (composited with screen blend).
usage: SPR=undecided|blue|gold python shot_spr.py"""
import os, sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

kind = os.environ.get("SPR", "undecided")
SID = f"spr_{kind}"
N = 144 if kind == "undecided" else 72
sc = new_scene((540, 540), samples=12, frames=N, motion_blur=False)
w = bpy.data.worlds.new("Black")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
orb = Orb("P", seed={"undecided": 3.3, "blue": 5.1, "gold": 8.7}[kind])
burst = Burst("Burst")
color = GOLD if kind == "gold" else BLUE
wave = Shockwave("Wave", color, thickness=0.006)
cam = camera((0, -3.2, 0.0), (0, 0, 0), lens=50)
TC = 12 / FPS


def update(t):
    if kind == "undecided":
        orb.set(t)
        return
    x = t - TC
    if x < 0:
        orb.set(t)
        burst.set((0, 0, 0), 0.1, 0)
    else:
        # milder, shorter flash than the hero measurement: these repeat every ~0.4 s
        orb.set(t, collapse=smoother(x / 0.18), target=color, energy=1.5, flash=math.exp(-x / 0.05) * 0.45)
        burst.set((0, 0, 0), 0.25 + 0.3 * ease_out_expo(x / 0.2), 5 * math.exp(-x / 0.05), tuple(lerp((1, 1, 1), color, 0.5)))
    wave.update((0, 0, 0), t, TC, radius=0.4, reach=0.9, dur=0.4, strength=6, normal=(0, -1, 0.2), color=color)


run(SID, update)
