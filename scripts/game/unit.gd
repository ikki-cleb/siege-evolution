class_name Unit
extends Node2D
## A unit the player placed on the board. Every unit blocks its tile;
## attackers also shoot at invaders in range during waves.

var data: UnitData
var cell: Vector2i
var board: Board
var hp: float
## True once a smasher breaks it. It stays broken until the wave ends.
var destroyed := false

var _cooldown := 0.0


func setup(p_data: UnitData, p_cell: Vector2i, p_board: Board) -> void:
	data = p_data
	cell = p_cell
	board = p_board
	hp = data.max_hp
	position = board.cell_center(cell)
	var sprite := Sprite2D.new()
	sprite.texture = data.texture
	add_child(sprite)


func take_damage(amount: float) -> void:
	if destroyed:
		return
	hp -= amount
	if hp <= 0.0:
		hp = 0.0
		destroyed = true
		visible = false
		board.on_unit_destroyed(self)
	queue_redraw()


## Back to full health (called between waves).
func restore() -> void:
	hp = data.max_hp
	destroyed = false
	visible = true
	_cooldown = 0.0
	queue_redraw()


func _process(delta: float) -> void:
	if destroyed or data.role != UnitData.Role.ATTACKER or not board.wave_active:
		return
	_cooldown -= delta
	if _cooldown > 0.0:
		return
	var target := _find_target()
	if target == null:
		return
	_cooldown = data.attack_interval
	board.fx.add_shot(position, target.position, data.shot_color)
	target.take_damage(data.damage)


## Picks the invader in range that is closest to reaching the base.
func _find_target() -> Invader:
	var best: Invader = null
	var best_distance := INF
	for invader in board.invaders:
		if invader.is_flying() and not data.hits_air:
			continue
		if position.distance_to(invader.position) > data.attack_range * Board.TILE:
			continue
		var distance := invader.distance_to_base()
		if distance < best_distance:
			best_distance = distance
			best = invader
	return best


func _draw() -> void:
	# Health bar, only shown while damaged.
	if hp < data.max_hp:
		draw_rect(Rect2(-7, -9, 14, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-7, -9, 14.0 * hp / data.max_hp, 2), Color(0.3, 1, 0.4))
