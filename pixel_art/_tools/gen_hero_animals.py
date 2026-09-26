"""Premium hero ANIMAL skins v2 — 48x56 cells, same frame order as heroes.
penguin / crab / bunny / fox / cat / owl — detailed: layered feathers/fur
dithering, multi-tone shells with speculars, animated tails/ears per frame.
Faces LEFT. row0 idle0 idle1 jump collect | row1 run0..run3
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *
from PIL import ImageFilter as IF

OUT = "/workspace/pixel_art/characters"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)
W, H = 48, 56


def N():
    return Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))


def shadow(img):
    sh = Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))
    ellipse(sh, 13, 49, 35, 54, (20, 16, 30, 70))
    return Image.alpha_composite(img, sh.filter(IF.GaussianBlur(SCALE // 2)))


# =============================================================== PENGUIN
def penguin(ph=0):
    ph = int(round(float(ph)))
    """t = body tint dict; ph = anim phase value (leg/arm/sway offset)"""
    img = N()
    sway = ph % 3 - 1 if ph >= 0 else 0
    body = (44, 52, 74, 255); body_d = (26, 32, 50, 255); belly = (240, 244, 250, 255)
    beak = (248, 176, 64, 255); feet = (240, 156, 52, 255)
    lift = ph
    # feet
    fx = 18 + ph
    rect(img, 16 - abs(lift), 47, 23 - abs(lift), 49, feet)
    rect(img, 16 - abs(lift), 49, 24 - abs(lift), 50, darker(feet, 40))
    rect(img, 26 + (lift or sway), 47, 33 + (lift or sway), 49, feet)
    rect(img, 26 + (lift or sway), 49, 34 + (lift or sway), 50, darker(feet, 40))
    # tail feathers
    line(img, [(33, 40), (37, 44)], body_d, 3)
    # egg body
    rrect(img, 14, 20, 34, 47, body, radius=4)
    ellipse(img, 14, 26, 34, 47, body)
    # belly
    rrect(img, 16, 26, 30, 46, belly, radius=4)
    bottom_shade(img, 16, 26, 30, 46, None, 26)
    top_light(img, 16, 26, 30, 46, None, 10)
    # head
    ellipse(img, 15, 6, 35, 26, body)
    rect(img, 15, 16, 35, 24, body)
    # face plate (white cheeks around eyes)
    ellipse(img, 16, 10, 26, 20, belly)
    ellipse(img, 24, 10, 33, 19, belly)
    # dark eye mask band
    rect(img, 15, 12, 34, 15, body)
    # eyes looking left
    eye(img, 18, 12, look=(-1, 0), size=4)
    eye(img, 26, 12, look=(-1, 0), size=3)
    # beak (profile-ish, two lobes)
    poly = [(14, 16), (22, 15), (22, 19), (15, 19)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in poly], fill=beak)
    rect(img, 13, 16, 15, 18, beak)
    rect(img, 13, 18, 22, 19, darker(beak, 45))
    px(img, 14, 16, lighter(beak, 30))
    # blush
    blush(img, 17, 19, (250, 150, 150, 110))
    # wings (flap amount from ph)
    flap = 0 if ph in (0,1) else (2 if ph==2 else -1)
    # far wing
    limb_col = body_d
    ellipse(img, 30, 24 + flap, 37, 40 + flap, limb_col)
    # near wing swings while running
    wy = 24 - (sway * 2)
    ellipse(img, 12, wy, 18, 40 - wy + 24, limb_col)
    top_light(img, 12, wy, 18, wy + 3, None, 18)
    # little gold coin scarf badge? no—keep clean; add head highlight
    px(img, 20, 7, lighter(body, 40)); px(img, 21, 7, lighter(body, 40))
    return img


# ================================================================= CRAB
def crab(ph=0):
    ph = int(round(float(ph)))
    img = N()
    shell = (232, 84, 72, 255); shell_d = (176, 48, 52, 255); shell_l = (255, 140, 110, 255)
    leg = (214, 66, 64, 255); claw = (240, 110, 90, 255); claw_d = (190, 60, 60, 255)
    step = ph % 2
    # legs (3 per side, scuttle animation via step)
    for i, lx in enumerate((14, 20, 26)):
        off = (i + step) % 2
        line(img, [(lx, 38), (lx - 4 + off, 44), (lx - 5 + off, 49)], leg, 2)
        line(img, [(lx + 14, 38), (lx + 18 - off, 44), (lx + 19 - off, 49)], leg, 2)
    # claws raised a bit when jumping ph==-5
    raise_ = -abs(ph) if ph < 0 else 0
    # left claw
    cy = 30 + raise_
    line(img, [(15, 38), (11, cy + 4)], leg, 3)
    ellipse(img, 6, cy, 14, cy + 8, claw)
    rect(img, 6, cy + 2, 9, cy + 3, claw_d)          # claw split
    rect(img, 6, cy + 5, 10, cy + 6, claw_d)
    px(img, 7, cy, lighter(claw, 40))
    # right claw
    line(img, [(35, 38), (39, cy + 4)], leg, 3)
    ellipse(img, 36, cy, 44, cy + 8, claw)
    rect(img, 40, cy + 2, 44, cy + 3, claw_d)
    rect(img, 40, cy + 5, 43, cy + 6, claw_d)
    px(img, 42, cy, lighter(claw, 40))
    # shell dome
    ellipse(img, 10, 20, 40, 42, shell)
    rect(img, 10, 30, 40, 40, shell)
    bottom_shade(img, 10, 24, 40, 41, None, 40)
    top_light(img, 12, 20, 38, 26, None, 34)
    # shell speckles + spiral hints
    rnd = random.Random(5)
    noise(img, 14, 24, 36, 36, [shell_d, shell_l], 0.16, seed=11)
    for sx, sy in ((18, 28), (30, 26), (24, 33)):
        px(img, sx, sy, shell_d); px(img, sx + 1, sy, shell_d)
    # rim
    rect(img, 11, 39, 39, 40, shell_d)
    # eye stalks
    for ex in (18, 30):
        line(img, [(ex, 22), (ex - 1, 14)], shell_d, 2)
        ellipse(img, ex - 4, 8, ex + 2, 14, (252, 246, 238, 255))
        rect(img, ex - 3, 10 + (ph % 2 if ph > 0 else 0), ex, 13, INK)      # pupil
        px(img, ex - 3, 9, (255, 255, 255, 255))
    return img


# ================================================================= BUNNY
def bunny(ph=0):
    ph = int(round(float(ph)))
    img = N()
    fur = (238, 226, 232, 255); fur_d = (198, 180, 196, 255); pink = (244, 168, 184, 255)
    suit = (120, 190, 140, 255); suit_d = (78, 148, 100, 255)              # overalls
    kick = ph
    # fluffy tail
    ellipse(img, 33, 36, 39, 42, (255, 255, 255, 255))
    noise(img, 33, 36, 39, 42, [fur_d], 0.2, seed=2)
    # feet (big!)
    rect(img, 12 - max(0, -kick), 46, 22, 49, fur)
    rect(img, 12 - max(0, -kick), 49, 22, 50, fur_d)
    rect(img, 26 + max(0, kick), 46, 36, 49, fur)
    rect(img, 26 + max(0, kick), 49, 36, 50, fur_d)
    top_light(img, 12, 46, 22, 47, None, 12)
    # body overalls
    rrect(img, 15, 26, 34, 46, suit, radius=3)
    bottom_shade(img, 15, 26, 34, 46, None, 36)
    rect(img, 15, 42, 34, 42, suit_d)
    px(img, 24, 30, (250, 230, 120, 255)); px(img, 28, 30, (250, 230, 120, 255))  # buttons
    # chest fur
    rrect(img, 17, 24, 32, 32, fur, radius=3)
    # arms
    ellipse(img, 12, 28 - kick, 17, 36 - kick, fur)
    ellipse(img, 33, 28 + kick, 38, 36 + kick, fur)
    # head
    ellipse(img, 14, 10, 36, 30, fur)
    rect(img, 14, 20, 36, 28, fur)
    top_light(img, 16, 10, 34, 16, None, 14)
    bottom_shade(img, 14, 20, 36, 29, None, 22)
    # ears (long, one tilts with ph)
    tilt = ph % 2
    e1x = 18 - tilt
    line(img, [(e1x + 2, 12), (e1x, 0)], fur, 5)
    line(img, [(e1x + 2, 11), (e1x + 1, 2)], fur_d, 2)
    e2x = 26 + tilt
    line(img, [(e2x, 12), (e2x + 3, 1)], fur, 5)
    line(img, [(e2x + 1, 11), (e2x + 3, 3)], fur_d, 2)
    # face
    eye(img, 17, 17, look=(-1, 0), size=4)
    eye(img, 26, 17, look=(-1, 0), size=3)
    # nose + mouth + whiskers
    rect(img, 21, 22, 23, 23, pink)
    px(img, 22, 24, fur_d); px(img, 21, 25, fur_d); px(img, 23, 25, fur_d)
    rect(img, 12, 22, 16, 22, (255, 255, 255, 160))
    rect(img, 12, 24, 16, 24, (255, 255, 255, 160))
    rect(img, 28, 22, 32, 22, (255, 255, 255, 160))
    blush(img, 16, 23, (244, 150, 160, 110)); blush(img, 28, 23, (244, 150, 160, 110))
    return img


# ==================================================================== FOX
def fox(ph=0):
    ph = int(round(float(ph)))
    img = N()
    fur = (236, 128, 56, 255); fur_d = (186, 82, 34, 255); cream = (252, 236, 214, 255)
    dark = (60, 44, 52, 255)
    trot = ph
    # big bushy tail (wags with ph)
    wag = (trot % 3) - 1
    for i in range(6):
        ellipse(img, 32 + i, 26 - i + wag * 2, 44 + i - 6, 38 - i + wag * 2, fur if i < 4 else cream)
    ellipse(img, 36, 24 + wag, 46, 34 + wag, fur)
    ellipse(img, 41, 24 + wag, 46, 30 + wag, cream)
    # legs (dark socks)
    for lx, off in ((16, -trot), (22, trot), (28, trot), (33, -trot)):
        rect(img, lx, 42, lx + 3, 48 + (off % 2), dark)
        rect(img, lx, 48 + (off % 2), lx + 4, 49 + (off % 2), darker(dark, 25))
    # body
    rrect(img, 13, 28, 36, 44, fur, radius=3)
    rrect(img, 14, 34, 30, 43, cream, radius=3)
    bottom_shade(img, 13, 28, 36, 44, None, 34)
    top_light(img, 14, 28, 34, 31, None, 26)
    # arms
    ellipse(img, 11, 30 - trot, 16, 38 - trot, fur_d)
    ellipse(img, 33, 30 + trot, 38, 38 + trot, fur_d)
    # head (pointy muzzle to the left)
    ellipse(img, 12, 10, 36, 30, fur)
    rect(img, 12, 20, 36, 28, fur)
    # ears
    tri = [(14, 14), (18, 2), (22, 14)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in tri], fill=fur)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(16, 12), (18, 5), (21, 12)]], fill=(40, 30, 40, 255))
    tri2 = [(27, 14), (31, 2), (35, 14)]
    d.polygon([(x * SCALE, y * SCALE) for x, y in tri2], fill=fur)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(29, 12), (31, 5), (33, 12)]], fill=(40, 30, 40, 255))
    # cheek fluff
    rrect(img, 11, 18, 22, 28, cream, radius=2)
    rrect(img, 26, 18, 36, 27, cream, radius=2)
    # muzzle pointing left
    rrect(img, 8, 21, 16, 27, cream, radius=2)
    rect(img, 7, 22, 8, 23, dark)                       # nose
    px(img, 7, 22, lighter(dark, 30))
    # eyes
    eye(img, 15, 17, look=(-1, 0), size=4)
    eye(img, 25, 17, look=(-1, 0), size=3)
    # brow marks
    rect(img, 14, 13, 18, 13, fur_d); rect(img, 26, 13, 30, 13, fur_d)
    return img


# ==================================================================== CAT
def cat(ph=0):
    ph = int(round(float(ph)))
    img = N()
    fur = (128, 138, 190, 255); fur_d = (88, 96, 148, 255); cream = (246, 238, 226, 255)
    pink = (240, 160, 176, 255)
    swish = ph % 3 - 1
    # curling tail (segments along an arc, tip moves with swish)
    pts = [(34, 40), (40, 38), (43, 32), (41, 26), (36, 24 + swish * 2)]
    line(img, pts, fur, 4)
    line(img, pts[:-1], fur, 4)
    px(img, 36, 23 + swish * 2, cream); px(img, 37, 23 + swish * 2, cream)
    for sx, sy in ((40, 36), (42, 30)):
        px(img, sx, sy, fur_d)
    # paws
    for lx, off in ((15, -max(0, swish)), (21, max(0, swish)), (28, -max(0, swish)), (33, max(0, swish))):
        ellipse(img, lx, 44 + off, lx + 5, 48 + off, cream)
        px(img, lx + 1, 47 + off, fur_d)
    # body
    rrect(img, 13, 28, 36, 46, fur, radius=4)
    rrect(img, 17, 34, 32, 45, cream, radius=3)
    bottom_shade(img, 13, 28, 36, 46, None, 32)
    # tabby stripes on back
    for sx in (24, 29, 33):
        rect(img, sx, 28, sx + 1, 31, fur_d)
    # arms
    ellipse(img, 11, 30, 16, 38, fur)
    ellipse(img, 33, 30, 38, 38, fur)
    # head
    ellipse(img, 13, 10, 37, 30, fur)
    rect(img, 13, 20, 37, 28, fur)
    # ears (triangles)
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(15, 14), (18, 3), (24, 12)]], fill=fur)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(17, 12), (18, 6), (22, 11)]], fill=pink)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(27, 12), (33, 3), (36, 14)]], fill=fur)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(29, 11), (33, 6), (34, 12)]], fill=pink)
    # face: muzzle + big eyes
    ellipse(img, 12, 18, 22, 28, cream)
    ellipse(img, 26, 18, 36, 27, cream)
    eye(img, 16, 16, look=(-1, 0), size=5)
    eye(img, 27, 16, look=(-1, 0), size=4)
    # tiny open smile (meow) when collecting uses ph=-9
    if swish == -99:
        pass
    rect(img, 20, 23, 22, 24, pink)                     # nose
    px(img, 21, 25, fur_d); px(img, 20, 26, fur_d); px(img, 22, 26, fur_d)
    # whiskers
    rect(img, 8, 22, 12, 22, (255, 255, 255, 170))
    rect(img, 8, 25, 12, 25, (255, 255, 255, 170))
    rect(img, 32, 22, 37, 22, (255, 255, 255, 170))
    return img


# =================================================================== OWL
def owl(ph=0):
    ph = int(round(float(ph)))
    img = N()
    feather = (150, 108, 72, 255); f_d = (108, 74, 50, 255); f_l = (196, 156, 110, 255)
    face = (238, 220, 190, 255); beak = (240, 168, 70, 255); foot = (232, 158, 62, 255)
    blink = ph % 4 == 3
    flap = -abs(ph) if ph < 0 else 0
    # ear tufts
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(14, 12), (16, 2), (22, 10)]], fill=f_d)
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(28, 10), (34, 2), (36, 12)]], fill=f_d)
    # feet
    for fx in (17, 27):
        for k in range(3):
            line(img, [(fx + k * 2, 44), (fx + k * 2 - 1 + ph % 2, 49)], foot, 2)
    # body egg
    ellipse(img, 12, 14, 38, 46, feather)
    rect(img, 12, 24, 38, 42, feather)
    # chest chevrons (V feather pattern)
    for row, yy in enumerate(range(28, 44, 4)):
        for col, xx in enumerate(range(15, 36, 5)):
            ox = (row % 2) * 2
            line(img, [(xx + ox, yy), (xx + ox + 2, yy + 2), (xx + ox + 4, yy)], f_l, 1)
    # facial discs
    ellipse(img, 13, 10, 25, 22, face)
    ellipse(img, 25, 10, 37, 22, face)
    ring = f_d
    for cx, cyy, r in ((19, 16, 6), (31, 16, 6)):
        d.ellipse([(cx - r) * SCALE, (cyy - r) * SCALE, (cx + r) * SCALE, (cyy + r) * SCALE], outline=ring, width=SCALE)
    # huge amber eyes
    for ex in (19, 31):
        if blink:
            rect(img, ex - 3, 16, ex + 2, 17, f_d)
        else:
            ellipse(img, ex - 3, 12, ex + 3, 19, (250, 196, 70, 255))
            rect(img, ex - 2, 14, ex + 1, 18, INK)
            px(img, ex - 2, 13, (255, 255, 255, 255))
            px(img, ex + 1, 16, (255, 240, 200, 200))
    # beak between discs
    d.polygon([(x * SCALE, y * SCALE) for x, y in [(23, 17), (27, 17), (25, 22)]], fill=beak)
    px(img, 24, 18, lighter(beak, 30))
    # wings spread when flap!=0
    wy = 22 + flap
    ellipse(img, 5, wy, 14, 42, f_d)
    ellipse(img, 36, wy, 45, 42, f_d)
    for i in range(4):
        rect(img, 6, wy + 6 + i * 4, 13, wy + 6 + i * 4, feather)
        rect(img, 37, wy + 6 + i * 4, 44, wy + 6 + i * 4, feather)
    top_light(img, 14, 14, 36, 18, None, 16)
    return img


BUILDERS = {"penguin": penguin, "crab": crab, "bunny": bunny, "fox": fox, "cat": cat, "owl": owl}

# frame params: idle small bob, run big phase, jump negative(flap/tuck), collect wave
FRAMES = {
    "penguin": [dict(ph=0), dict(ph=0.4), dict(ph=2.0), dict(ph=1.2),
                dict(ph=-1), dict(ph=2), dict(ph=-2), dict(ph=3)],
    "crab":    [dict(ph=0), dict(ph=1), dict(ph=-3), dict(ph=2),
                dict(ph=1), dict(ph=0), dict(ph=1), dict(ph=0)],
    "bunny":   [dict(ph=0), dict(ph=1), dict(ph=4), dict(ph=2),
                dict(ph=1), dict(ph=2), dict(ph=3), dict(ph=0)],
    "fox":     [dict(ph=0), dict(ph=1), dict(ph=3), dict(ph=2),
                dict(ph=1), dict(ph=2), dict(ph=3), dict(ph=4)],
    "cat":     [dict(ph=0), dict(ph=1), dict(ph=2), dict(ph=3),
                dict(ph=1), dict(ph=2), dict(ph=3), dict(ph=4)],
    "owl":     [dict(ph=0), dict(ph=1), dict(ph=-3), dict(ph=2),
                dict(ph=1), dict(ph=2), dict(ph=3), dict(ph=4)],
}
ORDER = ["idle0", "idle1", "jump", "collect", "run0", "run1", "run2", "run3"]

for name, fn in BUILDERS.items():
    sheet = Sheet(4, W, H, rows=2)
    prev = []
    for i, prm in enumerate(FRAMES[name]):
        fr = finalize(fn(**prm), (36, 26, 44, 255))
        fr = shadow(fr.resize((W * SCALE, H * SCALE)))
        fr = finalize_shadowed = fr
        sheet.add(fr)
        prev.append(fr)
    sheet.save(os.path.join(OUT, f"hero_{name}.png"))
    save_scaled(hframes(prev[:4]), os.path.join(PREV, f"hero_{name}_idle_jump_collect@3x.png"), 3)
    save_scaled(hframes(prev[4:]), os.path.join(PREV, f"hero_{name}_run@3x.png"), 3)
print("animal heroes ok:", ", ".join(BUILDERS))
