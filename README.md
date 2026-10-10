# Siege Evolution

A portrait puzzle tower defense for iOS and Android, made with Godot 4.7.
See `DESIGN.md` for the game design.

## Project layout

| Folder | What's in it |
|---|---|
| `scenes/` | `menu.tscn` (starts the game) and `game.tscn` (plays one level) |
| `scripts/game/` | Gameplay: `game.gd` (rules, waves, ATP, refunds, evolving), `board.gd` (grid and pathfinding), `unit.gd`, `invader.gd` |
| `scripts/ui/` | `menu.gd` (world/pack/level select) and `hud.gd` (in-level buttons and labels) |
| `scripts/progress.gd` | Saved progress and menu choices (available everywhere as `Progress`) |
| `scripts/data/` | Definitions of what a unit, invader, pack, wave, level and biome contain |
| `data/` | The actual content (`.tres` files you can edit in Godot's Inspector) |
| `art/` | 16×16 sprites. Replace any PNG with your own art of the same name. |
| `tests/` | Automated playtest and the auto-player used for balancing |
| `tools/` | Content source (`tools/content/*.json`) and helper scripts |

## Common tasks

- **Play it:** open the folder in Godot 4.7 and press F5.
- **Rebalance:** change a stat in `tools/content/immune_system.json` (pack stats
  live there and are shared by every world) or a world's own file (or use
  `python3 tools/tune.py unit_id damage=5`), then rebuild the content:
  `godot --headless --script tools/build_content.gd`
- **Edit a level:** each world's layouts, starting hands, waves and tutorial tips
  are in its file in `tools/content/` (`.` floor, `#` blocked, `S` spawn,
  `B` base). Rebuild the content afterwards.
- **Investigate one level:**
  `godot --headless --fixed-fps 60 --script tests/debug_level.gd -- 1 swarm 2`
  (world index, pack, level number)
- **Try later worlds:** in a test build, Store → "Test: unlock all worlds".
- **Sounds and music:** `python3 tools/make_audio.py --only-missing` regenerates
  placeholders without touching files you've replaced in `assets/`.
- **New art:** `python3 tools/make_placeholder_art.py --only-missing` draws
  placeholders only for sprites that don't exist yet.
- **Run the automated playtest** (rules checks plus a balance table for every pack):
  `godot --headless --fixed-fps 60 --script tests/sim_test.gd`
  Add `-- rules` to skip the slower balance run.
- **Build for the web:** `tools/export_web.sh path/to/godot`
- **Build for itch.io:** `tools/export_itch.sh path/to/godot`, then upload
  `build/siege-evolution-web.zip` as an HTML game played in the browser.
