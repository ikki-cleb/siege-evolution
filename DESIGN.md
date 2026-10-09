# Game Design Document

Status: **pre-production, v0.1**. Items marked _(proposed)_ are Claude's
suggestions awaiting the user's approval.

## Pitch

A puzzle tower defense played in portrait on phones. Each level is a hand-built
puzzle on a fixed grid: place walls and defenders so that invaders have to path
around or smash through them before they reach your base. Levels last 10 waves.
The scale grows as you progress: you start inside the body, and after you beat
each biome's final boss the game zooms out to a bigger world with new towers.

## Platform & tech

| Decision | Choice |
|---|---|
| Engine | Godot 4, GDScript |
| Platforms | iOS + Android (iOS builds require a Mac with Xcode) |
| Orientation | Portrait only |
| Art | 16×16 pixel tiles, integer-scaled; placeholders now, user draws final art |
| Menus | Sleek, clean, modern UI (contrasts with the pixel battlefield) |
| Business model | Paid up front, no ads or IAP |

## Core loop

1. **Build phase:** see the next wave's preview and the predicted invader path.
   Place, move, or remove units, with undo available.
2. **Wave phase:** invaders spawn and travel to the base. You can't build while a
   wave runs. Fast-forward is available (1×/2×/3×).
3. Repeat for **10 waves**. Survive wave 10 to clear the level.
4. **Lose condition:** the base has HP, and each invader that reaches it does damage.
   Tougher invaders do more damage. The level fails at 0 HP.

## Grid & pathing

- Fixed grid of about **9 columns × 14 rows**, with the whole level visible and no scrolling.
- Invaders path toward the base with grid pathfinding (A*), recalculated when
  the layout changes.
- **The player may never fully seal the path.** Placement is rejected if it
  would leave no route. _(proposed: standard mazing-TD rule)_
- Level designers can pre-place rocks or terrain to shape each puzzle.

## Units (the player's side)

Two roles. **Both occupy and block their tile.**

- **Walls:** cheap blockers whose job is to shape the path. Some have HP so
  smashers can break them.
- **Attackers:** deal damage to invaders. They still block their tile.

**Economy (hand + small income):** each level gives a fixed starting hand of
units, plus a small currency earned between waves to buy extras from that
level's allowed list.

### Starter roster, World 1 (Immune System) _(proposed)_

| Unit | Role | Idea |
|---|---|---|
| Cell Membrane | Wall | Basic cheap blocker |
| Platelet Clot | Wall | Tough, high-HP wall for holding back smashers |
| Neutrophil | Attacker | Short-range, fast hits |
| B-Cell | Attacker | Long-range antibody shots |
| Macrophage | Attacker | Slow, engulfs (instantly kills) small invaders |
| Fever Node | Attacker | Area damage-over-time aura |

## Invaders

Behavior depends on invader type:

- **Pathers:** route around all blockers (most invaders).
- **Smashers:** walk straight toward the base and attack blocking units
  until they break.
- **Fliers:** ignore blockers entirely, so you need attackers with range coverage.

### Starter roster, World 1 _(proposed)_

| Invader | Type | Idea |
|---|---|---|
| Rhinovirus | Pather | Weak, comes in swarms |
| Bacterium | Pather | Medium HP, splits into 2 on death |
| Parasite Worm | Smasher | Chews through walls |
| Spore | Flier | Drifts over the maze |
| **Boss: Superbug** | Smasher | World 1 final boss, resists one attack type |

## Progression

- **Worlds / biomes** scale up in size as you go: Immune System → (proposed)
  Backyard Bugs → Pond / Forest → … Beating a biome's final boss "zooms out"
  to the next biome with new themed towers and invaders.
- **Unlocks from completing levels:** new levels and worlds, new unit types, cosmetics
  (palettes, unit skins, menu themes).
- No permanent stat upgrades, to keep puzzles fair and designed. _(user did not select this)_

## Quality of life (in prototype)

- Fast-forward (2×/3×)
- Path preview during build phase
- Undo during build phase
- Next-wave preview

## Prototype scope

- **About 5 levels** in World 1 (Immune System), ending with a boss level.
- Goal: prove the core puzzle is fun before expanding.

## Open questions

- Game title / working name
- Final unit and invader roster and stats
- Do units get destroyed permanently by smashers, or repaired between waves?
- Star rating or scoring per level?
- Can units be sold or refunded, and for how much?
- Save system details (local only, iCloud/Google Play sync?)
- Sound and music direction
