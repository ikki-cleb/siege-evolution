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
## Emitted when a killed invader drops coins. `where` is in screen coordinates.
signal coins_dropped(amount: int, where: Vector2)
## A relic carrier was killed (the game then offers a relic after the wave).
signal relic_dropped(where: Vector2)
## A relic carrier reached the base: that relic is lost.
signal relic_lost
## Emitted for every invader killed (achievements count them).
signal invader_killed(invader: Invader)
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
## The boss's route (shown before the boss wave) is purple and thicker.
## Very faint grey lines between tiles (build phase only).
const GRID_COLOR := Color(0.85, 0.85, 0.85, 0.16)
## After a placement changes a route, the new route flashes this color.
const ROUTE_FLASH_COLOR := Color(1.0, 0.95, 0.6)
const ROUTE_FLASH_TIME := 0.7
const BOSS_PATH_COLOR := Color(0.75, 0.4, 1.0, 0.9)
const BOSS_PATH_WIDTH := 2.5
## Seconds a bomb takes to fall. Its target tile shows a warning meanwhile.
const BOMB_FALL_TIME := 0.9
## A bomb's full damage hits its target; the 8 tiles around take this share.
const BOMB_SPLASH := 0.5
## Goo left by spillers (Kitchen Defense).
const SPILL_COLOR := Color(0.85, 0.6, 0.2)
## The flash when a piñata bursts (Birthday Bash).
const PINATA_COLOR := Color(1.0, 0.45, 0.8)
## Capstone explosions reach this far (tiles).
const EXPLODE_RADIUS := 1.5
## Lingering zones: size (tiles), how long they last, and their colors.
const ZONE_RADIUS := 1.0
const ZONE_TIME := 3.0
const ZONE_COLORS := {"burn": Color(1.0, 0.45, 0.15), "freeze": Color(0.55, 0.85, 1.0), "toxic": Color(0.5, 0.95, 0.3)}

var grid_size := Vector2i.ZERO
var rocks := {}  # Vector2i -> true
## Land spawn points ("S").
var spawn_cells: Array[Vector2i] = []
## Sea spawn points for boats ("N").
var sea_spawn_cells: Array[Vector2i] = []
var water := {}  # Vector2i -> true
## The base is 3 tiles wide and 2 tall. `base_cell` is the "B" in the level
## layout (bottom middle of the block); routes are aimed at it, but an
## invader arrives as soon as it steps onto any tile in `base_cells`.
var base_cell := NO_CELL
var base_cells: Array[Vector2i] = []
const BASE_SIZE := Vector2i(3, 2)
## 0-1, set by the game: the base shows cracks as it loses health.
## Draws the big base sprite (see BaseView).
var base_view: BaseView
## Relics picked this level (they boost units; see RelicSet).
var relics := RelicSet.new()

var units := {}  # Vector2i -> Unit
var invaders: Array[Invader] = []

## True while a wave is running. Units only act during waves.
var wave_active := false
## Lingering zones on the ground: {pos, kind, power, time, owner}.
var zones: Array[Dictionary] = []
# Piñata surprises (see start_pinata_seeds).
var _pinata_seed_base := 0
var _pinatas_spawned := 0
var _pinatas_tossed := 0

# Two pathfinding grids. Walkers treat units as walls; smashers only avoid
# rocks, because they plan to chew straight through any unit in the way.
var _walk_grid := AStarGrid2D.new()
var _smash_grid := AStarGrid2D.new()
# Boats get the same pair, but only water (and the base) is open to them.
var _boat_grid := AStarGrid2D.new()
var _boat_smash_grid := AStarGrid2D.new()

# What the board draws on top of the tiles (set by the game).
var show_path_preview := false
## Faint gridlines over the board while the player is building.
var show_grid := false
## Routes that just changed (lists of cells) and how long they still flash.
var _route_flash: Array = []
var _route_flash_time := 0.0
var preview_smashers := false
var preview_fliers := false
var preview_jumpers := false
## The boss coming in the next wave (null if none) and the spawn tiles it
## uses. Its route is drawn in purple.
var preview_boss: InvaderData = null
var preview_boss_spawns: Array[Vector2i] = []
## Bombs on their way down: {target, damage, time}. They hit when time runs out.
## Glow + skull on the boss's spawn tiles (see show_boss_spawns).
var boss_marker: BossMarker
var _falling_bombs: Array[Dictionary] = []
var selected_cell := NO_CELL
## While an upgrade is being previewed: its range, drawn as a gold circle
## around the selected unit (0 = no preview).
var preview_range := 0.0

## A tile treated as blocked while testing "what if a unit stood here?".
var _pretend_unit := NO_CELL

var _flash_cell := NO_CELL
var _flash_time := 0.0

## Draws shots and pulses above units and invaders.
var fx: ShotEffects
## Effects that sit on the ground, under units and invaders.
var ground_fx: ShotEffects
## Tile art comes from the world (biome) being played, unless the level
## has its own.
var biome: BiomeData
var _tiles := {}
## True when the level has a painted background instead of floor tiles.
var _has_background := false


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
	_make_base_block()
	_add_spawners()

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
			var sea_blocked := not water.has(cell) and not base_cells.has(cell)
			_boat_grid.set_point_solid(cell, sea_blocked)
			_boat_smash_grid.set_point_solid(cell, sea_blocked)

	if level.background:
		_add_background(level.background)
	boss_marker = BossMarker.new()
	add_child(boss_marker)
	# Effects on the ground (burrow holes, splashes): drawn under units and
	# invaders, because they're added before any of them.
	ground_fx = ShotEffects.new()
	add_child(ground_fx)
	_add_base_view()
	fx = ShotEffects.new()
	fx.z_index = 10
	add_child(fx)
	queue_redraw()


## A painted ground image for the whole board, shrunk smoothly to fit
## (drawn behind everything; the board then skips its floor tiles).
func _add_background(texture: Texture2D) -> void:
	# Smooth shrinking needs mipmaps (smaller copies of the image).
	var image := texture.get_image()
	if image.is_compressed():
		image.decompress()
	image.generate_mipmaps()
	var sprite := Sprite2D.new()
	sprite.texture = ImageTexture.create_from_image(image)
	sprite.centered = false
	sprite.scale = Vector2(grid_size * TILE) / Vector2(image.get_size())
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	sprite.z_index = -1  # behind the board's own tiles
	add_child(sprite)
	_has_background = true
	# On painted ground, use the see-through rock/spawn/base tiles (made by
	# tools/make_cutout_tiles.py) so they don't show squares of floor color.
	for key in ["rock", "spawn", "base"]:
		_tiles[key] = _cutout(_tiles[key])


## Animated spawners (tools/draw_spawners.py) on the spawn tiles. Where a
## world has one, the still spawn tile isn't drawn.
var _animated_spawns := {}


func _add_spawners() -> void:
	var land := SpawnerView.strip_for(_tiles.spawn)
	var sea := SpawnerView.strip_for(biome.sea_spawn_texture, true)
	for cell in spawn_cells:
		if land:
			add_child(SpawnerView.new().setup(land, cell))
			_animated_spawns[cell] = true
	for cell in sea_spawn_cells:
		if sea:
			add_child(SpawnerView.new().setup(sea, cell))
			_animated_spawns[cell] = true


## The see-through "_cut" version of a tile, or the tile itself if there is none.
func _cutout(texture: Texture2D) -> Texture2D:
	if texture == null:
		return null
	var path := texture.resource_path.replace(".png", "_cut.png")
	return load(path) if ResourceLoader.exists(path) else texture


# --- Grid helpers -----------------------------------------------------------

func cell_center(cell: Vector2i) -> Vector2:
	return Vector2(cell * TILE) + Vector2(TILE, TILE) / 2.0


func is_inside(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < grid_size.x and cell.y < grid_size.y


## Grows the base from its "B" tile into a 3x2 block: centered on B and
## reaching up from the bottom edge (down from the top edge), shifted inward
## at the sides. Whatever the layout had on those tiles becomes base.
func _make_base_block() -> void:
	base_cells.clear()
	if base_cell == NO_CELL:
		return
	var left := clampi(base_cell.x - 1, 0, grid_size.x - BASE_SIZE.x)
	var top := base_cell.y - (BASE_SIZE.y - 1) if base_cell.y > 0 else base_cell.y
	for y in range(top, top + BASE_SIZE.y):
		for x in range(left, left + BASE_SIZE.x):
			var cell := Vector2i(x, y)
			base_cells.append(cell)
			rocks.erase(cell)
			water.erase(cell)


## The big base sprite over the base tiles, sticking up into the row above.
func _add_base_view() -> void:
	base_view = BaseView.new()
	var path := "res://art/tiles/%s/base_big.png" % biome.id
	base_view.texture = load(path) if ResourceLoader.exists(path) else _tiles.base
	var top_left := Vector2(base_cells[0] * TILE) if not base_cells.is_empty() else Vector2(base_cell * TILE)
	var block := Vector2(BASE_SIZE * TILE)
	# The art is 96x80 for a 96x64 block (2x pixel density): 8 board pixels
	# of headroom above the tiles.
	var headroom := block.x * 80.0 / 96.0 - block.y
	base_view.area = Rect2(top_left - Vector2(0, headroom), Vector2(block.x, block.y + headroom))
	add_child(base_view)


## Called by the game when an invader reaches the base.
func hit_base(health: float) -> void:
	base_view.health = health
	base_view.hit()


## Updates the base's cracks without the hit flash (e.g. after healing).
func set_base_health(health: float) -> void:
	base_view.health = health
	base_view.queue_redraw()


func is_base(cell: Vector2i) -> bool:
	return base_cells.has(cell)


## The middle of the base block (where fliers and bombers head).
func base_center() -> Vector2:
	var total := Vector2.ZERO
	for cell in base_cells:
		total += cell_center(cell)
	return total / base_cells.size() if not base_cells.is_empty() else cell_center(base_cell)


## A route cut off at the first base tile it touches (that's where an
## invader arrives).
func _trim_to_base(path: Array[Vector2i]) -> Array[Vector2i]:
	for i in path.size():
		if is_base(path[i]):
			return path.slice(0, i + 1)
	return path


## True if the tile is open land floor with nothing on it.
func is_buildable(cell: Vector2i) -> bool:
	return (is_inside(cell) and not rocks.has(cell) and not units.has(cell) and not water.has(cell)
		and not is_base(cell) and not spawn_cells.has(cell))


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
		var path := _trim_to_base(_boat_grid.get_id_path(spawn, base_cell))
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
		var path := _trim_to_base(_walk_grid.get_id_path(spawn, base_cell))
		if path.is_empty():
			paths.clear()
			break
		paths.append(path)
	if pretend:
		_walk_grid.set_point_solid(cell, was_solid)
	return paths


## The route a walking invader takes from `from_cell` to the base.
func walker_path(from_cell: Vector2i) -> Array[Vector2i]:
	return _trim_to_base(_walk_grid.get_id_path(from_cell, base_cell))


## The route a smasher takes: shortest path that only avoids rocks.
func smasher_path(from_cell: Vector2i) -> Array[Vector2i]:
	return _trim_to_base(_smash_grid.get_id_path(from_cell, base_cell))


## The route a jumper takes: like a walker's, but it may hop over a single
## unit tile to the open tile beyond. Consecutive tiles in the result that
## are 2 apart are hops. (A small Dijkstra search; the grid is tiny.)
func jumper_path(from_cell: Vector2i) -> Array[Vector2i]:
	var cost_so_far := {from_cell: 0}
	var came_from := {}
	var reached := NO_CELL
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
		if is_base(cell):
			reached = cell
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
	if reached == NO_CELL:
		return path
	var cell := reached
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
		return _trim_to_base(grid.get_id_path(from_cell, base_cell))
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
	var routes_before := _walker_routes()
	var unit := Unit.new()
	unit.setup(data, cell, self)
	add_child(unit)
	units[cell] = unit
	_blocking_grid(cell).set_point_solid(cell, true)
	_flash_changed_routes(routes_before)
	queue_redraw()
	return unit


## Every spawn's walking route right now.
func _walker_routes() -> Array:
	var routes := []
	for spawn in spawn_cells:
		routes.append(walker_path(spawn))
	return routes


## Makes any route that a placement just changed flash for a moment, so the
## player sees their unit push the maze around.
func _flash_changed_routes(routes_before: Array) -> void:
	var routes_after := _walker_routes()
	_route_flash.clear()
	for i in routes_after.size():
		if routes_after[i] != routes_before[i]:
			_route_flash.append(routes_after[i])
	if not _route_flash.is_empty():
		_route_flash_time = ROUTE_FLASH_TIME


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


## The best aura each kind of capstone around `cell` gives it:
## {"speed": attack speed bonus, "shield": damage reduction, "cleanse": goo-proof}.
func aura_at(cell: Vector2i) -> Dictionary:
	var aura := {"speed": 0.0, "shield": 0.0, "cleanse": false}
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			if dx == 0 and dy == 0:
				continue
			var neighbor := intact_unit_at(cell + Vector2i(dx, dy))
			if neighbor == null:
				continue
			aura.speed = maxf(aura.speed, neighbor.data.aura_speed)
			aura.shield = maxf(aura.shield, neighbor.data.aura_shield)
			aura.cleanse = aura.cleanse or neighbor.data.aura_cleanse
	return aura


## "Explode on break": a destroyed capstone blasts the invaders around it
## (and leaves its zone behind, if it has one).
func explode(pos: Vector2, damage: float, unit_data: UnitData) -> void:
	Sfx.play("bomb", 0.1)
	shake_requested.emit(2.0)
	fx.add_puff(pos, Color(1, 0.7, 0.3))
	fx.add_pulse(pos, TILE * EXPLODE_RADIUS, Color(1, 0.6, 0.2))
	for invader in invaders.duplicate():
		if invader.alive and not invader.underground and invader.position.distance_to(pos) <= EXPLODE_RADIUS * TILE:
			invader.take_damage(damage, true)
	if unit_data.zone_kind != "":
		add_zone(pos, unit_data, null)


## Adds a lingering patch (or refreshes the one this unit already has there).
func add_zone(pos: Vector2, unit_data: UnitData, owner: Node) -> void:
	for zone in zones:
		if zone.owner == owner and owner != null and zone.pos.distance_to(pos) < TILE * 0.5:
			zone.time = ZONE_TIME
			return
	zones.append({"pos": pos, "kind": unit_data.zone_kind, "power": unit_data.zone_power,
		"time": ZONE_TIME, "owner": owner})
	queue_redraw()


## Zones hurt, slow or poison the ground invaders standing in them.
func _update_zones(delta: float) -> void:
	for zone in zones:
		zone.time -= delta
		for invader in invaders.duplicate():
			if not invader.alive or invader.underground or invader.is_flying():
				continue
			if invader.position.distance_to(zone.pos) > ZONE_RADIUS * TILE:
				continue
			match zone.kind:
				"burn":
					invader.take_damage(zone.power * delta, true, false)
				"freeze":
					invader.apply_slow(zone.power, 0.3)
				"toxic":
					# Re-dose only when the last dose is running out, so it doesn't stack up.
					if invader.poison_time < 1.0:
						invader.apply_poison(zone.power, 2.0, false)
	zones = zones.filter(func(zone): return zone.time > 0.0)
	queue_redraw()


## Between waves: every unit is repaired to full, even destroyed ones.
func restore_units() -> void:
	zones.clear()
	queue_redraw()
	for cell in units:
		units[cell].restore()
		_blocking_grid(cell).set_point_solid(cell, true)


# --- Invaders ---------------------------------------------------------------

func spawn_invader(data: InvaderData, spawn_index: int) -> Invader:
	# Boats start at sea spawns; fliers use land spawns, or sea ones if a
	# level has no land spawns.
	var start := spawn_cell_for(data, spawn_index)
	var invader := _add_invader(data, cell_center(start), route_for(data, start), 0)
	if not data.pinata_pool.is_empty():
		# The 1st, 2nd, 3rd... piñata of the wave always gets the same seed.
		invader.pinata_seed = _pinata_seed_base + _pinatas_spawned
		_pinatas_spawned += 1
	return invader


## Called at the start of each wave. Piñata surprises come from this seed,
## so replaying the same level and wave gives the same surprises.
func start_pinata_seeds(seed_text: String) -> void:
	_pinata_seed_base = seed_text.hash()
	_pinatas_spawned = 0
	_pinatas_tossed = 0


## Breaks a piñata open: picks its surprise from its seed.
func _burst_pinata(pinata: Invader) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = pinata.pinata_seed
	var pool := pinata.data.pinata_pool
	var count := rng.randi_range(pinata.data.pinata_min, pinata.data.pinata_max)
	fx.add_pulse(pinata.position, TILE * 1.2, PINATA_COLOR)
	Sfx.play("pinata", 0.1)
	for i in count:
		spawn_from(pinata, pool[rng.randi() % pool.size()], 1, pinata.drops_coins)


## Adds invaders at another invader's position, following its route
## (used for splitting and for boss minions).
## `ahead` > 0 lands them that many tiles further along the parent's route.
func spawn_from(parent: Invader, data: InvaderData, count: int, drops_coins := true, ahead := 0) -> void:
	# Where along the parent's route they start.
	var from_index := parent.path_index
	var start := parent.position
	if ahead > 0 and parent.path.size() >= 2 and parent.path_index < parent.path.size():
		from_index = mini(parent.path_index + ahead, parent.path.size() - 2)
		start = cell_center(parent.path[from_index])
	for i in count:
		# Nudge them apart a little so they don't overlap exactly.
		var nudge := Vector2(randf_range(-3, 3), randf_range(-3, 3))
		var path: Array[Vector2i] = []
		var index := 0
		if parent.is_flying() and not data.movement == InvaderData.Movement.FLIER:
			# Dropped from a flier: start walking from the open tile below it
			# (or the first spawn if it's over a rock).
			var below := Vector2i((parent.position / TILE).floor())
			path = route_for(data, below if _is_open(below) or is_base(below) else spawn_cells[0])
		elif data.movement == InvaderData.Movement.PATHER and from_index < parent.path.size():
			# Walkers need their own kind of route, even if the parent was a smasher.
			path = route_for(data, parent.path[from_index])
		elif data.movement != InvaderData.Movement.FLIER:
			path = parent.path.duplicate()
			index = from_index
		var invader := _add_invader(data, start + nudge, path, index)
		invader.drops_coins = drops_coins
		# The new piece visibly flies out of its parent to its spot.
		invader.toss_in(parent.position)
		if not data.pinata_pool.is_empty():
			# Tossed piñatas get their own numbering, so their surprises don't
			# depend on how they interleave with the wave's own piñatas.
			invader.pinata_seed = _pinata_seed_base + 100000 + _pinatas_tossed
			_pinatas_tossed += 1


func _add_invader(data: InvaderData, pos: Vector2, path: Array[Vector2i], path_index: int) -> Invader:
	var invader := Invader.new()
	invader.setup(data, self, pos, path, path_index)
	add_child(invader)
	invaders.append(invader)
	return invader


func on_invader_killed(invader: Invader) -> void:
	invaders.erase(invader)
	invader_killed.emit(invader)
	if invader.data.anim_death:
		_play_death(invader)
	else:
		fx.add_puff(invader.position, Color(1, 1, 1, 0.9))
	Sfx.play("kill")
	if invader.drops_coins and invader.data.coin_drop > 0:
		coins_dropped.emit(invader.data.coin_drop, to_global(invader.position))
	# Bounty capstones pay extra for the invaders they finish off.
	var hitter = invader.last_hitter
	if invader.drops_coins and is_instance_valid(hitter) and hitter.data.bounty > 0:
		coins_dropped.emit(hitter.data.bounty, to_global(invader.position))
	# Relic carriers drop their relic.
	if invader.carries_relic:
		relic_dropped.emit(invader.position)
	if invader.data.split_into:
		spawn_from(invader, invader.data.split_into, invader.data.split_count)
	if not invader.data.pinata_pool.is_empty():
		_burst_pinata(invader)
	# Spreading poison jumps to everyone nearby when its carrier dies.
	if invader.poison_time > 0.0 and invader.poison_spreads:
		for other in invaders:
			if other.position.distance_to(invader.position) <= POISON_SPREAD_RANGE * TILE:
				other.apply_poison(invader.poison_dps, invader.poison_time, true)
	invader.queue_free()


## An invader's death animation, played once where it died (the invader
## itself is removed right away).
func _play_death(invader: Invader) -> void:
	var strip := invader.data.anim_death
	var sprite := Sprite2D.new()
	sprite.position = invader.position
	sprite.z_index = 4
	var size := (1.75 if invader.data.is_boss else 1.0) * TILE / strip.get_height()
	sprite.scale = Vector2(size, size)
	var player := StripPlayer.new()
	sprite.add_child(player)
	add_child(sprite)
	player.finished.connect(sprite.queue_free)
	player.play_once(sprite, strip)


## Marks the tiles the boss will come from (empty on non-boss levels).
func show_boss_spawns(cells: Array[Vector2i]) -> void:
	boss_marker.spots.clear()
	for cell in cells:
		boss_marker.spots.append(cell_center(cell))
	boss_marker.queue_redraw()


## Which tile an invader starts on for a wave entry's spawn index.
func spawn_cell_for(data: InvaderData, spawn_index: int) -> Vector2i:
	var spawns := sea_spawn_cells if data.naval or spawn_cells.is_empty() else spawn_cells
	return spawns[spawn_index % spawns.size()]


## A bomber lets go of a bomb: it falls from `from` onto `cell` (with a
## warning on the target tile) and explodes when it lands.
func drop_bomb(from: Vector2, cell: Vector2i, damage: float) -> void:
	_falling_bombs.append({"target": cell, "damage": damage, "time": BOMB_FALL_TIME})
	fx.add_falling_bomb(from, cell_center(cell), BOMB_FALL_TIME)


## True while a bomb is still falling (the wave isn't over until it lands).
func has_falling_bombs() -> bool:
	return not _falling_bombs.is_empty()


func _update_falling_bombs(delta: float) -> void:
	for falling in _falling_bombs:
		falling.time -= delta
	var landed := _falling_bombs.filter(func(falling): return falling.time <= 0.0)
	_falling_bombs = _falling_bombs.filter(func(falling): return falling.time > 0.0)
	for falling in landed:
		bomb(falling.target, falling.damage)


## A bomb landing: full damage on the target tile, half on the 8 around.
func bomb(cell: Vector2i, damage: float) -> void:
	Sfx.play("bomb", 0.1)
	shake_requested.emit(4.0)
	fx.add_explosion(cell_center(cell), TILE * 1.5)
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
				# A blob of goo flies from the spiller onto the unit.
				fx.add_lob(cell_center(cell), unit.position, SPILL_COLOR)
				unit.make_sticky(slow)
				hit_any = true
	if hit_any:
		Sfx.play("spill", 0.15)


func on_invader_reached_base(invader: Invader) -> void:
	invaders.erase(invader)
	invader.queue_free()
	if invader.carries_relic:
		relic_lost.emit()
	base_hit.emit(invader.data)


# --- Feedback ---------------------------------------------------------------

## Briefly flashes a tile red, e.g. when a placement isn't allowed.
func flash(cell: Vector2i) -> void:
	_flash_cell = cell
	_flash_time = 0.4
	queue_redraw()


func _process(delta: float) -> void:
	if wave_active and not zones.is_empty():
		_update_zones(delta)
	if not _falling_bombs.is_empty():
		_update_falling_bombs(delta)
	if _flash_time > 0.0:
		_flash_time -= delta
		queue_redraw()
	if _route_flash_time > 0.0:
		_route_flash_time -= delta
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
			var texture: Texture2D = null if _has_background else _tiles.floor
			if sea_spawn_cells.has(cell):
				# Under an animated drain, plain water.
				texture = biome.water_texture if _animated_spawns.has(cell) else biome.sea_spawn_texture
			elif water.has(cell):
				texture = biome.water_texture
			elif rocks.has(cell):
				texture = _tiles.rock
			elif spawn_cells.has(cell) and not _animated_spawns.has(cell):
				texture = _tiles.spawn
			if texture:
				draw_texture(texture, Vector2(cell * TILE))

	if show_grid:
		_draw_grid()

	if show_path_preview:
		for spawn in spawn_cells:
			if preview_fliers:
				draw_dashed_line(cell_center(spawn), base_center(), FLIER_PATH_COLOR, 1.0, 3.0)
			if preview_smashers:
				_draw_path(smasher_path(spawn), SMASHER_PATH_COLOR)
			if preview_jumpers:
				_draw_path(jumper_path(spawn), JUMPER_PATH_COLOR)
			_draw_path(walker_path(spawn), PATH_COLOR)
	# A route that just changed: drawn bright and thick, then fading out.
	if _route_flash_time > 0.0:
		var fade := _route_flash_time / ROUTE_FLASH_TIME
		for route in _route_flash:
			_draw_path(route, Color(ROUTE_FLASH_COLOR, 0.9 * fade), 1.0 + 1.5 * fade)
	# The boss's route goes on top so it's never hidden. It shows even with
	# the Paths toggle off: players should always see what the boss will do.
	if preview_boss:
		for spawn in preview_boss_spawns:
			if preview_boss.movement == InvaderData.Movement.FLIER:
				draw_dashed_line(cell_center(spawn), base_center(), BOSS_PATH_COLOR, BOSS_PATH_WIDTH, 4.0)
			else:
				_draw_path(route_for(preview_boss, spawn), BOSS_PATH_COLOR, BOSS_PATH_WIDTH)

	for zone in zones:
		var color: Color = ZONE_COLORS.get(zone.kind, Color.WHITE)
		var fade := clampf(zone.time / ZONE_TIME, 0.0, 1.0)
		draw_circle(zone.pos, ZONE_RADIUS * TILE, Color(color, 0.22 * fade))
		draw_arc(zone.pos, ZONE_RADIUS * TILE, 0, TAU, 24, Color(color, 0.5 * fade), 1.0)

	if selected_cell != NO_CELL:
		draw_rect(Rect2(Vector2(selected_cell * TILE), Vector2(TILE, TILE)), Color.WHITE, false, 1.0)
		var unit: Unit = units.get(selected_cell)
		if unit and unit.data.can_attack():
			draw_arc(cell_center(selected_cell), unit.stat("attack_range") * TILE, 0, TAU, 48, Color(1, 1, 1, 0.6), 1.0)
		if preview_range > 0.0:
			draw_arc(cell_center(selected_cell), preview_range * TILE, 0, TAU, 48, Color(Palette.GOLD, 0.9), 1.5)

	if _flash_time > 0.0:
		draw_rect(Rect2(Vector2(_flash_cell * TILE), Vector2(TILE, TILE)), Color(1, 0, 0, _flash_time))


## Thin lines between all tiles, so it's easy to see where a unit will go.
func _draw_grid() -> void:
	var board_size := Vector2(grid_size * TILE)
	for x in range(1, grid_size.x):
		draw_line(Vector2(x * TILE, 0), Vector2(x * TILE, board_size.y), GRID_COLOR, 0.5)
	for y in range(1, grid_size.y):
		draw_line(Vector2(0, y * TILE), Vector2(board_size.x, y * TILE), GRID_COLOR, 0.5)


func _draw_path(path: Array[Vector2i], color: Color, width := 1.0) -> void:
	if path.size() < 2:
		return
	var points := PackedVector2Array()
	for cell in path:
		points.append(cell_center(cell))
	draw_polyline(points, color, width)
