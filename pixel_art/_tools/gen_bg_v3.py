"""Premium backgrounds v3 — richer skies with vertical gradients, cloud
bands, distant parallax silhouettes, aurora (snow), sunset ocean (beach).
worlds/<w>/bg_far.png + bg_mid.png @ 480x270 logical -> saved at that size.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw

ROOT = "/workspace/pixel_art/worlds"
W, H = 480, 270


def grad(pal):
    """pal: list of (y_frac, (r,g,b)) -> gradient image"""
    img = Image.new("RGB", (1, H))
    px = img.load()
    for y in range(H):
        f = y / H
        for i in range(len(pal) - 1):
            f0, c0 = pal[i]; f1, c1 = pal[i + 1]
            if f0 <= f <= f1:
                t = (f - f0) / max(1e-6, f1 - f0)
                px[0, y] = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
                break
    return img.resize((W, H))


def dither_sky(img, seed, density=0.05):
    rnd = random.Random(seed)
    px = img.load()
    for _ in range(int(W * H * density / 40)):
        x, y = rnd.randint(0, W - 1), rnd.randint(0, H - 1)
        r, g, b = px[x, y]
        amt = rnd.choice([-6, 6])
        px[x, y] = (max(0, min(255, r + amt)), max(0, min(255, g + amt)), max(0, min(255, b + amt)))
    return img


def clouds(draw, band_y, n, col, seed, stretch=(30, 90)):
    rnd = random.Random(seed)
    for _ in range(n):
        cx = rnd.randint(-20, W + 20); cy = band_y + rnd.randint(-14, 14)
        wdt = rnd.randint(*stretch); hgt = rnd.randint(10, 22)
        for lob in range(4):
            lx = cx + int(rnd.uniform(-wdt / 2, wdt / 2)); ly = cy + rnd.randint(-4, 4)
            draw.ellipse([lx, ly, lx + wdt // rnd.randint(2, 3), ly + hgt], fill=col)


# ------------------------------------------------------------------ MEADOW
far = grad([(0, (122, 196, 240)), (0.55, (176, 226, 248)), (0.8, (222, 244, 250)), (1, (206, 236, 210))])
d = ImageDraw.Draw(far)
dither_sky(far, 1)
clouds(d, 46, 7, (252, 253, 255, 210), 4)
clouds(d, 92, 5, (250, 251, 254, 150), 6, (50, 110))
# sun with halo
d.ellipse([370, 22, 420, 72], fill=(255, 246, 196, 255))
d.ellipse([360, 12, 430, 82], outline=(255, 250, 220, 90), width=6)
# far mountains/hills layered
for base, amp, col in ((200, 46, (168, 200, 214)), (214, 34, (140, 186, 168))):
    pts = [(0, H)]
    for x in range(0, W + 1, 8):
        y = base - abs(math.sin(x * 0.011 + base) * amp) - math.sin(x * 0.05) * 5
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=col)
# mid rolling hills w/ tree line
mid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dm = ImageDraw.Draw(mid)
pts = [(0, H)]
for x in range(0, W + 1, 6):
    y = 226 - abs(math.sin(x * 0.008 + 2) * 30) - math.sin(x * 0.09) * 4
    pts.append((x, y))
pts.append((W, H))
dm.polygon(pts, fill=(120, 190, 110, 255))
pts = [(0, H)]
for x in range(0, W + 1, 6):
    y = 246 - abs(math.sin(x * 0.013 + 5) * 18)
    pts.append((x, y))
pts.append((W, H))
dm.polygon(pts, fill=(96, 172, 92, 255))
# tiny distant trees on ridge
rnd = random.Random(9)
for _ in range(40):
    x = rnd.randint(0, W); y = 224 - abs(math.sin(x * 0.008 + 2) * 30) - math.sin(x * 0.09) * 4
    s = rnd.randint(5, 10)
    dm.polygon([(x, y - s * 2), (x - s // 2, y), (x + s // 2, y)], fill=(64, 132, 70, 255))
# floating island cluster (game motif)
for fx, fy, fs in ((90, 120, 1.0), (300, 96, 0.8), (410, 150, 0.6)):
    dm.ellipse([fx - 26 * fs, fy, fx + 26 * fs, fy + 16 * fs], fill=(120, 190, 110, 255))
    dm.polygon([(fx - 22 * fs, fy + 8 * fs), (fx + 22 * fs, fy + 8 * fs), (fx, fy + 34 * fs)],
               fill=(146, 108, 66, 255))
    dm.ellipse([fx - 26 * fs, fy - 4 * fs, fx + 26 * fs, fy + 8 * fs], fill=(150, 210, 130, 255))
    dm.arc([fx - 10 * fs, fy + 18 * fs, fx + 6 * fs, fy + 30 * fs], 0, 180, fill=(96, 172, 92, 200), width=2)
far.convert("RGBA").save(f"{ROOT}/classic_meadow/bg_far.png")
mid.save(f"{ROOT}/classic_meadow/bg_mid.png")

# -------------------------------------------------------------------- SNOW
far = grad([(0, (24, 34, 78)), (0.4, (58, 82, 140)), (0.75, (140, 170, 214)), (1, (214, 230, 246))])
d = ImageDraw.Draw(far)
dither_sky(far, 2)
# stars
rnd = random.Random(3)
for _ in range(90):
    x, y = rnd.randint(0, W), rnd.randint(0, 150)
    a = rnd.choice([(255, 255, 255, 220), (210, 230, 255, 160)])
    d.point((x, y), fill=a)
    if rnd.random() < 0.1:
        d.line([x - 2, y, x + 2, y], fill=a, width=1); d.line([x, y - 2, x, y + 2], fill=a, width=1)
# moon + glow
d.ellipse([380, 26, 428, 74], fill=(244, 248, 255, 255))
d.ellipse([388, 22, 434, 66], fill=(58, 82, 140, 255))
d.ellipse([368, 14, 440, 86], outline=(230, 240, 255, 40), width=8)
# aurora ribbons
for band, yy, alpha in ((0, 54, 70), (1, 74, 50), (2, 94, 36)):
    pts = []
    for x in range(0, W + 1, 8):
        pts.append((x, yy + math.sin(x * 0.02 + band * 2) * 16))
    ribbon = [(x, y - 12) for x, y in pts] + [(x, y + 16) for x, y in reversed(pts)]
    col = (100 + band * 30, 235, 190 - band * 20, alpha)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon(ribbon, fill=col)
    far = Image.alpha_composite(far.convert("RGBA"), ov)
    d = ImageDraw.Draw(far)
# jagged ice peaks
for base, amp, col in ((208, 60, (176, 200, 228)), (222, 40, (148, 176, 210))):
    pts = [(0, H)]
    x = 0
    up = True
    while x <= W:
        y = base - (amp if up else amp * 0.4) + math.sin(x * 0.3) * 3
        pts.append((x, y)); up = not up; x += 34
    pts.append((W, H))
    d.polygon(pts, fill=col)
mid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dm = ImageDraw.Draw(mid)
pts = [(0, H)]
for x in range(0, W + 1, 6):
    y = 232 - abs(math.sin(x * 0.01 + 1) * 22)
    pts.append((x, y))
pts.append((W, H))
dm.polygon(pts, fill=(226, 238, 250, 255))
# spruce silhouettes row
rnd = random.Random(7)
for _ in range(26):
    x = rnd.randint(0, W); y = 230 - abs(math.sin(x * 0.01 + 1) * 22) + rnd.randint(0, 8)
    s = rnd.randint(10, 20)
    dm.polygon([(x, y - s * 2), (x - s // 2, y), (x + s // 2, y)], fill=(38, 84, 74, 255))
    dm.polygon([(x, y - s * 2 + 4), (x - s // 3, y - s // 2), (x + s // 3, y - s // 2)], fill=(52, 108, 92, 255))
    dm.line([x - 2, y - s, x + 2, y - s], fill=(236, 244, 252, 255), width=2)
far.save(f"{ROOT}/snow_town/bg_far.png")
mid.save(f"{ROOT}/snow_town/bg_mid.png")

# ------------------------------------------------------------------- BEACH
far = grad([(0, (255, 150, 96)), (0.35, (255, 196, 120)), (0.6, (255, 228, 160)), (0.62, (250, 200, 120)), (1, (210, 120, 90))])
d = ImageDraw.Draw(far)
dither_sky(far, 3)
# big setting sun over sea line
sea_y = 168
d.ellipse([196, 96, 284, 184], fill=(255, 236, 150, 255))
d.ellipse([186, 86, 294, 194], outline=(255, 240, 180, 70), width=7)
# sun stripes behind clouds
for i, cy in enumerate((110, 132, 152)):
    d.rectangle([0, cy, W, cy + 6 + i * 2], fill=(255, 170, 110, 120))
# palms silhouette left
for px_, ph in ((30, 90), (58, 70)):
    d.line([px_, sea_y, px_ + 8, sea_y - ph], fill=(120, 60, 60, 255), width=5)
    for k in range(5):
        a = math.pi + k * math.pi / 5
        d.line([px_ + 8, sea_y - ph, px_ + 8 + 26 * math.cos(a), sea_y - ph + 16 * math.sin(a) - 6],
               fill=(120, 60, 60, 255), width=3)
# ocean band with shimmer
d.rectangle([0, sea_y, W, H], fill=(48, 128, 178, 255))
d.rectangle([0, sea_y, W, sea_y + 8], fill=(120, 190, 220, 255))
rnd = random.Random(11)
for _ in range(60):
    x, y = rnd.randint(0, W - 20), rnd.randint(sea_y + 10, 226)
    d.line([x, y, x + rnd.randint(8, 26), y], fill=(96, 176, 214, 255), width=2)
# sun glitter path on water
for gy in range(sea_y + 4, 230, 6):
    wdt = 30 - (gy - sea_y) // 6
    d.line([240 - wdt, gy, 240 + wdt, gy], fill=(255, 226, 150, 200), width=2)
# distant sailboats
for bx, by, bs in ((90, 186, 1.0), (370, 178, 0.8)):
    d.polygon([(bx, by - 14 * bs), (bx, by), (bx + 9 * bs, by)], fill=(252, 246, 232, 255))
    d.polygon([(bx - 6 * bs, by), (bx + 10 * bs, by), (bx + 6 * bs, by + 4), (bx - 4 * bs, by + 4)],
              fill=(120, 74, 40, 255))
mid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dm = ImageDraw.Draw(mid)
# near wave crest band (animated in engine via shader offset; static foam here)
pts = [(0, H)]
for x in range(0, W + 1, 6):
    pts.append((x, 236 + math.sin(x * 0.06) * 4))
pts.append((W, H))
dm.polygon(pts, fill=(66, 148, 214, 255))
for x in range(0, W, 3):
    y = 236 + math.sin(x * 0.06) * 4
    dm.line([x, y, x + 2, y], fill=(214, 240, 255, 255), width=2)
# wet sand strip
dm.rectangle([0, 250, W, H], fill=(214, 186, 120, 255))
dm.rectangle([0, 250, W, 253], fill=(246, 224, 158, 255))
far.save(f"{ROOT}/beach/bg_far.png")
mid.save(f"{ROOT}/beach/bg_mid.png")
print("backgrounds v3 ok")
