"""MEGA ground tilesets v2 — 16x16 tiles, multi-row sheets, premium detail:
3-tone surface with dithered seams, grass blades / snow crust / sand ripples,
sub-surface dirt strata with pebbles & roots, depth shadow at bottom edge,
terrain-set-friendly autotile masks.

ground/mega_grass.png : 8 cols x 4 rows @16
  row0 surfaces (4 variants), row1 dirt fill w/ strata+pebbles (2) + blends(2)
  row2 inner corners TL TR BL BR   row3 edges L / R / single-blade top / floater
ground/mega_snow.png  : same layout, icy strata + sparkles
ground/mega_sand.png  : same layout, wet-sand underlayer + ripple lines
ground/water_river.png: 4 cols x 4 rows @16, 4-frame flow cycle per variant:
  row0 river flow, row1 lake bobbing surface, row2 shallow/edge blend, row3 waterfall
ground/water_deep.png : 2 cols x 4 rows @16 deep sea gradient bands (beach)
ground/cliff_*.png    : 3 cols x 2 rows @16 grass-on-rock cliff faces (top/side/bottom)
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *

OUT = "/workspace/pixel_art/ground"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)
S = 16  # logical tile


def T(seed):
    return Image.new("RGBA", (S * SCALE, S * SCALE), (0, 0, 0, 0)), random.Random(seed)


# ------------------------------------------------------------------ GRASS
GRASS_TOP = [(124, 196, 96, 255), (104, 178, 82, 255), (146, 214, 112, 255)]
GRASS_MID = (86, 152, 70, 255)
DIRT = [(134, 92, 58, 255), (112, 74, 46, 255), (154, 110, 70, 255)]
STRATA = (96, 62, 38, 255)
PEBBLE = (176, 152, 122, 255)


def grass_surface(seed, blades=1):
    img, rnd = T(seed)
    rect(img, 0, 3, S - 1, S - 1, GRASS_MID)
    rect(img, 0, 0, S - 1, 3, GRASS_TOP[0])
    # dithered seam between top band and mid
    for xx in range(S):
        if rnd.random() < 0.5:
            put(img, xx, 3, GRASS_TOP[2] if rnd.random() < .5 else GRASS_TOP[1])
    # tonal variation patches
    for _ in range(10):
        x, y = rnd.randint(0, S - 2), rnd.randint(4, S - 2)
        put(img, x, y, lighter(GRASS_MID, 14))
    for _ in range(8):
        x, y = rnd.randint(0, S - 1), rnd.randint(4, S - 1)
        put(img, x, y, darker(GRASS_MID, 16))
    # top highlight line + grass blades poking above
    for xx in range(S):
        if rnd.random() < 0.75:
            put(img, xx, 0, GRASS_TOP[2])
    for _ in range(3 + blades):
        bx = rnd.randint(0, S - 1)
        bh = rnd.choice([1, 1, 2])
        put(img, bx, 0, GRASS_TOP[1])
        if bh == 2 and bx > 0:
            put(img, bx - 1 if rnd.random() < .5 else bx + 1, 0, GRASS_TOP[2])
    # blade tips that break the silhouette on the TOP row only look good; keep inside tile
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 26)
    return img


def dirt_fill(seed, blend_top=False):
    img, rnd = T(seed)
    rect(img, 0, 0, S - 1, S - 1, DIRT[0])
    # strata bands
    for by in (5, 10):
        for xx in range(S):
            if rnd.random() < 0.8:
                put(img, xx, by + rnd.randint(0, 1), STRATA)
    # speckle tones
    for _ in range(26):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
        put(img, x, y, rnd.choice(DIRT + [darker(DIRT[1], 18)]))
    # pebbles (3px clusters w/ highlight)
    for _ in range(2):
        px_, py = rnd.randint(1, S - 3), rnd.randint(2, S - 3)
        rect(img, px_, py, px_ + 1, py, PEBBLE)
        px(img, px_, py + 1, darker(PEBBLE, 40)); px(img, px_ + 1, py + 1, darker(PEBBLE, 60))
        px(img, px_, py, lighter(PEBBLE, 25))
    # roots
    rx = rnd.randint(2, S - 4)
    line(img, [(rx, 0), (rx + 1, 3), (rx - 1, 6)], darker(DIRT[1], 30), 1)
    if blend_top:
        for xx in range(S):
            c = rnd.choice(GRASS_TOP + [GRASS_MID])
            put(img, xx, 0, c)
            if rnd.random() < 0.6:
                put(img, xx, 1, GRASS_MID if rnd.random() < .5 else rnd.choice(GRASS_TOP))
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 30)
    return img


def grass_corner(seed, tl=True):
    img = dirt_fill(seed)
    rnd = random.Random(seed + 99)
    # quarter disc of turf
    for yy in range(6):
        for xx in range(6):
            if (xx - (0 if tl else 5)) ** 2 + (yy - 0) ** 2 <= 26 or \
               (tl and xx <= 5 - yy) or (not tl and xx >= yy - 1):
                pass
    # simpler: paint triangular turf wedge
    for yy in range(5):
        if tl:
            xs = range(0, S - yy * 2 if yy < 4 else S)
        else:
            xs = range(yy * 2 if yy < 4 else 0, S)
        for xx in xs:
            put(img, xx, yy, GRASS_TOP[0] if yy < 3 else GRASS_MID)
    for xx in range(0, S, 2):
        put(img, xx, 0, GRASS_TOP[2])
    bottom_shade(img, 0, 3, S - 1, S - 1, None, 24)
    return img


def grass_edge_side(seed, left=True):
    img = dirt_fill(seed)
    for yy in range(S):
        if left:
            put(img, 0, yy, GRASS_MID); put(img, 1, yy, GRASS_TOP[1] if yy < 6 else darker(GRASS_MID, 10))
        else:
            put(img, S - 1, yy, GRASS_MID); put(img, S - 2, yy, GRASS_TOP[1] if yy < 6 else darker(GRASS_MID, 10))
    return img


# ------------------------------------------------------------------- SNOW
SNOW_TOP = [(240, 247, 253, 255), (222, 234, 246, 255), (255, 255, 255, 255)]
ICE_BAND = (186, 214, 238, 255)
FROST = [(150, 176, 210, 255), (126, 152, 190, 255), (170, 196, 226, 255)]


def snow_surface(seed):
    img, rnd = T(seed)
    rect(img, 0, 2, S - 1, S - 1, SNOW_TOP[0])
    rect(img, 0, 0, S - 1, 2, SNOW_TOP[2])
    # crust shading + sparkle dots
    for _ in range(14):
        x, y = rnd.randint(0, S - 1), rnd.randint(3, S - 1)
        put(img, x, y, SNOW_TOP[1])
    for _ in range(4):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 2)
        put(img, x, y, (255, 255, 255, 255))
    # blue shadow dimples
    for _ in range(5):
        x, y = rnd.randint(0, S - 2), rnd.randint(5, S - 2)
        px(img, x, y, ICE_BAND); px(img, x + 1, y, shade(ICE_BAND, da=140))
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 22)
    return img


def frost_fill(seed, blend_top=False):
    img, rnd = T(seed)
    rect(img, 0, 0, S - 1, S - 1, FROST[0])
    for by in (4, 9):
        for xx in range(S):
            if rnd.random() < 0.7:
                put(img, xx, by, FROST[1])
    for _ in range(20):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
        put(img, x, y, rnd.choice(FROST))
    # ice crystal shards
    for _ in range(2):
        cx, cy = rnd.randint(3, S - 4), rnd.randint(4, S - 3)
        px(img, cx, cy, (226, 242, 255, 255)); px(img, cx - 1, cy - 1, (226, 242, 255, 200))
        px(img, cx + 1, cy + 1, (226, 242, 255, 200)); px(img, cx, cy + 1, (255, 255, 255, 255))
    if blend_top:
        for xx in range(S):
            put(img, xx, 0, SNOW_TOP[rnd.randint(0, 1)])
            if rnd.random() < 0.5:
                put(img, xx, 1, SNOW_TOP[0])
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 26)
    return img


# -------------------------------------------------------------------- SAND
SAND_T = [(246, 224, 158, 255), (232, 206, 140, 255), (255, 240, 190, 255)]
SAND_M = (214, 186, 120, 255)
WETSAND = [(188, 156, 98, 255), (168, 136, 84, 255), (206, 176, 118, 255)]


def sand_surface(seed):
    img, rnd = T(seed)
    rect(img, 0, 0, S - 1, S - 1, SAND_T[0])
    # ripple arcs
    for _ in range(3):
        ry = rnd.randint(3, S - 2); rx = rnd.randint(0, S - 6)
        line(img, [(rx, ry), (rx + 2, ry - 1), (rx + 4, ry)], SAND_T[1], 1)
    for _ in range(16):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
        put(img, x, y, rnd.choice([SAND_T[2], SAND_M]))
    # shells grit
    for _ in range(2):
        x, y = rnd.randint(1, S - 2), rnd.randint(2, S - 2)
        px(img, x, y, (255, 250, 240, 255))
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 20)
    return img


def wetsand_fill(seed, blend_top=False):
    img, rnd = T(seed)
    rect(img, 0, 0, S - 1, S - 1, WETSAND[0])
    for _ in range(18):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
        put(img, x, y, rnd.choice(WETSAND))
    # wet shine streaks
    for _ in range(2):
        yy = rnd.randint(2, S - 2)
        for xx in range(rnd.randint(0, 6), min(S, rnd.randint(8, 15))):
            put(img, xx, yy, lighter(WETSAND[2], 18))
    if blend_top:
        for xx in range(S):
            put(img, xx, 0, SAND_T[1]); put(img, xx, 1, WETSAND[2] if rnd.random() < .5 else SAND_M)
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 26)
    return img


# ------------------------------------------------------------------- WATER
W_DEEP = (40, 108, 176, 255)
W_MID = (66, 148, 214, 255)
W_HI = (120, 190, 240, 255)
W_FOAM = (214, 240, 255, 255)


def water_tile(kind, frame, seed=4):
    img, rnd = T(seed + frame * 31)
    rect(img, 0, 0, S - 1, S - 1, W_MID)
    off = frame * 2
    if kind == "river":
        # flowing diagonal current lines scrolling right->left
        rect(img, 0, 0, S - 1, S - 1, W_MID)
        for lane, base in enumerate((2, 7, 12)):
            for xx in range(S):
                yy = base + int(1.6 * math.sin((xx + off * 2 + lane * 5) * 0.55))
                put(img, xx, yy, W_HI if lane % 2 == 0 else W_DEEP)
        for _ in range(6):
            x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
            put(img, x, y, lighter(W_MID, 16))
    elif kind == "lake":
        for xx in range(S):
            put(img, xx, 0, W_HI)
            if rnd.random() < .4:
                put(img, xx, 1, lighter(W_MID, 20))
        # bobbing glints
        for i in range(3):
            gx = (i * 6 + off) % S
            rect(img, gx, 5 + (frame % 2), gx + 2, 5 + (frame % 2), W_HI)
            px(img, gx + 1, 10 - (frame % 2), shade(W_HI, da=170))
    elif kind == "shallow":
        rect(img, 0, 6, S - 1, S - 1, lighter(W_MID, 26))
        rect(img, 0, 10, S - 1, S - 1, lighter(W_MID, 44))
        for xx in range(S):
            wy = 4 + int(math.sin((xx + off * 2) * 0.6) * 1.5)
            put(img, xx, wy, W_FOAM)
            put(img, xx, wy + 1, W_HI)
    elif kind == "fall":
        rect(img, 0, 0, S - 1, S - 1, W_HI)
        for xx in range(0, S, 2):
            for yy in range(((xx + off * 3) % 4), S, 4):
                put(img, xx, yy, W_FOAM)
                put(img, xx + 1, yy, lighter(W_MID, 30))
        rect(img, 0, 0, S - 1, 1, W_DEEP)
    return img


import math


def build_sheet(name, tiles, cols):
    rows = (len(tiles) + cols - 1) // cols
    sheet = Sheet(cols, S, S, rows=rows)
    sheet.rows = rows
    for t in tiles:
        sheet.add(t)
    canvas = sheet.save(os.path.join(OUT, name))
    canvas.resize((canvas.width * 4, canvas.height * 4), Image.NEAREST).save(
        os.path.join(PREV, name.replace(".png", "@4x.png")))
    return canvas


# grass mega: row0 4 surfaces | row1 dirtA dirtB blend-topA blend-topB | row2 corners | row3 sides+floater
grass = []
for i in range(4):
    grass.append(grass_surface(3 + i, blades=i))
grass += [dirt_fill(11), dirt_fill(12), dirt_fill(13, True), dirt_fill(14, True)]
grass += [grass_corner(21, True), grass_corner(22, False),
          flip_h(grass_corner(21, True)), flip_h(grass_corner(22, False))]
grass += [grass_edge_side(31, True), grass_edge_side(32, False),
          grass_surface(99, blades=3), dirt_fill(33)]
build_sheet("mega_grass.png", grass, 8)

snow = []
for i in range(4):
    snow.append(snow_surface(5 + i))
snow += [frost_fill(15), frost_fill(16), frost_fill(17, True), frost_fill(18, True)]
snow += [grass_corner(23, True), grass_corner(24, False),
         flip_h(grass_corner(23, True)), flip_h(grass_corner(24, False))]
# replace generic corners' green with snow palette quick tint: rebuild w/ snow colors
def snow_corner(seed, tl):
    img = frost_fill(seed)
    rnd = random.Random(seed + 7)
    for yy in range(5):
        xs = range(0, max(1, S - yy * 2)) if tl else range(min(S - 1, yy * 2), S)
        for xx in xs:
            put(img, xx, yy, SNOW_TOP[2] if yy < 2 else SNOW_TOP[0])
    bottom_shade(img, 0, 3, S - 1, S - 1, None, 20)
    return img
snow[8] = snow_corner(23, True); snow[9] = snow_corner(24, False)
snow[10] = flip_h(snow[8]); snow[11] = flip_h(snow[9])
def snow_side(seed, left):
    img = frost_fill(seed)
    for yy in range(S):
        if left:
            put(img, 0, yy, SNOW_TOP[1]); put(img, 1, yy, SNOW_TOP[0])
        else:
            put(img, S - 1, yy, SNOW_TOP[1]); put(img, S - 2, yy, SNOW_TOP[0])
    return img
snow += [snow_side(35, True), snow_side(36, False), snow_surface(51), frost_fill(37)]
build_sheet("mega_snow.png", snow, 8)

sand = []
for i in range(4):
    sand.append(sand_surface(7 + i))
sand += [wetsand_fill(19), wetsand_fill(20), wetsand_fill(21, True), wetsand_fill(22, True)]
def sand_corner(seed, tl):
    img = wetsand_fill(seed)
    for yy in range(5):
        xs = range(0, max(1, S - yy * 2)) if tl else range(min(S - 1, yy * 2), S)
        for xx in xs:
            put(img, xx, yy, SAND_T[2] if yy < 2 else SAND_T[0])
    bottom_shade(img, 0, 3, S - 1, S - 1, None, 20)
    return img
sand += [sand_corner(25, True), sand_corner(26, False),
         flip_h(sand_corner(25, True)), flip_h(sand_corner(26, False))]
def sand_side(seed, left):
    img = wetsand_fill(seed)
    for yy in range(S):
        c = SAND_T[0] if yy < 5 else SAND_M
        if left:
            put(img, 0, yy, c); put(img, 1, yy, SAND_T[1])
        else:
            put(img, S - 1, yy, c); put(img, S - 2, yy, SAND_T[1])
    return img
sand += [sand_side(37, True), sand_side(38, False), sand_surface(55), wetsand_fill(39)]
build_sheet("mega_sand.png", sand, 8)

# water: 4 kinds x 4 frames
water = []
for kind in ("river", "lake", "shallow", "fall"):
    for f in range(4):
        water.append(water_tile(kind, f))
build_sheet("water_river.png", water, 4)

deep = []
for f in range(4):
    img, rnd = T(70 + f)
    rect(img, 0, 0, S - 1, S - 1, W_DEEP)
    for yy in range(S):
        put(img, 0, yy, darker(W_DEEP, 12)); put(img, S - 1, yy, darker(W_DEEP, 12))
    for i in range(3):
        gy = (i * 5 + f) % S
        for xx in range(2 + ((f + i) % 3), min(S - 2, 8 + ((f + i) % 4))):
            put(img, xx, gy, W_MID if (xx + gy) % 3 else lighter(W_MID, 12))
    deep.append(img)
build_sheet("water_deep.png", deep, 2)

# cliffs: rock with grass lip
def cliff(seed, part):
    img, rnd = T(seed)
    ROCK = (122, 116, 128, 255); ROCK_D = (86, 80, 96, 255); ROCK_L = (158, 152, 166, 255)
    rect(img, 0, 0, S - 1, S - 1, ROCK)
    for _ in range(20):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
        put(img, x, y, rnd.choice([ROCK_D, ROCK_L]))
    # crack lines
    cx = rnd.randint(3, 12)
    line(img, [(cx, 2), (cx - 1, 7), (cx + 1, 13)], ROCK_D, 1)
    if part == "top":
        for xx in range(S):
            put(img, xx, 0, GRASS_TOP[2]); put(img, xx, 1, GRASS_TOP[0]); put(img, xx, 2, GRASS_MID)
        for xx in range(0, S, 3):
            put(img, xx, 3, darker(GRASS_MID, 20))
    elif part == "sideL":
        for yy in range(S):
            put(img, 0, yy, ROCK_L); put(img, 1, yy, lighter(ROCK, 12))
    elif part == "sideR":
        for yy in range(S):
            put(img, S - 1, yy, ROCK_D); put(img, S - 2, yy, darker(ROCK, 12))
    bottom_shade(img, 0, 0, S - 1, S - 1, None, 26)
    return img

cliff_t = []
for v in range(2):
    cliff_t += [cliff(80 + v, "top"), cliff(90 + v, "sideL"), cliff(100 + v, "sideR")]
build_sheet("cliff_grass.png", cliff_t, 3)
print("mega ground ok")
