"""Draws the 16x16 placeholder sprites for the prototype.

Run from the project folder:  python3 tools/make_placeholder_art.py
Replace any PNG in art/ with your own 16x16 drawing of the same name and the
game will use it automatically. (Don't re-run this script afterwards, or it
will overwrite your art.)
"""
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "art"
CLEAR = (0, 0, 0, 0)


def hexc(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def new():
    return Image.new("RGBA", (16, 16), CLEAR)


def disc(img, cx, cy, r, color):
    for y in range(16):
        for x in range(16):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                img.putpixel((x, y), color)


def ring(img, cx, cy, r, color, thickness=1.0):
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r - thickness < d <= r:
                img.putpixel((x, y), color)


def rect(img, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            img.putpixel((x, y), color)


def px(img, points, color):
    for p in points:
        img.putpixel(p, color)


def save(img, rel):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def speckle(img, colors, count, seed):
    rng = random.Random(seed)
    for _ in range(count):
        img.putpixel((rng.randrange(16), rng.randrange(16)), rng.choice(colors))


# --- Tiles ------------------------------------------------------------------

def floor():
    img = Image.new("RGBA", (16, 16), hexc("#7a3346"))
    speckle(img, [hexc("#86394f"), hexc("#6e2d3f")], 40, 1)
    rect(img, 0, 0, 15, 0, hexc("#6a2a3b"))
    rect(img, 0, 0, 0, 15, hexc("#6a2a3b"))
    return img


def rock():
    img = Image.new("RGBA", (16, 16), hexc("#3a1622"))
    speckle(img, [hexc("#2c1019"), hexc("#4a1d2b")], 50, 2)
    rect(img, 0, 0, 15, 1, hexc("#56243a"))
    return img


def spawn():
    img = floor()
    disc(img, 8, 8, 7, hexc("#1d0a1a"))
    ring(img, 8, 8, 7, hexc("#5c2a6e"), 1.2)
    ring(img, 8, 8, 4, hexc("#3d1a4a"), 1.0)
    return img


def base():
    img = floor()
    heart = hexc("#ff4d6d")
    dark = hexc("#b3203f")
    disc(img, 5.5, 6, 3.6, heart)
    disc(img, 10.5, 6, 3.6, heart)
    for y in range(7, 15):
        half = max(0, 7 - (y - 7))
        rect(img, 8 - half, y, 7 + half, y, heart) if half > 0 else None
    px(img, [(4, 5), (5, 4)], hexc("#ffb3c1"))
    px(img, [(12, 9), (11, 11), (9, 13)], dark)
    return img


# --- Units ------------------------------------------------------------------

def membrane():
    img = new()
    rect(img, 1, 1, 14, 14, hexc("#e9c46a"))
    rect(img, 1, 1, 14, 1, hexc("#f4dd9c"))
    rect(img, 1, 14, 14, 14, hexc("#b8923a"))
    for y in (4, 8, 12):
        for x in range(2, 14, 3):
            img.putpixel((x + (y // 4) % 2, y), hexc("#c9a24a"))
    return img


def clot():
    img = new()
    disc(img, 8, 8, 7.5, hexc("#8d1b2e"))
    disc(img, 6, 6, 3, hexc("#b02a40"))
    disc(img, 11, 10, 2.5, hexc("#a32438"))
    px(img, [(5, 4), (4, 5)], hexc("#e0566e"))
    ring(img, 8, 8, 7.5, hexc("#5a0f1c"))
    return img


def neutrophil():
    img = new()
    disc(img, 8, 8, 7, hexc("#d9c2f0"))
    ring(img, 8, 8, 7, hexc("#9b7bc4"))
    # Multi-lobed nucleus
    disc(img, 5.5, 7, 2.2, hexc("#6a3fa0"))
    disc(img, 9, 6, 2.2, hexc("#6a3fa0"))
    disc(img, 9.5, 10, 2.2, hexc("#6a3fa0"))
    return img


def b_cell():
    img = new()
    disc(img, 8, 8, 7, hexc("#9fd3ff"))
    ring(img, 8, 8, 7, hexc("#3c7fc4"))
    disc(img, 8, 9, 3.5, hexc("#2d5f99"))
    # Little antibody "Y"
    px(img, [(8, 2), (8, 3), (7, 1), (9, 1), (6, 0), (10, 0)], hexc("#ffffff"))
    return img


# --- Invaders ---------------------------------------------------------------

def rhinovirus():
    img = new()
    disc(img, 8, 8, 4.5, hexc("#7bd24a"))
    ring(img, 8, 8, 4.5, hexc("#3f8a22"))
    for i in range(8):
        a = i * math.tau / 8
        x, y = 8 + math.cos(a) * 6, 8 + math.sin(a) * 6
        img.putpixel((int(x), int(y)), hexc("#b6f58a"))
    px(img, [(7, 7), (9, 9)], hexc("#3f8a22"))
    return img


def bacterium():
    img = new()
    for x in range(3, 13):
        rect(img, x, 5, x, 10, hexc("#c6d84a"))
    disc(img, 3.5, 8, 3, hexc("#c6d84a"))
    disc(img, 12.5, 8, 3, hexc("#c6d84a"))
    rect(img, 3, 5, 12, 5, hexc("#e2ef8a"))
    px(img, [(5, 8), (8, 7), (11, 9)], hexc("#7d8a1f"))
    px(img, [(15, 9), (15, 11), (0, 6)], hexc("#a7b83a"))
    return img


def bacterium_half():
    img = new()
    disc(img, 8, 8, 3.5, hexc("#c6d84a"))
    ring(img, 8, 8, 3.5, hexc("#7d8a1f"))
    px(img, [(7, 7)], hexc("#e2ef8a"))
    return img


def worm():
    img = new()
    body = hexc("#c28a5a")
    for i, (x, y) in enumerate([(3, 12), (5, 10), (7, 8), (9, 6), (11, 5)]):
        disc(img, x, y, 2.6 if i < 4 else 3.2, body if i % 2 else hexc("#a8703f"))
    px(img, [(11, 4), (13, 5)], hexc("#2a1408"))
    px(img, [(13, 6), (14, 6)], hexc("#ff6b6b"))
    return img


def spore():
    img = new()
    disc(img, 8, 9, 3.5, hexc("#f0e6ff"))
    ring(img, 8, 9, 3.5, hexc("#a78bd6"))
    for x, y in [(2, 5), (14, 5), (3, 3), (13, 3), (4, 6), (12, 6)]:
        img.putpixel((x, y), hexc("#d8c8ff", 200))
    px(img, [(8, 9)], hexc("#a78bd6"))
    return img


if __name__ == "__main__":
    for name, fn in {
        "tiles/floor.png": floor, "tiles/rock.png": rock,
        "tiles/spawn.png": spawn, "tiles/base.png": base,
        "units/membrane.png": membrane, "units/clot.png": clot,
        "units/neutrophil.png": neutrophil, "units/b_cell.png": b_cell,
        "invaders/rhinovirus.png": rhinovirus, "invaders/bacterium.png": bacterium,
        "invaders/bacterium_half.png": bacterium_half, "invaders/worm.png": worm,
        "invaders/spore.png": spore,
    }.items():
        save(fn(), name)
    print("Placeholder art written to", ROOT)
