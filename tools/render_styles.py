"""Style sheet: 4 waystone shapes x 3 themes (docs/images/styles.png)."""
import math, os
from PIL import Image, ImageDraw
from iso import *
from iso import ROOT

# ---------- palettes (dark -> white, same layout as PURPLE) ----------
SOUL = [(10, 50, 60), (20, 110, 130), (40, 170, 190), (110, 230, 240), (200, 255, 255), (255, 255, 255)]
ENDP = [(40, 20, 60), (120, 70, 150), (200, 150, 225), (232, 200, 245), (250, 238, 255), (255, 255, 255)]


# ---------- theme materials ----------
def blackstone(face, a, b, w):
    return noisy((42, 36, 44), a, b, 31, 0.2), False


def blackstone_bricks(face, a, b, w):
    if b % 4 == 3 or (a + (4 if (b // 4) % 2 else 0)) % 8 == 7:
        return (22, 18, 26), False
    return noisy((52, 46, 56), a, b, 33, 0.15), False


def end_stone_bricks(face, a, b, w):
    if b % 4 == 3 or (a + (4 if (b // 4) % 2 else 0)) % 8 == 7:
        return (176, 172, 120), False
    return noisy((226, 224, 166), a, b, 35, 0.06), False


def purpur_pillar(face, a, b, w):
    if face == "up":
        return purpur(face, a, b, w)
    return noisy((168, 120, 168) if a % 4 else (136, 92, 136), a, b, 37, 0.06), False


def crystal(pal):
    def m(face, a, b, w):
        return [pal[3], pal[4], pal[2], pal[3]][(a + b) % 4], True
    return m


def swirl(pal):
    def m(face, a, b, w):
        ang = math.sin(a * 0.7 + b * 0.45) + math.cos(b * 0.6 - a * 0.3)
        return pal[2 + int((ang + 2) / 4 * 3)], True
    return m


def starfield(face, a, b, w):  # End-gateway style
    r = h(a, b, 39)
    if r > 0.93:
        return ENDP[5], True
    if r > 0.82:
        return [(90, 200, 190), (190, 150, 240)][int(r * 100) % 2], True
    return noisy((14, 20, 30), a, b, 41, 0.4), True


def runes(base, pal, x0, top, pattern):
    def m(face, a, b, w):
        if face != "up":
            u, v = a - x0, top - b
            if 0 <= v < len(pattern) and 0 <= u < len(pattern[0]):
                ch = pattern[v][u]
                if ch in "LPW":
                    return pal[{"P": 2, "L": 3, "W": 5}[ch]], True
        return base(face, a, b, w)
    return m


def cube(frame, fill, accent, pal):
    """Full-block variant: frame border, fill, glowing centre emblem."""
    def m(face, a, b, w):
        u, v = a % 16, b % 16
        if u in (0, 15) or v in (0, 15):
            return frame(face, a, b, w)
        d = math.hypot(u - 7.5, v - 7.5)
        if face == "up":
            if d < 3: return pal[5 if d < 1.2 else 4], True
            if d < 5: return pal[2 if (u + v) % 2 else 3], True
            if 5.5 < d < 6.5: return accent(face, a, b, w)
        else:
            dm = abs(u - 7.5) + abs(v - 7.5)
            if dm < 2: return pal[5], True
            if dm < 4: return pal[3], True
            if 4.5 < dm < 5.6: return accent(face, a, b, w)
        return fill(face, a, b, w)
    return m


THEMES = {
    "Classic": dict(base=stone_bricks, core=dark_stone, trim=stone_bricks, floor=obsidian,
                    glow=amethyst, portal=portal, pal=PURPLE),
    "Nether": dict(base=blackstone_bricks, core=blackstone, trim=gold, floor=blackstone,
                   glow=crystal(SOUL), portal=swirl(SOUL), pal=SOUL),
    "End": dict(base=end_stone_bricks, core=purpur, trim=purpur_pillar, floor=obsidian,
                glow=crystal(ENDP), portal=starfield, pal=ENDP),
}

RUNE = ["..LL..", ".LPPL.", "..PP..", "LPWWPL", "..PP..", "..PP..", ".LPPL.", "..LL.."]


# ---------- shapes ----------
def block(t, name):
    if name == "Classic":
        return [Box(0, 0, 0, 16, 16, 16, textured("wst_waystone_top.png", "wst_waystone_side.png"))]
    fill = blackstone_bricks if name == "Nether" else end_stone_bricks
    frame = gold if name == "Nether" else purpur
    return [Box(0, 0, 0, 16, 16, 16, cube(frame, fill, frame, t["pal"]))]


def obelisk(t, name):
    return [Box(0, 0, 0, 16, 3, 16, t["base"]), Box(2, 3, 2, 14, 5, 14, t["trim"]),
            Box(4, 5, 4, 12, 15, 12, runes(t["core"], t["pal"], 5, 13, RUNE)),
            Box(5, 15, 5, 11, 22, 11, t["core"]), Box(6, 22, 6, 10, 27, 10, t["glow"])]


def arch(t, name):
    return [Box(0, 0, 4, 16, 2, 12, t["base"]), Box(0, 2, 5, 3, 25, 11, t["base"]),
            Box(13, 2, 5, 16, 25, 11, t["base"]), Box(-1, 25, 4, 17, 28, 12, t["trim"]),
            Box(6, 28, 6, 10, 30, 10, t["glow"]), Box(3, 2, 7, 13, 25, 9, t["portal"])]


def pad(t, name):
    corners = [(0, 0), (14, 0), (0, 14), (14, 14)]
    return [Box(0, 0, 0, 16, 2, 16, t["base"]), Box(2, 2, 2, 14, 3, 14, t["floor"]),
            Box(4, 3, 4, 12, 3.4, 12, t["portal"]),
            *[Box(x, 2, z, x + 2, 7, z + 2, t["trim"] if name == "Nether" else t["core"]) for x, z in corners],
            *[Box(x + 0.5, 7, z + 0.5, x + 1.5, 9, z + 1.5, t["glow"]) for x, z in corners]]


SHAPES = [("Rune Block", "1 block", block), ("Obelisk", "1.7 blocks", obelisk),
          ("Arch Gate", "1.9 blocks", arch), ("Teleport Pad", "0.6 blocks", pad)]

COLS, CW, CH, HEAD = 3, 360, 400, 70
sheet = Image.new("RGB", (COLS * CW, len(SHAPES) * CH), (24, 20, 32))
d = ImageDraw.Draw(sheet)
for r, (shape, size, fn) in enumerate(SHAPES):
    for c, (tname, t) in enumerate(THEMES.items()):
        cx, cy = c * CW, r * CH
        d.rounded_rectangle([cx + 8, cy + 8, cx + CW - 8, cy + CH - 8], 14, fill=(36, 30, 48))
        render([ground()] + fn(t, tname), cx + CW / 2, cy + 270, d)
        d.text((cx + 22, cy + 20), f"{shape} · {tname}", font=FONT, fill=(236, 214, 255))
        d.text((cx + 22, cy + 50), size, font=SMALL, fill=(180, 170, 200))
sheet.save(os.path.join(ROOT, "docs", "images", "styles.png"))
print("saved", sheet.size)
