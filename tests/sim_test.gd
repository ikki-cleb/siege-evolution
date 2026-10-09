extends SceneTree
## Automated playtest. Plays levels without a screen, as fast as possible,
## and checks the rules work. Run from the project folder:
##   godot --headless --fixed-fps 60 --script tests/sim_test.gd
##
## Prints PASS/FAIL lines and exits with code 1 if anything failed.

const MAIN_SCENE := "res://scenes/main.tscn"
const GameScript := preload("res://scripts/game/game.gd")

var failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	await _test_rules()
	await _test_level(0, [], false, "Level 1, no defenses")
	await _test_level(0, LEVEL_1_PLAN, true, "Level 1, bot plan")
	await _test_level(1, [], false, "Level 2, no defenses")
	await _test_level(1, LEVEL_2_PLAN, true, "Level 2, bot plan")
	print("\n%s" % ("ALL TESTS PASSED" if failures == 0 else "%d TEST(S) FAILED" % failures))
	quit(1 if failures > 0 else 0)


# A simple "player": every build phase it tries each placement in order,
# skipping ones it can't afford, that are already built, or that are illegal.
const LEVEL_1_PLAN := [
	# Worm kill zone: a clot in the smasher lane with neutrophils on its corners.
	["clot", 4, 4], ["neutrophil", 3, 4], ["neutrophil", 5, 4],
	["membrane", 0, 4], ["membrane", 1, 4], ["membrane", 2, 4], ["membrane", 6, 4],
	["b_cell", 6, 5], ["membrane", 7, 4],
	["neutrophil", 6, 7], ["b_cell", 5, 6],
	["membrane", 8, 10], ["membrane", 7, 10], ["membrane", 6, 10], ["membrane", 5, 10],
	["membrane", 4, 10], ["membrane", 3, 10], ["membrane", 2, 10], ["membrane", 1, 10],
	["neutrophil", 1, 9], ["b_cell", 3, 12], ["neutrophil", 3, 9], ["b_cell", 5, 12],
]

const LEVEL_2_PLAN := [
	# Kill zone for worms from the left spawn, flier defense near the base.
	["clot", 1, 2], ["neutrophil", 0, 2], ["neutrophil", 2, 2],
	["b_cell", 2, 12], ["b_cell", 3, 8],
	# Serpentine: row 6 open only at x=1, row 9 open only at x=7..8.
	["membrane", 2, 6], ["membrane", 3, 6], ["membrane", 4, 6], ["membrane", 5, 6],
	["membrane", 6, 6], ["membrane", 7, 6], ["membrane", 8, 6], ["membrane", 0, 6],
	["membrane", 0, 9], ["membrane", 1, 9], ["membrane", 2, 9], ["membrane", 3, 9],
	["membrane", 4, 9], ["membrane", 5, 9], ["membrane", 6, 9],
	# Kill zone for worms from the right spawn.
	["clot", 8, 2], ["neutrophil", 7, 2], ["neutrophil", 7, 1],
	["b_cell", 0, 11], ["neutrophil", 2, 7], ["b_cell", 6, 10], ["neutrophil", 8, 10],
]


func _start_level(index: int) -> Node:
	GameScript.level_index = index
	var game: Node = load(MAIN_SCENE).instantiate()
	root.add_child(game)
	await process_frame
	return game


func _unit_type(game: Node, id: String) -> UnitData:
	for type in game.unit_types:
		if type.id == id:
			return type
	return null


func _place(game: Node, id: String, cell: Vector2i) -> bool:
	var type := _unit_type(game, id)
	var before: int = game.board.units.size()
	game.selected_type = null
	game.select_type(type)
	game._on_cell_tapped(cell)
	return game.board.units.size() > before


func _test_level(index: int, plan: Array, expect_win: bool, label: String) -> void:
	var game := await _start_level(index)
	var frames := 0
	var lowest_hp: int = game.base_hp
	var log := []
	var leaks := {}
	game.board.base_hit.connect(func(inv): leaks[inv.id] = leaks.get(inv.id, 0) + 1)
	while game.phase != game.Phase.WON and game.phase != game.Phase.LOST:
		if game.phase == game.Phase.BUILD:
			for step in plan:
				var cell := Vector2i(step[1], step[2])
				if not game.board.units.has(cell):
					_place(game, step[0], cell)
			log.append("w%d:%dhp/%du" % [game.wave_number + 1, game.base_hp, game.board.units.size()])
			game.start_wave()
		await process_frame
		frames += 1
		if frames > 60 * 60 * 30:
			break
	var won: bool = game.phase == game.Phase.WON
	_check(won == expect_win, "%s: %s with %d/%d base HP after %d waves (%.0fs game time)" % [
		label, "WON" if won else "LOST", game.base_hp, game.level.base_hp, game.wave_number, frames / 60.0])
	print("      ", " ".join(log))
	print("      leaked: ", leaks)
	game.queue_free()
	await process_frame


func _test_rules() -> void:
	var game := await _start_level(0)
	var board: Board = game.board

	# Sealing the path must be refused. Row 1 is fully open, 9 tiles wide.
	game.atp = 999
	for x in 8:
		_place(game, "membrane", Vector2i(x, 1))
	var sealed := _place(game, "membrane", Vector2i(8, 1))
	_check(not sealed and not board.walker_path(board.spawn_cells[0]).is_empty(),
		"Placement that would seal the path is refused")

	# The 6 free membranes went on x=0..5, so x=6 and x=7 were bought with ATP.
	# Undoing the last one should remove it and refund its 4 ATP.
	var atp_before: int = game.atp
	game.undo()
	_check(not board.units.has(Vector2i(7, 1)) and game.atp == atp_before + 4,
		"Undo removes the last placed unit and refunds its ATP")
	# Undo twice more: x=6 (bought) and x=5 (free, goes back to the hand).
	game.undo()
	game.undo()
	_check(game.hand["membrane"] == 1 and game.atp == atp_before + 8,
		"Undo returns free units to the hand")

	# Selling refunds 75%, and undoing the sale takes it back.
	game._on_cell_tapped(Vector2i(0, 1))
	var atp_pre_sell: int = game.atp
	game.sell_selected()
	_check(game.atp == atp_pre_sell + 3 and not board.units.has(Vector2i(0, 1)),
		"Selling a 4 ATP membrane refunds 3 ATP")
	game.undo()
	_check(game.atp == atp_pre_sell and board.units.has(Vector2i(0, 1)),
		"Undoing a sale restores the unit and takes the ATP back")

	# Damaged and destroyed units are fully restored between waves.
	var unit: Unit = board.units[Vector2i(0, 1)]
	unit.take_damage(999)
	var other: Unit = board.units[Vector2i(1, 1)]
	other.take_damage(5)
	_check(unit.destroyed, "A unit can be destroyed")
	game.start_wave()
	while game.phase == game.Phase.WAVE:
		await process_frame
	_check(not unit.destroyed and unit.hp == unit.data.max_hp and other.hp == other.data.max_hp,
		"Units are fully repaired between waves")
	_check(not game.can_undo(), "Undo history is cleared once a wave starts")

	game.queue_free()
	await process_frame


func _check(ok: bool, text: String) -> void:
	print("%s  %s" % ["PASS" if ok else "FAIL", text])
	if not ok:
		failures += 1
