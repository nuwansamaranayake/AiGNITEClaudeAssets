"""Procedural astrophotography-style sky as an equirectangular HDR (EXR half).
Milky Way band with dust lanes, temperature-colored stars, faint emission nebulae."""
import os, sys, numpy as np
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
import cv2
W, H = int(sys.argv[2]) if len(sys.argv) > 2 else 12288, None
H = W // 2
OUT = sys.argv[1]
rng = np.random.default_rng(7)

def hash3(ix, iy, iz, seed):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFFFF).astype(np.float32) / float(0xFFFFFF)

def vnoise(p, seed):
    i = np.floor(p).astype(np.int64); f = p - i
    f = f * f * (3 - 2 * f)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return out

def fbm(p, octaves, seed, lac=2.0, gain=0.5):
    a, s, tot = 1.0, 0.0, 0.0
    for o in range(octaves):
        s = s + a * vnoise(p, seed + o); tot += a
        p = p * lac; a *= gain
    return s / tot

def dirs(w, h):
    lon = (np.arange(w) + 0.5) / w * 2 * np.pi - np.pi
    lat = np.pi / 2 - (np.arange(h) + 0.5) / h * np.pi
    lon, lat = np.meshgrid(lon, lat)
    return np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], -1).astype(np.float32), lat

# galactic frame: tilted plane
ng = np.array([0.35, -0.25, 0.9]); ng /= np.linalg.norm(ng)
gc = np.cross(ng, [0, 0, 1.0]); gc /= np.linalg.norm(gc)     # galactic centre direction
gc = np.cos(0.6) * gc + np.sin(0.6) * np.cross(ng, gc)

# ---------- diffuse layer at low res ----------
lw = 3072; lh = lw // 2
d, _ = dirs(lw, lh)
b = np.arcsin(np.clip(d @ ng, -1, 1))                          # galactic latitude
cosc = d @ gc
band = np.exp(-(b / 0.16) ** 2)
bulge = np.exp(-((1 - cosc) / 0.10)) * np.exp(-(b / 0.22) ** 2)
clump = fbm(d * 6.0, 7, 11)
fine = fbm(d * 30.0, 5, 23)
glow = band * (0.35 + 0.9 * clump ** 2) * (0.7 + 0.6 * fine) + 1.4 * bulge * (0.6 + 0.8 * clump)
dust = fbm(d * 9.0 + 3.1, 7, 41)
lanes = np.clip((dust - 0.42) * 3.2, 0, 1) * np.exp(-(b / 0.07) ** 2) * (0.6 + 0.4 * band)
glow = glow * (1 - 0.85 * lanes)
warm = np.array([1.0, 0.82, 0.62]); cool = np.array([0.72, 0.82, 1.0])
mix = np.clip(bulge * 2.5, 0, 1)[..., None]
diffuse = glow[..., None] * (warm * mix + cool * (1 - mix)) * 0.030
# faint emission nebulae
neb = fbm(d * 3.0 + 7.7, 7, 77)
ha = np.clip((neb - 0.58) * 4.0, 0, 1) ** 2
oiii = np.clip((fbm(d * 4.0 + 1.3, 6, 99) - 0.60) * 4.0, 0, 1) ** 2
diffuse += ha[..., None] * np.array([0.9, 0.18, 0.35]) * 0.020 + oiii[..., None] * np.array([0.1, 0.55, 0.65]) * 0.012
diffuse += 0.0012 * np.array([0.55, 0.6, 1.0])                  # airglow floor
img = cv2.resize(diffuse.astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
img = np.maximum(img, 0)

# ---------- stars ----------
N = 900_000
v = rng.normal(size=(N, 3)); v /= np.linalg.norm(v, axis=1, keepdims=True)
# extra stars concentrated in the band
M = 700_000
u = rng.normal(size=(M, 3)); u -= (u @ ng)[:, None] * ng; u /= np.linalg.norm(u, axis=1, keepdims=True)
bb = rng.normal(scale=0.10, size=M)
v2 = u * np.cos(bb)[:, None] + ng * np.sin(bb)[:, None]
v = np.concatenate([v, v2])
flux = (rng.pareto(1.45, len(v)) + 1) ** 1.0 * 0.004
flux = np.minimum(flux, 60)
T = np.clip(rng.lognormal(np.log(5600), 0.35, len(v)), 2800, 20000)
def bb_rgb(T):
    t = T / 100.0
    r = np.where(t <= 66, 255, 329.7 * (t - 60) ** -0.1332)
    g = np.where(t <= 66, 99.47 * np.log(t) - 161.1, 288.1 * (t - 60) ** -0.0755)
    bl = np.where(t >= 66, 255, np.where(t <= 19, 0, 138.5 * np.log(np.maximum(t - 10, 1e-3)) - 305.0))
    c = np.clip(np.stack([r, g, bl], 1), 0, 255) / 255.0
    return c / c.max(1, keepdims=True)
col = bb_rgb(T)
col = 0.55 * col + 0.45                                         # stars look pale in photos
lat = np.arcsin(np.clip(v[:, 2], -1, 1)); lon = np.arctan2(v[:, 1], v[:, 0])
x = (lon + np.pi) / (2 * np.pi) * W - 0.5; y = (np.pi / 2 - lat) / np.pi * H - 0.5
stars = np.zeros((H, W, 3), np.float32)
dim = flux < 0.25
xi = np.floor(x[dim]).astype(int); yi = np.floor(y[dim]).astype(int); fx = x[dim] - xi; fy = y[dim] - yi
for ox, oy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
    xx = (xi + ox) % W; yy = np.clip(yi + oy, 0, H - 1)
    for c in range(3):
        np.add.at(stars[..., c], (yy, xx), (flux[dim] * col[dim, c] * w).astype(np.float32))
stars = cv2.GaussianBlur(stars, (0, 0), 0.55)
# bright stars: explicit gaussian kernels, stretched in x near the poles
for i in np.nonzero(~dim)[0]:
    s = 0.8 + 0.35 * np.log1p(flux[i] * 4)
    sx = s / max(np.cos(lat[i]), 0.05)
    r = int(np.ceil(4 * max(s, sx)))
    ys = np.arange(int(y[i]) - int(4 * s) - 1, int(y[i]) + int(4 * s) + 2)
    xs = np.arange(int(x[i]) - r - 1, int(x[i]) + r + 2)
    ys = ys[(ys >= 0) & (ys < H)]
    g = np.exp(-((xs[None, :] - x[i]) ** 2) / (2 * sx * sx) - ((ys[:, None] - y[i]) ** 2) / (2 * s * s))
    g *= flux[i] / (2 * np.pi * s * s) * 3.0
    stars[ys[:, None], xs[None, :] % W] += g[..., None] * col[i]
img = img + stars
print("max", img.max(), "mean", img.mean())
cv2.imwrite(OUT, img[..., ::-1].astype(np.float32), [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF])
prev = np.clip((img / (1 + img)) ** (1 / 2.2) * 1.8, 0, 1)
cv2.imwrite(OUT.replace(".exr", "_preview.jpg"), (cv2.resize(prev, (2048, 1024), interpolation=cv2.INTER_AREA)[..., ::-1] * 255).astype(np.uint8))
