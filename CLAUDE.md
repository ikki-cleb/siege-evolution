# Project: Siege Evolution (working title)

Godot 4 mobile game (iOS + Android), portrait, 16×16 pixel art. See `DESIGN.md`
for the full game design — keep it updated whenever a design decision changes.

## How to work with the user

- **When running as an Opus model:** ask many clarifying questions at almost
  every step of development, **always as AskUserQuestion prompts (multiple
  choice / checkboxes), never as plain-text question lists**, and do it very
  frequently (several rounds per feature is good) before implementing.
  Surface design choices, edge cases, and trade-offs rather than deciding
  silently.
- **When running as any other model (Sonnet, Haiku, etc.):** assume the user
  wants a minor tweak. Just make the change; only ask a question if it is
  genuinely blocking.
- The user is **new to coding**. Keep code simple and well-commented, prefer
  readable GDScript over clever patterns, and briefly explain what changed and
  why after each task.

## Conventions

- Engine: Godot 4.7, GDScript (not C#).
- Data-driven content: units, invaders, and levels defined as Resources /
  data files, not hardcoded in scripts, so new content needs no code changes.
- Art: animated sprites are code-drawn 32x32 strips (see Environment); the
  user may swap any of them for generated art. Name files predictably so
  they can be swapped 1:1. Still 16x16 sprites remain as fallbacks.

## Handoff: where the project stands (keep this section up to date)

**Status (v1.0 content-complete):** all 5 main worlds plus both bonus
worlds are built: **Kitchen Defense** (spillers, Rat King) and **Birthday
Bash** (piñatas with seeded "surprise" contents, the Clown). 35 levels
(5 per world, 8 waves each),
5 packs, evolutions, saves, a test-mode store, the "Siege Pixel" font
(clear digits + coin icon), coins as currency, a Cancel button, sound,
music and victory screens. **Capstones** (a second evolution tier, 2 per
tier-1 evolution, 120 total, 12 new mechanics, themed names in every world)
plus a two-tap upgrade preview and drag-to-scroll menus. **Packs swap
freely** (shared world progress; each pack remembers levels it beat) and
there are **27 achievements** (`data/achievements.json`,
`scripts/achievements.gd`, Achievements screen + unlock banner).
**Art:** every unit and enemy has code-drawn animated sprites (idle/attack,
move/death) in all 7 worlds; only living things have faces. Levels can take
painted backgrounds (game support done, none delivered yet).
`DESIGN.md` has every design decision; read it before changing gameplay.

**World order (v1.1):** Backyard Bugs, Wild Kingdom, Microscopic, Total
War, Galactic Siege (Microscopic moved from 1st to 3rd; the user found its
body-tissue art unsettling for a first world). Saves are keyed by world id.
`Progress.WORLDS` sets the order; tests use `load_biome(2)` for Microscopic
(where pack stats live). Backyard's tutorial has the beginner tips.
Difficulty was retuned to rise in order: Backyard got Microscopic's old
budgets (14/22/28/32) and a 450 HP Giant Centipede; Microscopic got
17/28/28/36 and a 600 HP Superbug (Precision limits how high L4-5 can go).

**Art handoff state.** The user is making the 35 level backgrounds in
ChatGPT from drag-and-drop prompt files in `docs/art/chatgpt/` (one per
world; filenames like `kitchen_defense_level_03.png`). When they send the
images: `tools/import_backgrounds.py <folder>` (it also softens them: 30%
less color, less contrast, a bit brighter, as the user chose), then import +
content build, then republish. **Imported so far: Microscopic, Backyard Bugs, Kitchen Defense, Birthday Bash (all 5 each).**
Images pasted mid-turn in chat don't get saved as files; ask the user to
attach them in their own message. The user's batches arrive in reverse
level order (oak roots = Backyard 5, pine forest = Wild Kingdom 5, toy road
playmat = Total War 5); check each scene against the prompt file. Follow-up once backgrounds exist: obstacle/spawn/base tiles
have their old floor color baked in and will show as squares on top of the
art; redraw them with transparency. Two Claude Docs briefs exist for
reference: backgrounds https://claude.ai/artifact/Dk8EnbQN1PGpeuyhSoS4xK and
sprites https://claude.ai/artifact/VnjA9ALpqnN1UNRHhVscKi (the sprite one
describes 64x64 AI art; the user chose code-drawn 32x32 instead, with
`docs/art/units.csv` / `enemies.csv` as full lists if they upgrade some).

**Playtest links.** The private Claude artifact for this game is
https://claude.ai/artifact/DA13mBPrv71jQU9WuZJDUC. Republish to that same URL
(Artifact tool with `url`) after `tools/export_web.sh`. The user also
playtests on itch.io: build with `tools/export_itch.sh godot`, copy
`build/siege-evolution-web.zip` into `playtest/` (gitignored) and send it to
them; they upload it themselves.

**Environment.** `.claude/hooks/session-start.sh` installs Godot 4.7.2 as
`godot` plus the web export templates in cloud sessions. Commands:
- Rebuild content after editing `tools/content/*.json`: `godot --headless --script tools/build_content.gd`
- Rules tests (about 1 minute): `godot --headless --fixed-fps 60 --script tests/sim_test.gd -- rules`
- Balance for one world (about 10 minutes; run in the background): `... tests/sim_test.gd -- world=4` (0-based; 5 = Kitchen, 6 = Birthday)
- After adding new PNGs, run `godot --headless --import` before the content build, or it can't load them
- Full suite, all worlds (about 50 minutes): `... tests/sim_test.gd`
- Replay one level with layouts and leaks: `... tests/debug_level.gd -- <world> <pack> <level> [seed]`
- Placeholder art and audio: `python3 tools/make_placeholder_art.py --only-missing`, `python3 tools/make_audio.py --only-missing`
- Game font (Pixelify Sans + clearer digits + coin icon U+E000): `pip install fonttools && python3 tools/make_font.py`
- Code-drawn sprites (32x32 frames, the current art): `python3 tools/draw_sprites.py [world]`; designs for all 7 worlds live in `tools/sprites/world_<name>.py` (shared parts in `parts.py`, drawing kit in `kit.py`); `tools/preview_sprites.py <world> <out.png>` makes a contact sheet. It skips anything listed in `art/anim/imported.txt`.
- Animated sprites (the user generates them): `python3 tools/import_sprites.py <folder>` (files named `<world>_<id>_<anim>.png` strips or `_<anim>_<n>.png` frames), then import + content build. Placeholder strips: `python3 tools/make_placeholder_anims.py` (never overwrites).
- Painted level backgrounds (the user generates them): `python3 tools/import_backgrounds.py <folder>` (files named `<world_id>_level_NN.png`), then `godot --headless --import` and the content build. Levels without one keep their floor tiles.

**How content works.** Pack stats live once in `tools/content/immune_system.json`.
Every other world reuses them via `"packs_from"` + `"renames"`, so packs play
the same at every scale. Each world's JSON holds its invaders, wave rules,
tutorial (level 1) and level tables; levels 2-5 are generated from a threat
budget. `tools/tune.py <id> key=value` edits stats.

**Gotchas learned the hard way:**
- Keep `editor/export/convert_text_resources_to_binary=false` in project.godot,
  or exported builds lose level layouts.
- Scripts with `class_name` (Board, Unit, Invader, Hud...) must not use
  autoload names (Audio, Look, Progress, Store) directly. Tests compile them
  before autoloads exist. Use `Sfx.play()`, `Palette.*`, or `get_node("/root/...")`.
- The Claude artifact host only serves common file types, so `export_web.sh`
  ships the wasm/pck as base64 `.txt` and `web/shell.html` decodes them.
  The itch build is a normal web export.
- Balance: keep invader stats comparable across worlds (packs restart at base
  stats each world); make worlds harder with mechanics, layouts and wave mixes.
  Water lanes along map edges can't be defended, so run rivers through the land.
- Placing a unit changes the route (units block), so the auto-player judges
  placements by the route after placing. It's a decent but imperfect player.
- `Progress.load_biome()` loads a whole world (every unit, sprite, level) and is
  slow, especially on the web. Code that only needs a world's id uses
  `Progress.world_id(index)`; a win used to freeze ~10s from repeated loads.
- Commit and push after every piece of work (a stop hook enforces it).

**Open questions for the user:** how the code-drawn sprites feel in play
(any designs to redraw); how capstones feel (prices, strongest mechanics);
how the bonus worlds feel (bot wins 90% of Kitchen and 70% of Birthday
levels 2-5; Fortress and Precision struggle most); sounds and music;
Blinker frequency; whether bosses feel fair now that they're an instant
loss (the user chose to playtest before tuning further: Swarm vs the
Mothership, and the Rat King level, where Kitchen fell from 90% to 80%).

**Bosses (latest playtest round):** a boss reaching the base is an
instant loss (minions do normal damage); the boss spawn tile has a purple
glow + skull all level (`scripts/game/boss_marker.gd`); the boss route is a
thick purple line before the boss wave (even with Paths off); bombs fall
for 0.9s with a red warning before they explode (`Board.drop_bomb`).

**Recent fixes worth knowing:** a ~10s freeze after winning a level (slow
world loading in achievement checks) is fixed and guarded by a test; the
loading screen no longer says "World 1". Web build: `index.pck.b64.txt` must
stay under the artifact's 16 MB-per-file limit. It was 8.2 MB with no
backgrounds. Backgrounds are 864x1344 and the importer writes a `.import`
with lossy compression at quality 0.4 (Godot's lossless default made 5
backgrounds cost 14 MB). Each one adds ~0.2 MB to the b64 file, so all 35
should land near 15 MB: if it goes over, lower `compress/lossy_quality`
in the .import files or the WIDTH/HEIGHT in `tools/import_backgrounds.py`.

**Latest balance (5 levels x 8 waves, bot wins on levels 2-5), after
bosses became an instant loss:** World 1 95%, World 2 95%, World 3 88%,
World 4 88%, World 5 75%, Kitchen 80%, Birthday 70%. Every check passes.
After the reorder: Backyard 100%, Wild Kingdom 90%, Microscopic 95% (the
bot can't separate W2/W3 finely; Precision is the binding pack).
The Mothership went 1100 -> 550 HP and the bot now covers a flying boss's
marked flight line; Swarm (weakest anti-air) still loses that level in the
bot runs. Comet Tail losses predate the boss change. Path preview now shows on every level
(saved "Paths" toggle in the HUD).

**Next steps (user's call):** import the user's backgrounds when they
arrive (and make obstacle tiles transparent); playtest feedback (sprites,
capstones, bonus worlds); cosmetic unlocks; real billing (Apple StoreKit and
Google Play Billing plugins, see the TODOs in `scripts/store.gd`); native
iOS/Android builds and TestFlight / Play internal testing.
