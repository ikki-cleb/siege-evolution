"""Draws the 16x16 relic icons into art/relics/<id>.png.

Designs live in tools/relics/designs.py (one function per relic id in
data/relics.json). It also writes the rarity badges drawn behind them
(art/relics/badge_<rarity>.png). Usage:
    python3 tools/draw_relics.py              # write every icon
    python3 tools/draw_relics.py --preview out.png   # contact sheet only
"""
import json
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "relics"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from designs import DESIGNS  # noqa: E402
from kit import Icon, hexc, shade  # noqa: E402

OUT_DIR = os.path.join(ROOT, "art", "relics")
RARITY = {"common": "#c8c0c8", "rare": "#60a8ff", "epic": "#c070ff"}


def draw(relic):
    icon = Icon()
    DESIGNS[relic["id"]](icon, relic["color"])
    return icon.finish()


def rarity_badge(rarity):
    """The 20x20 backing behind an icon, in the rarity's color."""
    img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = hexc(RARITY[rarity])
    d.rounded_rectangle((0, 0, 19, 19), 3, fill=shade(color, -0.5), outline=color)
    d.rounded_rectangle((1, 1, 18, 18), 2, outline=shade(color, -0.3))
    return img


def badge(relic, scale):
    """The icon on its rarity badge, as the game shows it (20x20 pixels)."""
    img = rarity_badge(relic["rarity"])
    img.alpha_composite(draw(relic), (2, 2))
    return img.resize((20 * scale, 20 * scale), Image.NEAREST)


def preview(relics, path):
    fonts = os.path.join(ROOT, "assets", "fonts")
    title = ImageFont.truetype(os.path.join(fonts, "Coiny-Regular.ttf"), 18)
    head = ImageFont.truetype(os.path.join(fonts, "Coiny-Regular.ttf"), 28)
    body = ImageFont.truetype(os.path.join(fonts, "SpaceMono-Regular.ttf"), 12)
    cols, cw, ch, gap, pad = 5, 280, 120, 10, 24
    groups = [(r, [x for x in relics if x["rarity"] == r]) for r in RARITY]
    height = pad + 56 + sum(44 + ((len(g) + cols - 1) // cols) * (ch + gap) for _, g in groups)
    sheet = Image.new("RGBA", (pad * 2 + cols * cw + (cols - 1) * gap, height), (23, 13, 20, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, pad), "Relics (%d)" % len(relics), font=head, fill=(243, 227, 234))
    y = pad + 56
    for rarity, group in groups:
        d.text((pad, y), "%s (%d)" % (rarity.upper(), len(group)), font=title, fill=RARITY[rarity])
        y += 34
        for n, relic in enumerate(group):
            x = pad + (n % cols) * (cw + gap)
            yy = y + (n // cols) * (ch + gap)
            d.rounded_rectangle((x, yy, x + cw, yy + ch), 8, fill=(42, 22, 34), outline=RARITY[rarity], width=2)
            sheet.alpha_composite(badge(relic, 4), (x + 8, yy + 12))
            d.text((x + 98, yy + 10), relic["name"], font=title, fill=(243, 227, 234))
            for j, line in enumerate(textwrap.wrap(relic["desc"], 24)[:5]):
                d.text((x + 98, yy + 38 + j * 15), line, font=body, fill=(210, 195, 202))
        y += ((len(group) + cols - 1) // cols) * (ch + gap) + 10
    sheet.save(path)


def main():
    relics = json.load(open(os.path.join(ROOT, "data", "relics.json")))
    missing = [r["id"] for r in relics if r["id"] not in DESIGNS]
    if missing:
        sys.exit("No design for: " + ", ".join(missing))
    if "--preview" in sys.argv:
        preview(relics, sys.argv[sys.argv.index("--preview") + 1])
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    for relic in relics:
        draw(relic).save(os.path.join(OUT_DIR, relic["id"] + ".png"))
    for rarity in RARITY:
        rarity_badge(rarity).save(os.path.join(OUT_DIR, "badge_%s.png" % rarity))
    print("Wrote %d relic icons to %s" % (len(relics), OUT_DIR))


if __name__ == "__main__":
    main()
