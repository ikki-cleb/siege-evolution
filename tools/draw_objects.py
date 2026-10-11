"""Draws the 32x32 map objects: each world's obstacles (3 looks each) and
Total War's animated water.

Writes next to each world's tiles:
  obstacle.png    3 rows (looks) x 1 column, or x 4 columns if animated
  water_anim.png  1 row x 4 frames (seamless water)
The board picks a look per obstacle tile (fixed by its position). Designs
live in tools/objects/designs.py.

    python3 tools/draw_objects.py                     # write everything
    python3 tools/draw_objects.py --preview out.png   # contact sheet only
Then run `godot --headless --import`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "objects"))
sys.path.insert(0, os.path.join(HERE, "sprites"))

from PIL import Image  # noqa: E402

from designs import FRAMES, LOOKS, OBSTACLES, WATER, water  # noqa: E402
from kit import SIZE, Canvas  # noqa: E402


# The "map object" look, so obstacles never read as units: colors a bit
# muted, and a soft outline in each object's own darker color (units have a
# black outline, a pad and animate).
MUTE = 0.28        # how much color is taken out (0 = none, 1 = grey)
OUTLINE_DARKEN = 0.5


# Worlds with very busy, colorful backgrounds get bolder objects: less
# muted and a darker outline, so they don't fade into the art (the user's
# pick for Birthday Bash). world id -> (mute, outline darken)
BOLD_WORLDS = {"birthday_bash": (0.0, 0.25)}


def object_style(img, world=""):
    mute, darken = BOLD_WORLDS.get(world, (MUTE, OUTLINE_DARKEN))
    pix = img.load()
    w, h = img.size
    # Mute the solid pixels (shadows are see-through, leave them).
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a < 200:
                continue
            grey = 0.3 * r + 0.59 * g + 0.11 * b
            pix[x, y] = tuple(int(c + (grey - c) * mute) for c in (r, g, b)) + (a,)
    # Outline every solid shape with a darker copy of the color next to it.
    src = img.copy()
    spix = src.load()
    for y in range(h):
        for x in range(w):
            if spix[x, y][3] >= 200:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and spix[nx, ny][3] >= 200:
                    r, g, b, _ = spix[nx, ny]
                    pix[x, y] = (int(r * darken), int(g * darken), int(b * darken), 255)
                    break
    return img


def obstacle_sheet(design, animated, world=""):
    frames = FRAMES if animated else 1
    sheet = Image.new("RGBA", (SIZE * frames, SIZE * LOOKS), (0, 0, 0, 0))
    for v in range(LOOKS):
        for t in range(frames):
            canvas = Canvas()
            design(canvas, v, t)
            sheet.alpha_composite(object_style(canvas.img, world), (t * SIZE, v * SIZE))
    return sheet


def water_strip(color):
    strip = Image.new("RGBA", (SIZE * FRAMES, SIZE), (0, 0, 0, 0))
    for t in range(FRAMES):
        canvas = Canvas()
        water(canvas, t, color)
        strip.alpha_composite(canvas.img, (t * SIZE, 0))
    return strip


def preview(path):
    scale = 3
    cell = SIZE * scale + 8
    names = sorted(OBSTACLES)
    sheet = Image.new("RGBA", (LOOKS * cell + 8, (len(names) + 1) * cell + 8), (70, 80, 66, 255))
    for row, name in enumerate(names):
        design, animated = OBSTACLES[name]
        art = obstacle_sheet(design, animated)
        for v in range(LOOKS):
            look = art.crop((0, v * SIZE, SIZE, (v + 1) * SIZE))
            sheet.alpha_composite(look.resize((SIZE * scale, SIZE * scale), Image.NEAREST),
                                  (8 + v * cell, 8 + row * cell))
    strip = water_strip(next(iter(WATER.values())))
    for t in range(min(LOOKS, FRAMES)):
        frame = strip.crop((t * SIZE, 0, (t + 1) * SIZE, SIZE))
        sheet.alpha_composite(frame.resize((SIZE * scale, SIZE * scale), Image.NEAREST),
                              (8 + t * cell, 8 + len(names) * cell))
    sheet.save(path)
    print("\n".join("%d: %s" % (n, name) for n, name in enumerate(names + ["water"])))


def main():
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
        return
    for name, (design, animated) in OBSTACLES.items():
        obstacle_sheet(design, animated, name.split("/")[0]).save(os.path.join(ROOT, "art", "tiles", name))
    for name, color in WATER.items():
        water_strip(color).save(os.path.join(ROOT, "art", "tiles", name))
    print("Wrote %d obstacle sets and %d water strips" % (len(OBSTACLES), len(WATER)))


if __name__ == "__main__":
    main()
