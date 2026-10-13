"""Draws the animated 32x32 spawners (where invaders come from).

Writes a 4-frame strip (128x32) per world/variant, next to that world's
tiles: art/tiles/<world>/[<variant>/]spawner.png (Total War's bathtub drain
is sea_spawner.png). The board plays the strip in a loop on every spawn
tile. Designs live in tools/spawners/designs.py.

    python3 tools/draw_spawners.py                     # write every strip
    python3 tools/draw_spawners.py --preview out.png   # contact sheet only
Then run `godot --headless --import`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spawners"))
sys.path.insert(0, os.path.join(HERE, "sprites"))

from PIL import Image  # noqa: E402

from designs import FRAMES, SPAWNERS  # noqa: E402
from kit import SIZE, Canvas  # noqa: E402


def frames(design):
    result = []
    for t in range(FRAMES):
        canvas = Canvas()
        design(canvas, t)
        result.append(canvas.finish().img)
    return result


def strip(design):
    image = Image.new("RGBA", (SIZE * FRAMES, SIZE), (0, 0, 0, 0))
    for t, frame in enumerate(frames(design)):
        image.alpha_composite(frame, (t * SIZE, 0))
    return image


def preview(path):
    scale = 3
    names = sorted(SPAWNERS)
    sheet = Image.new("RGBA", (FRAMES * (SIZE * scale + 8) + 40, len(names) * (SIZE * scale + 8) + 8),
                      (60, 70, 60, 255))
    for row, name in enumerate(names):
        for t, frame in enumerate(frames(SPAWNERS[name])):
            sheet.alpha_composite(frame.resize((SIZE * scale, SIZE * scale), Image.NEAREST),
                                  (8 + t * (SIZE * scale + 8), 8 + row * (SIZE * scale + 8)))
    sheet.save(path)
    print("\n".join("%d: %s" % (n, name) for n, name in enumerate(names)))


def main():
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
        return
    for name, design in SPAWNERS.items():
        out = os.path.join(ROOT, "art", "tiles", name)
        strip(design).save(out)
    print("Wrote %d spawner strips" % len(SPAWNERS))


if __name__ == "__main__":
    main()
