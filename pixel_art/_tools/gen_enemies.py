"""Slimes (green/snow/lava): idle-squish(4), move(4), squash-hit(2). 32x32, bottom y=29."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/enemies"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)

SLIMES = {
    "green": dict(body=(108, 196, 88), hi=(178, 235, 150), dk=(60, 130, 60),
                  eye=(30, 40, 30), mouth=True),
    "snow":  dict(body=(176, 220, 248), hi=(235, 250, 255), dk=(110, 160, 200),
                  eye=(30, 45, 70), icicle=True),
    "lava":  dict(body=(232, 96, 48), hi=(255, 190, 90), dk=(150, 40, 30),
                  eye=(60, 16, 10), ember=True),
}


def slime(C, w=20, h=16, dy=0, eye_open=True, look=0):
    """w/h = body size, dy = vertical offset of whole body (feet stay if dy<0 handled by caller)."""
    img = new()
    x0 = 16 - w // 2
    y1 = 29 + dy                      # bottom
    y0 = y1 - h                       # top
    # dome body: rounded top, flat bottom
    ellipse(img, x0, y0, x0 + w - 1, y0 + h * 2 - 1, C["body"])
    rect(img, x0, y0 + h - 4, x0 + w - 1, y1, C["body"])   # fill lower half
    # clear anything below baseline
    for yy in range(y1 + 1, 32):
        for xx in range(32):
            pass
    # shading: rim light left-top, dark bottom-right band
    ellipse(img, x0 + 2, y0 + 2, x0 + w // 2 - 1, y0 + h // 2, C["hi"])
    d = ImageDraw.Draw(img)
    # darker bottom strip with slight curve
    rect(img, x0 + 1, y1 - 3, x0 + w - 2, y1 - 1, C["dk"])
    px(img, x0, y1 - 1, C["dk"]); px(img, x0 + w - 1, y1 - 1, C["dk"])
    # eyes
    ex = 16 - 4 + look; 
    ey = y0 + h // 2 - 1
    def eye(x):
        if eye_open:
            rect(img, x, ey, x + 2, ey + 3, (255, 255, 255, 255))
            rect(img, x, ey + 1, x + 1, ey + 3, C["eye"])
            px(img, x, ey, C["eye"])
        else:
            line(img, [(x, ey + 2), (x + 2, ey + 2)], C["eye"], 1)
    eye(ex); eye(ex + 7)
    if C.get("mouth"):
        rect(img, ex + 3, ey + 5, ex + 4, ey + 5, C["eye"])
    if C.get("icicle"):
        px(img, x0 + 3, y0 - 1, (210, 240, 255, 255)); px(img, x0 + 3, y0, (210, 240, 255, 255))
        px(img, x0 + 4, y0, (160, 205, 235, 255))
    if C.get("ember"):
        rnd = random.Random(w + h)
        for i in range(4):
            px(img, x0 + 2 + rnd.randrange(w - 4), y0 + 1 + rnd.randrange(3), (255, 220, 120, 255))
    return img


def crop_bottom(img):
    """erase pixels below logical y=29 to keep baseline clean"""
    small = img.resize((32, 32), Image.NEAREST).convert("RGBA")
    for y in range(30, 32):
        for x in range(32):
            small.putpixel((x, y), (0, 0, 0, 0))
    return small.resize((128, 128), Image.NEAREST)


ANIM = {
    "idle": [dict(w=20, h=16), dict(w=19, h=14), dict(w=18, h=13), dict(w=19, h=15)],
    "move": [dict(w=21, h=15, look=-1), dict(w=19, h=16, look=-1),
             dict(w=21, h=15, look=0), dict(w=19, h=16, look=0)],
    "hit": [dict(w=24, h=7, eye_open=False), dict(w=22, h=5, eye_open=False)],
}

for name, C in SLIMES.items():
    frames = []
    order = [("idle", 0), ("idle", 1), ("idle", 2), ("idle", 3),
             ("move", 0), ("move", 1), ("move", 2), ("move", 3),
             ("hit", 0), ("hit", 1)]
    for anim, idx in order:
        fr = crop_bottom(outline(slime(C, **ANIM[anim][idx]), (28, 22, 34, 255)))
        frames.append(fr)
    sh = Sheet(5, 32, 32, rows=2)
    for f in frames:
        sh.add(f)
    sh.save(os.path.join(OUT, f"slime_{name}.png"))
    save_scaled(hframes(frames[:4]), os.path.join(PREV, f"slime_{name}_idle@3x.png"), 3)
    save_scaled(hframes(frames[4:8]), os.path.join(PREV, f"slime_{name}_move@3x.png"), 3)
    save_scaled(hframes(frames[8:]), os.path.join(PREV, f"slime_{name}_hit@3x.png"), 3)
print("enemies ok")
