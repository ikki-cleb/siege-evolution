# Project: Siege Evolution (working title)

Godot 4 mobile game (iOS + Android), portrait, 16×16 pixel art. See `DESIGN.md`
for the full game design — keep it updated whenever a design decision changes.

## How to work with the user

- **When running as an Opus model:** ask many clarifying questions at almost
  every step of development (use AskUserQuestion, several rounds if useful)
  before implementing. Surface design choices, edge cases, and trade-offs
  rather than deciding silently.
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
- Placeholder art is fine; the user will draw final art. Keep sprites 16×16
  and name files predictably so they can be swapped 1:1.

## Handoff: where the project stands (keep this section up to date)

**Status (v0.8):** all 5 main worlds are built and balanced against the
auto-player (35 levels), with 5 packs, evolutions, saves, a test-mode store,
a polished pixel-font UI, sound effects, music, and a final victory screen.
`DESIGN.md` has every design decision; read it before changing gameplay.

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
- Balance for one world (about 10 minutes; run in the background): `... tests/sim_test.gd -- world=4` (0-based)
- Full suite, all worlds (about 50 minutes): `... tests/sim_test.gd`
- Replay one level with layouts and leaks: `... tests/debug_level.gd -- <world> <pack> <level> [seed]`
- Placeholder art and audio: `python3 tools/make_placeholder_art.py --only-missing`, `python3 tools/make_audio.py --only-missing`

**How content works.** Pack stats live once in `tools/content/immune_system.json`.
Every other world reuses them via `"packs_from"` + `"renames"`, so packs play
the same at every scale. Each world's JSON holds its invaders, wave rules,
tutorial (level 1) and level tables; levels 2-7 are generated from a threat
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
- Commit and push after every piece of work (a stop hook enforces it).

**Open questions for the user:** how the sounds and music feel; whether
the new look is right; Blinker frequency; whether difficulty feels right in
real play (the bot finds early levels easy).

**Next steps (user's call):** the two bonus worlds (Kitchen Defense, Birthday
Bash; they're sold in the store but not built yet, which should be fixed
before a real release); cosmetic unlocks; real billing (Apple StoreKit and
Google Play Billing plugins, see the TODOs in `scripts/store.gd`); native
iOS/Android builds and TestFlight / Play internal testing.
