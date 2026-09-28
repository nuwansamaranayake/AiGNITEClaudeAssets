"""S04 measurement, rendered as two 960x1080 halves for a split screen.
Side A: near Earth, a detector ring closes around particle A; it turns BLUE.
Side B: far across the galaxy, particle B in its own detector turns GOLD at the same instant.
Everything is driven by source time s(t), which includes a slow-motion replay."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SHOT = "s04_measure"
info = shot_info(SHOT)
N = info["frames"]
T_C = word_time(SHOT, "blue") - 0.12          # the collapse instant
R0, R1 = 7.0, 11.9                             # replay window on screen
S0, S1 = T_C - 1.3, T_C + 0.3                  # source window it shows


def s_of_t(t):
    if t < R0:
        return t
    if t < R1:
        return S0 + (t - R0) * (S1 - S0) / (R1 - R0)
    return S1 + (t - R1)


def build(side):
    sid = "s04a" if side == "A" else "s04b"
    sc = new_scene((960, 1080), samples=10, frames=N, motion_blur=True)
    sc.render.motion_blur_shutter = 0.35
    mirror = 1 if side == "A" else -1
    if side == "A":
        world_sky(strength=0.85, rot_z=0.9, rot_x=0.25)
        sun_dir = Vector((0.55, -0.55, 0.45))
        sun(sun_dir, strength=3.2)
        earth(radius=16, loc=(-14, 52, -23), sun_dir=sun_dir, night_strength=1.5, seg=192)
        color, other = BLUE, (6.5, 6.0, 0.9)
    else:
        world_sky(strength=1.25, rot_z=0.0, rot_x=0.0, tint=(1.05, 0.95, 1.0))
        sun(Vector((-0.4, -0.6, 0.5)), strength=1.2, color=(1.0, 0.85, 0.75))
        color, other = GOLD, (-6.5, 6.0, 0.9)
    orb = Orb("P", seed=0.0 if side == "A" else 11.3)
    orb.light_power = 30.0
    link_ = Link("Link", n=520, radius=0.0026, strength=1.3)
    det = Detector("Det")
    burst = Burst("Burst", (0.85, 0.9, 1.0))
    wave = Shockwave("Wave", color, thickness=0.005)
    wave2 = Shockwave("Wave2", color, thickness=0.003)
    focus = empty("Focus")
    cam = camera((0.35 * mirror, -3.6, 0.3), (0, 0, 0), lens=45, fstop=4.0, focus_obj=focus)
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24
    tilt = Euler((0.32, 0.0, -0.42 * mirror))
    tilt_start = Euler((1.1, 0.6 * mirror, -1.3 * mirror))
    ring_from = Vector((-2.2 * mirror, 1.2, 1.5))
    tg0 = info["start"] / FPS

    def update(t):
        s = s_of_t(t)
        tg = tg0 + s
        x = s - T_C
        # detector
        if side == "A":
            k = smoother((s - 0.4) / 2.5)
            settle = 1 + 0.04 * math.sin(clamp((s - 2.9) / 0.5) * math.pi) * (1 - clamp((s - 2.9) / 0.5))
            loc = ring_from.lerp(Vector((0, 0, 0)), k)
            rot = Euler([lerp(a, b, k) for a, b in zip(tilt_start, tilt)])
            scl = settle
        else:
            loc, rot, scl = Vector((0, 0, 0)), tilt, 1.0
        charge = smoother((s - 2.9) / 1.1)
        if x < 0:
            pad, padc = 0.35 + 3.5 * charge ** 2, (0.35, 0.8, 1.0)
        else:
            pad = 3.0 + 30 * math.exp(-x / 0.1)
            padc = tuple(lerp((0.35, 0.8, 1.0), color, smoother(x / 0.25)))
        det.set(loc, rot, scl, pad, padc)
        # particle
        if x < 0:
            orb.set(tg, collapse=0.0, target=color, energy=1.25 + 0.35 * charge)
        else:
            orb.set(tg, collapse=smoother(x / 0.3), target=color, energy=1.5,
                    flash=math.exp(-x / 0.1) * 0.9, flicker=1.0)
        burst.set((0, 0, 0), 0.25 + 0.5 * ease_out_expo(x / 0.3) if x >= 0 else 0.1,
                  (18 * math.exp(-x / 0.08)) if x >= 0 else 0,
                  tuple(lerp((1, 1, 1), color, 0.4)))
        wave.update((0, 0, 0), s, T_C, radius=0.4, reach=5, dur=0.8, strength=10,
                    normal=(0.15 * mirror, -1, 0.35), color=color)
        wave2.update((0, 0, 0), s, T_C + 0.05, radius=0.4, reach=3.2, dur=0.7, strength=6,
                     normal=(0.9 * mirror, -0.3, 0.3), color=color)
        # the link: fades once measured (the pair is no longer entangled)
        fade = 1 - smoother(x / 0.9) if x >= 0 else 1.0
        link_.show(fade > 0.01)
        link_.update(Vector((0, 0, 0)), Vector(other), tg, amp=0.05, turns=5, strength=1.3 * fade)
        # camera: slow push-in
        p = smoother(s / 14)
        cam.location = Vector((lerp(0.42, 0.25, p) * mirror, lerp(-4.7, -3.8, p), lerp(0.36, 0.22, p)))
        aim(cam, Vector((0.05 * mirror, 0, 0.02)))
        focus.location = (0, 0, 0)

    return sid, update


def main(side):
    sid, update = build(side)
    run(sid, update)
