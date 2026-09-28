"""S02: close-up of the entangled pair. Both particles swirl blue and gold: undecided."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SID = "s02_pair"
info = shot_info(SID)
N = info["frames"]
res = (1920, 1080)
if "--half" in sys.argv:
    res = (960, 540)
sc = new_scene(res, samples=8, frames=N, motion_blur=False, exposure=0.0)
world_sky(strength=0.9, rot_z=2.2, rot_x=0.3)

A = Orb("A", seed=0.0)
B = Orb("B", seed=11.3)
link_ = Link("Link", radius=0.0024, strength=1.3)
focus = empty("Focus")
cam = camera((0, -5.2, 0.35), (0, 0, 0), lens=55, fstop=2.2, focus_obj=focus)
specks = speck_field()

t_think = word_time(SID, "think")
t_neither = word_time(SID, "neither")
t_each2 = word_time(SID, "each", 1)
T = N / FPS


def update(t):
    # pair slowly orbiting its centre, separation 2.3
    ang = 0.35 + t * 0.12
    sep = 1.15
    ca = Vector((-sep * math.cos(ang), -sep * math.sin(ang) * 0.35, 0.05 * math.sin(t * 0.9)))
    A.obj.location = ca
    B.obj.location = -ca + Vector((0, 0, 0.05 * math.sin(t * 0.9 + 1)))
    tg = info['start'] / FPS + t
    A.set(tg)
    B.set(tg)
    link_.update(A.obj.location, B.obj.location, tg, amp=0.05, turns=5, strength=1.3)
    # camera: slow arc, then push toward particle A for "neither has a colour yet"
    push = ramp(t, t_neither - 0.6, t_each2 + 1.2)
    base_ang = -0.30 + t * 0.035
    r = lerp(5.4, 2.1, push)
    tgt = lerp(Vector((0, 0, 0)), A.obj.location, push)
    cam.location = tgt + Vector((math.sin(base_ang) * r, -math.cos(base_ang) * r, lerp(0.45, 0.18, push)))
    aim(cam, tgt)
    cam.data.lens = lerp(50, 70, push)
    focus.location = tgt
    cam.data.dof.aperture_fstop = lerp(2.8, 1.6, push)
    update_specks(specks, tg)


run(SID, update)
