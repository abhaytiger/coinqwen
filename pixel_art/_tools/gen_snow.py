"""Snow Town: tileset, pine tree, snowman, icicles, present crate, milestone signpost."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/worlds/snow_town"
PREV = os.path.join(OUT, "previews")
for d in (OUT, PREV):
    os.makedirs(d, exist_ok=True)

SNOW = (236, 244, 252, 255); SNOW_D = (208, 222, 238, 255); SNOW_DD = (172, 192, 216, 255)
ICE = (150, 205, 235, 255); ICE_D = (100, 160, 205, 255)
BARK = (96, 70, 58, 255); BARK_D = (66, 46, 40, 255)
PINE = (58, 118, 92, 255); PINE_D = (38, 84, 68, 255)


# ------------------------------------------------------------- tileset 64x64
def tiles():
    # 1 grassy snow-topped ground
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, (120, 140, 160, 255))
    noise(t, 0, 4, 15, 15, [(104, 124, 146, 255), (136, 156, 176, 255)], .3, 1)
    rect(t, 0, 0, 15, 3, SNOW)
    for x, hgt in [(0,4),(1,3),(2,4),(3,5),(4,4),(5,3),(6,4),(7,5),(8,4),(9,3),(10,4),(11,5),(12,4),(13,3),(14,4),(15,5)]:
        rect(t, x, 0, x, hgt - 1, SNOW)
    rect(t, 0, 3, 15, 3, SNOW_D); 
    for x in range(0, 16, 3): px(t, x, 4 if x % 6 == 0 else 3, SNOW_D)
    noise(t, 2, 0, 14, 2, [(255, 255, 255, 255)], .18, 5)
    yield t
    # 2 underground ice/rock
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, (96, 112, 134, 255))
    noise(t, 0, 0, 15, 15, [(80, 96, 118, 255), (112, 128, 150, 255), (140, 180, 210, 255)], .35, 9)
    px(t, 4, 6, ICE); px(t, 5, 6, ICE); px(t, 4, 7, ICE_D); px(t, 11, 11, ICE); px(t, 10, 11, ICE_D)
    yield t
    # 3 pure snow drift
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, SNOW)
    noise(t, 0, 0, 15, 15, [(255, 255, 255, 255), SNOW_D], .22, 3)
    yield t
    # 4 frozen water
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, (86, 150, 200, 255))
    noise(t, 0, 0, 15, 15, [(110, 178, 222, 255), (70, 128, 180, 255)], .3, 11)
    line(t, [(2, 4), (6, 4), (9, 6), (13, 6)], (200, 235, 255, 200), 1)
    line(t, [(3, 11), (7, 11), (10, 13)], (200, 235, 255, 160), 1)
    yield t
    # 5 brick wall (house)
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, (150, 92, 74, 255))
    for y in range(0, 16, 4):
        rect(t, 0, y, 15, y, (108, 62, 50, 255))
        off = 0 if (y // 4) % 2 == 0 else 4
        for x in range(off, 16, 8):
            rect(t, x, y + 1, x, y + 3, (108, 62, 50, 255))
    noise(t, 0, 0, 15, 15, [(162, 104, 84, 255)], .15, 2)
    yield t
    # 6 wooden plank
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, (158, 116, 72, 255))
    for y in (0, 5, 10, 15): rect(t, 0, y, 15, y, (118, 82, 50, 255))
    noise(t, 0, 1, 15, 14, [(140, 100, 60, 255), (172, 130, 84, 255)], .18, 4)
    yield t
    # 7 cobble path under snow edges
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, (128, 122, 132, 255))
    for yy in range(0, 16, 4):
        for xx in range((yy // 4 % 2) * 2 - 2, 16, 6):
            rect(t, xx + 1, yy + 1, xx + 4, yy + 3, (148, 142, 152, 255))
            rect(t, xx + 1, yy + 1, xx + 4, yy + 1, (162, 156, 166, 255))
    yield t
    # 8 snow with carrot/green patch (decorative variant)
    t = new(16, 16)
    rect(t, 0, 0, 15, 15, SNOW)
    noise(t, 0, 0, 15, 15, [SNOW_D, (255, 255, 255, 255)], .25, 8)
    rect(t, 3, 10, 6, 12, (96, 150, 110, 255)); rect(t, 9, 5, 12, 7, (96, 150, 110, 255))
    yield t

sh = Sheet(8, 16, 16)
for t in tiles():
    sh.add(t)
sh.save(os.path.join(OUT, "tiles.png"))
save_scaled(sh.canvas, os.path.join(PREV, "tiles@4x.png"), 4)

# ------------------------------------------------------------- pine tree 32x48
def pine(seed=1):
    img = new(32, 48)
    rnd = random.Random(seed)
    rect(img, 14, 40, 17, 46, BARK)
    rect(img, 14, 40, 14, 46, BARK_D)
    layers = [(6, 38, 26), (8, 30, 22), (11, 22, 16), (14, 14, 10)]
    for x0, top, w in layers:
        cx = 16
        for yy in range(top, top + (x0 and 12 or 12)):
            pass
    # draw triangle layers manually
    def tri(top_y, bot_y, half):
        n = bot_y - top_y
        for i in range(n + 1):
            y = top_y + i
            hw = int(half * (i / n))
            rect(img, 16 - hw, y, 16 + hw, y, PINE)
            rect(img, 16 - hw, y, 16 - hw + max(1, hw // 3), y, PINE_D)  # left shade
    tri(10, 20, 6); tri(16, 29, 9); tri(25, 40, 12)
    # snow caps on layer bottoms
    for y, half in [(20, 6), (29, 9), (40, 12)]:
        rect(img, 16 - half, y - 1, 16 + half, y - 1, SNOW)
        for k in range(-half, half + 1, 3):
            px(img, 16 + k, y - 2, SNOW)
    rect(img, 14, 8, 18, 10, SNOW)   # top snow
    noise(img, 5, 22, 26, 39, [PINE_D], .12, seed)
    return img

p = pine()
save(p, os.path.join(OUT, "pine_tree.png"))
save_scaled(p, os.path.join(PREV, "pine_tree@3x.png"), 3)

# two pines cluster 64x48
cl = new(64, 48)
p2 = pine(7)
cl.paste(p.resize((128, 192), Image.NEAREST).crop((0, 0, 128, 192)).resize((96, 144), Image.LANCZOS).convert("RGBA"), (-16, 0), None)
cl2 = Image.new("RGBA", (64 * SCALE, 48 * SCALE), (0, 0, 0, 0))
a = pine(2).resize((96, 144), Image.NEAREST)   # small pine via re-draw? simpler: paste full twice
cl2.paste(pine(3).resize((128, 192), Image.NEAREST), (0, 0))
cl2.paste(pine(9).resize((128, 192), Image.NEAREST), (14 * SCALE, 6 * SCALE))
cluster = cl2.crop((0, 0, 64 * SCALE, 48 * SCALE))
save(cluster, os.path.join(OUT, "pine_cluster.png"))
save_scaled(cluster, os.path.join(PREV, "pine_cluster@3x.png"), 3)

# ------------------------------------------------------------- snowman 32x40
def snowman():
    img = new(32, 40)
    ellipse(img, 8, 24, 24, 39, SNOW); ellipse(img, 11, 12, 21, 24, SNOW)
    ellipse(img, 12, 3, 20, 12, SNOW)
    ellipse(img, 9, 25, 13, 28, SNOW_D)           # body shading
    ellipse(img, 12, 14, 14, 16, SNOW_D)
    rect(img, 14, 0, 18, 2, (40, 34, 48, 255))    # hat
    rect(img, 12, 2, 20, 3, (40, 34, 48, 255))
    rect(img, 14, 1, 18, 1, (180, 60, 60, 255))
    px(img, 14, 6, (40, 34, 48, 255)); px(img, 17, 6, (40, 34, 48, 255))  # eyes
    line(img, [(16, 8), (19, 9)], (240, 130, 50, 255), 1)                  # carrot nose
    px(img, 19, 9, (214, 100, 30, 255))
    for i, y in enumerate((15, 18, 21)):
        px(img, 16, y, (40, 34, 48, 255))                                   # buttons
    line(img, [(9, 16), (4, 11)], BARK, 1); line(img, [(4, 11), (3, 8)], BARK, 1)   # arms
    line(img, [(23, 16), (28, 12)], BARK, 1); line(img, [(28, 12), (29, 9)], BARK, 1)
    return outline(img, (120, 140, 165, 255))

sm = snowman()
save(sm, os.path.join(OUT, "snowman.png"))
save_scaled(sm, os.path.join(PREV, "snowman@3x.png"), 3)

# ------------------------------------------------------------- icicles 32x16
def icicles():
    img = new(32, 16)
    rect(img, 0, 0, 31, 2, SNOW_D)
    rnd = random.Random(4)
    x = 1
    while x < 31:
        L = rnd.choice([5, 8, 11, 6])
        for i in range(L):
            wdt = max(1, 3 - i // 3)
            rect(img, x, 2 + i, x + wdt - 1, 2 + i, ICE if i % 2 == 0 else ICE_D)
        x += rnd.choice([4, 5, 6])
    return img

ic = icicles()
save(ic, os.path.join(OUT, "icicles.png"))
save_scaled(ic, os.path.join(PREV, "icicles@4x.png"), 4)

# ------------------------------------------------------------- present crate 24x24
def present(col=(210, 70, 70), ribbon=(240, 210, 90)):
    img = new(24, 24)
    rect(img, 3, 6, 20, 21, col)
    rect(img, 3, 6, 20, 8, lighter(col, 30))
    rect(img, 2, 4, 21, 7, darker(col, 30))       # lid
    rect(img, 11, 4, 13, 21, ribbon)              # vertical ribbon
    rect(img, 2, 11, 21, 13, ribbon)              # horizontal
    rect(img, 9, 1, 15, 4, ribbon)                # bow
    px(img, 10, 2, darker(ribbon, 40)); px(img, 14, 2, darker(ribbon, 40))
    return outline(img, (40, 30, 40, 255))

pr = present()
save(pr, os.path.join(OUT, "present_crate.png"))
save_scaled(pr, os.path.join(PREV, "present_crate@4x.png"), 4)

# ------------------------------------------------------------- milestone sign 48x32
def sign(text_dots):
    img = new(48, 32)
    rect(img, 22, 16, 25, 30, BARK); rect(img, 22, 16, 22, 30, BARK_D)
    rect(img, 4, 2, 44, 18, (196, 150, 96, 255))
    rect(img, 4, 2, 44, 3, (222, 180, 124, 255))
    rect(img, 4, 17, 44, 18, (150, 108, 66, 255))
    rect(img, 4, 2, 5, 18, (150, 108, 66, 255))
    rect(img, 43, 2, 44, 18, (150, 108, 66, 255))
    rect(img, 6, 3, 14, 6, SNOW)                  # snow on sign top
    for x, y in text_dots:
        rect(img, x, y, x + 1, y + 1, (90, 60, 40, 255))
    return outline(img, (60, 42, 30, 255))

dots = []
for i in range(6):                                # three coins icon row
    dots += [(12 + i * 6, 9)]
sg = sign(dots)
save(sg, os.path.join(OUT, "milestone_sign.png"))
save_scaled(sg, os.path.join(PREV, "milestone_sign@3x.png"), 3)
print("snow ok")
