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
## If scripts fail to compile, checks silently never run; catch that too.
var checks_run := 0
const MIN_RULE_CHECKS := 48
var progress: Node


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	progress = root.get_node("Progress")
	var biome: BiomeData = progress.load_biome(0)
	await _test_rules(biome)
	await _test_burrowing(progress.load_biome(1))
	await _test_jumping(progress.load_biome(2))
	await _test_sea_and_bombs(progress.load_biome(3))
	await _test_space(progress.load_biome(4))
	await _test_kitchen(progress.load_biome(5))
	if not OS.get_cmdline_user_args().has("rules"):
		# "-- world=2" balances just one world (0-based index; 5 = Kitchen).
		var worlds := [0, 1, 2, 3, 4, 5]
		for arg in OS.get_cmdline_user_args():
			if arg.begins_with("world="):
				worlds = [int(arg.split("=")[1])]
		for index in worlds:
			await _test_balance(progress.load_biome(index))
	progress.reset()
	if checks_run < MIN_RULE_CHECKS:
		print("FAIL  Only %d checks ran (expected at least %d). Look for SCRIPT ERROR above." % [checks_run, MIN_RULE_CHECKS])
		failures += 1
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


# --- Jumping ----------------------------------------------------------------

func _test_jumping(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 0)  # Cornfield: spawn (4,0), base (4,13)
	var board: Board = game.board
	var wall: UnitData = game.unit_types[0]
	# A one-tile-thick wall across row 3, with a gap at the far left edge.
	for x in range(1, 9):
		board.place_unit(wall, Vector2i(x, 3))
	var route := board.jumper_path(board.spawn_cells[0])
	_check(_has_hop(route) and route.size() < board.walker_path(board.spawn_cells[0]).size(),
		"Jumpers hop a one-tile wall instead of walking around it")
	# Make it two tiles thick: no more hopping.
	for x in range(1, 9):
		board.place_unit(wall, Vector2i(x, 4))
	route = board.jumper_path(board.spawn_cells[0])
	_check(not _has_hop(route), "Walls two tiles thick stop jumpers")
	for x in range(1, 9):
		board.remove_unit(Vector2i(x, 4))

	# A real deer actually makes the hop and keeps going.
	board.wave_active = true
	var deer_data: InvaderData = load("res://data/invaders/wild_kingdom/deer.tres")
	board.spawn_invader(deer_data, 0)
	var deer: Invader = board.invaders[0]
	var crossed := false
	for i in 60 * 20:
		await process_frame
		if not is_instance_valid(deer) or not deer.alive:
			break
		if deer.position.y > board.cell_center(Vector2i(4, 4)).y - 1 and deer.position.x > 20:
			crossed = true
			break
	_check(crossed, "A deer hops the wall and continues toward the base")
	await _stop(game)


# --- Water lanes and bombers -------------------------------------------------

func _test_sea_and_bombs(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 1)  # Bathtub Beach (sea level)
	var board: Board = game.board
	var wall: UnitData = game.unit_types[0]
	var fighter: UnitData = game.unit_types[1]
	game.atp = 999
	_check(not game.try_place(fighter, Vector2i(4, 4)), "Attackers can't be placed on water")
	_check(game.try_place(wall, Vector2i(5, 2)), "The basic wall can be placed on water (as a net)")
	_check(not game.try_place(wall, Vector2i(4, 2)), "A net can't seal a water lane")
	var boat_data: InvaderData = load("res://data/invaders/total_war/patrol_boat.tres")
	var route := board.route_for(boat_data, board.sea_spawn_cells[0])
	var all_water := route.all(func(cell): return board.water.has(cell) or cell == board.base_cell)
	_check(not route.is_empty() and all_water and not route.has(Vector2i(5, 2)),
		"Boats stay on water and steer around nets")
	var soldier: InvaderData = load("res://data/invaders/total_war/toy_soldier.tres")
	var land_route := board.route_for(soldier, board.spawn_cells[0])
	_check(not land_route.any(func(cell): return board.water.has(cell)), "Land troops never walk on water")
	await _stop(game)

	# A bomber hits the most valuable unit near its flight line.
	game = await _start(biome, 0, 0)  # Sandbox
	board = game.board
	wall = game.unit_types[0]
	fighter = game.unit_types[1]
	var cheap := board.place_unit(wall, Vector2i(4, 4))
	var pricey := board.place_unit(fighter, Vector2i(4, 5))
	board.wave_active = true
	board.spawn_invader(load("res://data/invaders/total_war/toy_bomber.tres"), 0)
	for i in 60 * 15:
		await process_frame
		if pricey.hp < pricey.data.max_hp or pricey.destroyed:
			break
	_check(pricey.destroyed or pricey.hp < pricey.data.max_hp, "Bombers target the most valuable unit nearby")
	_check(cheap.hp < cheap.data.max_hp or cheap.destroyed, "The blast also damages neighboring units")
	await _stop(game)


# --- Teleporters and the Mothership ------------------------------------------

func _test_space(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 0)  # Moon Landing
	var board: Board = game.board
	board.wave_active = true
	board.spawn_invader(load("res://data/invaders/galactic_siege/blinker.tres"), 0)
	var blinker: Invader = board.invaders[0]
	var last := blinker.path_index
	var jumped := false
	for i in 60 * 6:
		await process_frame
		if not is_instance_valid(blinker) or not blinker.alive:
			break
		if blinker.path_index - last >= 3:
			jumped = true
			break
		last = blinker.path_index
	_check(jumped, "Blinkers teleport several tiles forward along their route")
	await _stop(game)

	game = await _start(biome, 0, 6)  # Mothership level
	board = game.board
	var wall: UnitData = game.unit_types[0]
	for x in [2, 4, 6]:
		for y in [3, 6, 9, 11]:
			if board.is_buildable(Vector2i(x, y)):
				board.place_unit(wall, Vector2i(x, y))
	var bombs := [0]
	board.wave_active = true
	var boss_data: InvaderData = load("res://data/invaders/galactic_siege/mothership.tres")
	board.spawn_invader(boss_data, 0)
	var boss: Invader = board.invaders[0]
	var minion_routes_ok := true
	var hp_total := func():
		var total := 0.0
		for cell in board.units:
			total += board.units[cell].hp
		return total
	var hp_before: float = hp_total.call()
	for i in 60 * 40:
		await process_frame
		for invader in board.invaders:
			if invader != boss and invader.path.is_empty():
				minion_routes_ok = false
	_check(board.invaders.size() > 1 and minion_routes_ok, "The Mothership drops blinkers that walk a real route")
	_check(hp_total.call() < hp_before - boss_data.bomb_damage, "The Mothership bombs more than once")
	await _stop(game)

	# The final victory screen: big congratulations, plus a bonus-world pitch
	# only when the player doesn't own both bonus worlds.
	var store: Node = root.get_node("Store")
	for owned in [false, true]:
		store.reset_test_purchases()
		if owned:
			store.buy(store.BUNDLE_ALL)
		game = await _start(biome, 0, 6)
		game.hud.show_end_screen(true)
		await process_frame
		var texts := _all_texts(game.hud)
		var has_pitch := texts.any(func(t): return t.contains("See bonus worlds"))
		_check(texts.has("VICTORY!") and has_pitch == not owned,
			"Final victory screen %s the bonus worlds" % ("hides" if owned else "suggests"))
		await _stop(game)
	store.reset_test_purchases()


# --- Kitchen Defense: spillers and the bonus world-cleared screen -------------

func _test_kitchen(biome: BiomeData) -> void:
	# Pantry Raid: spawn (4,0), base (4,13); the route runs down column 4.
	var game := await _start(biome, 0, 0)
	var board: Board = game.board
	var attacker: UnitData = game.unit_types[1]
	var beside_left: Unit = board.place_unit(attacker, Vector2i(3, 2))
	var beside_right: Unit = board.place_unit(attacker, Vector2i(5, 2))
	var far_away: Unit = board.place_unit(attacker, Vector2i(0, 12))
	board.wave_active = true
	var slug_data: InvaderData = load("res://data/invaders/kitchen_defense/slug.tres")
	board.spawn_invader(slug_data, 0)
	var slug: Invader = board.invaders[0]
	slug.hp = 100000.0  # Keep it alive so it walks past the units.
	for i in 60 * 10:
		await process_frame
	_check(beside_left.sticky > 0.0 or beside_right.sticky > 0.0,
		"Slugs slime the units beside their route")
	_check(far_away.sticky == 0.0, "Units away from the route stay clean")
	board.restore_units()
	_check(beside_left.sticky == 0.0 and beside_right.sticky == 0.0, "The free repair after a wave washes the goo off")
	await _stop(game)

	# Sticky units attack 40% slower: compare the wait after one attack.
	game = await _start(biome, 0, 0)
	board = game.board
	var clean: Unit = board.place_unit(attacker, Vector2i(0, 6))
	var gooey: Unit = board.place_unit(attacker, Vector2i(8, 6))
	gooey.make_sticky(slug_data.spill_slow)
	board.wave_active = true
	for x in [0, 8]:
		var ant: Invader = board._add_invader(load("res://data/invaders/kitchen_defense/sugar_ant.tres"),
			board.cell_center(Vector2i(x, 7)), [Vector2i(x, 7)] as Array[Vector2i], 0)
		ant.hp = 100000.0
		ant.set_process(false)
	clean._process(0.0)
	gooey._process(0.0)
	_check(is_equal_approx(gooey._cooldown, clean._cooldown / (1.0 - slug_data.spill_slow)),
		"Sticky units attack 40%% slower (%.2fs vs %.2fs)" % [gooey._cooldown, clean._cooldown])
	await _stop(game)

	# Beating the Rat King shows a world-cleared screen that suggests the
	# other bonus world, but never the one just beaten.
	var store: Node = root.get_node("Store")
	store.reset_test_purchases()
	store.buy(store.WORLD_KITCHEN)
	game = await _start(biome, 0, 6)
	game.hud.show_end_screen(true)
	await process_frame
	var texts := _all_texts(game.hud)
	_check(texts.has("Kitchen Defense cleared!") and texts.any(func(t): return t.contains("Birthday Bash"))
		and not texts.any(func(t): return t.contains(": Kitchen Defense")),
		"Kitchen Defense shows its own world-cleared screen")
	await _stop(game)
	store.reset_test_purchases()
	_check(store.product(store.WORLD_KITCHEN).get("warning", "") == "POST-GAME: HARD",
		"The store warns that Kitchen Defense is post-game hard")


## Every Label and Button text under a node (for checking screens).
func _all_texts(node: Node) -> Array[String]:
	var result: Array[String] = []
	for child in node.get_children():
		if child is Label or child is Button:
			result.append(child.text)
		result.append_array(_all_texts(child))
	return result


func _has_hop(route: Array[Vector2i]) -> bool:
	for i in range(1, route.size()):
		if (route[i] - route[i - 1]).length() > 1.5:
			return true
	return false


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
	checks_run += 1
	print("%s  %s" % ["PASS" if ok else "FAIL", text])
	if not ok:
		failures += 1
