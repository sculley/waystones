"""Design-exploration sheet of alternative waystone styles (docs/images/concepts.png)."""
import math, os
from PIL import Image, ImageDraw
from iso import *
from iso import ROOT

# ---------- designs ----------
RUNE = ["..LL..", ".LPPL.", "..PP..", "LPWWPL", "..PP..", "..PP..", ".LPPL.", "..LL.."]

designs = [
    ("1  Rune Block (current)", "Full block · stand on top",
     [Box(0, 0, 0, 16, 16, 16, textured("wst_waystone_top.png", "wst_waystone_side.png"))]),
    ("2  Gilded Deepslate", "Full block · darker, gold trim",
     [Box(0, 0, 0, 16, 16, 16, themed_cube(gold, deepslate_tiles, gold))]),
    ("3  End Beacon", "Full block · End stone & purpur",
     [Box(0, 0, 0, 16, 16, 16, themed_cube(purpur, end_stone, purpur))]),
    ("4  Obelisk", "~1.7 blocks tall · crystal tip",
     [Box(0, 0, 0, 16, 3, 16, stone_bricks), Box(2, 3, 2, 14, 5, 14, stone_bricks),
      Box(4, 5, 4, 12, 15, 12, rune_overlay(dark_stone, (5, 0), (0, 13), [r.ljust(6, ".") for r in RUNE])),
      Box(5, 15, 5, 11, 22, 11, dark_stone), Box(6, 22, 6, 10, 27, 10, amethyst)]),
    ("5  Arch Gate", "~1.9 blocks tall · walk-through portal",
     [Box(0, 0, 4, 16, 2, 12, stone_bricks), Box(0, 2, 5, 3, 26, 11, stone_bricks),
      Box(13, 2, 5, 16, 26, 11, stone_bricks), Box(-1, 26, 4, 17, 30, 12, stone_bricks),
      Box(6, 30, 6, 10, 32, 10, amethyst), Box(3, 2, 7, 13, 26, 9, portal)]),
    ("6  Floating Crystal", "Pedestal with hovering crystal",
     [Box(1, 0, 1, 15, 3, 15, stone_bricks), Box(5, 3, 5, 11, 10, 11, dark_stone),
      Box(2, 10, 2, 14, 13, 14, stone_bricks), Box(3, 13, 3, 13, 14, 13, obsidian),
      Box(6, 17, 6, 10, 25, 10, amethyst), Box(7, 15.5, 7, 9, 17, 9, amethyst), Box(7, 25, 7, 9, 26.5, 9, amethyst)]),
    ("7  Teleport Pad", "Low platform · step on to travel",
     [Box(0, 0, 0, 16, 2, 16, stone_bricks), Box(2, 2, 2, 14, 3, 14, obsidian),
      Box(4, 3, 4, 12, 3.4, 12, portal),
      *[Box(x, 2, z, x + 2, 7, z + 2, dark_stone) for x, z in [(0, 0), (14, 0), (0, 14), (14, 14)]],
      *[Box(x + 0.5, 7, z + 0.5, x + 1.5, 9, z + 1.5, amethyst) for x, z in [(0, 0), (14, 0), (0, 14), (14, 14)]]]),
    ("8  Lodestone Shrine", "Half-height · compass needle",
     [Box(0, 0, 0, 16, 4, 16, stone_bricks), Box(2, 4, 2, 14, 8, 14, rune_overlay(dark_stone, (5, 0), (0, 7), [".LPPL.", "LP..PL", ".LPPL."])),
      Box(1, 8, 1, 15, 10, 15, lambda f,a,b,w: gold(f,a,b,w) if (a in (1,14) or b in (1,14) or f!='up') else stone_bricks(f,a,b,w)), Box(4, 10, 7, 12, 11, 9, amethyst), Box(7, 10, 4, 9, 11, 12, obsidian)]),
]

COLS, CW, CH = 2, 420, 470
sheet = Image.new("RGB", (COLS * CW, math.ceil(len(designs) / COLS) * CH), (24, 20, 32))
d = ImageDraw.Draw(sheet)
for i, (name, note, boxes) in enumerate(designs):
    cx, cy = (i % COLS) * CW, (i // COLS) * CH
    d.rounded_rectangle([cx + 8, cy + 8, cx + CW - 8, cy + CH - 8], 14, fill=(36, 30, 48))
    render([ground()] + boxes, cx + CW / 2 - 8 * S * 0 , cy + 300, d)
    d.text((cx + 24, cy + 20), name, font=FONT, fill=(236, 214, 255))
    d.text((cx + 24, cy + 50), note, font=SMALL, fill=(180, 170, 200))
sheet.save(os.path.join(ROOT, "docs", "images", "concepts.png"))
print("saved", sheet.size)
