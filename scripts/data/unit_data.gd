class_name UnitData
extends Resource
## Describes one kind of unit the player can place: a wall or an attacker.
## Each unit type lives in its own file in data/units/. To rebalance a unit,
## open its .tres file in Godot and change the numbers in the Inspector.

enum Role { WALL, ATTACKER }

@export var id: String = ""
@export var display_name: String = ""
@export var role: Role = Role.WALL
## Price in ATP when bought from the shop. Selling refunds 75% of this.
@export var cost: int = 5
@export var max_hp: int = 20

@export_group("Attack (attackers only)")
@export var damage: int = 0
## How far the unit can hit, measured in tiles from its center.
@export var attack_range: float = 1.5
## Seconds between attacks.
@export var attack_interval: float = 1.0
## Whether this unit can hit flying invaders.
@export var hits_air: bool = false

@export_group("Looks")
@export var texture: Texture2D
@export var shot_color: Color = Color.WHITE
@export_multiline var description: String = ""
