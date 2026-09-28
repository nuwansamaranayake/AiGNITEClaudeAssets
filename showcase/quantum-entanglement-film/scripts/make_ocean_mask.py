"""Ocean mask (for sun glint roughness) derived from the NASA Blue Marble day map."""
import pathlib, cv2, numpy as np
TEX = pathlib.Path(__file__).resolve().parents[1] / "tex"
d = cv2.imread(str(TEX / "earth_day.jpg")).astype(np.float32) / 255
b, g, r = d[..., 0], d[..., 1], d[..., 2]
m = ((b > r + 0.04) & (b > g - 0.02) & (d.max(-1) < 0.45)).astype(np.float32)
m = cv2.GaussianBlur(m, (0, 0), 1.2)
cv2.imwrite(str(TEX / "earth_ocean_mask.png"), (m * 255).astype(np.uint8))
print("ocean fraction", round(float(m.mean()), 3))
