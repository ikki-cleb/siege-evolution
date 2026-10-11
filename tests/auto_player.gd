class_name AutoPlayer
extends RefCounted
## A simple, reasonably competent player for automated balance testing.
## Each build phase it spends everything it can:
##   - walls go where they lengthen the invaders' route the most,
##   - attackers go where they cover the most route (plus smasher lanes and
##     flier lines when those invaders appear in the level),
##   - leftover coins go into evolutions.
## It doesn't plan ahead like a person would, so a level it beats with every
## pack should be fair; a level it loses badly may be too hard.

var game
var board: Board
var rng := RandomNumberGenerator.new()
var _has_smashers := false
var _has_fliers := false
var _has_jumpers := false
## A flying boss needs several anti-air units, not just one.
var _has_flying_boss := false
var _boat_cells := {}  # water tiles boats use, for coverage scoring
var _flier_points: Array[Vector2] = []
## Points along a flying boss's flight line (from its marked spawn tile).
## Like a player who sees the skull marker, the bot covers this line first.
var _boss_flier_points: Array[Vector2] = []
## Coins kept back when buying a capstone, so the bot still builds.
const CAPSTONE_RESERVE := 10


func _init(p_game, seed_value := 1) -> void:
	game = p_game
	board = game.board
	rng.seed = seed_value
	for wave in game.level.waves:
		for entry in wave.entries:
			_has_smashers = _has_smashers or entry.invader.movement == InvaderData.Movement.SMASHER
			_has_fliers = _has_fliers or entry.invader.movement == InvaderData.Movement.FLIER
			_has_jumpers = _has_jumpers or entry.invader.jumps
			_has_flying_boss = _has_flying_boss or (entry.invader.is_boss and entry.invader.movement == InvaderData.Movement.FLIER)
	for wave in game.level.waves:
		for entry in wave.entries:
			if entry.invader.naval:
				for spawn in board.sea_spawn_cells:
					for cell in board.route_for(entry.invader, spawn):
						_boat_cells[cell] = 1
	for wave in game.level.waves:
		for entry in wave.entries:
			if entry.invader.is_boss and entry.invader.movement == InvaderData.Movement.FLIER:
				for spawn in game._boss_spawn_cells(wave):
					_boss_flier_points.append_array(_line_points(spawn))
	for spawn in board.spawn_cells:
		var from := board.cell_center(spawn)
		var to := board.base_center()
		var steps := int(from.distance_to(to) / (Board.TILE * 0.5))
		for i in steps:
			_flier_points.append(from.lerp(to, float(i) / steps))


## Points every half tile on the straight line from a spawn to the base.
func _line_points(spawn: Vector2i) -> Array[Vector2]:
	var points: Array[Vector2] = []
	var from := board.cell_center(spawn)
	var to := board.base_center()
	var steps := int(from.distance_to(to) / (Board.TILE * 0.5))
	for i in steps:
		points.append(from.lerp(to, float(i) / steps))
	return points


## Spends coins and free units until nothing more is worth doing.
func build_phase() -> void:
	for i in 80:
		if not _take_action():
			break


func _take_action() -> bool:
	var wall_count := 0
	var fighter_count := 0
	for cell in board.units:
		if board.units[cell].base_data.role == UnitData.Role.WALL:
			wall_count += 1
		else:
			fighter_count += 1
	if fighter_count >= 4 and rng.randf() < 0.3 and _evolve():
		return true
	var want_wall := wall_count < fighter_count * 1.5 + 2
	if want_wall and _place_wall():
		return true
	if _place_fighter():
		return true
	if not want_wall and _place_wall():
		return true
	return _evolve()


func _affordable(type: UnitData) -> bool:
	return game.hand.get(type.id, 0) > 0 or game.coins >= type.cost


## Free units first, then whichever affordable type we've spent least on.
func _choose_type(candidates: Array[UnitData]) -> UnitData:
	var best: UnitData = null
	var best_score := INF
	for type in candidates:
		if not _affordable(type):
			continue
		if game.hand.get(type.id, 0) > 0:
			return type
		var spent := 0.0
		for cell in board.units:
			if board.units[cell].base_data == type:
				spent += type.cost
		# Without enough anti-air yet, strongly prefer units that hit fliers.
		if _has_fliers and type.hits_air and _anti_air_count() < (5 if _has_flying_boss else 1):
			spent -= 1000.0
		if spent < best_score:
			best_score = spent
			best = type
	return best


func _anti_air_count() -> int:
	var count := 0
	for cell in board.units:
		if board.units[cell].data.hits_air and board.units[cell].data.can_attack():
			count += 1
	return count


func _types(walls: bool) -> Array[UnitData]:
	var result: Array[UnitData] = []
	for type in game.unit_types:
		if (type.role == UnitData.Role.WALL) == walls:
			result.append(type)
	return result


func _place_wall() -> bool:
	var type := _choose_type(_types(true))
	if type == null:
		return false
	var current_paths := _routes_if_blocked(Board.NO_CELL)
	var current_length := _total_length(current_paths)
	var current_cover := _path_cover(current_paths)
	var on_path := _walker_cells()
	var best := Board.NO_CELL
	var best_score := -INF
	for y in board.grid_size.y:
		for x in board.grid_size.x:
			var cell := Vector2i(x, y)
			if not board.is_buildable(cell):
				continue
			var paths := _routes_if_blocked(cell)
			if paths.is_empty():
				continue
			var gain := _total_length(paths) - current_length
			# How much of the new route our attackers can still reach.
			var cover_gain := _path_cover(paths) - current_cover
			var touches_path := on_path.has(cell)
			if gain <= 0 and cover_gain <= 0 and not touches_path:
				continue
			if cover_gain < 0.0:
				continue  # Never lead the route away from our attackers.
			# Prefer longer routes past our attackers, then extending lines.
			var score := gain * 4.0 + cover_gain * 6.0 + _solid_neighbors(cell) \
				+ (2.0 if touches_path else 0.0) + rng.randf()
			if score > best_score:
				best_score = score
				best = cell
	return best != Board.NO_CELL and game.try_place(type, best)


## Walker routes if a unit stood here, plus jumper routes when the level has
## jumpers (so thin walls that deer just hop over don't look useful).
func _routes_if_blocked(cell: Vector2i) -> Array:
	var paths := board.walker_paths_if_blocked(cell)
	if paths.is_empty() or not _has_jumpers:
		return paths
	return paths + board.jumper_paths_if_blocked(cell)


## Route length in steps (a hop counts as two tiles).
func _total_length(paths: Array) -> int:
	var total := 0
	for path in paths:
		total += path.size()
	return total


## Sum over every route tile of how many of our attackers can reach it.
func _path_cover(paths: Array) -> float:
	var fighters: Array[Unit] = []
	for cell in board.units:
		var unit: Unit = board.units[cell]
		if unit.data.can_attack() and unit.data.role != UnitData.Role.WALL:
			fighters.append(unit)
	var cover := 0.0
	for path in paths:
		for cell in path:
			var center := board.cell_center(cell)
			for unit in fighters:
				if unit.position.distance_to(center) <= unit.data.attack_range * Board.TILE:
					cover += 1.0
	return cover


func _place_fighter() -> bool:
	var type := _choose_type(_types(false))
	if type == null:
		return false
	var current_cover := _path_cover(_routes_if_blocked(Board.NO_CELL))
	var best := Board.NO_CELL
	var best_score := 0.0
	for y in board.grid_size.y:
		for x in board.grid_size.x:
			var cell := Vector2i(x, y)
			if not board.is_buildable(cell):
				continue
			# The unit blocks its own tile, so judge it by the route AFTER placing it.
			var paths := _routes_if_blocked(cell)
			if paths.is_empty():
				continue
			var walker := {}
			for path in paths:
				for path_cell in path:
					walker[path_cell] = walker.get(path_cell, 0) + 1
			var smasher := _smasher_cells() if _has_smashers else {}
			var score := _coverage(cell, type, walker, smasher) + rng.randf() * 0.5
			# Penalize moving the route away from attackers already placed.
			score += min(0.0, _path_cover(paths) - current_cover)
			score += type.adjacency_bonus * 10.0 * board.neighbor_count(cell)
			if score > best_score:
				best_score = score
				best = cell
	return best != Board.NO_CELL and game.try_place(type, best)


func _evolve() -> bool:
	var best: Unit = null
	for cell in board.units:
		var unit: Unit = board.units[cell]
		if unit.data.evolutions.is_empty() or not game.is_ready_to_evolve(unit):
			continue
		if unit.base_data.role == UnitData.Role.WALL and not _has_smashers:
			continue
		# First evolutions before capstones, then the priciest unit.
		if best == null or unit.data.tier < best.data.tier \
				or (unit.data.tier == best.data.tier and unit.base_data.cost > best.base_data.cost):
			best = unit
	if best == null:
		return false
	var into: UnitData = best.data.evolutions[rng.randi() % best.data.evolutions.size()]
	# Capstones only with coins to spare (it keeps a little for new units).
	var reserve := CAPSTONE_RESERVE if into.tier == 2 else 0
	if game.coins < into.cost + reserve:
		return false
	game._select_cell(best.cell)
	game.evolve_selected(into)
	game._select_cell(Board.NO_CELL)
	return best.data == into


func _coverage(cell: Vector2i, type: UnitData, walker: Dictionary, smasher: Dictionary) -> float:
	var center := board.cell_center(cell)
	var reach := type.attack_range * Board.TILE
	var score := 0.0
	for path_cell in walker:
		if center.distance_to(board.cell_center(path_cell)) <= reach:
			score += walker[path_cell]
	for path_cell in smasher:
		if center.distance_to(board.cell_center(path_cell)) <= reach:
			score += 1.0
	for path_cell in _boat_cells:
		if center.distance_to(board.cell_center(path_cell)) <= reach:
			score += 1.0
	if type.hits_air:
		for point in _flier_points:
			if center.distance_to(point) <= reach:
				score += 0.5
		for point in _boss_flier_points:
			if center.distance_to(point) <= reach:
				score += 2.0
	return score


## Tiles on any walker route, with how many routes use them.
func _walker_cells() -> Dictionary:
	var cells := {}
	for spawn in board.spawn_cells:
		for cell in board.walker_path(spawn):
			cells[cell] = cells.get(cell, 0) + 1
	return cells


func _smasher_cells() -> Dictionary:
	var cells := {}
	for spawn in board.spawn_cells:
		for cell in board.smasher_path(spawn):
			cells[cell] = 1
	return cells


func _solid_neighbors(cell: Vector2i) -> int:
	var count := 0
	for offset in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
		var next: Vector2i = cell + offset
		if not board.is_inside(next) or board.rocks.has(next) or board.units.has(next):
			count += 1
	return count
