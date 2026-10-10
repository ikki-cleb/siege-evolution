class_name UnitData
extends Resource
## Describes one kind of unit the player can place, or one evolution of it.
## Each unit lives in data/packs/<pack>/<unit>.tres. To rebalance a unit,
## open its file in Godot and change the numbers in the Inspector.

enum Role {
	WALL,     ## Mainly blocks. May still have a small effect (slow, poison...).
	ATTACKER, ## Mainly deals damage.
	SUPPORT,  ## Helps other units (e.g. marks targets) rather than killing.
}

enum AttackMode {
	SINGLE, ## Hits one target (the one closest to the base).
	PULSE,  ## Hits every invader in range at once.
}

@export var id: String = ""
@export var display_name: String = ""
@export var role: Role = Role.WALL
## Coins to buy this unit. For an evolution, the coins to evolve into it.
@export var cost: int = 5
@export var max_hp: int = 20
## HP regained per second during waves (pauses for 2s after being hit).
@export var regen: float = 0.0
## Share of smasher damage bounced back at the smasher (0.5 = half).
@export var reflect: float = 0.0

@export_group("Attack")
@export var attack_mode: AttackMode = AttackMode.SINGLE
@export var damage: float = 0.0
## How far the unit reaches, in tiles from its center.
@export var attack_range: float = 1.5
## Seconds between attacks.
@export var attack_interval: float = 1.0
@export var hits_air: bool = false
## Ignores invader armor.
@export var pierce: bool = false
## Single-target hits also damage invaders this many tiles around the target.
@export var splash_radius: float = 0.0
## Attacks faster for each unit on the 8 tiles around it (0.15 = +15% each).
@export var adjacency_bonus: float = 0.0

@export_group("Effects on hit")
## Slows invaders by this share of their speed (0.3 = 30% slower).
@export var slow: float = 0.0
@export var slow_duration: float = 0.0
@export var stun_duration: float = 0.0
## Poison damage per second (ignores armor).
@export var poison_dps: float = 0.0
@export var poison_duration: float = 0.0
## When a poisoned invader dies, the poison jumps to invaders nearby.
@export var poison_spreads: bool = false
## Marked invaders take this much extra damage from everything (0.4 = +40%).
@export var mark_bonus: float = 0.0
@export var mark_duration: float = 0.0

@export_group("Evolution")
## The two evolutions this unit can become (empty for evolved units).
@export var evolutions: Array[UnitData] = []

@export_group("Water")
## Can be placed on water tiles (each pack's basic wall: nets and mines).
@export var can_place_on_water: bool = false
## Sprite used when this unit sits on water.
@export var water_texture: Texture2D

@export_group("Looks")
@export var texture: Texture2D
@export var shot_color: Color = Color.WHITE
@export_multiline var description: String = ""


## True if this unit does anything to invaders on its own.
func can_attack() -> bool:
	return damage > 0.0 or slow > 0.0 or poison_dps > 0.0 or mark_bonus > 0.0 or stun_duration > 0.0
