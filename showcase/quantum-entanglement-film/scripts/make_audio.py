"""Soundtrack: narration + original synthesized score + sound design, all locked to events.json.
Outputs audio/soundtrack.wav (48 kHz, 24-bit stereo, -16 LUFS integrated, peaks <= -1.5 dBFS)
and audio/voice_only.wav for checks."""
import json, math, pathlib, subprocess
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, lfilter, fftconvolve, resample_poly, sosfilt
import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
EV = json.loads((ROOT / "events.json").read_text())
TL = json.loads((ROOT / "timeline.json").read_text())
SR = 48000
FPS = EV["fps"]
DUR = EV["total_frames"] / FPS + 0.8
NS = int(DUR * SR)
rng = np.random.default_rng(7)


def st(sid):
    return EV["shots"][sid]["start"] / FPS


def A(sid, t):
    return st(sid) + t


def buf():
    return np.zeros((NS, 2), np.float32)


def add(dst, sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if sig.ndim == 1:
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
    j = min(NS, i + len(sig))
    if i < 0:
        sig = sig[-i:]
        i = 0
    if j > i:
        dst[i:j] += sig[: j - i] * gain


def lp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "low")
    return lfilter(b, a, x, axis=0).astype(np.float32)


def hp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "high")
    return lfilter(b, a, x, axis=0).astype(np.float32)


def bp(x, f1, f2, order=2):
    sos = butter(order, [f1 / (SR / 2), f2 / (SR / 2)], "band", output="sos")
    return sosfilt(sos, x, axis=0).astype(np.float32)


# ---------------------------------------------------------------- reverb (synthetic stereo IR)
def make_ir(rt60=3.2, predelay=0.02, bright=6000):
    n = int((rt60 + predelay) * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.91 * t / rt60) * (t > predelay)
    ir = rng.standard_normal((n, 2)).astype(np.float32) * env[:, None]
    ir = lp(ir, bright, 1)
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    return ir


IR_BIG = make_ir(4.2, 0.03, 5000)
IR_ROOM = make_ir(0.9, 0.01, 7000)


def reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1).astype(np.float32)
    return x * (1 - wet) + y * wet


# ---------------------------------------------------------------- oscillators
TABLE = 4096
ph = np.arange(TABLE) / TABLE
SAW = sum(np.sin(2 * np.pi * k * ph) / k * (1 - k / 28) for k in range(1, 28)).astype(np.float32)
SAW /= np.abs(SAW).max()


def osc(freq, n, table=SAW, phase0=None):
    f = np.full(n, freq, np.float32) if np.isscalar(freq) else freq.astype(np.float32)
    phase = (np.cumsum(f / SR) + (rng.random() if phase0 is None else phase0)) % 1.0
    return np.interp(phase * TABLE, np.arange(TABLE), table).astype(np.float32)


def env_adsr(n, a, r, sustain=1.0):
    e = np.ones(n, np.float32) * sustain
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, sustain, na) ** 1.5
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def pad_chord(notes, dur, a=2.5, r=3.0, cutoff=1400, detune=0.006, gain=0.06):
    n = int(dur * SR)
    out = np.zeros((n, 2), np.float32)
    for i, f in enumerate(notes):
        for d, pan in ((-detune, -0.7), (0.0, 0.0), (detune, 0.7)):
            v = osc(f * (1 + d), n)
            # slow breathing filter via crossfade with a sine
            s = np.sin(2 * np.pi * np.cumsum(np.full(n, f * (1 + d)) / SR) + rng.random() * 6.28).astype(np.float32)
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * (0.07 + 0.02 * i) * np.arange(n) / SR + rng.random() * 6.28)
            v = v * (0.35 + 0.35 * lfo) + s * 0.6
            l, rr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
            out[:, 0] += v * l
            out[:, 1] += v * rr
    out = lp(out, cutoff, 2)
    return out * env_adsr(n, a, r)[:, None] * gain / max(1, len(notes)) * 3


def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + phase).astype(np.float32)


def bell(f, dur=2.5, ratio=3.5, index=2.2, decay=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    mod = index * np.exp(-t / (decay * 0.5)) * np.sin(2 * np.pi * f * ratio * t)
    y = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / decay)
    y[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return y.astype(np.float32)


def impact(strength=1.0, dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t / 0.18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    nz = lp(rng.standard_normal(n).astype(np.float32), 900, 2) * np.exp(-t / 0.09)
    click = hp(rng.standard_normal(n).astype(np.float32), 2000) * np.exp(-t / 0.012) * 0.3
    y = sub * 0.9 + nz * 0.5 + click
    return (y * strength).astype(np.float32)


def whoosh(dur, f0=250, f1=3200, gain=0.4):
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    # time-varying band via three overlapping fixed bands crossfaded
    t = np.linspace(0, 1, n)
    bands = [(f0, f0 * 2.5), (math.sqrt(f0 * f1) / 1.6, math.sqrt(f0 * f1) * 1.6), (f1 / 2.5, min(f1, 18000))]
    ys = [bp(x, lo, hi) for lo, hi in bands]
    w0 = np.clip(1 - 2 * t, 0, 1)
    w2 = np.clip(2 * t - 1, 0, 1)
    w1 = 1 - w0 - w2
    y = ys[0] * w0 + ys[1] * w1 + ys[2] * w2
    e = np.sin(np.pi * t) ** 1.6
    return (y * e * gain).astype(np.float32)


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return (bp(rng.standard_normal(n).astype(np.float32), 2500, 6000) * np.exp(-t / 0.004) * 0.5).astype(np.float32)


def thump(f=55, dur=0.6, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ff = f * (1 + 0.8 * np.exp(-t / 0.03))
    return (np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / 0.16) * gain).astype(np.float32)


def glide(f0, f1, dur, gain=0.2):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** t
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 5.5 * t * dur)
    return (y * trem * np.sin(np.pi * np.clip(t * 1.0, 0, 1)) ** 0.5 * gain).astype(np.float32)


# ---------------------------------------------------------------- voice
FF = imageio_ffmpeg.get_ffmpeg_exe()


def load_mp3(path):
    raw = subprocess.run([FF, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


voice = buf()
for s in TL["shots"]:
    v = load_mp3(ROOT / "audio" / f"{s['id']}.mp3")
    v = hp(v, 70)
    add(voice, v, s["start"] / FPS + s["pre"], gain=1.0, pan=0.0)
voice = reverb(voice, IR_ROOM, 0.06)

# ---------------------------------------------------------------- score
Hz = lambda n: 440.0 * 2 ** ((n - 69) / 12)
D2, A2, F3, C4, E4 = Hz(38), Hz(45), Hz(53), Hz(60), Hz(64)
chords = {
    "Dm9": [Hz(38), Hz(45), Hz(53), Hz(60), Hz(64)],
    "Bbmaj7": [Hz(34), Hz(41), Hz(50), Hz(57), Hz(64)],
    "Gm9": [Hz(31), Hz(38), Hz(46), Hz(53), Hz(57)],
    "Asus": [Hz(33), Hz(40), Hz(50), Hz(52), Hz(57)],
    "Fadd9": [Hz(29), Hz(41), Hz(48), Hz(55), Hz(57)],
    "Dmaj9": [Hz(38), Hz(45), Hz(54), Hz(61), Hz(64)],
    "Apedal": [Hz(33), Hz(45)],
}
music = buf()
e = EV
born = A("s01_birth", e["s01"]["t_born"])
c1 = A("s04_measure", e["s04"]["T_C"])
c2 = A("s04_measure", e["s04"]["replay_collapse"])
plan = [  # (chord, start, end, cutoff, gain)
    ("Apedal", 0.0, born + 0.3, 500, 0.05),
    ("Dmaj9", born - 0.05, born + 5.0, 2600, 0.07),
    ("Dm9", born + 3.0, st("s02_pair") + 8.5, 1500, 0.06),
    ("Bbmaj7", st("s02_pair") + 7.5, st("s03_apart") + 1.0, 1500, 0.06),
    ("Gm9", st("s03_apart") + 0.0, st("s03_apart") + 6.5, 1700, 0.065),
    ("Asus", st("s03_apart") + 5.5, st("s04_measure") + 1.0, 1500, 0.06),
    ("Apedal", st("s04_measure") + 0.2, c1 + 0.2, 700, 0.07),
    ("Dm9", c1 - 0.02, st("s04_measure") + e["s04"]["R0"] + 0.3, 1800, 0.06),
    ("Apedal", st("s04_measure") + e["s04"]["R0"], c2 + 0.2, 500, 0.06),
    ("Bbmaj7", c2 - 0.02, st("s05_repeat") + 3.0, 1800, 0.06),
    ("Dm9", st("s05_repeat") + 1.5, A("s05_repeat", e["s05"]["compare"]) + 0.5, 1500, 0.055),
    ("Fadd9", A("s05_repeat", e["s05"]["compare"]), st("s06_boxes") + 1.5, 2400, 0.06),
    ("Bbmaj7", st("s06_boxes") + 0.5, A("s06_boxes", e["s06"]["entangled"]), 1300, 0.055),
    ("Gm9", A("s06_boxes", e["s06"]["entangled"]) - 0.3, A("s06_boxes", e["s06"]["that"]) + 0.5, 1900, 0.06),
    ("Fadd9", A("s06_boxes", e["s06"]["that"]), st("s07_nosignal") + 1.5, 2200, 0.06),
    ("Asus", st("s07_nosignal") + 0.5, A("s07_nosignal", e["s07"]["arrive_t"]) + 0.3, 1100, 0.05),
    ("Dm9", A("s07_nosignal", e["s07"]["arrive_t"]), st("s08_real") + 2.0, 1800, 0.055),
    ("Bbmaj7", st("s08_real") + 1.0, st("s08_real") + 8.0, 2000, 0.065),
    ("Fadd9", st("s08_real") + 7.0, st("s08_real") + 13.0, 2400, 0.07),
    ("Gm9", st("s08_real") + 12.0, st("s09_outro") + 1.0, 2200, 0.065),
    ("Asus", st("s09_outro") + 0.2, A("s09_outro", e["s09"]["that"]) + 0.2, 1600, 0.06),
    ("Dmaj9", A("s09_outro", e["s09"]["that"]), DUR - 0.2, 2800, 0.075),
]
for name, t0, t1, fc, g in plan:
    add(music, pad_chord(chords[name], t1 - t0 + 2.5, a=1.8, r=2.8, cutoff=fc, gain=g), t0)
# sub bass follows chord roots
for name, t0, t1, fc, g in plan:
    n = int((t1 - t0 + 2.0) * SR)
    s = sine(chords[name][0] / 2 if chords[name][0] > 60 else chords[name][0], n) * env_adsr(n, 1.5, 2.0) * 0.05
    add(music, s, t0)
# shimmer: sparse high bells on chord tones, slower in calm parts
bell_times = np.arange(3.0, DUR - 6, 2.7) + rng.uniform(-0.4, 0.4, len(np.arange(3.0, DUR - 6, 2.7)))
for bt in bell_times:
    cur = [c for c in plan if c[1] <= bt < c[2] + 1]
    if not cur:
        continue
    notes = chords[cur[-1][0]]
    f = notes[rng.integers(len(notes))] * 4
    add(music, bell(f, 3.0, ratio=2.0, index=0.8, decay=1.1) * 0.018, bt, pan=float(rng.uniform(-0.6, 0.6)))
music = reverb(music, IR_BIG, 0.45)

# ---------------------------------------------------------------- sound design
sfx = buf()
# S01: pulse streak and the birth flash
add(sfx, whoosh(0.8, 400, 6000, 0.35), A("s01_birth", e["s01"]["t_in"]) - 0.05)
add(sfx, impact(0.9, 3.5), born)
add(sfx, bell(Hz(74), 4.0, 2.0, 1.5, 1.6) * 0.12, born, pan=-0.2)
add(sfx, bell(Hz(81), 4.0, 2.0, 1.5, 1.6) * 0.10, born + 0.02, pan=0.2)
# S03: launch and zoom-outs
add(sfx, whoosh(1.2, 200, 3000, 0.35), A("s03_apart", e["s03"]["apart"]) - 0.5)
add(sfx, whoosh(0.7, 300, 5000, 0.3), A("s03_apart", e["s03"]["cut_ab"]) - 0.35)
add(sfx, whoosh(0.9, 250, 5000, 0.33), A("s03_apart", e["s03"]["cut_bc"]) - 0.45)
add(sfx, bell(Hz(69), 3.0, 2.0, 1.0, 1.4) * 0.05, A("s03_apart", e["s03"]["link"]) + 0.3)
# S04: detector glide, charge-up ticks, collapse, replay
add(sfx, whoosh(2.4, 120, 1200, 0.22), st("s04_measure") + 0.4)
for k in range(int((e["s04"]["T_C"] - 2.9) * 6)):
    add(sfx, tick(), A("s04_measure", 2.9 + k / 6), gain=0.35 + 0.1 * k)
for tcol, g in ((c1, 1.0), (c2, 0.8)):
    add(sfx, impact(g, 3.5), tcol)
    add(sfx, bell(Hz(76), 3.5, 3.5, 2.0, 1.2) * 0.10 * g, tcol, pan=-0.5)   # A: blue
    add(sfx, bell(Hz(71), 3.5, 3.5, 2.0, 1.2) * 0.10 * g, tcol, pan=0.5)    # B: gold
add(sfx, whoosh(0.5, 3000, 300, 0.25), A("s04_measure", e["s04"]["R0"]) - 0.25)   # rewind
# S05: each trial pings, left and right
for tr in e["s05"]["trials"]:
    t = A("s05_repeat", tr["t"])
    fL = Hz(76) if tr["left"] == "B" else Hz(71)
    fR = Hz(76) if tr["right"] == "B" else Hz(71)
    add(sfx, bell(fL, 1.6, 3.5, 1.4, 0.6) * 0.07, t, pan=-0.6)
    add(sfx, bell(fR, 1.6, 3.5, 1.4, 0.6) * 0.07, t, pan=0.6)
for k in range(10):
    add(sfx, bell(Hz(81 + (k % 3) * 2), 1.4, 2.0, 0.8, 0.5) * 0.04, A("s05_repeat", e["s05"]["opposite"] - 0.4 + k * 0.12))
# S06: x-ray scans and the transformation
for key in ("blue", "gold"):
    add(sfx, glide(900, 2200, 0.45, 0.05), A("s06_boxes", e["s06"][key] - 0.1))
add(sfx, whoosh(0.9, 500, 7000, 0.25), A("s06_boxes", e["s06"]["entangled"] - 0.6))
add(sfx, bell(Hz(74), 3.0, 1.5, 2.2, 1.3) * 0.08, A("s06_boxes", e["s06"]["entangled"] - 0.05))
# S07: a message that cannot go, then notes travelling at light speed
add(sfx, glide(500, 900, 0.9, 0.05), A("s07_nosignal", e["s07"]["messages"] - 0.2))
add(sfx, glide(420, 300, 0.35, 0.06), A("s07_nosignal", e["s07"]["no"]))
add(sfx, glide(300, 600, e["s07"]["arrive_t"] - e["s07"]["send_t"], 0.035), A("s07_nosignal", e["s07"]["send_t"]))
add(sfx, bell(Hz(79), 3.0, 2.0, 1.2, 1.2) * 0.09, A("s07_nosignal", e["s07"]["arrive_t"]))
# S08: beam hum and photon pair arrivals
n = int((st("s09_outro") - A("s08_real", e["s08"]["sent"])) * SR)
hum = (sine(110, n) * 0.5 + sine(220, n) * 0.25 + sine(330.5, n) * 0.1) * env_adsr(n, 0.4, 1.5) * 0.015
add(sfx, hum, A("s08_real", e["s08"]["sent"]))
for ta in e["s08"]["arrivals"]:
    add(sfx, bell(Hz(88), 0.8, 3.0, 0.8, 0.25) * 0.018, A("s08_real", ta), pan=-0.4)
    add(sfx, bell(Hz(88), 0.8, 3.0, 0.8, 0.25) * 0.018, A("s08_real", ta), pan=0.4)
# S09: two synchronized heartbeats
for b in e["s09"]["beats"]:
    add(sfx, thump(52, 0.7, 0.55), A("s09_outro", b) - 0.05, pan=-0.3)
    add(sfx, thump(52, 0.7, 0.55), A("s09_outro", b) - 0.05, pan=0.3)
    add(sfx, thump(44, 0.6, 0.35), A("s09_outro", b) + 0.2)
sfx = reverb(sfx, IR_BIG, 0.3)

# ---------------------------------------------------------------- mix: duck music under the voice
venv = np.abs(voice).max(1)
k_att, k_rel = math.exp(-1 / (0.03 * SR)), math.exp(-1 / (0.45 * SR))
# fast envelope follower on a decimated signal
dec = 48
v_d = venv[: len(venv) // dec * dec].reshape(-1, dec).max(1)
envd = np.zeros_like(v_d)
a1, r1 = math.exp(-1 / (0.03 * SR / dec)), math.exp(-1 / (0.45 * SR / dec))
acc = 0.0
for i, x in enumerate(v_d):
    acc = (a1 if x > acc else r1) * acc + (1 - (a1 if x > acc else r1)) * x
    envd[i] = acc
env = np.repeat(envd, dec)
env = np.pad(env, (0, NS - len(env)), mode="edge")
duck = 1 - 0.55 * np.clip(env / 0.08, 0, 1)
speech = env > 0.03


def rms_db(x):
    return 10 * np.log10(np.mean(x ** 2) + 1e-12)


# level-relative gains: music bed 16 dB under the voice while it speaks, effects 9 dB under
v_rms = rms_db(voice[speech])
music *= 10 ** ((v_rms - 16 - rms_db((music * duck[:, None])[speech])) / 20)
s_env = np.abs(sfx).max(1)
active = s_env > s_env.max() * 0.02
sfx *= 10 ** ((v_rms - 9 - rms_db(sfx[active])) / 20)
mix = voice * 1.0 + music * duck[:, None] + sfx * (1 - 0.25 * np.clip(env / 0.08, 0, 1))[:, None]
fade_n = int(2.5 * SR)
mix[-fade_n:] *= np.linspace(1, 0, fade_n)[:, None] ** 2

# ---- objective mix checks
bg = music * duck[:, None] + sfx * (1 - 0.25 * np.clip(env / 0.08, 0, 1))[:, None]
snr = rms_db(voice[speech]) - rms_db(bg[speech])
print(f"CHECK voice-to-background during speech: {snr:.1f} dB (target >= 12)")
gaps = ~speech
print(f"CHECK music level in gaps vs voice: {rms_db(bg[gaps]) - rms_db(voice[speech]):.1f} dB")
meter = pyln.Meter(SR)
loud = meter.integrated_loudness(mix)
mix = pyln.normalize.loudness(mix, loud, -16.0)
peak = np.abs(mix).max()
lim = 10 ** (-1.5 / 20)
if peak > lim:
    # soft knee limiter: tanh above 70% of the ceiling
    thr = lim * 0.7
    over = np.abs(mix) > thr
    print(f"CHECK samples in limiter knee: {100 * over.mean():.4f}%  pre-limit peak {20 * np.log10(peak):.2f} dBFS")
    mix[over] = np.sign(mix[over]) * (thr + (lim - thr) * np.tanh((np.abs(mix[over]) - thr) / (lim - thr)))
final_loud = meter.integrated_loudness(mix)
sf.write(ROOT / "audio" / "soundtrack.wav", mix.astype(np.float32), SR, subtype="PCM_24")
vo = pyln.normalize.loudness(voice, meter.integrated_loudness(voice), -16.0)
sf.write(ROOT / "audio" / "voice_only.wav", np.clip(vo, -1, 1).astype(np.float32), SR, subtype="PCM_16")
print(f"soundtrack: {DUR:.2f}s  integrated {final_loud:.2f} LUFS  peak {20 * np.log10(np.abs(mix).max()):.2f} dBFS")
