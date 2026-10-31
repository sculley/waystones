"""Original pixel art for the Waystones add-on (16x16 textures + pack icon)."""
import math
import random
import sys
from PIL import Image

import os
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(7)

STONE = [(74, 72, 84), (92, 90, 103), (108, 106, 120), (124, 122, 137), (140, 138, 152)]
MORTAR = (52, 50, 60)
PURPLE = [(58, 24, 104), (98, 42, 168), (150, 78, 230), (196, 140, 255), (236, 214, 255), (255, 255, 255)]
GOLD = [(96, 62, 18), (160, 112, 34), (222, 172, 58), (255, 226, 120)]


def stone_px(x, y):
    return STONE[min(4, max(0, 2 + random.choice([-1, 0, 0, 0, 1])))]


def bricks(img, top_light=True):
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), stone_px(x, y))
    # Two rows of bricks with offset joints
    for y in range(16):
        for x in range(16):
            row = y // 4
            off = 4 if row % 2 else 0
            if y % 4 == 3 or (x + off) % 8 == 7:
                img.putpixel((x, y), MORTAR)
            elif top_light and y % 4 == 0:
                img.putpixel((x, y), STONE[3])


def side():
    img = Image.new("RGBA", (16, 16))
    bricks(img)
    # recessed panel
    for y in range(2, 14):
        for x in range(4, 12):
            img.putpixel((x, y), STONE[0] if (x in (4, 11) or y in (2, 13)) else MORTAR)
    rune = [
        "...LL...",
        "..LPPL..",
        ".LP..PL.",
        "..LPPL..",
        "...PP...",
        ".L.PP.L.",
        "LPPWWPPL",
        ".L.PP.L.",
        "...PP...",
        "...LL...",
    ]
    colours = {"P": PURPLE[2], "L": PURPLE[3], "W": PURPLE[5]}
    for j, row in enumerate(rune):
        for i, c in enumerate(row):
            if c in colours:
                img.putpixel((4 + i, 3 + j), colours[c])
    # glow bleed onto panel
    for y in range(3, 13):
        for x in range(5, 11):
            if img.getpixel((x, y)) == MORTAR:
                img.putpixel((x, y), PURPLE[0])
    return img


def top():
    img = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), stone_px(x, y))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if x in (0, 15) or y in (0, 15):
                img.putpixel((x, y), STONE[0])
            elif d > 7.2:
                continue
            elif d > 6.2:
                img.putpixel((x, y), MORTAR)
            elif d > 5.2:
                img.putpixel((x, y), STONE[3] if (x + y) % 3 else STONE[4])
            elif d > 4.3:
                img.putpixel((x, y), MORTAR)
            else:
                # swirling portal
                ang = math.atan2(y - 7.5, x - 7.5) + d * 0.9
                band = (math.sin(ang * 3) + 1) / 2
                level = 1 + int(band * 2) + (2 if d < 1.5 else 1 if d < 2.6 else 0)
                img.putpixel((x, y), PURPLE[min(5, level)])
    # four runes at compass points
    for x, y in [(7, 2), (8, 2), (7, 13), (8, 13), (2, 7), (2, 8), (13, 7), (13, 8)]:
        img.putpixel((x, y), PURPLE[3])
    return img


def bottom():
    img = Image.new("RGBA", (16, 16))
    bricks(img, top_light=False)
    return img


def wayfinder():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    cx, cy = 7.5, 8.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            if d <= 6.9:
                if d > 5.9:
                    img.putpixel((x, y), GOLD[0])
                elif d > 4.9:
                    img.putpixel((x, y), GOLD[3] if (x - cx) + (y - cy) < -2 else GOLD[2] if y < cy + 2 else GOLD[1])
                else:
                    shade = 1 if (x - cx) + (y - cy) > 2 else 2
                    img.putpixel((x, y), PURPLE[shade])
    # loop at top
    for x, y in [(6, 0), (7, 0), (8, 0), (9, 0), (6, 1), (9, 1)]:
        img.putpixel((x, y), GOLD[2] if y == 0 else GOLD[1])
    # four-point star needle
    star = {(7, 4): 4, (8, 4): 4, (7, 5): 4, (8, 5): 4, (7, 6): 5, (8, 6): 5,
            (4, 8): 4, (5, 8): 4, (6, 8): 5, (9, 8): 5, (10, 8): 4, (11, 8): 4,
            (4, 9): 3, (11, 9): 3, (6, 9): 5, (9, 9): 5,
            (7, 7): 5, (8, 7): 5, (7, 8): 5, (8, 8): 5, (7, 9): 5, (8, 9): 5,
            (7, 10): 5, (8, 10): 5, (7, 11): 4, (8, 11): 4, (7, 12): 3, (8, 12): 3}
    for (x, y), lvl in star.items():
        img.putpixel((x, y), PURPLE[lvl])
    img.putpixel((5, 6), PURPLE[4])  # glint
    return img


def pack_icon(side_img, top_img, item):
    size = 256
    icon = Image.new("RGBA", (size, size))
    for y in range(size):
        for x in range(size):
            t = math.hypot(x - 128, y - 128) / 181
            a, b = (60, 26, 110), (18, 10, 34)
            icon.putpixel((x, y), tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,))
    # isometric-ish block: top face skewed above side face
    face = side_img.resize((128, 128), Image.NEAREST)
    lid = top_img.resize((128, 48), Image.NEAREST)
    icon.paste(lid, (52, 44))
    icon.paste(face, (52, 92))
    charm = item.resize((96, 96), Image.NEAREST)
    icon.alpha_composite(charm, (150, 146))
    return icon


s, t, b, w = side(), top(), bottom(), wayfinder()
s.save(f"{OUT}/Waystones_RP/textures/blocks/wst_waystone_side.png")
t.save(f"{OUT}/Waystones_RP/textures/blocks/wst_waystone_top.png")
b.save(f"{OUT}/Waystones_RP/textures/blocks/wst_waystone_bottom.png")
w.save(f"{OUT}/Waystones_RP/textures/items/wst_wayfinder.png")
ic = pack_icon(s, t, w)
ic.save(f"{OUT}/Waystones_RP/pack_icon.png")
ic.save(f"{OUT}/Waystones_BP/pack_icon.png")


# ---------- Waystones Guide icon ----------
# K outline, C cover purple, c cover dark, H cover light, P pages, p page shade, G gold, g gold dark, W glow
art = [
    "................",
    "...KKKKKKKKKK...",
    "..KHHHHHHHHHCK..",
    "..KHCCCCCCCCcKP.",
    "..KHCGGGGGGCcKP.",
    "..KHCG....GCcKP.",
    "..KHCC.GG.CCcKP.",
    "..KHCCGWWGCCcKP.",
    "..KHCC.GG.CCcKP.",
    "..KHCG....GCcKP.",
    "..KHCGGGGGGCcKP.",
    "..KHCCCCCCCCcKP.",
    "..KHccccccccckp.",
    "..KPPPPPPPPPPPp.",
    "...KKKKKKKKKKKK.",
    "................",
]
pal = {"K": (34, 16, 56), "C": (110, 50, 180), "c": (78, 32, 132), "H": (160, 96, 230),
       "P": (236, 226, 200), "p": (190, 176, 150), "G": (226, 176, 60), "g": (150, 104, 30),
       "W": (255, 240, 255), ".": None, "k": (34, 16, 56)}
art = [r.replace(".GG.", "gGGg") if i in (6, 8) else r for i, r in enumerate(art)]
img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
for y, row in enumerate(art):
    for x, ch in enumerate(row):
        if pal.get(ch): img.putpixel((x, y), pal[ch] + (255,))
img.save(f"{OUT}/Waystones_RP/textures/items/wst_guide.png")
