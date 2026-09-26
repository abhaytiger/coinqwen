"""Stage dressing v3 — more elements per world, premium shading (pxlib2).
Meadow: windmill(4f), flower_bed, berry_bush, signpost_mile, bench, scarecrow,
        river_reed, pebble_pile, lamp_post, tiny_pond_ring
Snow:   snow_fort, igloo_big, cabin_v2, ice_castle_turret, lantern_snow,
        frozen_pond_ring, spruce_v2, mittens_sign, chimney_smoke(3f)
Beach:  pier_lamp, boat, sand_bucket_set, palm_v2, rock_arch, tidepool,
        boardwalk_plank, jellyfish_balloon, bonfire, beachflag
Water edges for ponds/riverbanks included as tiles.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *

ROOT = "/workspace/pixel_art"
P_M = f"{ROOT}/worlds/classic_meadow"; P_S = f"{ROOT}/worlds/snow_town"; P_B = f"{ROOT}/worlds/beach"
for p in (P_M, P_S, P_B):
    os.makedirs(f"{p}/previews", exist_ok=True)


def save2(img, path):
    small = img.resize((img.width // SCALE, img.height // SCALE), Image.NEAREST)
    small.save(path)
    small.resize((small.width * 3, small.height * 3), Image.NEAREST).save(
        path.replace(".png", "@3x.png").replace(os.path.dirname(path),
                                                os.path.join(os.path.dirname(path), "previews")))
    return small


WOOD = (146, 98, 58, 255); WOOD_D = (104, 66, 38, 255); WOOD_L = (180, 130, 82, 255)
ROOF = (196, 76, 62, 255); ROOF_D = (148, 50, 46, 255)
STONE = (140, 136, 150, 255); STONE_D = (98, 94, 112, 255); STONE_L = (176, 172, 186, 255)
LEAF = (88, 168, 76, 255); LEAF_D = (54, 128, 60, 255); LEAF_L = (140, 208, 110, 255)
SNOWC = (246, 250, 255, 255); SNOWD = (206, 222, 240, 255); ICE = (168, 216, 248, 255)
SANDC = (246, 224, 158, 255); SANDD = (214, 186, 120, 255)
SEA = (66, 148, 214, 255); SEA_D = (40, 108, 176, 255)


def plank(x0, y0, x1, y1, img, base=WOOD):
    rect(img, x0, y0, x1, y1, base)
    top_light(img, x0, y0, x1, y1, None, 22)
    bottom_shade(img, x0, y0, x1, y1, None, 34)
    for gx in range(x0 + 2, x1, 4):
        line(img, [(gx, y0 + 1), (gx - 1, y1 - 1)], darker(base, 22), 1)


# ================================================================ MEADOW
def windmill(f):
    img = new(40, 56)
    # tower
    for i, yy in enumerate(range(18, 54)):
        wdt = 6 + int((yy - 18) * 0.28)
        rect(img, 20 - wdt, yy, 20 + wdt, yy, STONE if yy % 6 else STONE_D)
    top_light(img, 12, 20, 28, 52, None, 18)
    rrect(img, 14, 14, 26, 19, ROOF, radius=2)
    bottom_shade(img, 14, 14, 26, 19, None, 30)
    rect(img, 17, 44, 23, 53, WOOD_D)                      # door
    arch = [(17, 44), (18, 42), (22, 42), (23, 44)]
    for a in arch: put(img, a[0], a[1], WOOD)
    px(img, 22, 48, (250, 220, 110, 255))                  # handle glint
    # blades cross rotating by frame
    cx, cy = 20, 12
    for k in range(4):
        a = math.tau * k / 4 + f * math.tau / 16
        ex, ey = cx + 11 * math.cos(a), cy + 11 * math.sin(a)
        line(img, [(cx, cy), (ex, ey)], WOOD_L, 2)
        mx, my = cx + 7 * math.cos(a + 0.18), cy + 7 * math.sin(a + 0.18)
        line(img, [(mx, my), (ex, ey)], (238, 232, 214, 255), 3)
    ellipse(img, cx - 2, cy - 2, cx + 2, cy + 2, WOOD_D)
    px(img, cx - 1, cy - 1, WOOD_L)
    return finalize(img, (36, 26, 44, 255))


def flower_bed():
    img = new(32, 16)
    rect(img, 0, 8, 31, 15, WOOD_D)                        # planter box
    rect(img, 1, 9, 30, 14, WOOD); top_light(img, 1, 9, 30, 14, None, 18)
    rect(img, 0, 8, 31, 9, WOOD_L)
    rnd = random.Random(3)
    cols = [(240, 96, 110, 255), (250, 200, 80, 255), (170, 120, 230, 255), (255, 150, 190, 255)]
    for i in range(8):
        fx = 2 + i * 4 + rnd.randint(-1, 1); fy = rnd.randint(1, 5)
        line(img, [(fx, fy + 2), (fx, 8)], LEAF_D, 1)
        ellipse(img, fx - 1, fy - 1, fx + 2, fy + 2, cols[i % 4])
        px(img, fx, fy, (255, 240, 160, 255))
    return finalize(img, (36, 26, 44, 255))


def bench():
    img = new(32, 20)
    rect(img, 3, 8, 28, 10, WOOD); top_light(img, 3, 8, 28, 10, None, 26)
    rect(img, 3, 12, 28, 14, WOOD); rect(img, 3, 4, 28, 6, WOOD_L)
    for sx in (5, 26):
        rect(img, sx, 15, sx + 2, 19, WOOD_D)
        rect(img, sx, 0, sx + 2, 4, WOOD_D)
    rect(img, 3, 10, 28, 10, darker(WOOD, 30))
    return finalize(img, (36, 26, 44, 255))


def scarecrow():
    img = new(24, 40)
    line(img, [(12, 6), (12, 39)], WOOD_D, 2)
    line(img, [(4, 14), (20, 14)], WOOD_D, 2)
    rrect(img, 6, 10, 18, 24, (212, 168, 84, 255), radius=2)     # shirt
    bottom_shade(img, 6, 10, 18, 24, None, 34)
    ellipse(img, 8, 2, 16, 10, (244, 208, 160, 255))             # sack head
    px(img, 10, 6, INK); px(img, 14, 6, INK)
    line(img, [(10, 9), (14, 9)], INK, 1)
    rrect(img, 6, 0, 18, 3, (150, 108, 60, 255), radius=1)       # hat
    rect(img, 3, 3, 21, 4, (150, 108, 60, 255))
    noise(img, 6, 26, 18, 30, [(212, 168, 84, 255), (180, 140, 70, 255)], .5, seed=8)  # straw
    return finalize(img, (36, 26, 44, 255))


def reeds():
    img = new(16, 20)
    for rx, h, bend in ((3, 16, 2), (7, 19, -1), (11, 14, 2), (13, 18, 1)):
        line(img, [(rx, 19), (rx, 19 - h + 3), (rx + bend, 19 - h)], (96, 158, 84, 255), 1)
    px(img, 7, 1, (150, 110, 60, 255)); px(img, 7, 2, (150, 110, 60, 255))  # cattail
    return finalize(img, (36, 26, 44, 255))


def lamp_post():
    img = new(16, 32)
    rect(img, 6, 8, 9, 30, (56, 52, 68, 255))
    top_light(img, 6, 8, 9, 30, None, 20)
    rrect(img, 4, 29, 11, 31, (40, 36, 52, 255), radius=1)
    ellipse(img, 4, 2, 11, 9, (255, 226, 130, 255))              # glow glass
    rect(img, 3, 1, 12, 2, (56, 52, 68, 255)); rect(img, 5, 0, 10, 1, (56, 52, 68, 255))
    px(img, 7, 4, (255, 255, 220, 255)); px(img, 8, 5, (255, 255, 220, 255))
    return finalize(img, (36, 26, 44, 255))


def signpost():
    img = new(24, 28)
    rect(img, 10, 8, 13, 27, WOOD_D)
    rrect(img, 2, 2, 22, 9, WOOD, radius=1)
    top_light(img, 2, 2, 22, 9, None, 24)
    rect(img, 5, 4, 15, 4, (90, 60, 34, 255)); rect(img, 5, 6, 12, 6, (90, 60, 34, 255))
    ellipse(img, 17, 3, 21, 7, (250, 208, 74, 255))              # coin decal
    px(img, 18, 4, (255, 240, 160, 255))
    return finalize(img, (36, 26, 44, 255))


def meadow_tiles():
    # pond water edge ring tiles (4 variants of shoreline)
    out = []
    for v in range(4):
        img = new(16, 16)
        rnd = random.Random(20 + v)
        rect(img, 0, 0, 15, 15, (104, 178, 82, 255))
        for _ in range(10):
            put(img, rnd.randint(0, 15), rnd.randint(0, 15), (86, 152, 70, 255))
        ellipse(img, 2 + v, 3, 14 - v, 15, SEA)
        ellipse(img, 4 + v, 5, 12 - v, 14, SEA_D)
        for xx in range(4, 12):
            put(img, xx, 4 + (xx + v) % 2, (120, 190, 240, 255))
        out.append(finalize(img, None) if False else img)
    return out


# =================================================================== SNOW
def igloo_big():
    img = new(48, 32)
    ellipse(img, 4, 4, 44, 40, SNOWC)
    rect(img, 4, 20, 44, 36, SNOWC)
    # block seams
    for row, yy in enumerate((12, 20, 28)):
        for xx in range(6 + (row % 2) * 4, 42, 8):
            rect(img, xx, yy, xx + 1, yy, SNOWD)
    arc = darker(SNOWC, 26)
    d = ImageDraw.Draw(img)
    d.arc([10 * SCALE, 10 * SCALE, 38 * SCALE, 40 * SCALE], 180, 360, fill=(200, 214, 232, 255), width=SCALE)
    # entrance tunnel
    ellipse(img, 18, 18, 30, 36, (52, 66, 96, 255))
    ellipse(img, 20, 21, 28, 36, (28, 38, 62, 255))
    for xx in range(17, 31, 3):
        put(img, xx, 17 + abs(xx - 24) // 3, SNOWD)
    # warm light inside
    px(img, 24, 30, (255, 200, 110, 200)); px(img, 23, 31, (255, 200, 110, 140))
    top_light(img, 8, 4, 40, 12, None, 8)
    return finalize(img, (44, 40, 66, 255))


def ice_turret():
    img = new(24, 40)
    rect(img, 4, 12, 19, 39, ICE)
    for yy in range(14, 38, 5):
        rect(img, 4, yy, 19, yy, lighter(ICE, 26))
    bottom_shade(img, 4, 12, 19, 39, None, 30)
    top_light(img, 4, 12, 19, 39, None, 20)
    # crenellations
    for cx in (4, 10, 16):
        rrect(img, cx, 8, cx + 4, 13, ICE, radius=1)
    # spire
    tri = [(11, 0), (8, 8), (15, 8)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in tri], fill=(214, 238, 255, 255))
    px(img, 11, 2, (255, 255, 255, 255))
    rect(img, 9, 24, 14, 31, (86, 140, 190, 255))               # window
    px(img, 10, 25, (200, 235, 255, 255))
    return finalize(img, (44, 40, 66, 255))


def spruce_v2():
    img = new(32, 48)
    rect(img, 14, 38, 17, 47, (92, 62, 44, 255))
    line(img, [(15, 40), (15, 46)], (66, 44, 30, 255), 1)
    greens = [(30, 96, 66, 255), (40, 116, 78, 255), (52, 136, 90, 255)]
    tiers = [(16, 2, 24), (11, 10, 30), (7, 20, 36)]
    for i, (half, y0, y1) in enumerate(tiers):
        pts = [(16, y0 - 2), (16 - half, y1), (16 + half, y1)]
        d = ImageDraw.Draw(img)
        d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=greens[i % 3])
        # snow caps on branch tips
        for sx in range(16 - half + 3, 16 + half - 2, 5):
            put(img, sx, y1 - 3, SNOWC); put(img, sx + 1, y1 - 3, SNOWC)
            put(img, sx, y1 - 4, shade(SNOWC, da=150))
        rect(img, 16 - half, y1 - 1, 16 + half, y1, darker(greens[i % 3], 30))
    return finalize(img, (30, 40, 44, 255))


def snow_fort():
    img = new(48, 28)
    rect(img, 2, 8, 45, 27, SNOWD)
    rect(img, 2, 8, 45, 12, SNOWC)
    for bx in range(4, 44, 7):
        rect(img, bx, 14, bx + 5, 18, SNOWC)
        rect(img, bx + 3, 20, bx + 8, 24, SNOWC)
        rect(img, bx, 14, bx + 5, 14, lighter(SNOWC, 4))
    for cx in (2, 40):
        rect(img, cx, 4, cx + 6, 10, SNOWC)                     # corner towers
        rect(img, cx + 1, 2, cx + 5, 4, SNOWD)
    # flag
    line(img, [(24, 0), (24, 8)], WOOD_D, 1)
    pts = [(24, 0), (31, 2), (24, 5)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=(226, 84, 84, 255))
    bottom_shade(img, 2, 8, 45, 27, None, 26)
    return finalize(img, (44, 40, 66, 255))


def cabin_v2():
    img = new(56, 44)
    # log walls
    rect(img, 6, 18, 49, 42, (128, 88, 56, 255))
    for ly in range(20, 42, 4):
        rect(img, 6, ly, 49, ly, (98, 64, 40, 255))
        rect(img, 6, ly + 1, 49, ly + 1, (150, 106, 66, 255))
    for lx in (6, 49):
        rect(img, lx - 1, 18, lx + 1, 42, (110, 74, 46, 255))
    # roof with heavy snow
    pts = [(28, 2), (2, 20), (54, 20)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=(120, 56, 48, 255))
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(28, 2), (6, 18), (50, 18)]], fill=(140, 66, 54, 255))
    rect(img, 2, 17, 54, 20, SNOWC)
    for sx in range(4, 52, 6):
        put(img, sx, 20 + (sx % 3 == 0), SNOWC); put(img, sx + 1, 20, SNOWD)
    # door + wreath + glowing window
    rect(img, 12, 26, 21, 42, (86, 56, 34, 255))
    rect(img, 13, 27, 20, 41, (104, 70, 44, 255))
    ellipse(img, 14, 30, 19, 35, (40, 110, 66, 255))
    ellipse(img, 15, 31, 18, 34, (104, 70, 44, 255))
    for k in range(3):
        px(img, 15 + k * 2, 30, (226, 84, 84, 255))
    rect(img, 32, 26, 43, 34, (250, 208, 110, 255))
    rect(img, 32, 26, 43, 26, (98, 64, 40, 255)); rect(img, 37, 26, 38, 34, (98, 64, 40, 255))
    rect(img, 32, 26, 43, 34, None)
    d.rectangle([32 * SCALE, 26 * SCALE, 43 * SCALE, 34 * SCALE], outline=(98, 64, 40, 255), width=SCALE)
    px(img, 34, 28, (255, 240, 180, 255))
    # chimney + smoke handled separately; snow drift at base
    ellipse(img, 0, 38, 56, 46, SNOWC)
    rect(img, 0, 41, 56, 46, SNOWC)
    noise(img, 2, 40, 54, 44, [SNOWD], .25, seed=4)
    return finalize(img, (44, 40, 66, 255))


def smoke(f):
    img = new(16, 16)
    for i in range(3):
        r = 2 + ((f + i) % 3)
        cx = 8 + int(math.sin((f + i) * 1.3) * 2)
        cy = 12 - i * 4 - (f % 2)
        alpha = 150 - i * 40
        ellipse(img, cx - r, cy - r, cx + r, cy + r, (226, 232, 240, max(40, alpha)))
    return img


def mittens_sign():
    img = new(20, 28)
    rect(img, 9, 6, 11, 27, WOOD_D)
    rrect(img, 3, 0, 8, 7, (226, 84, 84, 255), radius=2)
    rrect(img, 12, 1, 17, 8, (96, 150, 226, 255), radius=2)
    rect(img, 4, 7, 7, 9, (226, 84, 84, 255)); rect(img, 13, 8, 16, 10, (96, 150, 226, 255))
    px(img, 5, 2, (255, 255, 255, 200)); px(img, 14, 3, (255, 255, 255, 200))
    return finalize(img, (44, 40, 66, 255))


# ================================================================== BEACH
def palm_v2():
    img = new(48, 64)
    # curved trunk with segment rings
    pts = [(22, 62), (22, 52), (25, 42), (28, 32), (30, 22)]
    line(img, pts, (150, 104, 62, 255), 5)
    line(img, pts, (120, 80, 46, 255), 1)
    for i in range(1, len(pts) - 1):
        px(img, pts[i][0] - 2, pts[i][1], (176, 128, 80, 255))
    # coconuts
    ellipse(img, 26, 20, 31, 25, (110, 74, 44, 255)); px(img, 27, 21, (150, 110, 70, 255))
    ellipse(img, 30, 22, 35, 27, (96, 62, 36, 255))
    # fronds radiating
    tips = [(-16, -14), (-6, -20), (8, -18), (18, -10), (20, 2), (-18, 0)]
    for tx, ty in tips:
        ex, ey = 30 + tx, 18 + ty
        mx, my = 30 + tx * 0.5, 16 + ty * 0.5 - 4
        line(img, [(30, 18), (mx, my), (ex, ey)], (52, 148, 74, 255), 2)
        # leaflets
        for t in range(3):
            lx = 30 + tx * (0.3 + t * 0.25); ly = 16 + ty * (0.3 + t * 0.25) - 3 * (1 - t * 0.2)
            px(img, int(lx) - 1, int(ly) + 1, (36, 120, 60, 255))
            px(img, int(lx) + 1, int(ly) + 2, (86, 178, 96, 255))
    return finalize(img, (30, 40, 44, 255))


def boat():
    img = new(48, 32)
    # hull crescent
    pts = [(6, 14), (42, 14), (36, 26), (12, 26)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=(178, 116, 64, 255))
    rect(img, 6, 13, 42, 15, (210, 148, 90, 255))
    for hx in range(8, 41, 6):
        put(img, hx, 20, (140, 88, 48, 255))
    d.line([6 * SCALE, 14 * SCALE, 42 * SCALE, 14 * SCALE], fill=(120, 74, 40, 255), width=SCALE)
    # mast + sail
    rect(img, 23, 0, 25, 14, WOOD_D)
    pts2 = [(25, 1), (38, 12), (25, 12)]
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts2], fill=(250, 244, 226, 255))
    px(img, 30, 6, (240, 120, 90, 255)); px(img, 31, 7, (240, 120, 90, 255))  # stripe dot
    rect(img, 25, 8, 33, 8, (240, 120, 90, 180))
    # little flag
    pts3 = [(23, 0), (16, 2), (23, 4)]
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts3], fill=(96, 178, 226, 255))
    return finalize(img, (30, 40, 44, 255))


def tidepool():
    img = new(32, 16)
    rnd = random.Random(9)
    ellipse(img, 2, 2, 30, 15, SEA_D)
    ellipse(img, 4, 3, 28, 14, SEA)
    for _ in range(6):
        x, y = rnd.randint(6, 26), rnd.randint(5, 12)
        px(img, x, y, (120, 190, 240, 255))
    # rim stones + starfish + anemone
    for sx, sy in ((3, 3), (8, 1), (16, 1), (24, 2), (29, 6), (2, 8)):
        ellipse(img, sx, sy, sx + 2, sy + 2, STONE); px(img, sx, sy, STONE_L)
    ellipse(img, 12, 8, 18, 12, (250, 140, 90, 255))
    px(img, 15, 9, (255, 200, 140, 255))
    for k in range(5):
        a = k * math.tau / 5
        px(img, int(15 + 4 * math.cos(a)), int(10 + 3 * math.sin(a)), (250, 140, 90, 255))
    return finalize(img, (30, 40, 44, 255))


def bonfire():
    img = new(24, 24)
    for k in range(4):
        a = math.tau * k / 4 + 0.4
        x1, y1 = 12 + 8 * math.cos(a), 18 + 4 * math.sin(a)
        x2, y2 = 12 - 8 * math.cos(a), 18 - 4 * math.sin(a)
        line(img, [(x1, y1), (x2, y2)], (120, 78, 44, 255), 2)
    flame = [(12, 2), (8, 10), (10, 14), (14, 14), (16, 10)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in flame], fill=(255, 150, 50, 255))
    inner = [(12, 6), (10, 12), (14, 12)]
    d.polygon([(x * SCALE, y * SCALE) for x, y in inner], fill=(255, 220, 110, 255))
    px(img, 12, 9, (255, 250, 210, 255))
    ellipse(img, 2, 18, 22, 23, (90, 84, 92, 255))          # stone ring
    for sx in range(3, 22, 4):
        put(img, sx, 19, STONE_L); put(img, sx + 1, 21, STONE_D)
    return finalize(img, (30, 40, 44, 255))


def beachflag():
    img = new(20, 32)
    rect(img, 3, 0, 4, 31, (238, 232, 214, 255))
    pts = [(4, 1), (18, 4), (4, 10)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in pts], fill=(240, 120, 90, 255))
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(4, 4), (11, 5), (4, 7)]], fill=(255, 230, 150, 255))
    ellipse(img, 0, 28, 8, 32, SANDD)                        # sand mound anchor
    return finalize(img, (30, 40, 44, 255))


def pier_lamp():
    img = new(16, 28)
    rect(img, 6, 6, 9, 27, (120, 90, 60, 255))
    top_light(img, 6, 6, 9, 27, None, 22)
    rrect(img, 3, 0, 12, 7, (255, 226, 130, 255), radius=2)
    rect(img, 2, 0, 13, 1, (86, 66, 48, 255))
    px(img, 6, 3, (255, 255, 220, 255))
    return finalize(img, (30, 40, 44, 255))


def bucket_set():
    img = new(24, 16)
    # bucket
    rrect(img, 2, 4, 12, 14, (96, 178, 226, 255), radius=1)
    rect(img, 2, 4, 12, 5, (140, 208, 246, 255))
    d = ImageDraw.Draw(img)
    d.arc([3 * SCALE, 0, 11 * SCALE, 8 * SCALE], 180, 360, fill=(60, 120, 170, 255), width=SCALE)
    # sand pile + spade
    ellipse(img, 12, 8, 23, 16, SANDC)
    px(img, 16, 7, SANDC); px(img, 18, 6, SANDC)
    line(img, [(20, 2), (17, 9)], WOOD_D, 1)
    rrect(img, 15, 9, 19, 12, (200, 200, 210, 255), radius=1)
    return finalize(img, (30, 40, 44, 255))


def rock_arch():
    img = new(48, 40)
    d = ImageDraw.Draw(img)
    d.arc([6 * SCALE, 6 * SCALE, 42 * SCALE, 42 * SCALE], 180, 360, fill=STONE, width=5 * SCALE)
    rect(img, 6, 22, 14, 39, STONE); rect(img, 34, 22, 42, 39, STONE)
    noise(img, 6, 8, 42, 38, [STONE_D, STONE_L], .22, seed=13)
    for xx in range(8, 40, 3):
        put(img, xx, 6 + int(4 - abs(xx - 24) * 0.28), STONE_L)
    # under-arch shadow + sea glimpse
    rect(img, 16, 26, 32, 39, (30, 90, 150, 160))
    for xx in range(18, 30, 4):
        put(img, xx, 32 + (xx % 3), (120, 190, 240, 200))
    return finalize(img, (30, 40, 44, 255))


# ------------------------------------------------------------------ export
MEAD = {"windmill": [windmill(f) for f in range(4)], "flower_bed": [flower_bed()],
        "bench": [bench()], "scarecrow": [scarecrow()], "river_reed": [reeds()],
        "lamp_post": [lamp_post()], "signpost_mile": [signpost()]}
for name, frames in MEAD.items():
    sh = Sheet(len(frames), frames[0].width // SCALE, frames[0].height // SCALE)
    for f in frames:
        sh.add(f)
    canvas = sh.save(f"{P_M}/{name}.png")
    canvas.resize((canvas.width * 3, canvas.height * 3), Image.NEAREST).save(f"{P_M}/previews/{name}@3x.png")
pond = Sheet(4, 16, 16)
for t in meadow_tiles():
    pond.add(t)
c = pond.save(f"{P_M}/pond_tiles.png")
c.resize((c.width * 4, c.height * 4), Image.NEAREST).save(f"{P_M}/previews/pond_tiles@4x.png")

SNW = {"igloo_big": igloo_big(), "ice_turret": ice_turret(), "spruce_v2": spruce_v2(),
       "snow_fort": snow_fort(), "cabin_v2": cabin_v2(), "mittens_sign": mittens_sign()}
for name, im in SNW.items():
    save2(im, f"{P_S}/{name}.png")
sm = Sheet(3, 16, 16)
for f in range(3):
    sm.add(smoke(f))
c = sm.save(f"{P_S}/chimney_smoke.png")
c.resize((c.width * 4, c.height * 4), Image.NEAREST).save(f"{P_S}/previews/chimney_smoke@4x.png")

BCH = {"palm_v2": palm_v2(), "boat": boat(), "tidepool": tidepool(), "bonfire": bonfire(),
       "beachflag": beachflag(), "pier_lamp": pier_lamp(), "bucket_set": bucket_set(),
       "rock_arch": rock_arch()}
for name, im in BCH.items():
    save2(im, f"{P_B}/{name}.png")
print("stage v3 ok")
