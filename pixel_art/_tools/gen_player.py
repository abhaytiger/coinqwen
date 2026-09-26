"""Procedural player character: idle(2) + run(4) + jump + collect pose, 3 skins.
Faces LEFT (Godot flips with scale.x = -1)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/characters"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)

INK = (38, 28, 52, 255)

SKINS = {
    "default": dict(suit=(76, 122, 214), suit_d=(48, 82, 150), hood=(98, 148, 235),
                    skin=(241, 194, 154), pack=(224, 166, 62), boots=(62, 46, 58)),
    "snow": dict(suit=(228, 238, 248), suit_d=(168, 188, 208), hood=(200, 220, 238),
                 skin=(241, 194, 154), pack=(94, 148, 190), boots=(74, 88, 110),
                 scarf=(226, 84, 84)),
    "beach": dict(suit=(250, 140, 70), suit_d=(208, 96, 44), hood=(255, 200, 92),
                  skin=(198, 132, 92), pack=(64, 176, 158), boots=(58, 122, 116),
                  shades=True),
}


def draw_body(C, leg_f=0, leg_b=0, arm_f=0, arm_b=0, bob=0, lean=0):
    img = new()
    y0 = bob
    # --- back arm (behind body, to the right side)
    bx, by = 21 + lean, 14 + y0
    line(img, [(bx, by), (bx + 2 + arm_b, by + 5)], C["suit_d"], 3)
    rect(img, bx + 1 + arm_b, by + 5, bx + 2 + arm_b, by + 6, C["skin"])
    # --- legs (feet land on y=28)
    hip_y = 21 + y0
    line(img, [(18, hip_y), (19 + leg_b, 26)], C["suit_d"], 3)
    rect(img, 17 + leg_b, 27, 20 + leg_b, 28, C["boots"])
    line(img, [(14, hip_y), (13 + leg_f, 26)], C["suit"], 3)
    rect(img, 11 + leg_f, 27, 14 + leg_f, 28, C["boots"])
    # --- backpack (right/back side)
    rect(img, 21 + lean // 2, 13 + y0, 24 + lean // 2, 19 + y0, C["pack"])
    rect(img, 21 + lean // 2, 15 + y0, 24 + lean // 2, 15 + y0, darker(C["pack"], 40))
    rect(img, 24 + lean // 2, 13 + y0, 24 + lean // 2, 19 + y0, darker(C["pack"], 60))
    # --- torso
    rect(img, 11 + lean, 12 + y0, 20 + lean, 22 + y0, C["suit"])
    rect(img, 11 + lean, 20 + y0, 20 + lean, 22 + y0, C["suit_d"])            # shorts
    rect(img, 11 + lean, 12 + y0, 12 + lean, 22 + y0, lighter(C["suit"], 20))  # rim light
    px(img, 15 + lean, 20 + y0, (240, 214, 96, 255))                          # buckle
    # --- head (hood), face looks left
    hx, hy = 10 + lean, 4 + y0
    rect(img, hx, hy + 1, hx + 9, hy + 8, C["hood"])
    rect(img, hx + 1, hy, hx + 8, hy + 1, C["hood"])
    rect(img, hx + 1, hy + 9, hx + 8, hy + 9, C["hood"])
    rect(img, hx, hy + 3, hx + 4, hy + 8, C["skin"])                          # face
    px(img, hx - 1, hy + 4, C["skin"]); px(img, hx - 1, hy + 5, C["skin"])    # nose
    if C.get("shades"):
        rect(img, hx - 1, hy + 4, hx + 3, hy + 5, (30, 30, 38, 255))
        px(img, hx + 1, hy + 4, (110, 150, 190, 255))
    else:
        px(img, hx + 1, hy + 5, INK)                                          # eye
        px(img, hx + 2, hy + 5, INK)
    rect(img, hx + 4, hy + 3, hx + 4, hy + 8, darker(C["skin"], 30))          # face shadow
    rect(img, hx + 9, hy + 1, hx + 9, hy + 8, C["suit_d"])                    # hood back shade
    if C.get("scarf"):
        rect(img, hx + 1, hy + 9, hx + 8, hy + 10, C["scarf"])
        rect(img, hx + 6, hy + 11, hx + 8, hy + 13, C["scarf"])               # tail flapping back
    # --- front arm
    fx, fy = 15 + lean, 14 + y0
    line(img, [(fx, fy), (fx - 1 + arm_f, fy + 5)], C["suit"], 3)
    rect(img, fx - 2 + arm_f, fy + 5, fx - 1 + arm_f, fy + 6, C["skin"])
    return img


def sprite(args, skin):
    c = dict(SKINS[skin])
    return outline(draw_body(c, **args), (30, 22, 44, 255))


ANIMS = {
    "idle": [dict(bob=0), dict(bob=1)],
    "run": [dict(leg_f=-3, leg_b=3, arm_f=2, arm_b=-2, bob=0, lean=1),
            dict(leg_f=0, leg_b=0, arm_f=0, arm_b=0, bob=-1, lean=0),
            dict(leg_f=3, leg_b=-3, arm_f=-2, arm_b=2, bob=0, lean=1),
            dict(leg_f=0, leg_b=0, arm_f=1, arm_b=-1, bob=-1, lean=0)],
    "jump": [dict(leg_f=-2, leg_b=2, arm_f=-2, arm_b=2, bob=-1, lean=0)],
    "collect": [dict(leg_f=0, leg_b=0, arm_f=-4, arm_b=2, bob=0, lean=1)],
}

ORDER = [("idle", 0), ("idle", 1), ("jump", 0), ("collect", 0),
         ("run", 0), ("run", 1), ("run", 2), ("run", 3)]

for skin in SKINS:
    sheet = Sheet(4, 32, 32, rows=2)
    prev = []
    for anim, idx in ORDER:
        fr = sprite(ANIMS[anim][idx], skin)
        sheet.add(fr)
        prev.append(fr)
    sheet.save(os.path.join(OUT, f"player_{skin}.png"))
    save_scaled(hframes(prev[:4]), os.path.join(PREV, f"player_{skin}_idle_jump_collect@4x.png"), 4)
    save_scaled(hframes(prev[4:]), os.path.join(PREV, f"player_{skin}_run@4x.png"), 4)
print("player ok")
