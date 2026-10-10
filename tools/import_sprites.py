"""Brings animated unit and invader art into the game.

Put the files in one folder and run from the project folder:

    python3 tools/import_sprites.py path/to/folder

Names (the full list is in the art brief):
    <world>_<id>_<anim>.png        a strip: frames side by side, square
    <world>_<id>_<anim>_<n>.png    or one file per frame (n = 1, 2, 3...)
  e.g. immune_system_macrophage_attack.png, kitchen_defense_slug_move_2.png
  Units: idle (loops), attack (plays per shot; not for plain walls).
  Invaders: move (loops), death (plays once).

Frames are resized to 64x64 and saved as strips in art/anim/, replacing the
placeholders. Then rebuild:
    godot --headless --import
    godot --headless --script tools/build_content.gd
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_placeholder_anims import FRAME, pack_rows  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
UNIT_ANIMS = ("idle", "attack")
INVADER_ANIMS = ("move", "death")
NAME = re.compile(r"^(.+)_(idle|attack|move|death)(?:_(\d+))?$")


def targets():
    """Every animation the game can use: (world, id, anim) -> output path."""
    all_content = {}
    for path in sorted((PROJECT / "tools" / "content").glob("*.json")):
        content = json.loads(path.read_text())
        all_content[content["biome"]["id"]] = content
    result = {}
    for world, content in all_content.items():
        for pack_id, unit_id, _row in pack_rows(content, all_content):
            for anim in UNIT_ANIMS:
                result[(world, unit_id, anim)] = PROJECT / "art/anim" / world / "units" / pack_id / f"{unit_id}_{anim}.png"
        for invader in content["invaders"]:
            for anim in INVADER_ANIMS:
                result[(world, invader["id"], anim)] = PROJECT / "art/anim" / world / "invaders" / f"{invader['id']}_{anim}.png"
    return result, sorted(all_content, key=len, reverse=True)


def fit_frame(image):
    """One square frame resized to FRAME x FRAME (sharp when growing, smooth when shrinking)."""
    image = image.convert("RGBA")
    side = max(image.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(image, ((side - image.width) // 2, side - image.height))
    return square.resize((FRAME, FRAME), Image.NEAREST if side <= FRAME else Image.LANCZOS)


def split_strip(image):
    """A strip's frames: square, side by side (the height is the frame size)."""
    count = max(1, image.width // image.height)
    return [image.crop((i * image.height, 0, (i + 1) * image.height, image.height)) for i in range(count)]


def main(folder):
    known, worlds = targets()
    groups = defaultdict(list)  # (world, id, anim) -> [(frame number, path)]
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() not in (".png", ".webp"):
            continue
        match = NAME.match(path.stem)
        world = next((w for w in worlds if match and match.group(1).startswith(w + "_")), None)
        if not match or world is None:
            print("skipped (name should be <world>_<id>_<anim>.png):", path.name)
            continue
        key = (world, match.group(1)[len(world) + 1:], match.group(2))
        if key not in known:
            print("skipped (no such unit/invader animation in that world):", path.name)
            continue
        groups[key].append((int(match.group(3) or 0), path))
    for key, files in sorted(groups.items()):
        frames = []
        for _n, path in sorted(files):
            image = Image.open(path)
            frames += split_strip(image) if len(files) == 1 else [image]
        sheet = Image.new("RGBA", (FRAME * len(frames), FRAME), (0, 0, 0, 0))
        for i, image in enumerate(frames):
            sheet.alpha_composite(fit_frame(image), (i * FRAME, 0))
        out = known[key]
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        print(f"{key[0]} {key[1]} {key[2]}: {len(frames)} frames -> {out.relative_to(PROJECT)}")
    print(len(groups), "animation(s) imported.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
