# Siege Evolution

A portrait puzzle tower defense for iOS and Android, made with Godot 4.7.
See `DESIGN.md` for the game design.

## Project layout

| Folder | What's in it |
|---|---|
| `scenes/` | `main.tscn`, the scene that runs a level |
| `scripts/game/` | Gameplay: `game.gd` (rules, waves, ATP), `board.gd` (grid and pathfinding), `unit.gd`, `invader.gd` |
| `scripts/ui/` | `hud.gd`, the on-screen buttons and labels |
| `scripts/data/` | Definitions of what a unit, invader, wave and level contain |
| `data/` | The actual units, invaders and levels (`.tres` files you can edit in Godot's Inspector) |
| `art/` | 16×16 sprites. Replace any PNG with your own art of the same name. |
| `tests/` | Automated playtest |
| `tools/` | Helper scripts (placeholder art, initial content, web export) |

## Common tasks

- **Play it:** open the folder in Godot 4.7 and press F5.
- **Rebalance:** open a file in `data/units/` or `data/invaders/` and change the numbers.
- **Edit a level:** open `data/levels/level_01.tres`. `layout` is the map
  (`.` floor, `#` wall tissue, `S` spawn, `B` base), and `waves` holds the 10 waves.
- **Run the automated playtest:**
  `godot --headless --fixed-fps 60 --script tests/sim_test.gd`
- **Build for the web:** `tools/export_web.sh path/to/godot`
