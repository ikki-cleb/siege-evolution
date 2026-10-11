"""Makes see-through versions of the rock, spawn and base tiles.

The tiles were drawn on top of each world's floor tile, so on a level with a
painted background they showed up as little squares of the old floor color.
This tool removes every pixel that matches the floor tile underneath, adds a
soft shadow so the obstacle still stands out on busy art, and saves the
result next to the original as <name>_cut.png. The game uses the _cut
version on levels that have a painted background.

Tiles that fill their whole square (no floor pixels showing) are copied as
they are. Run it again after redrawing any tile:

    python3 tools/make_cutout_tiles.py
    godot --headless --import
"""
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
TILES = ["rock", "spawn", "base"]
SHADOW = (0, 0, 0, 90)  # a soft dark copy, 1 pixel down and to the right
# Rocks (obstacles) get a dark outline and a stronger shadow, so they don't
# get mistaken for pebbles painted into the background.
OUTLINE = (18, 14, 20, 230)
ROCK_SHADOW = (0, 0, 0, 150)
# Worlds whose rock tile is a full square: cut it into a rounded blob first.
ROUND_ROCKS = {"immune_system"}


def cut_out(tile, floor):
    """Clears the pixels that are the same as the floor tile."""
    result = tile.copy()
    for y in range(tile.height):
        for x in range(tile.width):
            if tile.getpixel((x, y)) == floor.getpixel((x, y)):
                result.putpixel((x, y), (0, 0, 0, 0))
    return result


def add_shadow(tile, color=SHADOW):
    """Puts a shadow under the art, so it reads on any background."""
    shadow = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    for y in range(tile.height):
        for x in range(tile.width):
            if tile.getpixel((x, y))[3] > 0 and x + 1 < tile.width and y + 1 < tile.height:
                shadow.putpixel((x + 1, y + 1), color)
    shadow.alpha_composite(tile)
    return shadow


def add_outline(tile):
    """Draws a 1-pixel dark line around the art, on its see-through edge."""
    result = tile.copy()
    for y in range(tile.height):
        for x in range(tile.width):
            if tile.getpixel((x, y))[3] > 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < tile.width and 0 <= ny < tile.height and tile.getpixel((nx, ny))[3] > 0:
                    result.putpixel((x, y), OUTLINE)
                    break
    return result


def round_off(tile):
    """Keeps only a rounded blob in the middle of a square tile."""
    result = tile.copy()
    center = (tile.width - 1) / 2
    for y in range(tile.height):
        for x in range(tile.width):
            if (x - center) ** 2 + (y - center) ** 2 > 6.3 ** 2:
                result.putpixel((x, y), (0, 0, 0, 0))
    return result


def main():
    made = 0
    for floor_path in sorted(PROJECT.glob("art/tiles/**/floor.png")):
        folder = floor_path.parent
        floor = Image.open(floor_path).convert("RGBA")
        for name in TILES:
            path = folder / f"{name}.png"
            if not path.exists():
                continue
            tile = Image.open(path).convert("RGBA")
            cut = cut_out(tile, floor)
            if name == "rock" and folder.name in ROUND_ROCKS:
                cut = round_off(cut)
            if all(cut.getpixel((x, y))[3] > 0 for x in range(cut.width) for y in range(cut.height)):
                result = tile  # fills its whole square: keep it as a solid block
            elif name == "rock":
                result = add_shadow(add_outline(cut), ROCK_SHADOW)
            else:
                result = add_shadow(cut)
            result.save(folder / f"{name}_cut.png")
            made += 1
    print(made, "cut-out tile(s) written.")


if __name__ == "__main__":
    main()
