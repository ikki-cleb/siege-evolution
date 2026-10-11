"""Puts the loading screen's art into web/shell.html: the marching
invaders and the game's own fonts.

The loading screen is plain HTML (it shows before the game starts), so the
invaders' walk strips and tiny copies of the game fonts (only the letters
the loading screen uses) are embedded as data URLs between the PARADE
markers. Re-run after redrawing any of these invaders or changing a font:

    python3 tools/make_loading_parade.py
"""
import base64
import io
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

PROJECT = Path(__file__).resolve().parent.parent
SHELL = PROJECT / "web" / "shell.html"
# One invader from each world (4-frame 32x32 walk strips).
MARCHERS = [
    "backyard_bugs/invaders/termite",
    "wild_kingdom/invaders/coyote",
    "immune_system/invaders/rhinovirus",
    "total_war/invaders/toy_recruit",
    "galactic_siege/invaders/grub",
    "kitchen_defense/invaders/sugar_ant",
]


# The game's fonts and the letters the loading screen shows with each.
FONTS = {
    "SiegeTitle": ("assets/fonts/SiegeTitle.ttf", "SIEGEVOLUTN"),
    "SiegeText": ("assets/fonts/SiegeText.ttf",
                  "From the backyard to the stars. Loading 0123456789% Starting... "
                  "The game could not start. This browser is missing:"),
}


def font_face(family, path, letters):
    """A @font-face rule with only `letters` from the font (a few KB)."""
    font = TTFont(PROJECT / path)
    options = subset.Options()
    options.flavor = "woff2" if _has_brotli() else None
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=letters)
    subsetter.subset(font)
    data = io.BytesIO()
    font.flavor = options.flavor
    font.save(data)
    kind = "woff2" if options.flavor else "truetype"
    mime = "font/woff2" if options.flavor else "font/ttf"
    encoded = base64.b64encode(data.getvalue()).decode()
    return f"@font-face {{ font-family: '{family}'; src: url(data:{mime};base64,{encoded}) format('{kind}'); }}"


def _has_brotli():
    try:
        import brotli  # noqa: F401
        return True
    except ImportError:
        return False


# Units that stand under the track and shoot at the parade: one per pack
# (Backyard Bugs, the first world), with the pack's color for pad and shots.
SHOOTERS = [
    ("backyard_bugs/units/fortress/bombardier_beetle", "#d1603d"),
    ("backyard_bugs/units/swarm/honeybee", "#e9c46a"),
    ("backyard_bugs/units/precision/firefly", "#4ea8de"),
    ("backyard_bugs/units/control/click_beetle", "#9d79d6"),
    ("backyard_bugs/units/toxin/paper_wasp", "#6cc551"),
]


def data_url(path):
    data = base64.b64encode((PROJECT / "art" / "anim" / path).read_bytes()).decode()
    return f"url(data:image/png;base64,{data})"


def main():
    rules = [font_face(family, path, letters) for family, (path, letters) in FONTS.items()]
    for index, path in enumerate(MARCHERS):
        rules.append(f"#parade .inv-{index} {{ background-image: {data_url(path + '_move.png')}; }}")
        rules.append(f"#parade .inv-{index}.dead {{ background-image: {data_url(path + '_death.png')}; }}")
    for index, (path, color) in enumerate(SHOOTERS):
        rules.append(f"#units .unit-{index} {{ --pack: {color}; background-image: {data_url(path + '_idle.png')}; }}")
        rules.append(f"#units .unit-{index}.firing {{ background-image: {data_url(path + '_attack.png')}; }}")
    block = ("/* PARADE START (made by tools/make_loading_parade.py; don't edit by hand) */\n"
             + "\n".join(rules) + "\n/* PARADE END */")
    text = SHELL.read_text()
    text = re.sub(r"/\* PARADE START.*?PARADE END \*/", lambda _: block, text, flags=re.S)
    SHELL.write_text(text)
    print(f"Embedded {len(MARCHERS)} marchers, {len(SHOOTERS)} shooters and {len(FONTS)} fonts in {SHELL.relative_to(PROJECT)} "
          f"({len(block) // 1024} KB)")


if __name__ == "__main__":
    main()
