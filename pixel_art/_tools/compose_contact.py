"""Compose premium contact sheets for review."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw

ROOT = "/workspace/pixel_art"


def cell(path, maxw=260, pad=10, label=""):
    im = Image.open(path).convert("RGBA")
    s = max(1, min(maxw // max(1, im.width), 4))
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    w, h = im.width, im.height + (14 if label else 0)
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (24, 20, 34, 255))
    d = ImageDraw.Draw(out)
    ck = Image.new("RGBA", (im.width, im.height), (40, 36, 52, 255))
    dc = ImageDraw.Draw(ck)
    for y in range(0, im.height, 8):
        for x in range(0, im.width, 8):
            if (x // 8 + y // 8) % 2:
                dc.rectangle([x, y, x + 7, y + 7], fill=(52, 46, 66, 255))
    out.paste(ck, (pad, pad), ck)
    out.paste(im, (pad, pad), im)
    if label:
        d.text((pad + 2, im.height + pad + 2), label, fill=(230, 220, 200, 255))
    return out


def row(items, out_path, cols=None):
    ims = []
    for p, lab in items:
        if not os.path.exists(p):
            print("missing", p); continue
        ims.append(cell(p, label=lab))
    if not ims:
        return
    cols = cols or len(ims)
    rows = (len(ims) + cols - 1) // cols
    cw = max(i.width for i in ims); ch = max(i.height for i in ims)
    canvas = Image.new("RGBA", (cw * cols, ch * rows), (24, 20, 34, 255))
    for idx, i in enumerate(ims):
        canvas.paste(i, ((idx % cols) * cw, (idx // cols) * ch))
    canvas.save(out_path)
    print("wrote", out_path)


C = f"{ROOT}/characters"; E = f"{ROOT}/enemies"; G = f"{ROOT}/ground"; CO = f"{ROOT}/coins"
row([(f"{C}/hero_default.png", "hero default 8f"), (f"{C}/hero_snow.png", "hero snow"),
     (f"{C}/hero_beach.png", "hero beach"), (f"{C}/hero_penguin.png", "penguin"),
     (f"{C}/hero_crab.png", "crab"), (f"{C}/hero_bunny.png", "bunny"),
     (f"{C}/hero_fox.png", "fox"), (f"{C}/hero_cat.png", "cat"), (f"{C}/hero_owl.png", "owl")],
    f"{C}/CONTACT_heroes_v2.png", cols=3)
row([(f"{E}/jelly_green.png", "jelly green 12f"), (f"{E}/jelly_ice.png", "jelly ice"),
     (f"{E}/jelly_ember.png", "jelly ember")], f"{E}/CONTACT_enemies_v2.png", cols=3)
row([(f"{G}/mega_grass.png", "mega grass 8x4"), (f"{G}/mega_snow.png", "mega snow"),
     (f"{G}/mega_sand.png", "mega sand"), (f"{G}/water_river.png", "river/lake/shallow/fall x4f"),
     (f"{G}/water_deep.png", "deep sea"), (f"{G}/cliff_grass.png", "cliff set")],
    f"{G}/CONTACT_ground_v2.png", cols=2)
row([(f"{CO}/gold_classic.png", "gold classic 8f spin"), (f"{CO}/gold_snow.png", "gold snow"),
     (f"{CO}/gold_beach.png", "gold beach"), (f"{CO}/gold_mega.png", "mega gold 10f")],
    f"{CO}/CONTACT_gold_v2.png", cols=2)
