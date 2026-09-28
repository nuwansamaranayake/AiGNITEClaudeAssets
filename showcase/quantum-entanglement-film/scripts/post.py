"""Film-look finishing for rendered frames: multi-scale bloom, lens vignette,
chromatic fringing, gentle grade and animated grain.

usage: post.py <in_dir> <out.mp4> [--bloom 1.0] [--thr 0.55] [--grain 1.0] [--still frame.png]
Writes an H.264 (CRF 12) intermediate at 24 fps for Remotion. Input frames are
16-bit PNG (RGB or RGBA; RGBA is composited over black unless --keep-alpha,
which writes PNGs instead)."""
import argparse, os, sys, glob, subprocess, numpy as np, cv2
import imageio_ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--bloom", type=float, default=1.0)
ap.add_argument("--thr", type=float, default=0.55)
ap.add_argument("--grain", type=float, default=1.0)
ap.add_argument("--vignette", type=float, default=0.28)
ap.add_argument("--ca", type=float, default=1.0)
ap.add_argument("--streak", type=float, default=0.0)
ap.add_argument("--still", default=None)
ap.add_argument("--scale", default=None, help="WxH output size (upscale)")
ap.add_argument("--keep-alpha", action="store_true")
ap.add_argument("--nograde", action="store_true", help="no black lift or tint (sprites composited with screen blend)")
ap.add_argument("--start", type=int, default=0)
a = ap.parse_args()

files = sorted(glob.glob(os.path.join(a.src, "[0-9][0-9][0-9][0-9].png")))
if a.still:
    files = [os.path.join(a.src, a.still)]
if not files:
    sys.exit(f"no frames in {a.src}")


def to_lin(x):
    return np.power(np.clip(x, 0, 1), 2.2)


def to_disp(x):
    return np.power(np.clip(x, 0, 1), 1 / 2.2)


_vig = {}
_ca = {}


def vignette(h, w):
    k = (h, w)
    if k not in _vig:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        nx = (x - w / 2) / (w / 2)
        ny = (y - h / 2) / (h / 2)
        r2 = (nx * nx * 0.78 + ny * ny)
        _vig[k] = (1 - a.vignette * np.clip(r2, 0, 2) ** 1.4)[..., None].astype(np.float32)
    return _vig[k]


def chroma(img):
    h, w = img.shape[:2]
    if (h, w) not in _ca:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        maps = []
        for s in (1 + 0.0009 * a.ca, 1.0, 1 - 0.0009 * a.ca):
            maps.append(((x - w / 2) * s + w / 2, (y - h / 2) * s + h / 2))
        _ca[(h, w)] = maps
    out = np.empty_like(img)
    for c, (mx, my) in enumerate(_ca[(h, w)]):
        out[..., c] = cv2.remap(img[..., c], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out


def bloom(lin):
    lum = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    thr = a.thr ** 2.2
    knee = thr * 0.6
    soft = np.clip(lum - thr + knee, 0, 2 * knee)
    soft = soft * soft / (4 * knee + 1e-6)
    contrib = np.maximum(soft, lum - thr) / np.maximum(lum, 1e-4)
    bright = lin * contrib[..., None]
    h, w = lin.shape[:2]
    acc = np.zeros_like(lin)
    small = bright
    weights = [0.9, 0.75, 0.6, 0.5, 0.42, 0.35]
    scale = 1
    for i, wgt in enumerate(weights):
        small = cv2.pyrDown(small)
        scale *= 2
        b = cv2.GaussianBlur(small, (0, 0), 1.6)
        up = cv2.resize(b, (w, h), interpolation=cv2.INTER_LINEAR)
        acc += up * wgt
    out = lin + acc * 0.55 * a.bloom
    if a.streak > 0:
        s = cv2.resize(bright, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        s = cv2.GaussianBlur(s, (0, 0), sigmaX=60, sigmaY=0.8)
        out += cv2.resize(s, (w, h)) * np.array([0.6, 0.75, 1.0], np.float32) * a.streak * 6
    return out


def grade(lin):
    # gentle S-curve in display space, slightly cool shadows and warm highlights
    d = to_disp(lin / (1 + 0.08 * lin))
    d = d + 0.035 * np.sin(np.pi * d) * (d - 0.5) * 2
    luma = d @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    sh = np.clip(1 - luma * 3, 0, 1)[..., None]
    d = d + sh * np.array([-0.004, 0.0015, 0.010], np.float32)
    d = luma[..., None] + (d - luma[..., None]) * 1.06
    return np.clip(d + 0.006, 0, 1)


rng = np.random.default_rng(1234)


def grain(d, idx):
    h, w = d.shape[:2]
    g = np.random.default_rng(idx * 7919 + 17).standard_normal((h // 2 + 1, w // 2 + 1)).astype(np.float32)
    g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
    luma = d @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    amt = (0.018 + 0.02 * np.sqrt(np.clip(luma, 0, 1)) * (1 - luma)) * a.grain
    return np.clip(d + (g * amt)[..., None], 0, 1)


def process(path, idx):
    raw = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if raw is None:
        raise SystemExit(f"unreadable frame {path}")
    img = raw.astype(np.float32) / (65535.0 if raw.dtype == np.uint16 else 255.0)
    alpha = None
    if img.shape[2] == 4:
        alpha = img[..., 3:4]
        img = img[..., :3]
    img = img[..., ::-1]
    if a.scale:
        W, H = map(int, a.scale.split("x"))
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_LANCZOS4)
        img = np.clip(img + 0.35 * (img - cv2.GaussianBlur(img, (0, 0), 1.0)), 0, 1)
        if alpha is not None:
            alpha = cv2.resize(alpha, (W, H), interpolation=cv2.INTER_LANCZOS4)[..., None]
    lin = to_lin(img)
    lin = bloom(lin)
    if a.ca > 0:
        lin = chroma(lin)
    h, w = lin.shape[:2]
    lin = lin * vignette(h, w)
    d = to_disp(lin / (1 + 0.08 * lin)) if a.nograde else grade(lin)
    if a.grain > 0:
        d = grain(d, idx)
    return d, alpha


if a.still or a.keep_alpha:
    os.makedirs(a.dst if a.keep_alpha else os.path.dirname(a.dst) or ".", exist_ok=True)
    for i, f in enumerate(files):
        d, alpha = process(f, i)
        out = (d[..., ::-1] * 65535).astype(np.uint16)
        if a.keep_alpha and alpha is not None:
            out = np.dstack([out, (np.clip(alpha, 0, 1) * 65535).astype(np.uint16)])
        dst = a.dst if a.still else os.path.join(a.dst, os.path.basename(f))
        cv2.imwrite(dst, out)
    print("wrote", len(files))
    sys.exit(0)

first = cv2.imread(files[0], cv2.IMREAD_UNCHANGED)
h, w = first.shape[:2]
if a.scale:
    w, h = map(int, a.scale.split("x"))
ff = imageio_ffmpeg.get_ffmpeg_exe()
p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{w}x{h}", "-r", "24",
                      "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                      "-x264-params", "aq-mode=3", "-movflags", "+faststart", a.dst], stdin=subprocess.PIPE)
for i, f in enumerate(files):
    d, _ = process(f, a.start + i)
    p.stdin.write((d * 65535).astype("<u2").tobytes())
    if i % 48 == 0:
        print(f"post {os.path.basename(a.src)} {i}/{len(files)}", flush=True)
p.stdin.close()
p.wait()
if p.returncode:
    sys.exit("ffmpeg failed")
print("wrote", a.dst, len(files), "frames")
