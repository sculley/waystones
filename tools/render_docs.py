"""README artwork: docs/images/banner.png and docs/images/items.png."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import iso
from iso import Box, FONT_DIR, ROOT, end_stone, grass, noisy, textured

IMAGES = os.path.join(ROOT, "docs", "images")
ITEMS = os.path.join(ROOT, "Waystones_RP", "textures", "items")
BG_TOP, BG_BOTTOM = (34, 16, 62), (10, 6, 22)
LILAC, MUTED = (236, 214, 255), (190, 176, 214)


def netherrack(face, a, b, w):
    return noisy((122, 40, 40), a, b, 21, 0.25), False


WAYSTONE = textured("wst_waystone_top.png", "wst_waystone_side.png")


def background(w, h, stars=90):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)))
    rnd = random.Random(3)
    for _ in range(stars):
        x, y, s = rnd.randrange(w), rnd.randrange(h), rnd.choice([2, 2, 2, 4])
        d.rectangle([x, y, x + s - 1, y + s - 1], fill=rnd.choice([(200, 180, 255), (150, 120, 220), (255, 255, 255)]))
    return img


def pixel_text(text, size, colour, scale):
    """Crisp blocky text: render small without antialiasing, then scale up."""
    font = ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", size)
    l, t, r, b = font.getbbox(text)
    small = Image.new("RGBA", (r - l + 2, b - t + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(small)
    d.fontmode = "1"
    d.text((1 - l, 1 - t), text, font=font, fill=colour)
    return small.resize((small.width * scale, small.height * scale), Image.NEAREST)


def paste_text(img, text, size, colour, scale, centre_x, top, shadow=(20, 8, 40)):
    sh = pixel_text(text, size, shadow + (255,), scale)
    fg = pixel_text(text, size, colour + (255,), scale)
    x = int(centre_x - fg.width / 2)
    img.paste(sh, (x + scale, top + scale), sh)
    img.paste(fg, (x, top), fg)


def glow_arc(img, p0, p1, lift):
    """Glowing dashed arc between two points."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mid = ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - lift)
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * mid[0] + t ** 2 * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * mid[1] + t ** 2 * p1[1]) for t in [i / 60 for i in range(61)]]
    d.line(pts, fill=(170, 100, 255, 90), width=14)
    blurred = layer.filter(ImageFilter.GaussianBlur(6))
    d2 = ImageDraw.Draw(blurred)
    for i in range(0, 60, 2):
        d2.line([pts[i], pts[i + 1]], fill=(236, 214, 255, 255), width=4)
    img.paste(blurred, (0, 0), blurred)


def banner():
    W, H = 1280, 490
    img = background(W, H)
    iso.S = 4.4
    d = ImageDraw.Draw(img)
    spots = [(300, 320, grass), (640, 340, netherrack), (980, 320, end_stone)]
    tops = []
    for x, y, ground_mat in spots:
        iso.render([Box(-6, -3, -6, 22, 0, 22, ground_mat), Box(0, 0, 0, 16, 16, 16, WAYSTONE)], x, y, d)
        tops.append((x, y - 8 * iso.S - 6))  # centre of the block top face
    glow_arc(img, tops[0], tops[1], 70)
    glow_arc(img, tops[1], tops[2], 70)
    paste_text(img, "WAYSTONES", 22, LILAC, 5, W / 2, 26)
    paste_text(img, "Teleport anywhere. Overworld · Nether · End.", 12, MUTED, 2, W / 2, 168)
    for (x, _, _), label in zip(spots, ["Overworld", "Nether", "The End"]):
        paste_text(img, label, 10, MUTED, 2, x, H - 38)
    img.save(os.path.join(IMAGES, "banner.png"))


def items():
    W, H = 1200, 400
    img = background(W, H, stars=40)
    d = ImageDraw.Draw(img)
    cards = [("Waystone", "Place, name and link"), ("Wayfinder", "Travel from anywhere"), ("Waystones Guide", "Every player gets one")]
    cw = W // 3
    for i, (name, note) in enumerate(cards):
        cx = i * cw + cw // 2
        d.rounded_rectangle([i * cw + 16, 16, (i + 1) * cw - 16, H - 16], 18, fill=(36, 26, 56), outline=(86, 56, 140), width=2)
        if i == 0:
            iso.S = 6.4
            iso.render([Box(0, 0, 0, 16, 16, 16, WAYSTONE)], cx, 120, d)
        else:
            icon = Image.open(os.path.join(ITEMS, ["wst_wayfinder.png", "wst_guide.png"][i - 1])).convert("RGBA")
            icon = icon.resize((176, 176), Image.NEAREST)
            img.paste(icon, (cx - 88, 70), icon)
        paste_text(img, name, 12, LILAC, 3, cx, 282)
        paste_text(img, note, 10, MUTED, 2, cx, 336)
    img.save(os.path.join(IMAGES, "items.png"))


if __name__ == "__main__":
    os.makedirs(IMAGES, exist_ok=True)
    banner()
    items()
    print("rendered banner.png and items.png")
