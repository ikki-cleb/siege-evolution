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
    if art_style == "toys":
        return fort_wall(color, style) if kind == "block" else toy_unit(color, style)
    if art_style == "tech":
        return tech_wall(color, style) if kind == "block" else robot_unit(color, style)
    if art_style == "kitchen":
        return kitchen_wall(color, style) if kind == "block" else kitchen_tool(color, style)
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


# --- Toy war world ----------------------------------------------------------

def sand():
    img = Image.new("RGBA", (16, 16), hexc("#e2c98f"))
    speckle(img, [hexc("#d6bb7f"), hexc("#ecd6a2"), hexc("#c9ad70")], 50, 31)
    rect(img, 0, 0, 15, 0, hexc("#d2b67a"))
    rect(img, 0, 0, 0, 15, hexc("#d2b67a"))
    return img


def toy_block():
    img = sand()
    rect(img, 2, 2, 13, 13, hexc("#3a7bd5"))
    rect(img, 2, 2, 13, 3, hexc("#6aa0ea"))
    rect(img, 2, 12, 13, 13, hexc("#24569c"))
    px(img, [(7, 6), (8, 6), (6, 7), (9, 7), (6, 8), (9, 8), (7, 9), (8, 9)], hexc("#f0f0f0"))  # an "O" letter
    return img


def toy_box():
    img = sand()
    rect(img, 1, 3, 14, 14, hexc("#c0392b"))
    rect(img, 1, 3, 14, 5, hexc("#e05a48"))
    rect(img, 4, 8, 11, 12, hexc("#2a1010"))
    return img


def toy_fort():
    img = sand()
    rect(img, 2, 6, 13, 14, hexc("#7a8a5a"))
    for x in (2, 5, 8, 11):
        rect(img, x, 4, x + 1, 5, hexc("#7a8a5a"))
    rect(img, 7, 10, 8, 14, hexc("#3a3a2a"))
    rect(img, 8, 0, 8, 4, hexc("#5a4a3a"))
    rect(img, 9, 0, 12, 2, hexc("#e8c84a"))  # flag
    return img


def bath_water():
    img = Image.new("RGBA", (16, 16), hexc("#5aaee0"))
    for x, y in [(2, 3), (9, 6), (5, 11), (12, 13)]:
        px(img, [(x, y), (x + 1, y), (x + 2, y)], hexc("#8fd0f5"))
    px(img, [(13, 2), (3, 8)], hexc("#e8f8ff"))  # bubbles
    return img


def drain():
    img = bath_water()
    ring(img, 8, 8, 5.5, hexc("#c8d0d8"), 1.3)
    for y in (6, 8, 10):
        rect(img, 5, y, 10, y, hexc("#8a96a2"))
    return img


def toy_unit(color, style):
    """An attacker drawn as a toy soldier figure or a toy turret."""
    img = new()
    base, dark, light = shade(color, 0.0), shade(color, -0.3), shade(color, 0.25)
    if style % 2 == 0:  # army figure on a little base
        disc(img, 8, 4, 2.5, base)                 # head
        rect(img, 6, 6, 10, 11, base)              # body
        rect(img, 6, 12, 7, 13, dark)              # legs
        rect(img, 9, 12, 10, 13, dark)
        rect(img, 4, 14, 12, 15, dark)             # plastic base
        rect(img, 10, 7, 14, 8, hexc("#3a3a3a"))   # gun
        px(img, [(7, 2), (8, 2), (9, 2)], dark)    # helmet rim
        if style >= 6:
            px(img, [(7, 8), (8, 8)], light)
    else:  # turret
        disc(img, 8, 10, 5.5, base)
        ring(img, 8, 10, 5.5, dark)
        disc(img, 8, 10, 2.5, light)
        rect(img, 7, 1, 9, 8, hexc("#3a3a3a"))     # barrel
        if style >= 7:
            rect(img, 4, 1, 5, 6, hexc("#3a3a3a"))  # second barrel
    return img


def fort_wall(color, style):
    """A wall drawn as a toy fortification, tinted with the pack color."""
    img = new()
    base, dark, light = shade(color, -0.1), shade(color, -0.35), shade(color, 0.2)
    kind = style % 5
    if kind == 0:  # sandbags
        for row, y in enumerate((11, 7, 3)):
            for x in range(1 + (row % 2) * 2, 14, 5):
                rect(img, x, y, x + 3, y + 3, base)
                rect(img, x, y, x + 3, y, light)
    elif kind == 1:  # repair depot / crates
        rect(img, 2, 4, 13, 14, base)
        px(img, [(i + 2, i + 4) for i in range(11)] + [(13 - i, i + 4) for i in range(11)], dark)
        rect(img, 2, 4, 13, 4, light)
    elif kind == 2:  # concrete bunker
        rect(img, 1, 5, 14, 14, base)
        rect(img, 1, 5, 14, 6, light)
        rect(img, 4, 9, 11, 10, hexc("#1a1a1a"))  # slit
    elif kind == 3:  # barbed wire / tank trap
        for x in (3, 8, 13):
            px(img, [(x - 2, 13), (x - 1, 12), (x, 11), (x + 1, 12), (x + 2, 13), (x, 10), (x, 9)], base)
        for x in range(0, 16, 2):
            px(img, [(x, 6 + (x // 2) % 2)], dark)
    else:  # oil barrels
        for x in (2, 9):
            rect(img, x, 4, x + 4, 14, base)
            rect(img, x, 6, x + 4, 6, dark)
            rect(img, x, 11, x + 4, 11, dark)
            rect(img, x, 4, x + 4, 4, light)
    return img


def water_net(color, heavy=False):
    img = new()
    rope = shade(hexc(color), 0.25)
    for i in range(1, 16, 3 if heavy else 4):
        rect(img, i, 2, i, 13, rope)
        rect(img, 1, i if i < 14 else 13, 14, i if i < 14 else 13, rope)
    for x in (1, 14):
        disc(img, x, 2, 1.5, hexc("#f05a3a"))  # floats
    return img


def naval_mine(color):
    img = new()
    disc(img, 8, 9, 5, hexc("#3a3a42"))
    ring(img, 8, 9, 5, shade(hexc(color), -0.2))
    for x, y in [(8, 2), (8, 15), (1, 9), (15, 9), (3, 4), (13, 4), (3, 14), (13, 14)]:
        px(img, [(x, y)], hexc("#d0d0d0"))
    px(img, [(6, 7), (7, 6)], hexc("#8a8a92"))
    return img


def toy_vehicle(body, size=1.0, turret=False, wheels=True, boat=False, plane=False, sub=False):
    img = new()
    c = hexc(body)
    if plane:
        rect(img, 2, 7, 13, 9, c)
        rect(img, 6, 3, 8, 13, c)
        rect(img, 11, 5, 12, 11, shade(c, -0.2))
        return img
    if sub:
        rect(img, 2, 8, 13, 11, c)
        disc(img, 2, 9.5, 2, c)
        disc(img, 13, 9.5, 2, c)
        rect(img, 7, 5, 9, 8, shade(c, -0.2))
        return img
    w = int(5 * size)
    rect(img, 8 - w, 8, 7 + w, 12, c)
    if boat:
        rect(img, 8 - w + 1, 13, 7 + w - 1, 13, shade(c, -0.25))
        rect(img, 7, 4, 9, 7, shade(c, 0.2))
        return img
    if turret:
        rect(img, 5, 5, 10, 8, shade(c, 0.15))
        rect(img, 10, 6, 15, 7, hexc("#2a2a2a"))
    if wheels:
        for x in range(8 - w, 8 + w, 3):
            disc(img, x + 1, 13, 1.4, hexc("#2a2a2a"))
    return img


def toy_figure(body):
    img = new()
    c = hexc(body)
    disc(img, 8, 4, 2.2, c)
    rect(img, 6, 6, 10, 11, c)
    rect(img, 6, 12, 7, 14, shade(c, -0.25))
    rect(img, 9, 12, 10, 14, shade(c, -0.25))
    rect(img, 2, 7, 6, 8, hexc("#3a3a3a"))
    return img


# --- Space world ------------------------------------------------------------

def moon_floor():
    img = Image.new("RGBA", (16, 16), hexc("#b8b8c0"))
    speckle(img, [hexc("#a8a8b2"), hexc("#c8c8d0"), hexc("#9a9aa4")], 45, 41)
    ring(img, 11, 5, 2.2, hexc("#9a9aa4"))
    rect(img, 0, 0, 15, 0, hexc("#a2a2ac"))
    rect(img, 0, 0, 0, 15, hexc("#a2a2ac"))
    return img


def crater():
    img = moon_floor()
    disc(img, 8, 8, 6.8, hexc("#6a6a76"))
    disc(img, 9, 9, 5, hexc("#55555f"))
    ring(img, 8, 8, 6.8, hexc("#d8d8e0"))
    return img


def deck_plate():
    img = Image.new("RGBA", (16, 16), hexc("#4a5260"))
    rect(img, 0, 0, 15, 0, hexc("#3a414c"))
    rect(img, 0, 0, 0, 15, hexc("#3a414c"))
    rect(img, 0, 8, 15, 8, hexc("#424a56"))
    px(img, [(2, 2), (13, 2), (2, 13), (13, 13)], hexc("#7a8494"))  # rivets
    return img


def bulkhead():
    img = Image.new("RGBA", (16, 16), hexc("#2a2f38"))
    for y in range(0, 16, 4):
        rect(img, 0, y, 15, y, hexc("#e0b030"))  # hazard stripes
        px(img, [(x, y + 1) for x in range(0, 16, 2)], hexc("#1a1d22"))
    rect(img, 2, 2, 13, 13, hexc("#3a414c"))
    return img


def asteroid_floor():
    img = Image.new("RGBA", (16, 16), hexc("#6a5a4e"))
    speckle(img, [hexc("#5e4e44"), hexc("#7a6a5c"), hexc("#4e4038")], 55, 43)
    px(img, [(3, 4), (12, 11)], hexc("#e8e8ff"))  # glints of starlight
    return img


def asteroid_rock():
    img = Image.new("RGBA", (16, 16), hexc("#0c0c18"))
    for x, y in [(2, 3), (12, 2), (6, 13), (14, 10)]:
        px(img, [(x, y)], hexc("#e8e8ff"))  # open space between rocks
    disc(img, 8, 8, 5.5, hexc("#5a4a40"))
    disc(img, 7, 7, 2.5, hexc("#6e5e52"))
    return img


def warp_gate(floor_fn):
    img = floor_fn()
    ring(img, 8, 8, 7, hexc("#8a5ad8"), 1.5)
    disc(img, 8, 8, 4.5, hexc("#3a1a6a"))
    disc(img, 8, 8, 2, hexc("#c8a0ff"))
    return img


def reactor(floor_fn):
    img = floor_fn()
    disc(img, 8, 9, 6.5, hexc("#9ad8f0"))
    ring(img, 8, 9, 6.5, hexc("#3a6a8a"), 1.3)
    disc(img, 8, 9, 2.5, hexc("#f0fcff"))
    rect(img, 7, 1, 8, 3, hexc("#3a6a8a"))
    return img


def robot_unit(color, style):
    """An attacker drawn as a robot or a tech turret, tinted with the pack color."""
    img = new()
    body, dark, light = shade(color, 0.0), shade(color, -0.3), shade(color, 0.3)
    if style % 2 == 0:  # robot
        rect(img, 4, 2, 11, 7, body)            # head
        rect(img, 5, 4, 10, 5, hexc("#60f0ff"))  # visor
        rect(img, 5, 8, 10, 12, dark)           # body
        rect(img, 3, 8, 4, 11, body)            # arms
        rect(img, 11, 8, 12, 11, body)
        rect(img, 5, 13, 6, 15, dark)           # legs
        rect(img, 9, 13, 10, 15, dark)
        px(img, [(7, 0), (7, 1)], light)        # antenna
    else:  # turret with a glowing barrel
        disc(img, 8, 11, 5, dark)
        disc(img, 8, 10, 3.5, body)
        rect(img, 7, 1, 8, 8, light)
        px(img, [(7, 1), (8, 1)], hexc("#60f0ff"))
    if style >= 6:
        px(img, [(4, 2), (11, 2)], light)
    return img


def tech_wall(color, style):
    """A wall drawn as a tech barrier, tinted with the pack color."""
    img = new()
    base, dark, light = shade(color, -0.1), shade(color, -0.35), shade(color, 0.3)
    kind = style % 5
    if kind == 0:  # hull plate
        rect(img, 1, 1, 14, 14, base)
        rect(img, 1, 1, 14, 1, light)
        px(img, [(3, 3), (12, 3), (3, 12), (12, 12)], dark)
    elif kind == 1:  # nanite mass
        for cx, cy in [(5, 6), (10, 6), (7, 10), (11, 11), (4, 11)]:
            disc(img, cx, cy, 2.6, base)
        speckle(img, [light], 10, 5)
    elif kind == 2:  # core block
        rect(img, 2, 2, 13, 13, dark)
        disc(img, 8, 8, 3.5, base)
        disc(img, 8, 8, 1.5, light)
    elif kind == 3:  # scrap barrier
        rect(img, 1, 6, 14, 13, base)
        for x in range(1, 15, 3):
            rect(img, x, 4, x + 1, 6, dark)
    else:  # energy field
        for y in range(1, 15, 2):
            rect(img, 2, y, 13, y, base)
        rect(img, 1, 1, 1, 14, light)
        rect(img, 14, 1, 14, 14, light)
    return img


def alien(body, eyes="#ff4060", size=1.0, legs=4, wings=False, pods=0, mech=False):
    img = new()
    c = hexc(body)
    if mech:
        rect(img, 3, 3, 12, 9, c)
        rect(img, 5, 5, 10, 6, hexc(eyes))
        rect(img, 3, 10, 5, 15, shade(c, -0.25))
        rect(img, 10, 10, 12, 15, shade(c, -0.25))
        rect(img, 0, 5, 2, 7, shade(c, 0.2))
        return img
    if wings:
        rect(img, 1, 7, 14, 9, hexc("#8a96a8"))
        disc(img, 8, 8, 3.5 * size, c)
        rect(img, 6, 6, 9, 6, hexc(eyes))
        return img
    if pods:
        for cx, cy in [(5, 7), (10, 6), (8, 11)][:pods]:
            disc(img, cx, cy, 3, c)
            px(img, [(int(cx), int(cy))], hexc(eyes))
        return img
    disc(img, 8, 9, 4 * size, c)
    px(img, [(7, 8), (9, 8)], hexc(eyes))
    for i in range(legs):
        x = 4 + i * (8 // max(1, legs - 1))
        px(img, [(x, 13), (x, 14)], shade(c, -0.3))
    return img


def ufo(body, size=1.0, bomb=False):
    img = new()
    rect(img, int(8 - 6 * size), 8, int(7 + 6 * size), 10, hexc(body))
    disc(img, 8, 7, 3 * size, hexc("#a0e8ff"))
    if bomb:
        disc(img, 8, 13, 1.5, hexc("#2a2a2a"))
    return img


ALIEN_INVADER_ART = {
    "spawnling": lambda: alien("#9ad84a", size=0.6, legs=2),
    "grub": lambda: alien("#7ac83a", size=0.8),
    "drone": lambda: alien("#3a9a5a", size=0.9, eyes="#ffd040"),
    "brood_pod": lambda: alien("#b8a05a", pods=3),
    "hive_pod": lambda: alien("#7a6a3a", pods=3, eyes="#ffd040"),
    "blinker": lambda: alien("#a060f0", size=0.9, eyes="#ffffff", legs=0),
    "phase_stalker": lambda: alien("#6a30c0", size=1.0, eyes="#ff60ff", legs=2),
    "hopper": lambda: alien("#d88a3a", size=0.8, legs=2),
    "tunneler": lambda: alien("#8a6a4a", size=0.9, legs=6),
    "crusher": lambda: alien("#6a7a8a", mech=True),
    "assault_mech": lambda: alien("#4a5260", eyes="#ffd040", mech=True),
    "saucer": lambda: ufo("#a0a8b8", size=0.8),
    "interceptor": lambda: alien("#6a7a9a", wings=True),
    "ufo_bomber": lambda: ufo("#7a8090", size=1.0, bomb=True),
    "mothership": lambda: ufo("#5a5a7a", size=1.25),
}


TOY_INVADER_ART = {
    "toy_recruit": lambda: toy_figure("#c8a878"),
    "toy_soldier": lambda: toy_figure("#b88a50"),
    "ranger": lambda: toy_figure("#8a5a30"),
    "troop_truck": lambda: toy_vehicle("#9a8a60", size=1.1),
    "armored_carrier": lambda: toy_vehicle("#6a6a58", size=1.2, turret=True),
    "motorbike": lambda: toy_vehicle("#d04040", size=0.6),
    "toy_tank": lambda: toy_vehicle("#8a8a50", size=1.1, turret=True),
    "heavy_tank": lambda: toy_vehicle("#5a5a40", size=1.4, turret=True),
    "paper_plane": lambda: toy_vehicle("#f0f0f0", plane=True),
    "jet": lambda: toy_vehicle("#8a96a8", plane=True),
    "toy_bomber": lambda: toy_vehicle("#7a8a6a", plane=True),
    "heavy_bomber": lambda: toy_vehicle("#4a5a3a", plane=True),
    "patrol_boat": lambda: toy_vehicle("#e8e8e8", size=0.8, boat=True),
    "destroyer": lambda: toy_vehicle("#9aa0aa", size=1.1, boat=True),
    "submarine": lambda: toy_vehicle("#4a4a5a", sub=True),
    "battleship": lambda: toy_vehicle("#6a707a", size=1.4, boat=True),
    "mega_tank": lambda: toy_vehicle("#4a4a30", size=1.5, turret=True),
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


# --- Kitchen world (bonus) ----------------------------------------------------

def shelf_planks():
    """Pantry shelf: wooden planks."""
    img = Image.new("RGBA", (16, 16), hexc("#b07a48"))
    for y in (0, 5, 10, 15):
        rect(img, 0, y, 15, y, hexc("#8a5a32"))
    speckle(img, [hexc("#a06c3e"), hexc("#c08a58")], 25, 51)
    return img


def glass_jar():
    img = shelf_planks()
    rect(img, 3, 3, 12, 14, hexc("#c8e8f0"))
    rect(img, 4, 4, 11, 13, hexc("#e8b850"))   # jam inside
    rect(img, 3, 1, 12, 3, hexc("#d04040"))     # red lid
    px(img, [(4, 5), (4, 6), (4, 7)], hexc("#ffffff"))
    return img


def counter_tiles():
    """Counter top: white tiles with grout lines."""
    img = Image.new("RGBA", (16, 16), hexc("#e8e4dc"))
    rect(img, 0, 0, 15, 0, hexc("#b8b0a4"))
    rect(img, 0, 0, 0, 15, hexc("#b8b0a4"))
    rect(img, 0, 8, 15, 8, hexc("#c8c0b4"))
    rect(img, 8, 0, 8, 15, hexc("#c8c0b4"))
    return img


def tin_can_rock():
    img = counter_tiles()
    disc(img, 8, 8, 6.5, hexc("#a8b0b8"))
    ring(img, 8, 8, 6.5, hexc("#6a727a"))
    ring(img, 8, 8, 4, hexc("#8a9298"))
    px(img, [(6, 5), (5, 6)], hexc("#e8eef2"))
    return img


def checker_floor():
    """Kitchen floor: checkered linoleum."""
    img = Image.new("RGBA", (16, 16), hexc("#d8d0c0"))
    rect(img, 0, 0, 7, 7, hexc("#5a7a8a"))
    rect(img, 8, 8, 15, 15, hexc("#5a7a8a"))
    return img


def chair_leg():
    img = checker_floor()
    disc(img, 8, 8, 5.5, hexc("#5a3a1e"))
    disc(img, 8, 8, 3.5, hexc("#7a5030"))
    px(img, [(6, 6)], hexc("#9a6a40"))
    return img


def mouse_hole(floor_fn):
    img = floor_fn()
    disc(img, 8, 10, 6, hexc("#1a1210"))
    rect(img, 2, 10, 13, 15, hexc("#1a1210"))
    ring(img, 8, 10, 6, hexc("#6a4a30"))
    return img


def cookie_jar(floor_fn):
    img = floor_fn()
    disc(img, 8, 9, 6.5, hexc("#f0e0c8"))
    ring(img, 8, 9, 6.5, hexc("#a08060"), 1.2)
    rect(img, 5, 1, 10, 3, hexc("#c87040"))      # lid
    for x, y in [(6, 9), (10, 8), (8, 12)]:
        disc(img, x, y, 1.6, hexc("#b07030"))    # cookies showing through
    return img


def kitchen_tool(color, style):
    """An attacker drawn as a kitchen tool or gadget, tinted with the pack color."""
    img = new()
    body, dark, light = shade(color, 0.05), shade(color, -0.3), shade(color, 0.3)
    if style % 2 == 0:  # utensil: a handle with a head
        rect(img, 7, 7, 8, 15, hexc("#8a5a32"))  # wooden handle
        disc(img, 7.5, 4.5, 3.6, body)
        ring(img, 7.5, 4.5, 3.6, dark)
        px(img, [(6, 3)], light)
    else:  # gadget: a little appliance with a dial
        rect(img, 2, 4, 13, 14, body)
        rect(img, 2, 4, 13, 4, light)
        rect(img, 2, 14, 13, 14, dark)
        disc(img, 8, 9, 2.5, dark)
        px(img, [(8, 8)], hexc("#ffffff"))
        rect(img, 4, 2, 5, 3, dark)
    if style >= 6:
        px(img, [(12, 1), (13, 2)], light)
    return img


def kitchen_wall(color, style):
    """A wall drawn as a kitchen object, tinted with the pack color."""
    img = new()
    base, dark, light = shade(color, -0.05), shade(color, -0.35), shade(color, 0.3)
    kind = style % 5
    if kind == 0:  # tin can (side view)
        rect(img, 3, 2, 12, 14, base)
        rect(img, 3, 5, 12, 11, light)
        rect(img, 3, 2, 12, 2, dark)
        rect(img, 3, 14, 12, 14, dark)
    elif kind == 1:  # sponge
        rect(img, 1, 4, 14, 13, base)
        rect(img, 1, 4, 14, 6, hexc("#3a9a4a"))   # scrubby side
        speckle(img, [dark], 14, 7)
    elif kind == 2:  # cast-iron block / pan seen from above
        disc(img, 8, 8, 6.5, dark)
        disc(img, 8, 8, 5, base)
        rect(img, 13, 7, 15, 9, dark)
    elif kind == 3:  # sugar cube / board
        rect(img, 2, 2, 13, 13, light)
        rect(img, 2, 2, 13, 2, hexc("#ffffff"))
        speckle(img, [base], 10, 9)
    else:  # wrap / flypaper
        for y in range(2, 15, 3):
            rect(img, 1, y, 14, y + 1, base)
        rect(img, 1, 1, 1, 14, dark)
    return img


def pest(body, kind="ant", size=1.0, spots=None, wings=False):
    """Pantry pests: ants, slugs, mice, roaches and flies."""
    img = new()
    c = hexc(body)
    dark = shade(c, -0.3)
    if kind == "ant":
        for cx, r in [(4.5, 2.0), (8, 1.6), (11.5, 2.4)]:
            disc(img, cx, 8, r * size, c)
        for x in (6, 8, 10):
            px(img, [(x, 5), (x, 11)], dark)
        px(img, [(2, 6), (2, 10)], dark)
    elif kind == "slug":
        rect(img, 2, 9, 13, 12, c)
        disc(img, 12, 9, 2.6 * size, c)
        px(img, [(12, 5), (14, 5), (12, 6), (14, 6)], dark)  # eye stalks
        rect(img, 1, 13, 10, 13, hexc("#d8c890", 160))        # slime trail
    elif kind == "mouse":
        disc(img, 7, 9, 3.6 * size, c)
        disc(img, 11, 8, 2.2 * size, c)
        disc(img, 10, 5, 1.4, shade(c, 0.25))                  # ear
        px(img, [(12, 8)], hexc("#1a1a1a"))
        px(img, [(2, 10), (1, 11), (0, 11)], hexc("#e0a0a0"))  # tail
    elif kind == "roach":
        disc(img, 8, 8, 4.5 * size, c)
        rect(img, 8, 4, 8, 12, dark)
        for y in (5, 8, 11):
            px(img, [(2, y), (14, y)], dark)
        px(img, [(6, 1), (10, 1), (7, 2), (9, 2)], dark)        # antennae
    elif kind == "fly":
        disc(img, 8, 9, 2.6 * size, c)
        disc(img, 5, 6, 2.2, hexc("#d8eaf8", 200))
        disc(img, 11, 6, 2.2, hexc("#d8eaf8", 200))
        px(img, [(7, 8), (9, 8)], hexc("#c02020"))
    elif kind == "nest":
        disc(img, 8, 9, 6, hexc("#c8a868"))
        speckle(img, [hexc("#a08048"), hexc("#e0c890")], 18, 13)
        for x, y in [(5, 8), (10, 7), (8, 11)]:
            disc(img, x, y, 1.4, c)
    if spots:
        px(img, [(7, 7), (9, 9)], hexc(spots))
    return img


def rat_king():
    img = new()
    disc(img, 8, 9, 6.5, hexc("#6a6070"))
    disc(img, 4, 4, 2.2, hexc("#8a8090"))
    disc(img, 12, 4, 2.2, hexc("#8a8090"))
    px(img, [(6, 8), (10, 8)], hexc("#ff3030"))
    rect(img, 5, 1, 11, 2, hexc("#ffd23c"))                  # crown
    px(img, [(5, 0), (8, 0), (11, 0)], hexc("#ffd23c"))
    px(img, [(7, 11), (9, 11)], hexc("#f0f0f0"))             # teeth
    return img


KITCHEN_INVADER_ART = {
    "mouse": lambda: pest("#a89888", "mouse", 0.8),
    "rat": lambda: pest("#6a6070", "mouse", 1.0),
    "sugar_ant": lambda: pest("#3a2a20", "ant"),
    "fire_ant": lambda: pest("#c03a20", "ant", 1.1),
    "slug": lambda: pest("#a89a5a", "slug"),
    "honey_ant": lambda: pest("#e8a830", "ant", 1.3, spots="#ffe080"),
    "mouse_nest": lambda: pest("#a89888", "nest"),
    "rat_nest": lambda: pest("#5a5060", "nest"),
    "cockroach": lambda: pest("#7a4a22", "roach"),
    "giant_roach": lambda: pest("#4a2a12", "roach", 1.3),
    "fruit_fly": lambda: pest("#c08040", "fly", 0.8),
    "housefly": lambda: pest("#3a3a40", "fly", 1.1),
    "rat_king": rat_king,
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
    for name, fn in {"floor": sand, "rock": toy_block, "spawn": toy_box, "base": toy_fort,
                     "water": bath_water, "sea_spawn": drain}.items():
        save(fn(), f"tiles/total_war/{name}.png")
    for folder, floor_fn, rock_fn in [("", moon_floor, crater), ("station/", deck_plate, bulkhead),
                                      ("asteroid/", asteroid_floor, asteroid_rock)]:
        for name, fn in {"floor": floor_fn, "rock": rock_fn, "spawn": warp_gate, "base": reactor}.items():
            save(fn(floor_fn), f"tiles/galactic_siege/{folder}{name}.png") if name in ("spawn", "base") \
                else save(fn(), f"tiles/galactic_siege/{folder}{name}.png")
    for folder, floor_fn, rock_fn in [("", shelf_planks, glass_jar), ("counter/", counter_tiles, tin_can_rock),
                                      ("floor/", checker_floor, chair_leg)]:
        save(floor_fn(), f"tiles/kitchen_defense/{folder}floor.png")
        save(rock_fn(), f"tiles/kitchen_defense/{folder}rock.png")
        save(mouse_hole(floor_fn), f"tiles/kitchen_defense/{folder}spawn.png")
        save(cookie_jar(floor_fn), f"tiles/kitchen_defense/{folder}base.png")

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
                # Basic walls on water: nets (base and HP branch) and mines (reflect branch).
                if content.get("water_walls") and unit.get("water"):
                    color = pack["color"]
                    save(water_net(color), f"units/{biome_id}/{pack['id']}/{unit['id']}_water.png")
                    for branch, evo in enumerate(unit["evolutions"]):
                        art = water_net(color, heavy=True) if branch == 0 else naval_mine(color)
                        save(add_badge(art, branch), f"units/{biome_id}/{pack['id']}/{evo['id']}_water.png")
        for invader in content["invaders"]:
            art = (INVADER_ART.get(invader["art"]) or BACKYARD_INVADER_ART.get(invader["art"])
                   or FARM_INVADER_ART.get(invader["art"]) or TOY_INVADER_ART.get(invader["art"])
                   or KITCHEN_INVADER_ART.get(invader["art"]) or ALIEN_INVADER_ART[invader["art"]])
            save(art(), f"invaders/{biome_id}/{invader['id']}.png")
    print("Placeholder art written to", ROOT)
