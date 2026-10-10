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
## Elite and boss invaders are drawn larger.
@export var is_elite: bool = false
@export var is_boss: bool = false

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
