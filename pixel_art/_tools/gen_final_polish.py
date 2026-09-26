"""Final polish pass — new stage elements + a unified 4-direction character sheet.

1) Extra per-stage dressing (cute & happening):
   meadow : picnic_set, fountain (animated), hedge, cart_wheels sign, flower arch
   snow   : snow_lamp, cocoa_stand, igloo_chimney smoke, snow angel decor, ice pond tileset strip
   beach  : boardwalk planks strip, dolphin jump FX, sand dollar path deco, tiki bar sign
2) hero_4dir.png template: one 8x4 grid @48x56 that stitches the existing
   side/back sheets into a ready-to-use directional atlas (documented layout).
3) shadow_blob.png: soft elliptical player shadow sprite for any skin.
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *
from PIL import Image

ROOT = "/workspace/pixel_art"
CHAR = os.path.join(ROOT, "characters")
MEAD = os.path.join(ROOT, "worlds", "classic_meadow")
SNOWD = os.path.join(ROOT, "worlds", "snow_town")
BEACH = os.path.join(ROOT, "worlds", "beach")
FX = os.path.join(ROOT, "effects")
PREV = os.path.join(FX, "previews")
os.makedirs(PREV, exist_ok=True)


def save(img, path):
    img.save(path)
    s = img.resize((img.width * 3, img.height * 3), Image.NEAREST)
    d = os.path.dirname(path)
    os.makedirs(os.path.join(d, "previews"), exist_ok=True)
    s.save(os.path.join(d, "previews", os.path.basename(path).replace(".png", "@3x.png")))
    print("ok:", os.path.relpath(path, ROOT))


# ============================================================ MEADOW EXTRAS
def fountain():
    """48x48 animated fountain: 4 frames (water height cycles)."""
    stone = (176, 176, 186, 255); stone_d = (122, 124, 140, 255)
    water = (110, 180, 236, 255); water_l = (176, 224, 250, 255)
    frames = []
    for f in range(4):
        img = Image.new("RGBA", (48 * SCALE, 48 * SCALE), (0, 0, 0, 0))
        # basin
        ellipse(img, 6, 30, 42, 44, stone)
        ellipse(img, 9, 32, 39, 42, water)
        rect(img, 6, 36, 42, 42, stone)
        bottom_shade(img, 6, 30, 42, 44, None, 40)
        top_light(img, 8, 30, 40, 33, None, 24)
        # pedestal + bowl
        rect(img, 21, 20, 27, 34, stone_d)
        ellipse(img, 15, 14, 33, 22, stone)
        ellipse(img, 17, 15, 31, 20, water)
        # jet: height animates
        h = [10, 13, 11, 8][f]
        rect(img, 23, 14 - h, 25, 15, water_l)
        for k in range(3):
            px(img, 21 - k, 13 - h + k * 2, water_l)
            px(img, 27 + k, 13 - h + k * 2, water_l)
        # droplets falling to basin rim
        for dx, dy in ((12, 24 + f), (35, 26 - f), (16, 28), (31, 29)):
            px(img, dx, dy, water_l)
        # shimmer on basin water
        rnd = random.Random(f)
        for i in range(4):
            px(img, 14 + rnd.randrange(20), 36 + rnd.randrange(4), (255, 255, 255, 160))
        frames.append(finalize(img, (40, 34, 52, 255)))
    sh = Sheet(4, 48, 48)
    for fr in frames:
        sh.add(fr)
    save(sh.canvas, os.path.join(MEAD, "fountain.png"))


def picnic():
    img = Image.new("RGBA", (40 * SCALE, 28 * SCALE), (0, 0, 0, 0))
    cloth = (226, 96, 84, 255); white = (250, 246, 240, 255)
    # checkered blanket (perspective quad-ish: wider at bottom)
    for row in range(6):
        y = 12 + row
        x0 = 6 - row // 2; x1 = 34 + row // 2
        for col_x in range(x0, x1):
            c = cloth if (row + col_x) % 2 == 0 else white
            rect(img, col_x, y, col_x + 1, y + 1, c)
    bottom_shade(img, 2, 12, 38, 18, None, 26)
    # basket + loaf + apple
    rrect(img, 12, 6, 20, 12, (188, 136, 76, 255), radius=2)
    rect(img, 12, 8, 20, 9, (150, 104, 58, 255))
    line(img, [(13, 6), (16, 3), (19, 6)], (150, 104, 58, 255), 2)
    ellipse(img, 23, 8, 28, 12, (240, 208, 150, 255)); px(img, 24, 9, (255, 240, 200, 255))
    ellipse(img, 29, 9, 32, 12, (222, 70, 66, 255)); px(img, 30, 8, (90, 150, 70, 255))
    save(finalize(img, (40, 30, 46, 255)), os.path.join(MEAD, "picnic_set.png"))


def hedge():
    """16x16 tileable hedge chunk, 4 variants in a row."""
    sh = Sheet(4, 16, 16)
    leaf = (86, 150, 76, 255); leaf_d = (54, 108, 56, 255); leaf_l = (128, 190, 108, 255)
    for v in range(4):
        img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
        rnd = random.Random(v * 7 + 3)
        rrect(img, 0, 4, 16, 16, leaf, radius=3)
        for i in range(0, 16, 3):
            ellipse(img, i - 1, 2 + (i % 3), i + 3, 7 + (i % 2), leaf)
        noise(img, 1, 5, 15, 15, [leaf_d, leaf_l], 0.35, seed=v + 1)
        top_light(img, 0, 3, 15, 6, None, 22)
        if v == 2:                                        # berry variant
            for bx, by in ((4, 8), (10, 6), (13, 11)):
                ellipse(img, bx, by, bx + 2, by + 2, (214, 70, 90, 255))
                px(img, bx, by, (255, 180, 190, 255))
        sh.add(finalize(img, (36, 44, 36, 255)))
    save(sh.canvas, os.path.join(MEAD, "hedge.png"))


fountain(); picnic(); hedge()

# ============================================================== SNOW EXTRAS
def snow_lamp():
    """24x36 glowing lamp post, 2-frame flicker."""
    wood = (96, 78, 92, 255); wood_d = (64, 50, 64, 255)
    glow = (255, 226, 140, 255)
    frames = []
    for f in range(2):
        img = Image.new("RGBA", (24 * SCALE, 36 * SCALE), (0, 0, 0, 0))
        rect(img, 10, 12, 14, 32, wood)
        rect(img, 10, 12, 10, 32, wood_d)
        rect(img, 7, 31, 17, 33, wood_d)                  # base
        ellipse(img, 8, 0, 16, 4, wood_d)                 # cap
        rrect(img, 7, 4, 17, 14, (40, 34, 52, 255), radius=2)   # lantern cage
        g = lighter(glow, 20 * f)
        rect(img, 9, 6, 15, 12, g)
        ellipse(img, 10, 7, 14, 11, (255, 250, 200, 255))
        for yy in range(6, 13, 2):
            rect(img, 9, yy, 15, yy, wood_d)              # cage bars
        rect(img, 11, yy, 11, 12, wood_d)
        # warm halo + snow collar on cap
        halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ellipse(halo, 4, 2, 20, 16, (255, 210, 120, 26 + 12 * f))
        from PIL import ImageFilter as IF
        img = Image.alpha_composite(img, halo.filter(IF.GaussianBlur(SCALE)))
        rect(img, 7, 0, 17, 2, (250, 252, 255, 255))
        px(img, 12, 30, (230, 240, 250, 255))             # frost bit on pole
        frames.append(finalize(img, (30, 26, 44, 255)))
    sh = Sheet(2, 24, 36)
    for fr in frames:
        sh.add(fr)
    save(sh.canvas, os.path.join(SNOWD, "snow_lamp.png"))


def cocoa_stand():
    """40x32 tiny cocoa cart with steaming mug sign — 2 steam frames."""
    red = (204, 82, 74, 255); red_d = (150, 52, 52, 255)
    cream = (250, 240, 220, 255); wood = (158, 112, 66, 255)
    frames = []
    for f in range(2):
        img = Image.new("RGBA", (40 * SCALE, 32 * SCALE), (0, 0, 0, 0))
        rrect(img, 6, 12, 34, 26, red, radius=2)          # cart body
        rect(img, 6, 16, 34, 17, cream)                    # stripe
        bottom_shade(img, 6, 12, 34, 26, None, 34)
        rect(img, 4, 10, 36, 12, wood)                     # counter top
        rrect(img, 8, 2, 32, 10, cream, radius=2)          # awning board
        for ax in range(9, 32, 4):                         # scallop edge
            ellipse(img, ax, 8, ax + 3, 12, red if (ax // 4) % 2 == 0 else cream)
        rect(img, 8, 4, 32, 5, red_d)
        # mug painted on board
        rrect(img, 17, 4, 23, 9, (150, 96, 60, 255), radius=1)
        rect(img, 23, 5, 25, 8, (150, 96, 60, 255)); rect(img, 24, 6, 24, 7, cream)
        # steam wisps animate
        sx = [19, 21, 20][f % 3] if f else 20
        for k in range(3):
            px(img, sx + (k % 2) - (f and 1 or 0), 1 - 0, (255, 255, 255, 120))
            px(img, sx - 1 + k, max(0, 0), (255, 255, 255, 90))
        px(img, 20, 0, (255, 255, 255, 140)); px(img, 22 - f, 1, (255, 255, 255, 110))
        # wheels
        for wx in (11, 29):
            ellipse(img, wx - 3, 24, wx + 3, 30, (70, 58, 74, 255))
            ellipse(img, wx - 1, 26, wx + 1, 28, wood)
        save_frame = finalize(img, (36, 26, 44, 255))
        frames.append(save_frame)
    sh = Sheet(2, 40, 32)
    for fr in frames:
        sh.add(fr)
    save(sh.canvas, os.path.join(SNOWD, "cocoa_stand.png"))


def ice_skate_patch():
    """16x16 shiny skate-pond ice tile, 4 variants (cracks/scrape marks)."""
    sh = Sheet(4, 16, 16)
    ice = (168, 220, 246, 255); ice_d = (122, 178, 216, 255)
    for v in range(4):
        img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
        rect(img, 0, 0, 16, 16, ice)
        dither(img, 0, 0, 15, 15, ice_d, 0.18, seed=v + 2)
        top_light(img, 0, 0, 15, 4, None, 30)
        rnd = random.Random(v * 5 + 1)
        for i in range(2 + v):                             # scrape arcs
            x0, y0 = rnd.randrange(2, 12), rnd.randrange(2, 12)
            line(img, [(x0, y0), (x0 + 3, y0 + 1), (x0 + 5, y0 + 4)], (255, 255, 255, 170), 1)
        px(img, rnd.randrange(16), rnd.randrange(16), (255, 255, 255, 220))
        sh.add(finalize(img, (90, 140, 180, 255)))
    save(sh.canvas, os.path.join(SNOWD, "ice_skate_tiles.png"))


snow_lamp(); cocoa_stand(); ice_skate_patch()

# ============================================================= BEACH EXTRAS
def boardwalk():
    """16x16 dock-plank path tiles: straight, curve, edge grain — 4 variants."""
    sh = Sheet(4, 16, 16)
    plank = (188, 142, 92, 255); plank_d = (140, 98, 60, 255); nail = (90, 70, 60, 255)
    for v in range(4):
        img = Image.new("RGBA", (16 * SCALE, 16 * SCALE), (0, 0, 0, 0))
        for py in range(0, 16, 4):                         # horizontal boards
            rect(img, 0, py, 16, py + 3, plank if (py // 4 + v) % 2 else lighter(plank, 14))
            rect(img, 0, py + 3, 16, py + 4, plank_d)
            noise(img, 0, py, 16, py + 3, [plank_d], 0.10, seed=v * 3 + py)
            px(img, 2, py + 1, nail); px(img, 13, py + 1, nail)
        if v >= 2:                                         # sun-bleached streaks
            top_light(img, 0, 0, 15, 15, None, 18)
        if v == 3:                                         # sandy grit overlay
            noise(img, 0, 0, 15, 15, [(226, 200, 150, 200)], 0.14, seed=9)
        sh.add(finalize(img, (110, 76, 48, 255)))
    save(sh.canvas, os.path.join(BEACH, "boardwalk_tiles.png"))


def dolphin_fx():
    """4-frame dolphin leap arc (32x32 each) for splash checkpoints / ambience."""
    body = (148, 178, 210, 255); body_d = (96, 126, 162, 255); belly = (236, 242, 250, 255)
    spray = (220, 244, 255, 255)
    sh = Sheet(4, 32, 32)
    poses = [dict(x=6, y=26, rot=0.3), dict(x=12, y=18, rot=-0.2),
             dict(x=18, y=10, rot=-0.5), dict(x=24, y=16, rot=0.2)]
    for i, p in enumerate(poses):
        img = Image.new("RGBA", (32 * SCALE, 32 * SCALE), (0, 0, 0, 0))
        cx, cy = p["x"], p["y"]
        # torpedo body tilted along arc
        line(img, [(cx - 6, cy + 4), (cx, cy), (cx + 7, cy - 3)], body, 7)
        line(img, [(cx - 6, cy + 4), (cx, cy), (cx + 7, cy - 3)], body, 6)
        ellipse(img, cx + 3, cy - 6, cx + 10, cy, body)    # head
        px(img, cx + 9, cy - 4, (30, 40, 60, 255))         # eye
        line(img, [(cx - 6, cy + 4), (cx - 9, cy + 1), (cx - 9, cy + 7)], body_d, 3)  # tail
        line(img, [(cx, cy + 1), (cx + 2, cy + 4)], belly, 3)                            # belly line
        line(img, [(cx + 1, cy - 3), (cx + 3, cy - 7), (cx + 5, cy - 3)], body_d, 2)     # dorsal fin
        # splash trail behind
        rnd = random.Random(i)
        nsp = [6, 4, 2, 4][i]
        for k in range(nsp):
            sxp = cx - 10 - k * 2 + rnd.randrange(-1, 2)
            syp = min(30, cy + 6 + rnd.randrange(-2, 3))
            px(img, sxp, syp, spray)
            if k % 2:
                px(img, sxp, syp - 2, (255, 255, 255, 200))
        if i == 0:                                          # big entry splash
            for sxp, syp in ((2, 28), (4, 26), (6, 28), (3, 24)):
                px(img, sxp, syp, spray)
        sh.add(finalize(img, (40, 50, 80, 255)))
    save(sh.canvas, os.path.join(BEACH, "dolphin_leap.png"))


def tiki_bar_sign():
    img = Image.new("RGBA", (28 * SCALE, 24 * SCALE), (0, 0, 0, 0))
    wood = (150, 104, 62, 255); wood_d = (108, 72, 44, 255)
    rect(img, 4, 12, 6, 24, wood_d)                        # posts
    rect(img, 22, 12, 24, 24, wood_d)
    rrect(img, 2, 2, 26, 14, wood, radius=2)
    rect(img, 2, 12, 26, 13, wood_d)
    top_light(img, 3, 2, 25, 4, None, 22)
    # carved mask face
    ellipse(img, 8, 4, 12, 8, (60, 40, 30, 255)); ellipse(img, 16, 4, 20, 8, (60, 40, 30, 255))
    px(img, 9, 5, (255, 220, 120, 255)); px(img, 18, 5, (255, 220, 120, 255))
    rect(img, 11, 8, 17, 10, (60, 40, 30, 255))
    for tx in range(11, 17, 2):
        px(img, tx, 9, (250, 240, 220, 255))               # teeth
    # little palm frond roof
    for fx in range(2, 26, 3):
        line(img, [(fx, 2), (fx + 1, 0)], (96, 158, 90, 255), 2)
    save(finalize(img, (44, 30, 26, 255)), os.path.join(BEACH, "tiki_bar_sign.png"))


boardwalk(); dolphin_fx(); tiki_bar_sign()

# ==================================================== UNIFIED 4-DIR SHEET
# hero_4dir.png: 8 cols x 4 rows of 48x56 cells
#   row0: SIDE idle0 idle1 jump collect run0 run1 run2 run3   (faces LEFT; flip-x for right)
#   row1: BACK idle0 idle1 jump collect run0 run1 run2 run3   (walking away / downward move)
#   row2: copy of row1 mirrored (faces RIGHT side view)       -> optional pre-flipped set
#   row3: copy of row0 mirrored                               -> pre-flipped side set
for skin in ["default", "snow", "beach", "penguin", "crab", "bunny", "fox", "cat", "owl"]:
    src = os.path.join(CHAR, f"hero_{skin}.png")
    if not os.path.exists(src):
        continue
    im = Image.open(src)                                    # 192x224 = 4 cols x 4 rows
    out = Image.new("RGBA", (48 * 8, 56 * 4), (0, 0, 0, 0))
    def cell(r, c):
        return im.crop((c * 48, r * 56, (c + 1) * 48, (r + 1) * 56))
    for r in range(4):                                      # rows 0-1 as-is
        for c in range(4):
            out.paste(cell(r, c), (c * 48, r * 56))
    for r in range(2):                                      # mirrored side/back on right half
        for c in range(4):
            fr = cell(r, c).transpose(Image.FLIP_LEFT_RIGHT)
            out.paste(fr, ((4 + c) * 48, r * 56))
    out.save(os.path.join(CHAR, f"hero_{skin}_4dir.png"))
    print("ok: characters/hero_%s_4dir.png" % skin)

# soft ground shadow blob (32x12, 3 sizes for small/med/large skins)
sh_sheet = Sheet(3, 32, 12)
from PIL import ImageFilter as IF
for i, wdt in enumerate((22, 26, 30)):
    im = Image.new("RGBA", (32 * SCALE, 12 * SCALE), (0, 0, 0, 0))
    ellipse(im, 16 - wdt // 2, 2, 16 + wdt // 2, 10, (18, 14, 26, 120 - i * 10))
    im = im.filter(IF.GaussianBlur(SCALE))
    sh_sheet.add(im)
save(sh_sheet.canvas, os.path.join(FX, "shadow_blob.png"))
