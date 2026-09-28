"""Face-on barred spiral galaxy (Milky Way-like) as RGBA EXR for an emissive plane.
Warm bulge and bar, bluish star-forming arms, pink HII knots, dark dust lanes."""
import os, sys, numpy as np
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
import cv2
S = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
OUT = sys.argv[1]
rng = np.random.default_rng(21)
y, x = (np.mgrid[0:S, 0:S].astype(np.float32) + 0.5) / S * 2 - 1
r = np.sqrt(x * x + y * y) + 1e-6
th = np.arctan2(y, x)


def noise2(scale, octaves, seed):
    acc = np.zeros((S, S), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = int(scale * 2 ** o) + 2
        g = np.random.default_rng(seed + o).random((n, n)).astype(np.float32)
        acc += amp * cv2.resize(g, (S, S), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.55
    return acc / tot


# log spiral arms, pitch ~ 13 deg, bar of radius 0.16
pitch = np.tan(np.radians(13))
bar_r = 0.16
phase = np.log(np.maximum(r, bar_r) / bar_r) / pitch
turb = noise2(6, 6, 3) - 0.5
arms_major = np.cos(2 * (th - phase) + 2.2 * turb) * 0.5 + 0.5
arms_minor = np.cos(2 * (th - phase) + np.pi * 0.55 + 3.0 * turb) * 0.5 + 0.5
arms = np.maximum(arms_major ** 6, 0.55 * arms_minor ** 8)
disk = np.exp(-r / 0.28) * (r < 1.0)
radial_fade = np.clip((0.95 - r) / 0.25, 0, 1)
clumps = noise2(40, 5, 9)
arm_light = arms * disk * radial_fade * (0.55 + 0.9 * clumps ** 2) * np.clip(r / 0.12, 0, 1)
# bar and bulge
ang_bar = 0.45
xb = x * np.cos(ang_bar) + y * np.sin(ang_bar)
yb = -x * np.sin(ang_bar) + y * np.cos(ang_bar)
bar = np.exp(-(xb / 0.19) ** 2 - (yb / 0.055) ** 2)
bulge = np.exp(-(r / 0.07) ** 1.3)
diffuse = np.exp(-r / 0.33) * 0.35
# dust lanes: trailing inner edges of the arms
dust_phase = np.cos(2 * (th - phase) - 0.55 + 2.2 * turb) * 0.5 + 0.5
dust = (dust_phase ** 10) * np.clip(r / 0.1, 0, 1) * np.exp(-r / 0.45) * (0.4 + 0.8 * noise2(30, 5, 13))
dust = np.clip(dust * 1.8, 0, 0.92)
warm = np.array([1.0, 0.78, 0.52], np.float32)
white = np.array([0.95, 0.93, 1.0], np.float32)
blue = np.array([0.55, 0.72, 1.0], np.float32)
img = (bulge[..., None] * 3.2 + bar[..., None] * 1.3) * warm
img += diffuse[..., None] * (0.6 * warm + 0.4 * white)
img += arm_light[..., None] * 1.6 * blue
img *= (1 - dust)[..., None]
# resolved stars and star clusters along the arms
n = 260_000
px = rng.random(n) * S
py = rng.random(n) * S
w = arm_light[py.astype(int), px.astype(int)] + 0.15 * diffuse[py.astype(int), px.astype(int)]
keep = rng.random(n) < w * 3.0
px, py = px[keep], py[keep]
stars = np.zeros((S, S), np.float32)
np.add.at(stars, (py.astype(int), px.astype(int)), rng.pareto(1.6, len(px)).astype(np.float32) * 0.25 + 0.05)
stars = cv2.GaussianBlur(stars, (0, 0), 0.8)
img += stars[..., None] * np.array([0.8, 0.88, 1.0], np.float32)
# pink HII regions on the arms
m = 1800
hx = rng.random(m * 8) * S
hy = rng.random(m * 8) * S
hw = arms[hy.astype(int), hx.astype(int)] * (r[hy.astype(int), hx.astype(int)] > 0.18) * (r[hy.astype(int), hx.astype(int)] < 0.85)
sel = rng.random(len(hx)) < hw ** 3 * 0.35
hii = np.zeros((S, S), np.float32)
np.add.at(hii, (hy[sel].astype(int), hx[sel].astype(int)), 1.0)
hii = cv2.GaussianBlur(hii, (0, 0), 2.2) * 5.0
img += hii[..., None] * np.array([1.0, 0.35, 0.55], np.float32)
img = cv2.GaussianBlur(img, (0, 0), 0.6)
img *= 0.9
alpha = np.clip(img.max(-1) * 3.0, 0, 1) * np.clip((1.0 - r) / 0.1, 0, 1)
out = np.dstack([img[..., ::-1], alpha]).astype(np.float32)
cv2.imwrite(OUT, out, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF])
prev = np.clip((img / (1 + img)) ** (1 / 2.2) * 1.4, 0, 1)
cv2.imwrite(OUT.replace(".exr", "_preview.jpg"), (cv2.resize(prev, (1024, 1024), interpolation=cv2.INTER_AREA)[..., ::-1] * 255).astype(np.uint8))
print("galaxy max", img.max())
