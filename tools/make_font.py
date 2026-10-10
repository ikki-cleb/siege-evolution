"""Builds the game font: Pixelify Sans with clearer, blocky digits and a coin.

Pixelify's own "2" curls back up at the bottom, so at small sizes it looks
like an 8. This script copies assets/fonts/PixelifySans.ttf (the original,
untouched) and swaps in the 0-9 shapes drawn below, saving the result as
assets/fonts/SiegePixel.ttf (the font the game uses).

Run from the project folder:  python3 tools/make_font.py
Needs fontTools:  pip install fonttools

It also adds a coin icon (the in-game currency) as character U+E000, so a
coin can sit inside any text. Scripts write it as Palette.COIN.

To change a digit or the coin, edit its picture below ('#' = filled pixel)
and rerun.
The font is licensed under the SIL Open Font License (assets/fonts/OFL.txt);
modified versions must keep that license, which this one does.
"""
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

PROJECT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT / "assets" / "fonts" / "PixelifySans.ttf"
OUTPUT = PROJECT / "assets" / "fonts" / "SiegePixel.ttf"

DIGITS = {
    "0": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
}

# The coin: 7 pixels wide, drawn at the same pixel size as the digits.
COIN_CHAR = 0xE000
COIN = ["..###..", ".#####.", "##.####", "##.####", "#######", ".#####.", "..###.."]

# Where Pixelify's own digits sit (font units, 1000 per em), so the new ones
# line up with the letters around them.
LEFT, RIGHT = 60, 531
BOTTOM, TOP = -12, 633
OVERLAP = 2  # pixels overlap slightly so no hairline gaps appear between them


PIXEL_W = (RIGHT - LEFT) / 5
PIXEL_H = (TOP - BOTTOM) / 7


def pixel_glyph(rows):
    """Turns a picture like [".#.", "###"] into a font glyph."""
    pen = TTGlyphPen(None)
    pixel_w, pixel_h = PIXEL_W, PIXEL_H
    width = len(rows[0])
    for row_index, row in enumerate(rows):
        y_top = TOP - row_index * pixel_h
        x = 0
        # One rectangle per run of filled pixels in the row.
        while x < width:
            if row[x] != "#":
                x += 1
                continue
            start = x
            while x < width and row[x] == "#":
                x += 1
            x0 = round(LEFT + start * pixel_w)
            x1 = round(LEFT + x * pixel_w)
            y0 = round(y_top - pixel_h - OVERLAP)
            y1 = round(y_top + OVERLAP)
            # Clockwise outline (TrueType's direction for filled shapes).
            pen.moveTo((x0, y0))
            pen.lineTo((x0, y1))
            pen.lineTo((x1, y1))
            pen.lineTo((x1, y0))
            pen.closePath()
    return pen.glyph()


def main():
    font = TTFont(SOURCE)
    cmap = font.getBestCmap()
    for char, rows in DIGITS.items():
        assert len(rows) == 7 and all(len(r) == 5 for r in rows), char
        name = cmap[ord(char)]
        glyph = pixel_glyph(rows)
        font["glyf"][name] = glyph
        glyph.recalcBounds(font["glyf"])
        advance = font["hmtx"][name][0]
        font["hmtx"][name] = (advance, glyph.xMin)
    # The coin is a brand-new character.
    coin = pixel_glyph(COIN)
    font.setGlyphOrder(font.getGlyphOrder() + ["coin"])
    font["glyf"]["coin"] = coin
    coin.recalcBounds(font["glyf"])
    font["hmtx"]["coin"] = (round(LEFT * 2 + PIXEL_W * len(COIN[0])), coin.xMin)
    for table in font["cmap"].tables:
        table.cmap[COIN_CHAR] = "coin"
    # A modified font gets its own name (as the font license asks).
    for record in font["name"].names:
        if record.nameID in (1, 3, 4, 6, 16):
            text = record.toUnicode().replace("Pixelify Sans", "Siege Pixel").replace("PixelifySans", "SiegePixel")
            record.string = text
    font.save(OUTPUT)
    print("Wrote", OUTPUT)


if __name__ == "__main__":
    main()
