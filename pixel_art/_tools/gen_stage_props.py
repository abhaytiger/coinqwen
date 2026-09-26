"""Stage-dressing props for all three worlds — cute & happening.
Meadow: hut, fence, mushroom house, lantern, hay bale, cart, well, mailbox, butterfly(4f)
Snow:   igloo (lit+dark), cabin w/ chimney smoke, snow globe, candle, sled, frozen bush,
        snow-pine variant, stocking sign, penguin friend (idle 2f + wave 2f)
Beach:  lifeguard tower, tiki torch, surfboard, sandcastle, buoy, seaweed, cooler box,
        hammock palm (tall), flamingo floatie
Each sprite saved 1x into its world folder + @3x preview."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

MEAD = "/workspace/pixel_art/worlds/classic_meadow"
SNOW = "/workspace/pixel_art/worlds/snow_town"
BEACH = "/workspace/pixel_art/worlds/beach"
for d in (MEAD, SNOW, BEACH):
    os.makedirs(os.path.join(d, "previews"), exist_ok=True)


def blank(w=32, h=32):
    return Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0))


def save1(img, folder, name, prev=None):
    small = img.resize((img.width // SCALE, img.height // SCALE), Image.NEAREST)
    small.save(os.path.join(folder, name + ".png"))
    save_scaled(img, os.path.join(folder, "previews", name + (prev or "@3x.png")), 3)


WALL = (222, 190, 140); WOOD = (150, 104, 62); WOOD_D = (108, 72, 42)
ROOF = (196, 84, 66); ROOF_D = (150, 58, 48); GLASS = (150, 210, 235)


# ================================================================== MEADOW
def hut():
    img = blank(48, 40)
    # walls
    rect(img, 6, 16, 41, 37, WALL)
    noise(img, 6, 16, 41, 37, [(204, 172, 124)], 0.08, seed=3)
    # timber frame
    for x in (6, 41):
        rect(img, x, 16, x + 1, 37, WOOD_D)
    rect(img, 6, 16, 41, 17, WOOD_D)
    # roof (stepped triangle)
    for i in range(11):
        rect(img, 3 + i, 5 + i, 44 - i, 6 + i, ROOF if i % 2 == 0 else ROOF_D)
    rect(img, 2, 4, 45, 5, ROOF_D)
    # door
    rect(img, 20, 24, 27, 37, WOOD); rect(img, 20, 24, 27, 24, WOOD_D)
    px(img, 26, 31, (60, 44, 30))
    # windows with warm glow
    for wx in (10, 33):
        rect(img, wx, 22, wx + 5, 27, WOOD_D)
        rect(img, wx + 1, 23, wx + 4, 26, GLASS)
        px(img, wx + 2, 24, (255, 240, 180)); px(img, wx + 3, 25, (255, 240, 180))
    # chimney + smoke puffs
    rect(img, 34, 0, 38, 8, (120, 96, 84))
    ellipse(img, 33, 6, 39, 8, (96, 76, 66))
    for sx, sy, r in ((40, 0, 2), (43, 2, 1)):
        ellipse(img, sx, sy, sx + r * 2, sy + r * 2, (235, 235, 240, 200))
    return outline(img)


def fence():
    img = blank(48, 20)
    for px_ in (2, 16, 30, 44):
        rect(img, px_, 2, px_ + 3, 17, WOOD)
        rect(img, px_, 2, px_ + 3, 3, WOOD_D)
        px(img, px_ + 1, 1, WOOD_D); px(img, px_ + 2, 1, WOOD_D)
    rect(img, 0, 6, 47, 8, lighter(WOOD, 18))
    rect(img, 0, 12, 47, 14, WOOD)
    rect(img, 0, 14, 47, 14, WOOD_D)
    return outline(img)


def mush_house():
    img = blank(32, 36)
    rect(img, 11, 18, 20, 33, (240, 224, 190))       # stem/walls
    noise(img, 11, 18, 20, 33, [(216, 198, 166)], 0.15, 8)
    ellipse(img, 2, 4, 29, 20, (222, 74, 66))         # cap
    ellipse(img, 4, 4, 27, 12, (238, 106, 92))
    for cx, cy in ((7, 9), (15, 6), (23, 10), (11, 14), (20, 15)):
        ellipse(img, cx, cy, cx + 3, cy + 2, (252, 240, 220))
    rect(img, 14, 24, 19, 33, WOOD_D)                 # round-ish door
    ellipse(img, 14, 22, 19, 26, WOOD_D)
    px(img, 18, 29, (240, 200, 120))
    return outline(img)


def lantern():
    img = blank(16, 28)
    rect(img, 7, 2, 8, 24, WOOD_D)                    # post
    rect(img, 4, 0, 11, 1, (70, 56, 44))
    rect(img, 3, 1, 12, 10, (90, 72, 54))             # lamp cage
    rect(img, 5, 3, 10, 8, (255, 214, 110))
    px(img, 7, 4, (255, 246, 200)); px(img, 8, 6, (255, 246, 200))
    rect(img, 3, 10, 12, 11, (70, 56, 44))
    return outline(img)


def hay_bale():
    img = blank(24, 18)
    ellipse(img, 0, 2, 23, 17, (222, 178, 92))
    ellipse(img, 2, 4, 21, 15, (238, 198, 112))
    for yy in (6, 9, 12):
        line(img, [(3, yy), (21, yy)], (200, 156, 78), 1)
    rect(img, 10, 2, 13, 17, (188, 146, 70))          # twine band
    rect(img, 10, 2, 13, 17, (160, 120, 60), )
    return outline(img)


def cart():
    img = blank(40, 26)
    rect(img, 4, 6, 34, 16, WOOD)                     # tub
    rect(img, 4, 6, 34, 7, WOOD_D)
    for xx in range(6, 34, 6):
        rect(img, xx, 8, xx, 15, WOOD_D)
    # coins piled inside
    ellipse(img, 8, 2, 28, 9, (248, 202, 74))
    noise(img, 8, 2, 28, 8, [(255, 230, 140), (214, 158, 40)], 0.3, 4)
    # wheels
    for wx in (9, 27):
        ellipse(img, wx, 14, wx + 9, 23, WOOD_D)
        ellipse(img, wx + 2, 16, wx + 7, 21, (214, 176, 116))
        px(img, wx + 4, 18, WOOD_D)
    rect(img, 34, 9, 39, 10, WOOD_D)                  # handle
    return outline(img)


def well():
    img = blank(28, 32)
    rect(img, 4, 18, 23, 30, (150, 150, 160))         # stone ring
    noise(img, 4, 18, 23, 30, [(118, 118, 132), (176, 176, 188)], 0.25, 11)
    rect(img, 6, 20, 21, 24, (40, 60, 90))            # dark water hole
    rect(img, 6, 20, 21, 21, (90, 140, 180))
    for x in (6, 20):                                  # posts
        rect(img, x, 6, x + 1, 18, WOOD_D)
    for i in range(9):                                 # little roof
        rect(img, 2 + i, 2 + i // 2, 25 - i, 3 + i // 2, ROOF if i % 2 else ROOF_D)
    rect(img, 10, 10, 16, 11, WOOD)                    # winch
    line(img, [(13, 11), (13, 19)], (60, 50, 40), 1)   # rope
    rect(img, 11, 19, 15, 22, (180, 140, 90))          # bucket
    return outline(img)


def mailbox():
    img = blank(16, 24)
    rect(img, 6, 10, 9, 22, WOOD_D)
    rect(img, 2, 4, 13, 11, (90, 140, 200))
    ellipse(img, 2, 2, 13, 8, (90, 140, 200))
    rect(img, 2, 2, 13, 3, (60, 100, 160))
    rect(img, 12, 5, 13, 8, (230, 80, 70))             # flag
    px(img, 4, 7, (30, 40, 60))
    return outline(img)


def butterfly_frames():
    cols = [(250, 150, 200), (150, 200, 250)]
    frames = []
    for ci, wc in enumerate(cols):
        for wing in (0, 1, 2):                          # down, mid, up
            img = blank(16, 12)
            body = (60, 50, 70)
            rect(img, 7, 3, 8, 9, body)
            px(img, 7, 2, body); px(img, 8, 2, body)
            spread = [4, 6, 5][wing]; lift = [1, 0, -2][wing]
            ellipse(img, 7 - spread, 3 + lift, 6, 8 + lift, wc)
            ellipse(img, 9, 3 + lift, 9 + spread, 8 + lift, wc)
            px(img, 7 - spread + 1, 5 + lift, lighter(wc, 40))
            px(img, 9 + spread - 1, 5 + lift, darker(wc, 30))
            frames.append(outline(img))
    sh = Sheet(3, 16, 12, rows=2)
    for f in frames:
        sh.add(f)
    canvas = sh.save(os.path.join(MEAD, "butterfly.png"))
    save_scaled(canvas, os.path.join(MEAD, "previews", "butterfly@4x.png"), 4)


save1(hut(), MEAD, "hut")
save1(fence(), MEAD, "fence")
save1(mush_house(), MEAD, "mushroom_house")
save1(lantern(), MEAD, "lantern")
save1(hay_bale(), MEAD, "hay_bale")
save1(cart(), MEAD, "coin_cart")
save1(well(), MEAD, "well")
save1(mailbox(), MEAD, "mailbox")
butterfly_frames()


# ===================================================================== SNOW
IG = (222, 236, 248); IG_D = (176, 198, 222)


def igloo(lit=False):
    img = blank(40, 26)
    ellipse(img, 2, 0, 37, 48, IG)                     # dome
    rect(img, 2, 12, 37, 24, IG)
    # brick seams
    for yy in (6, 11, 16, 21):
        line(img, [(3, yy), (36, yy)], IG_D, 1)
    for i, (sx, sy) in enumerate([(8, 6), (20, 6), (30, 11), (14, 11), (6, 16), (24, 16), (16, 21), (30, 21)]):
        rect(img, sx, sy, sx, sy + 4, IG_D)
    # entrance tunnel
    ellipse(img, 14, 12, 26, 25, (120, 150, 185))
    ellipse(img, 16, 14, 24, 25, (56, 78, 108))
    if lit:
        ellipse(img, 18, 17, 22, 22, (255, 208, 120))  # warm glow inside
        px(img, 20, 19, (255, 244, 200))
    else:
        px(img, 20, 18, (90, 120, 155))
    # snow on top ridge
    for x in range(6, 34):
        if random.Random(x).random() < 0.5:
            px(img, x, 3 - (abs(x - 20) // 9), (255, 255, 255))
    return outline(img)


def snow_cabin():
    img = blank(48, 44)
    rect(img, 6, 18, 41, 40, (140, 96, 60))            # log wall
    for yy in range(19, 40, 3):
        rect(img, 6, yy, 41, yy, (108, 72, 44))
    # snow-laden roof
    for i in range(12):
        rect(img, 2 + i, 6 + i, 45 - i, 8 + i, (120, 84, 54))
    rect(img, 1, 4, 46, 7, (246, 250, 255))
    for x in range(2, 46, 3):
        px(img, x, 7, (230, 240, 250)); px(img, x + 1, 8, (246, 250, 255))
    # glowing window
    rect(img, 12, 24, 19, 30, (80, 54, 36))
    rect(img, 13, 25, 18, 29, (255, 214, 120))
    px(img, 15, 27, (255, 246, 200)); rect(img, 15, 25, 16, 29, (80, 54, 36))
    # door with wreath
    rect(img, 28, 26, 35, 40, (96, 64, 42))
    ellipse(img, 29, 30, 34, 35, (60, 120, 70))
    px(img, 31, 30, (230, 70, 60)); px(img, 32, 34, (230, 70, 60))
    px(img, 34, 33, (240, 200, 120))                   # knob
    # chimney with animated-look smoke
    rect(img, 36, 0, 41, 8, (120, 96, 84))
    rect(img, 35, 0, 42, 1, (246, 250, 255))
    for sx, sy in ((43, 2), (45, 0)):
        ellipse(img, sx, sy, sx + 3, sy + 3, (235, 238, 245, 210))
    # snow drift at base
    for x in range(0, 48):
        h = 2 + int(2 * abs(((x % 12) - 6) / 6.0))
        rect(img, x, 41, x, min(43, 41 + (4 - h)), (246, 250, 255))
    return outline(img)


def snow_globe():
    img = blank(24, 28)
    ellipse(img, 2, 0, 21, 19, (200, 228, 250, 120))
    ellipse(img, 4, 2, 19, 17, (230, 244, 255, 90))
    px(img, 6, 4, (255, 255, 255, 200)); px(img, 7, 5, (255, 255, 255, 200))
    # mini tree inside
    for i in range(4):
        rect(img, 10 - i, 8 + i * 2, 11 + i, 9 + i * 2, (70, 140, 90))
    rect(img, 10, 16, 11, 17, (120, 84, 54))
    px(img, 8, 12, (255, 255, 255)); px(img, 14, 10, (255, 255, 255)); px(img, 12, 14, (255, 255, 255))
    rect(img, 4, 19, 19, 24, (170, 60, 60))            # wooden base
    rect(img, 3, 24, 20, 26, (140, 46, 46))
    rect(img, 4, 21, 19, 21, (210, 90, 80))
    return outline(img)


def candle():
    img = blank(12, 20)
    rect(img, 4, 6, 7, 16, (246, 230, 200))
    rect(img, 4, 6, 4, 16, (222, 202, 168))
    rect(img, 3, 16, 8, 18, (200, 180, 150))
    line(img, [(6, 5), (6, 4)], (60, 50, 50), 1)
    ellipse(img, 4, 0, 7, 4, (255, 190, 80))
    ellipse(img, 5, 1, 6, 3, (255, 240, 180))
    return outline(img)


def sled():
    img = blank(28, 16)
    rect(img, 2, 10, 25, 12, (150, 60, 50))            # board
    rect(img, 2, 12, 25, 13, (110, 44, 40))
    px(img, 1, 10, (255, 220, 120)); px(img, 0, 9, (255, 220, 120))  # curled runner tip
    for x in (6, 18):                                   # seat posts
        rect(img, x, 5, x + 1, 10, WOOD_D)
    rect(img, 4, 3, 22, 5, WOOD)
    rect(img, 4, 3, 22, 3, lighter(WOOD, 25))
    line(img, [(24, 5), (26, 1), (24, 1)], (90, 60, 40), 1)  # pull rope
    return outline(img)


def frozen_bush():
    img = blank(24, 20)
    ellipse(img, 1, 6, 22, 19, (96, 140, 120))
    ellipse(img, 3, 4, 20, 14, (120, 168, 144))
    ellipse(img, 2, 2, 21, 9, (238, 246, 255))         # snow cap
    px(img, 6, 10, (255, 255, 255)); px(img, 15, 12, (255, 255, 255))
    px(img, 10, 14, (230, 80, 80)); px(img, 17, 9, (230, 80, 80))  # berries
    return outline(img)


def snow_pine():
    img = blank(24, 32)
    rect(img, 10, 26, 13, 31, (110, 78, 52))
    for i, (w, y) in enumerate([(16, 18), (13, 11), (10, 4)]):
        x0 = 12 - w // 2
        for t in range(7):
            ww = max(2, w - t * 2)
            rect(img, 12 - ww // 2, y + t, 12 - ww // 2 + ww - 1, y + t, (58, 118, 84))
        ellipse(img, x0, y, x0 + w - 1, y + 8, (58, 118, 84))
        # snow shelves
        rect(img, x0 + 1, y + 6, x0 + w - 2, y + 7, (240, 248, 255))
        px(img, x0 + w // 2, y, (250, 252, 255))
    px(img, 12, 2, (255, 220, 120))                    # star topper
    px(img, 11, 3, (255, 220, 120)); px(img, 13, 3, (255, 220, 120))
    return outline(img)


def stocking_sign():
    img = blank(20, 28)
    rect(img, 9, 10, 11, 27, WOOD_D)
    rect(img, 2, 2, 17, 4, WOOD)
    # stocking hanging from bar
    rect(img, 4, 4, 8, 12, (220, 70, 70))
    rect(img, 4, 4, 8, 5, (245, 245, 245))
    rect(img, 4, 12, 10, 16, (220, 70, 70))
    rect(img, 8, 12, 10, 16, (200, 56, 56))
    rect(img, 4, 14, 6, 16, (245, 245, 245))
    px(img, 6, 9, (255, 220, 120))
    return outline(img)


def penguin_friend(frames_kind):
    """small non-player penguin: idle(2f) or wave(2f)."""
    imgs = []
    for f in range(2):
        img = blank(24, 28)
        bob = f
        BK = (52, 60, 86); WH = (240, 244, 250); BE = (248, 170, 60)
        rect(img, 7, 25 + bob, 10, 26 + bob, BE); rect(img, 13, 25 + bob, 16, 26 + bob, BE)
        ellipse(img, 5, 9 + bob, 18, 26 + bob, BK)
        ellipse(img, 8, 13 + bob, 16, 25 + bob, WH)
        ellipse(img, 6, 2 + bob, 17, 12 + bob, BK)
        ellipse(img, 8, 5 + bob, 15, 11 + bob, WH)
        d = ImageDraw.Draw(img)
        d.polygon([(c[0] * SCALE + SCALE / 2, c[1] * SCALE + SCALE / 2) for c in
                   [(6, 6 + bob), (3, 7 + bob), (6, 8 + bob)]], fill=BE)
        px(img, 9, 5 + bob, (20, 20, 30)); px(img, 9, 4 + bob, (255, 255, 255))
        wa = -6 if (frames_kind == "wave" and f == 1) else 0
        line(img, [(16, 13 + bob), (19, 17 + bob + wa)], BK, 2)
        if frames_kind == "scarf":
            rect(img, 6, 10 + bob, 17, 11 + bob, (230, 80, 80))
            rect(img, 7, 11 + bob, 9, 15 + bob, (230, 80, 80))
        imgs.append(outline(img))
    return imgs


sh = Sheet(2, 24, 28)
for fr in penguin_friend("idle"):
    sh.add(fr)
c = sh.save(os.path.join(SNOW, "penguin_idle.png"))
save_scaled(c, os.path.join(SNOW, "previews", "penguin_idle@3x.png"), 3)
sh = Sheet(2, 24, 28)
for fr in penguin_friend("wave"):
    sh.add(fr)
c = sh.save(os.path.join(SNOW, "penguin_wave.png"))
save_scaled(c, os.path.join(SNOW, "previews", "penguin_wave@3x.png"), 3)
sh = Sheet(2, 24, 28)
for fr in penguin_friend("scarf"):
    sh.add(fr)
c = sh.save(os.path.join(SNOW, "penguin_scarf.png"))
save_scaled(c, os.path.join(SNOW, "previews", "penguin_scarf@3x.png"), 3)

save1(igloo(False), SNOW, "igloo")
save1(igloo(True), SNOW, "igloo_lit")
save1(snow_cabin(), SNOW, "snow_cabin")
save1(snow_globe(), SNOW, "snow_globe")
save1(candle(), SNOW, "candle")
save1(sled(), SNOW, "sled")
save1(frozen_bush(), SNOW, "frozen_bush")
save1(snow_pine(), SNOW, "snow_pine")
save1(stocking_sign(), SNOW, "stocking_sign")


# ==================================================================== BEACH
LT = (240, 214, 150); LT_D = (208, 178, 112); TEAL = (70, 190, 190)


def lifeguard():
    img = blank(40, 48)
    for x in (8, 28):                                   # stilts
        rect(img, x, 22, x + 2, 46, WOOD)
        rect(img, x, 22, x, 46, WOOD_D)
    line(img, [(9, 40), (29, 26)], WOOD_D, 1)           # cross brace
    line(img, [(9, 26), (29, 40)], WOOD_D, 1)
    rect(img, 4, 20, 34, 23, lighter(WOOD, 12))         # deck
    rect(img, 4, 23, 34, 24, WOOD_D)
    rect(img, 8, 8, 30, 20, (246, 240, 226))            # hut
    rect(img, 8, 12, 30, 13, TEAL)
    rect(img, 12, 13, 24, 19, TEAL)                     # window
    px(img, 14, 15, (255, 255, 255, 180))
    for i in range(6):                                   # striped awning roof
        rect(img, 5 + i, 4 + i, 34 - i, 6 + i, (235, 80, 80) if i % 2 == 0 else (250, 246, 240))
    rect(img, 4, 3, 35, 4, (200, 60, 60))
    ellipse(img, 30, 14, 36, 19, (250, 240, 230))       # life ring on side
    ellipse(img, 32, 16, 34, 18, (235, 80, 80))
    return outline(img)


def tiki_torch():
    img = blank(12, 32)
    rect(img, 5, 8, 7, 30, (128, 88, 52))
    for yy in range(10, 30, 4):
        rect(img, 5, yy, 7, yy, (96, 62, 36))
    rect(img, 3, 5, 9, 9, (150, 104, 60))               # carved cup
    px(img, 4, 6, (90, 58, 32)); px(img, 8, 7, (90, 58, 32)); px(img, 6, 8, (90, 58, 32))
    ellipse(img, 3, 1, 9, 6, (255, 170, 60))            # flame
    ellipse(img, 4, 0, 8, 4, (255, 220, 120))
    px(img, 6, 0, (255, 250, 210))
    return outline(img)


def surfboard():
    img = blank(12, 32)
    ellipse(img, 3, 0, 9, 31, (250, 200, 70))
    ellipse(img, 4, 2, 8, 29, (250, 240, 220))
    rect(img, 5, 4, 6, 27, (90, 170, 220))              # stripe
    px(img, 5, 8, (235, 90, 90)); px(img, 6, 14, (235, 90, 90)); px(img, 5, 20, (235, 90, 90))
    return outline(img)


def sandcastle():
    img = blank(40, 30)
    rect(img, 4, 14, 36, 28, LT)                        # main keep
    noise(img, 4, 14, 36, 28, [LT_D], 0.12, 6)
    for tx, th in ((2, 8), (30, 8)):                     # side towers
        rect(img, tx, th, tx + 7, 28, LT)
        for i in range(4):
            px(img, tx + i * 2, th, LT); px(img, tx + i * 2 + 1, th, LT_D if i % 2 else LT)
    rect(img, 14, 4, 24, 28, lighter(LT, 8))             # central tower
    for i in range(6):
        px(img, 14 + i * 2, 3, LT); px(img, 15 + i * 2, 3, LT_D)
    rect(img, 17, 20, 21, 28, (150, 104, 62))            # door
    ellipse(img, 17, 18, 21, 22, (150, 104, 62))
    # flag
    line(img, [(19, 3), (19, -1)], (90, 60, 40), 1)
    rect(img, 19, 0, 23, 1, (240, 90, 90))
    # shell trim + moat shadow
    px(img, 8, 16, (250, 220, 210)); px(img, 30, 18, (250, 220, 210)); px(img, 19, 12, (255, 230, 150))
    rect(img, 0, 28, 39, 29, LT_D)
    return outline(img)


def buoy():
    img = blank(16, 20)
    ellipse(img, 2, 4, 13, 17, (235, 80, 80))
    rect(img, 2, 9, 13, 11, (250, 246, 240))
    ellipse(img, 6, 0, 9, 5, (120, 100, 80))
    px(img, 7, 1, (255, 220, 120))
    ellipse(img, 4, 6, 6, 8, (250, 160, 150, 180))
    return outline(img)


def seaweed():
    img = blank(16, 18)
    rnd = random.Random(2)
    for sx in (3, 8, 12):
        h = rnd.randrange(8, 15)
        sway = rnd.choice((-1, 1))
        for i in range(h):
            px(img, sx + int(sway * (i % 4 == 3)), 17 - i, (60, 140, 80) if i % 2 else (90, 170, 100))
    rect(img, 1, 16, 14, 17, LT_D)
    return outline(img)


def cooler():
    img = blank(24, 18)
    rect(img, 2, 5, 21, 16, (90, 160, 210))
    rect(img, 2, 5, 21, 7, (250, 246, 240))             # lid
    rect(img, 2, 7, 21, 8, (200, 190, 180))
    rect(img, 10, 3, 13, 5, (150, 140, 130))            # latch
    px(img, 5, 11, (255, 255, 255, 160)); px(img, 6, 12, (255, 255, 255, 120))
    rect(img, 4, 10, 8, 13, (235, 80, 80))              # sticker
    px(img, 5, 11, (255, 255, 255)); px(img, 7, 12, (255, 255, 255))
    return outline(img)


def hammock_palm():
    """tall palm with a hammock strung to a second trunk."""
    img = blank(48, 56)
    # trunks
    for tx, lean in ((8, 1), (38, -1)):
        for i in range(34):
            x = tx + int(lean * (i // 8))
            rect(img, x, 55 - i, x + 3, 55 - i, (150, 108, 66) if i % 3 else (128, 90, 54))
    # fronds on both crowns
    for tx, lean, seed in ((8, 1, 1), (38, -1, 5)):
        cx, cy = tx + lean * 4, 21
        rnd = random.Random(seed)
        for ang in (-70, -30, 10, 50, 90, 130, 170, 210):
            rad = ang * 3.14159 / 180
            pts = [(cx + int(2 + 9 * __import__("math").cos(rad + s * 0.25)),
                    cy + int(2 + 6 * __import__("math").sin(rad + s * 0.25) + s * s * 0.7))
                   for s in range(5)]
            line(img, pts, (70, 160, 80), 2)
        ellipse(img, cx, cy, cx + 4, cy + 3, (110, 80, 50))
        # coconuts
        px(img, cx + 1, cy + 4, (120, 84, 50)); px(img, cx + 3, cy + 4, (100, 70, 44))
    # hammock
    line(img, [(12, 26), (22, 34), (34, 26)], (240, 120, 140), 2)
    line(img, [(12, 27), (22, 35), (34, 27)], (250, 180, 190), 1)
    line(img, [(12, 26), (10, 24)], (90, 70, 50), 1)
    line(img, [(34, 26), (37, 24)], (90, 70, 50), 1)
    return outline(img)


def flamingo():
    img = blank(28, 28)
    # floaty ring
    ellipse(img, 2, 16, 25, 27, (250, 130, 170))
    ellipse(img, 6, 19, 21, 24, (255, 210, 225))
    # body sits on ring
    ellipse(img, 8, 10, 20, 19, (250, 150, 185))
    # neck + head
    line(img, [(18, 12), (21, 7), (21, 3)], (250, 150, 185), 3)
    ellipse(img, 19, 0, 24, 4, (250, 150, 185))
    d = ImageDraw.Draw(img)
    d.polygon([(c[0] * SCALE + SCALE / 2, c[1] * SCALE + SCALE / 2) for c in
               [(19, 1), (16, 2), (19, 3)]], fill=(250, 200, 90))
    px(img, 21, 1, (40, 30, 40))
    # tail feather
    px(img, 8, 12, (235, 100, 150)); px(img, 7, 13, (235, 100, 150))
    return outline(img)


save1(lifeguard(), BEACH, "lifeguard_tower")
save1(tiki_torch(), BEACH, "tiki_torch")
save1(surfboard(), BEACH, "surfboard")
save1(sandcastle(), BEACH, "sandcastle")
save1(buoy(), BEACH, "buoy")
save1(seaweed(), BEACH, "seaweed")
save1(cooler(), BEACH, "cooler_box")
save1(hammock_palm(), BEACH, "hammock_palm")
save1(flamingo(), BEACH, "flamingo_float")
print("props ok")
