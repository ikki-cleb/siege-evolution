"""Makes a contact sheet of a world's drawn sprites: python3 tools/preview_sprites.py <world> <out.png>"""
import json
import sys
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent


def main(world, out):
    sys.path.insert(0, str(PROJECT / "tools"))
    from make_placeholder_anims import pack_rows
    all_content = {}
    for path in (PROJECT / "tools" / "content").glob("*.json"):
        d = json.loads(path.read_text())
        all_content[d["biome"]["id"]] = d
    base = PROJECT / "art" / "anim" / world
    units = [(pid, uid) for pid, uid, _ in pack_rows(all_content[world], all_content)]
    cell = 34
    rows = len(units) // 3 + len(all_content[world]["invaders"]) // 2 + 2
    sheet = Image.new("RGBA", (3 * (5 * cell + 8), rows * cell), (46, 34, 44, 255))
    for i, (pid, uid) in enumerate(units):
        r, col = divmod(i, 3)
        x0 = col * (5 * cell + 8)
        idle = Image.open(base / "units" / pid / f"{uid}_idle.png")
        frames = [idle.crop((0, 0, 32, 32)), idle.crop((32, 0, 64, 32))]
        atk = base / "units" / pid / f"{uid}_attack.png"
        if atk.exists():
            a = Image.open(atk)
            frames += [a.crop((f * 32, 0, f * 32 + 32, 32)) for f in range(3)]
        for f, img in enumerate(frames):
            sheet.alpha_composite(img, (x0 + f * cell + 1, r * cell + 1))
    y0 = (len(units) // 3 + 1) * cell
    for i, inv in enumerate(all_content[world]["invaders"]):
        r, col = divmod(i, 2)
        for k, anim in enumerate(("move", "death")):
            s = Image.open(base / "invaders" / f"{inv['id']}_{anim}.png")
            for f in range(4):
                sheet.alpha_composite(s.crop((f * 32, 0, f * 32 + 32, 32)), (col * 8 * cell + (k * 4 + f) * cell + 1 + col * 8, y0 + r * cell + 1))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
