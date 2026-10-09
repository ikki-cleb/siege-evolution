# Siege Evolution — Game Design Document

Status: **prototype v0.1 playable** (2 levels, 4 units, 4 invaders). Items marked _(proposed)_ are Claude's
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
5. **Pass/fail only:** no star ratings or scores. Clearing wave 10 = level passed.

**Between waves:**
- All damaged units are **repaired to full automatically, for free**, and units
  that smashers destroyed are restored too.
- Units can be **sold for 75% of their cost in ATP** (build phase only), even
  units that came free from the starting hand. _(Claude's call; confirm)_
- Undo reverses placements and sales during the current build phase.

**Currency:** ATP (the cell's energy molecule). You get a starting amount, plus
a fixed amount after each cleared wave. There are no per-kill rewards.

**Controls:** tap a unit in the bottom bar, then tap tiles to place it. Tap
a placed unit to see its info and range, and to sell it.

**Targeting:** attackers always shoot the invader in range that is closest to
the base.

## Grid & pathing

- Fixed grid of **9 columns × 14 rows**, with the whole level visible and no scrolling.
- Spawn points (one or more) and the base position vary per level.
- Invaders path toward the base with grid pathfinding (A*), recalculated when
  the layout changes.
- **The player may never fully seal the path.** Placement is rejected if it
  would leave no route.
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
- **Smashers:** take the shortest route that only avoids terrain, and chew
  through **any** unit (wall or attacker) in the way.
- **Fliers:** fly straight to the base, ignoring blockers. Only some
  attackers (e.g. the B-Cell) can hit them.
- **Base:** 20 HP by default (set per level). Each invader does its own
  base damage when it arrives.

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

## Prototype stats (v0.1)

Tuned with the automated playtest (`tests/sim_test.gd`), not real play yet.
The current values live in the .tres files in `data/`.

| Unit | Role | Cost | HP | Damage | Range | Rate | Air |
|---|---|---|---|---|---|---|---|
| Membrane | Wall | 4 | 20 | – | – | – | – |
| Platelet Clot | Wall | 10 | 90 | – | – | – | – |
| Neutrophil | Attacker | 12 | 30 | 3 | 1.5 | 0.5s | No |
| B-Cell | Attacker | 16 | 15 | 4 | 3.0 | 1.0s | Yes |

| Invader | Type | HP | Speed | Base dmg | Notes |
|---|---|---|---|---|---|
| Rhinovirus | Pather | 6 | 1.6 | 1 | Swarms |
| Bacterium | Pather | 14 | 1.0 | 2 | Splits into 2 halves (5 HP, 1.2 speed) |
| Parasite Worm | Smasher | 40 | 0.7 | 3 | Chews units at 6 HP/s |
| Spore | Flier | 8 | 1.0 | 1 | |

Not built yet: Macrophage, Fever Node, Superbug boss.

## Prototype scope

- **About 5 levels** in World 1 (Immune System), ending with a boss level.
- Goal: prove the core puzzle is fun before expanding.

## Open questions

- Final unit and invader roster and stats
- Save system details (local only, iCloud/Google Play sync?)
- Sound and music direction
