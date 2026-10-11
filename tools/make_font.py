"""Builds the game's two fonts from their open-source originals.

  Titles and buttons:  Coiny          -> assets/fonts/SiegeTitle.ttf
  All other text:      Space Mono     -> assets/fonts/SiegeText.ttf

The originals (assets/fonts/Coiny-Regular.ttf, SpaceMono-Regular.ttf) stay
untouched. Each copy gets three small pixel-style icons the game types into
text, drawn at the size of the font's digits:
  U+E000  coin (the currency; scripts write it as Palette.COIN)
  U+2192  right arrow (upgrade previews: "dmg 9 -> 17")
  U+2605  star (earned achievements)

SCALE shrinks or grows a whole font without touching any font sizes in the
scripts (it changes the font's "units per em"). Space Mono runs wide, so it's
drawn a bit smaller to fit the screens that were laid out for the old font.

Run from the project folder:  python3 tools/make_font.py
Needs fontTools:  pip install fonttools

Both fonts are licensed under the SIL Open Font License
(assets/fonts/OFL-Coiny.txt, OFL-SpaceMono.txt); modified versions must keep
that license and use a different name, which these do.
"""
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

PROJECT = Path(__file__).resolve().parent.parent
FONTS = PROJECT / "assets" / "fonts"

# source file, output file, new family name, scale (1.0 = as designed),
# characters to mirror left-right (Coiny draws "/" leaning the wrong way,
# so "0/27" read as "0\27"), and characters to redraw as a pointed V
# (Coiny's rounded V and v made "EVOLUTION" read as "EUOLUTION")
BUILDS = [
    ("Coiny-Regular.ttf", "SiegeTitle.ttf", "Siege Title", 1.0, "/", "Vv"),
    ("SpaceMono-Regular.ttf", "SiegeText.ttf", "Siege Text", 0.88, "", ""),
]
V_STROKE = 225  # stroke thickness for redrawn V shapes (Coiny's "l" is ~220)

# The icons, one string per row ('#' = filled pixel). 7 rows tall, like a digit.
EXTRA = {
    0xE000: ("coin", ["..###..", ".#####.", "##.####", "##.####", "#######", ".#####.", "..###.."]),
    0x2192: ("arrowright", [".....", "..#..", "...#.", "#####", "...#.", "..#..", "....."]),
    0x2605: ("star", ["...#...", "..###..", "#######", ".#####.", "..###..", ".##.##.", "##...##"]),
}
OVERLAP = 2  # pixels overlap slightly so no hairline gaps appear between them


def pixel_glyph(rows, left, bottom, top, pixel_w):
    """Turns a picture like [".#.", "###"] into a font glyph whose rows span
    the height of the font's digits."""
    pen = TTGlyphPen(None)
    pixel_h = (top - bottom) / len(rows)
    width = len(rows[0])
    for row_index, row in enumerate(rows):
        y_top = top - row_index * pixel_h
        x = 0
        # One rectangle per run of filled pixels in the row.
        while x < width:
            if row[x] != "#":
                x += 1
                continue
            start = x
            while x < width and row[x] == "#":
                x += 1
            x0 = round(left + start * pixel_w)
            x1 = round(left + x * pixel_w)
            y0 = round(y_top - pixel_h - OVERLAP)
            y1 = round(y_top + OVERLAP)
            # Clockwise outline (TrueType's direction for filled shapes).
            pen.moveTo((x0, y0))
            pen.lineTo((x0, y1))
            pen.lineTo((x1, y1))
            pen.lineTo((x1, y0))
            pen.closePath()
    return pen.glyph()


def mirror(font, char):
    """Flips one character left-right (keeping its outline direction)."""
    glyph = font["glyf"][font.getBestCmap()[ord(char)]]
    coords, ends, flags = glyph.getCoordinates(font["glyf"])
    middle = glyph.xMin + glyph.xMax
    flipped = [(middle - x, y) for x, y in coords]
    # Mirroring reverses each outline's direction; reverse the point order
    # back so the shape still fills.
    new_coords, new_flags, start = [], [], 0
    for end in ends:
        points = list(range(start, end + 1))
        points = [points[0]] + points[1:][::-1]
        new_coords += [flipped[i] for i in points]
        new_flags += [flags[i] for i in points]
        start = end + 1
    glyph.coordinates = type(coords)(new_coords)
    glyph.flags = type(flags)(new_flags)
    glyph.recalcBounds(font["glyf"])


def pointed_v(font, char):
    """Replaces a character with a bold V that has a pointed bottom, the
    same size as the original."""
    name = font.getBestCmap()[ord(char)]
    old = font["glyf"][name]
    x0, x1, bottom, top = old.xMin, old.xMax, max(0, old.yMin), old.yMax
    middle = (x0 + x1) / 2
    stroke = V_STROKE
    # How far down the inside notch reaches: keeps the arms about `stroke` thick.
    notch = bottom + stroke * 1.25
    tip = stroke * 0.42  # half-width of the bottom point
    points = [(x0, top), (x0 + stroke, top), (middle, notch), (x1 - stroke, top),
        (x1, top), (middle + tip, bottom), (middle - tip, bottom)]
    pen = TTGlyphPen(None)
    pen.moveTo(tuple(round(v) for v in points[0]))
    for point in points[1:]:
        pen.lineTo(tuple(round(v) for v in point))
    pen.closePath()
    glyph = pen.glyph()
    font["glyf"][name] = glyph
    glyph.recalcBounds(font["glyf"])
    font["hmtx"][name] = (font["hmtx"][name][0], glyph.xMin)


def build(source, output, family, scale, flip, vees):
    font = TTFont(FONTS / source)
    cmap = font.getBestCmap()
    for char in flip:
        mirror(font, char)
    for char in vees:
        pointed_v(font, char)
    # Size the icons from the font's own "0", so they sit like a digit.
    zero = font["glyf"][cmap[ord("0")]]
    left, bottom, top = 40, zero.yMin, zero.yMax
    pixel_w = (zero.xMax - zero.xMin) / 5
    for char, (name, rows) in EXTRA.items():
        glyph = pixel_glyph(rows, left, bottom, top, pixel_w)
        if name not in font.getGlyphOrder():
            font.setGlyphOrder(font.getGlyphOrder() + [name])
        font["glyf"][name] = glyph
        glyph.recalcBounds(font["glyf"])
        font["hmtx"][name] = (round(left * 2 + pixel_w * len(rows[0])), glyph.xMin)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[char] = name
    # Scale the whole font: more units per em = everything drawn smaller.
    font["head"].unitsPerEm = round(font["head"].unitsPerEm / scale)
    # A modified font gets its own name (as the font license asks).
    for record in font["name"].names:
        if record.nameID in (1, 3, 4, 6, 16):
            record.string = family if record.nameID != 6 else family.replace(" ", "")
    font.save(FONTS / output)
    print("Wrote", (FONTS / output).relative_to(PROJECT))


def main():
    for args in BUILDS:
        build(*args)


if __name__ == "__main__":
    main()
