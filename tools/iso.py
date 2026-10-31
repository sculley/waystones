"""Tiny isometric voxel renderer for Waystones artwork. Units are 1/16 of a block, same as Bedrock geometry."""
import math
from PIL import Image, ImageDraw, ImageFont

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "Waystones_RP", "textures", "blocks")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
S = 5.2  # screen px per 1/16 block
FONT = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 22)
SMALL = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", 15)


def h(*v):
    n = 0
    for i, x in enumerate(v):
        n = (n * 31 + int(x) * (73856093 if i % 2 else 19349663)) & 0xFFFFFFFF
    n ^= n >> 13
    n = (n * 1274126177) & 0xFFFFFFFF
    return (n & 0xFFFF) / 0xFFFF


def mix(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def noisy(base, a, b, c, amt=0.12):
    return mix(base, 1 + (h(a, b, c) - 0.5) * 2 * amt)


PURPLE = [(58, 24, 104), (98, 42, 168), (150, 78, 230), (196, 140, 255), (236, 214, 255), (255, 255, 255)]
GLOW = "glow"  # marker: second value in a (colour, glow) tuple


# ---------- materials: f(face, a, b, local) -> (rgb, emissive) ----------
# face: "up" | "south" | "east"; (a, b) texel coords on that face, world-aligned.

def stone(face, a, b, w):
    return noisy((118, 116, 128), a, b, hash(face) % 97), False


def stone_bricks(face, a, b, w):
    row = b // 4
    off = 4 if row % 2 else 0
    if b % 4 == 3 or (a + off) % 8 == 7:
        return (54, 52, 62), False
    return noisy((120, 118, 132), a, b, 3), False


def dark_stone(face, a, b, w):
    return noisy((70, 66, 82), a, b, 5, 0.15), False


def obsidian(face, a, b, w):
    return noisy((30, 18, 46), a, b, 7, 0.35), False


def amethyst(face, a, b, w):
    t = (a + b) % 4
    return [PURPLE[3], PURPLE[4], PURPLE[2], PURPLE[3]][t], True


def portal(face, a, b, w):
    ang = math.sin(a * 0.7 + b * 0.45) + math.cos(b * 0.6 - a * 0.3)
    return PURPLE[2 + int((ang + 2) / 4 * 3)], True


def gold(face, a, b, w):
    return noisy((226, 176, 60), a, b, 9, 0.1), False


def deepslate_tiles(face, a, b, w):
    if a % 8 in (0,) or b % 8 in (0,):
        return (28, 28, 34), False
    return noisy((58, 58, 66), a, b, 11, 0.15), False


def end_stone(face, a, b, w):
    return noisy((222, 220, 158), a, b, 13, 0.08), False


def purpur(face, a, b, w):
    if a % 8 == 0 or b % 8 == 0:
        return (128, 84, 128), False
    return noisy((170, 120, 170), a, b, 15, 0.08), False


def grass(face, a, b, w):
    if face == "up":
        return noisy((96, 156, 66), a, b, 17, 0.12), False
    return noisy((120, 86, 58), a, b, 19, 0.15) if b < -3 else noisy((96, 156, 66), a, b, 17), False


def textured(top_png, side_png, bottom_png=None):
    top, side = Image.open(f"{RP}/{top_png}").convert("RGB"), Image.open(f"{RP}/{side_png}").convert("RGB")
    def m(face, a, b, w):
        img = top if face == "up" else side
        c = img.getpixel((a % 16, 15 - (b % 16)) if face != "up" else (a % 16, b % 16))
        glow = c[2] > c[1] + 50  # purple pixels glow
        return c, glow
    return m


def rune_overlay(base, rune_cols, rune_rows, pattern):
    """Draw an emissive rune pattern onto side faces of a material."""
    def m(face, a, b, w):
        if face != "up":
            u = (a - rune_cols[0]) if face == "south" else (a - rune_cols[0])
            v = rune_rows[1] - b
            if 0 <= v < len(pattern) and 0 <= u < len(pattern[0]):
                ch = pattern[v][u]
                if ch == "P":
                    return PURPLE[2], True
                if ch == "L":
                    return PURPLE[3], True
                if ch == "W":
                    return PURPLE[5], True
        return base(face, a, b, w)
    return m


def themed_cube(frame, fill, accent):
    """Full-block variant: frame border, fill, glowing centre emblem."""
    def m(face, a, b, w):
        u, v = a % 16, b % 16
        edge = u in (0, 15) or v in (0, 15)
        if edge:
            return frame(face, a, b, w)
        d = math.hypot(u - 7.5, v - 7.5)
        if face == "up":
            if d < 3: return PURPLE[5 if d < 1.2 else 4], True
            if d < 5: return PURPLE[2 if (u + v) % 2 else 3], True
            if 5.5 < d < 6.5: return accent(face, a, b, w)
        else:
            diamond = abs(u - 7.5) + abs(v - 7.5)
            if diamond < 2: return PURPLE[5], True
            if diamond < 4: return PURPLE[3], True
            if 4.5 < diamond < 5.6: return accent(face, a, b, w)
        return fill(face, a, b, w)
    return m


# ---------- renderer ----------

class Box:
    def __init__(self, x0, y0, z0, x1, y1, z1, mat):
        self.lo, self.hi, self.mat = (x0, y0, z0), (x1, y1, z1), mat

    def contains(self, p):
        return all(self.lo[i] < p[i] < self.hi[i] for i in range(3))


def proj(x, y, z, ox, oy):
    return (ox + (x - z) * S * 0.866, oy + (x + z) * S * 0.5 - y * S)


def render(boxes, ox, oy, draw):
    quads = []
    for bx in boxes:
        (x0, y0, z0), (x1, y1, z1) = bx.lo, bx.hi
        def add(face, corners, a, b, centre, normal):
            probe = tuple(centre[i] + normal[i] * 0.05 for i in range(3))
            if any(o is not bx and o.contains(probe) for o in boxes):
                return
            col, glow = bx.mat(face, a, b, bx)
            shade = 1.0 if glow else {"up": 1.0, "south": 0.82, "east": 0.64}[face]
            quads.append((sum(centre), [proj(*c, ox, oy) for c in corners], mix(col, shade)))
        for x in range(math.floor(x0), math.ceil(x1)):
            for z in range(math.floor(z0), math.ceil(z1)):
                xa, xb, za, zb = max(x, x0), min(x + 1, x1), max(z, z0), min(z + 1, z1)
                add("up", [(xa, y1, za), (xb, y1, za), (xb, y1, zb), (xa, y1, zb)], x, z,
                    ((xa + xb) / 2, y1, (za + zb) / 2), (0, 1, 0))
        for x in range(math.floor(x0), math.ceil(x1)):
            for y in range(math.floor(y0), math.ceil(y1)):
                xa, xb, ya, yb = max(x, x0), min(x + 1, x1), max(y, y0), min(y + 1, y1)
                add("south", [(xa, ya, z1), (xb, ya, z1), (xb, yb, z1), (xa, yb, z1)], x, y,
                    ((xa + xb) / 2, (ya + yb) / 2, z1), (0, 0, 1))
        for z in range(math.floor(z0), math.ceil(z1)):
            for y in range(math.floor(y0), math.ceil(y1)):
                za, zb, ya, yb = max(z, z0), min(z + 1, z1), max(y, y0), min(y + 1, y1)
                add("east", [(x1, ya, za), (x1, ya, zb), (x1, yb, zb), (x1, yb, za)], z, y,
                    (x1, (ya + yb) / 2, (za + zb) / 2), (1, 0, 0))
    for _, pts, col in sorted(quads, key=lambda q: q[0]):
        draw.polygon(pts, fill=col)


def ground():
    return Box(-8, -3, -8, 24, 0, 24, grass)
