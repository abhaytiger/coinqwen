"""Footstep dust / kick-up puffs — one themed sheet per world, sized to match
the 48x56 hero frames so you can paste them straight under a character node.

Each file: 4 x 2 grid of 48x56 cells (same geometry as the hero sheets).
row0 = ground puff cycle (4 frames): tiny nudge -> billow -> drift -> fade
row1 = side-scatter cycle (4 frames): pebbles/spray thrown backward (to the
RIGHT of frame since characters face & walk left; mirror for rightward walk).

Palettes are matched to each world's ground:
  meadow : dry grass-dirt tans + stray leaf flecks
  snow   : powder-white puffs + ice chips
  beach  : pale gold sand grains + tiny water spray (for river/shore running)
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *
from PIL import ImageFilter as IF

OUT = "/workspace/pixel_art/effects"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)
W, H = 48, 56


def N():
    return Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))


def soft(img, r=1):
    return img.filter(IF.GaussianBlur(SCALE * r))


def puff(x0, y0, rad, col, spread=1.0):
    """One soft round puff at logical coords."""
    img = N()
    ellipse(img, x0 - rad, y0 - rad, x0 + rad, y0 + rad, col)
    return soft(img, 1)


def cloud(base_imgs, cx, cy, sizes, col):
    out = base_imgs
    for dx, dy, r in sizes:
        out = Image.alpha_composite(out, puff(cx + dx, cy + dy, r, col))
    return out


def grain_sheet(name, palette, chip_cols, seed=7, spray=False):
    """palette: list of RGBA dust tones (light->dark). chip_cols: solid debris bits."""
    rnd = random.Random(seed)
    rowA, rowB = [], []

    # ---------- row A: rising ground puff -------------------------------
    stages = [
        dict(n=2, rad=(2, 3), a=90, dy=0, sx=0),
        dict(n=4, rad=(3, 5), a=120, dy=-2, sx=3),
        dict(n=5, rad=(4, 6), a=80, dy=-5, sx=7),
        dict(n=4, rad=(3, 5), a=40, dy=-8, sx=10),
    ]
    for st in stages:
        img = N()
        for i in range(st["n"]):
            dx = 30 + rnd.randint(-3, 6) + st["sx"]          # behind the heel (char faces left)
            dy = 47 + rnd.randint(-2, 1) + st["dy"]
            r = rnd.randint(*st["rad"])
            col = palette[i % len(palette)]
            col = shade(col, da=int(st["a"] * (0.7 + rnd.random() * 0.5)))
            img = Image.alpha_composite(img, puff(dx, dy, r, col))
        # solid debris chips flying with the puff
        for i in range(2 + st["n"] // 2):
            cpx = 30 + rnd.randint(-2, 10) + st["sx"]
            cpy = 46 - rnd.randint(0, 6) + st["dy"] // 2
            px(img, cpx, cpy, chip_cols[rnd.randrange(len(chip_cols))])
        rowA.append(finalize_raw(img))

    # ---------- row B: backward scatter (pebbles / spray) ---------------
    for f in range(4):
        img = N()
        prog = f
        # small dust skirt stays under the foot
        img = Image.alpha_composite(img, puff(31 + prog * 2, 48 - prog, 3 + prog,
                                              shade(palette[0], da=70 - f * 18)))
        n_bits = 6 - f
        for i in range(n_bits):
            bx = 30 + prog * 4 + rnd.randint(-2, 4) + (i % 3) * 3
            by = 46 - prog * 3 - (i * 2) % 7
            c = chip_cols[rnd.randrange(len(chip_cols))]
            if spray and i % 3 == 0:                          # droplets for beach/river
                ellipse(img, bx, by, bx + 2, by + 3, (170, 220, 245, 210 - f * 40))
                px(img, bx, by, (240, 250, 255, 220))
            else:
                rect(img, bx, by, bx + 1, by + 1, c)
            if f >= 2:                                        # bits start falling back down
                px(img, bx + 1, by + 2, shade(c, da=-60))
        rowB.append(finalize_raw(img))

    sheet = Sheet(4, W, H, rows=2)
    for fr in rowA + rowB:
        sheet.add(fr.resize((W, H), Image.NEAREST))
    sheet.canvas.save(os.path.join(OUT, f"dust_{name}.png"))
    save_scaled(hframes(rowA), os.path.join(PREV, f"dust_{name}_puff@3x.png"), 3)
    save_scaled(hframes(rowB), os.path.join(PREV, f"dust_{name}_scatter@3x.png"), 3)
    print("dust ok:", name)


def finalize_raw(img):
    """no outline pass for translucent FX — just clamp alpha noise."""
    d = img.getdata()
    out = [(r, g, b, 0 if a < 12 else a) for r, g, b, a in d]
    img.putdata(out)
    return img


# ------------------------------------------------------------------ palettes
MEADOW_PAL = [(212, 186, 140, 255), (190, 162, 116, 255), (168, 140, 98, 255)]
MEADOW_CHIP = [(120, 96, 66, 255), (96, 148, 72, 255), (150, 120, 84, 255), (210, 176, 96, 255)]
SNOW_PAL = [(244, 249, 255, 255), (222, 234, 246, 255), (204, 218, 234, 255)]
SNOW_CHIP = [(198, 222, 244, 255), (232, 244, 255, 255), (176, 200, 226, 255)]
SAND_PAL = [(244, 224, 170, 255), (228, 202, 140, 255), (210, 180, 118, 255)]
SAND_CHIP = [(214, 186, 128, 255), (236, 214, 166, 255), (188, 158, 104, 255)]

grain_sheet("meadow", MEADOW_PAL, MEADOW_CHIP, seed=11)
grain_sheet("snow", SNOW_PAL, SNOW_CHIP, seed=23)
grain_sheet("beach", SAND_PAL, SAND_CHIP, seed=31, spray=True)
