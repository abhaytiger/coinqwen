"""HIGH-DETAIL ROCKS v2 — geological rock sets per world, pixel-perfect.

Drawn at 8x supersample with numpy fBm mineral texture, strata banding,
crack networks, moss/lichen/snow-cap/wet-sheen overlays, 3-tone lighting
(top-left sun), then downsampled with box averaging so every logical pixel
is a true average of 64 sub-samples => extremely dense detail at game res,
plus an HD render kept at full resolution for close-up props / cinematics.

props/rock_large.png / rock_small.png  -> upgraded hero boulders (meadow)
worlds/<world>/rock_*.png              -> 6 unique rocks per world (logical)
worlds/<world>/rocks_hd/*.png          -> HD versions (512-ish px)
worlds/<world>/rock_set.png            -> contact sheet @2x preview
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageFilter

ROOT = "/workspace/pixel_art"
SS = 8  # supersample


# simpler robust value-noise fbm (bilinear upsample of random lattices)
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
        layer = top * (1 - fy[:, None]) + bot * fy[:, None]
        acc += layer * amp; tot += amp; amp *= 0.52; cell = min(size, cell * 2 + 3)
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-9)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a * (1 - t) + b * t


def blob_mask(size, seed, lumps, base_r=0.34, flatten=0.78):
    """organic boulder silhouette: union of offset ellipses + noise wobble"""
    rnd = random.Random(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    u = (xx / (size - 1) - .5); v = (yy / (size - 1) - .5) / flatten
    m = np.zeros((size, size))
    cx, cy = .5, .55
    lobes = [(cx, cy, base_r)] + [(cx + dx, cy + dy, r) for dx, dy, r in lumps]
    for lx, ly, lr in lobes:
        d = np.sqrt((u - (lx - .5)) ** 2 + ((v - (ly - .55)) * flatten) ** 2)
        m = np.maximum(m, smoothstep(lr + 0.02, lr - 0.02, d))
    wob = vn(seed + 5, size) - 0.5
    m = np.clip(m + wob * 0.22, 0, 1)
    return m


def rock_image(pal, seed, lumps, strata_ang=0.0, feature=None, size_log=48):
    S = size_log * SS
    mask = blob_mask(S, seed, lumps)
    n1 = vn(seed + 11, S); n2 = vn(seed + 22, S); n3 = vn(seed + 33, S)
    base = np.array(pal["base"], float)
    hi = np.array(pal["hi"], float); lo = np.array(pal["lo"], float)
    dark = np.array(pal["dark"], float)
    # mineral grain: two noise octaves mixed through palette
    grain = mix(n1, n2, 0.5)
    base3 = base[:3]; hi3 = hi[:3]; lo3 = lo[:3]; dark3 = dark[:3]
    col = np.repeat(base3[None, None, :], S, 0).repeat(S, 1).astype(float)
    col = mix(col, lo3[None, None, :], ((1 - grain) * 0.55)[..., None])
    col = mix(col, hi3[None, None, :], (smoothstep(0.62, 0.95, n2) * 0.6)[..., None])
    # strata bands (sedimentary look) warped by noise
    yy, xx = np.mgrid[0:S, 0:S]
    c, s = math.cos(strata_ang), math.sin(strata_ang)
    band = ((xx * c + yy * s) / S * 7.0 + vn(seed + 44, S) * 2.2) % 1.0
    bands = smoothstep(0.45, 0.5, band) * smoothstep(0.62, 0.57, band)
    col = mix(col, dark3[None, None, :], bands[..., None] * 0.5)
    # crack network: thin ridges where noise crosses threshold
    cr = vn(seed + 55, S)
    ridge = smoothstep(0.485, 0.5, cr) * smoothstep(0.53, 0.515, cr)
    col = mix(col, dark3[None, None, :], ridge[..., None] * 0.85)
    # chip highlights along crack edges (upper side catches light)
    chip = np.roll(ridge, (1, 0), (0, 1)) - ridge
    col = mix(col, hi3[None, None, :], np.clip(chip, 0, 1)[..., None] * 0.5)
    # spherical-ish shading: light from top-left
    lx = (xx / S - 0.28); ly = (yy / S - 0.30)
    diff = 1.0 - np.clip(np.sqrt(lx ** 2 + ly ** 2) * 1.35, 0, 1)
    col = mix(col, dark3[None, None, :], ((1 - diff) * 0.42)[..., None])
    col = mix(col, hi3[None, None, :], (smoothstep(0.72, 0.98, diff) * 0.5)[..., None])
    # specular dot near top-left rim
    spec = np.exp(-(((xx - S * 0.3) ** 2 + (yy - S * 0.26) ** 2)) / (2 * (S * 0.05) ** 2))
    col = mix(col, np.array(pal.get("spec", (255, 255, 255))[:3], float)[None, None, :],
              spec[..., None] * 0.75)
    # contact shadow under belly
    amb = smoothstep(0.82, 0.55, yy / S)
    col = mix(col, dark3[None, None, :], amb[..., None] * 0.25)
    # ---- world features -------------------------------------------------
    if feature == "moss":
        mm = np.clip(vn(seed + 66, S) * 1.5 - 0.55, 0, 1)
        # moss prefers upward-facing (top half) surfaces
        mm *= smoothstep(0.65, 0.25, yy / S)
        moss = np.array(pal["moss"][:3], float)
        moss2 = np.array(pal["moss2"][:3], float)
        mc = mix(moss[None, None, :], moss2[None, None, :], n3[..., None])
        col = mix(col, mc, np.clip(mm, 0, 1)[..., None] * 0.9)
        # moss speckle dots
        dots = smoothstep(0.86, 0.9, vn(seed + 67, S)) * (mask > 0)
        col = mix(col, moss2[None, None, :], dots[..., None] * 0.8)
    elif feature == "snowcap":
        sm = vn(seed + 66, S)
        cap = smoothstep(0.52, 0.30, yy / S) * smoothstep(0.35, 0.55, sm + 0.25 * (1 - yy / S))
        snow = np.array((250, 252, 255), float)
        bluish = np.array((208, 224, 246), float)
        sc = mix(bluish[None, None, :], snow[None, None, :], smoothstep(0.2, 0.8, 1 - yy / S)[..., None])
        col = mix(col, sc, np.clip(cap, 0, 1)[..., None])
        # icicle drips on lower rim
        drip = (vn(seed + 68, S) > 0.86) & (yy / S > 0.55)
        col = mix(col, np.array((190, 222, 250), float)[None, None, :], drip[..., None] * 0.7)
    elif feature == "wet":
        sheen = smoothstep(0.55, 0.95, vn(seed + 66, S) * (1 - yy / S))
        col = mix(col, np.array((255, 255, 255), float)[None, None, :], sheen[..., None] * 0.28)
        col *= mix(np.ones((S, S, 3)), np.array((0.82, 0.86, 0.95))[None, None, :], 0.6)
        # barnacles
        bz = vn(seed + 69, S)
        barn = smoothstep(0.9, 0.93, bz) * (yy / S > 0.45)
        bc = np.array((236, 226, 208), float)
        col = mix(col, bc[None, None, :], barn[..., None])
        col = mix(col, np.array((120, 100, 80), float)[None, None, :],
                  (np.roll(barn, 1, 0) * 0.6)[..., None])
    elif feature == "lava":
        glow = smoothstep(0.55, 0.75, vn(seed + 70, S))
        col = mix(col, np.array(pal["glow"], float)[None, None, :], glow[..., None] * 0.5)
    # alpha + edge AO
    a = np.clip(mask * 255, 0, 255)
    edge_dark = smoothstep(0.9, 0.55, mask)  # just inside silhouette
    col = mix(col, dark3[None, None, :], (edge_dark * 0.35)[..., None] * (mask > 0)[..., None])
    rgba = np.dstack([np.clip(col, 0, 255), a]).astype(np.uint8)
    hd = Image.fromarray(rgba)
    # ink outline at logical res for style consistency
    lg = hd.resize((size_log, size_log), Image.BOX)
    return hd, lg


def add_outline(lg, ink=(40, 30, 46, 255)):
    from PIL import ImageDraw
    a = lg.split()[3].point(lambda v: 255 if v > 60 else 0)
    out = Image.new("RGBA", (lg.width + 2, lg.height + 2), (0, 0, 0, 0))
    solid = Image.new("RGBA", out.size, ink)
    ring = Image.new("L", out.size, 0)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        sh = Image.new("L", a.size, 0); sh.paste(a, (dx, dy)); 
        tmp = Image.new("L", out.size, 0); tmp.paste(sh, (1, 1))
        ring = Image.fromarray(np.maximum(np.array(ring), np.array(tmp)), "L")
    out = Image.composite(solid, out, ring)
    out.paste(lg, (1, 1), lg)
    return out.crop((0, 0, lg.width, lg.height))


SETS = {
    "classic_meadow": dict(pal=dict(base=(148, 142, 138, 255), hi=(196, 192, 186, 255),
                                    lo=(108, 102, 100, 255), dark=(70, 64, 66, 255),
                                    moss=(96, 158, 82, 255), moss2=(150, 196, 96, 255)),
                           feature="moss",
                           rocks=[("rock_granite", 40, []), ("rock_mossy", 44, [(-.12, -.08, .12)]),
                                  ("rock_pebble_l", 32, [(.1, -.05, .1)]), ("rock_pebble_s", 24, []),
                                  ("rock_stump_base", 48, [(-.14, -.02, .1), (.12, -.06, .09)]),
                                  ("rock_boulder_big", 56, [(0, -.12, .13)])]),
    "snow_town": dict(pal=dict(base=(158, 168, 186, 255), hi=(214, 226, 240, 255),
                               lo=(112, 124, 148, 255), dark=(72, 82, 104, 255)),
                      feature="snowcap",
                      rocks=[("rock_frost", 60, []), ("rock_icy_l", 44, [(-.1, -.06, .11)]),
                             ("rock_icy_s", 28, []), ("rock_snowboulder", 56, [(0, -.1, .12)]),
                             ("rock_shard", 36, [(.12, -.08, .08)]), ("rock_driftstone", 48, [])]),
    "beach": dict(pal=dict(base=(150, 130, 116, 255), hi=(206, 184, 160, 255),
                           lo=(104, 86, 78, 255), dark=(60, 46, 42, 255),
                           spec=(255, 250, 235, 255)),
                  feature="wet",
                  rocks=[("rock_wet", 40, []), ("rock_barnacle", 48, [(-.12, -.05, .1)]),
                         ("rock_coral_stone", 32, []), ("rock_smooth_pebble", 24, []),
                         ("rock_reef_big", 56, [(0, -.1, .12), (.14, .02, .08)]),
                         ("rock_tidepool_rim", 48, [])]),
}

for world, cfg in SETS.items():
    wd = os.path.join(ROOT, "worlds", world)
    hdd = os.path.join(wd, "rocks_hd")
    pv = os.path.join(wd, "previews")
    for d in (wd, hdd, pv):
        os.makedirs(d, exist_ok=True)
    sheet_imgs = []
    for name, sz, lumps in cfg["rocks"]:
        hd, lg = rock_image(cfg["pal"], sz, lumps, strata_ang=random.Random(sz).uniform(-0.4, 0.4),
                            feature=cfg["feature"], size_log=sz)
        hd.save(os.path.join(hdd, f"{name}_hd.png"))
        add_outline(lg).save(os.path.join(wd, f"{name}.png"))
        sheet_imgs.append(add_outline(lg))
        print(world, name, sz)

# upgrade legacy shared props with the new meadow hero rocks
mw = SETS["classic_meadow"]
hd, lg = rock_image(mw["pal"], 44, [(-.12, -.08, .12)], feature="moss", size_log=24)
add_outline(lg).save(os.path.join(ROOT, "props", "rock_small.png"))
hd, lg = rock_image(mw["pal"], 40, [(0, -.12, .13), (-.12, -.04, .09)], feature="moss", size_log=24)
add_outline(lg).save(os.path.join(ROOT, "props", "rock_large.png"))
print("rocks HD ok")
