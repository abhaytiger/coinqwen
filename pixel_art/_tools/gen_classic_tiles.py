"""Classic meadow world tileset (8 x 16px tiles)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

OUT = "/workspace/pixel_art/worlds/classic_meadow"
PREV = os.path.join(OUT, "previews")
for d in (OUT, PREV):
    os.makedirs(d, exist_ok=True)

GRASS = (96, 176, 84); GRASS_D = (58, 128, 62); GRASS_L = (146, 210, 116)
DIRT = (150, 106, 66); DIRT_D = (112, 76, 46); DIRT_L = (176, 132, 88)
STONE = (140, 140, 150); STONE_D = (100, 100, 112); STONE_L = (176, 176, 188)

def tiles():
    t = new(16, 16); rect(t, 0, 0, 15, 15, GRASS)                       # 0 grass
    noise(t, 0, 0, 15, 15, [GRASS_D, GRASS_L], .25, 2)
    for x in range(0, 16, 5): px(t, x, 0, GRASS_L); px(t, x + 1, 0, GRASS_L)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, DIRT)                        # 1 dirt
    noise(t, 0, 0, 15, 15, [DIRT_D, DIRT_L], .3, 4)
    px(t, 4, 5, DIRT_D); px(t, 11, 10, DIRT_D); px(t, 8, 13, DIRT_L)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, STONE)                       # 2 stone
    noise(t, 0, 0, 15, 15, [STONE_D, STONE_L], .3, 6)
    line(t, [(2, 4), (6, 4), (8, 7)], STONE_D, 1); line(t, [(10, 11), (13, 11)], STONE_D, 1)
    yield t
    t = new(16, 16); rect(t, 0, 4, 15, 15, DIRT)                        # 3 grass top
    noise(t, 0, 5, 15, 15, [DIRT_D, DIRT_L], .25, 8)
    rect(t, 0, 4, 15, 6, GRASS)
    for x, hgt in enumerate([6, 5, 6, 7, 6, 5, 6, 7, 6, 6, 5, 6, 7, 6, 5, 6]):
        rect(t, x, 4, x, hgt - 1, GRASS)
        if hgt > 5: px(t, x, hgt - 1, GRASS_D)
    noise(t, 1, 4, 14, 6, [GRASS_L], .2, 10)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, (0, 0, 0, 0))                # 4 single blade deco
    line(t, [(4, 15), (4, 11), (3, 10)], GRASS_D, 1)
    line(t, [(8, 15), (8, 9), (9, 8)], GRASS, 1)
    line(t, [(12, 15), (12, 12), (13, 11)], GRASS_L, 1)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, (66, 140, 200, 255))         # 5 water
    rnd = random.Random(12)
    for _ in range(10):
        x = rnd.randrange(16); y = rnd.randrange(16)
        px(t, x, y, (96, 176, 226, 255)); px(t, x + 1, y, (96, 176, 226, 255))
    line(t, [(2, 5), (5, 5), (7, 7)], (150, 210, 240, 255), 1)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, BRICK := (178, 122, 96, 255))# 6 brick wall
    for y in range(0, 16, 4):
        rect(t, 0, y, 15, y, (128, 84, 66, 255))
        off = 0 if (y // 4) % 2 == 0 else 4
        for x in range(off, 16, 8): rect(t, x, y + 1, x, y + 3, (128, 84, 66, 255))
    noise(t, 0, 0, 15, 15, [(192, 136, 108, 255)], .12, 14)
    yield t
    t = new(16, 16); rect(t, 0, 0, 15, 15, (166, 128, 84, 255))         # 7 wood
    for y in (0, 5, 10, 15): rect(t, 0, y, 15, y, (120, 88, 56, 255))
    noise(t, 1, 1, 15, 14, [(150, 112, 72, 255)], .16, 16)
    yield t

sh = Sheet(8, 16, 16)
for t in tiles(): sh.add(t)
sh.save(os.path.join(OUT, "tiles.png"))
save_scaled(sh.canvas, os.path.join(PREV, "tiles@4x.png"), 4)
print("classic tiles ok")
