class_name Invader
extends Node2D
## One invader moving toward the base. How it moves depends on its type:
## walkers follow their path around units, smashers stop to chew through
## units on their path, and fliers go in a straight line.

var data: InvaderData
var board: Board
var hp: float
var alive := true
## The tiles this invader will walk through, ending at the base.
var path: Array[Vector2i] = []
## Which tile in `path` it is currently heading toward.
var path_index := 0


func setup(p_data: InvaderData, p_board: Board, start: Vector2, p_path: Array[Vector2i], p_index: int) -> void:
	data = p_data
	board = p_board
	hp = data.max_hp
	position = start
	path = p_path
	path_index = p_index
	var sprite := Sprite2D.new()
	sprite.texture = data.texture
	add_child(sprite)
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


func take_damage(amount: float) -> void:
	if not alive:
		return
	hp -= amount
	queue_redraw()
	if hp <= 0.0:
		alive = false
		board.on_invader_killed(self)


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
	if is_flying():
		_fly(delta)
	else:
		_walk(delta)


func _fly(delta: float) -> void:
	var target := board.cell_center(board.base_cell)
	position = position.move_toward(target, data.speed * Board.TILE * delta)
	if position.distance_to(target) < 0.5:
		alive = false
		board.on_invader_reached_base(self)


func _walk(delta: float) -> void:
	var step := data.speed * Board.TILE * delta
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
				blocker.take_damage(data.smash_damage * delta)
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
	if hp < data.max_hp:
		draw_rect(Rect2(-6, -9, 12, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-6, -9, 12.0 * hp / data.max_hp, 2), Color(1, 0.3, 0.3))
