"""Recipe artwork.

docs/images/recipes.png           crafting grids for the README
Waystones_RP/font/glyph_E5.png    the same icons as font glyphs, so the in-game
                                  guide can draw recipes inside its text
                                  (character U+E5xx = cell xx, row-major, 16 per row)

Ingredient icons are original pixel art drawn here, not copies of game textures.
"""
import math
import os

from PIL import Image, ImageDraw

import iso
from iso import Box, ROOT, textured
from render_docs import IMAGES, ITEMS, LILAC, MUTED, background, paste_text

# ---------- 16x16 pixel icons ----------

def blank():
    return Image.new("RGBA", (16, 16), (0, 0, 0, 0))


def from_rows(rows, palette):
    img = blank()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in palette:
                img.putpixel((x, y), palette[ch] + (255,))
    return img


def stone_bricks():
    img = blank()
    for y in range(16):
        for x in range(16):
            off = 4 if (y // 4) % 2 else 0
            if y % 4 == 3 or (x + off) % 8 == 7:
                c = (64, 62, 72)
            else:
                c = iso.noisy((126, 124, 136), x, y, 3, 0.1)
            img.putpixel((x, y), c + (255,))
    return img


def obsidian():
    img = blank()
    for y in range(16):
        for x in range(16):
            r = iso.h(x, y, 7)
            c = (86, 56, 120) if r > 0.9 else iso.noisy((30, 18, 46), x, y, 7, 0.35)
            img.putpixel((x, y), c + (255,))
    return img


def amethyst_shard():
    return from_rows([
        "................",
        "..........ddd...",
        ".........dLWWd..",
        "........dLLWLd..",
        ".......dPLLLLd..",
        "......dPPLLLd...",
        ".....dPPPLLd....",
        "....dPPPPLd.....",
        "...dPPPPLd......",
        "..dPPPPPd.......",
        "..dPPPPd........",
        "..dPPPd.........",
        "...ddd..........",
        "................",
        "................",
        "................",
    ], {"d": (62, 26, 110), "P": (128, 66, 200), "L": (180, 128, 250), "W": (240, 220, 255)})


def ender_pearl():
    img = blank()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 6.2:
                continue
            if d > 5.2:
                c = (10, 50, 46)
            elif d < 2:
                c = (16, 70, 62)
            else:
                c = (36, 132, 112) if (x + y) % 5 else (52, 160, 136)
            img.putpixel((x, y), c + (255,))
    for x, y in [(5, 4), (6, 4), (5, 5)]:
        img.putpixel((x, y), (190, 250, 230, 255))
    return img


def compass():
    img = blank()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 6.6:
                continue
            c = (60, 60, 70) if d > 5.6 else (150, 150, 162) if d > 4.6 else (214, 214, 222)
            img.putpixel((x, y), c + (255,))
    for i in range(4):  # needle: red half points north-east
        img.putpixel((8 + i, 7 - i), (210, 40, 40, 255))
        img.putpixel((7 - i, 8 + i), (90, 90, 100, 255))
    img.putpixel((7, 7), (40, 40, 48, 255))
    img.putpixel((8, 8), (40, 40, 48, 255))
    return img


def book():
    img = blank()
    d = ImageDraw.Draw(img)
    d.rectangle([3, 2, 12, 13], fill=(120, 66, 36, 255))      # cover
    d.rectangle([11, 3, 13, 14], fill=(236, 228, 206, 255))   # page edges
    d.line([(11, 14), (13, 14)], fill=(190, 180, 160, 255))
    d.rectangle([3, 2, 4, 13], fill=(84, 44, 22, 255))        # spine
    d.rectangle([6, 5, 9, 6], fill=(160, 100, 60, 255))       # label
    return img


def arrow():
    return from_rows([
        "................",
        "................",
        "................",
        "................",
        "........LL......",
        "........LLL.....",
        "..LLLLLLLLLL....",
        "..LLLLLLLLLLL...",
        "..LLLLLLLLLLL...",
        "..LLLLLLLLLL....",
        "........LLL.....",
        "........LL......",
        "................",
        "................",
        "................",
        "................",
    ], {"L": LILAC})


def plus():
    return from_rows(["................"] * 5 + ["......LLLL......"] * 0 + [
        ".......LL.......", ".......LL.......", "....LLLLLLLL....", "....LLLLLLLL....",
        ".......LL.......", ".......LL.......",
    ] + ["................"] * 5, {"L": LILAC})


def item(name):
    return Image.open(os.path.join(ITEMS, name)).convert("RGBA")


PIXEL_ICONS = {
    "stone_bricks": stone_bricks(), "amethyst_shard": amethyst_shard(), "ender_pearl": ender_pearl(),
    "obsidian": obsidian(), "compass": compass(), "book": book(),
    "wayfinder": item("wst_wayfinder.png"), "guide": item("wst_guide.png"),
}
NAMES = {"stone_bricks": "Stone Bricks", "amethyst_shard": "Amethyst Shard", "ender_pearl": "Ender Pearl",
         "obsidian": "Obsidian", "compass": "Compass", "book": "Book"}


def waystone_icon(size):
    """Small isometric waystone block that fits a size x size square."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    iso.S = size / 32.5
    d = ImageDraw.Draw(canvas)
    iso.render([Box(0, 0, 0, 16, 16, 16, textured("wst_waystone_top.png", "wst_waystone_side.png"))],
               size / 2, size / 2, d)
    return canvas


def icon(name, size):
    if name == "waystone":
        return waystone_icon(size)
    return PIXEL_ICONS[name].resize((size, size), Image.NEAREST)


# ---------- slots ----------
SLOT_IN, SLOT_DARK, SLOT_LIGHT = (52, 40, 76), (20, 12, 34), (96, 72, 136)


def slot(size, border):
    img = Image.new("RGBA", (size, size), SLOT_IN + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, size - 1, border - 1], fill=SLOT_DARK)
    d.rectangle([0, 0, border - 1, size - 1], fill=SLOT_DARK)
    d.rectangle([0, size - border, size - 1, size - 1], fill=SLOT_LIGHT)
    d.rectangle([size - border, 0, size - 1, size - 1], fill=SLOT_LIGHT)
    return img


def slot_with(name, size, border, icon_size):
    s = slot(size, border)
    if name:
        ic = icon(name, icon_size)
        o = (size - icon_size) // 2
        s.alpha_composite(ic, (o, o))
    return s


# ---------- recipes (mirrors Waystones_BP/recipes) ----------
S, A, E, O, C, B = "stone_bricks", "amethyst_shard", "ender_pearl", "obsidian", "compass", "book"
RECIPES = [
    ("Waystone", "Crafting table", [[S, A, S], [S, E, S], [O, O, O]], "waystone"),
    ("Wayfinder", "Crafting table", [[None, A, None], [E, C, E], [None, A, None]], "wayfinder"),
    ("Waystones Guide", "Any arrangement", [[None, None, None], [B, A, None], [None, None, None]], "guide"),
]


def readme_image():
    W, H = 1200, 490
    img = background(W, H, stars=40).convert("RGBA")
    d = ImageDraw.Draw(img)
    cw, SL, GAP, RS = W // 3, 60, 4, 76
    for i, (title, note, grid, result) in enumerate(RECIPES):
        x0 = i * cw
        cx = x0 + cw // 2
        d.rounded_rectangle([x0 + 16, 16, x0 + cw - 16, 352], 18, fill=(36, 26, 56), outline=(86, 56, 140), width=2)
        paste_text(img, title, 10, LILAC, 3, cx, 40)
        grid_w = 3 * SL + 2 * GAP
        total = grid_w + 16 + 40 + 16 + RS
        gx, gy = cx - total // 2, 108
        for r, row in enumerate(grid):
            for c, name in enumerate(row):
                img.alpha_composite(slot_with(name, SL, 4, 48), (gx + c * (SL + GAP), gy + r * (SL + GAP)))
        mid = gy + grid_w // 2
        img.alpha_composite(arrow().resize((48, 48), Image.NEAREST), (gx + grid_w + 12, mid - 24))
        img.alpha_composite(slot_with(result, RS, 4, 64), (gx + grid_w + 72, mid - RS // 2))
        paste_text(img, note, 10, MUTED, 2, cx, 316)
    # ingredient key: two rows of three
    keys = list(NAMES)
    kw = (W - 32) // 3
    for i, k in enumerate(keys):
        x, y = 16 + (i % 3) * kw, 372 + (i // 3) * 52
        img.alpha_composite(slot_with(k, 44, 3, 32), (x + 70, y))
        paste_text(img, NAMES[k], 9, MUTED, 2, x + 130 + 90, y + 12)
    img.convert("RGB").save(os.path.join(IMAGES, "recipes.png"))


# ---------- glyph sheet ----------
CELL = 48  # 16 x 48 = 768 px sheet
GLYPHS = ["slot", S, A, E, O, C, B, "waystone", "wayfinder", "guide", "arrow", "plus"]


def glyph_sheet():
    sheet = Image.new("RGBA", (16 * CELL, 16 * CELL), (0, 0, 0, 0))
    for i, name in enumerate(GLYPHS):
        if name == "arrow":
            g = arrow().resize((CELL, CELL), Image.NEAREST)
        elif name == "plus":
            g = plus().resize((CELL, CELL), Image.NEAREST)
        else:
            g = slot_with(None if name == "slot" else name, CELL, 3, 36)
        sheet.alpha_composite(g, ((i % 16) * CELL, (i // 16) * CELL))
    out = os.path.join(ROOT, "Waystones_RP", "font")
    os.makedirs(out, exist_ok=True)
    sheet.save(os.path.join(out, "glyph_E5.png"))


if __name__ == "__main__":
    readme_image()
    glyph_sheet()
    print("rendered recipes.png and glyph_E5.png:", ", ".join(f"{n}=U+E5{i:02X}" for i, n in enumerate(GLYPHS)))
