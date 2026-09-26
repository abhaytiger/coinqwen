"""pxlib - tiny pixel-art drawing library for procedural sprite generation.

All sprites are drawn on a logical 32x32 (or custom) grid at SUBPIXEL resolution,
then downsampled with NEAREST to get crisp, chunky pixels.
"""
import random
from PIL import Image, ImageDraw

SCALE = 4            # subpixel factor: each logical pixel = SCALE x SCALE real px
GRID = 32            # default logical grid size


# ---------------------------------------------------------------- primitives
def new(gw=GRID, gh=GRID):
    return Image.new("RGBA", (gw * SCALE, gh * SCALE), (0, 0, 0, 0))


def rect(img, x0, y0, x1, y1, col):
    d = ImageDraw.Draw(img)
    d.rectangle([x0 * SCALE, y0 * SCALE, (x1 + 1) * SCALE - 1, (y1 + 1) * SCALE - 1], fill=col)


def ellipse(img, x0, y0, x1, y1, col):
    """Filled ellipse inside the logical box (x0,y0)-(x1,y1)."""
    d = ImageDraw.Draw(img)
    d.ellipse([x0 * SCALE, y0 * SCALE, (x1 + 1) * SCALE - 1, (y1 + 1) * SCALE - 1], fill=col)


def line(img, pts, col, w=1):
    d = ImageDraw.Draw(img)
    sp = [(p[0] * SCALE + SCALE / 2, p[1] * SCALE + SCALE / 2) for p in pts]
    d.line(sp, fill=col, width=w * SCALE, joint="curve")


def px(img, x, y, col):
    if 0 <= x < img.width // SCALE and 0 <= y < img.height // SCALE:
        rect(img, x, y, x, y, col)


def shade(col, dl=0, dr=0, dg=0, db=0, da=None):
    r, g, b = col[0], col[1], col[2]
    a = col[3] if len(col) > 3 else 255
    if da is not None:
        a = da
    cl = lambda v: max(0, min(255, int(v)))
    return (cl(r + dr), cl(g + dg), cl(b + db), a)


def darker(col, amt=30, alpha=None):
    f = 1 - amt / 255.0
    a = col[3] if len(col) > 3 else 255
    return (int(col[0] * f), int(col[1] * f), int(col[2] * f), a if alpha is None else alpha)


def lighter(col, amt=40, alpha=None):
    a = col[3] if len(col) > 3 else 255
    return (min(255, col[0] + amt), min(255, col[1] + amt), min(255, col[2] + amt),
            a if alpha is None else alpha)


def outline(img, col=(24, 16, 32, 255)):
    """Add a 1-logical-pixel outline around existing opaque pixels."""
    w, h = img.size
    out = Image.new("RGBA", (w + 2 * SCALE, h + 2 * SCALE), (0, 0, 0, 0))
    mask = img.split()[3].point(lambda v: 255 if v > 40 else 0)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        shifted = Image.new("L", mask.size, 0)
        shifted.paste(mask, (dx * SCALE, dy * SCALE))
        out_mask = Image.new("L", out.size, 0)
        out_mask.paste(shifted, (SCALE, SCALE))
        solid = Image.new("RGBA", out.size, col)
        out = Image.composite(solid, out, out_mask)
    out.paste(img, (SCALE, SCALE), img)
    return out.crop((SCALE, SCALE, SCALE + w, SCALE + h))


def noise(img, x0, y0, x1, y1, cols, density=0.35, seed=7):
    rnd = random.Random(seed)
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            if rnd.random() < density:
                px(img, xx, yy, rnd.choice(cols))


def flip_h(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def save(img, path, factor=1):
    small = img.resize((img.width // SCALE, img.height // SCALE), Image.NEAREST)
    if factor != 1:
        small = small.resize((small.width * factor, small.height * factor), Image.NEAREST)
    small.save(path)
    return small


def save_scaled(img, path, factor=4):
    small = img.resize((img.width // SCALE, img.height // SCALE), Image.NEAREST)
    small.resize((small.width * factor, small.height * factor), Image.NEAREST).save(path)
    return small


# ------------------------------------------------------------- sprite sheets
class Sheet:
    """Grid sheet builder: place finished sprites into cells of a big canvas."""

    def __init__(self, cols, cell_w=32, cell_h=32, rows=1):
        self.cols = cols
        self.cw = cell_w
        self.ch = cell_h
        self.rows = rows
        self.n = 0
        self.canvas = Image.new("RGBA", (cols * cell_w, rows * cell_h), (0, 0, 0, 0))

    def add(self, sprite):
        s = sprite.resize((sprite.width // SCALE, sprite.height // SCALE), Image.NEAREST)
        x = (self.n % self.cols) * self.cw
        y = (self.n // self.cols) * self.ch
        self.canvas.paste(s, (x, y), s)
        self.n += 1
        if self.n > self.cols * self.rows:
            raise ValueError("sheet full")
        return self

    def save(self, path):
        self.canvas.save(path)
        return self.canvas


def hframes(frames, gap=2):
    """Join frames horizontally into one RGBA strip (for @3x preview PNGs)."""
    smalls = [f.resize((f.width // SCALE, f.height // SCALE), Image.NEAREST) for f in frames]
    w = sum(s.width for s in smalls) + gap * (len(smalls) - 1)
    h = max(s.height for s in smalls)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for s in smalls:
        out.paste(s, (x, 0), s)
        x += s.width + gap
    return out
