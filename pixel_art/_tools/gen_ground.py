"""Ground tilesets: grass (meadow), snow, sand — each a 4x2 sheet of 16x16 tiles.

Layout (index = row*4 + col):
  0 surface   1 fill      2 inner corner TL   3 outer corner TR
  4 edge L    5 edge R    6 inner corner BL   7 outer corner BR
Row 1 (8..15): same 8 tiles with a random seed -> seamless-looking variants.
Autotile mask bits (Godot TileSet terrain): TL=1 TR=2 BL=4 BR=8.
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/ground"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)

THEMES = {
    "grass": dict(top=(96, 176, 72), top_hi=(140, 208, 104), dirt=(134, 96, 60),
                 dirt_dk=(104, 72, 44), blade=(168, 220, 120), pebble=(112, 80, 52),
                 edge_col=(70, 120, 52)),
    "snow":  dict(top=(238, 246, 255), top_hi=(255, 255, 255), dirt=(196, 214, 236),
                 dirt_dk=(160, 182, 210), blade=(255, 255, 255), pebble=(176, 196, 220),
                 edge_col=(150, 175, 205)),
    "sand":  dict(top=(240, 214, 150), top_hi=(252, 236, 184), dirt=(216, 182, 118),
                 dirt_dk=(180, 148, 92), blade=(252, 240, 200), pebble=(190, 158, 100),
                 edge_col=(196, 164, 106)),
}


def base_fill(img, T, seed):
    """bulk (bottom) material with speckles."""
    rect(img, 0, 0, 15, 15, T["dirt"])
    noise(img, 0, 0, 15, 15, [T["dirt_dk"], T["pebble"]], density=0.10, seed=seed)


def surface(img, T, seed, cols=None):
    """draw the top layer over given columns; cols None = full width."""
    cols = cols if cols is not None else range(16)
    for x in cols:
        rect(img, x, 0, x, 2, T["top"])
        px(img, x, 3, T["top"] if random.Random(seed + x * 7).random() < 0.5 else T["dirt"])
    # highlight dapples on the cap
    rnd = random.Random(seed)
    for x in cols:
        if rnd.random() < 0.45:
            px(img, x, 0, T["top_hi"])
        if rnd.random() < 0.25:
            px(img, x, 1, T["top_hi"])


def tile_surface(T, seed):
    img = new(16, 16); img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
    base_fill(img, T, seed)
    surface(img, T, seed)
    # little blades / sparkles poking up
    rnd = random.Random(seed + 99)
    for _ in range(3):
        x = rnd.randrange(1, 15)
        px(img, x, rnd.randrange(0, 2), T["blade"])
    return img


def tile_fill(T, seed):
    img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
    base_fill(img, T, seed)
    return img


def tile_inner(T, seed, corners):
    """surface covers only the given corner cells region: corners='TL','TR','BL','BR'.
    Draws an L-shaped cap hugging that corner."""
    img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
    base_fill(img, T, seed)
    rnd = random.Random(seed)
    xs = range(0, 8) if "L" in corners else range(8, 16)
    ys = 0 if "T" in corners else 1
    if ys == 0:  # top corner: cap along top edge, tapering down at the side
        for i, x in enumerate(xs):
            d = abs(x - (7 if "L" in corners else 8))
            hgt = max(0, 3 - d // 2)
            for y in range(hgt + 1):
                px(img, x, y, T["top"] if y > 0 or rnd.random() < 0.6 else T["top_hi"])
    else:  # bottom corner: wrap the cap around the underside of the side edge
        for i, x in enumerate(xs):
            d = abs(x - (7 if "L" in corners else 8))
            hgt = max(0, 2 - d // 2)
            for y in range(15, 15 - hgt, -1):
                px(img, x, y, T["top"])
    return img


def tile_outer(T, seed, corner):
    """rounded corner where two capped edges meet: 'TL','TR','BL','BR'."""
    img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
    base_fill(img, T, seed)
    cx = 0 if corner.endswith("L") else 15
    cy = 0 if corner.startswith("T") else 15
    r = 6
    for y in range(0, 9):
        for x in range(0, 9):
            dx = (x - (r - 0.5)) * (-1 if cx == 0 else 1)
            dy = (y - (r - 0.5)) * (-1 if cy == 0 else 1)
            pass
    # simpler: quarter-disc of surface centred at the outer corner pixel
    for yy in range(16):
        for xx in range(16):
            ax = xx if cx == 0 else 15 - xx
            ay = yy if cy == 0 else 15 - yy
            dist = (ax - 5.5) ** 2 + (ay - 5.5) ** 2
            if dist <= 30:
                col = T["top"]
                if 22 < dist <= 30 and random.Random(xx * 31 + yy).random() < 0.5:
                    col = T["top_hi"]
                px(img, xx, yy, col)
            elif dist <= 38 and random.Random(xx * 17 + yy * 3).random() < 0.5:
                px(img, xx, yy, T["top"])
    return img


def tile_edge_side(T, seed, side):
    """vertical strip of surface on left or right edge (walls/eclipses)."""
    img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
    base_fill(img, T, seed)
    rnd = random.Random(seed)
    for y in range(16):
        w = 3 if rnd.random() < 0.7 else 2
        xs = range(0, w) if side == "L" else range(16 - w, 16)
        for x in xs:
            px(img, x, y, T["top"] if rnd.random() < 0.75 else T["top_hi"])
    return img


for name, T in THEMES.items():
    sh = Sheet(8, 16, 16, rows=2)
    seeds = [11, 12, 13, 14, 15, 16, 17, 18]
    order = [tile_surface(T, seeds[0]), tile_fill(T, seeds[1]),
             tile_inner(T, seeds[2], "TL"), tile_outer(T, seeds[3], "TR"),
             tile_edge_side(T, seeds[4], "L"), tile_edge_side(T, seeds[5], "R"),
             tile_inner(T, seeds[6], "BL"), tile_outer(T, seeds[7], "BR")]
    for t in order:
        sh.add(t)
    for i, t in enumerate(order):
        sh.add(tile_surface(T, 40 + i * 7) if i == 0 else
               tile_fill(T, 40 + i * 7) if i == 1 else t)
    canvas = sh.save(os.path.join(OUT, f"{name}.png"))
    save_scaled(canvas, os.path.join(PREV, f"{name}@4x.png"), 4)

# big decorative grass tuft + flower patch props for stage dressing
tuft = Image.new("RGBA", (16 * SCALE, 12 * SCALE), (0, 0, 0, 0))
g = THEMES["grass"]
for bx, hh, lean in ((3, 6, -1), (6, 9, 0), (9, 7, 1), (12, 5, 1)):
    for i in range(hh):
        px(tuft, bx + (i * lean) // 3, 11 - i, g["top"] if i % 2 else g["top_hi"])
save_scaled(tuft, os.path.join(OUT, "grass_tuft.png"), 1)
save_scaled(tuft, os.path.join(PREV, "grass_tuft@6x.png"), 6)

patch = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
rnd = random.Random(5)
for _ in range(14):
    x, y = rnd.randrange(1, 15), rnd.randrange(6, 15)
    px(patch, x, y, g["top"]); px(patch, x, y - 1, g["top_hi"])
for fx, fy, fc in ((4, 4, (240, 90, 110)), (9, 2, (255, 214, 90)), (12, 6, (170, 120, 230))):
    ellipse(patch, fx, fy, fx + 2, fy + 2, fc)
    px(patch, fx + 1, fy + 1, (255, 250, 220))
    px(patch, fx + 1, fy + 3, g["top"]); px(patch, fx + 1, fy + 4, g["top"])
save_scaled(patch, os.path.join(OUT, "flower_patch.png"), 1)
save_scaled(patch, os.path.join(PREV, "flower_patch@6x.png"), 6)

print("ground ok")
