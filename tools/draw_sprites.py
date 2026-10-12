"""Draws the game's animated unit and invader sprites in code (32x32 frames).

Run from the project folder:   python3 tools/draw_sprites.py [world ...]
Then:  godot --headless --import  and the content build.

Each world's designs live in tools/sprites/world_<name>.py. A design draws
one pose; this script turns it into strips:
  units:    idle (2 frames, a slow breath) and attack (3 frames, by style)
  invaders: move (4 frames) and death (4 frames, a generic burst)
Tier-1 evolutions are the base design plus a decoration for their branch:
power (spikes, a fiercer look) or reach (an antenna with a lens; walls get
spikes or armor bands). Capstones reuse tier 1 in the game.

Strips you imported with tools/import_sprites.py are never overwritten
(they're listed in art/anim/imported.txt).
"""
import importlib
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sprites.kit import SIZE, Canvas, death_frames, hexc, shade  # noqa: E402
from make_placeholder_anims import pack_rows  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
ANIM = PROJECT / "art" / "anim"
IMPORTED = ANIM / "imported.txt"
WORLD_MODULES = {"immune_system": "world_immune", "backyard_bugs": "world_backyard", "wild_kingdom": "world_farm", "total_war": "world_toys", "galactic_siege": "world_space",
                 "kitchen_defense": "world_kitchen", "birthday_bash": "world_party"}


def pose(**changes):
    p = {"mood": "calm", "mouth": "smile", "act": "idle"}
    p.update(changes)
    return p


def decorate(c, top, branch, style, pc):
    """Marks a tier-1 evolution: power = spikes, reach = an antenna with a lens."""
    x, y = top
    if branch is None:
        return
    if style == "wall":
        if branch == 0:  # more HP: an armor band with rivets
            c.rect(4, 19, 28, 22, shade(pc, -0.2))
            for rx in (7, 12, 17, 22, 26):
                c.px(rx, 20, shade(pc, 0.3))
        else:  # utility: spikes along the top
            for sx_ in (7, 12, 17, 22, 26):
                c.poly([(sx_ - 2, y + 1), (sx_, y - 3), (sx_ + 2, y + 1)], shade(pc, 0.1))
        return
    if branch == 0:  # power: three spikes on the head
        for dx in (-4, 0, 4):
            c.poly([(x + dx - 1.5, y + 1.5), (x + dx, y - 3 - (dx == 0)), (x + dx + 1.5, y + 1.5)], shade(pc, -0.05))
    else:  # reach: a stalk with a lens
        c.line([(x + 5, y + 3), (x + 9, y - 3)], shade(pc, -0.25))
        c.ellipse(x + 9.5, y - 4, 2.4, 2.4, shade(pc, 0.25))
        c.px(x + 9, y - 5, (255, 255, 255, 255))


# Tier-1 evolutions are drawn this much bigger than their base unit (the
# canvas scales around the unit's feet), so upgrades look more powerful.
TIER_SCALE = 1.12


def _draw(design, p, branch, style, pc, sx=1.0, sy=1.0, dx=0.0, dy=0.0, effect=None, tiered=False):
    if tiered and branch is not None:
        sx, sy = sx * TIER_SCALE, sy * TIER_SCALE
    c = Canvas(sx, sy, dx, dy)
    p = dict(p, pc=pc, branch=branch)
    if tiered:
        # New-style designs draw each evolution themselves (p["branch"]:
        # None = base, 0 = power branch, 1 = utility branch); faces stay cute.
        top = design(c, p)
    else:
        if branch == 0 and style != "wall":
            p["mood"] = "angry" if p["mood"] == "calm" else p["mood"]
        top = design(c, p)
        decorate(c, top, branch, style, pc)
    c.finish()
    if effect:
        effect(c, top)
    return c.img


def unit_frames(design, style, branch, pc, can_attack, tiered=False):
    light = shade(pc, 0.3)

    def draw(*args, **kwargs):  # every frame of this unit uses the same style
        return _draw(*args, tiered=tiered, **kwargs)

    idle = [draw(design, pose(), branch, style, pc), draw(design, pose(), branch, style, pc, 1.04, 0.95)]
    if not can_attack:
        return idle, None
    if style == "melee":
        attack = [draw(design, pose(mood="squint", act="wind"), branch, style, pc, 1.1, 0.88),
                  draw(design, pose(mood="angry", mouth="open", act="fire"), branch, style, pc, 0.95, 1.08, dy=-2,
                       effect=lambda c, t: (c.ring(16, 12, 7, light), c.ring(16, 12, 5, (255, 255, 255, 255), 150))),
                  draw(design, pose(), branch, style, pc)]
    elif style == "pulse":
        attack = [draw(design, pose(mood="squint", act="wind"), branch, style, pc, 1.05, 0.94,
                       effect=lambda c, t: c.ring(16, 20, 8, light, 140)),
                  draw(design, pose(mood="wide", act="fire"), branch, style, pc, 1.08, 1.04,
                       effect=lambda c, t: (c.ring(16, 20, 13, light), c.ring(16, 20, 15, light, 90))),
                  draw(design, pose(), branch, style, pc)]
    else:  # ranged and support: wind up, then fire from the head
        attack = [draw(design, pose(mood="squint", act="wind"), branch, style, pc, 1.1, 0.88),
                  draw(design, pose(mood="wide", act="fire"), branch, style, pc, 0.94, 1.07,
                       effect=lambda c, t: c.glow(t[0], max(3, t[1] - 3), 3.5, light)),
                  draw(design, pose(), branch, style, pc)]
    return idle, attack


def enemy_frames(design):
    move = []
    for phase in range(4):
        c = Canvas()
        design(c, {"phase": phase})
        c.finish()
        move.append(c.img)
    return move, death_frames(move[0])


def save_strip(frames, path, imported):
    if frames is None or str(path.relative_to(PROJECT)) in imported:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (SIZE * len(frames), SIZE), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.alpha_composite(frame, (i * SIZE, 0))
    sheet.save(path)
    return 1


def main(worlds):
    imported = set(IMPORTED.read_text().split()) if IMPORTED.exists() else set()
    all_content = {}
    for path in sorted((PROJECT / "tools" / "content").glob("*.json")):
        content = json.loads(path.read_text())
        all_content[content["biome"]["id"]] = content
    w1 = all_content["immune_system"]
    made = 0
    for world in worlds or WORLD_MODULES:
        module = importlib.import_module("sprites." + WORLD_MODULES[world])
        # Every world uses World 1's attack style for each pack slot.
        styles = {uid: style for uid, (_d, style) in importlib.import_module("sprites.world_immune").UNITS.items()}
        designs = getattr(module, "DESIGNS", None) or {uid: d for uid, (d, _s) in module.UNITS.items()}
        content = all_content[world]
        renames = content.get("renames", {})
        for pack in w1["packs"]:
            pc = hexc(pack["color"])
            for unit in pack["units"]:
                design, style = designs[unit["id"]], styles[unit["id"]]
                for branch, row in [(None, unit)] + list(enumerate(unit["evolutions"])):
                    merged = dict(unit, **row) if branch is not None else unit
                    can_attack = any(merged.get(k) for k in ("damage", "slow", "poison", "mark", "stun"))
                    uid = renames.get(row["id"], [row["id"]])[0]
                    idle, attack = unit_frames(design, style, branch, pc, can_attack,
                                               tiered=getattr(module, "TIERED", False))
                    out = ANIM / world / "units" / pack["id"]
                    made += save_strip(idle, out / f"{uid}_idle.png", imported)
                    made += save_strip(attack, out / f"{uid}_attack.png", imported)
        for invader in content["invaders"]:
            move, death = enemy_frames(module.ENEMIES[invader["id"]])
            out = ANIM / world / "invaders"
            made += save_strip(move, out / f"{invader['id']}_move.png", imported)
            made += save_strip(death, out / f"{invader['id']}_death.png", imported)
    print(made, "strips drawn.")


if __name__ == "__main__":
    main(sys.argv[1:])
