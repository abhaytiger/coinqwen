"""Stage GOLDEN COINS — one hero rotating coin per world, 8-frame spin @32px:
face-on -> edge-on with a travelling specular glint and rim shading.
gold_classic (meadow star-emboss), gold_snow (crystal emboss), gold_beach (sun emboss).
Also a shared big 'mega_gold' 10-frame spin @48 for milestone drops.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from pxlib2 import *

OUT = "/workspace/pixel_art/coins"
PREV = os.path.join(OUT, "previews")
os.makedirs(PREV, exist_ok=True)

GOLDS = {
    "gold_classic": dict(base=(250, 200, 60, 255), hi=(255, 240, 150, 255),
                         lo=(196, 130, 28, 255), edge=(150, 92, 16, 255), emblem="star"),
    "gold_snow":    dict(base=(214, 234, 250, 255), hi=(255, 255, 255, 255),
                         lo=(140, 176, 214, 255), edge=(96, 130, 170, 255), emblem="flake", gold=False),
    "gold_beach":   dict(base=(255, 190, 92, 255), hi=(255, 244, 190, 255),
                         lo=(206, 130, 44, 255), edge=(158, 92, 26, 255), emblem="sun"),
}


def coin_frame(C, f, total=8, R=13):
    S_ = R * 2 + 4
    img = Image.new("RGBA", (S_ * SCALE, S_ * SCALE), (0, 0, 0, 0))
    cx = cy = S_ / 2
    ang = f / total * math.tau
    w = max(0.18, abs(math.cos(ang)))          # horizontal squash = spin
    hgt = 1.0 + 0.06 * math.sin(ang * 2)       # slight elastic bob
    x0, y0 = cx - R * w, cy - R * hgt
    x1, y1 = cx + R * w, cy + R * hgt
    # coin body
    ellipse(img, x0, y0, x1, y1, C["base"])
    # rim ring
    d = ImageDraw.Draw(img)
    d.ellipse([x0 * SCALE, y0 * SCALE, (x1 + 1) * SCALE, (y1 + 1) * SCALE],
              outline=C["edge"], width=SCALE)
    inner = 2.2 * max(w, 0.25)
    d.ellipse([(x0 + inner) * SCALE, (y0 + inner) * SCALE,
               (x1 + 1 - inner) * SCALE, (y1 + 1 - inner) * SCALE],
              outline=C["lo"], width=SCALE)
    # bottom-edge thickness band (3d)
    for xx in range(int(x0) + 2, int(x1) - 1):
        yy = int(y1 - 1.2)
        if alpha_at(img, xx, yy) > 200:
            put(img, xx, yy, C["lo"])
    # travelling specular arc
    sp = (f / total) * math.tau
    for t in range(5):
        a = math.pi * 1.15 + t * 0.16 + (f % total) * 0.10
        rx = cx + (R - 3) * w * math.cos(a)
        ry = cy + (R - 3) * hgt * math.sin(a)
        put(img, int(rx), int(ry), C["hi"])
    # center emblem (only when face is wide enough)
    if w > 0.55:
        em = C["emblem"]
        alpha = int(255 * min(1.0, (w - 0.55) / 0.3))
        col = shade(C["lo"], da=alpha)
        if em == "star":
            pts = []
            for i in range(10):
                rr = 5 if i % 2 == 0 else 2
                aa = -math.pi / 2 + i * math.pi / 5
                pts.append((cx + rr * w * math.cos(aa), cy + rr * math.sin(aa)))
            d.polygon([(p[0] * SCALE, p[1] * SCALE) for p in pts], fill=col)
        elif em == "flake":
            for k in range(3):
                aa = k * math.pi / 3
                line(img, [(int(cx - 5 * w * math.cos(aa)), int(cy - 5 * math.sin(aa))),
                           (int(cx + 5 * w * math.cos(aa)), int(cy + 5 * math.sin(aa)))], col, 1)
            px(img, int(cx), int(cy), shade(C["hi"], da=alpha))
        elif em == "sun":
            ellipse(img, cx - 3 * w, cy - 3, cx + 3 * w, cy + 3, col)
            for k in range(8):
                aa = k * math.tau / 8
                put(img, int(cx + 6 * w * math.cos(aa)), int(cy + 6 * math.sin(aa)), col)
    # sparkle cross at frame 0 & 4
    if f in (0, 4):
        sc = (255, 255, 255, 220)
        rect(img, int(cx + 5 * w), int(cy - 6), int(cx + 5 * w) + 2, int(cy - 6), sc)
        rect(img, int(cx + 5 * w) + 1, int(cy - 7), int(cx + 5 * w) + 1, int(cy - 5), sc)
    return img


for name, C in GOLDS.items():
    frames = [coin_frame(C, f) for f in range(8)]
    sheet = Sheet(8, 32, 32)
    for fr in frames:
        s = fr.resize((fr.width // SCALE, fr.height // SCALE), Image.NEAREST)
        # center into 32 cell
        canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        canvas.paste(s, ((32 - s.width) // 2, (32 - s.height) // 2), s)
        sheet.canvas.paste(canvas, ((sheet.n % 8) * 32, 0), canvas)
        sheet.n += 1
    sheet.save(os.path.join(OUT, f"{name}.png"))
    save_scaled(hframes(frames), os.path.join(PREV, f"{name}@3x.png"), 3)

# mega milestone coin (gold only), 10 frames @48
C = GOLDS["gold_classic"]
frames = [coin_frame(C, f, total=10, R=19) for f in range(10)]
sheet = Sheet(10, 48, 48)
for fr in frames:
    s = fr.resize((fr.width // SCALE, fr.height // SCALE), Image.NEAREST)
    canvas = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    canvas.paste(s, ((48 - s.width) // 2, (48 - s.height) // 2), s)
    sheet.canvas.paste(canvas, ((sheet.n % 10) * 48, 0), canvas)
    sheet.n += 1
sheet.save(os.path.join(OUT, "gold_mega.png"))
save_scaled(hframes(frames), os.path.join(PREV, "gold_mega@2x.png"), 2)
print("golden coins ok")
