"""ULTRA ground v3 — 'very high resolution' terrain WITHOUT breaking tiling.

Two upgrades per world:

1) TILE VARIANTS: the mega_* sheets grow from 4 to 8 unique surface tiles and
   from 2 to 4 unique dirt/frost/wet-sand fills (mirrored copies included),
   so long runs never show an obvious repeat pattern.

2) HD GROUND DECALS (the real 'high resolution' pass): large 64x64 / 96x96
   patches rendered at 8x supersample with numpy fBm — pebble clusters, root
   networks, cracks, moss patches, litter, ice lenses, shells, wet streaks —
   painted OVER the tile grid by the game to break up repetition at any zoom.
   Each decal also ships as a full-res *_hd.png for close-ups/cinematics.

Outputs (overwrites + extends):
  ground/mega_grass.png | mega_snow.png | mega_sand.png   (8 cols x 5 rows @16)
  ground/decals/<world>_*.png        logical decals (transparent edges)
  ground/decals/hd/*_hd.png          true-HD renders
  ground/decal_sheet_<world>.png     contact sheets
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image

# reuse existing generators' primitives by importing them is unsafe (they save
# on import); instead re-implement tiny helpers + call their functions via exec
# of just the function bodies we need. Simplest: import module pieces we need.
from pxlib import SCALE, Sheet, flip_h, ellipse, rect, line, px, shade, darker, lighter
from pxlib2 import alpha_at, get, put, top_light, bottom_shade
import gen_ground_mega as gm  # NOTE: this re-saves the old sheets first; we
# overwrite mega_* afterwards with the richer variant sets below.

OUT = "/workspace/pixel_art/ground"
DEC = os.path.join(OUT, "decals")
HD = os.path.join(DEC, "hd")
for d in (OUT, DEC, HD):
    os.makedirs(d, exist_ok=True)
S = 16
SS = 8


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
        tot += amp; amp *= 0.52; cell = min(size, cell * 2 + 3)
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-9)


def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a * (1 - t) + b * t


# ----------------------------------------------------------- extra surfaces --
def grass_surface2(seed, blades=2, patchy=True):
    img = gm.grass_surface(seed, blades)
    rnd = random.Random(seed * 31 + 7)
    if patchy:
        for _ in range(6):
            x, y = rnd.randint(0, S - 3), rnd.randint(4, S - 3)
            w = rnd.randint(2, 3)
            for xx in range(x, min(S, x + w)):
                put(img, xx, y, lighter(gm.GRASS_MID, rnd.choice([8, 18])))
        # tiny flowers embedded
        for _ in range(rnd.randint(0, 2)):
            x, y = rnd.randint(1, S - 2), rnd.randint(5, S - 2)
            c = rnd.choice([(250, 240, 120, 255), (250, 160, 190, 255), (240, 244, 252, 255)])
            px(img, x, y, c); px(img, x + 1, y, darker(c, 30))
    return img


def snow_surface2(seed):
    img = gm.snow_surface(seed)
    rnd = random.Random(seed * 17 + 3)
    # wind ripple lines
    for _ in range(3):
        y = rnd.randint(4, S - 2); x = rnd.randint(0, S - 5)
        for xx in range(x, min(S, x + rnd.randint(3, 6))):
            put(img, xx, y, gm.SNOW_TOP[1])
            if xx > x:
                put(img, xx, y - 1, (255, 255, 255, 255))
    # frozen pebbles poking through
    for _ in range(2):
        x, y = rnd.randint(1, S - 2), rnd.randint(3, S - 2)
        px(img, x, y, (150, 168, 196, 255)); px(img, x + 1, y, (120, 140, 172, 255))
        px(img, x, y - 1, (236, 244, 252, 255))
    return img


def sand_surface2(seed):
    img = gm.sand_surface(seed)
    rnd = random.Random(seed * 13 + 5)
    # ripple chain + shell grit + crab hole
    for _ in range(2):
        y = rnd.randint(2, S - 3); x = rnd.randint(0, S - 6)
        for xx in range(x, min(S, x + 5)):
            put(img, xx, y + int(round(math.sin((xx - x) * 1.2))), gm.SAND_T[1])
    hx, hy = rnd.randint(3, S - 4), rnd.randint(4, S - 4)
    ellipse(img, hx, hy, hx + 2, hy + 1, darker(gm.SAND_M, 46))
    px(img, hx + 1, hy, darker(gm.SAND_M, 70))
    for _ in range(3):
        x, y = rnd.randint(0, S - 1), rnd.randint(0, S - 1)
        px(img, x, y, (255, 248, 232, 255))
    return img


# ============================================================ HD decals =====
def decal(world, name, size_log, fn, seed):
    SZ = size_log * SS
    yy, xx = np.mgrid[0:SZ, 0:SZ]
    u = xx / SZ; v = yy / SZ
    col = np.zeros((SZ, SZ, 3)); a = np.zeros((SZ, SZ))
    col, a = fn(u, v, SZ, seed)
    a = np.clip(a, 0, 1) * feather_alpha(u, v)
    rgba = np.dstack([np.clip(col, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
    hd = Image.fromarray(rgba)
    lg = hd.resize((size_log, size_log), Image.BOX)
    hd.save(os.path.join(HD, f"{name}_hd.png"))
    lg.save(os.path.join(DEC, f"{name}.png"))
    return lg


def feather_alpha(u, v, soft=0.18):
    """fade rectangle edges so decals blend over tiles seamlessly"""
    ax = np.minimum(ss(0, soft, u), ss(1, 1 - soft, u))
    ay = np.minimum(ss(0, soft, v), ss(1, 1 - soft, v))
    return ax * ay


def pebbles_layer(u, v, SZ, seed, pal, count=9, rmin=0.02, rmax=0.06):
    a = np.zeros((SZ, SZ)); col = np.zeros((SZ, SZ, 3))
    rnd = random.Random(seed)
    for i in range(count):
        cx, cy = rnd.uniform(.1, .9), rnd.uniform(.15, .9)
        r = rnd.uniform(rmin, rmax)
        d = np.sqrt((u - cx) ** 2 + ((v - cy) * 1.15) ** 2)
        m = ss(r + 0.008, r - 0.008, d)
        tone = rnd.choice(pal)
        sh = np.clip(1.15 - 1.6 * np.sqrt((u - (cx + r * .3)) ** 2 + (v - (cy + r * .4)) ** 2) / max(r, .01), 0, 1)
        pc = np.array(tone, float) * (0.65 + 0.5 * sh[..., None])
        col = mix(col, pc, m[..., None])
        a = np.maximum(a, m * 0.95)
        # drop shadow under pebble
        sd = ss(r * 1.5 + 0.01, r * 1.5 - 0.01, np.sqrt((u - cx) ** 2 + ((v - cy - r * .5) * 2) ** 2))
        col = mix(col, np.array(tone, float) * 0.45, sd[..., None] * 0.5)
        a = np.maximum(a, sd * 0.4)
    return col, a


def meadow_litter(u, v, SZ, seed):
    col, a = pebbles_layer(u, v, SZ, seed, [(150, 108, 66), (120, 84, 52), (176, 138, 88)], 6, .015, .04)
    rnd = random.Random(seed + 1)
    # fallen leaves & needles
    for i in range(7):
        cx, cy = rnd.uniform(.1, .9), rnd.uniform(.15, .9)
        ang = rnd.uniform(0, math.pi); L = rnd.uniform(.05, .09)
        dx, dy = math.cos(ang), math.sin(ang)
        px_, py_ = u - cx, v - cy
        along = px_ * dx + py_ * dy
        perp = -px_ * dy + px_ * 0 + py_ * dx
        m = ss(L, L * 0.7, np.abs(along)) * ss(0.03, 0.012, np.abs(perp))
        leafc = np.array(rnd.choice([(168, 96, 44), (200, 150, 60), (110, 150, 70)]), float)
        col = mix(col, leafc[None, None, :], m[..., None]); a = np.maximum(a, m * 0.9)
    # grass tufts (bright blade fans)
    for i in range(10):
        bx, by = rnd.uniform(.05, .95), rnd.uniform(.2, .95)
        h = rnd.uniform(.06, .12)
        for k in (-2, -1, 0, 1, 2):
            tx = bx + k * 0.012
            m = ss(0.006, 0.0, np.abs(u - (tx + (by - v) * k * 0.15))) * ss(by, by - h, v) * (v < by)
            gc = np.array((150, 210, 110), float) if k % 2 else np.array((100, 170, 80), float)
            col = mix(col, gc[None, None, :], m[..., None]); a = np.maximum(a, m * 0.85)
    return col, a


def meadow_rocks(u, v, SZ, seed):
    col, a = pebbles_layer(u, v, SZ, seed, [(150, 146, 142), (118, 114, 112), (180, 176, 172)], 10, .02, .07)
    rnd = random.Random(seed + 2)
    # moss patches binding the cluster
    mm = np.clip(vn(seed + 40, SZ) * 1.6 - 0.62, 0, 1)
    mc = np.array((104, 166, 88), float)
    col = mix(col, mc[None, None, :], mm[..., None] * 0.7)
    a = np.maximum(a, mm * 0.6)
    return col, a


def meadow_cracks(u, v, SZ, seed):
    n = vn(seed + 50, SZ)
    ridge = ss(0.487, 0.5, n) * ss(0.525, 0.512, n)
    col = np.repeat(np.array((70, 52, 40), float)[None, None, :], SZ, 0).repeat(SZ, 1)
    chip = np.clip(np.roll(ridge, 1, 0) - ridge, 0, 1)
    col = mix(col, np.array((200, 180, 150), float)[None, None, :], chip[..., None] * 0.6)
    return col, ridge * 0.85


def snow_drift(u, v, SZ, seed):
    n = vn(seed + 60, SZ)
    band = ss(0.55, 0.62, n) * 0.9
    col = np.repeat(np.array((252, 253, 255), float)[None, None, :], SZ, 0).repeat(SZ, 1)
    blue = np.array((206, 224, 246), float)
    col = mix(col, blue[None, None, :], (1 - ss(0.3, 0.9, v))[..., None] * 0.2)
    a = band
    # sparkle points
    sp = (vn(seed + 61, SZ) > 0.93)
    col = mix(col, np.array((255, 255, 255), float)[None, None, :], sp[..., None])
    a = np.maximum(a, sp * band)
    return col, a


def snow_ice_lens(u, v, SZ, seed):
    col, a = pebbles_layer(u, v, SZ, seed, [(186, 214, 238), (160, 196, 230), (214, 236, 252)], 8, .02, .06)
    gl = ss(0.8, 0.95, vn(seed + 70, SZ))
    col = mix(col, np.array((255, 255, 255), float)[None, None, :], gl[..., None] * 0.8)
    a = np.maximum(a, gl * 0.7)
    return col, a


def snow_tracks(u, v, SZ, seed):
    a = np.zeros((SZ, SZ)); col = np.zeros((SZ, SZ, 3))
    rnd = random.Random(seed)
    for i in range(5):
        cx, cy = rnd.uniform(.15, .85), rnd.uniform(.15, .9)
        d = np.sqrt((u - cx) ** 2 + ((v - cy) * 1.2) ** 2)
        dent = ss(0.06, 0.02, d)
        shade_c = np.array((208, 222, 240), float)
        rim = ss(0.075, 0.06, d) * ss(0.05, 0.065, d)
        col = mix(col, shade_c[None, None, :], dent[..., None])
        col = mix(col, np.array((255, 255, 255), float)[None, None, :], rim[..., None])
        a = np.maximum(a, (dent * 0.55 + rim * 0.5))
    return col, a


def beach_shells(u, v, SZ, seed):
    col, a = pebbles_layer(u, v, SZ, seed, [(226, 200, 150), (200, 172, 122), (244, 224, 176)], 7, .012, .03)
    rnd = random.Random(seed + 3)
    for i in range(3):
        cx, cy = rnd.uniform(.15, .85), rnd.uniform(.2, .85)
        r = rnd.uniform(.05, .08); ang = rnd.uniform(0, 6)
        dx, dy = u - cx, v - cy
        rr = np.hypot(dx, dy); th = np.arctan2(dy, dx)
        fan = (rr < r) & (np.mod((th - ang) / (math.pi / 3.5), 1) < 0.5)
        edge = ss(r, r - 0.01, rr) * (rr > r * 0.25)
        m = fan * edge
        sc = np.array((252, 236, 226), float)
        col = mix(col, sc[None, None, :], m[..., None]); a = np.maximum(a, m * 0.9)
        ln = ((np.mod((th - ang) / (math.pi / 14), 1) < 0.25) & (rr < r)).astype(float) * edge
        col = mix(col, np.array((214, 170, 150), float)[None, None, :], ln[..., None] * 0.7)
    return col, a


def beach_wet_streaks(u, v, SZ, seed):
    wave = np.sin(u * math.pi * 3 + vn(seed + 80, SZ) * 4) * 0.08 + 0.55
    band = ss(0.10, 0.0, np.abs(v - wave))
    sheen = ss(0.85, 0.95, vn(seed + 81, SZ)) * band
    col = np.repeat(np.array((176, 148, 96), float)[None, None, :], SZ, 0).repeat(SZ, 1)
    col = mix(col, np.array((255, 252, 240), float)[None, None, :], sheen[..., None])
    foam = ss(0.03, 0.0, np.abs(v - (wave - 0.05))) * (np.sin(u * 40) > -0.3)
    col = mix(col, np.array((246, 252, 255), float)[None, None, :], foam[..., None])
    a = np.clip(band * 0.6 + sheen * 0.3 + foam * 0.8, 0, 1)
    return col, a


def beach_seaweed(u, v, SZ, seed):
    a = np.zeros((SZ, SZ)); col = np.zeros((SZ, SZ, 3))
    rnd = random.Random(seed + 4)
    for i in range(4):
        bx = rnd.uniform(.1, .9); L = rnd.uniform(.25, .5); ph = rnd.uniform(0, 6)
        strand = np.abs(u - (bx + np.sin(v * 12 + ph) * 0.05))
        m = ss(0.02, 0.008, strand) * ss(v - L, v - L + 0.05, 0) * ((v > 0.9 - L) & (v < 0.92))
        wc = np.array((58, 118, 70), float) if i % 2 else np.array((96, 140, 58), float)
        col = mix(col, wc[None, None, :], m[..., None]); a = np.maximum(a, m * 0.9)
    col, pa = pebbles_layer(u, v, SZ, seed + 9, [(196, 172, 122)], 4, .01, .02)
    return col, np.maximum(a, pa * 0.7)


DECALS = [
    ("meadow", "decal_litter", 64, meadow_litter, 101),
    ("meadow", "decal_rockcluster", 96, meadow_rocks, 102),
    ("meadow", "decal_cracks", 64, meadow_cracks, 103),
    ("snow", "decal_driftline", 64, snow_drift, 201),
    ("snow", "decal_icelens", 96, snow_ice_lens, 202),
    ("snow", "decal_tracks", 64, snow_tracks, 203),
    ("beach", "decal_shells", 64, beach_shells, 301),
    ("beach", "decal_wetsand", 96, beach_wet_streaks, 302),
    ("beach", "decal_seaweed", 64, beach_seaweed, 303),
]
made = []
for world, name, sz, fn, seed in DECALS:
    made.append((world, name, decal(world, name, sz, fn, seed)))
    print("decal", name)

# ------------------------------------------------- rebuild mega sheets v3 ---
grass = []
for i in range(4):
    grass.append(gm.grass_surface(3 + i, blades=i))
for i in range(4):
    grass.append(grass_surface2(140 + i, blades=i))                       # NEW row
grass += [gm.dirt_fill(11), gm.dirt_fill(12),
          flip_h(gm.dirt_fill(11)), flip_h(gm.dirt_fill(12))]             # 4 fills
grass += [gm.dirt_fill(13, True), gm.dirt_fill(14, True),
          flip_h(gm.dirt_fill(13, True)), flip_h(gm.dirt_fill(14, True))]
grass += [gm.grass_corner(21, True), gm.grass_corner(22, False),
          flip_h(gm.grass_corner(21, True)), flip_h(gm.grass_corner(22, False))]
grass += [gm.grass_edge_side(31, True), gm.grass_edge_side(32, False),
          gm.grass_surface(99, blades=3), gm.dirt_fill(33)]
gm.build_sheet("mega_grass.png", grass, 8)

snow = []
for i in range(4):
    snow.append(gm.snow_surface(5 + i))
for i in range(4):
    snow.append(snow_surface2(150 + i))
snow += [gm.frost_fill(15), gm.frost_fill(16), flip_h(gm.frost_fill(15)), flip_h(gm.frost_fill(16))]
snow += [gm.frost_fill(17, True), gm.frost_fill(18, True),
         flip_h(gm.frost_fill(17, True)), flip_h(gm.frost_fill(18, True))]
sc_t = gm.frost_fill(23); 
def snow_corner2(seed, tl):
    img = gm.frost_fill(seed)
    for yy in range(5):
        xs = range(0, max(1, S - yy * 2)) if tl else range(min(S - 1, yy * 2), S)
        for xx in xs:
            put(img, xx, yy, gm.SNOW_TOP[2] if yy < 2 else gm.SNOW_TOP[0])
    bottom_shade(img, 0, 3, S - 1, S - 1, None, 20)
    return img
snow += [snow_corner2(23, True), snow_corner2(24, False),
         flip_h(snow_corner2(23, True)), flip_h(snow_corner2(24, False))]
def snow_side2(seed, left):
    img = gm.frost_fill(seed)
    for yy in range(S):
        if left:
            put(img, 0, yy, gm.SNOW_TOP[1]); put(img, 1, yy, gm.SNOW_TOP[0])
        else:
            put(img, S - 1, yy, gm.SNOW_TOP[1]); put(img, S - 2, yy, gm.SNOW_TOP[0])
    return img
snow += [snow_side2(35, True), snow_side2(36, False), gm.snow_surface(51), gm.frost_fill(37)]
gm.build_sheet("mega_snow.png", snow, 8)

sand = []
for i in range(4):
    sand.append(gm.sand_surface(7 + i))
for i in range(4):
    sand.append(sand_surface2(160 + i))
sand += [gm.wetsand_fill(19), gm.wetsand_fill(20), flip_h(gm.wetsand_fill(19)), flip_h(gm.wetsand_fill(20))]
sand += [gm.wetsand_fill(21, True), gm.wetsand_fill(22, True),
         flip_h(gm.wetsand_fill(21, True)), flip_h(gm.wetsand_fill(22, True))]
def sand_corner2(seed, tl):
    img = gm.wetsand_fill(seed)
    for yy in range(5):
        xs = range(0, max(1, S - yy * 2)) if tl else range(min(S - 1, yy * 2), S)
        for xx in xs:
            put(img, xx, yy, gm.SAND_T[2] if yy < 2 else gm.SAND_T[0])
    bottom_shade(img, 0, 3, S - 1, S - 1, None, 20)
    return img
sand += [sand_corner2(25, True), sand_corner2(26, False),
         flip_h(sand_corner2(25, True)), flip_h(sand_corner2(26, False))]
def sand_side2(seed, left):
    img = gm.wetsand_fill(seed)
    for yy in range(S):
        c = gm.SAND_T[0] if yy < 5 else gm.SAND_M
        if left:
            put(img, 0, yy, c); put(img, 1, yy, gm.SAND_T[1])
        else:
            put(img, S - 1, yy, c); put(img, S - 2, yy, gm.SAND_T[1])
    return img
sand += [sand_side2(37, True), sand_side2(38, False), gm.sand_surface(55), gm.wetsand_fill(39)]
gm.build_sheet("mega_sand.png", sand, 8)

# decal contact sheets per world
for world in ("meadow", "snow", "beach"):
    items = [lg for w, n, lg in made if w == world]
    Wtot = sum(i.width + 4 for i in items)
    Htot = max(i.height for i in items)
    sheet = Image.new("RGBA", (Wtot, Htot), (30, 26, 38, 255))
    x = 0
    for i in items:
        sheet.paste(i, (x, 0), i); x += i.width + 4
    sheet.save(os.path.join(OUT, f"decal_sheet_{world}.png"))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(
        os.path.join(OUT, "previews", f"decal_sheet_{world}@2x.png"))
print("ultra ground ok")
