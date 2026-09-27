"""TRUE-HD GOLD COINS — physically-styled rotating bullion coins.

Rendered at 8x supersample with numpy (fBm brushed-metal micro texture,
gold-tinted environment reflections, anisotropic rim reeding = milled edge
teeth, double raised rims, beaded border, embossed emblem w/ two-tone
sculpt + AO, travelling specular glints + bloom during the spin).

Outputs
  coins/hd/<style>_fN.png        256px HD frames (10-frame spin)
  coins/hd/<style>_mega_fN.png   384px HD milestone coin frames
  coins/gold_*.png               logical 32px sheets (8 frames, NEAREST-safe)
  coins/gold_mega.png            logical 48px sheet (10 frames)
  ui/icon_coin.png               16px HUD icon (face-on, crisp)
  coins/previews/*               strips + a big beauty render
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageFilter

ROOT = "/workspace/pixel_art"
OUT = os.path.join(ROOT, "coins")
HD = os.path.join(OUT, "hd")
PREV = os.path.join(OUT, "previews")
for d in (OUT, HD, PREV):
    os.makedirs(d, exist_ok=True)


def vn(seed, size):
    rnd = np.random.RandomState(seed)
    acc = np.zeros((size, size)); amp = 1.0; tot = 0.0; cell = 3
    for o in range(6):
        n = min(size, cell)
        g = rnd.rand(n + 1, n + 1) * 2 - 1
        ys = np.linspace(0, n - 1 + 0.999, size); xs = np.linspace(0, n - 1 + 0.999, size)
        y0 = ys.astype(int); x0 = xs.astype(int); fy = ys - y0; fx = xs - x0
        def at(dy, dx):
            return g[np.clip(y0 + dy, 0, n)[:, None], np.clip(x0 + dx, 0, n)[None, :]]
        top = at(0, 0) * (1 - fx[:, None]) + at(0, 1) * fx[:, None]
        bot = at(1, 0) * (1 - fx[:, None]) + at(1, 1) * fx[:, None]
        acc += (top * (1 - fy[:, None]) + bot * fy[:, None]) * amp
        tot += amp; amp *= 0.5; cell = min(size, cell * 2 + 3)
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-9)


def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a * (1 - t) + b * t


STYLES = {
    "classic": dict(base=(252, 206, 74), hi=(255, 246, 178), lo=(198, 132, 30),
                    edge=(150, 88, 16), glow=(255, 230, 140), emblem="star"),
    "snow":    dict(base=(226, 240, 252), hi=(255, 255, 255), lo=(146, 180, 216),
                    edge=(96, 128, 168), glow=(220, 244, 255), emblem="flake"),
    "beach":   dict(base=(255, 194, 96), hi=(255, 246, 196), lo=(208, 128, 44),
                    edge=(158, 88, 24), glow=(255, 226, 150), emblem="sun"),
}


def emblem_h(u, v, kind, rot=0.0):
    """height field in [0,1] on face disc coords u,v in [-1,1]"""
    c, s = math.cos(rot), math.sin(rot)
    x = u * c - v * s; y = u * s + v * c
    r = math.hypot(x, y); ang = math.atan2(y, x)
    if kind == "star":
        k = 5
        bound = 0.30 + 0.24 * max(0, math.cos(ang * k)) ** 1.6
        h = ss(bound + 0.03, bound - 0.03, r)
        # inner relief
        h = max(h, 0.35 * ss(0.16 + 0.1 * max(0, math.cos(ang * k)) ** 2, 0.0, r))
        return min(1, h)
    if kind == "flake":
        h = 0.0
        for k in range(6):
            a = k * math.pi / 3
            px_, py_ = x * math.cos(-a) - y * math.sin(-a), x * math.sin(-a) + y * math.cos(-a)
            if 0 <= px_ <= 0.5 and abs(py_) < 0.045:
                h = max(h, 1 - abs(py_) / 0.045)
            for bt in (0.26, 0.38):
                bx, by = px_ - bt, py_
                aa = math.radians(50)
                qx, qy = bx * math.cos(-aa) - by * math.sin(-aa), bx * math.sin(-aa) + by * math.cos(-aa)
                if 0 <= qx <= 0.13 and abs(qy) < 0.035 and px_ > bt - 0.05:
                    h = max(h, 0.8 - abs(qy) / 0.035 * 0.3)
        h = max(h, 0.9 if r < 0.09 else 0.0)
        return h
    if kind == "sun":
        h = 0.9 if r < 0.17 else 0.0
        rays = ss(0.42, 0.30, r) * ss(0.4, 0.6, abs(math.cos(ang * 6)))
        h = max(h, rays * 0.85)
        ring = ss(0.03, 0.0, abs(r - 0.23))
        h = max(h, ring)
        return min(1, h)
    return 0.0


def coin_render(style, f, total, R_px, seed=7, back=False):
    S = R_px * 2
    ang = f / total * math.tau
    squash = 0.10 + 0.90 * abs(math.cos(ang))          # ellipse width factor
    yy, xx = np.mgrid[0:S, 0:S].astype(float)
    cx = cy = (S - 1) / 2
    u = (xx - cx) / (R_px * squash)                     # face coords (-1..1 across)
    v = (yy - cy) / R_px
    r = np.sqrt(((xx - cx) / R_px) ** 2 + ((yy - cy) / (R_px)) ** 2)
    inside_face = (np.sqrt((u) ** 2 + v ** 2) <= 1.0) & (squash > 0.28)
    P = STYLES[style]
    base = np.array(P["base"], float); hi = np.array(P["hi"], float)
    lo = np.array(P["lo"], float); edge = np.array(P["edge"], float)

    brushed = vn(seed + 3, S)
    fine = vn(seed + 4, S * 2 // 3)
    col = np.repeat(base[None, None, :], S, 0).repeat(S, 1).astype(float)
    # brushed metal grain
    col = mix(col, lo[None, None, :], (1 - brushed)[..., None] * 0.30)
    col = mix(col, hi[None, None, :], ss(0.72, 0.95, fine[..., ::3][:, ::3] if False else vn(seed + 4, S))[..., None] * 0.35)
    # dome shading of planchet (light top-left)
    lx = u * 0.6 - 0.55; ly = v - 0.55
    diff = np.clip(1.0 - np.sqrt(lx ** 2 + ly ** 2) * 0.85, 0, 1)
    col = mix(col, hi[None, None, :], ss(0.75, 1.0, diff)[..., None] * 0.55)
    col = mix(col, lo[None, None, :], (1 - diff)[..., None] * 0.35)
    # env reflection band (warm floor bounce at bottom)
    bounce = ss(0.55, 0.95, v) * (1 - np.abs(u))
    col = mix(col, np.array((255, 170, 60), float)[None, None, :], bounce[..., None] * 0.30)
    # field ring recess + double rim
    rr = np.sqrt(u ** 2 + v ** 2)
    field = ss(0.80, 0.76, rr)                          # inside rim line
    rim_hi = ss(0.03, 0.0, np.abs(rr - 0.90))           # raised ring
    col = mix(col, hi[None, None, :], rim_hi[..., None] * 0.7)
    col = mix(col, edge[None, None, :], ss(0.78, 0.84, rr)[..., None] * (1 - rim_hi)[..., None] * 0.5)
    # beaded border between 0.80r and 0.88r
    th = np.arctan2(v, u)
    beads = (rr > 0.78) & (rr < 0.90)
    bn = ss(0.55, 0.8, np.cos(th * 18 + 0.3))
    col = mix(col, hi[None, None, :], (beads & (bn > 0.5))[..., None] * 0.35)
    col = mix(col, lo[None, None, :], (beads & (bn <= 0.5))[..., None] * 0.30)
    # emblem emboss (front styles) with light-direction sculpt
    eh = np.zeros((S, S))
    mask_zone = (rr < 0.62) & inside_face
    idx = np.argwhere(mask_zone)
    if len(idx) and not back:
        hv = np.zeros((S, S))
        us = u[idx[:, 0], idx[:, 1]]; vs = v[idx[:, 0], idx[:, 1]]
        for k in range(len(idx)):
            hv[idx[k, 0], idx[k, 1]] = emblem_h(us[k], vs[k], P["emblem"])
        eh = hv
    elif back:
        # reverse: concentric milled rings + mint mark dot pattern
        hv = ss(0.02, 0.0, np.abs((rr * 9) % 1 - 0.5) - 0.18) * (rr < 0.8)
        eh = hv
    if eh.max() > 0:
        gx = np.roll(eh, -1, 1) - np.roll(eh, 1, 1)
        gy = np.roll(eh, -1, 0) - np.roll(eh, 1, 0)
        lit = np.clip(-(gx * 0.7 + gy * 0.7) * 6 + 0.5, 0, 1)     # light from TL
        ao = ss(0.0, 0.35, eh)                                     # contact shadow at foot
        col = mix(col, hi[None, None, :], (eh * lit)[..., None] * 0.85)
        col = mix(col, edge[None, None, :], (eh * (1 - lit))[..., None] * 0.6)
        col = mix(col, lo[None, None, :], (ao[..., None] * 0.15) * (eh > 0)[..., None])
        col = mix(col, base * 1.06, (eh * 0.25)[..., None])
    # ---- edge band when turned: milled reeding ----------------------------
    edge_w = (1 - squash) * R_px * 0.9
    side = (~inside_face) & (np.abs(xx - cx) < R_px + 2) & (r <= 1.0 + (1 - squash) * 0.5) \
        & (np.abs(yy - cy) <= R_px * np.sqrt(np.clip(1 - ((np.abs(xx - cx) - R_px * squash) / max(edge_w, 1)) ** 2, 0, 1)))
    teeth = ss(0.4, 0.6, np.sin((xx / max(edge_w, 1)) * math.pi * 14)) * 0.5 + 0.5
    ec = mix(edge[None, None, :] * 1.0, hi[None, None, :], teeth[..., None] * 0.6)
    ec = mix(ec, np.array((90, 50, 8), float)[None, None, :], ss(0.6, 1.0, np.abs(v))[..., None] * 0.5)
    col = np.where(side[..., None], ec, col)
    # travelling specular glints (two passes per half turn)
    ca = math.cos(ang * 2 + 0.7)
    for gd in (ca, -ca * 0.6):
        gx_ = cx + gd * R_px * 0.55; gy_ = cy - R_px * 0.35
        d2 = ((xx - gx_) / (R_px * 0.34)) ** 2 + ((yy - gy_) / (R_px * 0.6)) ** 2
        g = np.exp(-d2 * 2.2) * (0.55 + 0.45 * abs(math.cos(ang)))
        col = mix(col, np.array((255, 255, 240), float)[None, None, :], g[..., None] * 0.75)
    a = np.where(inside_face | side, 1.0, 0.0)
    rgba = np.dstack([np.clip(col, 0, 255), (a * 255)]).astype(np.uint8)
    img = Image.fromarray(rgba)
    # outer outline ring for pixel-art readability
    outline = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    od = np.clip(ss(0.985, 1.0, r) * (r < 1.02), 0, 1) * (a > 0)
    oa = np.dstack([np.repeat((edge * 0.9)[None, None, :], S, 0).repeat(S, 1), (od * 255)[..., None]]).astype(np.uint8)
    outline = Image.fromarray(oa)
    img = Image.alpha_composite(outline, img)
    # bloom
    glow = img.filter(ImageFilter.GaussianBlur(max(2, S // 40)))
    ga = glow.split()[3].point(lambda p: int(p * 0.35))
    glow.putalpha(ga)
    return Image.alpha_composite(glow, img)


def down(img, size_log):
    return img.resize((size_log, size_log), Image.BOX)


# ---- generate: 10-frame HD spins @256 + logical 8-frame sheets @32 ---------
LOGICAL = {}
for style in STYLES:
    hd_frames = []
    for f in range(10):
        im = coin_render(style, f, 10, 128, seed={"classic": 7, "snow": 17, "beach": 27}[style])
        im.save(os.path.join(HD, f"{style}_f{f}.png"))
        hd_frames.append(im)
    LOGICAL[style] = hd_frames
    print("HD frames:", style)

# logical sheets: pick 8 evenly-spread frames from the 10-frame cycle
def build_sheet(style, cell=32, nframes=8, fname=None, src_total=10):
    frames = LOGICAL[style]
    cols = nframes
    canvas = Image.new("RGBA", (cell * cols, cell), (0, 0, 0, 0))
    for i in range(cols):
        src = frames[int(round(i * (src_total - 1) / max(cols - 1, 1)))]
        small = down(src, cell)
        canvas.paste(small, (i * cell, 0), small)
    canvas.save(os.path.join(OUT, fname))
    return canvas


build_sheet("classic", 32, 8, "gold_classic.png")
build_sheet("snow", 32, 8, "gold_snow.png")
build_sheet("beach", 32, 8, "gold_beach.png")

# mega milestone coin: bigger logical 48px cells from dedicated 384px renders
for style in ("classic",):
    big = [coin_render(style, f, 10, 192, seed=7) for f in range(10)]
    for f, im in enumerate(big):
        im.save(os.path.join(HD, f"{style}_mega_f{f}.png"))
    canvas = Image.new("RGBA", (48 * 10, 48), (0, 0, 0, 0))
    for i, im in enumerate(big):
        s = down(im, 96).resize((48, 48), Image.LANCZOS)
        canvas.paste(s, (i * 48, 0), s)
    canvas.save(os.path.join(OUT, "gold_mega.png"))
    print("mega ok")

# previews
strip = Image.new("RGBA", (256 * 5, 256), (24, 20, 34, 255))
for i in range(5):
    strip.paste(LOGICAL["classic"][i * 2], (i * 256, 0), LOGICAL["classic"][i * 2])
strip.resize((strip.width // 2, strip.height // 2)).save(os.path.join(PREV, "gold_classic_spin@hd.png"))
big_beauty = LOGICAL["classic"][0]
big_beauty.save(os.path.join(PREV, "gold_hero_frame@256.png"))

# UI icon 16px (face-on)
icon = down(LOGICAL["classic"][0], 16)
icon.save(os.path.join(ROOT, "ui", "icon_coin.png"))
print("true-HD gold coins ok")
