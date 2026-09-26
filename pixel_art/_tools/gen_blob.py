"""Blobby jumping green enemy — cuter, rounder cousin of the slime.
Sheet 5x2 @32x32: idle-squish(4) | move-waddle(4) | jump crouch+air(2). Bottom y=30."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/enemies"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)

BODY = (116, 208, 96); HI = (190, 240, 160); DK = (66, 140, 70); EYE = (36, 52, 36)


def blob(w=22, h=18, dy=0, eye_open=True, look=0, blush=True, mouth="smile"):
    img = Image.new("RGBA", (32 * SCALE, 32 * SCALE), (0, 0, 0, 0))
    x0 = 16 - w // 2
    y1 = 30 + dy
    y0 = y1 - h
    # squishy dome with fat rounded bottom
    ellipse(img, x0, y0, x0 + w - 1, y0 + int(h * 1.9), BODY)
    rect(img, x0 + 1, y0 + h - 5, x0 + w - 2, y1, BODY)
    # belly shade + rim light
    ellipse(img, x0 + 3, y0 + 2, x0 + w // 2, y0 + h // 2, HI)
    rect(img, x0 + 2, y1 - 3, x0 + w - 3, y1 - 1, DK)
    # googly eyes (big whites, dark pupils with shine)
    ex = 16 - 5 + look
    ey = y0 + h // 2 - 2
    def eye(x):
        if eye_open:
            ellipse(img, x, ey, x + 3, ey + 4, (255, 255, 255, 255))
            rect(img, x + 1, ey + 2, x + 2, ey + 3, EYE)
            px(img, x + 1, ey + 2, (255, 255, 255, 255))
        else:
            line(img, [(x + 1, ey + 2), (x + 2, ey + 3), (x + 3, ey + 2)], EYE, 1)
    eye(ex); eye(ex + 8)
    if blush:
        px(img, x0 + 2, ey + 4, (240, 150, 150, 200)); px(img, x0 + 3, ey + 4, (240, 150, 150, 160))
        px(img, x0 + w - 3, ey + 4, (240, 150, 150, 200)); px(img, x0 + w - 4, ey + 4, (240, 150, 150, 160))
    cx = 16 - 1
    if mouth == "smile":
        line(img, [(cx - 1, ey + 6), (cx, ey + 7), (cx + 1, ey + 6)], EYE, 1)
    elif mouth == "open":
        ellipse(img, cx - 1, ey + 6, cx + 2, ey + 8, EYE)
    # tiny sprout on head for extra cute
    px(img, 16, y0 - 1, (90, 160, 80, 255)); px(img, 16, y0 - 2, (90, 160, 80, 255))
    px(img, 17, y0 - 3, (120, 200, 110, 255)); px(img, 15, y0 - 2, (150, 215, 120, 255))
    return outline(img)


frames = []
# idle squish breathe (4)
for w, h in ((22, 18), (23, 17), (22, 18), (21, 19)):
    frames.append(blob(w, h))
# waddle move (4): lean + step squash
for i, (w, h, lk) in enumerate([(22, 18, -1), (23, 16, 0), (22, 18, 1), (23, 16, 0)]):
    f = blob(w, h, look=lk, mouth="open" if i % 2 else "smile")
    frames.append(f)
# jump: deep crouch then stretched air pose
frames.append(blob(26, 12, mouth="open"))
frames.append(blob(18, 24, dy=-4, mouth="open"))

sh = Sheet(5, 32, 32, rows=2)
for f in frames:
    sh.add(f)
canvas = sh.save(os.path.join(OUT, "blob_green.png"))
save_scaled(canvas, os.path.join(PREV, "blob_green@3x.png"), 3)
save_scaled(hframes(frames[:4]), os.path.join(PREV, "blob_green_idle@3x.png"), 3)
save_scaled(hframes(frames[4:8]), os.path.join(PREV, "blob_green_move@3x.png"), 3)
save_scaled(hframes(frames[8:]), os.path.join(PREV, "blob_green_jump@3x.png"), 3)
print("blob ok")
