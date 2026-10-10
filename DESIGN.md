# Siege Evolution: Game Design Document

Status: **v0.5, Worlds 1–3 playable** (21 levels, 5 packs, evolutions,
saved progress, store in test mode). Balance is tuned against an automated player, not real play yet.

## Pitch

A puzzle tower defense played in portrait on phones. Each level is a grid
where your units are the maze: walls and defenders shape the invaders' route
while they fight. There's no single solution. Many layouts work, and the best
ones aren't obvious going in. The scale grows as you progress: you start
inside the body, and each world's final boss zooms you out to a bigger world.

## Platform & tech

| Decision | Choice |
|---|---|
| Engine | Godot 4.7, GDScript |
| Platforms | iOS + Android (iOS builds need a Mac with Xcode). A web build is used for playtesting. |
| Orientation | Portrait only |
| Art | 16×16 pixel tiles, integer-scaled. Placeholders for now; the user draws the final art. |
| Menus | Plain and functional for now. The sleek design comes after the gameplay. |
| Business model | Free, no ads. Optional $1 purchases (see Monetization). |

## Structure

```
Title → World select → Pack select → Level select (7 levels) → Level (10 waves)
```

- **Worlds (biomes):** 7 levels each, at one scale. Beating level 7 (the boss)
  unlocks the next, larger-scale world. The five main worlds, in order:
  1. **Microscopic** (the immune system), built
  2. **Backyard Bugs** (defend the queen's anthill), built
  3. **Wild Kingdom** (human and animal scale: defend the farmhouse), built
  4. **Total War** (ships, tanks, bombs)
  5. **Galactic Siege** (planets, starships, alien invaders)
- **Bonus worlds** (bought separately, playable as soon as they're bought):
  **Kitchen Defense** and **Birthday Bash** (a kid's birthday party).
- **Each world has its own invader roster.** All behavior types appear in
  that world's level 1, and levels 2–7 add **elite variants** of them.
- **Starter pack:** picked when entering a world and kept for all 7 levels.
  Picking a different pack restarts that world at level 1 (after a confirm
  screen). Each pack plays the same way in every world; later worlds only
  give its units new names and art for the scale.
- **Progress** is saved locally (cleared levels and chosen pack per world).

### First level of every world (teaching level)

- Introduces every invader type in the world, about one idea per wave.
- Shows a tip in a footnote under the board before each wave (never a pop-up).
- Is the only level with the **path preview**, and a footnote says so.
- Gives extra ATP so players can try an evolution.

## Core loop

1. **Build phase:** see the next wave's contents. Place units, tap a placed
   unit to evolve or remove it.
2. **Wave phase:** invaders spawn and travel to the base. No building.
   Fast-forward is available (1×/2×/3×).
3. Survive **10 waves** to clear the level. **Pass/fail only**, no stars.
4. **Lose:** the base has 20 HP, and each invader does its own base damage
   when it arrives.

**Between waves:** all units (even destroyed ones) are **repaired for free**.
A wave where nothing reaches the base earns a small **clean-wave bonus**.

## Economy and refunds

- **ATP** is the currency: a starting amount, plus **drops from every kill**
  (shown as an orb flying to the ATP counter), plus the clean-wave bonus.
  ATP can only be spent between waves. Boss minions drop nothing.
- **Starting hand:** each level grants free units as an *ATP value per pack
  slot*, converted into copies of that pack's unit (24 ATP = three 8-ATP walls
  or eight 3-ATP walls), so every pack gets a fair hand. Hands are kept
  small (about half of v0.2) so drops matter.
- **Removing a unit:**
  - Placed (or evolved) **this build phase**: 100% refund. Free units go back
    to the hand.
  - Placed in an **earlier round**: 50% of its ATP cost (unit + evolution),
    including units that were free.
- No Undo button. Same-round removal does the same job.

## Grid & pathing

- Fixed grid of **9 × 14** tiles, with the whole level visible.
- Spawn points (1–3) and the base position vary per level.
- Walkers path with A*. **You can never fully seal the path.** Placements
  that would are refused.

## Units and packs

Every unit blocks its tile. Each pack has **6 units**: slots 0–2 at level 1,
then one new unit on **levels 2, 4 and 6**. Each unit **evolves once**, into
one of **two branches**, for ATP during a build phase, but only after it has
**survived a wave** (it can't evolve the round it's placed). Attackers usually get
a damage branch and a range branch; walls get an HP branch and a
reflect/utility branch. Evolutions are shown with a corner badge: red arrow
for power, blue ring for reach.

| Pack | Identity | Price |
|---|---|---|
| **Fortress** | Massive walls and slow, heavy hitters. Holds the line against smashers. | Free |
| **Swarm** | Cheap units that attack faster when packed together. | Free |
| **Precision** | Long range, big single hits, and marks that make targets take extra damage. | Free |
| **Control** | Slows, stuns and area damage. Deadly inside a long maze. | $1 |
| **Toxin** | Stacking poison that ignores armor and spreads when a victim dies. | $1 |

A bought pack unlocks in **every** world, including bonus worlds.

**Unit mechanics available:** single-target or pulse (hit everything in range),
splash, armor pierce, hits fliers or not, slow, stun (bosses resist 70%),
stacking poison (up to 3× a dose) with optional spreading, mark (+X% damage
taken), swarm adjacency bonus, wall regeneration (pauses 2s after being hit),
and reflect (bounces part of smasher damage back).

The full roster and stats live in `tools/content/immune_system.json`.

## How worlds reuse packs

Each pack plays exactly the same in every world: same stats, same unlock
order, same evolutions. A world only renames the units and gives them new art
(`"packs_from"` and `"renames"` in its JSON). In Backyard Bugs, walls are
garden objects (pebbles, twigs, acorn shells, spiderwebs, nettles) and
attackers are bugs (stag beetles, ants, spiders, stink bugs, wasps). In Wild
Kingdom, walls are farm materials (stone walls, hay bales, fences, mud,
brambles) and attackers are farm animals (bulls, hens, owls, skunks,
rattlesnakes).

## Invaders (World 1)

| Invader | Type | Notes |
|---|---|---|
| Rhinovirus | Walker | Fast, weak swarms |
| Flu Virus | Walker (elite, level 2+) | Much faster |
| Bacterium | Walker | Splits into 2 halves |
| Biofilm Colony | Walker (elite, level 3+) | Armor 2, splits |
| Parasite Worm | Smasher | Chews through any unit in its way |
| Hookworm | Smasher (elite, level 4+) | Regenerates |
| Spore | Flier | Flies straight over the maze |
| Fungal Spore | Flier (elite, level 5+) | Armor 1, tougher |
| **Superbug** | Boss smasher (level 7, wave 10) | Armor 1, releases Rhinoviruses as it walks |

Armor reduces each non-piercing hit (a hit always does at least 1). Poison ignores armor.

## Invaders (World 2: Backyard Bugs)

New behavior: **burrowers.** They walk a few tiles, tunnel under the next
stretch of their route (untargetable while underground), and resurface
further along. That rewards defense in depth over a single choke point.

| Invader | Type | Notes |
|---|---|---|
| Termite | Walker | Fast, weak swarms |
| Soldier Termite | Walker (elite, level 2+) | Faster, armor 1 |
| Aphid Cluster | Walker | Bursts into 3 aphids |
| Scale Colony | Walker (elite, level 3+) | Armor 2, bursts into aphids |
| Mole Cricket | **Burrower** | Walks 3 tiles, tunnels under the next 6 |
| Rhino Beetle | Smasher | Rams through units |
| Hercules Beetle | Smasher (elite, level 4+) | Armor 2 |
| Mosquito | Flier | |
| Hornet | Flier (elite, level 5+) | Armor 1, tougher |
| **Giant Centipede** | Boss smasher (level 7, wave 10) | Tunnels once, releases termites |

## Invaders (World 3: Wild Kingdom)

New behavior: **jumpers.** They plan their route as if they can hop over any
single unit tile (not rocks, not walls two tiles thick), pausing briefly
before each hop. On the tutorial level their route shows in orange. Burrowers
return from World 2. World 3 is noticeably harder: invaders are tougher for
the ATP they drop, though drops stay generous enough to keep building.

| Invader | Type | Notes |
|---|---|---|
| Rat | Walker | Fast swarms |
| Weasel | Walker (elite, level 2+) | Very fast, armor 1 |
| Deer | **Jumper** | Hops single unit tiles |
| Red Stag | Jumper (elite, level 3+) | Armor 1 |
| Coyote Pack | Walker | Scatters into 3 coyotes |
| Wolf Pack | Walker (elite, level 4+) | Armor 2, scatters into wolves |
| Wild Boar | Smasher | Charges through units |
| Moose | Smasher (elite, level 5+) | Armor 2 |
| Crow | Flier | |
| Hawk | Flier (elite, level 6+) | Armor 1 |
| Gopher | Burrower | Tunnels under 6 tiles |
| **Grizzly Bear** | Boss smasher (level 7, wave 10) | Armor 2, brings bear cubs |

## Monetization

Free app, **no ads**. Everything is in the **Store** (menu), and the paid
packs and bonus worlds can also be unlocked right where they appear.

| Item | Price |
|---|---|
| 3× speed (1× and 2× are free) | $1 |
| Control pack | $1 |
| Toxin pack | $1 |
| Kitchen Defense (bonus world) | $1 |
| Birthday Bash (bonus world) | $1 |
| **Everything bundle** (all five) | **$3** instead of $5 |

There's also a Restore Purchases button (Apple requires it). Prices shown
in-game are placeholders; the real localized prices come from the App
Store / Google Play.

**Implementation status:** `scripts/store.gd` handles ownership, the bundle,
and saving. Web and debug builds run in **test mode** (purchases are free and
instant). Phone release builds still need the Apple StoreKit and Google Play
Billing plugins connected (marked TODO), and the matching product ids set up
in App Store Connect and Google Play Console.

## Level generation

Each world's levels, wave rules and tutorial live in its JSON file
(`tools/content/<world>.json`). Level 1 is handwritten. Levels 2–7 are
generated from a threat budget that grows 32% per wave and a fixed category
mix per wave (swarm / split / smash / fly, plus burrow in World 2), with a
growing share of elites once they're introduced. The output is regular .tres
files that can be edited by hand.

## Balancing method

`tests/sim_test.gd` runs an automated player (`tests/auto_player.gd`) through
every level of every world with every pack (two seeds each) and prints base
HP left. `tests/debug_level.gd` replays one level and prints the layout and
leaks wave by wave. As of v0.4 the auto-player wins most levels comfortably,
so difficulty should be judged by human playtesting next. Current
targets: every pack beats at least 6 of 7 levels, levels with no defenses
are lost, and the packs' averages stay close together. Human playtesting
comes next.

## Open questions

- World 2 theme and scale (e.g. backyard bugs?), and how packs reskin there
- Cosmetic unlocks (palettes, skins, menu themes): what and when
- Content for worlds 4–5 and the two bonus worlds
- Orchard (World 3, level 3) is the hardest level for the bot, especially with Toxin
- Overall difficulty after human playtesting (the bot finds most levels easy)
- Sound and music direction
- Sleek menu visual design
- Save sync (iCloud / Google Play) or local only
