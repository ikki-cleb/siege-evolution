# Siege Evolution: Game Design Document

Status: **v1.2, all 5 main worlds plus both bonus worlds** (35 levels,
5 packs, evolutions, saved progress, sound, music, store in test mode). Balance is tuned against an automated player, not real play yet.

## Pitch

A puzzle tower defense played in portrait on phones. Each level is a grid
where your units are the maze: walls and defenders shape the invaders' route
while they fight. There's no single solution. Many layouts work, and the best
ones aren't obvious going in. Each world is its own setting with its own
invaders, from the backyard to outer space; beating a world's boss unlocks
the next one.

## Platform & tech

| Decision | Choice |
|---|---|
| Engine | Godot 4.7, GDScript |
| Platforms | iOS + Android (iOS builds need a Mac with Xcode). A web build is used for playtesting. |
| Orientation | Portrait only |
| Animation | Units and invaders can have **animation strips**: one PNG per animation, square 64×64 frames side by side (`art/anim/<world>/...`). Units: idle (loops, 4 fps) and attack (plays once per shot at 10 fps, sped up so it ends before the next shot; plain walls have none). Invaders: move (loops, 10 fps) and death (plays once where it died, replacing the white puff). Base units and tier-1 evolutions have their own strips; capstones reuse tier 1's and the game draws a gold star. Without strips the still sprite is used. **All sprites are drawn in code** at 32×32 per frame (`tools/draw_sprites.py`, designs in `tools/sprites/`): cute shaded cells with faces and pack-color accents; tier-1 evolutions add spikes (power branch) or a lens antenna (reach branch); walls add armor bands or spikes. Only living things have faces (cells, bugs, animals, aliens, pests, the clown); objects, toys, robots and gear don't. Final art can replace any strip via `tools/import_sprites.py`. Unit buttons show the first idle frame. |
| Art | 16×16 pixel tiles, integer-scaled. Placeholders for now; the user draws the final art. Each level can also have a painted **ground background** (detailed pixel art, 1152×1792, 9:14 portrait, no obstacles baked in) that replaces its floor tiles; rocks, spawns, base and water still draw on top. The importer softens every background (30% less color, a bit less contrast, slightly brighter) so the art stays calm and sprites stand out. |
| Menus | Clean dark style with two fonts (chosen from two rounds of screenshot comparisons): **Coiny** for titles, buttons and any label 18px or bigger, and **Space Mono** for all other text (both SIL OFL). `tools/make_font.py` builds `SiegeTitle.ttf` / `SiegeText.ttf` from them, adding the coin, arrow and star icons, shrinking Space Mono 12% to fit the layouts, mirroring Coiny's "/" (it leans the wrong way) and redrawing its V and v as pointed Vs (its rounded V made "EVOLUTION" read as "EUOLUTION"). Each world has an accent color (`scripts/look.gd`, `scripts/palette.gd`). |
| Business model | Free, no ads. Optional $1 purchases (see Monetization). |

## Structure

Worlds were cut from 7 levels of 10 waves to **5 levels of 8 waves** (the
old levels 3 and 5 were dropped, and waves grow faster so the final wave
is as big as before). Old saves convert by position. After the cut the bot
wins (levels 2-5): World 1 95%, World 2 95%, World 3 90%, World 4 90%,
World 5 85%, Kitchen 90%, Birthday 70%. Older numbers quoted below were
measured before the cut.

```
Title → World select → Level select with pack picker (5 levels) → Level (8 waves)
```

- **Worlds (biomes):** 5 levels each, at one scale. Beating level 5 (the boss)
  unlocks the next world. The five main worlds, in order (since v1.1;
  Microscopic used to be first, but its body-tissue art was too unsettling
  for a first world):
  1. **Backyard Bugs** (defend the queen's anthill), built
  2. **Wild Kingdom** (human and animal scale: defend the farmhouse), built
  3. **Microscopic** (the immune system), built
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
  that world's level 1, and levels 2–5 add **elite variants** of them.
- **Packs swap freely.** The level list has a pack picker at the top (it
  remembers the last pick per world). World progress is **shared**: beating
  a level with any pack unlocks the next one. Each pack also remembers which
  levels it has beaten, shown on the level list as initials ("Beaten: F S"),
  for pack mastery. Each pack plays the same way in every world; later
  worlds only give its units new names and art for the scale.
- **Progress** is saved locally: levels cleared per world, the last pack
  picked, and which levels each pack has beaten. Old saves convert (their
  single pack is credited with the levels it cleared).

## Achievements

27 achievements, listed on an **Achievements** screen from the title (earned
ones in gold with a star; locked ones dimmed with their goal and progress,
e.g. "1,240 / 5,000"). Earning one slides a banner in at the top of the
screen, in a level or in the menus. The list lives in
`data/achievements.json`; `scripts/achievements.gd` tracks and saves them.

- **Progress (8):** beat each main world (5), beat all 5 main worlds, beat
  each bonus world (2).
- **Pack mastery (6):** beat all 25 main-world levels with one pack (one per
  pack), and master all 5 packs. Bonus worlds don't count.
- **Skill (6):** Flawless (no base HP lost), Untouchable Boss (the same on a
  boss level), Close Call (win on 1 HP), Back to Basics (no evolutions),
  Blindfolded (boss level with Paths off the whole time), Minimalist (6 or
  fewer units on the board).
- **Collection & fun (7):** evolve a unit, buy a capstone, own capstones of
  all 12 mechanics, earn 10,000 coins, defeat 5,000 invaders, break 50
  piñatas, hold 100 coins at once.

### First level of every world (teaching level)

- Introduces every invader type in the world, about one idea per wave.
- Shows a tip in a footnote under the board before each wave (never a pop-up).
- Gives extra coins so players can try an evolution.

## Core loop

1. **Build phase:** see the next wave's contents. Place units, tap a placed
   unit to evolve or remove it.
2. **Wave phase:** invaders spawn and travel to the base. No building.
   Fast-forward is available (1×/2×/4×). The chosen speed only applies
   during waves; the build phase always runs at 1×, so starting a wave
   visibly speeds up.
3. Survive **8 waves** to clear the level. **Pass/fail only**, no stars.
4. **Removing a unit** takes two taps: the first turns the Remove button
   into "Tap again to remove", the second removes it (selecting anything
   else cancels).
5. **The base** is a 3x2 block on the bottom middle of the board (the "B"
   in a layout marks its bottom-middle tile; at the sides it shifts inward).
   Nothing can be built on it, and invaders arrive as soon as they step onto
   any of its tiles (fliers: as soon as they're over it). Each world draws it
   as one big sprite with depth (`tools/draw_bases.py`: anthill, farmhouse,
   heart, toy fort, reactor, cookie jar, cake). It cracks below 2/3 and 1/3
   HP, and flashes red and shakes when hit.
6. **Lose:** the base has 20 HP, and each invader does its own base damage
   when it arrives. **A boss reaching the base is always an instant loss**
   (its minions only do their normal damage).

**Boss levels:** the boss's spawn tile is marked with a pulsing purple glow
and a pixel skull for the whole level, so players can plan from wave 1. In
the build phase right before the boss wave, the boss's own route is drawn as
a thicker purple line (shown even with Paths off) and the footnote warns
that the boss reaching the base loses the level.

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

## Relics

On every level except a world's teaching level, waves **1, 3, 5 and 7** each
have one **relic carrier**: the toughest non-boss invader of the wave, glowing
gold with a gem over its head. Kill it and it drops a relic; if it reaches the
base, that relic is lost. When the wave ends, a **choose 1 of 3** card screen
opens (the next wave can't start until you pick). The relic **starts working
when the next wave starts** and lasts until the end of the level (max 4).
One-time relics (gift coins, base heal, free walls) pay out **the moment
they're picked**.

- **Pool:** 64 relics in `data/relics.json` (32 common, 22 rare, 10 epic).
  Each targets all units, a role (attackers, walls, anti-air, ground-only,
  single-target, pulse, long/short range) or a mechanic (splash, slow, stun,
  poison, mark, swarm, regen, reflect, chain, multishot, knockback), or is an
  economy relic (coins per kill, coins per wave, cheaper evolutions, better
  refunds, base heal, free walls, interest, gift coins, clean-wave bonus).
  New relics need no code if they use existing filters, stats and keys
  (a rules test checks every entry).
- **Offers** only include relics useful for the units you can field this
  level, never repeat one you have, and later relics in a level roll better
  rarities (epic chance 3% for the first, 18% for the fourth). Offers are
  **fully random** every time (the user chose variety and replayability
  over exact balance), so bot balance numbers vary a little between runs.
- **How it works in code:** `scripts/game/relic_set.gd` (pool, filters,
  offers, stat math), `Unit.stat()` (every relic-affected stat goes through
  it), `scripts/ui/relic_icon.gd` (38 pixel icons). Picked relics show as
  icons in the board's left margin (dimmed until active; tap for details).
  The auto-player picks the rarest relic, preferring unit upgrades.

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
- **Path preview** shows the next wave's routes during every build phase:
  the walker route, plus smasher (red), flier (blue) and jumper (orange)
  lines when the next wave has them, and the boss (thick purple) before the
  boss wave. A "Paths" button next to the speed
  button turns it off; the choice is saved.
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
then one new unit on **levels 2, 3 and 4**. Each unit **evolves once**, into
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

## Microscopic unit names

Microscopic uses plain body words, not biology terms, so the
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

## Invaders (Microscopic, World 3)

| Invader | Type | Notes |
|---|---|---|
| Rhinovirus | Walker | Fast, weak swarms |
| Flu Virus | Walker (elite, level 2+) | Much faster |
| Bacterium | Walker | Splits into 2 halves |
| Biofilm Colony | Walker (elite, level 3+) | Armor 2, splits |
| Parasite Worm | Smasher | Chews through any unit in its way |
| Hookworm | Smasher (elite, level 3+) | Regenerates |
| Spore | Flier | Flies straight over the maze |
| Fungal Spore | Flier (elite, level 4+) | Armor 1, tougher |
| **Superbug** | Boss smasher (level 5, last wave) | Armor 1, releases Rhinoviruses as it walks |

Armor reduces each non-piercing hit (a hit always does at least 1). Poison ignores armor.

## Invaders (Backyard Bugs, World 1)

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
| Hercules Beetle | Smasher (elite, level 3+) | Armor 2 |
| Mosquito | Flier | |
| Hornet | Flier (elite, level 4+) | Armor 1, tougher |
| **Giant Centipede** | Boss smasher (level 5, last wave) | Tunnels once, releases termites |

## Invaders (Wild Kingdom, World 2)

New behavior: **jumpers.** They plan their route as if they can hop over any
single unit tile (not rocks, not walls two tiles thick), pausing briefly
before each hop. On the tutorial level their route shows in orange. Burrowers
return from Backyard Bugs. Wild Kingdom's invaders are tougher for the coins
they drop, though drops stay generous enough to keep building.

| Invader | Type | Notes |
|---|---|---|
| Rat | Walker | Fast swarms |
| Weasel | Walker (elite, level 2+) | Very fast, armor 1 |
| Deer | **Jumper** | Hops single unit tiles |
| Red Stag | Jumper (elite, level 3+) | Armor 1 |
| Coyote Pack | Walker | Scatters into 3 coyotes |
| Wolf Pack | Walker (elite, level 3+) | Armor 2, scatters into wolves |
| Wild Boar | Smasher | Charges through units |
| Moose | Smasher (elite, level 4+) | Armor 2 |
| Crow | Flier | |
| Hawk | Flier (elite, level 4+) | Armor 1 |
| Gopher | Burrower | Tunnels under 6 tiles |
| **Grizzly Bear** | Boss smasher (level 5, last wave) | Armor 2, brings bear cubs |

## World 4: Total War (toy soldiers)

Tone is a lighthearted **toy war**: plastic army men, toy tanks, paper planes
and bath-toy boats. You defend a toy fort HQ. Walls are toy fortifications
(sandbags, barbed wire, concrete barriers, barricades, barrels), attackers
are toy troops and turrets.

**Sea levels (2, 3, 4) have water lanes.** Water tiles (`~`) carry boats only,
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
the wave as usual. **Bombs are telegraphed:** a bomb sprite falls from the
bomber for 0.9s while the 3x3 blast area blinks red with brackets on the
target tile, then it explodes (flash, fireball, shockwave, smoke) and deals
its damage. The same goes for the Mothership's repeated bombs.

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
| **Mega Tank** | Boss smasher (level 5) | Deploys toy soldiers |

**Balance lesson:** invader stats should stay comparable across worlds,
because packs restart at base stats in every world. Difficulty should come
from mechanics, layouts and wave mixes, not raw HP inflation.

## World 5: Galactic Siege (final main world)

Levels alternate settings with their own tiles: **moon surface** (levels 1,
3, 5), **station interior** (2) and **asteroid field** (4). Any level
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
hit it, and every pack has at least one. Since reaching the reactor is an
instant loss, it has 550 HP (was 1100), in line with the other final bosses.

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
levels 2-5** (level 1 is the easy teaching level) because more global
difficulty only broke Fortress and Precision while Swarm, Control and Toxin
kept winning. Final call is the user's playtest. Every pack beats at least
3 of 5 levels.

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
| **Rat King** | Boss smasher (level 5): sheds rats, leaves a grease trail |

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
wins **72% on levels 2-5** (Kitchen: 85%), every pack beats at least 3 of 5,
and every pack wins the teaching level. Piñatas count as 14 threat (body
plus surprise) and never appear in wave 1 of levels 2-5.

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
| **The Clown** | Boss smasher (level 5): tosses mini piñatas a few tiles ahead onto its route |

Beating the Clown shows the bonus world-cleared screen.

## Polish (v0.8)

- **Look:** one theme for menus and the in-level screen. Each world has an
  accent color, used for titles, card stripes and the HUD's accent lines.
- **Burrowing:** a burrower sinks into the ground with dirt spraying,
  leaving a hole. Underground it's a wobbling soil bump with a small shield
  icon (can't be hit) that leaves a fading trail, and a red dashed line runs
  to a pulsing red ring where it will come up. It pops out with a hop and a
  dirt burst, leaving a second hole for a few seconds. Submarines get the
  water version: splash, foam ripple, bubble trail, splash on surfacing.
- **Special moves read clearly:** teleporters flicker purple and show a
  shrinking ring plus a dashed line to their landing tile for 0.6s before a
  blink, then leave a purple streak and flash on arrival. Jumpers squash and
  bracket their landing tile while crouching, cast a shadow mid-hop and puff
  dust on landing. Split pieces, piñata surprises and boss minions fly out
  of their parent. Spillers lob visible goo blobs onto units, and sticky
  units get a goo puddle.
- **Player effects on enemies:** stunned = circling stars, slowed = frost
  specks, poisoned = green bubbles (one per stacked dose; poison and zones
  no longer make enemies flash white every frame), marked = red reticle,
  grabbed = gold hand. Chain hits draw lightning, splash hits flash their
  blast area, knockbacks leave a white shove streak.
- **Fire rate:** a unit's info line shows its fire rate as shots per
  second. A placed unit sped up by neighbors (Swarm), auras or slowed by goo
  shows its current rate with the base in brackets ("2.9 shots/s (base
  2.2)"). Long info lines drop to a smaller font so two lines fit.
- **Heft:** units are drawn 12% bigger, sit on a faint dark pad with a
  soft shadow, and drop onto their tile when placed (squash on landing,
  dust puffs, low thud sound). If a placement changes an invader route, the
  new route flashes bright yellow and fades over 0.7s.
- **Gridlines:** very faint grey lines between tiles during every build
  phase (hidden during waves), so it's easy to see where a unit will go.
- **Enemy outline:** every invader has a thin solid red ring around its
  sprite (`shaders/enemy_outline.gdshader`), so enemies never look like the
  player's units. Units have no outline.
- **Digits:** all digits in the game font have the same width, and the
  period has a gap on each side, so prices like "$1.00" can't read as "$100".
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
| 4× speed (1× and 2× are free) | $1 |
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
mix per wave (swarm / split / smash / fly, plus burrow in Backyard Bugs), with a
growing share of elites once they're introduced. The output is regular .tres
files that can be edited by hand.

## Balancing method

`tests/sim_test.gd` runs an automated player (`tests/auto_player.gd`) through
every level of every world with every pack (two seeds each) and prints base
HP left. `tests/debug_level.gd` replays one level and prints the layout and
leaks wave by wave. As of v0.4 the auto-player wins most levels comfortably,
so difficulty should be judged by human playtesting next. Current
targets: every pack beats at least 4 of 5 levels (3 of 5 in bonus worlds), levels with no defenses
are lost, and the packs' averages stay close together. Human playtesting
comes next.

## Open questions

- Cosmetic unlocks (palettes, skins, menu themes): what and when
- User's v0.8 playtest notes (to handle after Kitchen Defense)
- Overall difficulty after human playtesting (the bot finds most levels easy)
- How the sound, music and new look feel in real play; Blinker frequency
- Save sync (iCloud / Google Play) or local only
