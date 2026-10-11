"""Brings painted level backgrounds into the game.

Put the images in one folder, named <world_id>_level_NN.png (for example
kitchen_defense_level_03.png), then run from the project folder:

    python3 tools/import_backgrounds.py path/to/folder

Each image is center-cropped to the board's 9:14 portrait shape, resized to
720x1120, softened (see soften(): a light filter so backgrounds stay calm
and game sprites stand out), and saved as a compressed WebP in art/backgrounds/<world>/level_NN.webp
(WebP keeps the web build small). It also writes a Godot .import file that
tells Godot to store the image with lossy compression; Godot's default
(lossless) made each background ~2 MB inside the game and the web build
went over the 16 MB-per-file artifact limit with just 5 of them. Then rebuild:

    godot --headless --import
    godot --headless --script tools/build_content.gd
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

PROJECT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 720, 1120  # 5x the 144x224-pixel board (about 1:1 with a 1080p phone screen)
QUALITY = 85
# The "Light" filter the user picked: 30% less color, a bit less contrast,
# a touch brighter. Set all three to 1.0 to import images untouched.
SATURATION = 0.7
CONTRAST = 0.85
BRIGHTNESS = 1.04
NAME = re.compile(r"^([a-z_]+)_level_(\d\d)$")


def fit(image):
    """Center-crops to 9:14, then resizes to WIDTH x HEIGHT."""
    image = image.convert("RGB")
    w, h = image.size
    target = WIDTH / HEIGHT
    if w / h > target:  # too wide: trim the sides
        new_w = round(h * target)
        image = image.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
    else:  # too tall: trim top and bottom
        new_h = round(w / target)
        image = image.crop((0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h))
    return image.resize((WIDTH, HEIGHT), Image.LANCZOS)


def soften(image):
    """Calms a background down so it doesn't compete with the game."""
    image = ImageEnhance.Color(image).enhance(SATURATION)
    image = ImageEnhance.Contrast(image).enhance(CONTRAST)
    return ImageEnhance.Brightness(image).enhance(BRIGHTNESS)


IMPORT_SETTINGS = """[remap]

importer="texture"
type="CompressedTexture2D"

[params]

compress/mode=1
compress/lossy_quality=0.4
mipmaps/generate=false
"""


def write_import_settings(image_path):
    """Makes Godot store this background lossy (small) instead of lossless."""
    settings = image_path.with_name(image_path.name + ".import")
    text = settings.read_text() if settings.exists() else ""
    if "compress/mode=1" in text:
        return
    if "compress/mode=" in text:
        text = text.replace("compress/mode=0", "compress/mode=1")
    else:
        text = IMPORT_SETTINGS
    settings.write_text(text)


def main(folder):
    worlds = {p.stem for p in (PROJECT / "tools" / "content").glob("*.json")}
    done = 0
    for path in sorted(Path(folder).iterdir()):
        match = NAME.match(path.stem)
        if not match or path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            print("skipped (name should be <world_id>_level_NN.png):", path.name)
            continue
        world, number = match.groups()
        if world not in worlds:
            print("skipped (unknown world):", path.name)
            continue
        out = PROJECT / "art" / "backgrounds" / world / f"level_{number}.webp"
        out.parent.mkdir(parents=True, exist_ok=True)
        soften(fit(Image.open(path))).save(out, "WEBP", quality=QUALITY)
        write_import_settings(out)
        print(f"{path.name} -> {out.relative_to(PROJECT)} ({out.stat().st_size // 1024} KB)")
        done += 1
    print(done, "background(s) imported.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
