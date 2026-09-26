"""Final pass v5 — completes the up/down/left/right (side + top-down hybrid) view.

1. BACK-view jump animation for all 9 hero skins (the back rows previously reused
   a side-jump silhouette; now every skin gets a proper walk-away airborne pose).
   -> characters/hero_<skin>_back.png        4x2 @48x56
        row0 = BACK idle0 idle1 JUMP collect      row1 = BACK run0..run3
   -> rebuilds characters/hero_<skin>_4dir.png  8x4 @48x56
        row0 = SIDE idle0 idle1 jump collect run0..run3   (faces LEFT)
        row1 = BACK idle0 idle1 JUMP collect run0..run3   (move DOWN / away)
        row2 = BACK mirrored (faces RIGHT while moving away)
        row3 = SIDE mirrored (faces RIGHT)
      "move UP" reuses the same BACK frames with Sprite2D.flip_v = true at
      runtime — standard trick for this projection, no extra art needed.

2. Back-view sheets for the jelly enemies:
   -> enemies/jelly_green_back.png / jelly_ice_back.png / jelly_ember_back.png
      (same 5x2 @32 grid as their front sheets)

3. Extra footstep dust per world (sprint double-kick + slide/skid cloud):
   -> effects/dust_meadow_extra.png / dust_snow_extra.png / dust_beach_extra.png
      4x2 @48x56 : row0 sprint(4), row1 skid(4) — palettes matched to each ground.

4. Animated water-edge foam strips for the river & sea boundaries:
   -> ground/foam_river.png  (meadow/river edge, 4-frame cycle, 16x16 cells)
   -> ground/foam_sea.png    (beach surf edge, 4-frame cycle)
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *
from PIL import Image, ImageDraw, ImageFilter as IF

CHAR = "/workspace/pixel_art/characters"
ENEM = "/workspace/pixel_art/enemies"
FX = "/workspace/pixel_art/effects"
GND = "/workspace/pixel_art/ground"
PREV = os.path.join(CHAR, "previews")
os.makedirs(PREV, exist_ok=True)
W, H, SCALE = 48, 56, 4


def N():
    return Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))


def cl(im, r, c):
    """crop cell (r,c) from a sheet of WxH logical cells (already SCALE-scaled)."""
    return im.crop((c * W * SCALE, r * H * SCALE, (c + 1) * W * SCALE, (r + 1) * H * SCALE))


# ====================================================== BACK-JUMP OVERLAYS
# Per-skin airborne extras drawn on top of the blended back-idle/run body:
# tucked limbs silhouettes, raised wings/claws/ears, lifted tails.
def overlay_jump(img, skin):
    if skin == "penguin":                       # wings thrown up, feet tucked
        wing = (44, 52, 74, 255); wd = (26, 32, 50, 255)
        line(img, [(13, 26), (9, 16)], wd, 4); line(img, [(35, 26), (39, 16)], wd, 4)
        line(img, [(13, 25), (10, 17)], wing, 2); line(img, [(35, 25), (38, 17)], wing, 2)
        rect(img, 18, 44, 23, 46, (240, 156, 52, 255))       # tucked webbed feet
        rect(img, 26, 44, 31, 46, (240, 156, 52, 255))
        ellipse(img, 15, 40, 34, 45, (26, 32, 50, 255))      # tail fan down-flare
    elif skin == "crab":                        # claws raised, legs splayed in air
        shell = (226, 92, 74, 255); sd = (150, 52, 44, 255)
        for sx, dsign in ((12, -1), (36, 1)):      # claws raised overhead
            line(img, [(sx, 26), (sx + 3 * dsign, 18)], sd, 4)
            x0, x1 = sorted((sx + dsign - 2, sx + 6 * dsign))
            ellipse(img, x0, 12, x1, 19, shell)
        for i, lx in enumerate((16, 22, 27, 32)):            # curled swim legs
            line(img, [(lx, 42), (lx + (2 if i % 2 else -2), 45)], sd, 2)
    elif skin == "bunny":                       # ears flopped up, feet kicked back
        fd = (196, 190, 206, 255)
        line(img, [(20, 8), (18, 1)], fd, 3); line(img, [(28, 8), (30, 1)], fd, 3)
        ellipse(img, 21, 42, 27, 47, (252, 252, 255, 255))   # cotton tail puffs out
        rect(img, 15, 44, 20, 46, fd); rect(img, 29, 44, 34, 46, fd)
    elif skin == "fox":                         # big tail streaming downward-back
        fur = (236, 138, 62, 255); fd = (178, 92, 40, 255)
        line(img, [(33, 38), (39, 46)], fd, 6)
        line(img, [(33, 37), (38, 44)], fur, 4)
        ellipse(img, 37, 44, 42, 49, (252, 244, 232, 255))   # white tail tip
        rect(img, 16, 44, 20, 46, fd); rect(img, 28, 44, 32, 46, fd)  # paws tucked
    elif skin == "cat":                         # tail curling up, hind legs tucked
        fur = (120, 128, 150, 255); fd = (78, 84, 106, 255)
        line(img, [(34, 40), (40, 32), (38, 24)], fd, 3)     # S-curve airborne tail
        line(img, [(34, 39), (39, 32), (37, 25)], fur, 2)
        rect(img, 17, 43, 22, 45, fd); rect(img, 27, 43, 32, 45, fd)
    elif skin == "owl":                         # wings spread wide, talons folded
        feather = (150, 112, 78, 255); fdd = (96, 66, 44, 255)
        line(img, [(14, 28), (6, 20)], fdd, 5); line(img, [(34, 28), (42, 20)], fdd, 5)
        line(img, [(14, 27), (8, 21)], feather, 3); line(img, [(34, 27), (40, 21)], feather, 3)
        rect(img, 20, 44, 23, 46, (240, 190, 90, 255)); rect(img, 26, 44, 29, 46, (240, 190, 90, 255))
    elif skin == "snow":                        # scarf streams upward in the wind
        scarf = (226, 84, 96, 255)
        line(img, [(28, 14), (36, 6), (40, 2)], scarf, 3)    # trailing scarf ends
        rect(img, 17, 45, 22, 47, (60, 44, 36, 255)); rect(img, 27, 45, 32, 47, (60, 44, 36, 255))
    elif skin == "beach":                       # sunhat lifts off, sandals tuck
        hat = (244, 214, 120, 255)
        ellipse(img, 16, 2, 33, 8, hat)                     # hat floating higher
        rect(img, 15, 45, 21, 47, (196, 128, 96, 255)); rect(img, 27, 45, 33, 47, (196, 128, 96, 255))
    else:                                       # default adventurer: pack bounces up
        strap = (122, 84, 54, 255)
        rect(img, 20, 12, 29, 15, strap)                    # pack top lifted
        rect(img, 16, 45, 22, 47, (60, 44, 36, 255)); rect(img, 26, 45, 32, 47, (60, 44, 36, 255))
    # universal motion streaks under the feet
    d = ImageDraw.Draw(img)
    for x0, x1, a in ((18, 24, 70), (27, 35, 95), (21, 31, 55)):
        y = 52
        d.line([x0 * SCALE, y * SCALE, x1 * SCALE, y * SCALE], fill=(255, 255, 255, a), width=SCALE)


def make_back_jump(src_big, skin):
    """Blend back-idle (row2 col0) with back-run stride (row2 col3), stretch
    slightly, lift off ground, then add skin-specific airborne overlay."""
    idle = cl(src_big, 2, 0)
    run = cl(src_big, 2, 3)
    base = Image.blend(idle.convert("RGB"), run.convert("RGB"), 0.55).convert("RGBA")
    alpha = Image.blend(idle.split()[3], run.split()[3], 0.5)
    base.putalpha(alpha)
    w, h = base.size
    stretched = base.resize((int(w * 0.96), int(h * 1.05)), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(stretched, (int(w * 0.02), -int(h * 0.035)), stretched)
    ov = N()
    overlay_jump(ov, skin)
    canvas = Image.alpha_composite(canvas, ov)
    return soften_edges(canvas, edge_col=(34, 24, 48, 255), strength=0.5)


SKINS = ["default", "snow", "beach", "penguin", "crab", "bunny", "fox", "cat", "owl"]

print("--- hero back sheets + rebuilt 4dir ---")
for skin in SKINS:
    src = os.path.join(CHAR, f"hero_{skin}.png")
    if not os.path.exists(src):
        print("skip (missing):", src); continue
    im = Image.open(src).convert("RGBA")          # native 192x224
    big = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    def cell(r, c):
        return im.crop((c * W, r * H, (c + 1) * W, (r + 1) * H))
    jump_back = make_back_jump(big, skin)         # SCALE-space 48*4 x 56*4
    # standalone back sheet 4x2 @48x56 (native pixels)
    back_sheet = Image.new("RGBA", (W * 4, H * 2), (0, 0, 0, 0))
    seq0 = [cell(2, 0), cell(2, 1), jump_back.resize((W, H), Image.NEAREST), cell(2, 3)]
    for c, fr in enumerate(seq0):
        back_sheet.paste(fr, (c * W, 0))
    for c in range(4):
        back_sheet.paste(cell(3, c), (c * W, H))
    back_sheet.save(os.path.join(CHAR, f"hero_{skin}_back.png"))
    # unified 4dir 8x4
    uni = Image.new("RGBA", (W * 8, H * 4), (0, 0, 0, 0))
    side_row = [cell(0, c) for c in range(4)] + [cell(1, c) for c in range(4)]
    back_row = seq0 + [cell(3, c) for c in range(4)]
    for c, fr in enumerate(side_row):
        uni.paste(fr, (c * W, 0))
    for c, fr in enumerate(back_row):
        uni.paste(fr, (c * W, H))
    for r in range(2):
        for c in range(8):
            fr = uni.crop((c * W, r * H, (c + 1) * W, (r + 1) * H)).transpose(Image.FLIP_LEFT_RIGHT)
            uni.paste(fr, (c * W, (2 + r) * H))
    uni.save(os.path.join(CHAR, f"hero_{skin}_4dir.png"))
    # preview strip @3x: back idle, jump, collect, run0..3
    pv = Image.new("RGBA", (7 * W, H), (0, 0, 0, 0))
    seq = [cell(2, 0), seq0[2], cell(2, 3), cell(3, 0), cell(3, 1), cell(3, 2), cell(3, 3)]
    for c, fr in enumerate(seq):
        pv.paste(fr, (c * W, 0), fr)
    pv.resize((pv.width * 3, pv.height * 3), Image.NEAREST).save(
        os.path.join(PREV, f"hero_{skin}_back_idle_jump_run@3x.png"))
    print("ok: hero_%s_back.png + hero_%s_4dir.png" % (skin, skin))


# ===================================================== JELLY ENEMY BACK SHEETS
print("--- jelly enemy back sheets ---")
JCOL = {
    "jelly_green": ((120, 210, 120, 235), (60, 130, 70, 255), (190, 245, 190, 255)),
    "jelly_ice":   ((150, 215, 245, 235), (80, 140, 190, 255), (220, 245, 255, 255)),
    "jelly_ember": ((235, 130, 70, 235), (150, 60, 40, 255), (255, 210, 140, 255)),
}
ew, eh, ES = 32, 32, 4
def EN():
    return Image.new("RGBA", (ew * ES, eh * ES), (0, 0, 0, 0))

def blob_back(img, cols, sq, tent=0):
    col, col_d, col_l = cols
    cx, base = 16, 26
    w = int(10 + sq * 0.5); h = int(9 - sq)
    ellipse(img, cx - w, base - 2 * h, cx + w, base, col)
    rect(img, cx - w, base - h, cx + w, base, col)
    rrect(img, cx - w + 1, base - 2 * h - 2, cx + w - 1, base - 4, col, radius=3)
    bottom_shade(img, cx - w, base - 2 * h, cx + w, base, None, 40)
    top_light(img, cx - w + 2, base - 2 * h + 1, cx + w - 2, base - h, None, 30)
    ellipse(img, cx - 4, base - 2 * h + 2, cx + 1, base - h + 1, lighter(col, 40, 180))
    for tx in range(cx - w + 2, cx + w - 1, 3):              # tentacle fringe
        line(img, [(tx, base - 1), (tx + tent, base + 2)], col_d, 1)

for name, cols in JCOL.items():
    sh = Sheet(5, ew, eh, rows=2)
    for sq in (0, -1, 0, 1):                                 # idle breathe
        img = EN(); blob_back(img, cols, sq)
        sh.add(finalize(img, (34, 24, 48, 255)))
    img = EN(); blob_back(img, cols, 0)
    sh.add(finalize(img, (34, 24, 48, 255)))
    for j, wob in enumerate((-2, -1, 1, 2)):                 # move waddle
        img = EN(); blob_back(img, cols, 0 if j % 2 else 1, tent=wob)
        sh.add(finalize(img, (34, 24, 48, 255)))
    img = EN(); blob_back(img, cols, 3)                      # squash/hit
    sh.add(finalize(img, (34, 24, 48, 255)))
    canvas = sh.save(os.path.join(ENEM, f"{name}_back.png"))
    canvas.resize((canvas.width * 3, canvas.height * 3), Image.NEAREST).save(
        os.path.join(ENEM, "previews", f"{name}_back@3x.png"))
    print("ok: enemies/%s_back.png" % name)


# ====================================================== EXTRA DUST VARIANTS
print("--- extra dust variants ---")
MEADOW_P = [(214, 190, 140, 255), (190, 165, 115, 255), (168, 142, 96, 255)]
SNOW_P = [(236, 244, 252, 255), (214, 228, 242, 255), (196, 212, 230, 255)]
BEACH_P = [(240, 222, 170, 255), (222, 200, 148, 255), (200, 178, 126, 255)]
CHIPS = {"meadow": [(120, 160, 90, 255), (150, 120, 80, 255)],
         "snow": [(180, 210, 235, 255), (210, 235, 250, 255)],
         "beach": [(235, 205, 150, 255), (170, 210, 220, 255)]}

def puff(dx, dy, r, col):
    img = N()
    ellipse(img, dx - r, dy - r, dx + r, dy + r, col)
    return img.filter(IF.GaussianBlur(SCALE))

def grain(name, pal, chips):
    rnd = random.Random(11)
    sprint, skid = [], []
    for f in range(4):                       # sprint: alternating double kicks
        img = N()
        kx = 26 if f % 2 == 0 else 33
        for i in range(3 + (f > 1)):
            dx = kx + rnd.randint(-2, 8) + f * 3
            dy = 47 - rnd.randint(0, 3) - f
            r = rnd.randint(2, 5)
            img = Image.alpha_composite(img, puff(dx, dy, r, shade(pal[i % len(pal)], da=90 - f * 20)))
        for i in range(3):
            px(img, 28 + rnd.randint(0, 14) + f * 2, 45 - rnd.randint(0, 5),
               chips[rnd.randrange(len(chips))])
        sprint.append(img)
    for f in range(4):                       # skid: long low dragged cloud
        img = N()
        for i in range(5):
            dx = 28 + i * 3 + f * 2
            dy = 48 + rnd.randint(-1, 1)
            r = max(1, 5 - i) + (0 if f < 2 else -1)
            img = Image.alpha_composite(img, puff(dx, dy, r,
                              shade(pal[i % len(pal)], da=110 - f * 25 - i * 8)))
        if f < 3:
            for i in range(2):
                px(img, 30 + rnd.randint(2, 16), 47, chips[rnd.randrange(len(chips))])
        skid.append(img)
    sh = Sheet(4, W, H, rows=2)
    for fr in sprint + skid:
        sh.add(fr)
    canvas = sh.save(os.path.join(FX, f"dust_{name}_extra.png"))
    pv = canvas.resize((canvas.width * 3, canvas.height * 3), Image.NEAREST)
    pv.save(os.path.join(FX, "previews", f"dust_{name}_extra@3x.png"))
    print("ok: effects/dust_%s_extra.png" % name)

grain("meadow", MEADOW_P, CHIPS["meadow"])
grain("snow", SNOW_P, CHIPS["snow"])
grain("beach", BEACH_P, CHIPS["beach"])


# ======================================================== WATER EDGE FOAM
print("--- foam strips ---")
def lerp_col(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))

def foam_strip(path, base_a, base_b, seed):
    """4-frame cycle, 4x1 grid of 16x16 cells."""
    rnd = random.Random(seed)
    fw, fh, S = 16, 16, 4
    sh = Sheet(4, fw, fh)
    for f in range(4):
        img = Image.new("RGBA", (fw * S, fh * S), (0, 0, 0, 0))
        heights = []
        for x in range(fw):
            hgt = 6 + int(2.5 * abs(((x + f * 2) % 8) - 4) / 4)
            heights.append(hgt)
            rect(img, x, fh - hgt, x, fh - 1, lerp_col(base_a, base_b, ((x + f) % 4) / 4.0))
        for x in range(fw):                                   # foam caps
            edge = fh - heights[x]
            m = (x + f) % 3
            if m == 0:
                px(img, x, edge, (245, 252, 255, 235))
                if rnd.random() < 0.5:
                    px(img, x, edge - 1, (230, 245, 255, 140))
            elif m == 1:
                px(img, x, edge, (215, 238, 250, 190))
        for _ in range(2):                                    # sparkle bubbles
            bx, by = rnd.randrange(fw), rnd.randrange(fh - 5, fh - 1)
            px(img, bx, by, (255, 255, 255, 160))
        sh.add(img)
    canvas = sh.save(path)
    canvas.resize((canvas.width * 3, canvas.height * 3), Image.NEAREST).save(
        os.path.join(GND, "previews", os.path.basename(path).replace(".png", "@3x.png")))
    print("ok:", path)

A1 = (96, 176, 214, 200); B1 = (120, 196, 228, 200)     # river/meadow water
A2 = (70, 150, 200, 205); B2 = (110, 190, 230, 205)     # sea/beach water
foam_strip(os.path.join(GND, "foam_river.png"), A1, B1, 5)
foam_strip(os.path.join(GND, "foam_sea.png"), A2, B2, 9)
print("ALL DONE v5")
