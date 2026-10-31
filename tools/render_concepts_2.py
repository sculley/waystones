"""Second design-exploration sheet of waystone styles (docs/images/concepts-2.png)."""
import math, os
from PIL import Image, ImageDraw
from iso import *
from iso import ROOT


# ---------- extra materials: f(face, a, b, box) -> (rgb, emissive) ----------

def stone_with_moss(face, a, b, w):
    top_of_box = w.hi[1]
    mossy = face == "up" or (top_of_box - b < 2 and h(a, b, 21) > 0.5) or h(a, b, 23) > 0.93
    if mossy:
        return noisy((78, 120, 52), a, b, 25, 0.18), False
    if h(a, b, 27) > 0.93:
        return (60, 58, 66), False  # cracks
    return noisy((128, 126, 122), a, b, 29, 0.12), False


def blackstone(face, a, b, w):
    return noisy((42, 36, 44), a, b, 31, 0.2), False


def blackstone_bricks(face, a, b, w):
    if b % 4 == 3 or (a + (4 if (b // 4) % 2 else 0)) % 8 == 7:
        return (22, 18, 26), False
    return noisy((52, 46, 56), a, b, 33, 0.15), False


def gold_banded(base, rows):
    def m(face, a, b, w):
        return gold(face, a, b, w) if b in rows else base(face, a, b, w)
    return m


SOUL = [(20, 90, 110), (40, 170, 190), (110, 230, 240), (210, 255, 255)]
SEA = [(150, 200, 190), (190, 230, 220), (230, 250, 245)]
LAPIS = [(30, 60, 160), (60, 110, 230), (150, 190, 255)]
TEAL = [(10, 70, 80), (20, 140, 150), (80, 220, 220)]
PINK = [(200, 90, 150), (240, 150, 200), (255, 215, 235)]
AMBER = [(230, 140, 40), (255, 200, 90), (255, 240, 190)]


def flame(pal):
    def m(face, a, b, w):
        t = int((math.sin(a * 1.3 + b * 0.9) + 1) * 1.5 + (b - w.lo[1]) * 0.4)
        return pal[min(len(pal) - 1, t)], True
    return m


def soul_bed(face, a, b, w):
    return SOUL[1 if h(a, b, 35) > 0.4 else 0], True


def prismarine_bricks(face, a, b, w):
    if b % 4 == 3 or a % 8 == 7:
        return (40, 90, 80), False
    return noisy((90, 160, 140), a, b, 37, 0.12), False


def dark_prismarine(face, a, b, w):
    if a % 4 == 0 or b % 4 == 0:
        return (24, 56, 46), False
    return noisy((50, 92, 76), a, b, 39, 0.12), False


def sea_lantern(face, a, b, w):
    d = (a % 4 in (0, 3)) or (b % 4 in (0, 3))
    return SEA[0 if d else (2 if (a + b) % 3 == 0 else 1)], True


def copper(face, a, b, w):
    c = (78, 160, 132) if h(a, b, 41) > 0.08 else (150, 110, 80)  # verdigris with copper flecks
    return noisy(c, a, b, 43, 0.1), False


def cut_copper(face, a, b, w):
    if a % 8 == 0 or b % 8 == 0:
        return (52, 112, 92), False
    return copper(face, a, b, w)


def lamp(face, a, b, w):
    return AMBER[2 if (a + b) % 5 == 0 else 1], True


def deepslate_sculk(face, a, b, w):
    vein = abs(math.sin(a * 0.9 + math.cos(b * 0.7) * 2)) < 0.18
    if vein:
        return TEAL[2], True
    return deepslate_tiles(face, a, b, w)


def sculk(face, a, b, w):
    if h(a, b, 45) > 0.85:
        return TEAL[2], True
    return noisy((12, 36, 48), a, b, 47, 0.3), False


def bone(face, a, b, w):
    return noisy((226, 222, 200), a, b, 49, 0.06), False


def calcite(face, a, b, w):
    return noisy((222, 224, 222), a, b, 51, 0.06), False


def basalt(face, a, b, w):
    return noisy((76, 76, 84), a, b, 53, 0.12), False


def cherry_log(face, a, b, w):
    if face == "up":
        return noisy((210, 150, 160), a, b, 55, 0.1), False
    return noisy((58, 32, 44), a, b, 57, 0.15), False


def cherry_planks(face, a, b, w):
    if b % 4 == 3:
        return (176, 104, 112), False
    return noisy((228, 168, 170), a, b, 59, 0.07), False


def petal_portal(face, a, b, w):
    ang = math.sin(a * 0.7 + b * 0.45) + math.cos(b * 0.6 - a * 0.3)
    return PINK[int((ang + 2) / 4 * 2.99)], True


def sandstone(face, a, b, w):
    if face != "up" and b % 4 == 0:
        return (190, 168, 110), False
    return noisy((222, 204, 146), a, b, 61, 0.06), False


def glyph(base, pal, cols, top_row, pattern):
    """Emissive glyph on side faces. pattern chars: 1/2/3 = palette index, '.' = base."""
    def m(face, a, b, w):
        if face != "up":
            u, v = a - cols, top_row - b
            if 0 <= v < len(pattern) and 0 <= u < len(pattern[0]) and pattern[v][u] != ".":
                return pal[int(pattern[v][u]) - 1], True
        return base(face, a, b, w)
    return m


RUNE = ["..2..", ".2.2.", "2.3.2", ".2.2.", "..2..", "..2..", ".212.", "..2.."]
EYE = ["..22..", ".2..2.", "2.33.2", ".2..2.", "..22..", "..11..", "..11.."]

# ---------- designs ----------
spikes = [(6, 6, 10, 10, 22), (2, 8, 5, 11, 14), (10, 3, 13, 6, 17), (10, 10, 13, 13, 12), (3, 3, 6, 6, 10)]

designs = [
    ("9  Mossy Standing Stone", "~1.8 blocks tall · ancient ruin",
     [Box(1, 0, 2, 15, 2, 14, stone_with_moss),
      Box(2, 2, 4.5, 14, 20, 11.5, glyph(stone_with_moss, PURPLE[2:], 6, 17, RUNE)),
      Box(3, 20, 5, 13, 26, 11, stone_with_moss), Box(5, 26, 6, 11, 28, 10, stone_with_moss)]),
    ("10  Soul Brazier", "Nether · blackstone, gold, soul fire",
     [Box(0, 0, 0, 16, 3, 16, blackstone_bricks), Box(3, 3, 3, 13, 10, 13, gold_banded(blackstone, {6})),
      Box(1, 10, 1, 15, 13, 15, gold_banded(blackstone_bricks, {12})), Box(3, 13, 3, 13, 14, 13, soul_bed),
      Box(5, 14, 6, 8, 20, 9, flame(SOUL)), Box(9, 14, 8, 11, 22, 10, flame(SOUL)), Box(6, 14, 10, 9, 17, 12, flame(SOUL))]),
    ("11  Tide Shrine", "Ocean · prismarine & sea lantern",
     [Box(0, 0, 0, 16, 3, 16, prismarine_bricks),
      *[Box(x, 3, z, x + 3, 13, z + 3, dark_prismarine) for x, z in [(0, 0), (13, 0), (0, 13), (13, 13)]],
      Box(4, 3, 4, 12, 11, 12, sea_lantern), Box(0, 13, 0, 16, 16, 16, prismarine_bricks),
      Box(5, 16, 5, 11, 17, 11, sea_lantern)]),
    ("12  Copper Lamp Post", "~1.8 blocks tall · weathered copper",
     [Box(2, 0, 2, 14, 3, 14, cut_copper), Box(6, 3, 6, 10, 18, 10, copper),
      Box(3, 18, 3, 13, 20, 13, cut_copper), Box(5, 20, 5, 11, 26, 11, lamp),
      *[Box(x, 20, z, x + 1, 26, z + 1, copper) for x, z in [(4, 4), (11, 4), (4, 11), (11, 11)]],
      Box(2, 26, 2, 14, 28, 14, cut_copper), Box(7, 28, 7, 9, 30, 9, copper)]),
    ("13  Echo Stone", "Ancient City · deepslate & sculk",
     [Box(0, 0, 0, 16, 10, 16, deepslate_sculk), Box(2, 10, 2, 14, 12, 14, sculk),
      *[Box(x, 12, z, x + 2, 17, z + 2, bone) for x, z in [(2, 2), (12, 2), (2, 12), (12, 12)]],
      Box(6, 12, 6, 10, 13, 10, lambda f, a, b, w: (TEAL[2], True))]),
    ("14  Amethyst Geode", "Natural crystal cluster",
     [Box(0, 0, 0, 16, 3, 16, calcite), Box(1, 3, 1, 15, 5, 15, basalt),
      *[Box(x0, 5, z0, x1, top, z1, amethyst) for x0, z0, x1, z1, top in spikes],
      *[Box(x0 + 1, top, z0 + 1, x1 - 1, top + 2, z1 - 1, amethyst) for x0, z0, x1, z1, top in spikes]]),
    ("15  Cherry Torii", "~1.7 blocks tall · walk-through gate",
     [Box(0, 0, 6, 4, 2, 10, stone_bricks), Box(12, 0, 6, 16, 2, 10, stone_bricks),
      Box(1, 2, 7, 3, 24, 9, cherry_log), Box(13, 2, 7, 15, 24, 9, cherry_log),
      Box(-2, 24, 6.5, 18, 26, 9.5, cherry_planks), Box(0, 19, 7.5, 16, 20.5, 8.5, cherry_planks),
      Box(3, 2, 7.6, 13, 19, 8.4, petal_portal)]),
    ("16  Desert Sun Pillar", "~1.6 blocks tall · sandstone & lapis",
     [Box(0, 0, 0, 16, 3, 16, sandstone), Box(1, 3, 1, 15, 5, 15, sandstone),
      Box(4, 5, 4, 12, 20, 12, glyph(sandstone, LAPIS, 5, 17, EYE)),
      Box(3, 20, 3, 13, 22, 13, sandstone), Box(5, 22, 5, 11, 24, 11, gold), Box(7, 24, 7, 9, 26, 9, gold)]),
]

COLS, CW, CH = 2, 420, 470
sheet = Image.new("RGB", (COLS * CW, math.ceil(len(designs) / COLS) * CH), (24, 20, 32))
d = ImageDraw.Draw(sheet)
for i, (name, note, boxes) in enumerate(designs):
    cx, cy = (i % COLS) * CW, (i // COLS) * CH
    d.rounded_rectangle([cx + 8, cy + 8, cx + CW - 8, cy + CH - 8], 14, fill=(36, 30, 48))
    render([ground()] + boxes, cx + CW / 2, cy + 300, d)
    d.text((cx + 24, cy + 20), name, font=FONT, fill=(236, 214, 255))
    d.text((cx + 24, cy + 50), note, font=SMALL, fill=(180, 170, 200))
sheet.save(os.path.join(ROOT, "docs", "images", "concepts-2.png"))
print("saved", sheet.size)
