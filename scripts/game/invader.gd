class_name Invader
extends Node2D
## One invader moving toward the base. How it moves depends on its type:
## walkers follow their path around units, smashers stop to chew through
## units on their path, and fliers go in a straight line.
##
## Units can put effects on invaders: slow, stun, poison, and mark (takes
## extra damage). Each effect shows as a tint on the sprite.

var data: InvaderData
var board: Board
var hp: float
var alive := true
## False for boss minions, so bosses can't be farmed for ATP.
var drops_atp := true
## The tiles this invader will walk through, ending at the base.
var path: Array[Vector2i] = []
## Which tile in `path` it is currently heading toward.
var path_index := 0

# Active effects. Each has a strength and the seconds it has left.
var slow_amount := 0.0
var slow_time := 0.0
var stun_time := 0.0
var poison_dps := 0.0
var poison_time := 0.0
var poison_spreads := false
var mark_bonus := 0.0
var mark_time := 0.0

const POISON_STACK_LIMIT := 3.0

var _minion_timer := 0.0
var _sprite: Sprite2D


func setup(p_data: InvaderData, p_board: Board, start: Vector2, p_path: Array[Vector2i], p_index: int) -> void:
	data = p_data
	board = p_board
	hp = data.max_hp
	position = start
	path = p_path
	path_index = p_index
	_minion_timer = data.minion_interval
	_sprite = Sprite2D.new()
	_sprite.texture = data.texture
	if data.is_boss:
		_sprite.scale = Vector2(1.75, 1.75)
	add_child(_sprite)
	# Fliers are drawn above everything else on the board.
	z_index = 5 if is_flying() else 1


func is_flying() -> bool:
	return data.movement == InvaderData.Movement.FLIER


## Roughly how many tiles are left before this invader reaches the base.
## Attackers use this to target whoever is most dangerous.
func distance_to_base() -> float:
	if is_flying() or path_index >= path.size():
		return position.distance_to(board.cell_center(board.base_cell)) / Board.TILE
	var to_next := position.distance_to(board.cell_center(path[path_index])) / Board.TILE
	return (path.size() - 1 - path_index) + to_next


## A hit from a unit. Armor reduces each hit unless it pierces.
func take_damage(amount: float, pierce := false) -> void:
	if not alive:
		return
	if not pierce and data.armor > 0:
		amount = max(1.0, amount - data.armor)
	if mark_time > 0.0:
		amount *= 1.0 + mark_bonus
	hp -= amount
	queue_redraw()
	if hp <= 0.0:
		alive = false
		board.on_invader_killed(self)


func apply_slow(amount: float, duration: float) -> void:
	# A weaker slow never replaces a stronger one that's still running.
	if amount >= slow_amount or slow_time <= 0.0:
		slow_amount = amount
	slow_time = max(slow_time, duration)


func apply_stun(duration: float) -> void:
	# Bosses shrug off most of a stun.
	stun_time = max(stun_time, duration * (0.3 if data.is_boss else 1.0))


## Poison stacks: each new dose adds on top of what's already there, up to
## three times the strength of the dose.
func apply_poison(dps: float, duration: float, spreads: bool) -> void:
	var current := poison_dps if poison_time > 0.0 else 0.0
	poison_dps = max(current, min(current + dps, dps * POISON_STACK_LIMIT))
	poison_time = max(poison_time, duration)
	poison_spreads = poison_spreads or spreads


func apply_mark(bonus: float, duration: float) -> void:
	mark_bonus = max(mark_bonus if mark_time > 0.0 else 0.0, bonus)
	mark_time = max(mark_time, duration)


## Walkers find a new route when the maze changes (a smasher broke a unit).
func repath() -> void:
	if data.movement != InvaderData.Movement.PATHER or path_index >= path.size():
		return
	var new_path := board.walker_path(path[path_index])
	if not new_path.is_empty():
		path = new_path
		path_index = 0


func _process(delta: float) -> void:
	if not alive:
		return
	_update_effects(delta)
	if not alive:
		return
	if data.minion and data.minion_interval > 0.0:
		_minion_timer -= delta
		if _minion_timer <= 0.0:
			_minion_timer = data.minion_interval
			board.spawn_from(self, data.minion, data.minion_count, false)
	if stun_time > 0.0:
		return
	var speed := data.speed * (1.0 - slow_amount if slow_time > 0.0 else 1.0)
	if is_flying():
		_fly(speed * delta)
	else:
		_walk(speed * delta, delta)


func _update_effects(delta: float) -> void:
	slow_time = max(0.0, slow_time - delta)
	stun_time = max(0.0, stun_time - delta)
	mark_time = max(0.0, mark_time - delta)
	if data.regen > 0.0:
		hp = min(hp + data.regen * delta, data.max_hp)
	if poison_time > 0.0:
		poison_time = max(0.0, poison_time - delta)
		take_damage(poison_dps * delta, true)

	# Tint shows the strongest active effect.
	var tint := Color.WHITE
	if poison_time > 0.0:
		tint = Color(0.6, 1.0, 0.5)
	if slow_time > 0.0:
		tint = Color(0.6, 0.8, 1.0)
	if stun_time > 0.0:
		tint = Color(1.0, 1.0, 0.5)
	_sprite.modulate = tint
	queue_redraw()


func _fly(tiles: float) -> void:
	var target := board.cell_center(board.base_cell)
	position = position.move_toward(target, tiles * Board.TILE)
	if position.distance_to(target) < 0.5:
		alive = false
		board.on_invader_reached_base(self)


func _walk(tiles: float, delta: float) -> void:
	var step := tiles * Board.TILE
	while step > 0.0:
		if path_index >= path.size():
			alive = false
			board.on_invader_reached_base(self)
			return
		var next_cell := path[path_index]
		# Smashers stop and chew on any unit standing on their next tile.
		if data.movement == InvaderData.Movement.SMASHER:
			var blocker := board.intact_unit_at(next_cell)
			if blocker:
				blocker.take_damage(data.smash_damage * delta, self)
				return
		var target := board.cell_center(next_cell)
		var distance := position.distance_to(target)
		if distance > step:
			position = position.move_toward(target, step)
			return
		position = target
		step -= distance
		path_index += 1


func _draw() -> void:
	var half := 9.0 if data.is_boss else 6.0
	if hp < data.max_hp:
		draw_rect(Rect2(-half, -half - 4, half * 2, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-half, -half - 4, half * 2 * hp / data.max_hp, 2), Color(1, 0.3, 0.3))
	if mark_time > 0.0:
		draw_circle(Vector2(half - 1, -half + 1), 1.5, Color(1, 0.2, 0.2))
