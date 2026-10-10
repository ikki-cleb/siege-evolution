# Siege Evolution: Game Design Document

Status: **v0.9, all 5 main worlds plus the Kitchen Defense bonus world** (42 levels,
5 packs, evolutions, saved progress, sound, music, store in test mode). Balance is tuned against an automated player, not real play yet.

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
| Menus | Clean dark style with the "Siege Pixel" font (Pixelify Sans, SIL OFL, with redrawn digits because its 2 looked like an 8, plus the coin icon; built by `tools/make_font.py`) and an accent color per world (`scripts/look.gd`, `scripts/palette.gd`). |
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
  4. **Total War** (a toy war across the playroom and the bathtub), built
  5. **Galactic Siege** (moon, space station and asteroid levels), built
- **Bonus worlds** (bought separately, playable as soon as they're bought):
  **Kitchen Defense** and **Birthday Bash** (a kid's birthday party).
  They are **post-game**: harder than World 5, through mechanics, tighter
  layouts, nastier wave mixes and less starting coins (invader stats stay
  comparable to the main worlds). The store card warns about this before
  purchase. Each bonus world adds its own new invader type.
  - **Kitchen Defense**: built (see its section below).
  - **Birthday Bash**: built (see its section below).
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
- Gives extra coins so players can try an evolution.

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

## Capstones (second evolution tier)

After its first evolution, a unit can evolve **once more** into one of **two
capstones** (4 per unit, 120 in all). Capstones are powerful but
expensive: about **2× (unit cost + tier-1 cost)**, so players choose between
more units and one strong unit. Like tier 1, a unit must **survive a wave
after its first evolution** before it can take a capstone. Refunds follow
the usual rules (100% the round bought, 50% after). Capstones show a **gold
star badge** and a soft gold glow. The auto-player buys them when it has
spare coins.

Each capstone keeps its tier-1 stats and adds a **new mechanic**:

| Mechanic | What it does |
|---|---|
| Chain hit | Each hit jumps to 2-3 more invaders nearby (70% damage per jump) |
| Line pierce | Shots hit every invader in a line through the target |
| Multishot | Attacks 2-3 targets at once |
| Execute | Instantly finishes any non-boss below 15-35% HP |
| Knockback | Shoves ground invaders 1-2 tiles back along their route (bosses immune; 2s cooldown per invader) |
| Armor shred | Each hit permanently removes armor from the target (down to 0) |
| Bounty | Invaders it kills drop extra coins |
| Lingering zone | Leaves a burning, freezing or toxic patch for 3s |
| Grab | A smasher biting this wall is stunned (every 3s at most) |
| Explode on break | When destroyed, blasts invaders around it |
| Rebuild once | Comes back at full HP once per wave after being destroyed |
| Aura | The 8 neighbors attack faster, take less damage, or shrug off spill goo |

**Names:** every world names its capstones by adding a themed word for the
capstone's mechanic to that world's tier-1 name, so families stay obvious.
For example, Kitchen's "Stacked Cans" becomes "Self-Stacking Stacked Cans"
(rebuild) or "Sticky Stacked Cans" (grab); Total War's "Reinforced Sandbags"
becomes "Field-Repaired..." or "Barbed...". Names live in each world's
"renames" and can be edited freely.

## Economy and refunds

- **Coins** are the in-game currency (earned only by playing, never sold;
  formerly "coins"). Shown as a small gold coin icon next to the number, with
  no word. The icon is a character in the game font (`Palette.COIN`, drawn in
  `tools/make_font.py`), so it can sit inside any text. Coins come from a
  starting amount, plus **drops from every kill** (shown as an orb flying to
  the coin counter), plus the clean-wave bonus. Coins can only be spent
  between waves. Boss minions drop nothing.
- **Starting hand:** each level grants free units as an *coin value per pack
  slot*, converted into copies of that pack's unit (24 coins = three 8-coin walls
  or eight 3-coin walls), so every pack gets a fair hand. Hands are kept
  small (about half of v0.2) so drops matter.
- **Removing a unit:**
  - Placed (or evolved) **this build phase**: 100% refund. Free units go back
    to the hand.
  - Placed in an **earlier round**: 50% of its coins cost (unit + evolution),
    including units that were free.
- No Undo button. Same-round removal does the same job.

## Controls

- Tap a unit in the bar, then tap tiles to place it. Tap a placed unit to
  evolve or remove it.
- While a unit type or a placed unit is selected, a **Cancel** button
  appears next to Start Wave; tapping it (or the same unit again) deselects.
- **Upgrades take two taps.** The first tap previews an option: its
  description in the message line, before → after numbers and new mechanics
  in the footnote, its new range as a gold circle on the board, and the
  button changes to "Tap again to buy". The second tap buys it. Selecting
  anything else cancels the preview. Too-expensive options can still be
  previewed.
- **Menus scroll by dragging anywhere** (cards and buttons pass drags
  through). A press that moves more than 10 pixels is a scroll, not a tap.

## Grid & pathing

- Fixed grid of **9 × 14** tiles, with the whole level visible.
- Spawn points (1–3) and the base position vary per level.
- Walkers path with A*. **You can never fully seal the path.** Placements
  that would are refused.

## Units and packs

Every unit blocks its tile. Each pack has **6 units**: slots 0–2 at level 1,
then one new unit on **levels 2, 4 and 6**. Each unit **evolves once**, into
one of **two branches**, for coins during a build phase, but only after it has
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

## World 1 unit names

World 1 (Microscopic) uses plain body words, not biology terms, so the
theme reads instantly: Scab, Germ Eater, Scout Cell, White Blood Cell,
Skin Cell, Killer Cell, Antibody Shooter, Germ Tagger, Mucus Wall,
Sneeze Blaster, Fever Spot, Poison Cell, Acid Puddle, Rot Patch, and so on.
Capstones add a plain mechanic word ("Regrowing Thick Scab", "Chain Strong
Scout Cell"). File names and ids keep the original biology ids (e.g.
`macrophage.png` is the Germ Eater), so nothing else had to change.

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
the coins they drop, though drops stay generous enough to keep building.

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

## World 4: Total War (toy soldiers)

Tone is a lighthearted **toy war**: plastic army men, toy tanks, paper planes
and bath-toy boats. You defend a toy fort HQ. Walls are toy fortifications
(sandbags, barbed wire, concrete barriers, barricades, barrels), attackers
are toy troops and turrets.

**Sea levels (2, 4, 6) have water lanes.** Water tiles (`~`) carry boats only,
starting from sea spawns (`N`). Land invaders can't cross water. Only each
pack's **basic wall** can be placed on water, where it becomes a **net** (the
base wall and its HP evolution) or a **naval mine** (its reflect evolution).
Nets push boats into another lane but can never seal one. Landing troops
still march the land, so sea levels are two puzzles at once. Lanes run
through the land so units on both banks can cover them; lanes along the map
edges proved nearly impossible to defend.

**New behavior: bombers.** After about 30% of their flight they drop one bomb
on the most valuable unit within 2.5 tiles (unit plus evolution cost): full
damage to it, half to the 8 tiles around it. Destroyed units come back after
the wave as usual.

| Invader | Type | Notes |
|---|---|---|
| Toy Soldier / Toy Ranger (elite) | Walker | Swarms |
| Troop Truck / Armored Carrier (elite) | Walker | Unloads 3 recruits |
| Stunt Bike | Jumper | |
| Toy Tank / Heavy Tank (elite) | Smasher | |
| Paper Plane / Toy Jet (elite) | Flier | |
| **Toy Bomber** / Heavy Bomber (elite) | **Bomber** (flier) | 35 / 60 bomb damage |
| Patrol Boat / Destroyer (elite) | Boat | Water lanes |
| Submarine | Boat burrower | Dives under 6 tiles |
| Battleship | Boat smasher | Rams nets and mines |
| **Mega Tank** | Boss smasher (level 7) | Deploys toy soldiers |

**Balance lesson:** invader stats should stay comparable across worlds,
because packs restart at base stats in every world. Difficulty should come
from mechanics, layouts and wave mixes, not raw HP inflation.

## World 5: Galactic Siege (final main world)

Levels alternate settings with their own tiles: **moon surface** (levels 1,
4, 7), **station interior** (2, 5) and **asteroid field** (3, 6). Any level
can set its own tiles in its world's JSON (`"tiles": "station"`). You defend
the colony reactor. Walls are tech barriers (hull plates, scrap, energy
barriers, force fields, radioactive plates); attackers are robots and
turrets (mechs, bots, drones, laser and ion cannons, EMP towers).

**New behavior: teleporters ("blinkers").** Every few seconds they blink 3
tiles forward along their route (never straight onto the base), so one kill
zone isn't enough and you need coverage along the whole route. World 5 also
brings back burrowers (Tunnelers), jumpers (Hoppers) and bombers (UFO
Bombers): it's the "everything you've learned" world.

**Finale: the Mothership**, a flying boss that drifts slowly toward the
reactor, bombs your most valuable unit every few seconds, and drops blinkers
(which walk a real route from where they land). Only anti-air units can
hit it, and every pack has at least one.

| Invader | Type |
|---|---|
| Alien Grub / Alien Drone (elite) | Walker |
| Brood Pod / Hive Pod (elite) | Walker, bursts into spawnlings |
| **Blinker** / Phase Stalker (elite) | **Teleporter** |
| Hopper | Jumper |
| Tunneler | Burrower |
| Crusher Mech / Assault Mech (elite) | Smasher |
| Saucer / Interceptor (elite) | Flier |
| UFO Bomber | Bomber |
| **Mothership** | Flying boss: repeated bombs, drops blinkers |

## Bonus World: Kitchen Defense (post-game, built)

Pantry-pest scale: ants, cockroaches, mice and flies raid the kitchen; you
defend the **cookie jar**. Levels rotate three areas with their own tiles and
obstacles: **pantry shelves**, **counter top** and **kitchen floor** (jars,
cans, chair legs). Walls are kitchen objects (sugar cubes, sponges, tin cans,
cheese graters, cling wrap); attackers are kitchen tools and traps (fly
swatters, spray bottles, mousetraps, pepper grinders, toasters).

**Post-game difficulty:** the store card carries a red "POST-GAME: HARD"
tag and "Harder than Galactic Siege. Best after finishing the main game."
Difficulty comes from mechanics, tighter layouts, nastier wave mixes and less
starting coins, not inflated invader stats. Waves also grow faster (45% of
wave 1 per wave, vs 32% in main worlds), so early waves are fair and the
finish is brutal. Target was about 70% bot wins; tuning stopped at **85% on
levels 2-7** (level 1 is the easy teaching level) because more global
difficulty only broke Fortress and Precision while Swarm, Control and Toxin
kept winning. Final call is the user's playtest. Every pack beats at least
5 of 7 levels.

**New behavior: spillers.** Every 2 tiles it walks, a spiller splashes goo
on the units on the 8 tiles around it. A sticky unit attacks 40% slower
(60% of its normal attack speed) until the free repair after the wave; goo
doesn't stack. Long mazes lined with attackers get gummed up, so players
must choose where to fight. The counter: ranged attackers two tiles back
from the route stay clean, and walls don't care. Sticky units show goo
drips (`spill_every` / `spill_slow` in the world JSON).

Returning behaviors: walker swarms, splitters, smashers and fliers.

| Invader | Type |
|---|---|
| Sugar Ant / Fire Ant (elite) | Walker swarm |
| Slug | **Spiller**: slow, tanky, long slime trail |
| Honey Ant | Spiller (elite): faster, sticky |
| Mouse Nest / Rat Nest (elite) | Walker, bursts into mice |
| Cockroach / Giant Roach (elite) | Smasher |
| Fruit Fly / Housefly (elite) | Flier |
| **Rat King** | Boss smasher (level 7): sheds rats, leaves a grease trail |

Levels: 1 Pantry Raid, 2 Counter Top, 3 Under the Table, 4 Top Shelf,
5 Sink Side, 6 Crumb Trail, 7 Rat King's Feast. Pantry tiles are the
default; levels set `"tiles": "counter"` or `"floor"`.

Beating the Rat King shows a **world-cleared screen** (confetti,
"Kitchen Defense cleared!", and a nudge toward Birthday Bash if not owned).

## Bonus World: Birthday Bash (post-game)

Toy scale: **party crashers** invade a kid's birthday party: wind-up toys,
bouncy balls, balloons, party bags, spilled soda and piñatas. You defend the
**birthday cake**. Levels rotate the **backyard** (lawn and party table),
the **living room** (carpet and furniture) and the **bouncy castle**. Walls
are party gear (gift boxes, paper cups, folding chairs, balloon arches,
streamers); attackers are party gadgets (confetti cannons, water pistols,
noisemakers, sparklers, party horns, disco balls).

Same post-game rules as Kitchen Defense: the store card's
"POST-GAME: HARD" warning and faster wave growth (45% per wave). The bot
wins **72% on levels 2-7** (Kitchen: 85%), every pack beats at least 5 of 7,
and every pack wins the teaching level. Piñatas count as 14 threat (body
plus surprise) and never appear in wave 1 of levels 2-7.

**New behavior: piñatas.** A slow, tough walker that bursts into 3-5 small
invaders when broken (walkers, jumpers, fliers, small smashers; never elites
or bosses). The contents *look* random and there's no hint before it pops,
but they're fixed: each piñata's contents come from a seed made of the
level, the wave, and which piñata it is in that wave. Replaying a wave gives
the same surprises, so players can learn them.

Returning behaviors: walker swarms, splitters, smashers, jumpers, fliers,
bombers and spillers (the "everything" bonus world).

| Invader | Type |
|---|---|
| Wind-up Mouse / Wind-up Racer (elite) | Walker swarm |
| Party Bag / Goodie Bag (elite) | Walker, bursts into gumdrops |
| Bouncy Ball | Jumper |
| Toy Robot / Mega Robot (elite) | Smasher |
| Balloon / Big Balloon (elite) | Flier |
| Water Balloon | Bomber |
| Soda Spill / Frosting Blob (elite) | Spiller |
| **Piñata** | New: bursts into a fixed "surprise" |
| **The Clown** | Boss smasher (level 7): tosses mini piñatas a few tiles ahead onto its route |

Beating the Clown shows the bonus world-cleared screen.

## Polish (v0.8)

- **Look:** one theme for menus and the in-level screen. Each world has an
  accent color, used for titles, card stripes and the HUD's accent lines.
- **Game feel:** hit flashes, death puffs, walker bobbing, units pop in when
  placed, a gold sparkle on evolve, screen shake on bombs and base hits.
- **Audio:** generated chiptune sound effects and one music loop for the
  menu and each world (`tools/make_audio.py`). Sound and Music toggles on the
  title screen, saved between sessions. Replace any file in `assets/sfx` or
  `assets/music` with your own of the same name.
- **Final victory:** beating the Mothership shows a big congratulations
  screen with confetti. If the player doesn't own both bonus worlds, it
  suggests them with a button that opens the Store.

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

- Cosmetic unlocks (palettes, skins, menu themes): what and when
- User's v0.8 playtest notes (to handle after Kitchen Defense)
- Orchard (World 3, level 3) is the hardest level for the bot, especially with Toxin
- Overall difficulty after human playtesting (the bot finds most levels easy)
- How the sound, music and new look feel in real play; Blinker frequency
- Save sync (iCloud / Google Play) or local only
