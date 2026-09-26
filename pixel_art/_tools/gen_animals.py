"""Cute animal character skins: penguin, crab, bunny, fox, cat, owl.
Sheet 4x2 @32x32, face LEFT. Row0: idle(2) jump collect | Row1: run(4). Bottom y=30.
Also emits 16x16 UI skin icons into ui/."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

CH = "/workspace/pixel_art/characters"
UI = "/workspace/pixel_art/ui"
PREV = os.path.join(CH, "previews")
os.makedirs(PREV, exist_ok=True)


def blank():
    return Image.new("RGBA", (32 * SCALE, 32 * SCALE), (0, 0, 0, 0))


def eye(img, x, y, dark=(40, 32, 48), shine=True):
    rect(img, x, y, x + 1, y + 2, dark)
    if shine:
        px(img, x, y, (255, 255, 255, 255))


# ------------------------------------------------------------------ PENGUIN
def penguin(pose="idle", f=0):
    img = blank()
    BK = (48, 56, 82); BD = (30, 36, 58); WH = (240, 244, 250); BE = (248, 170, 60)
    bob = {"idle": [0, -1][f % 2], "jump": -3, "collect": -1}.get(pose, [0, -1, 0, 1][f % 4])
    # feet
    fw = 4
    fx1, fx2 = 11, 17
    if pose == "run":
        fx1 += [-2, 0, 2, 0][f % 4]; fx2 += [-2, 0, 2, 0][(f + 2) % 4]
    rect(img, fx1, 29 + bob, fx1 + fw, 30 + bob, BE)
    rect(img, fx2, 29 + bob, fx2 + fw, 30 + bob, BE)
    # body: black back, white belly
    ellipse(img, 9, 12 + bob, 22, 30 + bob, BK)
    ellipse(img, 11, 16 + bob, 20, 29 + bob, WH)
    # head
    ellipse(img, 10, 4 + bob, 21, 15 + bob, BK)
    ellipse(img, 12, 8 + bob, 20, 14 + bob, WH)
    # beak pointing left
    poly = [(9, 9 + bob), (5, 10 + bob), (9, 11 + bob)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE + SCALE / 2, y * SCALE + SCALE / 2) for x, y in poly], fill=BE)
    eye(img, 12, 7 + bob)
    # wings (flap on jump/collect/run)
    wa = {"jump": -3, "collect": -4}.get(pose, [0, 0, 1, 2][f % 4] if pose == "run" else 0)
    line(img, [(19, 15 + bob), (22, 19 + bob + wa)], BD, 2)
    # rosy cheeks
    px(img, 11, 10 + bob, (250, 170, 170, 180))
    return outline(img)


# --------------------------------------------------------------------- CRAB
def crab(pose="idle", f=0):
    img = blank()
    RD = (226, 92, 74); RK = (168, 52, 48); OR = (255, 150, 120)
    bob = {"idle": [0, -1][f % 2], "jump": -3, "collect": -1}.get(pose, [0, -1, 0, -1][f % 4])
    # legs (3 per side, scuttle when running)
    ph = [0, 1, 0, -1][f % 4] if pose == "run" else 0
    for i, lx in enumerate((10, 14, 18)):
        line(img, [(lx, 24 + bob), (lx - 3 + (i % 2) * 6, 28 + bob + ph)], RK, 1)
    # body shell
    ellipse(img, 7, 16 + bob, 24, 26 + bob, RD)
    ellipse(img, 9, 17 + bob, 22, 21 + bob, OR)
    # eyes on stalks
    for ex in (11, 18):
        rect(img, ex, 11 + bob, ex + 1, 15 + bob, RD)
        ellipse(img, ex - 1, 8 + bob, ex + 2, 11 + bob, (255, 255, 255, 255))
        px(img, ex, 9 + bob, (40, 30, 40))
    # claws out front (raise on collect/jump)
    lift = -4 if pose in ("jump", "collect") else 0
    ellipse(img, 2, 18 + bob + lift, 7, 23 + bob + lift, RD)
    px(img, 2, 18 + bob + lift, RK); px(img, 4, 17 + bob + lift, RK)
    ellipse(img, 24, 19 + bob, 29, 23 + bob, RD)
    return outline(img)


# -------------------------------------------------------------------- BUNNY
def bunny(pose="idle", f=0):
    img = blank()
    FU = (240, 228, 222); FD = (206, 186, 180); PK = (244, 170, 186)
    bob = {"idle": [0, -1][f % 2], "jump": -3, "collect": -1}.get(pose, [0, -1, -2, -1][f % 4])
    # feet
    if pose == "run":
        rect(img, 10 + [-1, 1, 2, 0][f % 4], 29, 13, 30, FU)
        rect(img, 17 + [1, -1, -2, 0][f % 4], 29, 20, 30, FU)
    else:
        rect(img, 10, 29 + bob, 13, 30 + bob, FU); rect(img, 17, 29 + bob, 20, 30 + bob, FU)
    # tail puff (right)
    ellipse(img, 22, 24 + bob, 25, 27 + bob, (255, 255, 255, 255))
    # body + head
    ellipse(img, 9, 17 + bob, 23, 30 + bob, FU)
    ellipse(img, 8, 8 + bob, 18, 19 + bob, FU)
    # ears, one flopped forward
    ear_tilt = [0, 1, 0, -1][f % 4] if pose == "run" else 0
    line(img, [(11, 8 + bob), (10 + ear_tilt, 1 + bob)], FU, 3)
    line(img, [(11, 7 + bob), (10 + ear_tilt, 2 + bob)], PK, 1)
    line(img, [(15, 8 + bob), (17 + ear_tilt, 2 + bob)], FU, 3)
    line(img, [(15, 7 + bob), (17 + ear_tilt, 3 + bob)], PK, 1)
    eye(img, 10, 12 + bob)
    px(img, 8, 15 + bob, PK)                       # nose
    line(img, [(9, 16 + bob), (11, 17 + bob)], FD, 1)  # cheek whisker
    return outline(img)


# ---------------------------------------------------------------------- FOX
def fox(pose="idle", f=0):
    img = blank()
    OR = (235, 138, 66); CR = (252, 238, 220); DK = (70, 48, 44)
    bob = {"idle": [0, -1][f % 2], "jump": -3, "collect": -1}.get(pose, [0, -1, -2, -1][f % 4])
    # bushy tail behind (curls up when jumping)
    tl = -3 if pose in ("jump", "collect") else 0
    ellipse(img, 22, 18 + bob + tl, 30, 27 + bob + tl, OR)
    ellipse(img, 26, 18 + bob + tl, 30, 23 + bob + tl, CR)
    # legs
    ly = [-1, 0, 1, 0][f % 4] if pose == "run" else 0
    for lx in (10, 13, 17, 20):
        rect(img, lx, 27 + bob, lx + 2, 30 + min(3, max(0, 3 + ly)), DK)
    # body + chest
    ellipse(img, 8, 16 + bob, 24, 29 + bob, OR)
    ellipse(img, 9, 20 + bob, 15, 28 + bob, CR)
    # head with snout to the left
    ellipse(img, 6, 6 + bob, 18, 17 + bob, OR)
    ellipse(img, 4, 12 + bob, 10, 16 + bob, CR)
    px(img, 4, 12 + bob, DK)                        # nose tip
    # pointy ears
    tri = [(8, 7 + bob), (7, 1 + bob), (11, 5 + bob)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * SCALE + SCALE / 2, y * SCALE + SCALE / 2) for x, y in tri], fill=OR)
    tri = [(14, 6 + bob), (15, 0 + bob), (17, 5 + bob)]
    d.polygon([(x * SCALE + SCALE / 2, y * SCALE + SCALE / 2) for x, y in tri], fill=OR)
    eye(img, 10, 10 + bob)
    return outline(img)


# ---------------------------------------------------------------------- CAT
def cat(pose="idle", f=0):
    img = blank()
    GY = (148, 152, 176); WT = (238, 238, 244); PK = (240, 160, 176); DG = (108, 112, 138)
    bob = {"idle": [0, -1][f % 2], "jump": -3, "collect": -1}.get(pose, [0, -1, -2, -1][f % 4])
    # curling tail (wags)
    wag = [0, 1, 2, 1][f % 4] if pose != "jump" else -3
    d = ImageDraw.Draw(img)
    tp = [(23, 26 + bob), (27, 24 + bob), (28, 19 + bob + wag), (26, 16 + bob + wag)]
    d.line([(x * SCALE + SCALE / 2, y * SCALE + SCALE / 2) for x, y in tp],
           fill=GY, width=3 * SCALE, joint="curve")
    # paws
    for lx in (10, 13, 18, 21):
        off = ([-1, 1, -1, 1][f % 4] if pose == "run" else 0) * (1 if lx % 2 else -1)
        rect(img, lx + max(-1, min(1, off)), 28 + bob, lx + 2, 30 + bob, WT)
    # body + bib
    ellipse(img, 8, 16 + bob, 24, 30 + bob, GY)
    ellipse(img, 10, 21 + bob, 16, 29 + bob, WT)
    # stripes
    for sx in (18, 21):
        rect(img, sx, 17 + bob, sx, 20 + bob, DG)
    # head + muzzle
    ellipse(img, 6, 6 + bob, 18, 17 + bob, GY)
    ellipse(img, 5, 12 + bob, 11, 16 + bob, WT)
    # triangle ears
    for ex in ((8, 1), (14, 0)):
        d.polygon([(c[0] * SCALE + SCALE / 2, c[1] * SCALE + SCALE / 2) for c in
                   [(ex[0], 7 + bob), (ex[0] + 1, ex[1] + bob), (ex[0] + 4, 5 + bob)]], fill=GY)
    px(img, ex[0] + 1, ex[1] + 2 + bob, PK)
    eye(img, 9, 10 + bob)
    px(img, 6, 13 + bob, PK)                        # nose
    line(img, [(4, 14 + bob), (8, 14 + bob)], DG, 1)  # whisker
    return outline(img)


# ---------------------------------------------------------------------- OWL
def owl(pose="idle", f=0):
    img = blank()
    BR = (150, 108, 74); LT = (214, 178, 130); DK = (96, 64, 44); YE = (250, 200, 80)
    bob = {"idle": [0, -1][f % 2], "jump": -3, "collect": -1}.get(pose, [0, -1, 0, -1][f % 4])
    wing_up = pose in ("jump", "collect") or f % 2 if pose == "run" else False
    # ear tufts
    for ex in (10, 19):
        rect(img, ex, 4 + bob, ex + 2, 7 + bob, BR)
    # body
    ellipse(img, 8, 6 + bob, 23, 29 + bob, BR)
    ellipse(img, 11, 14 + bob, 20, 28 + bob, LT)
    # feather scallops on belly
    for yy in (18, 22, 26):
        for xx in range(12, 20, 3):
            arc_pts = [(xx, yy), (xx + 1, yy + 1), (xx + 2, yy)]
            line(img, arc_pts, DK, 1)
    # big disc eyes
    for exx in (11, 17):
        ellipse(img, exx - 1, 8 + bob, exx + 3, 12 + bob, (250, 246, 238, 255))
        ellipse(img, exx, 9 + bob, exx + 2, 11 + bob, YE)
        px(img, exx + 1, 10 + bob, (30, 24, 28))
    # beak
    d = ImageDraw.Draw(img)
    d.polygon([(c[0] * SCALE + SCALE / 2, c[1] * SCALE + SCALE / 2) for c in
               [(14, 11 + bob), (13, 14 + bob), (16, 14 + bob)]], fill=YE)
    # wings flap
    wy = -5 if wing_up else 2
    ellipse(img, 4, 14 + bob + wy, 8, 24 + bob + wy // 2, DK)
    ellipse(img, 23, 14 + bob + wy, 27, 24 + bob + wy // 2, DK)
    # feet
    rect(img, 12, 29 + bob, 14, 30 + bob, YE); rect(img, 17, 29 + bob, 19, 30 + bob, YE)
    return outline(img)


ANIMALS = {"penguin": penguin, "crab": crab, "bunny": bunny,
           "fox": fox, "cat": cat, "owl": owl}

for name, fn in ANIMALS.items():
    frames = [fn("idle", 0), fn("idle", 1), fn("jump", 0), fn("collect", 0),
              fn("run", 0), fn("run", 1), fn("run", 2), fn("run", 3)]
    sh = Sheet(4, 32, 32, rows=2)
    for fr in frames:
        sh.add(fr)
    canvas = sh.save(os.path.join(CH, f"player_{name}.png"))
    save_scaled(canvas, os.path.join(PREV, f"player_{name}@3x.png"), 3)
    # UI icon: bust crop of the idle frame
    ic = frames[0].resize((32, 32), Image.NEAREST).crop((6, 2, 26, 22)).resize((16, 16), Image.NEAREST)
    base = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    base.paste(ic, (0, 0), ic)
    base.save(os.path.join(UI, f"icon_skin_{name}.png"))
    save_scaled(base, os.path.join(UI, "previews", f"icon_skin_{name}@4x.png"), 4)

print("animals ok")
