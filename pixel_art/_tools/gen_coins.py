"""Coins per world (spin/idle sparkle anims), gem, heart, coin pile + pickup FX."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/coins"
FXD = os.path.join(OUT, "effects")
PREV = os.path.join(OUT, "previews")
for d in (OUT, FXD, PREV):
    os.makedirs(d, exist_ok=True)

WORLD = {
    "classic": dict(face=(250, 204, 80), hi=(255, 240, 170), lo=(190, 130, 30),
                    edge=(140, 90, 20), sym=(200, 140, 30)),
    "snow":    dict(face=(206, 232, 250), hi=(255, 255, 255), lo=(140, 180, 214),
                    edge=(88, 120, 156), sym=(96, 150, 200)),   # ice token w/ snowflake
    "beach":   dict(face=(252, 186, 120), hi=(255, 232, 200), lo=(214, 120, 70),
                    edge=(150, 70, 40), sym=(230, 90, 70)),     # sand dollar coin
}


def coin_face(C, symbol="star"):
    img = new()
    ellipse(img, 7, 6, 24, 25, C["edge"])            # rim
    ellipse(img, 8, 7, 23, 24, C["face"])            # face
    ellipse(img, 9, 8, 14, 11, C["hi"])              # top-left shine
    arc_shade(img, C)
    if symbol == "star":
        for x, y in [(16,11),(16,12),(15,13),(16,13),(17,13),(14,14),(15,14),(16,14),
                     (17,14),(18,14),(15,15),(16,15),(17,15),(14,16),(15,16),(17,16),
                     (18,16),(13,17),(14,17),(18,17),(19,17),(14,18),(16,18),(18,18),
                     (13,19),(16,19),(19,19)]:
            px(img, x, y, C["sym"])
    elif symbol == "snow":
        for y in range(11, 21): px(img, 16, y, C["sym"]); px(img, 15, y, C["sym"])
        for x in range(11, 21): px(img, x, 15, C["sym"]); px(img, x, 16, C["sym"])
        for d in (-4, -3, 3, 4):
            px(img, 16 + d, 15 + d // 1, C["sym"]); px(img, 16 - d, 15 + d, C["sym"])
            px(img, 16 + d, 16 - d, C["sym"]); px(img, 16 - d, 16 - d, C["sym"])
    else:  # beach flower / sand dollar
        cx, cy = 16, 15
        for ang_i in range(8):
            import math
            a = ang_i * math.pi / 4
            for r in (2, 4):
                px(img, round(cx + math.cos(a) * r), round(cy + math.sin(a) * r), C["sym"])
        px(img, cx, cy, C["sym"]); px(img, cx + 1, cy, C["sym"])
    return img


def arc_shade(img, C):
    for x, y in [(22,10),(23,11),(23,12),(24,13),(24,14),(24,15),(24,16),(24,17),
                 (23,18),(23,19),(22,20),(21,21),(20,22),(19,22),(18,23),(17,23),
                 (16,23),(15,23),(14,22),(13,22)]:
        px(img, x, y, C["lo"])


def coin_edge(width):
    """side view of a coin; width in logical px"""
    img = new()
    w = max(2, width)
    x0 = 16 - w // 2
    rect(img, x0, 7, x0 + w - 1, 24, WORLD_EDGE_COL)
    rect(img, x0, 7, x0 + 1, 24, WORLD_HI_COL)
    rect(img, x0 + w - 1, 7, x0 + w - 1, 24, WORLD_LO_COL)
    return img


def coin_spin(C, symbol, widths=(14, 11, 7, 3, 7, 11)):
    """6-frame spin cycle: full face -> edges -> back-ish face -> ..."""
    frames = []
    globals()["WORLD_EDGE_COL"] = C["edge"]; globals()["WORLD_HI_COL"] = C["hi"]
    globals()["WORLD_LO_COL"] = C["lo"]
    frames.append(outline(coin_face(C, symbol)))
    frames.append(outline(coin_face(C, symbol)))          # hold face (sparkle differs)
    frames.append(outline(coin_edge(widths[1])))
    frames.append(outline(coin_edge(widths[3])))
    frames.append(outline(coin_edge(widths[1])))
    back = coin_face(C, symbol)
    back = flip_h(back)                                    # pseudo back side
    frames.append(outline(back))
    return frames


def add_sparkle(img, pts):
    small = img.resize((32, 32), Image.NEAREST).convert("RGBA")
    W = (255, 255, 255, 255)
    for x, y in pts:
        px(small, x, y, W)
    return small.resize((128, 128), Image.NEAREST)


for name, C in WORLD.items():
    sym = {"classic": "star", "snow": "snow", "beach": "flower"}[name]
    fr = coin_spin(C, sym)
    fr[1] = add_sparkle(fr[1], [(10, 5), (25, 9), (7, 18)])
    fr[5] = add_sparkle(fr[5], [(23, 22), (6, 8)])
    sh = Sheet(6, 32, 32)
    for f in fr:
        sh.add(f)
    sh.save(os.path.join(OUT, f"coin_{name}.png"))
    save_scaled(hframes(fr), os.path.join(PREV, f"coin_{name}_spin@3x.png"), 3)

# ---------------------------------------------------------- gem (milestone)
def gem():
    img = new()
    body = (110, 220, 235, 255); dk = (50, 140, 175, 255); lt = (220, 250, 255, 255)
    line(img, [(10, 8), (22, 8)], body, 1)
    poly = [(10, 8), (22, 8), (26, 14), (16, 26), (6, 14)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in poly], fill=body)
    d.polygon([(10 * SCALE, 8 * SCALE), (16 * SCALE, 14 * SCALE), (6 * SCALE, 14 * SCALE)], fill=lt)
    d.polygon([(22 * SCALE, 8 * SCALE), (16 * SCALE, 14 * SCALE), (26 * SCALE, 14 * SCALE)], fill=dk)
    d.polygon([(6 * SCALE, 14 * SCALE), (16 * SCALE, 14 * SCALE), (16 * SCALE, 26 * SCALE)], fill=shade(body, -20))
    d.line([(10 * SCALE, 8 * SCALE), (22 * SCALE, 8 * SCALE)], fill=lt, width=SCALE)
    px(img, 12, 10, lt); px(img, 13, 10, lt)
    return outline(img)

sh = Sheet(4, 32, 32)
g = gem()
sh.add(g); sh.add(add_sparkle(g, [(9, 6), (24, 16)])); sh.add(g)
sh.add(add_sparkle(g, [(20, 7), (7, 17), (25, 12)]))
sh.save(os.path.join(OUT, "gem_milestone.png"))
save_scaled(hframes([gem(), add_sparkle(gem(), [(9, 6), (24, 16)])]),
            os.path.join(PREV, "gem@3x.png"), 3)

# ---------------------------------------------------------- heart (hp)
def heart(col=(232, 76, 92)):
    img = new()
    dk = darker(col, 45); lt = lighter(col, 55)
    for x0, x1, y in [(10, 14, 9), (17, 21, 9), (9, 15, 10), (16, 22, 10),
                      (8, 23, 11), (8, 23, 12), (8, 23, 13), (9, 22, 14),
                      (10, 21, 15), (11, 20, 16), (12, 19, 17), (13, 18, 18),
                      (14, 17, 19), (15, 16, 20)]:
        rect(img, x0, y, x1, y, col)
    rect(img, 10, 10, 12, 11, lt); px(img, 9, 12, lt); px(img, 10, 12, lt)
    for x0, x1, y in [(8, 9, 13), (9, 10, 14), (10, 11, 15), (11, 12, 16),
                      (12, 13, 17), (13, 14, 18), (14, 15, 19), (15, 15, 20)]:
        rect(img, x0, y, x1, y, dk)
    return outline(img, (90, 24, 40, 255))

save(heart(), os.path.join(OUT, "heart.png"), 1)
save_scaled(heart(), os.path.join(PREV, "heart@4x.png"), 4)

# ---------------------------------------------------------- coin pile (UI/decor)
def pile():
    img = new(48, 32)
    C = WORLD["classic"]
    def one(x, y, s=6):
        ellipse(img, x, y, x + s * 2, y + s, C["edge"])
        ellipse(img, x + 1, y + 1, x + s * 2 - 1, y + s - 1, C["face"])
        px(img, x + 3, y + 2, C["hi"])
    one(4, 20); one(26, 20); one(15, 22); one(10, 13); one(22, 13); one(16, 6)
    return img

p = pile()
save_scaled(p, os.path.join(OUT, "coin_pile.png"), 1)
save_scaled(p, os.path.join(PREV, "coin_pile@3x.png"), 3)

# ---------------------------------------------------------- pickup FX (16x16, 4f)
def fx_ring(radius, alpha_col=(255, 226, 120)):
    img = new(16, 16)
    import math
    cx = cy = 7.5
    for i in range(12):
        a = i * math.tau / 12
        x = int(round(cx + math.cos(a) * radius)); y = int(round(cy + math.sin(a) * radius))
        px(img, x, y, alpha_col + (255,))
        px(img, x, y, (*alpha_col, 255))
    return img

def fx_star(t):
    img = new(16, 16)
    c = (255, 240, 170, 255)
    r = int(2 + t * 5)
    cx = cy = 7
    for k in range(-r, r + 1):
        px(img, cx + k, cy, c); px(img, cx, cy + k, c)
        if abs(k) <= r // 2:
            px(img, cx + k, cy - (r // 2 - abs(k)), c)
            px(img, cx + k, cy + (r // 2 - abs(k)), c)
    return img

sh = Sheet(4, 16, 16)
for i, r in enumerate((2, 4, 6, 7)):
    sh.add(fx_ring(r))
sh.save(os.path.join(FXD, "fx_coin_ring.png"))
sh2 = Sheet(4, 16, 16)
for t in (0, .33, .66, 1):
    sh2.add(fx_star(t))
sh2.save(os.path.join(FXD, "fx_coin_sparkle.png"))

def poof():
    frames = []
    import math
    rnd = random.Random(3)
    for step in range(4):
        img = new(16, 16)
        n = 6 + step * 3
        r = 2 + step * 1.6
        cols = [(235, 235, 245, 255 - step * 55), (200, 205, 220, 255 - step * 55),
                (255, 255, 255, 255 - step * 55)]
        for i in range(n):
            a = i * math.tau / n
            x = int(round(7 + math.cos(a) * r)); y = int(round(7 + math.sin(a) * r))
            px(img, x, y, rnd.choice(cols))
        if step < 2:
            px(img, 7, 7, (255, 255, 255, 255))
        frames.append(img)
    return frames

pf = poof()
sh3 = Sheet(4, 16, 16)
for f in pf: sh3.add(f)
sh3.save(os.path.join(FXD, "fx_poof.png"))
save_scaled(hframes(pf, 1), os.path.join(PREV, "fx_poof@4x.png"), 4)
print("coins ok")
