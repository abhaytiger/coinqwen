"""Beach world: tileset, palm tree, crab (walk+snap), shell & starfish collectibles,
beach umbrella, barrel, waves FX."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/worlds/beach"
PREV = os.path.join(OUT, "previews")
for d in (OUT, PREV):
    os.makedirs(d, exist_ok=True)

SAND = (240, 214, 160); SAND_D = (214, 182, 122); SAND_L = (252, 234, 190)
WET = (206, 178, 122); WOOD = (150, 108, 66); WOOD_D = (112, 78, 48)
LEAF = (72, 168, 92); LEAF_D = (44, 122, 66); TRUNK = (168, 122, 72); TRUNK_D = (128, 88, 52)


def tiles():
    t = new(16, 16); rect(t, 0, 0, 15, 15, SAND)
    noise(t, 0, 0, 15, 15, [SAND_D, SAND_L], .28, 2); yield t                    # dry sand
    t = new(16, 16); rect(t, 0, 0, 15, 15, WET)
    noise(t, 0, 0, 15, 15, [(188, 160, 106, 255), (222, 196, 140, 255)], .25, 5)
    rect(t, 0, 0, 15, 1, SAND); yield t                                          # wet sand edge
    t = new(16, 16); rect(t, 0, 0, 15, 15, (58, 158, 190, 255))                  # sea
    noise(t, 0, 0, 15, 15, [(44, 138, 172, 255), (96, 190, 214, 255)], .3, 7)
    line(t, [(1, 3), (4, 3), (6, 5), (9, 5)], (178, 230, 244, 255), 1)
    line(t, [(8, 11), (11, 11), (13, 13)], (148, 210, 230, 255), 1); yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, (128, 122, 116, 255))                 # rock
    noise(t, 0, 0, 15, 15, [(104, 98, 94, 255), (150, 144, 136, 255)], .35, 9)
    rect(t, 2, 2, 6, 3, (168, 162, 154, 255)); yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, WOOD)                                 # dock plank
    for y in (0, 7, 15): rect(t, 0, y, 15, y, WOOD_D)
    noise(t, 0, 1, 15, 6, [(138, 98, 58, 255)], .18, 3)
    px(t, 2, 3, WOOD_D); px(t, 13, 3, WOOD_D); px(t, 2, 11, WOOD_D); px(t, 13, 11, WOOD_D); yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, SAND)                                 # sand w/ pebbles
    noise(t, 0, 0, 15, 15, [SAND_D, SAND_L], .25, 11)
    ellipse(t, 3, 9, 5, 11, (168, 150, 128, 255)); px(t, 11, 4, (150, 134, 116, 255)); yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, (94, 178, 96, 255))                   # beach grass
    rnd = random.Random(4)
    for i in range(14):
        x = rnd.randrange(16); h = rnd.choice([4, 6, 8])
        line(t, [(x, 15), (x + rnd.choice((-1, 0, 1)), 15 - h)], LEAF if rnd.random() < .5 else LEAF_D, 1)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, (250, 246, 236, 255))                 # foam
    noise(t, 0, 0, 15, 15, [(214, 236, 244, 255), (180, 220, 235, 255)], .3, 6)
    yield t

sh = Sheet(8, 16, 16)
for t in tiles(): sh.add(t)
sh.save(os.path.join(OUT, "tiles.png"))
save_scaled(sh.canvas, os.path.join(PREV, "tiles@4x.png"), 4)

# ------------------------------------------------------------- palm tree 48x64
def palm(seed=2):
    img = new(48, 64)
    rnd = random.Random(seed)
    # curved trunk
    pts = [(22, 62)]
    x, y = 22, 62
    while y > 18:
        x += 1 if y % 8 < 4 else 0
        y -= 3
        pts.append((x, y))
    line(img, pts, TRUNK, 3)
    for i, (px_, py_) in enumerate(pts):
        px(img, px_ + 1, py_, TRUNK_D)
        if i % 2 == 0: px(img, px_ - 1, py_, lighter(TRUNK, 24))
    top = pts[-1]
    cx, cy = top
    # coconuts
    ellipse(img, cx - 4, cy + 2, cx, cy + 6, (120, 84, 52, 255))
    ellipse(img, cx + 2, cy + 3, cx + 6, cy + 7, (104, 72, 44, 255))
    # fronds: 6 arcs
    import math
    for k in range(6):
        a = math.pi * (0.08 + 0.84 * k / 5)
        ex = cx + math.cos(a) * 16 * (1 if k % 2 == 0 else -1) * (k < 3 or True)
        # build drooping frond
        dirx = 1 if k % 2 == 0 else -1
        span = [14, 18, 12][k % 3]
        fx, fy = cx, cy
        for i in range(span):
            fx += dirx
            fy = cy - int(6 * math.sin(i / span * math.pi)) + (i * i) // (span * 2)
            px(img, fx, fy, LEAF)
            px(img, fx, fy + 1, LEAF_D)
            if i % 3 == 1:
                px(img, fx + dirx, fy - 1, LEAF)
    px(img, cx, cy - 1, LEAF_D); px(img, cx - 1, cy, LEAF_D)
    return outline(img, (40, 60, 40, 255))

pm = palm()
save(pm, os.path.join(OUT, "palm_tree.png"))
save_scaled(pm, os.path.join(PREV, "palm_tree@3x.png"), 3)

# ------------------------------------------------------------- crab 32x24, 6 frames
CRAB = (228, 92, 64); CRAB_D = (178, 58, 44); CRAB_L = (252, 148, 110)

def crab(step=0, snap=False):
    img = new(32, 24)
    body_y = 8
    ellipse(img, 8, body_y, 24, 18, CRAB)
    ellipse(img, 9, body_y + 1, 15, body_y + 4, CRAB_L)          # shine
    ellipse(img, 10, 15, 22, 18, CRAB_D)                          # lower shade
    rect(img, 8, body_y, 24, 18, (0,0,0,0)) if False else None
    # eyes on stalks
    for ex in (12, 19):
        rect(img, ex, body_y - 3, ex + 1, body_y - 1, CRAB_D)
        rect(img, ex, body_y - 5, ex + 2, body_y - 3, (255, 255, 255, 255))
        px(img, ex + 1, body_y - 4, (30, 30, 40, 255))
    # legs (3 per side), animated
    for i in range(3):
        ph = (step + i) % 3
        ly = 13 + i
        line(img, [(9, ly), (5 - ph, ly + 3)], CRAB_D, 1)
        line(img, [(23, ly), (27 + ph, ly + 3)], CRAB_D, 1)
    # claws
    open_ = 2 if snap else 0
    rect(img, 1, 8 - step % 2, 6, 12 - step % 2, CRAB)           # left claw
    rect(img, 1, 6 - step % 2, 3, 8 - step % 2, CRAB_L)
    rect(img, 4, 5 - open_, 7, 8 - open_, CRAB)                  # pincer upper
    rect(img, 4, 9, 7, 11, CRAB_D)                               # pincer lower
    rect(img, 25, 8 + step % 2, 30, 12 + step % 2, CRAB)
    rect(img, 28, 6 + step % 2, 30, 8 + step % 2, CRAB_L)
    rect(img, 25, 5 + open_, 28, 8 + open_, CRAB)
    rect(img, 25, 9, 28, 11, CRAB_D)
    return outline(img, (90, 30, 26, 255))

frames = [crab(0), crab(1), crab(2), crab(0, True), crab(1), crab(2)]
sh = Sheet(6, 32, 24)
for f in frames: sh.add(f)
sh.save(os.path.join(OUT, "crab.png"))
save_scaled(hframes(frames, 1), os.path.join(PREV, "crab@3x.png"), 3)

# ------------------------------------------------------------- shells & starfish
def shell(col=(250, 200, 210), col_d=(214, 140, 160)):
    img = new(24, 24)
    ellipse(img, 3, 5, 21, 22, col)
    rect(img, 3, 16, 21, 22, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.pieslice([3 * SCALE, 5 * SCALE, 21 * SCALE, 23 * SCALE], 180, 360, fill=col)
    for ang in range(-60, 61, 20):                                # ribs
        import math
        a = math.radians(ang - 90)
        x0, y0 = 12, 21
        for r in range(2, 15, 2):
            px(img, int(x0 + math.cos(a + math.pi / 2) * r * 0 + math.sin(-a) * r) + 12 - 12 + int(math.sin(-a) * r), 
               int(y0 - abs(math.cos(a)) * r), col_d)
    d.pieslice([3 * SCALE, 5 * SCALE, 21 * SCALE, 23 * SCALE], 180, 360, outline=col_d, width=SCALE)
    rect(img, 10, 19, 14, 21, col_d)                              # hinge
    px(img, 11, 20, (255, 255, 255, 200))
    return outline(img, (140, 80, 96, 255))

s1 = shell(); s2 = shell((250, 226, 170), (208, 160, 90))
save(s1, os.path.join(OUT, "shell_pink.png")); save_scaled(s1, os.path.join(PREV, "shell_pink@4x.png"), 4)
save(s2, os.path.join(OUT, "shell_yellow.png")); save_scaled(s2, os.path.join(PREV, "shell_yellow@4x.png"), 4)

def starfish(col=(250, 130, 70)):
    img = new(24, 24)
    import math
    cx = cy = 11
    pts = []
    for i in range(10):
        r = 10 if i % 2 == 0 else 4
        a = math.tau * i / 10 - math.pi / 2
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=col)
    for i in range(0, 10, 2):
        a = math.tau * i / 10 - math.pi / 2
        for r in (5, 7):
            px(img, int(cx + math.cos(a) * r), int(cy + math.sin(a) * r), lighter(col, 40))
    px(img, cx, cy, darker(col, 40))
    return outline(img, (150, 60, 40, 255))

st = starfish()
save(st, os.path.join(OUT, "starfish.png")); save_scaled(st, os.path.join(PREV, "starfish@4x.png"), 4)

# ------------------------------------------------------------- umbrella 32x48
def umbrella():
    img = new(32, 48)
    rect(img, 15, 12, 16, 46, WOOD)                               # pole
    rect(img, 15, 12, 15, 46, lighter(WOOD, 24))
    d = ImageDraw.Draw(img)
    d.pieslice([2 * SCALE, 4 * SCALE, 30 * SCALE, 26 * SCALE], 180, 360, fill=(236, 84, 84, 255))
    for i, seg in enumerate([(20, 220), (110, 250)]):             # white wedges
        d.pieslice([2 * SCALE, 4 * SCALE, 30 * SCALE, 26 * SCALE], *seg, fill=(250, 244, 232, 255))
    d.pieslice([2 * SCALE, 4 * SCALE, 30 * SCALE, 26 * SCALE], 180, 360, outline=(150, 50, 50, 255), width=SCALE)
    for x in (2, 15, 29):                                         # scallops
        px(img, x, 16, (250, 244, 232, 255)); px(img, x, 17, (236, 84, 84, 255))
    rect(img, 2, 15, 29, 16, (190, 60, 60, 255))
    px(img, 15, 2, (240, 210, 90, 255)); px(img, 16, 2, (240, 210, 90, 255))
    px(img, 15, 1, (240, 210, 90, 255)); px(img, 16, 1, (240, 210, 90, 255))
    return outline(img, (90, 40, 40, 255))

ub = umbrella()
save(ub, os.path.join(OUT, "umbrella.png")); save_scaled(ub, os.path.join(PREV, "umbrella@3x.png"), 3)

# ------------------------------------------------------------- barrel 24x24
def barrel():
    img = new(24, 24)
    rect(img, 4, 3, 20, 21, (178, 128, 78, 255))
    for x in (7, 11, 15, 18): rect(img, x, 3, x, 21, (148, 104, 60, 255))
    rect(img, 4, 6, 20, 8, (96, 118, 138, 255))                  # metal bands
    rect(img, 4, 16, 20, 18, (96, 118, 138, 255))
    rect(img, 4, 3, 20, 4, (200, 156, 100, 255))
    rect(img, 4, 20, 20, 21, (128, 88, 52, 255))
    ellipse(img, 8, 0, 16, 4, (214, 172, 116, 255))              # lid top
    return outline(img, (60, 40, 28, 255))

br = barrel()
save(br, os.path.join(OUT, "barrel.png")); save_scaled(br, os.path.join(PREV, "barrel@4x.png"), 4)

# ------------------------------------------------------------- wave FX 48x16 x4
import math
sh = Sheet(4, 48, 16)
for ph in range(4):
    img = new(48, 16)
    for x in range(48):
        y = 8 + int(2.5 * math.sin((x + ph * 4) * math.tau / 24))
        rect(img, x, y, x, 15, (58, 158, 190, 255))
        rect(img, x, y, x, y + 1, (250, 250, 250, 255))
        rect(img, x, y + 2, x, y + 3, (188, 228, 240, 255))
    sh.add(img)
sh.save(os.path.join(OUT, "waves.png"))
print("beach ok")
