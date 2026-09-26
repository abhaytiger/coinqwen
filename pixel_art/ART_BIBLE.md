# Coin Quest — Pixel Art Bible (v4)

Final asset library for the cute, colourful platformer. Everything here is
**hand-built with code** (see `_tools/`), 16-bit premium style: soft top-light,
bottom shade, warm rim highlights, dithered gradients, chunky dark outlines.

- `SCALE = 4` inside generators → every sprite is drawn on a 4× subpixel grid,
  then downsampled to logical size. Import `_tools/pxlib.py` + `_tools/pxlib2.py`
  and reuse the helpers (`Sheet`, `rrect`, `top_light`, `bottom_shade`, `eye`,
  `finalize`…) to extend anything consistently.
- Re-run any generator after editing it: `python _tools/gen_heroes.py` etc.
- `MANIFEST.txt` lists every PNG with dimensions. Regenerate with
  `python _tools/make_manifest.py`.
- Each folder has a `previews/` subdir with @3x crops for eyeballing.
- `previews_all/contact_sheet_v4.png` — one-glance sanity sheet of the newest batch.

---

## 0. Movement model & direction convention (READ FIRST)

The character moves in a 2D plane (side view + light top-down tilt):
**left / right / up (away from camera) / down (toward camera)**.

| Move direction | Sprite set used | Flip |
|---|---|---|
| Walk **left** | side-view rows (rows 0–1 of `hero_*.png`) | none (art already faces left) |
| Walk **right** | side-view rows | `flip_x = true` on the Sprite2D |
| Walk **up** (away) | back-view rows (rows 2–3) | none |
| Walk **down** (toward cam) | back-view rows (rows 2–3) | optional tiny `flip_h` if you want the pack to sway; usually identical |

- **Side view** faces LEFT and shows the hooded face, backpack at the back edge.
- **Back view** (walk away/toward camera): no face visible — hood dome from behind,
  hair nape, full backpack with straps + coin-pouch glint, arms swinging at both
  sides, boots spread wider, sole flash mid-stride. Snow skin shows the scarf tail
  hanging down the back; beach skin shows the sunhat band.
- Idle/jump/collect exist in BOTH views so you never pop when changing direction.
- Convenience atlases: **`characters/hero_<skin>_4dir.png`** (8×4 @48×56) packs
  row0 = side frames, row1 = back frames, cols 4–7 = pre-flipped (facing right)
  copies of each row. Use either this or the base sheets — your call.

### Frame order inside every `hero_*.png` (4 cols × 4 rows, cells 48×56)
```
row0: idle0  idle1  jump   collect     (SIDE view, facing left)
row1: run0   run1   run2   run3        (SIDE view)
row2: idle0  idle1  jump   collect     (BACK view)
row3: run0   run1   run2   run3        (BACK view)
```

### Godot recipe (SpriteFrames, per skin)
```gdscript
# tex = preload("res://pixel_art/characters/hero_default.png")  # 192 x 224
for r in range(4):
    for c in range(4):
        var reg := Rect2(c * 48, r * 56, 48, 56)
        match r:
            0: frames.add_frame("side_idle", reg)      # idle0 idle1
            1: frames.add_frame("side_run",  reg)      # run0..run3
            2: frames.add_frame("back_idle", reg)
            3: frames.add_frame("back_run",  reg)
# jump = side_idle col2, collect = side_idle col3 (add as single-frame anims)
```
Player logic:
```gdscript
var dir := Input.get_vector("left","right","up","down")
if absf(dir.x) >= absf(dir.y):          # horizontal -> side view
    sprite.texture_frames = SIDE_SET
    sprite.flip_h = dir.x > 0           # art faces LEFT
else:                                   # vertical -> back view
    sprite.texture_frames = BACK_SET    # same sheet, rows 2-3
```
Play `run` while moving, `idle` when stopped, `jump` on leaving the ground,
`collect` on pickups (both views have them).

---

## 1. Characters — `characters/`

Nine skins, all identical geometry (4×4 grid @48×56, side + back views):

| File | Who |
|---|---|
| `hero_default.png` | blue-hood kid explorer (pack, pouch, laced boots) |
| `hero_snow.png` | white parka + red scarf (scarf tail visible in back view) |
| `hero_beach.png` | orange swimwear + sun shades (hat band in back view) |
| `hero_penguin.png` | tuxedo penguin, flippers swing/hop |
| `hero_crab.png` | wide carapace, 6 scuttling legs, big claws (back view = full shell w/ center seam) |
| `hero_bunny.png` | long ears, green overalls, cotton tail wiggles in back view |
| `hero_fox.png` | bushy cream-tipped tail sweeps side-to-side in back view |
| `hero_cat.png` | lavender tabby, curling tail, collar+bell seen from behind |
| `hero_owl.png` | amber eyes + facial discs front; layered back feathers + wing flap rear |

Extras baked into every frame: soft ground shadow ellipse, drop-shadow under
hood/wings, specular eye sparkles, blush cheeks.

Generators: `_tools/gen_heroes.py` (humanoids), `_tools/gen_hero_animals.py`
(animals), `_tools/gen_final_polish.py` (4dir atlases + shadow blob).

`effects/shadow_blob.png` — 3 soft elliptical shadows (small/med/large, 32×12
cells) if you prefer a separate shadow node instead of the baked-in one.

---

## 2. Enemies — `enemies/`

Front sheets (existing): `blob_green.png`, `slime_green.png`, `slime_snow.png`,
`slime_lava.png` — 5×2 @32×32. Row0: 4 idle-squish + 1 move; row1: 4 move + squash-hit.

**NEW back sheets** (`*_back.png`, same grids/layouts so you can hot-swap by
direction like the heroes): `blob_green_back.png`, `slime_green_back.png`,
`slime_snow_back.png`, `slime_lava_back.png`. Rear view = jelly body, glossy
sheen, eyes peeking around the silhouette edges, hop-waddle motion, snowcap /
ember-crack details kept. Generator: `_tools/gen_back_enemies.py`.

Direction handling for enemies patrolling toward/away: pick front vs `_back`
texture by sign of their velocity along the depth axis; flip_x for lateral.

---

## 3. Footstep dust — `effects/`  (NEW)

One themed sheet per world, sized **exactly like the hero frames (48×56 cells)**
so it can be pasted straight into the player's AnimationPlayer as extra tracks,
or spawned as a child Sprite2D offset to the feet. Layout: 4 cols × 2 rows:

```
row0: puff cycle f0..f3   — nudge -> billow -> drift -> fade (rising soft cloud)
row1: scatter f0..f3      — pebbles/spray kicked BACKWARD (to the right of frame,
                            since chars face left; flip_x when walking right)
```

| File | Matches ground of | Look |
|---|---|---|
| `dust_meadow.png` | classic meadow dirt/grass path | warm tan puffs + dirt/leaf chips |
| `dust_snow.png` | snow town | powder-white puffs + ice chips (soft, bright) |
| `dust_beach.png` | beach sand (+ riverbanks!) | pale gold grains + tiny water droplets near the shallows |

Spawn recipe (subtle!):
```gdscript
# in CharacterBody2D, signal-driven off the run animation's foot-contact frames
func _footstep():                      # call ~every 2 run frames
    var d := DUST_TEX   # preload dust_<world>.png for the CURRENT world
    var s := Sprite2D.new()
    s.texture = d
    s.region_enabled = true
    s.region_rect = Rect2(0, 0, 48, 56)          # start row0 (puff)
    s.position = feet_offset + Vector2(randf_range(-2,2), 0)
    s.flip_h = not sprite.flip_h                 # throw dust behind you
    s.modulate.a = 0.55                          # keep it SUBTLE
    add_child(s); s.z_index = z_index - 1        # under the character
    var tw := create_tween()
    for i in range(1, 4):                        # step through the 4 puff frames
        tw.tween_property(s, "region_rect:position:x", i * 48.0, 0.06)
    tw.tween_property(s, "modulate:a", 0.0, 0.12)
    tw.tween_callback(s.queue_free)
```
- Only emit while grounded & walking (skip when airborne/gliding).
- On the river/bonfire bridges use the **beach** sheet with `flip_h` matching
  flow-side, or spawn at the waterline for splash variant (row1 has droplets).
- Swap `DUST_TEX` when the player changes worlds (each stage sets its own).
- Optional harder hit: play row1 (scatter) on landing from a big jump.

---

## 4. Worlds — `worlds/`

### `classic_meadow/`  (Stage 1 — sunny grassland)
Backgrounds: `bg_far.png` (sky+mountains), `bg_mid.png` (hills+trees),
`ground_top.png` (grass strip), `dirt_fill.png`. Props: bushes, flowers,
mushrooms, wooden crate/sign, arch… **NEW:** `fountain.png` (4-frame animated
plaza fountain, jet height cycles + shimmer), `picnic_set.png` (checkered
blanket + basket + apple — story spot for NPC), `hedge.png` (4 tileable hedge
variants incl. berry one, 16×16).

### `snow_town/`  (Stage 2 — festive night)
Lamp-lit snow, icicles, pine trees, presents, snowman, gingerbread house…
**NEW:** `snow_lamp.png` (2-frame flickering warm halo — matches existing lamp
motif), `cocoa_stand.png` (2-frame steaming market cart), `ice_skate_tiles.png`
(4 shiny skate-pond variants — lay these where you want a slippery slide patch
inside the frozen-river section).

### `beach/`  (Stage 3 — river crossing + sunset coast)
Water tiles, wave foam strips, palm trees, shells, bridge planks, sunset sky…
**NEW:** `boardwalk_tiles.png` (4 dock-plank path variants — great for the
riverbank approach), `dolphin_leap.png` (4-frame leap arc — trigger near the
splash checkpoints as an ambience event!), `tiki_bar_sign.png` (carved mask
signpost for the checkpoint hut).

Each world folder also keeps its own `previews/` @3x crops.

---

## 5. Other folders (unchanged, still canonical)

- `coins/` — spin cycles, gem tiers, big treasure coin.
- `ground/` — mega tileset sheets (auto-tiling edges, slopes).
- `props/` — crates, springs, flags, checkpoints.
- `weather/` — rain/snow/petal particle sprites.
- `ui/` — HUD hearts, coin counter, buttons, fonts.
- `enemies/previews`, `characters/previews` — always-regenerated @3x strips,
  now including `hero_*_back_run@3x.png` previews.

---

## 6. Style rules (keep future art consistent)

1. Palette anchor: ink outline `(34,24,48)`; warm key light from top-left;
   bottom-shade 30–45 units; rim highlight 18–34 units.
2. Eyes: white + INK pupil + single sparkle; blush under eyes on all heroes.
3. Back views NEVER show eyes/face except slits peeking at the silhouette rim.
4. FX (dust) are unoutlined, blurred, alpha ≤ ~120/frame — subtle, never
   bigger than ⅓ of the character height at peak.
5. Every new animation must ship with matching front AND back variants if the
   thing can walk in the depth axis.
6. Cell sizes are law: heroes 48×56, enemies 32×32, tiles 16×16, FX 48×56.

— end of bible —
