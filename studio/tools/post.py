"""Turn raw Cycles bakes (float .npy) into web lightmaps.
Encoding: out = (clamp(irradiance / RANGE, 0, 1)) ** (1/2.2), stored as WebP. The page decodes pow(c, 2.2) * RANGE."""
import json, pathlib, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "raw", ROOT / "baked"
RANGE = {"W": 6.0, "P": 6.0, "B": 2.0}
meta = {"range": RANGE, "maps": {}}
for g in (0, 1):
    for s in ("W", "P", "B"):
        p = RAW / f"lm{g}_{s}_dn.npy"
        if not p.exists():
            p = RAW / f"lm{g}_{s}.npy"
        if not p.exists():
            continue
        a = np.load(p)
        a = np.nan_to_num(a, nan=0.0, posinf=RANGE[s], neginf=0.0)
        lum = a.mean(axis=2)
        nz = lum[lum > 0]
        pct = np.percentile(nz, [50, 90, 99, 99.9]) if nz.size else [0, 0, 0, 0]
        enc = np.clip(a / RANGE[s], 0, 1) ** (1 / 2.2)
        im = Image.fromarray((enc * 255 + 0.5).astype(np.uint8))
        name = f"lm{g}_{s}.webp"
        im.save(OUT / name, "WEBP", quality=92, method=6)
        meta["maps"][f"{g}{s}"] = name
        print(f"{name}: {im.size} p50={pct[0]:.3f} p90={pct[1]:.3f} p99={pct[2]:.3f} p99.9={pct[3]:.3f} clipped={(a.max(axis=2) > RANGE[s]).mean() * 100:.2f}% size={(OUT / name).stat().st_size // 1024}KB")
(OUT / "meta.json").write_text(json.dumps(meta))
if "--sheet" in sys.argv:
    tiles = [Image.open(OUT / f"lm{g}_{s}.webp").resize((512, 512)) for s in ("W", "P") for g in (0, 1)]
    sheet = Image.new("RGB", (1024, 1024))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * 512, (i // 2) * 512))
    sheet.save(RAW / "sheet.jpg", quality=85)
