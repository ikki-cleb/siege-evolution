extends SceneTree
## Automated playtest. Plays levels without a screen, as fast as possible.
## Run from the project folder:
##   godot --headless --fixed-fps 60 --script tests/sim_test.gd          (rules + balance)
##   godot --headless --fixed-fps 60 --script tests/sim_test.gd -- rules (rules only)
##
## Prints PASS/FAIL lines plus a balance table (base HP left for each pack on
## each level) and exits with code 1 if anything failed.

const GAME_SCENE := "res://scenes/game.tscn"

var failures := 0
var progress: Node


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	progress = root.get_node("Progress")
	var biome: BiomeData = progress.load_biome(0)
	await _test_rules(biome)
	await _test_burrowing(progress.load_biome(1))
	if not OS.get_cmdline_user_args().has("rules"):
		for index in [0, 1]:
			await _test_balance(progress.load_biome(index))
	progress.reset()
	print("\n%s" % ("ALL TESTS PASSED" if failures == 0 else "%d TEST(S) FAILED" % failures))
	quit(1 if failures > 0 else 0)


func _start(biome: BiomeData, pack_index: int, level_index: int) -> Node:
	progress.biome = biome
	progress.pack = biome.packs[pack_index]
	progress.level_index = level_index
	var game: Node = load(GAME_SCENE).instantiate()
	root.add_child(game)
	await process_frame
	return game


## Plays a level to the end. If `player` is null, nothing is ever built.
func _play(game: Node, player: AutoPlayer) -> void:
	var wave_frames := 0
	while game.phase != game.Phase.WON and game.phase != game.Phase.LOST:
		if game.phase == game.Phase.BUILD:
			if player:
				player.build_phase()
			game.start_wave()
			wave_frames = 0
		await process_frame
		wave_frames += 1
		if wave_frames > 60 * 60 * 4:
			_check(false, "Wave %d of %s never ended (stalemate?)" % [game.wave_number, game.level.display_name])
			return


func _stop(game: Node) -> void:
	game.queue_free()
	await process_frame


# --- Balance ----------------------------------------------------------------

func _test_balance(biome: BiomeData) -> void:
	print("\nBalance: base HP left (of 20) when the auto-player plays each pack. Two runs per cell; 'L8' = lost on wave 8.")
	var header := "%-22s" % "Level"
	for pack in biome.packs:
		header += "%11s" % pack.display_name
	print(header)
	var pack_wins := {}
	for level_index in biome.levels.size():
		var row := "%-22s" % biome.levels[level_index].display_name
		for pack_index in biome.packs.size():
			# Two runs with different random seeds, to smooth out luck.
			var results: Array[String] = []
			var wins := 0
			for seed_value in [7, 99]:
				var game := await _start(biome, pack_index, level_index)
				await _play(game, AutoPlayer.new(game, seed_value + level_index))
				if game.phase == game.Phase.WON:
					wins += 1
					results.append(str(game.base_hp))
				else:
					results.append("L%d" % game.wave_number)
				await _stop(game)
			row += "%11s" % "/".join(results)
			if wins >= 1:
				pack_wins[pack_index] = pack_wins.get(pack_index, 0) + 1
		print(row)

	for level_index in [0, 1]:
		var game := await _start(biome, 0, level_index)
		await _play(game, null)
		_check(game.phase == game.Phase.LOST, "%s is lost with no defenses (wave %d)" % [
			biome.levels[level_index].display_name, game.wave_number])
		await _stop(game)
	for pack_index in biome.packs.size():
		_check(pack_wins.get(pack_index, 0) >= biome.levels.size() - 1,
			"%s pack beats at least %d of %d levels" % [biome.packs[pack_index].display_name,
			biome.levels.size() - 1, biome.levels.size()])


# --- Burrowing --------------------------------------------------------------

func _test_burrowing(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 0)
	var board: Board = game.board
	board.wave_active = true
	var data: InvaderData = load("res://data/invaders/backyard_bugs/mole_cricket.tres")
	board.spawn_invader(data, 0)
	var cricket: Invader = board.invaders[0]
	var went_under := false
	var hit_while_under := true
	var max_index := 0
	for i in 60 * 30:
		await process_frame
		if not is_instance_valid(cricket) or not cricket.alive:
			break
		if cricket.underground and not went_under:
			went_under = true
			var hp_before := cricket.hp
			# Nothing should be able to target it now.
			var tester: Unit = board.place_unit(game.unit_types[1], Vector2i(0, 13))
			hit_while_under = tester._can_target(cricket)
			board.remove_unit(Vector2i(0, 13))
		max_index = max(max_index, cricket.path_index)
		if went_under and not cricket.underground:
			break
	_check(went_under, "Mole Crickets burrow after walking a few tiles")
	_check(not hit_while_under, "Underground invaders can't be targeted")
	_check(max_index >= data.burrow_after + data.burrow_length,
		"Burrowers resurface further along their route (tile %d)" % max_index)
	await _stop(game)


# --- Rules ------------------------------------------------------------------

func _test_rules(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 0)  # Fortress, level 1
	var board: Board = game.board
	var wall: UnitData = game.unit_types[0]
	var fighter: UnitData = game.unit_types[1]

	_check(game.unit_types.size() == 3, "Level 1 offers the pack's first 3 units")
	var expected_walls := maxi(1, roundi(float(game.level.hand_value[0]) / wall.cost))
	_check(game.hand.get(wall.id, 0) == expected_walls,
		"Starting hand converts ATP value into copies (%d ATP of %d-ATP walls = %d)" % [game.level.hand_value[0], wall.cost, expected_walls])

	# Sealing the path must be refused. Row 1 is fully open, 9 tiles wide.
	game.atp = 999
	for x in 8:
		game.try_place(wall, Vector2i(x, 1))
	_check(not game.try_place(wall, Vector2i(8, 1)) and not board.walker_path(board.spawn_cells[0]).is_empty(),
		"Placement that would seal the path is refused")

	# Same-round refunds: free units go back to the hand, bought units refund fully.
	game._select_cell(Vector2i(0, 1))  # first wall came from the hand
	game.sell_selected()
	_check(game.hand[wall.id] == 1, "Removing a free unit placed this round returns it to the hand")
	var atp_before: int = game.atp
	game._select_cell(Vector2i(7, 1))  # bought with ATP
	game.sell_selected()
	_check(game.atp == atp_before + wall.cost, "Removing a bought unit placed this round refunds 100%")

	# A unit can't evolve in the round it was placed.
	game.try_place(fighter, Vector2i(4, 5))
	game._select_cell(Vector2i(4, 5))
	var evo: UnitData = fighter.evolutions[0]
	_check(not game.can_evolve(evo), "A unit can't evolve in the round it was placed")
	var unit: Unit = board.units[Vector2i(4, 5)]

	# Damage a wall and destroy another, then play a wave.
	var damaged: Unit = board.units[Vector2i(1, 1)]
	damaged.take_damage(5)
	var broken: Unit = board.units[Vector2i(2, 1)]
	broken.take_damage(9999)
	_check(broken.destroyed, "A unit can be destroyed")
	var drops := [0]
	board.atp_dropped.connect(func(amount, _where): drops[0] += amount)
	var leaks := [0]
	board.base_hit.connect(func(_inv): leaks[0] += 1)
	atp_before = game.atp
	game.start_wave()
	while game.phase == game.Phase.WAVE:
		await process_frame
	_check(not broken.destroyed and broken.hp == broken.data.max_hp and damaged.hp == damaged.data.max_hp,
		"Units are fully repaired between waves")
	var bonus: int = game.level.atp_per_wave if leaks[0] == 0 else 0
	_check(drops[0] > 0 and game.atp == atp_before + drops[0] + bonus,
		"Kills drop ATP (%d dropped, %d leaks, bonus %d)" % [drops[0], leaks[0], bonus])

	# After surviving a wave it can evolve, which costs ATP.
	game.atp = 999
	game._select_cell(Vector2i(4, 5))
	game.evolve_selected(evo)
	_check(unit.data == evo and game.atp == 999 - evo.cost, "A veteran unit evolves, costing ATP")
	_check(not game.can_evolve(fighter.evolutions[1]), "An evolved unit can't evolve again")

	# Older unit refunds 50%; the evolution bought this round refunds 100%.
	var value: Dictionary = game.sell_value(unit)
	_check(value.atp == int(fighter.cost * 0.5) + evo.cost and not value.to_hand,
		"Old unit refunds 50%, plus 100% of an evolution bought this round")
	value = game.sell_value(board.units[Vector2i(1, 1)])
	_check(value.atp == int(wall.cost * 0.5) and not value.to_hand,
		"Free units from earlier rounds refund 50% of their cost in ATP")
	await _stop(game)

	# Store gating.
	var store: Node = root.get_node("Store")
	store.reset_test_purchases()
	game = await _start(biome, 0, 0)
	game.cycle_speed()
	game.cycle_speed()
	_check(game.speed == 1, "3x speed is skipped until it's bought")
	store.buy(store.SPEED_3X)
	game.cycle_speed()
	game.cycle_speed()
	_check(game.speed == 3, "3x speed works once bought")
	game.cycle_speed()
	await _stop(game)
	var toxin: PackData = biome.find_pack("toxin")
	_check(not store.owns(toxin.product_id) and store.owns(biome.find_pack("fortress").product_id),
		"Toxin is locked and Fortress is free")
	store.buy(store.BUNDLE_ALL)
	_check(store.owns(toxin.product_id) and store.owns(store.WORLD_BIRTHDAY) and progress.is_biome_unlocked(6),
		"The bundle unlocks every item, including bonus worlds")
	store.reset_test_purchases()

	# Unit effects, checked directly on a board.
	game = await _start(biome, 2, 0)  # Precision
	board = game.board
	var invader_data: InvaderData = load("res://data/invaders/immune_system/biofilm.tres")
	board.spawn_invader(invader_data, 0)
	var target: Invader = board.invaders[0]
	target.take_damage(5)
	_check(is_equal_approx(target.hp, invader_data.max_hp - 3), "Armor 2 reduces a 5-damage hit to 3")
	target.take_damage(5, true)
	_check(is_equal_approx(target.hp, invader_data.max_hp - 8), "Piercing hits ignore armor")
	target.apply_mark(0.5, 2.0)
	var hp_before := target.hp
	target.take_damage(6, true)
	_check(is_equal_approx(target.hp, hp_before - 9), "Marked invaders take extra damage")
	target.apply_slow(0.5, 1.0)
	target.apply_slow(0.2, 1.0)
	_check(is_equal_approx(target.slow_amount, 0.5), "A weaker slow doesn't replace a stronger one")
	target.apply_poison(4.0, 2.0, true)
	board.spawn_invader(load("res://data/invaders/immune_system/rhinovirus.tres"), 0)
	var neighbor: Invader = board.invaders[1]
	neighbor.position = target.position
	target.take_damage(999, true)
	_check(neighbor.poison_time > 0.0, "Spreading poison jumps to nearby invaders on death")
	await _stop(game)

	# Reflect and boss minions.
	game = await _start(biome, 0, 6)  # Fortress, level 7
	board = game.board
	var spike: UnitData = game.unit_types[0].evolutions[1]
	var spike_unit: Unit = board.place_unit(spike, Vector2i(4, 6))
	board.spawn_invader(load("res://data/invaders/immune_system/worm.tres"), 0)
	var worm: Invader = board.invaders[0]
	spike_unit.take_damage(10, worm)
	_check(is_equal_approx(worm.hp, worm.data.max_hp - 10 * spike.reflect), "Reflect bounces smasher damage back")
	board.wave_active = true
	var boss_data: InvaderData = load("res://data/invaders/immune_system/superbug.tres")
	board.spawn_invader(boss_data, 0)
	var count_before := board.invaders.size()
	for i in int(60 * (boss_data.minion_interval + 1.0)):
		await process_frame
	_check(board.invaders.size() > count_before, "The boss releases minions while it walks")
	await _stop(game)


func _check(ok: bool, text: String) -> void:
	print("%s  %s" % ["PASS" if ok else "FAIL", text])
	if not ok:
		failures += 1
