"""Premium hero characters v2 — 48x56 logical cells, richer anatomy:
shaded hood/torso, big sparkly eyes, fingered gloves, laces + soled boots,
straps + coin pouch on backpack, drop shadow. Same frame order as before:
row0 idle0 idle1 jump collect | row1 run0..run3   (faces LEFT)
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *

OUT = "/workspace/pixel_art/characters"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)
SCALE = 4
W, H = 48, 56          # logical canvas per frame


def N():
    return Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))


SKINS = {
    "default": dict(suit=(78, 128, 222), suit_d=(46, 80, 152), suit_l=(120, 168, 244),
                    hood=(100, 150, 238), skin=(244, 199, 160), skin_d=(214, 160, 118),
                    pack=(228, 170, 64), boots=(66, 48, 62), glove=(244, 199, 160),
                    trim=(240, 214, 96), hair=(92, 60, 44)),
    "snow": dict(suit=(232, 240, 250), suit_d=(160, 184, 208), suit_l=(255, 255, 255),
                 hood=(206, 224, 242), skin=(244, 199, 160), skin_d=(214, 160, 118),
                 pack=(96, 150, 196), boots=(74, 88, 112), glove=(226, 236, 248),
                 scarf=(228, 84, 84), trim=(255, 255, 255), hair=(120, 80, 60)),
    "beach": dict(suit=(252, 144, 72), suit_d=(206, 94, 42), suit_l=(255, 186, 120),
                  hood=(255, 204, 96), skin=(204, 138, 96), skin_d=(168, 108, 70),
                  pack=(64, 178, 160), boots=(58, 124, 118), glove=(204, 138, 96),
                  shades=True, trim=(255, 240, 150), hair=(60, 42, 34)),
}


def limb(img, pts, w, col):
    line(img, pts, col, w)


def draw(C, leg_f=0, leg_b=0, arm_f=0, arm_b=0, bob=0, lean=0, jump=False, collect=False):
    img = N()
    y0 = bob
    cx = 24 + lean  # body center x

    # ---------- ground shadow (soft ellipse under feet)
    sh = Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))
    ellipse(sh, 14, 50, 34, 54, (20, 16, 30, 60))
    sh = sh.filter(ImageFilter.BLUR) if hasattr(ImageFilter, "BLUR") else sh
    from PIL import ImageFilter as IF
    sh = sh.filter(IF.GaussianBlur(SCALE // 2))
    img = Image.alpha_composite(img, sh)

    hip_y = 36 + y0
    # ---------- back leg + boot
    limb(img, [(cx - 2, hip_y), (cx - 3 + leg_b, hip_y + 8)], 4, C["suit_d"])
    bx = cx - 6 + leg_b
    rect(img, bx, hip_y + 9, bx + 6, hip_y + 11, C["boots"])
    rect(img, bx, hip_y + 12, bx + 7, hip_y + 13, darker(C["boots"], 45))     # sole
    px(img, bx + 1, hip_y + 9, lighter(C["boots"], 25))
    # ---------- back arm + glove
    ax, ay = cx + 4, 26 + y0
    limb(img, [(ax, ay), (ax + 3 + arm_b, ay + 8)], 4, C["suit_d"])
    ellipse(img, ax + 2 + arm_b, ay + 8, ax + 5 + arm_b, ay + 11, C["glove"])

    # ---------- backpack (behind torso, right side) with coin pouch
    pk_x = cx + 5
    rrect(img, pk_x, 24 + y0, pk_x + 7, 36 + y0, C["pack"], radius=2)
    rect(img, pk_x, 28 + y0, pk_x + 7, 29 + y0, darker(C["pack"], 45))         # flap seam
    rect(img, pk_x + 7, 24 + y0, pk_x + 7, 36 + y0, darker(C["pack"], 60))
    top_light(img, pk_x, 24 + y0, pk_x + 7, 26 + y0, None, 26)
    ellipse(img, pk_x + 2, 31 + y0, pk_x + 4, 33 + y0, (250, 220, 110, 255))   # pouch coin glint
    px(img, pk_x + 2, 31 + y0, (255, 255, 230, 255))

    # ---------- torso (hoodie) with shading + hem
    tx0, ty0, tx1, ty1 = cx - 7, 23 + y0, cx + 5, 37 + y0
    rrect(img, tx0, ty0, tx1, ty1, C["suit"], radius=2)
    bottom_shade(img, tx0, ty0, tx1, ty1, None, 40)
    rect(img, tx0 + 1, ty1 - 3, tx1 - 1, ty1 - 3, C["suit_d"])                 # shorts line
    rect(img, tx0, ty0 + 1, tx0, ty1 - 2, C["suit_l"])                         # rim light left
    # hoodie pocket + drawstrings
    rect(img, cx - 5, 32 + y0, cx + 1, 32 + y0, C["suit_d"])
    px(img, cx - 3, 25 + y0, C["trim"]); px(img, cx - 1, 25 + y0, C["trim"])
    # ---------- front leg + boot
    limb(img, [(cx - 5, hip_y), (cx - 6 + leg_f, hip_y + 8)], 4, C["suit"])
    fx = cx - 10 + leg_f
    rect(img, fx, hip_y + 9, fx + 6, hip_y + 11, C["boots"])
    rect(img, fx, hip_y + 12, fx + 7, hip_y + 13, darker(C["boots"], 45))
    px(img, fx + 1, hip_y + 9, lighter(C["boots"], 30))
    px(img, fx + 2, hip_y + 10, lighter(C["boots"], 12))                       # lace hint

    # ---------- head: hood shell + face
    hx, hy = cx - 12, 8 + y0
    # hood dome
    ellipse(img, hx, hy, hx + 17, hy + 19, C["hood"])
    rect(img, hx, hy + 8, hx + 17, hy + 15, C["hood"])
    # hood fur/shadow inner ring
    arc_inner = darker(C["hood"], 30)
    for xx in range(hx + 2, hx + 16):
        put(img, xx, hy + 18, arc_inner)
    # face patch (looks left)
    rrect(img, hx + 1, hy + 5, hx + 9, hy + 16, C["skin"], radius=2)
    rect(img, hx + 8, hy + 6, hx + 9, hy + 15, C["skin_d"])                    # cheek shade
    # fringe of hair peeking out
    rect(img, hx + 1, hy + 4, hx + 6, hy + 5, C["hair"])
    px(img, hx + 7, hy + 4, C["hair"])
    # ear
    ellipse(img, hx + 9, hy + 9, hx + 11, hy + 12, C["skin"])
    px(img, hx + 10, hy + 10, C["skin_d"])
    # nose in profile
    px(img, hx, hy + 10, C["skin"]); px(img, hx, hy + 11, C["skin"])
    px(img, hx - 1, hy + 11, C["skin_d"])
    if C.get("shades"):
        rect(img, hx - 1, hy + 8, hx + 6, hy + 11, (34, 32, 44, 255))
        rect(img, hx - 1, hy + 8, hx + 1, hy + 9, (96, 140, 190, 255))         # reflection
        rect(img, hx + 6, hy + 9, hx + 9, hy + 10, (34, 32, 44, 255))          # temple arm
    else:
        eye(img, hx + 1, hy + 8, look=(-1, 0), size=4)                          # big sparkly eye
        # brow + smile
        rect(img, hx + 1, hy + 7, hx + 3, hy + 7, C["hair"])
        px(img, hx, hy + 13, (176, 96, 84, 255))
        px(img, hx + 1, hy + 14, (176, 96, 84, 255))
        blush(img, hx + 3, hy + 12, (244, 140, 130, 120))
    if C.get("scarf"):
        rrect(img, hx + 1, hy + 15, hx + 14, hy + 18, C["scarf"], radius=1)
        rect(img, hx + 10, hy + 18, hx + 14, hy + 24, C["scarf"])              # hanging tail
        rect(img, hx + 11, hy + 18, hx + 11, hy + 24, darker(C["scarf"], 40))
        for i in range(0, 5):
            px(img, hx + 10 + i, hy + 24, lighter(C["scarf"], 30))             # fringe
    # hood back-high over head
    rect(img, hx + 8, hy, hx + 16, hy + 3, darker(C["hood"], 18))

    # ---------- front arm + glove (raised when collecting)
    fax, fay = cx - 4, 26 + y0
    if collect:
        limb(img, [(fax, fay), (fax - 7, fay - 6)], 4, C["suit"])
        ellipse(img, fax - 11, fay - 11, fax - 7, fay - 7, C["glove"])
        px(img, fax - 11, fay - 12, C["glove"])                                 # pointing finger
        # wrist cuff
        px(img, fax - 8, fay - 8, C["suit_d"])
    else:
        limb(img, [(fax, fay), (fax - 2 + arm_f, fay + 8)], 4, C["suit"])
        ellipse(img, fax - 5 + arm_f, fay + 8, fax - 2 + arm_f, fay + 11, C["glove"])
        top_light(img, fax - 5 + arm_f, fay + 8, fax - 2 + arm_f, fay + 9, None, 22)
    return img


def sprite(args, skin):
    c = SKINS[skin]
    img = draw(c, **args)
    img = finalize(img, (34, 24, 48, 255))
    return img


ANIMS = {
    "idle": [dict(bob=0), dict(bob=1)],
    "run": [dict(leg_f=-4, leg_b=4, arm_f=3, arm_b=-3, bob=0, lean=2),
            dict(leg_f=0, leg_b=0, arm_f=0, arm_b=0, bob=-2, lean=1),
            dict(leg_f=4, leg_b=-4, arm_f=-3, arm_b=3, bob=0, lean=2),
            dict(leg_f=0, leg_b=0, arm_f=1, arm_b=-1, bob=-2, lean=1)],
    "jump": [dict(leg_f=-3, leg_b=3, arm_f=-4, arm_b=3, bob=-2, lean=1, jump=True)],
    "collect": [dict(collect=True, lean=1)],
}
ORDER = [("idle", 0), ("idle", 1), ("jump", 0), ("collect", 0),
         ("run", 0), ("run", 1), ("run", 2), ("run", 3)]

for skin in SKINS:
    sheet = Sheet(4, W, H, rows=2)
    prev = []
    for anim, idx in ORDER:
        fr = sprite(ANIMS[anim][idx], skin)
        sheet.add(fr)
        prev.append(fr)
    sheet.save(os.path.join(OUT, f"hero_{skin}.png"))
    save_scaled(hframes(prev[:4]), os.path.join(PREV, f"hero_{skin}_idle_jump_collect@3x.png"), 3)
    save_scaled(hframes(prev[4:]), os.path.join(PREV, f"hero_{skin}_run@3x.png"), 3)
print("heroes ok:", ", ".join(SKINS))
