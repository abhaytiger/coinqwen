"""UI kit, parallax backgrounds, menu background, weather particles."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

BASE = "/workspace/pixel_art"
UI = os.path.join(BASE, "ui"); BG = os.path.join(BASE, "backgrounds"); WE = os.path.join(BASE, "weather")
PREV = os.path.join(UI, "previews")
for d in (UI, BG, WE, PREV):
    os.makedirs(d, exist_ok=True)

GOLD = (240, 200, 90); GOLD_D = (176, 130, 40); CREAM = (250, 240, 214)
PANEL = (58, 66, 96, 235); PANEL_L = (86, 96, 132, 255)

# ---------------------------------------------------------------- nine-patch panel 48x48
def panel_patch():
    img = new(16, 16)
    rect(img, 0, 0, 15, 15, PANEL)
    rect(img, 1, 1, 14, 14, shade(PANEL, 14, 14, 22))
    # border + corner rivets drawn only around edge
    rect(img, 0, 0, 15, 0, GOLD); rect(img, 0, 15, 15, 15, GOLD_D)
    rect(img, 0, 0, 0, 15, GOLD); rect(img, 15, 0, 15, 15, GOLD_D)
    return img

np_ = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
p = panel_patch()
corners = [p.crop((0, 0, 6, 6)), p.crop((10, 0, 16, 6)), p.crop((0, 10, 6, 16)), p.crop((10, 10, 16, 16))]
np_.paste(corners[0], (0, 0)); np_.paste(corners[1], (42, 0))
np_.paste(corners[2], (0, 42)); np_.paste(corners[3], (42, 42))
np_.paste(p.crop((6, 0, 10, 6)).resize((32, 6), Image.NEAREST), (8, 0))     # top
np_.paste(p.crop((6, 10, 10, 16)).resize((32, 6), Image.NEAREST), (8, 42))  # bottom
np_.paste(p.crop((0, 6, 6, 10)).resize((6, 32), Image.NEAREST), (0, 8))     # left
np_.paste(p.crop((10, 6, 16, 10)).resize((6, 32), Image.NEAREST), (42, 8))  # right
np_.paste(p.crop((6, 6, 10, 10)).resize((32, 32), Image.NEAREST), (8, 8))   # center
np_.save(os.path.join(UI, "panel_ninepatch.png"))
save_scaled(np_, os.path.join(PREV, "panel_ninepatch@2x.png"), 2)

# ---------------------------------------------------------------- buttons
def button(col, label="Aa"):
    img = new(48, 20)
    rect(img, 2, 2, 46, 17, col)
    rect(img, 2, 2, 46, 3, lighter(col, 45))
    rect(img, 2, 15, 46, 17, darker(col, 45))
    rect(img, 1, 4, 1, 15, darker(col, 60)); rect(img, 46, 4, 46, 15, darker(col, 60))
    rect(img, 2, 1, 45, 1, lighter(col, 70))
    # simple 5x7-ish glyph block centered
    rect(img, 21, 7, 26, 12, (255, 255, 255, 210))
    rect(img, 22, 8, 25, 11, col)
    px(img, 23, 9, (255, 255, 255, 230)); px(img, 24, 9, (255, 255, 255, 230))
    return img

save(button((86, 168, 96)), os.path.join(UI, "btn_green.png"), 1)
save(button((224, 96, 84)), os.path.join(UI, "btn_red.png"), 1)
save(button((96, 130, 210)), os.path.join(UI, "btn_blue.png"), 1)

# ---------------------------------------------------------------- HUD coin counter bg
def hud_pill():
    img = new(64, 20)
    rect(img, 2, 2, 62, 18, (30, 34, 52, 220))
    rect(img, 3, 3, 61, 17, (44, 50, 74, 230))
    rect(img, 2, 2, 62, 2, (90, 100, 140, 255))
    rect(img, 2, 2, 2, 18, (90, 100, 140, 255))
    ellipse(img, 5, 4, 16, 17, (140, 90, 20, 255))
    ellipse(img, 6, 5, 15, 16, (250, 204, 80, 255))
    ellipse(img, 7, 6, 10, 8, (255, 240, 170, 255))
    return img

hp = hud_pill()
save(hp, os.path.join(UI, "hud_coin_counter.png"), 1)
save_scaled(hp, os.path.join(PREV, "hud_coin_counter@2x.png"), 2)

# ---------------------------------------------------------------- hearts row
def heart_small(col=(232, 76, 92)):
    img = new(16, 16)
    dk = darker(col, 45)
    for x0, x1, y in [(4, 6, 4), (9, 11, 4), (3, 12, 5), (3, 12, 6), (3, 12, 7),
                      (4, 11, 8), (5, 10, 9), (6, 9, 10), (7, 8, 11)]:
        rect(img, x0, y, x1, y, col)
    px(img, 4, 5, lighter(col, 60)); px(img, 5, 5, lighter(col, 60))
    rect(img, 3, 7, 4, 7, dk); rect(img, 4, 8, 5, 8, dk)
    return img

row = Image.new("RGBA", (16 * 3, 16), (0, 0, 0, 0))
h = heart_small()
row.paste(h, (0, 0)); row.paste(h, (16, 0))
row.paste(heart_small((90, 90, 110)), (32, 0))       # empty heart
row.save(os.path.join(UI, "hearts_row.png"))
save_scaled(row, os.path.join(PREV, "hearts_row@4x.png"), 4)

# ---------------------------------------------------------------- milestone progress bar
def bar():
    img = new(96, 16)
    rect(img, 0, 0, 95, 15, (30, 34, 52, 255))
    rect(img, 1, 1, 94, 14, (52, 58, 84, 255))
    rect(img, 2, 2, 60, 13, (96, 200, 110, 255))     # fill
    rect(img, 2, 2, 60, 3, (160, 236, 160, 255))
    rect(img, 58, 2, 60, 13, (220, 255, 220, 255))   # leading edge glow
    for x in range(4, 96, 12): rect(img, x, 0, x, 15, (30, 34, 52, 255))  # notches
    return img

b = bar()
save(b, os.path.join(UI, "progress_bar.png"), 1)
save_scaled(b, os.path.join(PREV, "progress_bar@3x.png"), 3)

# ---------------------------------------------------------------- skin icons 24x24
def icon_circle(face_fn):
    img = new(24, 24)
    ellipse(img, 2, 2, 21, 21, (36, 40, 60, 255))
    ellipse(img, 3, 3, 20, 20, (70, 78, 110, 255))
    face_fn(img)
    return outline(img, (20, 22, 34, 255))

def ic_default(img):
    ellipse(img, 7, 6, 16, 15, (98, 148, 235))       # hood head
    rect(img, 9, 9, 14, 13, (241, 194, 154))
    px(img, 11, 11, (30, 30, 40)); px(img, 13, 11, (30, 30, 40))
def ic_snow(img):
    ellipse(img, 7, 6, 16, 15, (228, 238, 248))
    rect(img, 9, 9, 14, 13, (241, 194, 154))
    rect(img, 8, 4, 15, 6, (200, 220, 238)); rect(img, 7, 13, 16, 14, (226, 84, 84))
def ic_beach(img):
    ellipse(img, 7, 6, 16, 15, (255, 200, 92))       # sun hat
    rect(img, 9, 9, 14, 13, (198, 132, 92))
    rect(img, 9, 10, 14, 11, (30, 30, 38))           # shades
    rect(img, 5, 5, 18, 6, (250, 140, 70))

for name, fn in (("default", ic_default), ("snow", ic_snow), ("beach", ic_beach)):
    i = icon_circle(fn)
    save(i, os.path.join(UI, f"icon_skin_{name}.png"))
    save_scaled(i, os.path.join(PREV, f"icon_skin_{name}@4x.png"), 4)

def ic_lock(img):
    rect(img, 8, 10, 15, 17, (150, 150, 165))
    rect(img, 9, 11, 14, 12, (190, 190, 205))
    line(img, [(10, 10), (10, 7), (13, 7), (13, 10)], (120, 120, 138), 1)
    px(img, 11, 13, (60, 60, 75)); px(img, 12, 14, (60, 60, 75))
save(icon_circle(ic_lock), os.path.join(UI, "icon_skin_locked.png"))

# ---------------------------------------------------------------- fonts preview (A-Z 0-9)
def glyph(ch):
    # 5x7 bitmap font subset
    F = {
     'A':["01110","10001","10001","11111","10001","10001","10001"],
     'B':["11110","10001","10001","11110","10001","10001","11110"],
     'C':["01110","10001","10000","10000","10000","10001","01110"],
     'D':["11110","10001","10001","10001","10001","10001","11110"],
     'E':["11111","10000","10000","11110","10000","10000","11111"],
     'F':["11111","10000","10000","11110","10000","10000","10000"],
     'G':["01110","10001","10000","10111","10001","10001","01110"],
     'H':["10001","10001","10001","11111","10001","10001","10001"],
     'I':["11111","00100","00100","00100","00100","00100","11111"],
     'J':["00111","00010","00010","00010","00010","10010","01100"],
     'K':["10001","10010","10100","11000","10100","10010","10001"],
     'L':["10000","10000","10000","10000","10000","10000","11111"],
     'M':["10001","11011","10101","10101","10001","10001","10001"],
     'N':["10001","11001","10101","10011","10001","10001","10001"],
     'O':["01110","10001","10001","10001","10001","10001","01110"],
     'P':["11110","10001","10001","11110","10000","10000","10000"],
     'Q':["01110","10001","10001","10001","10101","10010","01101"],
     'R':["11110","10001","10001","11110","10100","10010","10001"],
     'S':["01111","10000","10000","01110","00001","00001","11110"],
     'T':["11111","00100","00100","00100","00100","00100","00100"],
     'U':["10001","10001","10001","10001","10001","10001","01110"],
     'V':["10001","10001","10001","10001","10001","01010","00100"],
     'W':["10001","10001","10001","10101","10101","11011","10001"],
     'X':["10001","10001","01010","00100","01010","10001","10001"],
     'Y':["10001","10001","01010","00100","00100","00100","00100"],
     'Z':["11111","00001","00010","00100","01000","10000","11111"],
     '0':["01110","10011","10101","10101","10101","11001","01110"],
     '1':["00100","01100","00100","00100","00100","00100","01110"],
     '2':["01110","10001","00001","00010","00100","01000","11111"],
     '3':["11110","00001","00001","01110","00001","00001","11110"],
     '4':["10010","10010","10010","11111","00010","00010","00010"],
     '5':["11111","10000","11110","00001","00001","10001","01110"],
     '6':["01110","10000","10000","11110","10001","10001","01110"],
     '7':["11111","00001","00010","00100","01000","01000","01000"],
     '8':["01110","10001","10001","01110","10001","10001","01110"],
     '9':["01110","10001","10001","01111","00001","00001","01110"],
    }.get(ch)
    return F

CH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
cols = len(CH); sheet = Image.new("RGBA", (cols * 8, 10), (0, 0, 0, 0))
d = ImageDraw.Draw(sheet)
for i, ch in enumerate(CH):
    g = glyph(ch)
    for r, row in enumerate(g):
        for c, bit in enumerate(row):
            if bit == "1":
                d.rectangle([i * 8 + c, r, i * 8 + c, r], fill=(250, 240, 214, 255))
sheet.save(os.path.join(UI, "font_retro_sheet.png"))
save_scaled(sheet, os.path.join(PREV, "font_retro_sheet@3x.png"), 3)

# ---------------------------------------------------------------- parallax skies 320x180
def sky_gradient(w, h, stops):
    img = Image.new("RGB", (w, h))
    px_ = img.load()
    for y in range(h):
        t = y / (h - 1)
        # find segment
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]; t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0 or 1)
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                break
        for x in range(w):
            px_[x, y] = col
    return img.convert("RGBA")

def stars(img, n, seed):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.randrange(img.width); y = rnd.randrange(img.height // 2)
        b = rnd.choice([(255, 255, 255, 200), (255, 255, 255, 120), (200, 220, 255, 160)])
        img.putpixel((x, y), b)

# classic meadow day sky
sky = sky_gradient(320, 180, [(0, (116, 196, 240)), (.7, (176, 226, 248)), (1, (222, 244, 250))])
def cloud(x, y, s=1.0):
    for dx, dy, wdt, ht in [(0, 4, 26, 10), (6, 0, 16, 10), (14, 2, 18, 9), (24, 5, 12, 8)]:
        e = Image.new("RGBA", (wdt * 2, ht * 2), (0, 0, 0, 0))
        dd = ImageDraw.Draw(e)
        dd.ellipse([0, 0, wdt * 2 - 1, ht * 2 - 1], fill=(252, 252, 255, 235))
        e = e.resize((int(wdt * s), int(ht * s)))
        base = Image.new("RGBA", sky.size, (0, 0, 0, 0))
        base.paste(e, (x + int(dx * s), y + int(dy * s)))
        sky.alpha_composite(base)
cloud(40, 30); cloud(180, 55, .8); cloud(260, 20, .6)
# rolling hills far layer
d = ImageDraw.Draw(sky)
d.ellipse([-80, 130, 200, 210], fill=(150, 200, 160, 255))
d.ellipse([120, 140, 380, 215], fill=(130, 188, 148, 255))
sky.save(os.path.join(BG, "parallax_classic_far.png"))

# snow night sky with aurora
sky = sky_gradient(320, 180, [(0, (16, 22, 52)), (.6, (40, 58, 108)), (1, (120, 150, 190))])
stars(sky, 90, 11)
d = ImageDraw.Draw(sky)
for i in range(3):
    pts = []
    for x in range(0, 321, 20):
        pts.append((x, 40 + i * 12 + int(10 * math.sin(x / 40 + i))))
    d.line(pts, fill=(110, 230, 190, 60), width=8)
    d.line(pts, fill=(140, 250, 210, 90), width=3)
d.ellipse([-60, 150, 160, 220], fill=(226, 238, 250, 255))      # snow hills
d.ellipse([140, 158, 400, 224], fill=(208, 226, 244, 255))
sky.save(os.path.join(BG, "parallax_snow_far.png"))

# beach sunset sky
import math
sky = sky_gradient(320, 180, [(0, (48, 60, 120)), (.35, (226, 120, 90)), (.62, (250, 190, 110)), (1, (254, 226, 170))])
d = ImageDraw.Draw(sky)
d.ellipse([128, 96, 192, 160], fill=(255, 236, 170, 255))       # sun
d.ellipse([136, 104, 184, 152], fill=(255, 246, 210, 255))
for i in range(4):                                              # cloud bands
    y = 60 + i * 14
    d.rounded_rectangle([20 + i * 40, y, 140 + i * 44, y + 6], 3, fill=(250, 180, 150, 140))
d.rectangle([0, 150, 320, 180], fill=(64, 130, 170, 255))       # sea band
for x in range(0, 320, 14):
    d.line([(x, 154), (x + 8, 154)], fill=(250, 210, 150, 120), width=2)
sky.save(os.path.join(BG, "parallax_beach_far.png"))

# menu backdrop 640x360
menu = sky_gradient(640, 360, [(0, (26, 30, 70)), (.5, (92, 70, 130)), (.8, (236, 140, 96)), (1, (252, 208, 140))])
d = ImageDraw.Draw(menu)
stars(menu, 160, 21)
d.ellipse([268, 210, 372, 314], fill=(255, 240, 190, 255))      # big sun
d.ellipse([280, 222, 360, 302], fill=(255, 250, 226, 255))
for pts, col in [([(-40, 360), (140, 240), (320, 360)], (40, 44, 84, 255)),
                 ([(260, 360), (460, 230), (700, 360)], (48, 52, 96, 255))]:
    d.polygon(pts, fill=col)
d.rectangle([0, 330, 640, 360], fill=(28, 30, 58, 255))
# floating coins
for cx, cy, r in [(90, 120, 10), (540, 90, 8), (480, 200, 12), (150, 220, 7), (600, 260, 9)]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(140, 90, 20, 255))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=(250, 204, 80, 255))
    d.ellipse([cx - r + 3, cy - r + 3, cx - 1, cy - 1], fill=(255, 240, 170, 255))
menu.save(os.path.join(BG, "menu_bg.png"))
save_scaled(menu.resize((320, 180), Image.NEAREST), os.path.join(PREV, "menu_bg@2x.png"), 2)

# ---------------------------------------------------------------- weather 8x8 sprites
def flake(size=8, kind="snow"):
    img = new(8, 8)
    c = (255, 255, 255, 255) if kind == "snow" else (170, 210, 240, 255)
    cx = 3
    for k in range(3):
        px(img, cx + k, 3 + k // 2, c); px(img, cx - k, 3 + k // 2, c)
        px(img, cx + k, 4 - k // 2, c); px(img, cx - k, 4 - k // 2, c)
    px(img, cx, 1, c); px(img, cx, 6, c)
    return img

save(flake(), os.path.join(WE, "snowflake.png"))
save(flake(kind="ice"), os.path.join(WE, "snowflake_big.png"))
save_scaled(flake(), os.path.join(WE, "previews", "snowflake@8x.png"), 8) if False else None

def bubble():
    img = new(8, 8)
    ellipse(img, 1, 1, 6, 6, (180, 225, 245, 120))
    ellipse(img, 2, 2, 5, 5, (220, 245, 255, 60))
    px(img, 2, 2, (255, 255, 255, 220)); px(img, 3, 2, (255, 255, 255, 140))
    return img

save(bubble(), os.path.join(WE, "bubble.png"))

def leaf():
    img = new(8, 8)
    ellipse(img, 1, 2, 6, 5, (120, 180, 80, 255))
    line(img, [(1, 4), (6, 3)], (80, 130, 60, 255), 1)
    px(img, 6, 3, (80, 130, 60, 255))
    return img

save(leaf(), os.path.join(WE, "leaf.png"))
print("ui/bg ok")
