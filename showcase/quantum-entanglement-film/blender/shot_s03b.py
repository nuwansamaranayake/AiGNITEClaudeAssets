"""S03b: 'Across the Earth.' B sweeps over the planet to the far limb; the link follows the curve."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SHOT = "s03_apart"
info = shot_info(SHOT)
T0, T1 = 2.85, 4.75
N = round((T1 - T0) * FPS)
sc = new_scene((1920, 1080), samples=10, frames=N, motion_blur=True)
world_sky(strength=0.7, rot_z=1.3, rot_x=0.1)
sun_dir = Vector((0.75, -0.45, 0.35))
sun(sun_dir, strength=3.5)
rig, body, clouds, atmo = earth(radius=1.0, sun_dir=sun_dir, night_strength=2.0, seg=256)
rig.rotation_euler = (0.25, 0, math.radians(-25))
A = Orb("A", radius=0.05, seed=0.0)
B = Orb("B", radius=0.05, seed=11.3)
link_ = Link("Link", n=360, radius=0.0022, strength=1.6)
cam = camera((0.0, -3.9, 0.9), (0, 0, 0.05), lens=40)
TG0 = info["start"] / FPS
RR = 1.07
dA = Vector((-0.86, -0.42, 0.28)).normalized()
dB = Vector((0.88, -0.36, -0.12)).normalized()


def slerp(a, b, f):
    om = math.acos(max(-1, min(1, a.dot(b))))
    if om < 1e-5:
        return a.copy()
    return (a * math.sin((1 - f) * om) + b * math.sin(f * om)) / math.sin(om)


def update(t):
    tl = t - T0
    tg = TG0 + t
    rig.rotation_euler = (0.25, 0, math.radians(-25) + 0.035 * tl)
    clouds.rotation_euler = (0, 0, 0.01 * tl)
    f = ease_out_expo(clamp((tl - 0.05) / 0.9))
    arc_lift = 0.10
    A.obj.location = dA * RR

    def path(s_):
        d = slerp(dA, dB, s_ * f)
        return d * (RR + arc_lift * math.sin(math.pi * s_) * f)
    B.obj.location = path(1.0)
    A.set(tg, energy=2.2)
    B.set(tg, energy=2.2)
    link_.update_curve(path, tg, amp=0.0045, turns=28 * max(f, 0.05), strength=2.0)
    cam.location = Vector((0.1 * tl, -3.9 + 0.12 * tl, 0.9))
    aim(cam, Vector((0, 0, 0.05)))


run("s03b", update, time_map=lambda f: T0 + (f - 1) / FPS)
