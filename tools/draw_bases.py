"""Draws each world's home base as one big 3x2-tile sprite with depth.

The base covers 3x2 tiles on the board. Art is drawn at the same pixel
density as the units (32 pixels per tile), so each base is 96 pixels wide
and 80 tall: 64 for the two tile rows plus 16 of headroom above, so roofs,
flags and candles can stick up. Light comes from the top-left: left and top
faces are lighter, right faces and undersides darker, with a soft shadow on
the ground and a dark outline around everything.

Run from the project folder, then import:
    python3 tools/draw_bases.py
    godot --headless --import

Writes art/tiles/<world>/base_big.png. To use your own art instead, replace
that file (96x80, transparent background, the bottom 64 rows sit on the
base's tiles).
"""
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parent.parent
W, H = 96, 80
GROUND = 76  # where the base meets the ground (a little above the bottom)
OUTLINE = (24, 14, 22, 255)


def hexc(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def shade(color, amount):
    """Lighter (> 0) or darker (< 0) version of a color."""
    if amount >= 0:
        return tuple(int(c + (255 - c) * amount) for c in color[:3]) + (color[3],)
    return tuple(int(c * (1 + amount)) for c in color[:3]) + (color[3],)


class Base:
    def __init__(self):
        self.body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.body)

    def rect(self, x0, y0, x1, y1, color):
        self.d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=color)

    def ellipse(self, cx, cy, rx, ry, color):
        self.d.ellipse((cx - rx, cy - ry, cx + rx - 1, cy + ry - 1), fill=color)

    def poly(self, points, color):
        self.d.polygon(points, fill=color)

    def cylinder(self, cx, top, bottom, rx, ry, color):
        """An upright cylinder: shaded body (light left, dark right) and a lit top."""
        bands = [(0.0, 0.22), (0.18, 0.1), (0.5, 0.0), (0.78, -0.18), (0.92, -0.32)]
        x_left = cx - rx
        for i, (start, amount) in enumerate(bands):
            end = bands[i + 1][0] if i + 1 < len(bands) else 1.0
            x0 = round(x_left + start * 2 * rx)
            x1 = round(x_left + end * 2 * rx)
            self.rect(x0, top, x1, bottom, shade(color, amount))
        # Rounded bottom edge and a lighter top face.
        self.ellipse(cx, bottom, rx, ry, shade(color, -0.2))
        self.ellipse(cx, top, rx, ry, shade(color, 0.3))
        self.ellipse(cx - rx * 0.25, top - ry * 0.2, rx * 0.45, ry * 0.4, shade(color, 0.45))

    def box(self, x0, y0, x1, y1, depth, color, top_color=None):
        """A block seen from slightly above-right: front face, a darker right
        side going back by `depth`, and a lighter top."""
        top_color = top_color or shade(color, 0.25)
        self.poly([(x0, y0), (x0 + depth, y0 - depth), (x1 + depth, y0 - depth), (x1, y0)], top_color)
        self.poly([(x1, y0), (x1 + depth, y0 - depth), (x1 + depth, y1 - depth), (x1, y1)], shade(color, -0.3))
        self.rect(x0, y0, x1, y1, color)
        self.rect(x0, y0, x0 + 2, y1, shade(color, 0.15))  # lit left edge

    def finish(self):
        """Dark outline around the art, then a soft shadow on the ground under it."""
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow = ImageDraw.Draw(out)
        shadow.ellipse((8, GROUND - 6, W - 6, GROUND + 3), fill=(0, 0, 0, 90))
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        src = self.body.load()
        dst = ring.load()
        for y in range(H):
            for x in range(W):
                if src[x, y][3] > 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and src[nx, ny][3] > 0:
                        dst[x, y] = OUTLINE
                        break
        out.alpha_composite(ring)
        out.alpha_composite(self.body)
        return out


# --- The seven bases ----------------------------------------------------------

def anthill():
    """Backyard Bugs: the queen's anthill, a big layered dirt mound."""
    b = Base()
    dirt = hexc("#a0703f")
    for i, (rx, ry, cy) in enumerate([(44, 16, GROUND - 10), (36, 16, GROUND - 22), (26, 14, GROUND - 34), (16, 10, GROUND - 44)]):
        b.ellipse(48, cy, rx, ry, shade(dirt, -0.12 * (3 - i) * 0.5))
        b.ellipse(48 - rx * 0.25, cy - ry * 0.35, rx * 0.6, ry * 0.5, shade(dirt, 0.12 + 0.03 * i))
        b.ellipse(48 + rx * 0.45, cy + ry * 0.2, rx * 0.4, ry * 0.5, shade(dirt, -0.25))
    # Crumbs of soil and the entrance on top.
    for x, y in [(22, 58), (34, 50), (62, 46), (70, 60), (40, 66), (58, 64), (30, 40)]:
        b.rect(x, y, x + 2, y + 2, shade(dirt, -0.35))
        b.rect(x - 1, y - 1, x + 1, y, shade(dirt, 0.3))
    b.ellipse(48, GROUND - 52, 8, 4, hexc("#3a2414"))
    b.ellipse(48, GROUND - 51, 5, 2, hexc("#1a0f08"))
    return b.finish()


def farmhouse():
    """Wild Kingdom: a red farmhouse with a shingled roof."""
    b = Base()
    wall, roof = hexc("#c0453a"), hexc("#7a3b2a")
    b.box(14, 36, 74, GROUND, 10, wall)
    # Roof: front slope and the darker right side.
    b.poly([(8, 38), (44, 8), (80, 38)], roof)
    b.poly([(44, 8), (54, -2), (90, 28), (80, 38)], shade(roof, -0.3))
    b.poly([(8, 38), (44, 8), (44, 14), (16, 38)], shade(roof, 0.25))
    for y in range(16, 38, 6):  # shingle lines
        half = (y - 8) * 36 // 30
        b.rect(44 - half + 2, y, 44 + half - 2, y + 1, shade(roof, -0.15))
    # Door, windows, trim.
    b.rect(36, 52, 52, GROUND, hexc("#5a2a1a"))
    b.rect(38, 54, 50, GROUND, hexc("#7a3a24"))
    b.rect(48, 64, 50, 66, hexc("#e8c070"))
    for x in (20, 58):
        b.rect(x, 46, x + 12, 58, hexc("#f4e8c8"))
        b.rect(x + 2, 48, x + 10, 56, hexc("#5aa0d0"))
        b.rect(x + 2, 48, x + 5, 51, hexc("#a8d8f0"))
        b.rect(x + 5, 48, x + 7, 56, hexc("#f4e8c8"))
    b.rect(14, 36, 74, 38, shade(wall, 0.3))
    return b.finish()


def heart():
    """Immune Defense: a big, glossy heart (no face: it's an organ)."""
    b = Base()
    red = hexc("#e0405a")
    for i, amount in enumerate([-0.35, -0.15, 0.0]):
        inset = i * 3
        b.ellipse(32 + inset // 2, 34 + inset // 2, 22 - inset, 22 - inset, shade(red, amount))
        b.ellipse(62 - inset // 2, 34 + inset // 2, 22 - inset, 22 - inset, shade(red, amount))
        b.poly([(12 + inset, 37), (83 - inset, 37), (48, GROUND - 2 - inset)], shade(red, amount))
    # Shading: darker lower right, light top-left, a glossy highlight.
    b.ellipse(60, 52, 12, 10, shade(red, -0.12))
    b.ellipse(30, 28, 12, 9, shade(red, 0.25))
    b.ellipse(26, 24, 5, 4, shade(red, 0.6))
    b.ellipse(64, 26, 6, 4, shade(red, 0.3))
    # Blood vessels on top.
    for x0, x1 in ((40, 44), (50, 54)):
        b.rect(x0, 6, x1, 18, hexc("#4a6ad0") if x0 == 40 else hexc("#c03048"))
        b.rect(x0, 6, x0 + 1, 18, shade(hexc("#4a6ad0") if x0 == 40 else hexc("#c03048"), 0.3))
    return b.finish()


def toy_fort():
    """Total War: a toy fort HQ with towers and a flag."""
    b = Base()
    stone = hexc("#8a9a6a")
    # Back to front: right tower, the wall between, then the left tower.
    for x in (66,):
        b.box(x, 24, x + 18, GROUND, 6, shade(stone, -0.05))
        for cx in range(x, x + 18, 6):
            b.box(cx, 18, cx + 4, 24, 2, shade(stone, -0.05))
    b.box(22, 34, 66, GROUND, 6, stone)
    for cx in range(28, 62, 8):
        b.box(cx, 28, cx + 5, 34, 3, stone)
    for x in (8,):
        b.box(x, 24, x + 18, GROUND, 6, shade(stone, -0.05))
        for cx in range(x, x + 18, 6):
            b.box(cx, 18, cx + 4, 24, 2, shade(stone, -0.05))
    b.rect(38, 52, 52, GROUND, hexc("#3a2a1a"))  # gate
    b.ellipse(45, 52, 7, 6, hexc("#3a2a1a"))
    b.rect(39, 54, 41, GROUND, hexc("#5a4630"))
    for y in range(40, GROUND - 4, 8):  # brick lines
        b.rect(27, y, 66, y + 1, shade(stone, -0.18))
    b.rect(45, 2, 47, 28, hexc("#5a4630"))  # flag pole + flag
    b.poly([(47, 2), (62, 6), (47, 11)], hexc("#e8c040"))
    b.poly([(47, 2), (62, 6), (47, 5)], hexc("#f8e080"))
    return b.finish()


def reactor():
    """Galactic Siege: the colony reactor, a glowing core on a base ring."""
    b = Base()
    metal = hexc("#7a86a0")
    b.cylinder(48, 52, GROUND - 4, 40, 10, shade(metal, -0.1))
    b.cylinder(48, 30, 52, 24, 7, metal)
    # Glowing core dome with light rings.
    b.ellipse(48, 30, 18, 16, hexc("#3aa0e0"))
    b.ellipse(46, 26, 13, 11, hexc("#7ad0ff"))
    b.ellipse(43, 22, 6, 5, hexc("#e0f8ff"))
    for x in (14, 30, 66, 82):
        b.rect(x - 2, 54, x + 2, 64, hexc("#ffd860"))
        b.rect(x - 2, 54, x, 64, hexc("#fff0b0"))
    b.rect(20, 66, 76, 68, shade(metal, -0.35))
    return b.finish()


def cookie_jar():
    """Kitchen Defense: a glass cookie jar with a lid."""
    b = Base()
    glass = hexc("#bfe0e8", 255)
    b.cylinder(48, 22, GROUND - 4, 30, 8, glass)
    # Cookies inside, seen through the glass.
    for cx, cy in [(36, 56), (54, 60), (46, 44), (62, 46), (32, 66), (58, 70)]:
        b.ellipse(cx, cy, 8, 6, hexc("#c8904a"))
        b.ellipse(cx - 2, cy - 2, 5, 3, hexc("#e0b070"))
        for dx, dy in ((-3, 0), (2, -2), (1, 2)):
            b.rect(cx + dx, cy + dy, cx + dx + 2, cy + dy + 2, hexc("#5a3018"))
    b.rect(24, 26, 28, GROUND - 8, hexc("#f0ffff"))  # glass shine
    # Lid with a knob.
    b.cylinder(48, 12, 20, 32, 7, hexc("#d07a40"))
    b.cylinder(48, 2, 10, 8, 3, hexc("#d07a40"))
    return b.finish()


def cake():
    """Birthday Bash: a two-tier birthday cake with candles."""
    b = Base()
    sponge, frosting = hexc("#f4d8b0"), hexc("#ff9ac0")
    b.cylinder(48, 48, GROUND - 4, 40, 9, sponge)
    b.cylinder(48, 26, 48, 26, 7, sponge)
    for cy, rx in ((48, 40), (26, 26)):  # frosting tops and drips
        b.ellipse(48, cy, rx, 9 if rx == 40 else 7, frosting)
        b.ellipse(48 - rx // 3, cy - 2, rx // 2, 3, shade(frosting, 0.4))
        for x in range(48 - rx + 4, 48 + rx - 4, 8):
            b.rect(x, cy + 2, x + 4, cy + 9, frosting)
            b.ellipse(x + 2, cy + 9, 2, 2, frosting)
    for x, color in ((36, "#7ad0ff"), (48, "#ffe060"), (60, "#a0e070")):  # candles
        b.rect(x - 2, 8, x + 2, 24, hexc(color))
        b.rect(x - 2, 8, x - 1, 24, shade(hexc(color), 0.4))
        b.ellipse(x, 5, 2, 3, hexc("#ffb030"))
        b.ellipse(x, 5, 1, 2, hexc("#fff4c0"))
    return b.finish()


BASES = {
    "backyard_bugs": anthill,
    "wild_kingdom": farmhouse,
    "immune_system": heart,
    "total_war": toy_fort,
    "galactic_siege": reactor,
    "kitchen_defense": cookie_jar,
    "birthday_bash": cake,
}


def main():
    for world, design in BASES.items():
        path = PROJECT / "art" / "tiles" / world / "base_big.png"
        design().save(path)
        print("wrote", path.relative_to(PROJECT))


if __name__ == "__main__":
    main()
