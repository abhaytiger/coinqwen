"""Back-view (walk-away) animation sheets for enemies — same 5x2 @32x32 grid as
the front sheets: row0 = idle-squish(4) + move(1), row1 = move(4) + squash(2).
Blob/slime seen from behind: no face, just body, eyes peeking at the silhouette
edge, and a rear highlight.  Faces LEFT in 'move' frames like the fronts.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *

OUT = "/workspace/pixel_art/enemies"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)
Wp, Hp = 32, 32          # logical cell


def N():
    return Image.new("RGBA", (Wp * SCALE, Hp * SCALE), (0, 0, 0, 0))


def blob_body(img, col, col_d, col_l, sq, wide=False):
    """sq = vertical squish factor offset; draws rear-view jelly blob."""
    cx, base = 16, 27
    w = int(11 + sq * 0.6)
    h = int(11 - sq)
    ellipse(img, cx - w, base - 2 * h, cx + w, base, col)
    rect(img, cx - w, base - h, cx + w, base, col)
    rrect(img, cx - w + 1, base - 2 * h - 2, cx + w - 1, base - 4, col, radius=4)
    bottom_shade(img, cx - w, base - 2 * h, cx + w, base, None, 42)
    top_light(img, cx - w + 2, base - 2 * h, cx + w - 2, base - h, None, 30)
    # rear glossy highlight (jelly sheen)
    ellipse(img, cx - 5, base - 2 * h + 2, cx + 1, base - h, lighter(col, 45, 190))
    if wide:                                              # little butt dimples
        px(img, int(cx - 4), base - 3, col_d); px(img, int(cx + 4), base - 3, col_d)


def make_blob(name, col, col_d, col_l, eye_col, extra=None, sprout=False, blush_col=None):
    """Builds back sheet; `extra(img, phase)` adds character bits (ember glow, ice caps)."""
    frames = []
    # idle squish cycle (breathing)
    for i, sq in enumerate((0, -1, 0, 1)):
        img = N()
        blob_body(img, col, col_d, col_l, sq, wide=(i == 3))
        if sprout:                                        # leaf/antenna from behind
            line(img, [(16, 8 - sq), (16, 4 - sq)], (90, 140, 80, 255), 2)
            ellipse(img, 13, 1, 19, 5, (120, 190, 100, 255))
        if extra:
            extra(img, i)
        frames.append(finalize(img, (34, 24, 48, 255)))
    # move frames: hop side to side (waddle from behind), eyes peek at rim
    for i, ph in enumerate((-2, -1, 1, 2)):
        img = N()
        sq = 1 if abs(ph) == 2 else -1
        blob_body(img, col, col_d, col_l, sq)
        lean = ph
        # eyes peeking around the left silhouette edge (just two white slits)
        ex = 6 + lean
        ellipse(img, ex, 15, ex + 3, 18, (250, 250, 252, 255))
        px(img, ex, 16, eye_col); px(img, ex + 1, 16, eye_col)
        ex2 = 24 + lean
        ellipse(img, ex2, 15, ex2 + 3, 18, (250, 250, 252, 255))
        px(img, ex2 + 2, 16, eye_col); px(img, ex2 + 1, 16, eye_col)
        if sprout:
            line(img, [(16 + lean // 2, 8 - sq), (16 + lean, 4 - sq)], (90, 140, 80, 255), 2)
            ellipse(img, 13 + lean, 1, 19 + lean, 5, (120, 190, 100, 255))
        if extra:
            extra(img, 4 + i)
        frames.append(finalize(img, (34, 24, 48, 255)))
    # squash hit (flattened, from behind)
    for i, sq in enumerate((-3, -4)):
        img = N()
        blob_body(img, col, col_d, col_l, sq, wide=True)
        if extra:
            extra(img, 8 + i)
        frames.append(finalize(img, (34, 24, 48, 255)))

    sheet = Sheet(5, Wp, Hp, rows=2)
    for f in frames:
        sheet.add(f.resize((Wp, Hp), Image.NEAREST))
    sheet.canvas.save(os.path.join(OUT, f"{name}_back.png"))
    save_scaled(hframes(frames[4:8]), os.path.join(PREV, f"{name}_back_move@3x.png"), 3)
    print("back ok:", name)


# palettes matching the front sheets
make_blob("blob_green", (108, 200, 96, 255), (60, 130, 60, 255), (170, 232, 150, 255),
          INK, sprout=True, )
make_blob("slime_green", (96, 190, 110, 255), (50, 128, 74, 255), (158, 226, 168, 255), INK)
make_blob("slime_snow", (176, 224, 246, 255), (110, 160, 196, 255), (236, 250, 255, 255),
          (60, 90, 130, 255),
          extra=lambda img, p: [ellipse(img, 12, 6, 20, 12, (255, 255, 255, 210)),
                                px(img, 14 + (p % 3), 9, (200, 230, 250, 255))] if p < 4 else None)
make_blob("slime_lava", (214, 92, 54, 255), (140, 44, 34, 255), (255, 170, 90, 255),
          (255, 240, 120, 255),
          extra=lambda img, p: [px(img, x, y, (255, 210, 90, 230))
                                for x, y in ((11, 18), (20, 21), (16, 15), (23, 17))][:3])
