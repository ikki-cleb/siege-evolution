class_name InvaderData
extends Resource
## Describes one kind of invader. Each type lives in data/invaders/<biome>/.

enum Movement {
	PATHER,  ## Walks around every unit, taking the shortest open route.
	SMASHER, ## Walks straight at the base and chews through any unit in the way.
	FLIER,   ## Flies straight to the base, ignoring the maze entirely.
}

@export var id: String = ""
@export var display_name: String = ""
@export var movement: Movement = Movement.PATHER
@export var max_hp: int = 10
## Damage removed from every non-piercing hit (a hit always does at least 1).
@export var armor: int = 0
## HP regained per second.
@export var regen: float = 0.0
## Movement speed in tiles per second.
@export var speed: float = 1.0
## How much base HP this invader removes if it reaches the base.
@export var base_damage: int = 1
## Damage per second dealt to units blocking its way (smashers only).
@export var smash_damage: float = 0.0
## ATP dropped when killed (boss minions never drop any).
@export var atp_drop: int = 1
## Elite and boss invaders are drawn larger.
@export var is_elite: bool = false
@export var is_boss: bool = false

## Boats travel only on water tiles, starting from sea spawns ("N").
@export var naval: bool = false

@export_group("Bombing")
## Fliers with a bomb drop it once, partway along their flight, on the most
## valuable unit near them. The target takes full damage; the 8 tiles around
## it take half.
@export var bomb_damage: float = 0.0
## If above 0, keeps bombing every this many seconds (bosses).
@export var bomb_interval: float = 0.0

@export_group("Teleporting")
## Every this many seconds, blinks forward along its route (0 = never).
@export var blink_interval: float = 0.0
## How many tiles of its route each blink skips.
@export var blink_distance: int = 0

@export_group("Jumping")
## Jumpers can hop over any single unit tile (not rocks, and not walls two
## tiles thick). Each hop costs them a short pause.
@export var jumps: bool = false

@export_group("Burrowing")
## Tiles walked before digging underground (0 = never burrows).
@export var burrow_after: int = 0
## How many tiles of its route it skips while underground. Underground
## invaders can't be hit and smashers don't chew while tunneling.
@export var burrow_length: int = 0

@export_group("Splitting")
## If set, this invader splits into copies of another invader when killed.
@export var split_into: InvaderData
@export var split_count: int = 0

@export_group("Minions")
## If set, this invader releases minions while it walks (used by bosses).
@export var minion: InvaderData
@export var minion_count: int = 0
@export var minion_interval: float = 0.0

@export_group("Looks")
@export var texture: Texture2D
@export_multiline var description: String = ""
