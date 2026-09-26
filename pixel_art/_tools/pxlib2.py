"""pxlib2 - higher-detail pixel drawing toolkit (built on pxlib).

Adds: antialiased edges, soft shading helpers, dithering, highlights/shadows,
and a sub-pixel-accurate ellipse/rounded-rect set. Same SCALE=4 logical grid.
"""
import random
from PIL import Image, ImageDraw, ImageFilter
from pxlib import (SCALE, GRID, new, rect, ellipse, line, px, shade, darker,
                   lighter, outline, noise, flip_h, save, save_scaled, Sheet,
                   hframes)

INK = (38, 26, 50, 255)


def get(img, x, y):
    """logical-pixel read"""
    p = img.getpixel((x * SCALE + SCALE // 2, y * SCALE + SCALE // 2))
    return p


def put(img, x, y, col):
    rect(img, x, y, x, y, col)


def alpha_at(img, x, y):
    return get(img, x, y)[3]


def blend(c1, c2, t):
    """t in 0..1 toward c2"""
    a1 = c1[3] / 255.0
    a2 = c2[3] / 255.0
    o = a2 * t
    if a1 == 0 and o == 0:
        return (0, 0, 0, 0)
    r = int(c1[0] * (1 - o) + c2[0] * o)
    g = int(c1[1] * (1 - o) + c2[1] * o)
    b = int(c1[2] * (1 - o) + c2[2] * o)
    a = int(max(c1[3], c2[3] * t))
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), min(255, a))


def soften_edges(img, edge_col=None, strength=0.5):
    """Antialias silhouette: half-cover pixels along the border of shapes get
    blended toward the outline color, giving rounder-looking sprites."""
    w, h = img.size
    pxs = img.load()
    out = img.copy()
    opx = out.load()
    for yy in range(h):
        for xx in range(w):
            r, g, b, a = pxs[xx, yy]
            if a < 200:
                continue
            # count solid neighbors (subpixel coords)
            solid = 0
            total = 0
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = xx + dx, yy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    na = pxs[nx, ny][3]
                    total += 1
                    if na > 128:
                        solid += 1
            if solid < total:
                ec = edge_col or (30, 22, 44, 255)
                frac = (total - solid) / total * strength
                opx[xx, yy] = blend((r, g, b, a), ec, frac * 0.55)
    return out


def dither(img, x0, y0, x1, y1, col, density=0.5, seed=3):
    rnd = random.Random(seed)
    for yy in range(y0 * SCALE, (y1 + 1) * SCALE):
        for xx in range(x0 * SCALE, (x1 + 1) * SCALE):
            if ((xx // SCALE) + (yy // SCALE)) % 2 == (xx // SCALE) % 2:
                pass
            if rnd.random() < density:
                rect(img, xx // SCALE, yy // SCALE, xx // SCALE, yy // SCALE,
                     shade(col, da=int(255 * rnd.uniform(0.5, 1.0))))


def rrect(img, x0, y0, x1, y1, col, radius=1):
    """Rounded rectangle in logical pixels."""
    ellipse(img, x0, y0, x0 + radius * 2, y0 + radius * 2, col)
    ellipse(img, x1 - radius * 2, y0, x1, y0 + radius * 2, col)
    ellipse(img, x0, y1 - radius * 2, x0 + radius * 2, y1, col)
    ellipse(img, x1 - radius * 2, y1 - radius * 2, x1, y1, col)
    rect(img, x0 + radius, y0, x1 - radius, y1, col)
    rect(img, x0, y0 + radius, x1, y1 - radius, col)


def top_light(img, x0, y0, x1, y1, col, amt=30):
    """1px lighter rim along the top-left of a filled area."""
    base = get(img, x0 * SCALE // SCALE, y0) if False else None
    for xx in range(x0, x1 + 1):
        if alpha_at(img, xx, y0) > 200:
            put(img, xx, y0, lighter(get(img, xx, y0), amt))
    for yy in range(y0 + 1, y1 + 1):
        if alpha_at(img, x0, yy) > 200:
            put(img, x0, yy, lighter(get(img, x0, yy), amt - 8))


def bottom_shade(img, x0, y0, x1, y1, col, amt=34):
    for xx in range(x0, x1 + 1):
        if alpha_at(img, xx, y1) > 200:
            put(img, xx, y1, darker(get(img, xx, y1), amt))
    for yy in range(y0, y1):
        if alpha_at(img, x1, yy) > 200:
            put(img, x1, yy, darker(get(img, x1, yy), amt - 10))


def drop_shadow(img, w_log, h_log, off=(0, 0), radius_scale=1, alpha=70):
    """returns new image with a soft ground shadow appended below sprite."""
    pass


def eye(img, x, y, look=(-1, 0), size=2, white=(250, 250, 252, 255), pupil=INK, sparkle=True):
    """cute big eye: white ball + offset pupil + sparkle pixel"""
    ellipse(img, x, y, x + size - 1, y + size - 1, white)
    px(img, x + (size - 1) // 2 + look[0] // 2, y + (size - 1) // 2 + look[1] // 2, pupil)
    if size >= 3:
        rect(img, x + 1, y + 1, x + size - 2, y + size - 1, pupil)
    if sparkle:
        px(img, x, y, (255, 255, 255, 255))


def blush(img, x, y, col=(244, 130, 130, 150)):
    rect(img, x, y, x + 1, y, col)


def finalize(img, edge=(30, 22, 44, 255)):
    """outline + soften -> crisp-but-round premium look"""
    return soften_edges(outline(img, edge), edge_col=edge, strength=0.6)
