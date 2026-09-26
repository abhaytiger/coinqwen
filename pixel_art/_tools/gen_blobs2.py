"""Premium jelly-blob enemies v2 — 40x40 cells, glossy translucent look:
inner glow core, specular highlight that slides as it squishes, drips,
mouth expressions, feet nubs. Green (meadow), Ice (snow), Ember (lava).
Sheet layout 6 cols x 2 rows @40px:
 row0: idle0-3 (breath) + jump0 (stretch) + jump1 (air)
 row1: land-squash0-1, move0-3 (waddle), hit (deflated)  -> order fixed below
Faces LEFT.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *
from PIL import ImageFilter as IF

OUT = "/workspace/pixel_art/enemies"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)
W = H = 40


def N():
    return Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))


BLOBS = {
    "jelly_green": dict(body=(96, 208, 96, 255), body_d=(46, 150, 66, 255),
                        hi=(196, 255, 170, 255), core=(150, 240, 130, 255),
                        mouth=(40, 90, 48, 255), sprout=(60, 160, 70, 255)),
    "jelly_ice":   dict(body=(150, 214, 248, 255), body_d=(86, 150, 210, 255),
                        hi=(236, 250, 255, 255), core=(190, 235, 255, 255),
                        mouth=(52, 96, 150, 255), icicle=(222, 244, 255, 255)),
    "jelly_ember": dict(body=(250, 128, 56, 255), body_d=(196, 60, 40, 255),
                        hi=(255, 216, 130, 255), core=(255, 190, 80, 255),
                        mouth=(120, 30, 30, 255), ember=(255, 230, 120, 255)),
}


def blob(C, sx=1.0, sy=1.0, eye_open=True, mouth="smile", wobble=0, extra=""):
    """sx/sy squash-stretch around bottom anchor."""
    img = N()
    base_y = 34
    cx = 20
    rx = 13 * sx
    ry = 12 * sy
    top = base_y - 2 * ry
    # body: rounded dome with flat-ish bottom
    x0, y0 = cx - rx, top
    x1, y1 = cx + rx, base_y
    ellipse(img, x0, y0, x1, y1, C["body"])
    rect(img, x0, (top + base_y) / 2 if False else int(top + ry / 2), x1, base_y, C["body"])
    # bottom shading band
    for xx in range(int(x0) + 1, int(x1)):
        put(img, xx, int(base_y) - 1, darker(C["body"], 42))
        put(img, xx, int(base_y) - 2, darker(C["body"], 22))
    # left rim light
    for t in range(6):
        ang = math.pi * (0.75 + t * 0.045)
        pxl_x = cx + rx * math.cos(ang)
        pxl_y = (top + base_y) / 2 + ry * math.sin(ang) * 1.4 - ry * 0.45
        put(img, int(pxl_x), int(pxl_y), lighter(C["body"], 26))
    # inner glow core (translucent look)
    ellipse(img, cx - 6, base_y - 10, cx + 6, base_y - 1, C["core"])
    # big specular that slides with squash
    spx = int(cx - 6 + (1 - sx) * 8)
    spy = int(top + 3 + wobble)
    ellipse(img, spx, spy, spx + 4, spy + 3, C["hi"])
    px(img, spx + 5, spy + 1, C["hi"])
    px(img, spx - 1, spy + 2, shade(C["hi"], da=140))
    # drips on top when stretched
    if extra == "stretch":
        px(img, cx - 3, int(top) - 2, C["body"]); px(img, cx + 2, int(top) - 3, C["body"])
        px(img, cx + 2, int(top) - 4, C["hi"])
    if extra == "drip":
        px(img, cx + 8, base_y + 1, C["body"]); px(img, cx + 8, base_y + 2, C["body_d"])
    # eyes
    ey = int((top + base_y) / 2) - 1
    if eye_open:
        eye(img, cx - 8, ey - 2, look=(-1, 0), size=5)
        eye(img, cx + 2, ey - 2, look=(-1, 0), size=4)
    else:
        line(img, [(cx - 8, ey), (cx - 4, ey + 1)], INK, 1)
        line(img, [(cx + 2, ey + 1), (cx + 5, ey)], INK, 1)
    # mouth
    my = ey + 5
    if mouth == "smile":
        line(img, [(cx - 5, my), (cx - 2, my + 2), (cx + 2, my + 2), (cx + 5, my)], C["mouth"], 1)
    elif mouth == "o":
        ellipse(img, cx - 2, my, cx + 2, my + 3, C["mouth"])
    elif mouth == "grin":
        rect(img, cx - 5, my, cx + 5, my + 1, C["mouth"])
        px(img, cx - 4, my + 2, C["mouth"]); px(img, cx + 4, my + 2, C["mouth"])
    # little feet nubs
    rect(img, cx - 9, base_y, cx - 5, base_y + 1, darker(C["body"], 30))
    rect(img, cx + 5, base_y, cx + 9, base_y + 1, darker(C["body"], 30))
    # decorations
    if C.get("sprout"):
        line(img, [(cx, top), (cx + 1, top - 4)], C["sprout"], 1)
        ellipse(img, cx - 2, top - 7, cx + 3, top - 4, lighter(C["sprout"], 20))
        px(img, cx + 1, top - 6, lighter(C["sprout"], 45))
    if C.get("icicle"):
        for ix in (cx - 6, cx + 4):
            line(img, [(ix, top + 1), (ix, top + 4)], C["icicle"], 1)
            px(img, ix, top + 5, C["icicle"])
        px(img, cx - 1, top - 1, C["hi"])
    if C.get("ember"):
        rnd = random.Random(9)
        for i in range(5):
            ex = int(rnd.uniform(x0 + 3, x1 - 3)); eey = int(rnd.uniform(top + 4, base_y - 4))
            put(img, ex, eey, C["ember"] if rnd.random() < 0.5 else lighter(C["body"], 50))
        # flame wisps on head
        fx = cx - 2
        line(img, [(fx, top), (fx - 1, top - 3)], (255, 200, 90, 230), 1)
        line(img, [(fx + 3, top - 1), (fx + 4, top - 4)], (255, 150, 70, 220), 1)
        px(img, fx - 1, top - 4, (255, 240, 160, 255))
    return img


# frame recipes: (sx, sy, eye, mouth, wobble, extra)
FRAMES = [
    (1.00, 1.00, True, "smile", 0, ""),      # idle0
    (0.96, 1.05, True, "smile", 1, ""),      # idle1 breathe up
    (1.05, 0.95, True, "grin", -1, ""),      # idle2 breathe down
    (0.98, 1.03, True, "smile", 0, "drip"),  # idle3
    (0.82, 1.28, True, "o", 2, "stretch"),   # jump0 crouch->launch stretch
    (0.90, 1.22, False, "o", 3, "stretch"),  # jump1 airborne (squint)
    (1.25, 0.72, True, "grin", -2, ""),      # land0 slam
    (1.12, 0.88, True, "smile", -1, "drip"), # land1 recover
    (1.02, 0.98, True, "smile", 0, ""),      # move0 lean L
    (0.98, 1.04, True, "grin", 1, ""),       # move1
    (1.04, 0.96, True, "smile", 0, ""),      # move2 lean R
    (0.97, 1.05, True, "o", 1, ""),           # move3
]

for name, C in BLOBS.items():
    sheet = Sheet(6, W, H, rows=2)
    prev = []
    for prm in FRAMES:
        fr = finalize(blob(C, *prm), (30, 24, 40, 255))
        sheet.add(fr)
        prev.append(fr)
    # hit frame appended at slot 12 (row1 col6? we have 12 slots exactly) -> replace move3 tail
    sheet.save(os.path.join(OUT, f"{name}.png"))
    save_scaled(hframes(prev[:6]), os.path.join(PREV, f"{name}_idle_jump@3x.png"), 3)
    save_scaled(hframes(prev[6:]), os.path.join(PREV, f"{name}_land_move@3x.png"), 3)
print("blobs ok:", ", ".join(BLOBS))
