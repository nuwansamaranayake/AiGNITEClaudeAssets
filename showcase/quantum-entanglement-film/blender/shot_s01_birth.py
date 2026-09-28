"""S01: drift through a field of tiny particles; a pulse of light arrives, a flash,
and two entangled particles are born. Ends exactly on S02's first frame."""
import sys, math, random, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SID = "s01_birth"
info = shot_info(SID)
N = info["frames"]
T = N / FPS
sc = new_scene((1920, 1080), samples=8, frames=N, motion_blur=True, exposure=0.0)
world_sky(strength=0.9, rot_z=2.2, rot_x=0.3)

A = Orb("A", seed=0.0)
B = Orb("B", seed=11.3)
link_ = Link("Link", radius=0.0024, strength=1.3)
specks = speck_field()
focus = empty("Focus")
cam = camera((0.8, -30, 1.4), (0, 0, 0), lens=35, fstop=2.8, focus_obj=focus)

# incoming pulse of light (one photon)
pulse = uv_sphere("Pulse", 0.05, 32, 16)
pm, pem = glow_additive_mat("pulse", (0.8, 0.75, 1.0), 40)
assign(pulse, pm)
# flash: soft light burst plus two thin rings
flash = Burst("Flash")
glow = Burst("Afterglow", (0.75, 0.7, 1.0))
wave1 = Shockwave("Wave1", (0.8, 0.75, 1.0))
wave2 = Shockwave("Wave2", (0.7, 0.8, 1.0))
# sparks
rnd = random.Random(11)
sm, sem = glow_additive_mat("spark", (0.95, 0.9, 1.0), 14)
sparks = []
for i in range(70):
    d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 0.6))).normalized()
    o = uv_sphere(f"spark{i}", rnd.uniform(0.006, 0.014), 8, 4)
    assign(o, sm)
    o.visible_shadow = False
    sparks.append((o, d, rnd.uniform(1.2, 3.6)))

t_born = word_time(SID, "together") - 0.12       # flash lands on "together"
t_in = t_born - 0.75                            # pulse enters
t_every = word_time(SID, "everything")
TG0 = info["start"] / FPS

# S02 first-frame state (keep in sync with shot_s02_pair.py)
ang0 = 0.35
A_end = Vector((-1.15 * math.cos(ang0), -1.15 * math.sin(ang0) * 0.35, 0.0))
B_end = -A_end + Vector((0, 0, 0.05 * math.sin(1)))
cam_end = Vector((math.sin(-0.30) * 5.4, -math.cos(-0.30) * 5.4, 0.45))
pulse_from = Vector((-9.0, 4.0, 1.6))


def update(t):
    tg = TG0 + t
    # camera: long drift through the particle field, settling on S02's framing
    k = smoother(t / T)
    k = 1 - (1 - k) ** 2.2
    start = Vector((0.8, -30, 1.4))
    cam.location = start.lerp(cam_end, k) + Vector((0.25 * math.sin(t * 0.5), 0, 0.12 * math.sin(t * 0.37))) * (1 - k)
    aim(cam, Vector((0, 0, 0)))
    cam.data.lens = lerp(35, 50, smoother(t / T))
    focus.location = (0, 0, 0)
    cam.data.dof.aperture_fstop = lerp(8.0, 2.8, ramp(t, t_born - 1, T))
    update_specks(specks, tg)

    # the pulse streaks in along a slight curve
    x = (t - t_in) / (t_born - t_in)
    if 0 <= x < 1:
        set_visible(pulse, True)
        e = x ** 1.6
        pulse.location = pulse_from.lerp(Vector((0, 0, 0)), e) + Vector((0, 0, 0.4 * math.sin(math.pi * e)))
        pulse.scale = (1.0, 1.0, 1.0)
        pem.inputs["Strength"].default_value = 30 + 40 * x
    else:
        set_visible(pulse, False)

    # flash
    f = t - t_born
    if f >= 0:
        flash.set((0, 0, 0), 0.1 + 0.45 * ease_out_expo(f / 0.2), 30 * math.exp(-f / 0.07) + 4 * math.exp(-f / 0.25))
        g = 0.9 * math.exp(-f / 0.45) * smooth(f / 0.04)
        glow.set((0, 0, 0), 0.7 + 0.3 * f, g if g > 0.01 else 0)
    else:
        flash.set((0, 0, 0), 0.1, 0)
        glow.set((0, 0, 0), 0.1, 0)
    wave1.update((0, 0, 0), t, t_born, radius=0.2, reach=8, dur=1.0, strength=9, normal=(0.1, -0.3, 1))
    wave2.update((0, 0, 0), t, t_born + 0.06, radius=0.2, reach=6, dur=0.9, strength=6, normal=(0.9, 0.2, 0.4))
    for o, d, spd in sparks:
        if 0 <= f < 2.2:
            set_visible(o, True)
            dist = spd * (1 - math.exp(-f * 2.2)) / 2.2 * 2.0
            o.location = d * dist
            sem.inputs["Strength"].default_value = 18 * math.exp(-f / 0.7)
        else:
            set_visible(o, False)

    # the pair
    if f >= 0:
        set_visible(A.obj, True)
        set_visible(B.obj, True)
        e = ease_out_expo(f / 2.4)
        A.obj.location = Vector((0, 0, 0)).lerp(A_end, e)
        B.obj.location = Vector((0, 0, 0)).lerp(B_end, e)
        sc_ = 0.15 + 0.85 * smoother(f / 0.7)
        A.set_scale(sc_)
        B.set_scale(sc_)
        fl = math.exp(-f / 0.25)
        A.set(tg, flash=fl * 0.25)
        B.set(tg, flash=fl * 0.25)
        link_.show(True)
        link_.update(A.obj.location, B.obj.location, tg, amp=0.05 * smoother((f - 0.2) / 1.2), turns=5,
                     strength=1.3 * smoother((f - 0.25) / 1.4))
    else:
        set_visible(A.obj, False)
        set_visible(B.obj, False)
        link_.show(False)


run(SID, update)
