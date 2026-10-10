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
## Emitted when a killed invader drops ATP. `where` is in screen coordinates.
signal atp_dropped(amount: int, where: Vector2)
## Asks the game to shake the screen (bombs, base hits).
signal shake_requested(strength: float)

const TILE := 16
const NO_CELL := Vector2i(-1, -1)
## How far (in tiles) poison jumps when a poisoned invader dies.
const POISON_SPREAD_RANGE := 1.5
## Route-planning cost of one hop (a normal step costs 1, and a hop covers 2
## tiles), so jumpers only hop when it saves them at least a step.
const HOP_COST := 3
const DIRECTIONS: Array[Vector2i] = [Vector2i(0, 1), Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, -1)]


const PATH_COLOR := Color(1, 1, 1, 0.55)
const SMASHER_PATH_COLOR := Color(1, 0.35, 0.25, 0.7)
const FLIER_PATH_COLOR := Color(0.5, 0.85, 1, 0.7)
const JUMPER_PATH_COLOR := Color(1, 0.65, 0.2, 0.75)
## A bomb's full damage hits its target; the 8 tiles around take this share.
const BOMB_SPLASH := 0.5
## Goo left by spillers (Kitchen Defense).
const SPILL_COLOR := Color(0.85, 0.6, 0.2)

var grid_size := Vector2i.ZERO
var rocks := {}  # Vector2i -> true
## Land spawn points ("S").
var spawn_cells: Array[Vector2i] = []
## Sea spawn points for boats ("N").
var sea_spawn_cells: Array[Vector2i] = []
var water := {}  # Vector2i -> true
var base_cell := NO_CELL

var units := {}  # Vector2i -> Unit
var invaders: Array[Invader] = []

## True while a wave is running. Units only act during waves.
var wave_active := false

# Two pathfinding grids. Walkers treat units as walls; smashers only avoid
# rocks, because they plan to chew straight through any unit in the way.
var _walk_grid := AStarGrid2D.new()
var _smash_grid := AStarGrid2D.new()
# Boats get the same pair, but only water (and the base) is open to them.
var _boat_grid := AStarGrid2D.new()
var _boat_smash_grid := AStarGrid2D.new()

# What the board draws on top of the tiles (set by the game).
var show_path_preview := false
var preview_smashers := false
var preview_fliers := false
var preview_jumpers := false
var selected_cell := NO_CELL

## A tile treated as blocked while testing "what if a unit stood here?".
var _pretend_unit := NO_CELL

var _flash_cell := NO_CELL
var _flash_time := 0.0

## Draws shots and pulses above units and invaders.
var fx: ShotEffects
## Tile art comes from the world (biome) being played, unless the level
## has its own.
var biome: BiomeData
var _tiles := {}


func setup(level: LevelData, p_biome: BiomeData) -> void:
	biome = p_biome
	_tiles = {
		"floor": level.floor_texture if level.floor_texture else biome.floor_texture,
		"rock": level.rock_texture if level.rock_texture else biome.rock_texture,
		"spawn": level.spawn_texture if level.spawn_texture else biome.spawn_texture,
		"base": level.base_texture if level.base_texture else biome.base_texture,
	}
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
				"~":
					water[cell] = true
				"N":
					water[cell] = true
					sea_spawn_cells.append(cell)

	for grid in [_walk_grid, _smash_grid, _boat_grid, _boat_smash_grid]:
		grid.region = Rect2i(Vector2i.ZERO, grid_size)
		grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
		grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
		grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
		grid.update()
	for y in grid_size.y:
		for x in grid_size.x:
			var cell := Vector2i(x, y)
			# Land invaders can't cross rocks or water; boats only use water.
			var land_blocked := rocks.has(cell) or water.has(cell)
			_walk_grid.set_point_solid(cell, land_blocked)
			_smash_grid.set_point_solid(cell, land_blocked)
			var sea_blocked := not water.has(cell) and cell != base_cell
			_boat_grid.set_point_solid(cell, sea_blocked)
			_boat_smash_grid.set_point_solid(cell, sea_blocked)

	fx = ShotEffects.new()
	fx.z_index = 10
	add_child(fx)
	queue_redraw()


# --- Grid helpers -----------------------------------------------------------

func cell_center(cell: Vector2i) -> Vector2:
	return Vector2(cell * TILE) + Vector2(TILE, TILE) / 2.0


func is_inside(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < grid_size.x and cell.y < grid_size.y


## True if the tile is open land floor with nothing on it.
func is_buildable(cell: Vector2i) -> bool:
	return (is_inside(cell) and not rocks.has(cell) and not units.has(cell) and not water.has(cell)
		and cell != base_cell and not spawn_cells.has(cell))


## True if a land unit could go here without sealing off the base from any spawn.
func can_place(cell: Vector2i) -> bool:
	return is_buildable(cell) and path_length_if_blocked(cell) >= 0


## The full placement rule for a specific unit: land as usual, and water
## only for units that allow it (nets and mines), never sealing a sea lane.
func can_place_unit(data: UnitData, cell: Vector2i) -> bool:
	if not water.has(cell):
		return can_place(cell)
	if not data.can_place_on_water or units.has(cell) or sea_spawn_cells.has(cell):
		return false
	return not boat_paths_if_blocked(cell).is_empty() or sea_spawn_cells.is_empty()


## Every sea spawn's boat route if this water tile were blocked (empty if
## that would seal a lane).
func boat_paths_if_blocked(cell: Vector2i) -> Array:
	var was_solid := _boat_grid.is_point_solid(cell)
	_boat_grid.set_point_solid(cell, true)
	var paths := []
	for spawn in sea_spawn_cells:
		var path := _boat_grid.get_id_path(spawn, base_cell)
		if path.is_empty():
			paths.clear()
			break
		paths.append(path)
	_boat_grid.set_point_solid(cell, was_solid)
	return paths


## The grid a unit on this tile blocks: the boat grid on water, else walkers'.
func _blocking_grid(cell: Vector2i) -> AStarGrid2D:
	return _boat_grid if water.has(cell) else _walk_grid


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


## The route a jumper takes: like a walker's, but it may hop over a single
## unit tile to the open tile beyond. Consecutive tiles in the result that
## are 2 apart are hops. (A small Dijkstra search; the grid is tiny.)
func jumper_path(from_cell: Vector2i) -> Array[Vector2i]:
	var cost_so_far := {from_cell: 0}
	var came_from := {}
	var frontier: Array = [[0, from_cell]]
	while not frontier.is_empty():
		var best := 0
		for i in frontier.size():
			if frontier[i][0] < frontier[best][0]:
				best = i
		var item: Array = frontier.pop_at(best)
		var cell: Vector2i = item[1]
		if item[0] > cost_so_far[cell]:
			continue
		if cell == base_cell:
			break
		for direction in DIRECTIONS:
			var next: Vector2i = cell + direction
			var step_cost := 1
			if not _is_open(next):
				# Hop: over exactly one unit, onto an open tile.
				if _is_unit_tile(next) and _is_open(next + direction):
					next += direction
					step_cost = HOP_COST
				else:
					continue
			var new_cost: int = cost_so_far[cell] + step_cost
			if new_cost < cost_so_far.get(next, 1 << 30):
				cost_so_far[next] = new_cost
				came_from[next] = cell
				frontier.append([new_cost, next])
	var path: Array[Vector2i] = []
	if not cost_so_far.has(base_cell):
		return path
	var cell := base_cell
	while cell != from_cell:
		path.push_front(cell)
		cell = came_from[cell]
	path.push_front(from_cell)
	return path


## Open for walking: inside the grid, no rock or water, no intact unit.
func _is_open(cell: Vector2i) -> bool:
	return is_inside(cell) and not rocks.has(cell) and not water.has(cell) and not _is_unit_tile(cell)


func _is_unit_tile(cell: Vector2i) -> bool:
	return cell == _pretend_unit or intact_unit_at(cell) != null


## Every spawn's jumper route if a unit stood on this tile (NO_CELL = as is).
func jumper_paths_if_blocked(cell: Vector2i) -> Array:
	_pretend_unit = cell
	var paths := []
	for spawn in spawn_cells:
		paths.append(jumper_path(spawn))
	_pretend_unit = NO_CELL
	return paths


## The route an invader of this kind would take from a tile.
func route_for(data: InvaderData, from_cell: Vector2i) -> Array[Vector2i]:
	if data.naval:
		var grid := _boat_smash_grid if data.movement == InvaderData.Movement.SMASHER else _boat_grid
		return grid.get_id_path(from_cell, base_cell)
	match data.movement:
		InvaderData.Movement.SMASHER:
			return smasher_path(from_cell)
		InvaderData.Movement.PATHER:
			return jumper_path(from_cell) if data.jumps else walker_path(from_cell)
	return []


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
	_blocking_grid(cell).set_point_solid(cell, true)
	queue_redraw()
	return unit


func remove_unit(cell: Vector2i) -> void:
	var unit: Unit = units.get(cell)
	if unit == null:
		return
	units.erase(cell)
	unit.queue_free()
	_blocking_grid(cell).set_point_solid(cell, false)
	queue_redraw()


## Called by a unit when a smasher breaks it. The tile opens up, so walkers
## may now find a shorter route.
func on_unit_destroyed(unit: Unit) -> void:
	_blocking_grid(unit.cell).set_point_solid(unit.cell, false)
	for invader in invaders:
		invader.repath()


## Between waves: every unit is repaired to full, even destroyed ones.
func restore_units() -> void:
	for cell in units:
		units[cell].restore()
		_blocking_grid(cell).set_point_solid(cell, true)


# --- Invaders ---------------------------------------------------------------

func spawn_invader(data: InvaderData, spawn_index: int) -> void:
	# Boats start at sea spawns; fliers use land spawns, or sea ones if a
	# level has no land spawns.
	var spawns := sea_spawn_cells if data.naval or spawn_cells.is_empty() else spawn_cells
	var start := spawns[spawn_index % spawns.size()]
	_add_invader(data, cell_center(start), route_for(data, start), 0)


## Adds invaders at another invader's position, following its route
## (used for splitting and for boss minions).
func spawn_from(parent: Invader, data: InvaderData, count: int, drops_atp := true) -> void:
	for i in count:
		# Nudge them apart a little so they don't overlap exactly.
		var nudge := Vector2(randf_range(-3, 3), randf_range(-3, 3))
		var path: Array[Vector2i] = []
		var index := 0
		if parent.is_flying() and not data.movement == InvaderData.Movement.FLIER:
			# Dropped from a flier: start walking from the open tile below it
			# (or the first spawn if it's over a rock).
			var below := Vector2i((parent.position / TILE).floor())
			path = route_for(data, below if _is_open(below) or below == base_cell else spawn_cells[0])
		elif data.movement == InvaderData.Movement.PATHER and parent.path_index < parent.path.size():
			# Walkers need their own kind of route, even if the parent was a smasher.
			path = route_for(data, parent.path[parent.path_index])
		elif data.movement != InvaderData.Movement.FLIER:
			path = parent.path.duplicate()
			index = parent.path_index
		var invader := _add_invader(data, parent.position + nudge, path, index)
		invader.drops_atp = drops_atp


func _add_invader(data: InvaderData, pos: Vector2, path: Array[Vector2i], path_index: int) -> Invader:
	var invader := Invader.new()
	invader.setup(data, self, pos, path, path_index)
	add_child(invader)
	invaders.append(invader)
	return invader


func on_invader_killed(invader: Invader) -> void:
	invaders.erase(invader)
	fx.add_puff(invader.position, Color(1, 1, 1, 0.9))
	Sfx.play("kill")
	if invader.drops_atp and invader.data.atp_drop > 0:
		atp_dropped.emit(invader.data.atp_drop, to_global(invader.position))
	if invader.data.split_into:
		spawn_from(invader, invader.data.split_into, invader.data.split_count)
	# Spreading poison jumps to everyone nearby when its carrier dies.
	if invader.poison_time > 0.0 and invader.poison_spreads:
		for other in invaders:
			if other.position.distance_to(invader.position) <= POISON_SPREAD_RANGE * TILE:
				other.apply_poison(invader.poison_dps, invader.poison_time, true)
	invader.queue_free()


## A bomber's payload: full damage on the target tile, half on the 8 around.
func bomb(cell: Vector2i, damage: float) -> void:
	Sfx.play("bomb", 0.1)
	shake_requested.emit(4.0)
	fx.add_puff(cell_center(cell), Color(1, 0.6, 0.2))
	fx.add_pulse(cell_center(cell), TILE * 1.6, Color(1, 0.55, 0.15))
	fx.add_pulse(cell_center(cell), TILE * 0.8, Color(1, 0.9, 0.4))
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			var unit := intact_unit_at(cell + Vector2i(dx, dy))
			if unit:
				unit.take_damage(damage if dx == 0 and dy == 0 else damage * BOMB_SPLASH)


## A spiller's goo: every unit on the 8 tiles around `cell` gets sticky and
## attacks slower until the units are repaired after the wave.
func spill(cell: Vector2i, slow: float) -> void:
	fx.add_puff(cell_center(cell), SPILL_COLOR)
	var hit_any := false
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			var unit := intact_unit_at(cell + Vector2i(dx, dy))
			if unit:
				unit.make_sticky(slow)
				hit_any = true
	if hit_any:
		Sfx.play("spill", 0.15)


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
			var texture: Texture2D = _tiles.floor
			if sea_spawn_cells.has(cell):
				texture = biome.sea_spawn_texture
			elif water.has(cell):
				texture = biome.water_texture
			elif rocks.has(cell):
				texture = _tiles.rock
			elif spawn_cells.has(cell):
				texture = _tiles.spawn
			elif cell == base_cell:
				texture = _tiles.base
			draw_texture(texture, Vector2(cell * TILE))

	if show_path_preview:
		for spawn in spawn_cells:
			if preview_fliers:
				draw_dashed_line(cell_center(spawn), cell_center(base_cell), FLIER_PATH_COLOR, 1.0, 3.0)
			if preview_smashers:
				_draw_path(smasher_path(spawn), SMASHER_PATH_COLOR)
			if preview_jumpers:
				_draw_path(jumper_path(spawn), JUMPER_PATH_COLOR)
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
