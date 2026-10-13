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
import json
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


# Units that stand under the track and shoot at the parade: the same five
# units (one per pack) in every world; each load picks a world at random.
# Ids are Immune Defense's (where pack stats live); other worlds rename them.
SHOOTER_IDS = ["dendritic_cell", "basophil", "antibody_tagger", "cytokine_storm", "killer_t"]
PACKS = ["fortress", "swarm", "precision", "control", "toxin"]
PACK_COLORS = ["#d1603d", "#e9c46a", "#4ea8de", "#9d79d6", "#6cc551"]
WORLDS = ["backyard_bugs", "wild_kingdom", "immune_system", "total_war", "galactic_siege",
          "kitchen_defense", "birthday_bash"]


def shooters(world):
    """The five shooters' art paths in one world (renamed per world)."""
    content = json.loads((PROJECT / "tools" / "content" / f"{world}.json").read_text())
    renames = content.get("renames", {})
    return [f"{world}/units/{pack}/{renames.get(uid, [uid])[0]}"
            for uid, pack in zip(SHOOTER_IDS, PACKS)]


def data_url(path):
    data = base64.b64encode((PROJECT / "art" / "anim" / path).read_bytes()).decode()
    return f"url(data:image/png;base64,{data})"


def main():
    rules = [font_face(family, path, letters) for family, (path, letters) in FONTS.items()]
    for index, path in enumerate(MARCHERS):
        rules.append(f"#parade .inv-{index} b {{ background-image: {data_url(path + '_move.png')}; }}")
        rules.append(f"#parade .inv-{index}.dead b {{ background-image: {data_url(path + '_death.png')}; }}")
    for index, color in enumerate(PACK_COLORS):
        rules.append(f"#units .unit-{index} {{ --pack: {color}; }}")
    for w, world in enumerate(WORLDS):
        for index, path in enumerate(shooters(world)):
            rules.append(f"#units .w{w}.unit-{index} b {{ background-image: {data_url(path + '_idle.png')}; }}")
            rules.append(f"#units .w{w}.unit-{index}.firing b {{ background-image: {data_url(path + '_attack.png')}; }}")
    block = ("/* PARADE START (made by tools/make_loading_parade.py; don't edit by hand) */\n"
             + "\n".join(rules) + "\n/* PARADE END */")
    text = SHELL.read_text()
    text = re.sub(r"/\* PARADE START.*?PARADE END \*/", lambda _: block, text, flags=re.S)
    SHELL.write_text(text)
    print(f"Embedded {len(MARCHERS)} marchers, {len(SHOOTER_IDS)} shooters x {len(WORLDS)} worlds and {len(FONTS)} fonts in {SHELL.relative_to(PROJECT)} "
          f"({len(block) // 1024} KB)")


if __name__ == "__main__":
    main()
