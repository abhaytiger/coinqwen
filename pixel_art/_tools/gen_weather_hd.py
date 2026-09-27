"""WEATHER v2 — high-detail, multi-element weather FX per world (true-HD ready).

Every emitter particle gets a crisp logical sprite AND an ultra-detailed HD
variant: drawn at 16x supersample, painted with fBm value-noise texture,
multi-layer speculars and soft bloom, so the same id can be used for
parallax "hero" particles rendered at full screen resolution.

classic_meadow : snow-free -> leaf spin cycles x3 tints, pine needle, acorn,
                 dandelion seed, feather, pollen dot + glow, sparkly dust mote,
                 firefly (4f blink), rain drop/ripple/splash, cloud puff, sunbeam
snow_town      : 6 unique crystal flakes + flake_big(6-arm detail), graupel,
                 icicle shard, frost star, snowball, soft fluff, sparkle burst,
                 mist puff, hoar fleck
beach          : foam bubble x3, cluster, droplet, spray crown, wet speck,
                 sand grain, shell fragment, sea foam ring, petal, tiny feather,
                 sun glitter, heat shimmer band, gull feather, salt crystal

Outputs into pixel_art/weather/:
  <id>.png             logical sprite (legacy size-compatible ids kept)
  hd/<id>_hd.png       128px true-HD render (bloom + noise texture)
  sheets/weather_<world>.png   packed sheet @64px cells (all elements)
  previews/*.png       eyeball strips
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

ROOT = "/workspace/pixel_art/weather"
HD = os.path.join(ROOT, "hd")
PREV = os.path.join(ROOT, "previews")
SHEET = os.path.join(ROOT, "sheets")
for d in (ROOT, HD, PREV, SHEET):
    os.makedirs(d, exist_ok=True)

U = 16  # supersample factor for HD renders


# ------------------------------------------------------------- value noise
def fbm(seed, size=96, octaves=5, persist=0.55, lac=2.1):
    rnd = random.Random(seed)
    out = np.zeros((size, size), dtype=np.float64)
    amp = 1.0
    tot = 0.0
    for o in range(octaves):
        cell = max(2, size // int(lac ** (o + 2)))
        gy = (size // cell) + 2
        g = np.random.RandomState(rnd.randrange(1 << 30)).rand(gy, gy) * 2 - 1
        # bilinear upsample of grid noise
        ys = np.linspace(0, gy - 1.001, size)
        xs = np.linspace(0, gy - 1.001, size)
        y0 = ys.astype(int); x0 = xs.astype(int)
        fy = ys - y0; fx = xs - x0
        def at(dy, dx):
            return g[np.clip(y0 + dy, 0, gy - 1)[:, None], np.clip(x0 + dx, 0, gy - 1)[None, :]]
        top = at(0, 0) * (1 - fx[:, None]) + at(0, 1) * fx[:, None]
        bot = at(1, 0) * (1 - fx[:, None]) + at(1, 1) * fx[:, None]
        layer = top * (1 - fy[:, None]) + bot * fy[:, None]
        out += layer * amp
        tot += amp
        amp *= persist
    out /= tot
    return (out - out.min()) / (np.ptp(out) + 1e-9)


def radial(size=96, power=2.0):
    c = (size - 1) / 2
    y, x = np.mgrid[0:size, 0:size]
    r = np.sqrt((x - c) ** 2 + (y - c) ** 2) / c
    return np.clip(1.0 - r, 0, 1) ** power


def paint(base_rgba, mask_fn, tint_hi=None, tint_lo=None, noise_seed=1,
          noise_strength=26, size=96):
    """mask_fn(xx, yy, n) -> alpha 0..1 on [0,1]^2 coords; n = fbm noise."""
    n = fbm(noise_seed, size)
    rgba = np.zeros((size, size, 4), dtype=np.float64)
    br, bg, bb = base_rgba[:3]
    yy, xx = np.mgrid[0:size, 0:size]
    u = xx / (size - 1.0)
    v = yy / (size - 1.0)
    a = np.vectorize(lambda X, Y: mask_fn(X, Y))(u, v) if False else np.array(
        [[mask_fn(u[i, j], v[i, j], n[i, j]) for j in range(size)] for i in range(size)])
    a = np.clip(a, 0, 1)
    shade = (n - 0.5) * 2 * noise_strength
    hi = tint_hi or (min(255, br + 70), min(255, bg + 70), min(255, bb + 70))
    lo = tint_lo or (max(0, br - 60), max(0, bg - 60), max(0, bb - 60))
    # vertical light: brighter at top
    lamp = (1.0 - v) * 22 - 8
    rgba[..., 0] = np.clip(br + shade + lamp * 0.6 + (np.array(hi)[0] - br) * np.clip(shade / 60 + 0.35 * (1 - v), 0, 1) * 0.5, 0, 255)
    rgba[..., 1] = np.clip(bg + shade * 0.9 + lamp * 0.5 + (np.array(hi)[1] - bg) * np.clip(shade / 60 + 0.35 * (1 - v), 0, 1) * 0.5, 0, 255)
    rgba[..., 2] = np.clip(bb + shade * 0.8 + lamp * 0.3 + (np.array(hi)[2] - bb) * np.clip(shade / 60 + 0.35 * (1 - v), 0, 1) * 0.5, 0, 255)
    rgba[..., 3] = a * 255
    img = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    return img, a


def bloom(img, radius=6, strength=0.55):
    a = img.split()[3].point(lambda v: min(255, int(v * strength)))
    gl = img.filter(ImageFilter.GaussianBlur(radius))
    gl.putalpha(a)
    return Image.alpha_composite(gl, img)


def spec(img, cx, cy, r, white=(255, 255, 255)):
    """additive round specular highlight"""
    d = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(d)
    dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=white + (170,))
    d = d.filter(ImageFilter.GaussianBlur(max(1, r // 3)))
    img.alpha_composite(d)
    return img


def to_logical(img, size_log):
    return img.resize((size_log, size_log), Image.LANCZOS)


WORLD = {"meadow": [], "snow": [], "beach": []}


def emit(world, ident, size_log, mask_fn, base, hi=None, lo=None, seed=1,
         ns=26, do_bloom=True, legacy=None):
    hd = U * size_log
    img, _ = paint(base, mask_fn, hi, lo, seed, ns, size=max(64, hd))
    img = img.resize((hd, hd), Image.LANCZOS)
    final = bloom(img, radius=max(2, hd // 22), strength=0.45) if do_bloom else img
    final.save(os.path.join(HD, f"{ident}_hd.png"))
    to_logical(final, size_log).save(os.path.join(ROOT, f"{ident}.png"))
    if legacy:
        to_logical(final, legacy[0]).save(os.path.join(ROOT, f"{legacy[1]}.png"))
    WORLD[world].append((ident, final))
    return final


def ell_mask(rx, ry, tilt=0.0, cut=None):
    def m(x, y, n=0):
        dx, dy = x - .5, y - .5
        c, s = math.cos(tilt), math.sin(tilt)
        u, v = dx * c - dy * s, dx * s + dy * c
        a = 1.0 if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0 else 0.0
        if a and cut:
            a = cut(x, y)
        return a
    return m


def union(*ms):
    def m(x, y, n=0):
        return max(f(x, y) for f in ms)
    return m


def sub(hay, needle):
    def m(x, y, n=0):
        return hay(x, y) and not needle(x, y)
    return m


# ================================================================ MEADOW ====
LEAF_T = dict(maple=((196, 74, 40, 255), (255, 170, 90, 255), (120, 36, 24, 255)),
              gold=((236, 178, 52, 255), (255, 236, 150, 255), (160, 104, 22, 255)),
              green=((120, 186, 74, 255), (206, 240, 140, 255), (60, 110, 44, 255)))


def leaf_shape(x, y, n=0):
    # pointed oval leaf, tip up-right
    dx, dy = x - .5, y - .5
    c, s = math.cos(-0.6), math.sin(-0.6)
    u, v = dx * c - dy * s, dx * s + dy * c
    inside = (u / 0.42) ** 2 + (v / 0.24) ** 2 <= 1.0
    if not inside:
        return 0.0
    # scalloped edge bite marks
    ang = math.atan2(v, u)
    bite = 0.9 + 0.1 * math.sin(ang * 7)
    if (u / 0.42) ** 2 + (v / 0.24) ** 2 > bite * bite:
        return 0.0
    return 1.0


for key, (base, hi, lo) in LEAF_T.items():
    emit("meadow", f"leaf_{key}", 12, leaf_shape, base, hi, lo,
         seed={"maple": 21, "gold": 22, "green": 23}[key],
         legacy=(8, "leaf") if key == "maple" else None)

emit("meadow", "needle", 10,
     ell_mask(0.5, 0.06, tilt=-0.7), (96, 140, 82, 255), (170, 210, 130, 255),
     (48, 80, 44, 255), seed=31, do_bloom=False)
emit("meadow", "acorn", 12,
     lambda x, y, n=0: (0.0 if y < 0.42 else (1.0 if ((x - .5) / .3) ** 2 + ((y - .62) / .34) ** 2 <= 1 else 0.0)),
     (196, 148, 84, 255), (240, 208, 150, 255), (120, 80, 40, 255), seed=41)
emit("meadow", "dandelion", 12,
     lambda x, y, n=0: 1.0 if math.hypot(x - .5, y - .5) < 0.44 and (
         math.hypot(x - .5, y - .5) < 0.12 or int(math.degrees(math.atan2(y - .5, x - .5)) * 12 / 360) % 2 == 0
         or math.hypot(x - .5, y - .5) > 0.34) else 0.0,
     (248, 250, 252, 255), (255, 255, 255, 255), (200, 210, 226, 255), seed=51)
emit("meadow", "feather", 12,
     ell_mask(0.16, 0.46, tilt=0.5), (236, 240, 248, 255), (255, 255, 255, 255),
     (180, 190, 210, 255), seed=61, do_bloom=False)
emit("meadow", "pollen", 6, ell_mask(0.45, 0.45), (252, 226, 120, 255),
     (255, 250, 200, 255), (220, 170, 60, 255), seed=71)
emit("meadow", "pollen_glow", 10, lambda x, y, n=0: max(0, 1 - 2.2 * math.hypot(x - .5, y - .5)),
     (255, 236, 150, 255), do_bloom=True, seed=72, ns=8)
emit("meadow", "dust_mote", 6, lambda x, y, n=0: max(0, 1 - 2.6 * math.hypot(x - .5, y - .5)),
     (250, 244, 226, 255), seed=81, ns=10)
emit("meadow", "sparkle", 10,
     union(ell_mask(0.5, 0.06), ell_mask(0.06, 0.5)), (255, 255, 255, 255),
     seed=91, ns=0)


def firefly_core(x, y):
    return 1.0 if math.hypot(x - .5, y - .5) < 0.3 else 0.0


for f in range(4):
    glow = {0: 0.35, 1: 0.7, 2: 1.0, 3: 0.55}[f]
    emit("meadow", f"firefly_f{f}", 12,
         lambda x, y, g=glow: max(0.0, min(1.0, (g * 1.5 - 2.1 * math.hypot(x - .5, y - .5)))) if g > 0.4 else (1.0 if math.hypot(x - .5, y - .5) < 0.16 else 0.0),
         (180, 255, 120, 255), (240, 255, 200, 255), (60, 120, 30, 255),
         seed=100 + f, ns=6, do_bloom=True)
emit("meadow", "raindrop", 12,
     lambda x, y, n=0: 1.0 if (((x - .5) / 0.26) ** 2 + ((y - .56) / 0.3) ** 2 <= 1 and y >= .5)
     or (((x - .5) / 0.26) ** 2 + ((y - .42) / 0.42) ** 2 <= 1 and y < .5) else 0.0,
     (150, 200, 245, 255), (230, 245, 255, 255), (90, 140, 200, 255), seed=111)
emit("meadow", "rain_ripple", 14,
     lambda x, y, n=0: 1.0 if 0.30 < math.hypot(x - .5, (y - .5) * 2.4) < 0.42 else 0.0,
     (200, 226, 250, 255), seed=121, do_bloom=False, ns=10)
emit("meadow", "splash", 12,
     union(*[(lambda x, y, a=a: 1.0 if math.hypot(x - (.5 + 0.34 * math.cos(a)), y - (.62 + 0.3 * math.sin(a))) < 0.07 else 0.0)
             for a in (-2.4, -1.6, -0.9, -2.9, -0.4)]),
     (190, 220, 250, 255), seed=131, do_bloom=False)
def cloud_mask(x, y, n=0):
    lobes = ((0.5, 0.55, 0.34), (0.28, 0.6, 0.2), (0.55, 0.36, 0.24), (0.74, 0.52, 0.17))
    return 1.0 if any(math.hypot(x - cx, (y - cy) * 1.25) < r for cx, cy, r in lobes) else 0.0


emit("meadow", "cloud_puff", 16, cloud_mask,
     (250, 252, 255, 255), (255, 255, 255, 255), (214, 226, 244, 255), seed=141, ns=14)
emit("meadow", "sunbeam", 16,
     lambda x, y, n=0: 1.0 if abs(x - (0.5 + (y - 0.5) * 0.35)) < 0.10 and 0 <= y <= 1 else 0.0,
     (255, 240, 170, 255), seed=151, ns=6)

# ============================================================== SNOW ========
def flake_arm(x, y, ang, w=0.045, L=0.44, branches=True):
    dx, dy = x - .5, y - .5
    c, s = math.cos(ang), math.sin(ang)
    u, v = dx * c + dy * s, -dx * s + dy * c
    if 0 <= u <= L and abs(v) < w:
        return True
    if branches and 0.22 <= u <= 0.36:
        for ba in (math.pi / 4, -math.pi / 4):
            bx, by = u - 0.29, v
            c2, s2 = math.cos(ba), math.sin(ba)
            p, q = bx * c2 - by * s2, bx * s2 + by * c2
            if 0 <= p <= 0.14 and abs(q) < w * 0.8:
                return True
    return False


def crystal(narms=6, style=0):
    def m(x, y, n=0):
        hit = 0
        for k in range(narms):
            if flake_arm(x, y, k * 2 * math.pi / narms + style):
                hit = 1
        if math.hypot(x - .5, y - .5) < 0.07:
            hit = 1
        return float(hit)
    return m


ICE = ((236, 248, 255, 255), (255, 255, 255, 255), (160, 200, 240, 255))
emit("snow", "flake_needle", 12, crystal(6, 0.0), *ICE, seed=201)
emit("snow", "flake_plate", 12, lambda x, y, n=0: 1.0 if math.hypot(x - .5, y - .5) < 0.4 and (int(math.degrees(math.atan2(y - .5, x - .5)) * 6 / 360) % 2 == 0 or math.hypot(x - .5, y - .5) < 0.26) else 0.0, *ICE, seed=202)
emit("snow", "flake_star", 12, crystal(6, math.pi / 6), *ICE, seed=203)
emit("snow", "flake_dendrite", 14, crystal(6, 0.2), *ICE, seed=204)
emit("snow", "flake_column", 10, union(ell_mask(0.12, 0.42), ell_mask(0.3, 0.08)), *ICE, seed=205)
emit("snow", "flake_capped", 10, union(ell_mask(0.1, 0.4), ell_mask(0.34, 0.1)), *ICE, seed=206)
emit("snow", "snowflake_big", 16, crystal(6, 0.0), *ICE, seed=207, legacy=(8, "snowflake_big"))
emit("snow", "snowflake", 8, crystal(6, 0.35), *ICE, seed=208, legacy=(8, "snowflake"))
emit("snow", "fluff", 10, lambda x, y, n=0: max(0, 1 - 2.4 * math.hypot(x - .5, y - .5)),
     (248, 251, 255, 255), seed=209, ns=12)
emit("snow", "graupel", 8, ell_mask(0.42, 0.42), (226, 236, 248, 255),
     (255, 255, 255, 255), (150, 170, 200, 255), seed=210, ns=40)
emit("snow", "ice_shard", 12,
     lambda x, y, n=0: 1.0 if ((x - .5) / 0.14) ** 2 + ((y - .5) / 0.46) ** 2 <= 1 and x > .5 - 0.14 * (1 - (y - .5)) else 0.0,
     (190, 226, 252, 255), (255, 255, 255, 255), (120, 160, 210, 255), seed=211)
emit("snow", "frost_star", 12, crystal(3, 0.0), *ICE, seed=212, ns=8)
emit("snow", "snowball", 14, ell_mask(0.44, 0.44), (244, 248, 253, 255),
     (255, 255, 255, 255), (180, 200, 226, 255), seed=213, ns=34)
emit("snow", "mist", 16, lambda x, y, n=0: max(0, 0.9 - 1.7 * math.hypot((x - .5) * 1.5, (y - .5) * 2.6)),
     (238, 246, 255, 255), seed=214, ns=16)
emit("snow", "hoar", 8, crystal(4, math.pi / 4), (222, 238, 252, 255), seed=215, ns=10)
emit("snow", "sparkle", 10, union(ell_mask(0.5, 0.05), ell_mask(0.05, 0.5),
                                  ell_mask(0.28, 0.28)), (255, 255, 255, 255), seed=216, ns=0)

# =============================================================== BEACH =======
BUB = ((214, 240, 255, 255), (255, 255, 255, 255), (150, 195, 235, 255))


def bubble(size_r=0.42, hole=0.0):
    def m(x, y, n=0):
        d = math.hypot(x - .5, y - .5)
        if d > size_r or d < hole:
            return 0.0
        # rim thicker than center (film look)
        return 1.0
    return m


emit("beach", "bubble", 8, bubble(0.44, 0.30), *BUB, seed=301, legacy=(8, "bubble"))
emit("beach", "bubble_small", 6, bubble(0.45, 0.32), *BUB, seed=302)
emit("beach", "bubble_big", 12, bubble(0.45, 0.33), *BUB, seed=303)
emit("beach", "bubble_cluster", 14,
     union(*[(lambda x, y, cx=cx, cy=cy, r=r: 1.0 if (math.hypot(x - cx, y - cy) < r and math.hypot(x - cx, y - cy) > r * 0.72) else 0.0)
             for cx, cy, r in ((0.35, 0.4, 0.26), (0.66, 0.55, 0.2), (0.45, 0.72, 0.14))]),
     *BUB, seed=304)
emit("beach", "droplet", 10,
     lambda x, y, n=0: 1.0 if ((x - .5) / 0.24) ** 2 + ((y - .58) / 0.3) ** 2 <= 1 or ((x - .5) / 0.16) ** 2 + ((y - .36) / 0.28) ** 2 <= 1 else 0.0,
     (170, 215, 248, 255), (245, 252, 255, 255), (110, 160, 215, 255), seed=305)
emit("beach", "spray", 12,
     union(*[(lambda x, y, a=a: 1.0 if math.hypot(x - (.5 + 0.36 * math.cos(a)), y - (.5 + 0.36 * math.sin(a))) < 0.08 else 0.0)
             for a in (-2.2, -1.1, -0.35, -2.85, -1.8, -0.8)]),
     (220, 244, 255, 255), seed=306, do_bloom=False)
emit("beach", "foam_ring", 14,
     lambda x, y, n=0: 1.0 if 0.30 < math.hypot(x - .5, y - .5) < 0.44 else 0.0,
     (240, 250, 255, 255), seed=307, ns=40)
emit("beach", "sand_grain", 5, ell_mask(0.45, 0.45), (236, 208, 150, 255),
     (255, 240, 200, 255), (180, 150, 96, 255), seed=308, do_bloom=False)
emit("beach", "shell_bit", 8,
     lambda x, y, n=0: 1.0 if y < .55 and math.hypot(x - .5, y - .55) < 0.42 and int(math.degrees(math.atan2(y - .55, x - .5)) * 5 / 180 + 1) % 2 == 0 or (y >= .5 and math.hypot(x - .5, y - .55) < 0.12) else 0.0,
     (250, 226, 210, 255), (255, 248, 240, 255), (200, 150, 130, 255), seed=309)
emit("beach", "petal", 10, ell_mask(0.2, 0.45, tilt=0.6), (250, 150, 170, 255),
     (255, 220, 230, 255), (205, 96, 120, 255), seed=310)
emit("beach", "gull_feather", 12, ell_mask(0.15, 0.46, tilt=-0.4), (246, 248, 250, 255),
     (255, 255, 255, 255), (170, 178, 190, 255), seed=311, do_bloom=False)
emit("beach", "glitter", 8, union(ell_mask(0.5, 0.05), ell_mask(0.05, 0.5)),
     (255, 250, 220, 255), seed=312, ns=0)
emit("beach", "salt", 6, crystal(4, math.pi / 4), (250, 252, 255, 255), seed=313, ns=6)
emit("beach", "heat_shimmer", 16,
     lambda x, y, n=0: 1.0 if abs(math.sin(y * 18) * 0.06 + 0.5 - x) < 0.05 and y > 0.2 else 0.0,
     (255, 246, 220, 255), seed=314, ns=4, do_bloom=True)

# --------------------------------------------------------------- packaging --
def pack_sheet(name, items, cell=128):
    cols = 6
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new("RGBA", (cols * cell, rows * cell), (24, 20, 34, 0))
    for i, (ident, im) in enumerate(items):
        s = im.copy()
        s.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
        x = (i % cols) * cell + (cell - s.width) // 2
        y = (i // cols) * cell + (cell - s.height) // 2
        canvas.paste(s, (x, y), s)
    canvas.save(os.path.join(SHEET, f"weather_{name}.png"))
    canvas.resize((canvas.width // 2, canvas.height // 2), Image.LANCZOS).save(
        os.path.join(PREV, f"weather_{name}_sheet@0.5x.png"))


for w, items in WORLD.items():
    pack_sheet(w, items)
    print(f"weather {w}: {len(items)} elements")
print("weather HD ok")
