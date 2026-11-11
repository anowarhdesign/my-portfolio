"""Procedural source textures for the studio scene. Run with system Python (numpy + Pillow).
Outputs to studio/tex/ (used by Blender and embedded in the glb) and studio/baked/ (wallpapers the page loads)."""
import math, pathlib, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEX = ROOT / "tex"; TEX.mkdir(exist_ok=True)
BAKED = ROOT / "baked"; BAKED.mkdir(exist_ok=True)
rng = np.random.default_rng(7)
random.seed(7)

def font(size, bold=True):
    for name in (["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def serif(size):
    for name in ["georgiai.ttf", "timesi.ttf"]:
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except OSError:
            pass
    return font(size)

def mono(size):
    for name in ["consolab.ttf", "consola.ttf", "cour.ttf"]:
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except OSError:
            pass
    return font(size)

def streaks(w, h, sx, sy):
    """Tileable-ish stretched noise in 0..1."""
    small = (rng.random((max(2, h // sy), max(2, w // sx))) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0

def wood(w, h, base, dark, planks=0, seed_shift=0.0):
    g = 0.55 * streaks(w, h, 256, 3) + 0.3 * streaks(w, h, 96, 2) + 0.15 * streaks(w, h, 24, 1)
    g = (g - g.min()) / (g.max() - g.min())
    base = np.array(base, np.float32); dark = np.array(dark, np.float32)
    img = base[None, None, :] * (1 - g[..., None]) + dark[None, None, :] * g[..., None]
    if planks:
        ph = h // planks
        for i in range(planks):
            tint = 0.9 + 0.2 * random.random()
            img[i * ph:(i + 1) * ph] *= tint
            img[i * ph:i * ph + 2] *= 0.45
            off = random.randint(0, w - 1)
            for x in (off, (off + w // 2 + random.randint(-60, 60)) % w):
                img[i * ph:(i + 1) * ph, x:x + 2] *= 0.5
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

wood(1024, 1024, (150, 108, 72), (96, 62, 38), planks=8).save(TEX / "floor.jpg", quality=88)
wood(1024, 256, (222, 190, 148), (188, 150, 106)).save(TEX / "birch.jpg", quality=88)
wood(512, 1024, (104, 60, 38), (78, 42, 26)).transpose(Image.ROTATE_90).filter(ImageFilter.GaussianBlur(1.2)).save(TEX / "walnut.jpg", quality=88)

# pegboard: 40mm cell, vertical slots in offset rows
T = 128
tile = Image.new("RGB", (T, T), (50, 50, 55))
d = ImageDraw.Draw(tile)
def slot(cx, cy):
    d.rounded_rectangle((cx - 8, cy - 24, cx + 8, cy + 24), 8, fill=(9, 9, 11))
    d.arc((cx - 8, cy + 8, cx + 8, cy + 24), 20, 160, fill=(86, 86, 94), width=2)
for cx, cy in [(32, 64), (96, 0), (96, 128)]:
    slot(cx, cy)
noise = (rng.random((T, T, 1)) * 8 - 4)
tile = Image.fromarray(np.clip(np.asarray(tile, np.float32) + noise, 0, 255).astype(np.uint8))
big = Image.new("RGB", (T * 2, T * 2))
for i in range(2):
    for j in range(2):
        big.paste(tile, (i * T, j * T))
big.save(TEX / "pegboard.png")

# book cover
bw, bh = 720, 500
book = Image.new("RGB", (bw, bh), (86, 82, 224))
d = ImageDraw.Draw(book)
for y in range(bh):
    d.line((0, y, bw, y), fill=(86 - y // 40, 82 - y // 36, 224 - y // 22))
d.text((54, 150), "Notes on", font=font(86), fill=(245, 244, 255))
d.text((54, 240), "interfaces", font=font(86), fill=(245, 244, 255))
d.rounded_rectangle((54, 96, 96, 138), 21, outline=(245, 244, 255), width=4)
d.text((54, 400), "Anowar Hossain", font=font(30, False), fill=(214, 212, 255))
d.line((54, 372, 300, 372), fill=(214, 212, 255), width=2)
book.save(TEX / "book.jpg", quality=90)

# dusk sky with hills and a lake, used behind the window and as a wallpaper
def dusk(w, h, lake=True):
    y = np.linspace(0, 1, h)[:, None]
    stops = [(0.0, (16, 20, 58)), (0.32, (58, 42, 110)), (0.52, (150, 70, 120)), (0.66, (238, 128, 78)), (0.74, (255, 190, 120))]
    img = np.zeros((h, w, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = ((y >= a) & (y <= b)).astype(np.float32)
        t = np.clip((y - a) / (b - a), 0, 1)
        img += m * (np.array(ca) * (1 - t) + np.array(cb) * t)[:, None, :].reshape(h, 1, 3) if False else 0
    # simple loop version (clear and exact)
    img = np.zeros((h, w, 3), np.float32)
    for row in range(h):
        t = row / (h - 1)
        col = stops[-1][1]
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= t <= b:
                k = (t - a) / (b - a)
                col = tuple(ca[i] * (1 - k) + cb[i] * k for i in range(3))
                break
        img[row] = col
    im = Image.fromarray(img.astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    # sun glow at the horizon
    glow = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w * 0.50, h * 0.56, w * 0.86, h * 0.92), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(w // 14))
    im = Image.composite(Image.new("RGB", (w, h), (255, 214, 150)), im, glow)
    d = ImageDraw.Draw(im, "RGBA")
    # a few stars
    for _ in range(90):
        x, yy = random.randint(0, w - 1), random.randint(0, int(h * 0.3))
        a = random.randint(60, 200)
        d.point((x, yy), fill=(255, 255, 255, a))
    # thin clouds
    for _ in range(7):
        cx, cy = random.randint(0, w), random.randint(int(h * 0.36), int(h * 0.6))
        cw = random.randint(w // 8, w // 3)
        d.ellipse((cx - cw, cy - 5, cx + cw, cy + 5), fill=(255, 170, 130, 46))
    horizon = int(h * 0.74)
    # hill layers
    for i, (colr, amp, base) in enumerate([((70, 52, 104), 0.07, 0.70), ((44, 36, 82), 0.09, 0.735), ((24, 22, 54), 0.06, 0.76)]):
        pts = [(0, h)]
        ph1, ph2 = random.random() * 6, random.random() * 6
        for x in range(0, w + 8, 8):
            u = x / w
            e = math.sin(u * 5.1 + ph1) * 0.5 + math.sin(u * 11.3 + ph2) * 0.28 + math.sin(u * 23 + i) * 0.1
            pts.append((x, (base - amp * (0.5 + 0.5 * e)) * h))
        pts.append((w, h))
        d.polygon(pts, fill=colr + (255,))
    if lake:
        top = int(h * 0.80)
        sky = im.crop((0, horizon - (h - top), w, horizon)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(3))
        lake_img = Image.blend(sky, Image.new("RGB", sky.size, (20, 22, 60)), 0.45)
        im.paste(lake_img, (0, top))
        d = ImageDraw.Draw(im, "RGBA")
        for _ in range(60):
            yy = random.randint(top + 4, h - 2); x = random.randint(0, w)
            d.line((x, yy, x + random.randint(20, 90), yy), fill=(255, 200, 150, 30))
        d.rectangle((0, top - 2, w, top + 1), fill=(18, 16, 44, 255))
    return im.filter(ImageFilter.GaussianBlur(0.6))

dusk(4096, 2560).resize((2048, 1280), Image.LANCZOS).save(TEX / "dusk_window.jpg", quality=90)
dusk(3840, 2160).resize((1920, 1080), Image.LANCZOS).save(BAKED / "wall_dusk.jpg", quality=86)

# fern wallpaper (Barnsley fern, layered), a nod to the real desk's wallpaper
def fern_points(n):
    x = y = 0.0
    out = np.empty((n, 2), np.float32)
    r = rng.random(n)
    for i in range(n):
        p = r[i]
        if p < 0.01:
            x, y = 0.0, 0.16 * y
        elif p < 0.86:
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif p < 0.93:
            x, y = 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else:
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        out[i] = (x, y)
    return out

def fern_wall(w, h):
    acc = np.zeros((h, w, 3), np.float32)
    yy = np.linspace(0, 1, h)[:, None, None]
    acc += np.array((6, 30, 34), np.float32) * (1 - yy) + np.array((3, 14, 20), np.float32) * yy
    pts = fern_points(260000)
    layers = [  # cx, cy, scale, angle, colour, blur
        (0.20, 1.10, 0.115, -0.5, (28, 110, 84), 5), (0.86, 1.05, 0.12, 0.6, (24, 96, 78), 5),
        (0.55, 1.18, 0.15, 0.12, (60, 190, 120), 0), (0.30, 1.02, 0.10, 0.35, (120, 220, 140), 0),
        (0.78, 0.98, 0.085, -0.3, (90, 205, 150), 0), (0.05, 0.9, 0.09, 0.9, (40, 150, 110), 2),
    ]
    for cx, cy, sc, ang, colr, blur in layers:
        ca, sa = math.cos(ang), math.sin(ang)
        px = pts[:, 0] * ca - pts[:, 1] * sa
        py = pts[:, 0] * sa + pts[:, 1] * ca
        X = (cx * w + px * sc * h).astype(np.int32)
        Y = (cy * h - py * sc * h).astype(np.int32)
        ok = (X >= 0) & (X < w) & (Y >= 0) & (Y < h)
        dens = np.zeros((h, w), np.float32)
        np.add.at(dens, (Y[ok], X[ok]), 1.0)
        dens = np.clip(dens / 3.0, 0, 1)
        m = Image.fromarray((dens * 255).astype(np.uint8))
        m = m.filter(ImageFilter.GaussianBlur(blur if blur else 0.7))
        a = np.asarray(m, np.float32)[..., None] / 255.0
        a = np.clip(a * (1.6 if blur else 1.25), 0, 1)
        shade = 0.55 + 0.45 * (1 - np.linspace(0, 1, h)[:, None, None])
        acc = acc * (1 - a) + np.array(colr, np.float32) * shade * a
    vx = np.linspace(-1, 1, w)[None, :, None]; vy = np.linspace(-1, 1, h)[:, None, None]
    acc *= np.clip(1.08 - 0.34 * (vx ** 2 + vy ** 2), 0, 1.1)
    return Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8))

fern_wall(1920, 1080).save(BAKED / "wall_fern.jpg", quality=86)

# ember wallpaper (site palette)
def ember_wall(w, h):
    x = np.linspace(0, 1, w)[None, :]; y = np.linspace(0, 1, h)[:, None]
    def blob(cx, cy, r):
        return np.exp(-(((x - cx) * w / h) ** 2 + (y - cy) ** 2) / (r * r))
    img = np.zeros((h, w, 3), np.float32) + np.array((14, 13, 12), np.float32)
    for cx, cy, r, colr in [(0.78, 0.2, 0.5, (241, 78, 28)), (0.15, 0.95, 0.45, (191, 58, 17)), (0.5, 0.55, 0.3, (255, 128, 85))]:
        img += blob(cx, cy, r)[..., None] * np.array(colr, np.float32) * 0.62
    img += (rng.random((h, w, 1)) - 0.5) * 6
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

ember_wall(1920, 1080).save(BAKED / "wall_ember.jpg", quality=86)

# paper wallpaper (site paper tone with a soft grid)
pw = Image.new("RGB", (1920, 1080), (244, 241, 235))
d = ImageDraw.Draw(pw)
for gx in range(0, 1920, 60):
    d.line((gx, 0, gx, 1080), fill=(232, 227, 218))
for gy in range(0, 1080, 60):
    d.line((0, gy, 1920, gy), fill=(232, 227, 218))
d.ellipse((1240, -260, 2100, 600), fill=(250, 226, 214))
pw = pw.filter(ImageFilter.GaussianBlur(1.2))
pw.save(BAKED / "wall_paper.jpg", quality=86)

# plaque: facts already public on the site
pl = Image.new("RGB", (640, 400), (22, 20, 19))
d = ImageDraw.Draw(pl)
d.rounded_rectangle((14, 14, 626, 386), 18, outline=(120, 112, 104), width=3)
d.text((320, 96), "TOP RATED", font=font(64), fill=(232, 228, 220), anchor="mm")
d.line((200, 150, 440, 150), fill=(241, 78, 28), width=4)
d.text((320, 208), "100% job success", font=font(40, False), fill=(214, 208, 198), anchor="mm")
d.text((320, 268), "2,237 hours  ·  399+ projects", font=font(28, False), fill=(170, 164, 154), anchor="mm")
d.text((320, 338), "ANOWAR HOSSAIN", font=mono(22), fill=(241, 78, 28), anchor="mm")
pl.save(TEX / "plaque.jpg", quality=90)

# typographic print: the site's own headline
pr = Image.new("RGB", (600, 800), (244, 241, 235))
d = ImageDraw.Draw(pr)
d.text((56, 250), "Design that", font=font(74), fill=(14, 13, 12))
d.text((56, 334), "earns trust.", font=font(74), fill=(14, 13, 12))
d.text((54, 440), "Built to keep it.", font=serif(78), fill=(191, 58, 17))
d.ellipse((56, 120, 96, 160), fill=(241, 78, 28))
d.text((56, 690), "ANOWAR HOSSAIN  /  UI·UX  /  WEBFLOW  /  AI", font=mono(17), fill=(78, 73, 69))
pr.save(TEX / "print_headline.jpg", quality=90)

# leaves: u across the blade, v from stem to tip
def leaf_tex(name, base, vein, edge, blotch=None, bands=None):
    w, h = 128, 256
    u = np.linspace(-1, 1, w)[None, :]; v = np.linspace(0, 1, h)[:, None]
    base = np.array(base, np.float32); vein = np.array(vein, np.float32); edge = np.array(edge, np.float32)
    img = np.ones((h, w, 3), np.float32) * base * (0.82 + 0.30 * v[..., None])
    side = np.abs(u)
    veins = np.exp(-((((v * 9.0 - side * 3.2) % 1.0) - 0.5) ** 2) / 0.006) * (side > 0.06) * (1 - side) * 0.35
    mid = np.exp(-(u ** 2) / 0.004) * 0.75
    k = np.clip(veins + mid, 0, 1)[..., None]
    img = img * (1 - k) + vein * k
    if blotch is not None:
        n = np.asarray(Image.fromarray((rng.random((10, 6)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        m = np.clip((n - 0.62) * 5, 0, 1)[..., None] * 0.7
        img = img * (1 - m) + np.array(blotch, np.float32) * m
    if bands is not None:
        n = np.asarray(Image.fromarray((rng.random((26, 3)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        m = np.clip((n - 0.5) * 4, 0, 1)[..., None] * 0.55
        img = img * (1 - m) + np.array(bands, np.float32) * m
    e = np.clip((side - 0.80) / 0.14, 0, 1)[..., None]
    img = img * (1 - e) + edge * e
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(TEX / name, quality=90)
leaf_tex("leaf.jpg", (52, 128, 62), (112, 176, 96), (38, 104, 52), blotch=(150, 190, 96))
leaf_tex("leaf_light.jpg", (104, 166, 78), (170, 208, 120), (84, 146, 66), blotch=(206, 216, 130))
leaf_tex("leaf_dark.jpg", (30, 88, 54), (52, 116, 70), (176, 170, 78), bands=(86, 140, 96))

print("textures written:", sorted(p.name for p in TEX.iterdir()), sorted(p.name for p in BAKED.iterdir()))
