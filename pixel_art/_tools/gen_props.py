"""Classic meadow props + shared decor: bushes, flowers(anim), rocks, clouds, wooden sign."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/props"
PREV = os.path.join(OUT, "previews")
for d in (OUT, PREV):
    os.makedirs(d, exist_ok=True)

GRASS = (96, 176, 84); GRASS_D = (58, 128, 62); GRASS_L = (146, 210, 116)
ROCK = (146, 142, 138); ROCK_D = (108, 104, 102); ROCK_L = (180, 176, 172)


def bush(w=28, h=16, col=GRASS, dk=GRASS_D, lt=GRASS_L):
    img = new(32, 24)
    x0 = 16 - w // 2; y1 = 22
    ellipse(img, x0, y1 - h, x0 + w - 1, y1 + h // 2, col)
    rect(img, x0, y1 - h // 2, x0 + w - 1, y1, col)
    for yy in range(y1 + 1, 32):
        pass
    ellipse(img, x0 + 3, y1 - h + 2, x0 + w // 2, y1 - h // 2, lt)
    ellipse(img, x0 + w - 8, y1 - 4, x0 + w - 2, y1, dk)
    rnd = random.Random(w * 7 + h)
    for _ in range(w):
        x = x0 + 1 + rnd.randrange(max(1, w - 2)); y = y1 - h + 1 + rnd.randrange(h)
        px(img, x, y, rnd.choice([dk, lt]))
    # trim below baseline y=22
    small = img.resize((32, 24), Image.NEAREST).convert("RGBA")
    for y in range(23, 24):
        for x in range(32):
            small.putpixel((x, y), (0, 0, 0, 0))
    return outline(small.resize((128, 96), Image.NEAREST), (36, 60, 40, 255))

save(bush(28, 14), os.path.join(OUT, "bush_small.png"))
save_scaled(bush(28, 14), os.path.join(PREV, "bush_small@3x.png"), 3)
save(bush(32, 18), os.path.join(OUT, "bush_large.png"))
save_scaled(bush(32, 18), os.path.join(PREV, "bush_large@3x.png"), 3)


def rock(size=14, seed=3):
    img = new(24, 24)
    rnd = random.Random(seed)
    cx, cy = 12, 16 - size // 3
    pts = []
    for i in range(8):
        a = math.pi + i * math.tau / 8
        r = size * (0.62 + rnd.random() * 0.38) if i % 2 else size * 0.9
        pts.append((cx + math.cos(a) * r, cy + abs(math.sin(a)) * r * 0.7))
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=ROCK)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts[:4]], fill=ROCK_L)
    d.line([(p[0] * SCALE, p[1] * SCALE) for p in pts[-2:] + pts[:2]], fill=ROCK_D, width=SCALE)
    return outline(img, (60, 58, 56, 255))

save(rock(10, 3), os.path.join(OUT, "rock_small.png"))
save(rock(16, 8), os.path.join(OUT, "rock_large.png"))
save_scaled(hframes([rock(10, 3), rock(16, 8)], 2), os.path.join(PREV, "rocks@4x.png"), 4)


def flower(petal=(240, 96, 120), sway=0):
    img = new(16, 16)
    stem_top = (8 + sway, 5)
    line(img, [(8, 15), (8 + sway // 2, 10), stem_top], (66, 130, 66), 1)
    px(img, 7 - sway // 2, 11, (96, 168, 90)); px(img, 9 + sway // 2, 9, (96, 168, 90))
    x, y = stem_top
    c = (250, 220, 90)
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        px(img, x + dx, y + dy, petal)
    px(img, x, y, c)
    return img

sh = Sheet(4, 16, 16)
for s in (0, 1, 0, -1):
    sh.add(flower(sway=s))
sh.save(os.path.join(OUT, "flowers_red.png"))
sh2 = Sheet(4, 16, 16)
for s in (0, 1, 0, -1):
    sh2.add(flower((120, 150, 240), s))
sh2.save(os.path.join(OUT, "flowers_blue.png"))
save_scaled(hframes([flower(sway=s) for s in (0, 1, 0, -1)], 1),
            os.path.join(PREV, "flowers@6x.png"), 6)


def cloud_prop():
    img = new(48, 24)
    for x0, y0, x1, y1 in [(4, 10, 20, 20), (12, 4, 30, 18), (24, 8, 40, 20), (32, 12, 44, 20)]:
        ellipse(img, x0, y0, x1, y1, (252, 252, 255, 245))
    rect(img, 6, 18, 42, 20, (226, 234, 246, 245))
    return img

cp = cloud_prop()
save(cp, os.path.join(OUT, "cloud_prop.png"))
save_scaled(cp, os.path.join(PREV, "cloud_prop@3x.png"), 3)


def wood_sign():
    img = new(32, 32)
    rect(img, 14, 16, 17, 30, (118, 84, 54)); rect(img, 14, 16, 14, 30, (92, 64, 40))
    rect(img, 4, 4, 27, 18, (178, 130, 80))
    rect(img, 4, 4, 27, 5, (206, 160, 104)); rect(img, 4, 17, 27, 18, (128, 92, 56))
    rect(img, 4, 4, 5, 18, (128, 92, 56)); rect(img, 26, 4, 27, 18, (128, 92, 56))
    for x in (8, 14, 20): px(img, x, 8, (100, 70, 44)); px(img, x + 1, 8, (100, 70, 44))
    line(img, [(8, 12), (12, 12), (14, 14)], (100, 70, 44), 1)   # arrow-ish doodle
    return outline(img, (70, 48, 30, 255))

ws = wood_sign()
save(ws, os.path.join(OUT, "wooden_sign.png"))
save_scaled(ws, os.path.join(PREV, "wooden_sign@4x.png"), 4)


def stump():
    img = new(24, 24)
    rect(img, 5, 10, 19, 21, (150, 108, 66))
    rect(img, 5, 10, 6, 21, (112, 78, 48)); rect(img, 18, 10, 19, 21, (112, 78, 48))
    ellipse(img, 4, 4, 20, 12, (196, 156, 104))
    ellipse(img, 7, 6, 17, 10, (172, 132, 86))
    ellipse(img, 9, 7, 15, 9, (196, 156, 104))
    px(img, 6, 16, (112, 78, 48)); px(img, 15, 19, (112, 78, 48))
    return outline(img, (66, 44, 28, 255))

stm = stump()
save(stm, os.path.join(OUT, "stump.png"))
save_scaled(stm, os.path.join(PREV, "stump@4x.png"), 4)
print("props ok")
