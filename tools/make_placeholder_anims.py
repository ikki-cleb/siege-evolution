"""Makes simple placeholder animation strips from the current 16x16 sprites.

Run from the project folder:  python3 tools/make_placeholder_anims.py
Then:  godot --headless --import  and the content build.

Each strip is one PNG with 64x64 frames side by side (art/anim/<world>/...):
  units:    <id>_idle.png (2 frames), <id>_attack.png (3 frames, attackers only)
  invaders: <id>_move.png (4 frames), <id>_death.png (4 frames)
Base units and tier-1 evolutions get strips; capstones reuse tier 1's.
Existing strips are never overwritten, so real art is safe.
"""
import json
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
ART = PROJECT / "art"
FRAME = 64
CAN_ATTACK = ("damage", "slow", "poison", "mark", "stun")


def pack_rows(content, all_content):
    """A world's packs with that world's unit ids (as tools/build_content.gd does)."""
    renames = content.get("renames", {})
    rows = []
    for pack in all_content[content.get("packs_from", content["biome"]["id"])]["packs"]:
        for unit in pack["units"]:
            rows.append((pack["id"], renames.get(unit["id"], [unit["id"]])[0], unit))
            for evo in unit["evolutions"]:
                merged = dict(unit)
                merged.update(evo)
                rows.append((pack["id"], renames.get(evo["id"], [evo["id"]])[0], merged))
    return rows


def frame(source, sx=1.0, sy=1.0, dy=0, alpha=1.0):
    """One 64x64 frame: the 16x16 sprite scaled up 4x, then squashed/moved."""
    big = source.resize((FRAME, FRAME), Image.NEAREST)
    w, h = max(1, round(FRAME * sx)), max(1, round(FRAME * sy))
    big = big.resize((w, h), Image.NEAREST)
    if alpha < 1.0:
        big.putalpha(big.getchannel("A").point(lambda a: int(a * alpha)))
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    # Keep the feet on the ground: squashes anchor to the bottom center.
    out.alpha_composite(big, ((FRAME - w) // 2, FRAME - h + dy) if sy <= 1 else ((FRAME - w) // 2, (FRAME - h) // 2 + dy))
    return out


def strip(frames, path):
    if path.exists():
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (FRAME * len(frames), FRAME), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.alpha_composite(f, (i * FRAME, 0))
    sheet.save(path)
    return 1


def main():
    all_content = {}
    for path in sorted((PROJECT / "tools" / "content").glob("*.json")):
        content = json.loads(path.read_text())
        all_content[content["biome"]["id"]] = content
    made = 0
    for world, content in all_content.items():
        for pack_id, unit_id, row in pack_rows(content, all_content):
            src = Image.open(ART / "units" / world / pack_id / f"{unit_id}.png").convert("RGBA")
            out = ART / "anim" / world / "units" / pack_id
            made += strip([frame(src), frame(src, 1.0, 15 / 16)], out / f"{unit_id}_idle.png")
            if any(row.get(key) for key in CAN_ATTACK):
                made += strip([frame(src, 1.12, 0.84), frame(src, 0.92, 1.0, -4), frame(src)],
                              out / f"{unit_id}_attack.png")
        for invader in content["invaders"]:
            src = Image.open(ART / "invaders" / world / f"{invader['id']}.png").convert("RGBA")
            out = ART / "anim" / world / "invaders"
            made += strip([frame(src), frame(src, 1.0, 1.0, -4), frame(src), frame(src, 1.06, 0.94)],
                          out / f"{invader['id']}_move.png")
            made += strip([frame(src, 1.15, 1.15, alpha=0.9), frame(src, 1.3, 0.7, alpha=0.7),
                           frame(src, 0.7, 0.5, alpha=0.45), frame(src, 0.4, 0.25, alpha=0.2)],
                          out / f"{invader['id']}_death.png")
    print(made, "placeholder strips written to", ART / "anim")


if __name__ == "__main__":
    main()
