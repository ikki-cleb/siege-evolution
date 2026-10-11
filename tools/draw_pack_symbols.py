"""Draws each pack's 16x16 symbol into art/packs/:
    <pack>.png        the symbol in the pack's color
    <pack>_empty.png  the same shape as a dark, empty silhouette
The menus fill the silhouette with the color as the pack beats levels.
Usage: python3 tools/draw_pack_symbols.py [--preview out.png]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "relics"))

from PIL import Image  # noqa: E402

from kit import INK, OUTLINE, Icon, ramp  # noqa: E402

OUT_DIR = os.path.join(ROOT, "art", "packs")
# Same colors as the packs in tools/content/immune_system.json.
PACKS = {
    "fortress": "#d1603d",
    "swarm": "#e9c46a",
    "precision": "#4ea8de",
    "control": "#9d79d6",
    "toxin": "#6cc551",
}
EMPTY = (52, 40, 50, 255)
EMPTY_EDGE = (96, 80, 94, 255)


def fortress(i, c):
    # A castle tower with battlements and a gate.
    light, base, dark, darker = ramp(c)
    i.rect(3, 4, 12, 14, base)
    for x in (3, 7, 11):
        i.rect(x - 1, 1, x + 1, 4, base)
        i.rect(x - 1, 1, x + 1, 1, light)
    i.rect(12, 4, 12, 14, dark)
    i.rect(3, 4, 3, 14, light)
    i.ell(6, 9, 9, 14, darker)
    i.rect(6, 12, 9, 14, darker)
    i.pxs([(5, 6), (10, 6)], darker)


def swarm(i, c):
    # A honeycomb cluster of seven cells.
    light, base, dark, darker = ramp(c)
    cell = [".ddd.", "dbbbd", "dlbbd", "dbbbd", ".ddd."]
    for x, y in ((5, 0), (1, 3), (9, 3), (5, 5), (1, 8), (9, 8), (5, 10)):
        i.grid(x, y, cell, {"d": dark, "b": base, "l": light})


def precision(i, c):
    # A crosshair.
    light, base, dark, darker = ramp(c)
    i.ell(1, 1, 14, 14, base)
    i.ell(3, 3, 12, 12, (0, 0, 0, 0))
    i.rect(7, 0, 8, 5, base)
    i.rect(7, 10, 8, 15, base)
    i.rect(0, 7, 5, 8, base)
    i.rect(10, 7, 15, 8, base)
    i.rect(7, 7, 8, 8, light)
    i.pxs([(4, 2), (3, 3), (2, 4)], light)


def control(i, c):
    # A snowflake.
    light, base, dark, darker = ramp(c)
    for a, b in (((7, 0), (7, 15)), ((0, 7), (15, 7)), ((2, 2), (13, 13)), ((13, 2), (2, 13))):
        i.line([a, b], base, 2)
    for x, y in ((7, 2), (7, 12), (2, 7), (12, 7)):
        i.pxs([(x - 1, y), (x + 2, y), (x, y - 1), (x, y + 2)], base)
    i.ell(5, 5, 10, 10, base)
    i.ell(6, 6, 9, 9, light)


def toxin(i, c):
    # A poison drop with a skull.
    light, base, dark, darker = ramp(c)
    i.poly([(7, 0), (8, 0), (13, 7), (2, 7)], base)
    i.ell(2, 4, 13, 15, base)
    i.ell(2, 4, 13, 15, base)
    i.pxs([(5, 4), (4, 6)], light)
    i.grid(5, 7, [".####.", "######", "#..#..#"[:6], "######", ".#.#.."],
           {"#": (240, 240, 228, 255)})
    i.pxs([(6, 9), (9, 9)], INK)


DRAW = {"fortress": fortress, "swarm": swarm, "precision": precision, "control": control, "toxin": toxin}


def symbol(pack):
    icon = Icon()
    DRAW[pack](icon, PACKS[pack])
    return icon.finish()


def empty(pack):
    """The symbol's shape filled flat and dark, with its outline."""
    full = symbol(pack)
    img = Image.new("RGBA", full.size, (0, 0, 0, 0))
    for y in range(full.height):
        for x in range(full.width):
            r, g, b, a = full.getpixel((x, y))
            if a == 0:
                continue
            outline = (r, g, b, a) == OUTLINE
            img.putpixel((x, y), EMPTY_EDGE if outline else EMPTY)
    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if "--preview" in sys.argv:
        sheet = Image.new("RGBA", (len(PACKS) * 80 + 10, 170), (23, 13, 20, 255))
        for n, pack in enumerate(PACKS):
            sheet.alpha_composite(empty(pack).resize((64, 64), Image.NEAREST), (10 + n * 80, 10))
            sheet.alpha_composite(symbol(pack).resize((64, 64), Image.NEAREST), (10 + n * 80, 90))
        sheet.save(sys.argv[sys.argv.index("--preview") + 1])
        return
    for pack in PACKS:
        symbol(pack).save(os.path.join(OUT_DIR, pack + ".png"))
        empty(pack).save(os.path.join(OUT_DIR, pack + "_empty.png"))
    print("Wrote %d pack symbols to %s" % (len(PACKS), OUT_DIR))


if __name__ == "__main__":
    main()
