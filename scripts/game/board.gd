class_name Board
extends Node2D
## The battlefield: the tile grid, the units on it, the invaders walking it,
## and the pathfinding that decides where invaders go.
##
## Everything inside the board is measured in 16-pixel tiles. The game scales
## the whole board up on screen, so the pixel art stays crisp.

signal cell_tapped(cell: Vector2i)
## Emitted when an invader reaches the base.
signal base_hit(invader: InvaderData)

const TILE := 16
const NO_CELL := Vector2i(-1, -1)
## How far (in tiles) poison jumps when a poisoned invader dies.
const POISON_SPREAD_RANGE := 1.5

const FLOOR_TEXTURE := preload("res://art/tiles/floor.png")
const ROCK_TEXTURE := preload("res://art/tiles/rock.png")
const SPAWN_TEXTURE := preload("res://art/tiles/spawn.png")
const BASE_TEXTURE := preload("res://art/tiles/base.png")

const PATH_COLOR := Color(1, 1, 1, 0.55)
const SMASHER_PATH_COLOR := Color(1, 0.35, 0.25, 0.7)
const FLIER_PATH_COLOR := Color(0.5, 0.85, 1, 0.7)

var grid_size := Vector2i.ZERO
var rocks := {}  # Vector2i -> true
var spawn_cells: Array[Vector2i] = []
var base_cell := NO_CELL

var units := {}  # Vector2i -> Unit
var invaders: Array[Invader] = []

## True while a wave is running. Units only act during waves.
var wave_active := false

# Two pathfinding grids. Walkers treat units as walls; smashers only avoid
# rocks, because they plan to chew straight through any unit in the way.
var _walk_grid := AStarGrid2D.new()
var _smash_grid := AStarGrid2D.new()

# What the board draws on top of the tiles (set by the game).
var show_path_preview := false
var preview_smashers := false
var preview_fliers := false
var selected_cell := NO_CELL

var _flash_cell := NO_CELL
var _flash_time := 0.0

## Draws shots and pulses above units and invaders.
var fx: ShotEffects


func setup(level: LevelData) -> void:
	grid_size = Vector2i(level.layout[0].length(), level.layout.size())
	for y in grid_size.y:
		for x in grid_size.x:
			var cell := Vector2i(x, y)
			match level.layout[y][x]:
				"#":
					rocks[cell] = true
				"S":
					spawn_cells.append(cell)
				"B":
					base_cell = cell

	for grid in [_walk_grid, _smash_grid]:
		grid.region = Rect2i(Vector2i.ZERO, grid_size)
		grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
		grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
		grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
		grid.update()
		for cell in rocks:
			grid.set_point_solid(cell, true)

	fx = ShotEffects.new()
	fx.z_index = 10
	add_child(fx)
	queue_redraw()


# --- Grid helpers -----------------------------------------------------------

func cell_center(cell: Vector2i) -> Vector2:
	return Vector2(cell * TILE) + Vector2(TILE, TILE) / 2.0


func is_inside(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < grid_size.x and cell.y < grid_size.y


## True if the tile is open floor with nothing on it.
func is_buildable(cell: Vector2i) -> bool:
	return (is_inside(cell) and not rocks.has(cell) and not units.has(cell)
		and cell != base_cell and not spawn_cells.has(cell))


## True if a unit could go here without sealing off the base from any spawn.
func can_place(cell: Vector2i) -> bool:
	return is_buildable(cell) and path_length_if_blocked(cell) >= 0


## Total length of every walker route if this tile were blocked, or -1 if
## blocking it would seal a spawn off from the base. Pass NO_CELL to measure
## the routes as they are now.
func path_length_if_blocked(cell: Vector2i) -> int:
	var paths := walker_paths_if_blocked(cell)
	if paths.is_empty():
		return -1
	var total := 0
	for path in paths:
		total += path.size()
	return total


## Every spawn's walker route if this tile were blocked (empty if that would
## seal a spawn off). Pass NO_CELL for the routes as they are now.
func walker_paths_if_blocked(cell: Vector2i) -> Array:
	var pretend := is_inside(cell)
	var was_solid := pretend and _walk_grid.is_point_solid(cell)
	if pretend:
		_walk_grid.set_point_solid(cell, true)
	var paths := []
	for spawn in spawn_cells:
		var path := _walk_grid.get_id_path(spawn, base_cell)
		if path.is_empty():
			paths.clear()
			break
		paths.append(path)
	if pretend:
		_walk_grid.set_point_solid(cell, was_solid)
	return paths


## The route a walking invader takes from `from_cell` to the base.
func walker_path(from_cell: Vector2i) -> Array[Vector2i]:
	return _walk_grid.get_id_path(from_cell, base_cell)


## The route a smasher takes: shortest path that only avoids rocks.
func smasher_path(from_cell: Vector2i) -> Array[Vector2i]:
	return _smash_grid.get_id_path(from_cell, base_cell)


## The unit standing on a tile, if it's still in one piece; otherwise null.
func intact_unit_at(cell: Vector2i) -> Unit:
	var unit: Unit = units.get(cell)
	if unit and not unit.destroyed:
		return unit
	return null


## How many intact units stand on the 8 tiles around a tile.
func neighbor_count(cell: Vector2i) -> int:
	var count := 0
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			if (dx != 0 or dy != 0) and intact_unit_at(cell + Vector2i(dx, dy)):
				count += 1
	return count


# --- Units ------------------------------------------------------------------

func place_unit(data: UnitData, cell: Vector2i) -> Unit:
	var unit := Unit.new()
	unit.setup(data, cell, self)
	add_child(unit)
	units[cell] = unit
	_walk_grid.set_point_solid(cell, true)
	queue_redraw()
	return unit


func remove_unit(cell: Vector2i) -> void:
	var unit: Unit = units.get(cell)
	if unit == null:
		return
	units.erase(cell)
	unit.queue_free()
	_walk_grid.set_point_solid(cell, false)
	queue_redraw()


## Called by a unit when a smasher breaks it. The tile opens up, so walkers
## may now find a shorter route.
func on_unit_destroyed(unit: Unit) -> void:
	_walk_grid.set_point_solid(unit.cell, false)
	for invader in invaders:
		invader.repath()


## Between waves: every unit is repaired to full, even destroyed ones.
func restore_units() -> void:
	for cell in units:
		units[cell].restore()
		_walk_grid.set_point_solid(cell, true)


# --- Invaders ---------------------------------------------------------------

func spawn_invader(data: InvaderData, spawn_index: int) -> void:
	var start := spawn_cells[spawn_index % spawn_cells.size()]
	var path: Array[Vector2i] = []
	match data.movement:
		InvaderData.Movement.PATHER:
			path = walker_path(start)
		InvaderData.Movement.SMASHER:
			path = smasher_path(start)
	_add_invader(data, cell_center(start), path, 0)


## Adds invaders at another invader's position, following its route
## (used for splitting and for boss minions).
func spawn_from(parent: Invader, data: InvaderData, count: int) -> void:
	for i in count:
		# Nudge them apart a little so they don't overlap exactly.
		var nudge := Vector2(randf_range(-3, 3), randf_range(-3, 3))
		var path: Array[Vector2i] = []
		var index := 0
		if data.movement == InvaderData.Movement.PATHER and parent.path_index < parent.path.size():
			# Walkers need a walker route, even if the parent was a smasher.
			path = walker_path(parent.path[parent.path_index])
		elif data.movement != InvaderData.Movement.FLIER:
			path = parent.path.duplicate()
			index = parent.path_index
		_add_invader(data, parent.position + nudge, path, index)


func _add_invader(data: InvaderData, pos: Vector2, path: Array[Vector2i], path_index: int) -> void:
	var invader := Invader.new()
	invader.setup(data, self, pos, path, path_index)
	add_child(invader)
	invaders.append(invader)


func on_invader_killed(invader: Invader) -> void:
	invaders.erase(invader)
	if invader.data.split_into:
		spawn_from(invader, invader.data.split_into, invader.data.split_count)
	# Spreading poison jumps to everyone nearby when its carrier dies.
	if invader.poison_time > 0.0 and invader.poison_spreads:
		for other in invaders:
			if other.position.distance_to(invader.position) <= POISON_SPREAD_RANGE * TILE:
				other.apply_poison(invader.poison_dps, invader.poison_time, true)
	invader.queue_free()


func on_invader_reached_base(invader: Invader) -> void:
	invaders.erase(invader)
	invader.queue_free()
	base_hit.emit(invader.data)


# --- Feedback ---------------------------------------------------------------

## Briefly flashes a tile red, e.g. when a placement isn't allowed.
func flash(cell: Vector2i) -> void:
	_flash_cell = cell
	_flash_time = 0.4
	queue_redraw()


func _process(delta: float) -> void:
	if _flash_time > 0.0:
		_flash_time -= delta
		queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	# Touches arrive as mouse clicks (Godot converts them by default).
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var cell := Vector2i((get_local_mouse_position() / TILE).floor())
		if is_inside(cell):
			get_viewport().set_input_as_handled()
			cell_tapped.emit(cell)


# --- Drawing ----------------------------------------------------------------

func _draw() -> void:
	for y in grid_size.y:
		for x in grid_size.x:
			var cell := Vector2i(x, y)
			var texture := FLOOR_TEXTURE
			if rocks.has(cell):
				texture = ROCK_TEXTURE
			elif spawn_cells.has(cell):
				texture = SPAWN_TEXTURE
			elif cell == base_cell:
				texture = BASE_TEXTURE
			draw_texture(texture, Vector2(cell * TILE))

	if show_path_preview:
		for spawn in spawn_cells:
			if preview_fliers:
				draw_dashed_line(cell_center(spawn), cell_center(base_cell), FLIER_PATH_COLOR, 1.0, 3.0)
			if preview_smashers:
				_draw_path(smasher_path(spawn), SMASHER_PATH_COLOR)
			_draw_path(walker_path(spawn), PATH_COLOR)

	if selected_cell != NO_CELL:
		draw_rect(Rect2(Vector2(selected_cell * TILE), Vector2(TILE, TILE)), Color.WHITE, false, 1.0)
		var unit: Unit = units.get(selected_cell)
		if unit and unit.data.can_attack():
			draw_arc(cell_center(selected_cell), unit.data.attack_range * TILE, 0, TAU, 48, Color(1, 1, 1, 0.6), 1.0)

	if _flash_time > 0.0:
		draw_rect(Rect2(Vector2(_flash_cell * TILE), Vector2(TILE, TILE)), Color(1, 0, 0, _flash_time))


func _draw_path(path: Array[Vector2i], color: Color) -> void:
	if path.size() < 2:
		return
	var points := PackedVector2Array()
	for cell in path:
		points.append(cell_center(cell))
	draw_polyline(points, color, 1.0)
