"""Draws the 16x16 placeholder sprites.

Run from the project folder:  python3 tools/make_placeholder_art.py
Unit sprites are generated from tools/content/*.json (one color per pack,
a different pattern per unit, and a corner badge on evolutions: a red arrow
for the power branch, a blue ring for the reach branch).

Replace any PNG in art/ with your own 16x16 drawing of the same name and the
game will use it automatically. Re-running this script overwrites art/, so
pass --only-missing once you've started drawing your own:
    python3 tools/make_placeholder_art.py --only-missing
"""
import colorsys
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
ROOT = PROJECT / "art"
CLEAR = (0, 0, 0, 0)
ONLY_MISSING = "--only-missing" in sys.argv


def hexc(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def shade(color, lightness):
    """Lighten (>0) or darken (<0) a color, keeping its hue."""
    r, g, b = (c / 255 for c in color[:3])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.0, min(1.0, l + lightness))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255), color[3])


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
    for y in range(max(0, y0), min(15, y1) + 1):
        for x in range(max(0, x0), min(15, x1) + 1):
            img.putpixel((x, y), color)


def px(img, points, color):
    for x, y in points:
        if 0 <= x < 16 and 0 <= y < 16:
            img.putpixel((x, y), color)


def speckle(img, colors, count, seed):
    rng = random.Random(seed)
    for _ in range(count):
        img.putpixel((rng.randrange(16), rng.randrange(16)), rng.choice(colors))


def save(img, rel):
    path = ROOT / rel
    if ONLY_MISSING and path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


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
    disc(img, 5.5, 6, 3.6, heart)
    disc(img, 10.5, 6, 3.6, heart)
    for y in range(7, 15):
        half = 7 - (y - 7)
        if half > 0:
            rect(img, 8 - half, y, 7 + half, y, heart)
    px(img, [(4, 5), (5, 4)], hexc("#ffb3c1"))
    px(img, [(12, 9), (11, 11), (9, 13)], hexc("#b3203f"))
    return img


# --- Units (generated from the content table) -------------------------------

def block_unit(color, style):
    """A wall: a chunky block with one of several surface patterns."""
    img = new()
    dark, light = shade(color, -0.22), shade(color, 0.15)
    rect(img, 1, 1, 14, 14, color)
    rect(img, 1, 1, 14, 1, light)
    rect(img, 1, 14, 14, 14, dark)
    rect(img, 1, 1, 1, 14, light)
    rect(img, 14, 1, 14, 14, dark)
    pattern = style % 5
    if pattern == 0:  # bricks
        for y in (5, 9):
            rect(img, 2, y, 13, y, dark)
        px(img, [(7, y) for y in range(2, 5)] + [(4, y) for y in range(6, 9)]
           + [(10, y) for y in range(6, 9)] + [(7, y) for y in range(10, 14)], dark)
    elif pattern == 1:  # fibers
        for i in range(-12, 16, 4):
            px(img, [(x, x - i) for x in range(2, 14) if 2 <= x - i <= 13], dark)
    elif pattern == 2:  # nodules
        for cx, cy in [(5, 5), (10, 6), (6, 10), (11, 11)]:
            disc(img, cx, cy, 1.8, dark)
            px(img, [(cx - 1, cy - 1)], light)
    elif pattern == 3:  # spikes on top
        for x in range(2, 14, 3):
            px(img, [(x, 0), (x, 1), (x + 1, 1)], light)
        rect(img, 3, 6, 12, 9, dark)
    else:  # dots
        for y in range(3, 14, 3):
            for x in range(3 + (y // 3) % 2, 14, 3):
                px(img, [(x, y)], dark)
    if style >= 5:  # second set of walls gets an inner frame
        rect(img, 3, 3, 12, 3, light)
        rect(img, 3, 12, 12, 12, dark)
    return img


def cell_unit(color, style):
    """An attacker: a round cell with one of several nucleus shapes."""
    img = new()
    body = shade(color, 0.18)
    edge = shade(color, -0.18)
    nucleus = shade(color, -0.32)
    radius = 6.5 + (style % 3) * 0.4
    disc(img, 8, 8, radius, body)
    ring(img, 8, 8, radius, edge)
    shape = style % 6
    if shape == 0:  # one big round nucleus
        disc(img, 8, 8.5, 3.2, nucleus)
    elif shape == 1:  # lobed nucleus
        for cx, cy in [(5.5, 7), (9, 6), (9.5, 10)]:
            disc(img, cx, cy, 2.1, nucleus)
    elif shape == 2:  # Y (antibody)
        px(img, [(8, y) for y in range(8, 13)] + [(7, 7), (6, 6), (5, 5), (9, 7), (10, 6), (11, 5)], nucleus)
        px(img, [(8, 9), (8, 10)], nucleus)
    elif shape == 3:  # ring nucleus
        ring(img, 8, 8, 3.5, nucleus, 1.2)
    elif shape == 4:  # granules
        for cx, cy in [(5, 6), (9, 5), (11, 9), (7, 10), (5, 10), (9, 8)]:
            px(img, [(cx, cy), (cx + 1, cy)], nucleus)
    else:  # star
        for i in range(6):
            a = i * math.tau / 6
            px(img, [(int(8 + math.cos(a) * r), int(8 + math.sin(a) * r)) for r in (1, 2, 3)], nucleus)
    if style >= 6:  # later units get a highlight and an outer membrane dot pattern
        px(img, [(5, 4), (4, 5)], shade(color, 0.4))
    if style >= 12:
        for i in range(8):
            a = i * math.tau / 8 + 0.4
            px(img, [(int(8 + math.cos(a) * (radius + 0.5)), int(8 + math.sin(a) * (radius + 0.5)))], edge)
    return img


def add_badge(img, branch):
    """Marks an evolution: red arrow (power branch) or blue ring (reach branch)."""
    if branch == 0:
        red, dark = hexc("#ff5a3c"), hexc("#7a1a0c")
        rect(img, 11, 0, 15, 5, dark)
        px(img, [(13, 1), (12, 2), (13, 2), (14, 2), (13, 3), (13, 4)], red)
        px(img, [(11, 3), (15, 3)], dark)
    else:
        blue, dark = hexc("#7fe0ff"), hexc("#0c3a52")
        rect(img, 11, 0, 15, 5, dark)
        ring(img, 13.5, 2.5, 2.2, blue, 1.0)
    return img


def unit_sprite(unit, pack_color, art_style="cells"):
    kind, style = unit["art"]
    color = hexc(pack_color)
    if art_style == "bugs":
        return garden_wall(color, style) if kind == "block" else bug_unit(color, style)
    if art_style == "animals":
        return farm_wall(color, style) if kind == "block" else animal_unit(color, style)
    return block_unit(color, style) if kind == "block" else cell_unit(color, style)


def pack_rows(content, all_content):
    """A world's packs: its own, or another world's with units renamed."""
    if "packs_from" not in content:
        return content["packs"]
    renames = content["renames"]
    result = []
    for pack in all_content[content["packs_from"]]["packs"]:
        copy = json.loads(json.dumps(pack))
        for unit in copy["units"]:
            unit["id"] = renames[unit["id"]][0]
            for evo in unit["evolutions"]:
                evo["id"] = renames[evo["id"]][0]
        result.append(copy)
    return result


# --- Backyard world ---------------------------------------------------------

def grass():
    img = Image.new("RGBA", (16, 16), hexc("#4f8a3a"))
    speckle(img, [hexc("#5c9a44"), hexc("#447a32"), hexc("#6aa84f")], 50, 11)
    for x, y in [(3, 4), (11, 9), (7, 13)]:
        px(img, [(x, y), (x, y - 1), (x + 1, y - 2)], hexc("#7cc25c"))
    rect(img, 0, 0, 15, 0, hexc("#437530"))
    rect(img, 0, 0, 0, 15, hexc("#437530"))
    return img


def stone():
    img = grass()
    disc(img, 8, 8.5, 6.5, hexc("#8a8a84"))
    disc(img, 6.5, 6.5, 3.5, hexc("#a3a39c"))
    ring(img, 8, 8.5, 6.5, hexc("#5e5e58"))
    px(img, [(10, 11), (11, 10), (5, 10)], hexc("#6f6f69"))
    return img


def dirt_hole():
    img = grass()
    disc(img, 8, 8, 6.5, hexc("#6b4a2b"))
    disc(img, 8, 8.5, 4, hexc("#2a1a0c"))
    ring(img, 8, 8, 6.5, hexc("#8a6440"))
    return img


def anthill():
    img = grass()
    for y in range(4, 15):
        half = (y - 3) * 0.7
        rect(img, int(8 - half), y, int(7 + half), y, hexc("#a8743f"))
    speckle(img, [hexc("#8a5c2f")], 0, 1)
    for x, y in [(6, 8), (9, 10), (5, 12), (10, 13), (8, 6)]:
        px(img, [(x, y)], hexc("#8a5c2f"))
    disc(img, 8, 5, 1.6, hexc("#2a1a0c"))
    px(img, [(7, 2), (8, 1)], hexc("#ffd23c"))  # a little crown: the queen lives here
    return img


def bug_unit(color, style):
    """An attacker drawn as a bug: body, head, legs and antennae."""
    img = new()
    body = shade(color, 0.05)
    dark = shade(color, -0.3)
    light = shade(color, 0.3)
    leg = shade(color, -0.4)
    width = 4.2 + (style % 3) * 0.6
    # legs
    for y in (6, 9, 12):
        px(img, [(int(8 - width) - 1, y), (int(8 - width) - 2, y + 1), (int(8 + width), y), (int(8 + width) + 1, y + 1)], leg)
    # abdomen and thorax
    for y in range(6, 15):
        w = width * (1 - ((y - 10) / 5.5) ** 2) ** 0.5 if abs(y - 10) < 5.5 else 0
        if w > 0.5:
            rect(img, int(round(8 - w)), y, int(round(7 + w)), y, body)
    disc(img, 8, 4.5, 2.6, dark)  # head
    px(img, [(6, 1), (5, 0), (10, 1), (11, 0)], leg)  # antennae
    pattern = style % 4
    if pattern == 0:  # wing seam
        px(img, [(8, y) for y in range(7, 14)], dark)
    elif pattern == 1:  # spots
        for x, y in [(6, 9), (10, 9), (7, 12), (9, 12)]:
            px(img, [(x, y)], dark)
    elif pattern == 2:  # stripes
        for y in (8, 11, 13):
            rect(img, int(8 - width) + 1, y, int(7 + width) - 1, y, dark)
    else:  # shine
        px(img, [(6, 8), (6, 9), (7, 8)], light)
    if style >= 6:  # mandibles for the later units
        px(img, [(6, 2), (10, 2)], light)
    return img


def garden_wall(color, style):
    """A wall drawn as a garden object, tinted with the pack color."""
    img = new()
    base = shade(color, -0.12)
    dark, light = shade(color, -0.35), shade(color, 0.2)
    kind = style % 5
    if kind == 0:  # stacked pebbles
        for cx, cy, r in [(5, 10, 4), (11, 10, 4), (8, 5, 4)]:
            disc(img, cx, cy, r, base)
            ring(img, cx, cy, r, dark)
            px(img, [(int(cx) - 1, int(cy) - 2)], light)
    elif kind == 1:  # moss mound
        disc(img, 8, 10, 6.5, base)
        for x, y in [(4, 8), (8, 5), (12, 8), (6, 11), (10, 12)]:
            disc(img, x, y, 1.5, light)
    elif kind == 2:  # stump / log end
        disc(img, 8, 8, 7, base)
        ring(img, 8, 8, 7, dark, 1.2)
        ring(img, 8, 8, 4, dark)
        px(img, [(8, 8)], dark)
    elif kind == 3:  # twigs
        for i in range(-6, 8, 3):
            px(img, [(x, x + i) for x in range(1, 15) if 1 <= x + i <= 14], base)
            px(img, [(x, x + i + 1) for x in range(1, 15) if 1 <= x + i + 1 <= 14], dark)
    else:  # web / mesh
        ring(img, 8, 8, 7, light)
        ring(img, 8, 8, 4, light)
        for i in range(8):
            a = i * math.tau / 8
            px(img, [(int(8 + math.cos(a) * r), int(8 + math.sin(a) * r)) for r in range(1, 8)], light)
        disc(img, 8, 8, 1.5, base)
    if style >= 5:
        rect(img, 1, 14, 14, 15, dark)  # a soil base for the later walls
    return img


def bug_invader(body, head, legs=True, wings=False, size=1.0, spots=None, horn=False, segments=0):
    img = new()
    cx, cy = 8, 9
    if segments:
        for i in range(segments):
            disc(img, 3 + i * 2.2, 11 - (i % 2), 2.0 * size, hexc(body) if i % 2 else shade(hexc(body), -0.15))
        disc(img, 3 + segments * 2.2, 10, 2.4 * size, hexc(head))
        for i in range(segments):
            px(img, [(int(3 + i * 2.2), 13), (int(3 + i * 2.2), 14)], hexc("#2a1408"))
        return img
    if wings:
        disc(img, 4, 6, 3, hexc("#d8f0ff", 170))
        disc(img, 12, 6, 3, hexc("#d8f0ff", 170))
    disc(img, cx, cy, 4.2 * size, hexc(body))
    disc(img, cx, cy - 4.5 * size, 2.3 * size, hexc(head))
    if legs:
        for y in (8, 10, 12):
            px(img, [(int(cx - 4.5 * size) - 1, y), (int(cx + 4.5 * size), y)], hexc("#2a1408"))
    if spots:
        for x, y in [(6, 9), (10, 9), (8, 11)]:
            px(img, [(x, y)], hexc(spots))
    if horn:
        px(img, [(8, 1), (8, 2), (7, 0), (9, 3)], hexc("#2a1408"))
    return img


def aphid_cluster():
    img = new()
    for cx, cy in [(5, 7), (10, 6), (7, 11), (11, 11), (4, 11)]:
        disc(img, cx, cy, 2.4, hexc("#9fd44a"))
        px(img, [(int(cx), int(cy) - 1)], hexc("#d8f58a"))
    return img


def scale_colony():
    img = aphid_cluster()
    for x, y in [(5, 6), (10, 5), (7, 10), (11, 10)]:
        rect(img, x - 1, y, x + 1, y, hexc("#8a7a6a"))
    return img


# --- Farm world -------------------------------------------------------------

def pasture():
    img = Image.new("RGBA", (16, 16), hexc("#6fa04a"))
    speckle(img, [hexc("#7cae55"), hexc("#64943f"), hexc("#88b85e")], 45, 21)
    px(img, [(4, 5), (11, 11), (7, 2)], hexc("#e8e070"))  # little flowers
    rect(img, 0, 0, 15, 0, hexc("#5f8f3f"))
    rect(img, 0, 0, 0, 15, hexc("#5f8f3f"))
    return img


def boulder():
    img = pasture()
    disc(img, 8, 9, 6.8, hexc("#7a756c"))
    disc(img, 6, 6.5, 3.5, hexc("#968f84"))
    ring(img, 8, 9, 6.8, hexc("#4f4b45"))
    px(img, [(9, 12), (11, 10)], hexc("#5f5a52"))
    return img


def forest_edge():
    img = Image.new("RGBA", (16, 16), hexc("#2f4a24"))
    for cx, cy in [(4, 5), (11, 4), (8, 10), (3, 12), (13, 12)]:
        disc(img, cx, cy, 3.5, hexc("#3f6a2e"))
        px(img, [(cx - 1, cy - 1)], hexc("#5a8a42"))
    disc(img, 8, 9, 2.5, hexc("#141f10"))
    return img


def farmhouse():
    img = pasture()
    rect(img, 3, 7, 12, 14, hexc("#b8402e"))   # walls
    for x in range(2, 14):                        # roof
        top = 7 - min(x - 2, 13 - x) // 2
        rect(img, x, max(1, top), x, 7, hexc("#5a3020"))
    rect(img, 7, 10, 8, 14, hexc("#3a1a10"))     # door
    rect(img, 4, 9, 5, 10, hexc("#f0e0a0"))      # windows
    rect(img, 10, 9, 11, 10, hexc("#f0e0a0"))
    return img


def animal_unit(color, style):
    """An attacker drawn as a side-on animal or bird, tinted with the pack color."""
    img = new()
    body, dark, light = shade(color, 0.05), shade(color, -0.3), shade(color, 0.3)
    kind = style % 4
    if kind == 3:  # bird
        disc(img, 7, 9, 4.5, body)
        disc(img, 10.5, 5.5, 2.6, body)
        px(img, [(13, 5), (14, 6)], hexc("#f0a020"))  # beak
        px(img, [(11, 5)], hexc("#141414"))           # eye
        rect(img, 4, 8, 7, 9, dark)                   # wing
        px(img, [(6, 13), (8, 13), (6, 14), (8, 14)], hexc("#f0a020"))  # feet
        return img
    # four-legged animal
    rect(img, 3, 7, 11, 11, body)
    disc(img, 12, 6, 2.8, body)
    px(img, [(13, 5)], hexc("#141414"))
    for x in (4, 6, 9, 11):
        rect(img, x, 12, x, 14, dark)
    px(img, [(2, 7), (1, 6)], dark)  # tail
    if kind == 0:   # horns
        px(img, [(11, 2), (11, 3), (14, 2), (13, 3)], light)
    elif kind == 1:  # long ears
        px(img, [(11, 2), (11, 3), (12, 3)], dark)
    else:            # spots
        for x, y in [(5, 8), (8, 9), (10, 8)]:
            px(img, [(x, y)], dark)
    if style >= 6:
        rect(img, 3, 7, 11, 7, light)  # highlight on later units
    return img


def farm_wall(color, style):
    """A wall drawn as farm material, tinted with the pack color."""
    img = new()
    base, dark, light = shade(color, -0.1), shade(color, -0.35), shade(color, 0.2)
    kind = style % 5
    if kind == 0:  # stone wall
        rect(img, 1, 3, 14, 14, base)
        for y in (6, 10):
            rect(img, 1, y, 14, y, dark)
        px(img, [(5, y) for y in range(3, 6)] + [(10, y) for y in range(7, 10)] + [(6, y) for y in range(11, 14)], dark)
    elif kind == 1:  # hedge
        for cx, cy in [(5, 7), (10, 7), (8, 11), (4, 11), (12, 11)]:
            disc(img, cx, cy, 3.4, base)
            px(img, [(cx - 1, cy - 1)], light)
    elif kind == 2:  # silo / barrel
        rect(img, 3, 2, 12, 14, base)
        for y in (5, 9, 13):
            rect(img, 3, y, 12, y, dark)
        rect(img, 3, 2, 12, 2, light)
    elif kind == 3:  # hay bale / fence slats
        rect(img, 1, 4, 14, 13, base)
        for x in range(2, 14, 3):
            rect(img, x, 4, x, 13, dark)
        rect(img, 1, 4, 14, 4, light)
    else:  # wooden fence posts
        for x in (2, 7, 12):
            rect(img, x, 2, x + 1, 14, base)
            px(img, [(x, 2)], light)
        rect(img, 1, 5, 14, 6, dark)
        rect(img, 1, 10, 14, 11, dark)
    return img


def beast(body, head, size=1.0, horns=None, ears=False, flier=False, tail=True, pack=0):
    img = new()
    if flier:
        disc(img, 8, 9, 3.5 * size, hexc(body))
        rect(img, 1, 7, 15, 8, hexc(head))  # spread wings
        disc(img, 8, 5, 2 * size, hexc(head))
        px(img, [(8, 3)], hexc("#f0a020"))
        return img
    count = pack if pack else 1
    for i in range(count):
        ox = (i - (count - 1) / 2) * 4 if count > 1 else 0
        oy = (i % 2) * 3 - (1 if count > 1 else 0)
        s = size * (0.6 if count > 1 else 1.0)
        x0, x1 = int(8 + ox - 5 * s), int(8 + ox + 3 * s)
        y0, y1 = int(9 + oy - 2 * s), int(9 + oy + 2 * s)
        rect(img, x0, y0, x1, y1, hexc(body))
        disc(img, x1 + 1.5 * s, y0 - 0.5, 2.3 * s, hexc(head))
        for x in (x0 + 1, x1 - 1):
            rect(img, x, y1 + 1, x, min(15, y1 + int(3 * s)), hexc("#2a1a10"))
        if tail:
            px(img, [(x0 - 1, y0)], hexc(body))
        if ears:
            px(img, [(x1 + 1, y0 - 3), (x1 + 2, y0 - 3)], hexc(head))
        if horns:
            px(img, [(x1, y0 - 3), (x1 - 1, y0 - 4), (x1 + 3, y0 - 3), (x1 + 4, y0 - 4)], hexc(horns))
    return img


FARM_INVADER_ART = {
    "coyote": lambda: beast("#b8925a", "#a07a48", size=0.7, ears=True),
    "wolf": lambda: beast("#8a8a8a", "#6a6a6a", size=0.75, ears=True),
    "bear_cub": lambda: beast("#7a5030", "#6a4026", size=0.7, tail=False),
    "rat": lambda: beast("#8a7a70", "#6a5a50", size=0.6),
    "weasel": lambda: beast("#c08040", "#f0e0c0", size=0.65),
    "coyote_pack": lambda: beast("#b8925a", "#a07a48", ears=True, pack=3),
    "wolf_pack": lambda: beast("#8a8a8a", "#5a5a5a", ears=True, pack=3),
    "deer": lambda: beast("#b07840", "#c08850", size=0.9, ears=True),
    "red_stag": lambda: beast("#a05a30", "#b06a3a", size=1.0, horns="#e8d8b0"),
    "gopher": lambda: beast("#a07a50", "#8a6440", size=0.7, tail=False),
    "wild_boar": lambda: beast("#4a3a30", "#3a2a22", size=1.0, horns="#f0f0e0"),
    "moose": lambda: beast("#5a4030", "#4a3022", size=1.15, horns="#d8c8a0"),
    "crow": lambda: beast("#202024", "#38383e", flier=True, size=0.8),
    "hawk": lambda: beast("#8a5a30", "#c8a070", flier=True, size=0.95),
    "grizzly": lambda: beast("#6a4428", "#5a3820", size=1.3, ears=True, tail=False),
}


BACKYARD_INVADER_ART = {
    "aphid": lambda: bug_invader("#9fd44a", "#7ab030", legs=False, size=0.6),
    "termite": lambda: bug_invader("#e8d2a8", "#b07a3a", size=0.8),
    "soldier_termite": lambda: bug_invader("#d8b888", "#7a3a1a", size=0.9, horn=True),
    "aphid_cluster": aphid_cluster,
    "scale_colony": scale_colony,
    "mole_cricket": lambda: bug_invader("#8a5a32", "#5a3a1a", size=1.0, spots="#c08a5a"),
    "rhino_beetle": lambda: bug_invader("#5a3a22", "#3a2414", size=1.1, horn=True),
    "hercules_beetle": lambda: bug_invader("#a0a050", "#2a2a14", size=1.2, horn=True, spots="#3a3a1a"),
    "mosquito": lambda: bug_invader("#6a6a72", "#3a3a40", size=0.6, wings=True),
    "hornet": lambda: bug_invader("#e8b830", "#5a3a10", size=0.85, wings=True, spots="#2a1a08"),
    "giant_centipede": lambda: bug_invader("#b0402a", "#5a1a10", size=1.0, segments=5),
}


# --- Invaders ---------------------------------------------------------------

def rhinovirus(main="#7bd24a", edge="#3f8a22", tips="#b6f58a"):
    img = new()
    disc(img, 8, 8, 4.5, hexc(main))
    ring(img, 8, 8, 4.5, hexc(edge))
    for i in range(8):
        a = i * math.tau / 8
        px(img, [(int(8 + math.cos(a) * 6), int(8 + math.sin(a) * 6))], hexc(tips))
    px(img, [(7, 7), (9, 9)], hexc(edge))
    return img


def flu_virus():
    img = rhinovirus("#4ad2b0", "#1f7a63", "#ff8a8a")
    # Speed streaks
    px(img, [(0, 7), (1, 7), (0, 9), (1, 9), (2, 9)], hexc("#c8fff0"))
    return img


def bacterium(main="#c6d84a", light="#e2ef8a", dark="#7d8a1f"):
    img = new()
    for x in range(3, 13):
        rect(img, x, 5, x, 10, hexc(main))
    disc(img, 3.5, 8, 3, hexc(main))
    disc(img, 12.5, 8, 3, hexc(main))
    rect(img, 3, 5, 12, 5, hexc(light))
    px(img, [(5, 8), (8, 7), (11, 9)], hexc(dark))
    return img


def biofilm():
    img = bacterium("#9aa83a", "#c9d27a", "#4d5612")
    # Slimy armor plates
    for x in (4, 7, 10):
        rect(img, x, 4, x + 1, 4, hexc("#5d6b9a"))
        rect(img, x, 11, x + 1, 11, hexc("#5d6b9a"))
    return img


def bacterium_half():
    img = new()
    disc(img, 8, 8, 3.5, hexc("#c6d84a"))
    ring(img, 8, 8, 3.5, hexc("#7d8a1f"))
    px(img, [(7, 7)], hexc("#e2ef8a"))
    return img


def worm(body="#c28a5a", alt="#a8703f", mouth="#ff6b6b"):
    img = new()
    for i, (x, y) in enumerate([(3, 12), (5, 10), (7, 8), (9, 6), (11, 5)]):
        disc(img, x, y, 2.6 if i < 4 else 3.2, hexc(body) if i % 2 else hexc(alt))
    px(img, [(11, 4), (13, 5)], hexc("#2a1408"))
    px(img, [(13, 6), (14, 6)], hexc(mouth))
    return img


def hookworm():
    img = worm("#b0605a", "#8a3f3a", "#ffd23c")
    px(img, [(14, 4), (15, 3), (14, 7), (15, 8)], hexc("#f0e0d0"))  # hooks
    return img


def spore(main="#f0e6ff", edge="#a78bd6"):
    img = new()
    disc(img, 8, 9, 3.5, hexc(main))
    ring(img, 8, 9, 3.5, hexc(edge))
    for x, y in [(2, 5), (14, 5), (3, 3), (13, 3), (4, 6), (12, 6)]:
        img.putpixel((x, y), hexc("#d8c8ff", 200))
    px(img, [(8, 9)], hexc(edge))
    return img


def fungal_spore():
    img = spore("#ffd9a8", "#b0703a")
    ring(img, 8, 9, 5, hexc("#b0703a", 160))
    return img


def superbug():
    img = new()
    disc(img, 8, 8, 7, hexc("#5b2a86"))
    ring(img, 8, 8, 7, hexc("#2a0f45"), 1.3)
    for i in range(10):
        a = i * math.tau / 10
        px(img, [(int(8 + math.cos(a) * 7.4), int(8 + math.sin(a) * 7.4))], hexc("#e04aff"))
    disc(img, 6, 7, 1.4, hexc("#ff3b3b"))
    disc(img, 10, 7, 1.4, hexc("#ff3b3b"))
    rect(img, 5, 10, 11, 11, hexc("#1a0626"))
    px(img, [(6, 10), (8, 10), (10, 10)], hexc("#f0f0f0"))
    return img


INVADER_ART = {
    "rhinovirus": rhinovirus, "flu_virus": flu_virus, "bacterium": bacterium,
    "biofilm": biofilm, "bacterium_half": bacterium_half, "worm": worm,
    "hookworm": hookworm, "spore": spore, "fungal_spore": fungal_spore,
    "superbug": superbug,
}


if __name__ == "__main__":
    for name, fn in {"floor": floor, "rock": rock, "spawn": spawn, "base": base}.items():
        save(fn(), f"tiles/immune_system/{name}.png")
    for name, fn in {"floor": grass, "rock": stone, "spawn": dirt_hole, "base": anthill}.items():
        save(fn(), f"tiles/backyard_bugs/{name}.png")
    for name, fn in {"floor": pasture, "rock": boulder, "spawn": forest_edge, "base": farmhouse}.items():
        save(fn(), f"tiles/wild_kingdom/{name}.png")

    all_content = {}
    for content_file in sorted((PROJECT / "tools" / "content").glob("*.json")):
        content = json.loads(content_file.read_text())
        all_content[content["biome"]["id"]] = content
    for biome_id, content in all_content.items():
        style = content.get("art_style", "cells")
        for pack in pack_rows(content, all_content):
            for unit in pack["units"]:
                sprite = unit_sprite(unit, pack["color"], style)
                save(sprite, f"units/{biome_id}/{pack['id']}/{unit['id']}.png")
                for branch, evo in enumerate(unit["evolutions"]):
                    save(add_badge(sprite.copy(), branch), f"units/{biome_id}/{pack['id']}/{evo['id']}.png")
        for invader in content["invaders"]:
            art = (INVADER_ART.get(invader["art"]) or BACKYARD_INVADER_ART.get(invader["art"])
                   or FARM_INVADER_ART[invader["art"]])
            save(art(), f"invaders/{biome_id}/{invader['id']}.png")
    print("Placeholder art written to", ROOT)
