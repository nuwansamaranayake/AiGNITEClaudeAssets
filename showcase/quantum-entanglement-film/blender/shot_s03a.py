"""S03a: 'Now we send them far apart. One meter.' The pair flies apart, camera pulls back."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SHOT = "s03_apart"
info = shot_info(SHOT)
T0, T1 = 0.0, 3.35                      # shot-local seconds covered (handle after the 3.05 cut)
N = round((T1 - T0) * FPS)
sc = new_scene((1920, 1080), samples=8, frames=N, motion_blur=True)
world_sky(strength=0.9, rot_z=2.9, rot_x=0.2)
A = Orb("A", seed=0.0)
B = Orb("B", seed=11.3)
link_ = Link("Link", n=360, radius=0.0026, strength=1.3)
specks = speck_field(n=170, seed=5, yr=(-14, 12))
focus = empty("Focus")
cam = camera((0.6, -7.0, 0.7), (0, 0, 0), lens=45, fstop=4.0, focus_obj=focus)
t_apart = word_time(SHOT, "apart")
t_meter = word_time(SHOT, "meter")
TG0 = info["start"] / FPS


def update(t):
    tg = TG0 + t
    # separation: 2.3 at rest, launching on "apart", about 7 by "one meter"
    k = smoother((t - (t_apart - 0.45)) / 1.6)
    half = 1.15 + 2.4 * k + 0.25 * max(0, t - (t_apart + 1.15))
    wob = 0.05 * math.sin(t * 0.9)
    A.obj.location = Vector((-half, 0.0, wob))
    B.obj.location = Vector((half, 0.12 * k, -wob))
    A.set(tg)
    B.set(tg)
    link_.update(A.obj.location, B.obj.location, tg, amp=lerp(0.05, 0.035, k), turns=5, strength=1.3)
    # camera pulls back to hold both in frame
    d = lerp(6.6, 13.5, smoother((t - (t_apart - 0.5)) / 2.2))
    cam.location = Vector((0.6 + 0.3 * t, -d, 0.7 + 0.08 * d))
    aim(cam, Vector((0.1 * t, 0, 0)))
    focus.location = (0, 0, 0)
    update_specks(specks, tg)


run("s03a", update, time_map=lambda f: T0 + (f - 1) / FPS)
