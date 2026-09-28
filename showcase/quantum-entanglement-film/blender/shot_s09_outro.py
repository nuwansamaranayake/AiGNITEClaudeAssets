"""S09: 'Two particles. Far apart. Still acting as one.' Both pulse in perfect sync; title follows."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SID = "s09_outro"
info = shot_info(SID)
N = info["frames"]
T = N / FPS
sc = new_scene((1920, 1080), samples=8, frames=N, motion_blur=False)
world_sky(strength=0.95, rot_z=4.6, rot_x=-0.15)
A = Orb("A", seed=0.0)
B = Orb("B", seed=11.3)
link_ = Link("Link", n=520, radius=0.0026, strength=1.3)
specks = speck_field(n=200, seed=9, xr=(-9, 9), yr=(-6, 14), zr=(-3, 3))
focus = empty("Focus")
cam = camera((0, -8, 0.5), (0, 0, 0), lens=40, fstop=5.6, focus_obj=focus)
t_still = word_time(SID, "still")
t_one = word_time(SID, "one")
t_that = word_time(SID, "that")
TG0 = info["start"] / FPS


def beat(t, t0):
    return math.exp(-((t - t0) / 0.13) ** 2)


def update(t):
    tg = TG0 + t
    A.obj.location = Vector((-4.2, 0.6, 0.05 * math.sin(t * 0.8)))
    B.obj.location = Vector((4.2, 0.6, -0.05 * math.sin(t * 0.8)))
    # two synchronized heartbeats on "still acting as one"
    p = beat(t, t_still + 0.1) + beat(t, t_one + 0.05)
    A.set(tg, energy=1.3 + 2.2 * p)
    B.set(tg, energy=1.3 + 2.2 * p)
    fade = 1 - 0.35 * smoother((t - t_that) / 1.5)
    link_.update(A.obj.location, B.obj.location, tg, amp=0.045, turns=5, strength=(1.3 + 3.0 * p) * fade)
    k = smoother(t / T)
    cam.location = Vector((lerp(-0.4, 0.4, k), lerp(-9.5, -13.5, k), lerp(0.3, 1.6, k)))
    aim(cam, Vector((0, 0.6, lerp(0.0, 0.45, k))))
    focus.location = (0, 0.6, 0)
    update_specks(specks, tg)


run(SID, update)
