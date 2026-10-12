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
const MIN_RULE_CHECKS := 168
var progress: Node


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	progress = root.get_node("Progress")
	var biome: BiomeData = progress.load_biome(2)  # Microscopic (World 3)
	await _test_rules(biome)
	await _test_burrowing(progress.load_biome(0))
	await _test_jumping(progress.load_biome(1))
	await _test_sea_and_bombs(progress.load_biome(3))
	await _test_space(progress.load_biome(4))
	await _test_bosses(biome)
	await _test_base_block()
	await _test_relics(progress.load_biome(2))
	await _test_kitchen(progress.load_biome(5))
	await _test_selection(biome)
	await _test_party(progress.load_biome(6))
	await _test_capstones(biome)
	await _test_upgrade_preview(biome)
	await _test_menu_scrolling()
	await _test_menu_pizazz()
	_test_level_counts()
	await _test_path_toggle(biome)
	await _test_pack_swapping(biome)
	await _test_achievements(biome)
	await _test_background(biome)
	await _test_endless(progress.load_biome(0))
	await _test_animations(biome)
	if not OS.get_cmdline_user_args().has("rules"):
		# "-- world=2" balances just one world (0-based index: 0 = Backyard Bugs,
		# 1 = Wild Kingdom, 2 = Microscopic, 3 = Total War, 4 = Galactic Siege,
		# 5 = Kitchen, 6 = Birthday).
		var worlds := [0, 1, 2, 3, 4, 5, 6]
		for arg in OS.get_cmdline_user_args():
			if arg.begins_with("world="):
				worlds = [int(arg.split("=")[1])]
		for index in worlds:
			if OS.get_cmdline_user_args().has("endless"):
				await _test_endless_reach(progress.load_biome(index))
			else:
				await _test_balance(progress.load_biome(index))
	progress.reset()
	root.get_node("Achievements").reset()
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
			elif not game.relic_offer.is_empty():
				game.pick_relic(0)
			game.start_wave()
			wave_frames = 0
		await process_frame
		wave_frames += 1
		if wave_frames > 60 * 60 * 4:
			_check(false, "Wave %d of %s never ended (stalemate?)" % [game.wave_number, game.level.display_name])
			for invader in game.board.invaders:  # what's still alive, for debugging
				print("    still alive: %s at %s, hp %.0f/%.0f, underground %s" % [invader.data.id,
					game.board.cell_of(invader.position) if game.board.has_method("cell_of") else invader.position,
					invader.hp, invader.full_hp, invader.underground])
			print("    spawns left: %d, bombs falling: %s" % [game._spawn_queue.size(), game.board.has_falling_bombs()])
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
	var runs_won := 0
	var runs := 0
	for level_index in biome.levels.size():
		var row := "%-22s" % biome.levels[level_index].display_name
		for pack_index in biome.packs.size():
			# Two runs with different random seeds, to smooth out luck.
			var results: Array[String] = []
			var wins := 0
			for seed_value in [7, 99]:
				var game := await _start(biome, pack_index, level_index)
				await _play(game, AutoPlayer.new(game, seed_value + level_index))
				# The teaching level (level 1) doesn't count toward the win rate.
				if level_index > 0:
					runs += 1
				if game.phase == game.Phase.WON:
					wins += 1
					if level_index > 0:
						runs_won += 1
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
	# Bonus worlds are post-game hard: the bot should win about 70% of runs,
	# and every pack should still beat 3 of 5 levels (4 of 5 in main worlds).
	print("Bot won %d of %d runs on levels 2-%d (%d%%)" % [runs_won, runs, biome.levels.size(),
		roundi(100.0 * runs_won / runs)])
	var needed := biome.levels.size() - (2 if progress.is_bonus_biome(biome.id) else 1)
	for pack_index in biome.packs.size():
		_check(pack_wins.get(pack_index, 0) >= needed,
			"%s pack beats at least %d of %d levels" % [biome.packs[pack_index].display_name,
			needed, biome.levels.size()])


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
	game.coins = 999
	_check(not game.try_place(fighter, Vector2i(4, 4)), "Attackers can't be placed on water")
	_check(game.try_place(wall, Vector2i(5, 2)), "The basic wall can be placed on water (as a net)")
	_check(not game.try_place(wall, Vector2i(4, 2)), "A net can't seal a water lane")
	var boat_data: InvaderData = load("res://data/invaders/total_war/patrol_boat.tres")
	var route := board.route_for(boat_data, board.sea_spawn_cells[0])
	var all_water := route.all(func(cell): return board.water.has(cell) or board.is_base(cell))
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

	game = await _start(biome, 0, 4)  # Mothership level
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
		game = await _start(biome, 0, 4)
		game.hud.show_end_screen(true)
		await process_frame
		var texts := _all_texts(game.hud)
		var has_pitch := texts.any(func(t): return t.contains("See bonus worlds"))
		_check(texts.has("VICTORY!") and has_pitch == not owned,
			"Final victory screen %s the bonus worlds" % ("hides" if owned else "suggests"))
		await _stop(game)
	store.reset_test_purchases()


# --- Bosses: instant loss, spawn marker, purple route; bombs fall -------------

## The base is a 3x2 block: not buildable, routes end on it, and in every
## level it fits on the board without covering a spawn.
func _test_base_block() -> void:
	var ok := true
	for index in progress.WORLDS.size():
		var world: BiomeData = progress.load_biome(index)
		for level_index in world.levels.size():
			var level: LevelData = world.levels[level_index]
			var board := Board.new()
			root.add_child(board)
			board.setup(level, world)
			var fits := board.base_cells.size() == 6
			for cell in board.base_cells:
				fits = fits and board.is_inside(cell) and not board.spawn_cells.has(cell) \
					and not board.sea_spawn_cells.has(cell) and not board.is_buildable(cell)
			for spawn in board.spawn_cells:
				for route in [board.walker_path(spawn), board.smasher_path(spawn), board.jumper_path(spawn)]:
					fits = fits and not route.is_empty() and board.is_base(route[-1]) \
						and not board.is_base_side(route[-1])
			if not fits:
				print("  base block problem: %s level %d" % [world.id, level_index + 1])
			ok = ok and fits
			board.queue_free()
	await process_frame
	_check(ok, "The 3x2 base fits every level, can't be built on, and every route ends in its middle column")


# --- Relics -------------------------------------------------------------------

const RELIC_STATS := ["damage", "attack_range", "fire_rate", "max_hp", "regen", "reflect",
	"splash_radius", "slow", "slow_duration", "stun_duration", "poison_dps", "poison_duration",
	"mark_bonus", "mark_duration", "chain_count", "multishot", "knockback", "armor_shred",
	"execute_below", "adjacency_bonus", "crit", "boss_damage", "flier_damage", "armored_damage",
	"wall_buddy_damage", "wall_buddy_rate", "wall_slow", "wall_burn",
	# Archetype relics (rare/epic build-arounds).
	"wall_buddy_range", "wall_mark", "no_wall_damage", "walked_damage", "ground_damage",
	"vs_slowed", "vs_stunned", "vs_poisoned", "per_status_damage", "clean_target_damage",
	"damage_per_neighbor", "cluster_damage", "cluster_rate", "small_group_damage",
	"lonely_damage", "evolved_damage", "evolved_rate", "evolved_range", "unevolved_damage"]
const RELIC_ABILITIES := ["pierce", "hits_air", "poison_spreads", "rebuild"]
const RELIC_ECONOMY := ["kill_coins", "wave_coins", "clean_bonus_mult", "evolve_discount",
	"refund_old", "base_heal", "gift_coins", "free_walls", "interest",
	"wall_discount", "wall_refund", "unit_markup", "wave_walls"]
const RELIC_FILTERS := ["all", "attackers", "walls", "anti_air", "ground_only", "single", "pulse",
	"splash", "slow", "stun", "poison", "mark", "swarm", "regen", "reflect", "chain", "multishot",
	"knockback", "long_range", "short_range", "economy"]


func _test_relics(biome: BiomeData) -> void:
	# Every relic in the pool uses names the code understands (catches typos).
	var pool := RelicSet.pool()
	var valid := pool.size() >= 60
	var ids := {}
	for relic in pool:
		var ok: bool = RelicSet.RARITY_ORDER.has(relic.rarity) and RELIC_FILTERS.has(relic.filter) \
			and RelicIcon.has_art(relic.id) and not ids.has(relic.id)
		for key in relic.get("mult", {}).keys() + relic.get("add", {}).keys():
			ok = ok and RELIC_STATS.has(key)
		for ability in relic.get("grant", []):
			ok = ok and RELIC_ABILITIES.has(ability)
		for key in relic.get("economy", {}).keys():
			ok = ok and RELIC_ECONOMY.has(key)
		if not ok:
			print("  bad relic: %s" % relic.id)
		valid = valid and ok
		ids[relic.id] = true
	_check(valid, "The relic pool has 60+ relics, all with known stats, filters and icons")

	# Relics are on every level, teaching levels too.
	var game := await _start(biome, 0, 0)
	game.start_wave()
	_check(game._spawn_queue.filter(func(spawn): return spawn.get("carrier", false)).size() == 1,
		"Teaching levels have a relic carrier on wave 1 too")
	await _stop(game)

	# Wave 1 of level 2 has a glowing carrier; killing it earns a relic.
	game = await _start(biome, 0, 1)
	var board: Board = game.board
	game.start_wave()
	_check(game._spawn_queue.filter(func(spawn): return spawn.get("carrier", false)).size() == 1,
		"Relic waves have exactly one carrier")
	# Spawn the whole wave at once and kill everything.
	game._wave_time = 999.0
	await process_frame
	var carrier: Invader = null
	for invader in board.invaders:
		if invader.carries_relic:
			carrier = invader
	_check(carrier != null, "The carrier spawns glowing")
	for invader in board.invaders.duplicate():
		invader.take_damage(99999.0, true)
	for i in 10:
		await process_frame
	_check(game.phase == game.Phase.BUILD and game.relic_offer.size() == 3,
		"Killing the carrier offers 3 relics after the wave")
	var offer_ids: Array = game.relic_offer.map(func(relic): return relic.id)
	var unique := {}
	for id in offer_ids:
		unique[id] = true
	_check(unique.size() == 3 and game.relic_offer.all(func(relic): return RelicSet.useful_for(relic, game.unit_types)),
		"The 3 relics are different and all useful for the pack")
	game.start_wave()
	_check(game.phase == game.Phase.BUILD, "The next wave can't start until a relic is picked")

	# A picked relic only works from the next wave on.
	var unit: Unit = board.place_unit(game.unit_types[1], Vector2i(4, 8))
	var damage_before := unit.stat("damage")
	game.relic_offer = [RelicSet.find("sharpening_stone")]
	game.pick_relic(0)
	_check(is_equal_approx(unit.stat("damage"), damage_before), "A relic doesn't work until the next wave")
	game.start_wave()
	_check(is_equal_approx(unit.stat("damage"), damage_before * 1.15), "...then it powers up matching units")
	await _stop(game)

	# One-time relics pay out the moment they're picked.
	game = await _start(biome, 0, 1)
	var coins_before: int = game.coins
	game.relic_offer = [RelicSet.find("gift_box")]
	game.pick_relic(0)
	_check(game.coins == coins_before + 25, "Gift Box pays its coins right when it's picked")
	# Offers are random: rolling many times gives different offers.
	var seen := {}
	for i in 8:
		var offer := RelicSet.new().roll_offer(game.unit_types, 0, randi())
		seen[str(offer.map(func(relic): return relic.id))] = true
	_check(seen.size() > 1, "Relic offers are random, not the same every time")
	# Removing a unit takes two taps.
	var placed: Unit = game.board.place_unit(game.unit_types[0], Vector2i(4, 8))
	game._select_cell(placed.cell)
	game.hud.refresh()
	game.hud._on_remove_pressed()
	_check(game.board.units.has(Vector2i(4, 8)) and game.hud._sell_button.text.begins_with("Tap again"),
		"The first tap on Remove only asks to confirm")
	game.hud._on_remove_pressed()
	_check(not game.board.units.has(Vector2i(4, 8)), "...and the second tap removes the unit")
	await _stop(game)

	# Economy relics: evolutions get cheaper.
	game = await _start(biome, 0, 1)
	var evolution: UnitData = game.unit_types[1].evolutions[0]
	game.board.relics.add_pending(RelicSet.find("bargain_scroll"))
	game.board.relics.activate_pending()
	_check(game.evolve_cost(evolution) == roundi(evolution.cost * 0.75), "Bargain Scroll makes evolutions 25% cheaper")
	await _stop(game)

	# Wall relics: cheaper walls, wall buddies hit harder, walls slow and burn.
	game = await _start(biome, 0, 1)
	board = game.board
	var wall: UnitData = null
	var shooter: UnitData = null
	for type in game.unit_types:
		if type.role == UnitData.Role.WALL and wall == null:
			wall = type
		elif type.can_attack() and shooter == null:
			shooter = type
	var wall_price: int = game.unit_cost(wall)
	for id in ["bulk_bricks", "buddy_system", "sticky_mortar", "nettle_hedge"]:
		board.relics.add_pending(RelicSet.find(id))
	board.relics.activate_pending()
	_check(game.unit_cost(wall) == maxi(1, wall_price - 2) and game.unit_cost(shooter) == shooter.cost,
		"Bulk Bricks makes walls (only walls) 2 coins cheaper")
	var gunner: Unit = board.place_unit(shooter, Vector2i(4, 8))
	var lone_bonus := 0.0
	var dummy: Invader = null
	game.start_wave()
	game._wave_time = 999.0
	await process_frame
	for invader in board.invaders:
		if not invader.is_flying() and not invader.data.is_boss and invader.data.armor == 0:
			dummy = invader
			break
	if dummy:
		dummy.data = dummy.data.duplicate()  # no surprise crits from relics here
		lone_bonus = gunner._bonus_against(dummy)
		var brick: Unit = board.place_unit(wall, Vector2i(5, 8))
		_check(gunner.next_to_wall() and is_equal_approx(gunner._bonus_against(dummy), lone_bonus + 0.15),
			"Buddy System: +15% damage next to a wall")
		# Park the invader next to the wall and let the aura tick.
		dummy.position = brick.position + Vector2(Board.TILE * 0.6, 0)
		var hp_before := dummy.hp
		brick._aura_timer = 0.0
		brick._wall_aura(0.0)
		_check(dummy.slow_amount > 0.0 and dummy.hp < hp_before, "Wall relics slow and burn invaders next to walls")
	else:
		_check(false, "Wall relic test found a plain ground invader")
	await _stop(game)

	# Archetype relics: rare/epic build-arounds with conditions and costs.
	game = await _start(biome, 0, 1)
	board = game.board
	game.start_wave()
	game._wave_time = 999.0
	await process_frame
	var target: Invader = null
	for invader in board.invaders:
		if not invader.is_flying() and not invader.data.is_boss and invader.data.armor == 0:
			target = invader
			break
	var loner: Unit = board.place_unit(shooter, Vector2i(1, 8))
	var plain := loner._bonus_against(target)
	board.relics.add_pending(RelicSet.find("lone_wolf"))
	board.relics.add_pending(RelicSet.find("cold_snap"))
	board.relics.add_pending(RelicSet.find("champion"))
	board.relics.activate_pending()
	# Lone Wolf +40%, Champion's cost -15% (not evolved), no slow yet.
	_check(is_equal_approx(loner._bonus_against(target), plain + 0.4 - 0.15),
		"Lone Wolf boosts a unit with no neighbors; Champion weakens unevolved units")
	target.apply_slow(0.3, 5.0)
	_check(is_equal_approx(loner._bonus_against(target), plain + 0.4 - 0.15 + 0.3),
		"Cold Snap: slowed invaders take more damage")
	loner.evolve(loner.data.evolutions[0])
	_check(is_equal_approx(loner._bonus_against(target), plain + 0.4 + 0.6 + 0.3)
		and is_equal_approx(loner.stat("attack_range"), loner.data.attack_range + 0.5),
		"Champion: evolved units hit harder and reach farther")
	board.relics.add_pending(RelicSet.find("labyrinth"))
	board.relics.activate_pending()
	_check(game.unit_cost(wall) == 1 and game.unit_cost(shooter) == roundi(shooter.cost * 1.12),
		"Labyrinth: walls cost 1 coin, other units cost more")
	await _stop(game)


func _test_bosses(biome: BiomeData) -> void:
	var boss_data: InvaderData = load("res://data/invaders/immune_system/superbug.tres")
	var minion: InvaderData = load("res://data/invaders/immune_system/rhinovirus.tres")

	# Non-boss levels have no boss marker.
	var game := await _start(biome, 0, 0)
	_check(game.board.boss_marker.spots.is_empty(), "Levels without a boss have no boss marker")
	await _stop(game)

	game = await _start(biome, 0, 4)  # boss level
	var board: Board = game.board
	# Level 5 has all six units: their buttons must fit across the screen.
	var row: HBoxContainer = game.hud._unit_row
	_check(row.get_child_count() == 6 and row.position.x + row.size.x <= Hud.WIDTH - 4,
		"All six unit buttons fit on screen (row ends at %d of %d)" % [row.position.x + row.size.x, Hud.WIDTH])
	_check(board.boss_marker.spots.size() >= 1, "The boss's spawn tile is marked from the start of the level")
	_check(board.preview_boss == null, "The boss route isn't shown before the boss wave")
	# Jump to the boss wave's build phase.
	game.wave_number = game.level.waves.size() - 1
	game._enter_build_phase()
	_check(board.preview_boss == boss_data and not board.preview_boss_spawns.is_empty()
		and game.footnote().contains("Boss wave"),
		"Before the boss wave, its route is shown and a footnote warns about it")
	game.toggle_paths()  # Paths off...
	_check(board.preview_boss != null, "...and the boss route stays visible with Paths off")
	game.toggle_paths()
	game.start_wave()
	_check(board.preview_boss == null, "The boss route hides once the wave starts")
	_check(_all_texts(game.hud).has("BOSS INCOMING!"), "The boss wave opens with a BOSS INCOMING banner")
	# Every boss has detailed 64x64 art, its own 6-frame death, and is drawn 2x.
	var art_ok := true
	for index in progress.WORLDS.size():
		for level in progress.load_biome(index).levels:
			for wave in level.waves:
				for entry in wave.entries:
					if entry.invader.is_boss:
						art_ok = art_ok and entry.invader.anim_move.get_height() == 64 \
							and entry.invader.anim_death.get_width() == 64 * 6
	_check(art_ok and Invader.BOSS_SCALE == 2.0, "Bosses have 64x64 art with their own death, shown 2x")
	# A minion only does its normal damage...
	var hp_before: int = game.base_hp
	game._on_base_hit(minion)
	_check(game.base_hp == hp_before - minion.base_damage and game.phase == game.Phase.WAVE,
		"Boss minions reaching the base do normal damage")
	# ...but the boss itself ends the level at once.
	game._on_base_hit(boss_data)
	_check(game.base_hp == 0 and game.phase == game.Phase.LOST, "The boss reaching the base is an instant loss")
	await _stop(game)

	# Bombs fall for a moment (with a warning) before they hit.
	game = await _start(progress.load_biome(3), 0, 0)  # Sandbox (Total War)
	board = game.board
	var target := board.place_unit(game.unit_types[1], Vector2i(4, 5))
	board.wave_active = true
	board.spawn_invader(load("res://data/invaders/total_war/toy_bomber.tres"), 0)
	var saw_falling := false
	var hp_while_falling := -1.0
	for i in 60 * 15:
		await process_frame
		if board.has_falling_bombs() and not saw_falling:
			saw_falling = true
			hp_while_falling = target.hp
		if saw_falling and not board.has_falling_bombs():
			break
	_check(saw_falling and hp_while_falling == target.data.max_hp,
		"Bombs fall for a moment before doing damage")
	_check(target.destroyed or target.hp < target.data.max_hp, "A falling bomb hits when it lands")
	await _stop(game)


# --- Selection and the coin font --------------------------------------------

func _test_selection(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 0)
	var cancel: Button = game.hud._cancel_button
	_check(not cancel.visible, "No Cancel button when nothing is selected")
	game.select_type(game.unit_types[0])
	_check(cancel.visible, "Selecting a unit type shows the Cancel button")
	cancel.pressed.emit()
	_check(game.selected_type == null and not cancel.visible, "Cancel deselects the unit type")
	await _stop(game)


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
	game = await _start(biome, 0, 4)
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


# --- Birthday Bash: piñatas and the Clown ------------------------------------

## Breaks the nth piñata of a wave and lists what came out.
func _pinata_surprise(biome: BiomeData, seed_text: String, nth: int) -> Array[String]:
	var game := await _start(biome, 0, 0)
	var board: Board = game.board
	board.wave_active = true
	board.start_pinata_seeds(seed_text)
	var pinata_data: InvaderData = load("res://data/invaders/birthday_bash/pinata.tres")
	for i in nth + 1:
		board.spawn_invader(pinata_data, 0)
	var pinata: Invader = board.invaders[nth]
	pinata.take_damage(100000.0, true)
	var names: Array[String] = []
	for invader in board.invaders:
		if invader.data != pinata_data:
			names.append(invader.data.id)
	await _stop(game)
	return names


func _test_party(biome: BiomeData) -> void:
	var first := await _pinata_surprise(biome, "birthday/2/3", 0)
	var again := await _pinata_surprise(biome, "birthday/2/3", 0)
	_check(not first.is_empty() and first == again,
		"Replaying a wave gives the same piñata surprise (%s)" % ", ".join(first))
	var pinata_data: InvaderData = load("res://data/invaders/birthday_bash/pinata.tres")
	var pool_ids := pinata_data.pinata_pool.map(func(d): return d.id)
	_check(first.size() >= pinata_data.pinata_min and first.size() <= pinata_data.pinata_max
		and first.all(func(id): return pool_ids.has(id)),
		"Piñata surprises hold %d-%d of the world's small invaders" % [pinata_data.pinata_min, pinata_data.pinata_max])
	# Different piñatas (or waves) usually hide different surprises.
	var differs := false
	for nth in 4:
		var other := await _pinata_surprise(biome, "birthday/2/3", nth + 1)
		differs = differs or other != first
	_check(differs, "Different piñatas hide different surprises")

	# The Clown tosses mini piñatas a few tiles ahead of itself.
	var game := await _start(biome, 0, 4)
	var board: Board = game.board
	board.wave_active = true
	board.start_pinata_seeds("clown-test")
	var clown_data: InvaderData = load("res://data/invaders/birthday_bash/clown.tres")
	board.spawn_invader(clown_data, 0)
	var clown: Invader = board.invaders[0]
	var tossed_ahead := false
	for i in 60 * 10:
		await process_frame
		for invader in board.invaders:
			if invader.data.id == "mini_pinata" and invader.path_index >= 0 \
					and invader.position.distance_to(clown.position) > Board.TILE * 1.5:
				tossed_ahead = true
		if tossed_ahead:
			break
	_check(tossed_ahead, "The Clown tosses mini piñatas ahead onto its route")
	await _stop(game)

	# Beating the Clown suggests Kitchen Defense if it isn't owned.
	var store: Node = root.get_node("Store")
	store.reset_test_purchases()
	store.buy(store.WORLD_BIRTHDAY)
	game = await _start(biome, 0, 4)
	game.hud.show_end_screen(true)
	await process_frame
	var texts := _all_texts(game.hud)
	_check(texts.has("Birthday Bash cleared!") and texts.any(func(t): return t.contains(": Kitchen Defense.")),
		"Birthday Bash shows its world-cleared screen and suggests Kitchen Defense")
	await _stop(game)
	store.reset_test_purchases()
	_check(store.product(store.WORLD_BIRTHDAY).get("warning", "") == "POST-GAME: HARD",
		"The store warns that Birthday Bash is post-game hard")


# --- Capstones (second evolution tier) ----------------------------------------

const PACKS := "res://data/packs/immune_system/"
const INVADERS := "res://data/invaders/immune_system/"


## A tough, frozen-in-place invader for testing hits.
func _dummy(board: Board, id: String, cell: Vector2i, hp := 1000.0) -> Invader:
	var path: Array[Vector2i] = [cell]
	var invader := board._add_invader(load(INVADERS + id + ".tres"), board.cell_center(cell), path, 0)
	invader.hp = hp
	invader.set_process(false)
	return invader


func _test_capstones(biome: BiomeData) -> void:
	# Level 1 of World 1: an open 9x14 map with spawn (4,0) and base (4,13).
	var game := await _start(biome, 0, 0)
	var board: Board = game.board
	board.wave_active = true

	# Chain: one shot hits the target and jumps to the others nearby.
	var chain: Unit = board.place_unit(load(PACKS + "fortress/presenting_dendrite.tres"), Vector2i(1, 5))
	var a := _dummy(board, "rhinovirus", Vector2i(2, 6))
	var b := _dummy(board, "rhinovirus", Vector2i(3, 6))
	var c := _dummy(board, "rhinovirus", Vector2i(4, 6))
	chain._attack()
	_check(a.hp < 1000 and b.hp < 1000 and c.hp < 1000, "Chain hits jump to more invaders")
	_check(c.hp > a.hp, "Chain jumps deal less damage")
	for x in [a, b, c]:
		board.invaders.erase(x)
		x.queue_free()
	board.remove_unit(Vector2i(1, 5))

	# Multishot: three far-apart targets all get hit at once.
	var multi: Unit = board.place_unit(load(PACKS + "swarm/barrage_monocyte.tres"), Vector2i(4, 5))
	var targets: Array[Invader] = [_dummy(board, "rhinovirus", Vector2i(2, 5)),
		_dummy(board, "rhinovirus", Vector2i(6, 5)), _dummy(board, "rhinovirus", Vector2i(4, 7))]
	multi._attack()
	_check(targets.all(func(t): return t.hp < 1000), "Multishot hits 3 targets at once")
	for t in targets:
		board.invaders.erase(t)
		t.queue_free()
	board.remove_unit(Vector2i(4, 5))

	# Line pierce: the shot carries through to invaders behind the target.
	var lance: Unit = board.place_unit(load(PACKS + "precision/railgun_lance.tres"), Vector2i(4, 2))
	var front := _dummy(board, "rhinovirus", Vector2i(4, 4))
	var behind := _dummy(board, "rhinovirus", Vector2i(4, 6))
	front.hp = 10.0  # closest to the base? No: make the front one the target by distance.
	lance._attack()
	_check(front.hp < 10.0 and behind.hp < 1000, "Line pierce hits every invader in the line")
	for t in [front, behind]:
		if is_instance_valid(t):
			board.invaders.erase(t)
			t.queue_free()
	board.remove_unit(Vector2i(4, 2))

	# Execute: a wounded invader is finished off.
	var executioner: Unit = board.place_unit(load(PACKS + "fortress/devouring_macrophage.tres"), Vector2i(1, 8))
	# 25 HP minus a 20-damage hit (22 - 2 armor) leaves 5, under 25% of 24.
	var wounded := _dummy(board, "biofilm", Vector2i(2, 8), 25.0)
	executioner._hit(wounded)
	_check(not wounded.alive, "Execute finishes off wounded invaders")
	board.remove_unit(Vector2i(1, 8))

	# Armor shred: hits strip armor permanently.
	var shredder: Unit = board.place_unit(load(PACKS + "swarm/piercing_monocyte.tres"), Vector2i(1, 8))
	var armored := _dummy(board, "biofilm", Vector2i(2, 8))
	shredder._hit(armored)
	_check(armored.armor_lost == 1, "Armor shred strips armor")
	board.invaders.erase(armored)
	armored.queue_free()
	board.remove_unit(Vector2i(1, 8))

	# Knockback: shoves a walker back along its route (but never a boss).
	var pusher: Unit = board.place_unit(load(PACKS + "fortress/titan_macrophage.tres"), Vector2i(0, 8))
	var route := board.walker_path(Vector2i(4, 0))
	var walker := board._add_invader(load(INVADERS + "rhinovirus.tres"), board.cell_center(route[6]), route, 7)
	walker.hp = 1000.0
	walker.set_process(false)
	pusher._hit(walker)
	_check(walker.path_index < 7, "Knockback shoves invaders back along their route")
	var boss := board._add_invader(load(INVADERS + "superbug.tres"), board.cell_center(route[6]), route, 7)
	boss.set_process(false)
	pusher._hit(boss)
	_check(boss.path_index == 7, "Bosses can't be knocked back")
	for t in [walker, boss]:
		board.invaders.erase(t)
		t.queue_free()
	board.remove_unit(Vector2i(0, 8))

	# Bounty: kills pay extra coins.
	var drops := [0]
	board.coins_dropped.connect(func(amount, _where): drops[0] += amount)
	var hunter: Unit = board.place_unit(load(PACKS + "fortress/harvesting_dendrite.tres"), Vector2i(1, 8))
	var prey := _dummy(board, "rhinovirus", Vector2i(2, 8), 1.0)
	hunter._hit(prey)
	_check(drops[0] == prey.data.coin_drop + 2, "Bounty kills drop extra coins (%d)" % drops[0])
	board.remove_unit(Vector2i(1, 8))

	# Zones: a burning patch keeps hurting whoever stands in it.
	var burner: Unit = board.place_unit(load(PACKS + "fortress/foam_eruption.tres"), Vector2i(1, 8))
	var standing := _dummy(board, "rhinovirus", Vector2i(2, 8))
	burner._shoot(standing)
	var hp_after_hit := standing.hp
	board._update_zones(1.0)
	_check(not board.zones.is_empty() and standing.hp < hp_after_hit, "Lingering zones keep hurting invaders")
	board.restore_units()
	_check(board.zones.is_empty(), "Zones clear between waves")
	board.invaders.erase(standing)
	standing.queue_free()
	board.remove_unit(Vector2i(1, 8))

	# Grab: a smasher biting the wall gets stuck.
	var snare: Unit = board.place_unit(load(PACKS + "fortress/clotting_snare.tres"), Vector2i(1, 8))
	var biter := _dummy(board, "worm", Vector2i(1, 7))
	snare.take_damage(5.0, biter)
	_check(biter.stun_time > 0.0, "Grab walls stun the smashers biting them")
	board.remove_unit(Vector2i(1, 8))

	# Explode on break: blasts nearby invaders.
	var mine: Unit = board.place_unit(load(PACKS + "fortress/thrombus_mine.tres"), Vector2i(1, 8))
	mine.take_damage(100000.0, biter)
	_check(biter.hp < biter.data.max_hp - 50 or not biter.alive, "Exploding walls blast nearby invaders")
	board.remove_unit(Vector2i(1, 8))

	# Rebuild once: survives its first break each wave.
	var bastion: Unit = board.place_unit(load(PACKS + "fortress/fibrin_bastion.tres"), Vector2i(1, 8))
	bastion.take_damage(100000.0)
	_check(not bastion.destroyed and bastion.hp == bastion.data.max_hp, "Rebuild walls come back once")
	bastion.take_damage(100000.0)
	_check(bastion.destroyed, "...but only once per wave")
	board.remove_unit(Vector2i(1, 8))

	# Auras: neighbors take less damage, attack faster and ignore goo.
	board.place_unit(load(PACKS + "fortress/fortress_granuloma.tres"), Vector2i(1, 8))
	var guarded: Unit = board.place_unit(load(PACKS + "fortress/platelet_clot.tres"), Vector2i(2, 8))
	guarded.take_damage(10.0)
	_check(is_equal_approx(guarded.hp, guarded.data.max_hp - 7.0), "Shield auras cut neighbors' damage by 30%")
	guarded.make_sticky(0.4)
	_check(guarded.sticky == 0.0, "Cleanse auras keep neighbors free of goo")
	board.place_unit(load(PACKS + "fortress/signaling_fibroblast.tres"), Vector2i(3, 8))
	_check(board.aura_at(Vector2i(2, 9)).speed == 0.25, "Speed auras reach the 8 tiles around")
	await _stop(game)

	# Buying: a capstone needs a tier-1 unit that has survived a wave since
	# evolving, and refunds like everything else.
	game = await _start(biome, 0, 0)
	board = game.board
	game.coins = 999
	var base: UnitData = game.unit_types[1]
	game.try_place(base, Vector2i(0, 10))
	var unit: Unit = board.units[Vector2i(0, 10)]
	var coins_after_placing: int = game.coins
	game._select_cell(unit.cell)
	game.wave_number += 1
	var tier1: UnitData = base.evolutions[0]
	game.evolve_selected(tier1)
	var capstone: UnitData = tier1.evolutions[0]
	_check(unit.data == tier1 and not game.can_evolve(capstone), "Capstones need a wave after the first evolution")
	game.wave_number += 1
	game.evolve_selected(capstone)
	_check(unit.is_capstone() and game.coins == coins_after_placing - tier1.cost - capstone.cost
		and capstone.cost == 2 * (base.cost + tier1.cost),
		"A capstone costs 2x the unit plus its first evolution (%d)" % capstone.cost)
	var refund: int = game.sell_value(unit).coins
	_check(refund == int(base.cost * 0.5) + int(tier1.cost * 0.5) + capstone.cost,
		"Capstones refund fully the round they're bought")
	_check(unit.total_cost() == base.cost + tier1.cost + capstone.cost, "Bombers see a capstone's full value")
	await _stop(game)

	# Every world gives its capstones their own themed names (compared with
	# Microscopic, where the pack stats and base names live).
	var base_names := {}
	for name in _capstone_names(biome):
		base_names[name] = true
	var reused := 0
	for index in progress.WORLDS.size():
		if progress.world_id(index) == biome.id:
			continue
		for name in _capstone_names(progress.load_biome(index)):
			if base_names.has(name):
				reused += 1
	_check(reused == 0, "Every world has its own capstone names (%d reused from Microscopic)" % reused)


func _capstone_names(world: BiomeData) -> Array[String]:
	var names: Array[String] = []
	for pack in world.packs:
		for unit in pack.units:
			for tier1 in unit.evolutions:
				for capstone in tier1.evolutions:
					names.append(capstone.display_name)
	return names


# --- Animated sprites ------------------------------------------------------------

func _test_animations(biome: BiomeData) -> void:
	var game := await _start(biome, 0, 0)
	var board: Board = game.board
	board.wave_active = true
	var attacker: UnitData = load(PACKS + "fortress/macrophage.tres")
	var unit: Unit = board.place_unit(attacker, Vector2i(1, 8))
	_check(attacker.anim_idle != null and unit._sprite.hframes == StripPlayer.frames_in(attacker.anim_idle)
		and is_equal_approx(unit._art_scale * attacker.anim_idle.get_height(), Board.TILE * Unit.ART_BOOST),
		"Units play their idle strip, sized to fill the tile")
	unit._play_attack()
	_check(unit._sprite.texture == attacker.anim_attack, "Firing plays the attack strip")
	for i in 60:
		await process_frame
	_check(unit._sprite.texture == attacker.anim_idle, "...then returns to idle")
	var capstone: Unit = board.place_unit(load(PACKS + "fortress/presenting_dendrite.tres"), Vector2i(3, 8))
	_check(capstone._star.visible and capstone.data.anim_idle == load(PACKS + "fortress/mature_dendrite.tres").anim_idle,
		"Capstones reuse their tier-1 animation, with a gold star")
	var walker := _dummy(board, "rhinovirus", Vector2i(2, 10), 1.0)
	var outline: ShaderMaterial = walker._sprite.material
	_check(outline != null and outline.get_shader_parameter("frames") == walker._sprite.hframes
		and unit._sprite.material == null, "Enemies get the red outline (matching their strip's frames); units don't")
	var sprites_before := board.get_children().filter(func(c): return c is Sprite2D).size()
	walker.take_damage(5.0, true)
	_check(walker._sprite.hframes > 1 and board.get_children().filter(func(c): return c is Sprite2D).size() == sprites_before + 1,
		"Invaders walk with their move strip and play a death animation")
	await _stop(game)


# --- Painted level backgrounds ---------------------------------------------------

func _test_background(biome: BiomeData) -> void:
	# A plain 1152x1792 image stands in for a painted background.
	var image := Image.create(1152, 1792, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.3, 0.6, 0.3))
	var level: LevelData = biome.levels[0]
	level.background = ImageTexture.create_from_image(image)
	var game := await _start(biome, 0, 0)
	var sprite: Sprite2D = null
	for child in game.board.get_children():
		if child is Sprite2D:
			sprite = child
	_check(sprite != null and game.board._has_background
		and is_equal_approx(sprite.scale.x * 1152, 9 * Board.TILE) and is_equal_approx(sprite.scale.y * 1792, 14 * Board.TILE),
		"A level background fills the 9x14 board exactly")
	# Every spawn tile gets an animated spawner (and the still tile is hidden).
	var spawners: Array = game.board.get_children().filter(func(child): return child is SpawnerView)
	_check(spawners.size() == game.board.spawn_cells.size() + game.board.sea_spawn_cells.size()
		and spawners.all(func(view): return view.strip.get_width() == view.strip.get_height() * SpawnerView.FRAMES),
		"Each spawn tile plays an animated 4-frame spawner")
	# Obstacles use the 32x32 map-object art, in a mix of the 3 looks.
	var looks := {}
	for cell in game.board.rocks:
		looks[ObstacleLayer.look_for(cell)] = true
	_check(game.board.obstacle_layer.obstacles != null and (game.board.rocks.size() < 4 or looks.size() > 1),
		"Obstacles are drawn from the world's map-object art, in mixed looks")
	# The background is calmed by the fog + mute filter, at the player's
	# strength times the picture's busyness factor (a flat picture: the minimum).
	var material := sprite.material as ShaderMaterial
	_check(material != null and material.shader == CalmBackground.SHADER
		and is_equal_approx(material.get_shader_parameter("strength"),
			game.board.calm_strength * CalmBackground.BUSY_MIN),
		"Painted backgrounds get the calming filter (flat pictures get the least)")
	# A busy picture (fine checkerboard) gets a stronger filter than a flat one.
	var busy := Image.create(360, 560, false, Image.FORMAT_RGBA8)
	for y in 560:
		for x in 360:
			busy.set_pixel(x, y, Color.WHITE if (x / 2 + y / 2) % 2 == 0 else Color.BLACK)
	var busy_material := CalmBackground.make_material(busy, 1.0)
	_check(busy_material.get_meta("busy_factor") == CalmBackground.BUSY_MAX
		and material.get_meta("busy_factor") == CalmBackground.BUSY_MIN,
		"Busy backgrounds get a stronger filter than calm ones")
	# The Background setting is saved, clamped, and 0 turns the filter off.
	var progress = root.get_node("Progress")
	progress.set_calm_strength(9.0)
	var clamped: float = progress.calm_strength()
	progress.set_calm_strength(0.0)
	CalmBackground.set_strength(busy_material, progress.calm_strength())
	_check(is_equal_approx(clamped, progress.CALM_MAX)
		and busy_material.get_shader_parameter("strength") == 0.0,
		"The Background setting is clamped, and Off removes the filter")
	progress.set_calm_strength(progress.CALM_DEFAULT)
	level.background = null
	await _stop(game)


# --- Pack swapping and achievements ----------------------------------------------

## True if an image looks the same mirrored left-right (and, with
## `top_bottom`, also mirrored top-bottom).
func _symmetric(image: Image, top_bottom: bool) -> bool:
	for y in image.get_height():
		for x in image.get_width():
			var color := image.get_pixel(x, y)
			if color != image.get_pixel(image.get_width() - 1 - x, y):
				return false
			if top_bottom and color != image.get_pixel(x, image.get_height() - 1 - y):
				return false
	return true


## Every PackSymbol under a node.
func _pack_symbols(node: Node) -> Array:
	var result := []
	for child in node.get_children():
		if child is PackSymbol:
			result.append(child)
		result.append_array(_pack_symbols(child))
	return result


func _test_pack_swapping(biome: BiomeData) -> void:
	progress.reset()
	progress.choose_pack(biome, biome.packs[0])
	for index in 2:
		progress.level_index = index
		progress.complete_level()
	progress.choose_pack(biome, biome.packs[1])
	_check(progress.cleared(biome.id) == 2, "Swapping packs keeps world progress")
	progress.level_index = 0
	progress.complete_level()
	_check(progress.packs_that_beat(biome.id, 0) == ["fortress", "swarm"] and progress.packs_that_beat(biome.id, 1) == ["fortress"],
		"Each pack remembers the levels it has beaten")
	_check(progress.cleared(biome.id) == 2, "Replaying an earlier level never lowers progress")
	# The level screen shows the pack picker, and no pack screen is needed.
	progress.return_screen = "levels"
	var menu: Control = load("res://scenes/menu.tscn").instantiate()
	root.add_child(menu)
	await process_frame
	var texts := _all_texts(menu)
	var symbols := _pack_symbols(menu)
	var filled := symbols.filter(func(symbol): return symbol.fill >= 1.0)
	_check(texts.has("Swarm") and symbols.size() == 25 and filled.size() == 3,
		"The level list has a pack picker and fills a pack symbol for each pack that beat a level")
	# The world card's symbols fill up 1/5 per level beaten.
	menu._show(menu._show_biomes)
	await process_frame
	# Pack symbols are mirror images left-right; Precision and Control
	# also top-bottom (the user's rule).
	var all_symmetric := true
	for pack_id in PackSymbol.ORDER:
		var image: Image = load(PackSymbol.ART_DIR + pack_id + ".png").get_image()
		all_symmetric = all_symmetric and _symmetric(image, pack_id in ["precision", "control"])
	_check(all_symmetric, "Pack symbols are symmetrical (Precision and Control both ways)")
	# Backyard (always unlocked) shows 5 symbols; the test world is locked
	# after the reset, so its fill is checked through the count it uses.
	var card_symbols := _pack_symbols(menu)
	_check(card_symbols.size() == 5 and progress.levels_beaten_by(biome.id, "fortress") == 2
		and progress.levels_beaten_by(biome.id, "swarm") == 1,
		"World cards show the 5 pack symbols, filled by levels each pack beat (Fortress 2/5)")
	menu.queue_free()
	progress.return_screen = "title"
	progress.reset()
	await process_frame


func _test_achievements(biome: BiomeData) -> void:
	var achievements: Node = root.get_node("Achievements")
	achievements.reset()
	progress.reset()
	_check(achievements.list.size() == 27, "There are 27 achievements")
	# Winning a level used to freeze the game for ~10s while achievements
	# reloaded every world. It must stay instant.
	var started := Time.get_ticks_msec()
	achievements.on_level_won({"base_hp": 5, "max_hp": 20, "boss_level": false, "evolutions": 1,
		"paths_seen": true, "units": 20})
	_check(Time.get_ticks_msec() - started < 100, "Checking achievements after a win is instant (%d ms)" % (Time.get_ticks_msec() - started))
	achievements.on_level_won({"base_hp": 20, "max_hp": 20, "boss_level": true, "evolutions": 0,
		"paths_seen": false, "units": 5})
	_check(["flawless", "untouchable_boss", "back_to_basics", "blindfolded", "minimalist"].all(
		func(id): return achievements.is_earned(id)) and not achievements.is_earned("close_call"),
		"Winning flawlessly, unevolved and blind earns the matching skill achievements")
	achievements.add_stat("pinatas", 49)
	_check(not achievements.is_earned("pinata_smasher") and achievements.progress_of(achievements.find("pinata_smasher")) == [49, 50],
		"Locked achievements report their progress (49/50)")
	achievements.add_stat("pinatas", 1)
	_check(achievements.is_earned("pinata_smasher"), "Running totals earn achievements when they reach the goal")
	# Capstone Collector: one capstone of each mechanic.
	for pack in biome.packs:
		for unit in pack.units:
			for tier1 in unit.evolutions:
				for capstone in tier1.evolutions:
					achievements.on_evolved(capstone)
	_check(achievements.is_earned("capstone") and achievements.is_earned("capstone_collector"),
		"Capstones count toward Capstone Collector (all 12 mechanics exist)")
	# Pack mastery: every main-world level beaten with Fortress.
	for index in 5:
		var world: BiomeData = progress.load_biome(index)
		progress.choose_pack(world, world.packs[0])
		for level_index in world.levels.size():
			progress.level_index = level_index
			progress.complete_level()
	achievements.check_progress(false)
	_check(achievements.is_earned("fortress_master") and not achievements.is_earned("swarm_master")
		and achievements.is_earned("cell_to_the_stars") and achievements.is_earned("germ_buster"),
		"Beating every main level with one pack earns its mastery (and world achievements)")
	# The achievements screen lists every one.
	progress.return_screen = "title"
	var menu: Control = load("res://scenes/menu.tscn").instantiate()
	root.add_child(menu)
	await process_frame
	menu._show(menu._show_achievements)
	await process_frame
	var texts := _all_texts(menu)
	_check(texts.any(func(t): return t.contains("Fortress Master"))
		and texts.any(func(t): return t.contains("of 27 earned")), "The Achievements screen lists them all")
	menu.queue_free()
	achievements.reset()
	progress.reset()
	await process_frame


# --- Path preview on every level ------------------------------------------------

func _test_path_toggle(biome: BiomeData) -> void:
	progress.reset()
	var game := await _start(biome, 0, 2)  # level 3: not a teaching level
	_check(game.board.show_path_preview, "Paths show on every level by default")
	_check(game.board.show_grid, "Faint gridlines show while building")
	game.start_wave()
	_check(not game.board.show_grid, "...and hide during waves")
	await _stop(game)
	game = await _start(biome, 0, 2)
	game.toggle_paths()
	_check(not game.board.show_path_preview and game.hud._paths_button.text == "Paths: Off",
		"The Paths button hides the routes")
	await _stop(game)
	game = await _start(biome, 0, 1)
	_check(not game.board.show_path_preview, "The Paths choice is remembered")
	await _stop(game)
	progress.reset()


# --- Five levels of eight waves ------------------------------------------------

func _test_level_counts() -> void:
	var sizes_ok := true
	for index in progress.WORLDS.size():
		var world: BiomeData = progress.load_biome(index)
		sizes_ok = sizes_ok and world.levels.size() == 5
		for level in world.levels:
			sizes_ok = sizes_ok and level.waves.size() == 8
	_check(sizes_ok, "Every world has 5 levels of 8 waves")
	var pack: PackData = progress.load_biome(0).packs[0]
	_check(pack.units_for_level(4).size() == 6 and pack.units_for_level(3).size() == 5,
		"New units unlock on levels 2, 3 and 4")
	# An old save (7 levels per world) converts by position.
	var old_save := {"biomes": {"a": {"pack": "fortress", "cleared": 7},
		"b": {"pack": "swarm", "cleared": 4}, "c": {"pack": "swarm", "cleared": 3}}}
	var file := FileAccess.open(progress.SAVE_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(old_save))
	file.close()
	progress._load()
	_check(progress.cleared("a") == 5 and progress.cleared("b") == 3 and progress.cleared("c") == 2,
		"Old saves convert: 7 -> 5, 4 -> 3, 3 -> 2 levels cleared")
	progress._load()
	_check(progress.cleared("a") == 5 and progress.cleared("b") == 3, "Converted saves don't convert twice")
	_check(progress.packs_that_beat("a", 4) == ["fortress"] and progress.packs_that_beat("b", 2) == ["swarm"]
		and progress.packs_that_beat("b", 3).is_empty(), "Old saves credit their pack with the levels it cleared")
	progress.reset()


# --- Upgrade preview and menu scrolling ----------------------------------------

func _test_upgrade_preview(biome: BiomeData) -> void:
	# Fire rate: shots per second in the info line; a placed Swarm unit with
	# neighbors shows its faster current rate next to its base rate.
	var swarm_game := await _start(biome, 1, 0)
	swarm_game.coins = 999
	var swarm_type: UnitData = swarm_game.unit_types[1]
	var rate: String = swarm_game._num(1.0 / swarm_type.attack_interval)
	_check(swarm_game.describe(swarm_type).contains("%s shots/s" % rate), "Unit info shows fire rate in shots/s")
	var swarm_board: Board = swarm_game.board
	var packed: Unit = swarm_board.place_unit(swarm_type, Vector2i(4, 8))
	swarm_board.place_unit(swarm_game.unit_types[0], Vector2i(3, 8))
	swarm_board.place_unit(swarm_game.unit_types[0], Vector2i(5, 8))
	_check(swarm_type.adjacency_bonus > 0.0 and swarm_game.describe(swarm_type, packed).contains("(base %s)" % rate),
		"A packed Swarm unit shows its boosted fire rate and its base rate")
	await _stop(swarm_game)

	var game := await _start(biome, 0, 0)
	game.coins = 999
	var base: UnitData = game.unit_types[1]  # Germ Eater
	game.try_place(base, Vector2i(0, 10))
	var unit: Unit = game.board.units[Vector2i(0, 10)]
	game.wave_number += 1
	game._select_cell(unit.cell)
	game.hud.refresh()
	game.hud._on_evolve_pressed(0)
	var option: UnitData = base.evolutions[0]
	_check(unit.data == base and game.hud._message_label.text.contains(option.description),
		"The first tap on an upgrade only previews it")
	_check(game.hud._footnote_label.text.contains("dmg 9 \u2192 17"),
		"The preview shows stat changes (%s)" % game.hud._footnote_label.text)
	_check(game.hud._evolve_buttons[0].text.begins_with("Tap again"), "The previewed button asks for a second tap")
	game.hud._on_evolve_pressed(0)
	_check(unit.data == option, "The second tap buys the upgrade")
	# Previewing then selecting something else cancels the preview.
	game.wave_number += 1
	game.hud._on_evolve_pressed(1)
	game._select_cell(Board.NO_CELL)
	game.hud.refresh()
	_check(game.hud._armed_option == -1 and game.board.preview_range == 0.0,
		"Deselecting cancels an upgrade preview")
	await _stop(game)


func _test_menu_scrolling() -> void:
	progress.return_screen = "store"
	var menu: Control = load("res://scenes/menu.tscn").instantiate()
	root.add_child(menu)
	await process_frame
	var blocking := []
	var find_blockers := func(node: Node, again: Callable) -> void:
		for child in node.get_children():
			if child is Control and child.mouse_filter == Control.MOUSE_FILTER_STOP:
				blocking.append(child)
			again.call(child, again)
	find_blockers.call(menu._content, find_blockers)
	_check(blocking.is_empty(), "Menu cards and buttons let drags through to scroll (%d block)" % blocking.size())
	# A press that turned into a drag doesn't press the button.
	var shown := [menu._current_screen]
	menu._dragged = true
	var back: Button = menu._content.get_child(0).get_child(0)
	back.pressed.emit()
	await process_frame
	_check(menu._current_screen == shown[0], "Dragging across a button doesn't press it")
	menu._dragged = false
	back.pressed.emit()
	await process_frame
	_check(menu._current_screen != shown[0], "A plain tap still presses it")
	menu.queue_free()
	progress.return_screen = "title"
	await process_frame


## The title showcase, world stripes, postcards and screen slides.
func _test_menu_pizazz() -> void:
	var showcase: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/showcase.json"))
	var art_ok := true
	for index in progress.WORLDS.size():
		var id: String = progress.world_id(index)
		var units: Array = showcase.get(id, [])
		var card: Dictionary = showcase._cards.get(id, {})
		art_ok = art_ok and units.size() >= 10 and ResourceLoader.exists(card.get("boss", "")) \
			and ResourceLoader.exists(card.get("invader", ""))
		for unit in units:
			art_ok = art_ok and ResourceLoader.exists(unit.idle) and not unit.evolutions.is_empty()
			for evolution in unit.evolutions:
				art_ok = art_ok and ResourceLoader.exists(evolution.idle)
	_check(art_ok, "Every world has showcase units (with evolutions) and postcard boss/invader art")

	progress.reset()
	progress.return_screen = "title"
	var menu: Control = load("res://scenes/menu.tscn").instantiate()
	root.add_child(menu)
	await process_frame
	var hero: EvolutionShowcase = null
	for child in menu._content.get_children():
		if child is EvolutionShowcase:
			hero = child
	var picks: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/title_pool.json"))
	_check(menu._stripes.visible and menu._stripes._slices.size() == progress.WORLDS.size()
		and hero != null and picks.units.size() == 40 and hero._pool.size() == 40,
		"The title shows every world's map and a showcase pool of the 40 hand-picked units")
	hero._time = EvolutionShowcase.EVOLVE_AT + 0.5
	await process_frame
	_check(hero._branches.all(func(icon): return icon.strip != null and icon.modulate.a > 0.5)
		and hero._branch_names.all(func(label): return label.text != ""),
		"The showcase unit branches into both of its evolutions at once")

	# World select: postcards, slid in from the right; Backyard is new once.
	var new_before: bool = progress.is_world_new("backyard_bugs")
	menu._show(menu._show_biomes)
	var slid_right: bool = menu._scroll.position.x > 0
	await process_frame  # the old screen's nodes are freed at the end of the frame
	var icons: Array = menu._content.find_children("*", "AnimIcon", true, false)
	_check(new_before and not progress.is_world_new("backyard_bugs") and not menu._stripes.visible
		and icons.size() == 2 and slid_right,
		"World postcards: unlocked worlds show their boss and an invader; a new world celebrates once")
	menu._going_back = true
	menu._show(menu._show_title)
	_check(menu._scroll.position.x < 0, "Back slides the previous screen in from the left")
	menu.queue_free()
	await process_frame


## Endless mode: offered after the boss level, waves keep coming and ramp,
## relics stack once the pool runs dry, and the best wave is saved.
func _test_endless(biome: BiomeData) -> void:
	var game := await _start(biome, 0, biome.levels.size() - 1)
	game.wave_number = game.level.waves.size()
	game._finish(true)
	_check(_all_texts(game.hud).has("Continue in Endless"), "Beating the boss level offers Continue in Endless")
	game.base_hp = 3
	game.start_endless()
	await process_frame
	_check(game.endless and game.phase == game.Phase.BUILD and game.base_hp == game.level.base_hp
		and not _all_texts(game.hud).has("Continue in Endless") and game.hud._wave_label.text.contains("Endless"),
		"Continuing into endless repairs the base and goes back to building")
	var first: WaveData = game.wave_data(game.wave_number)
	var tenth: WaveData = game.wave_data(game.wave_number + 9)
	var threat := func(wave: WaveData) -> int:
		var total := 0
		for entry in wave.entries:
			total += entry.count * maxi(1, entry.invader.max_hp)
		return total
	_check(not first.entries.is_empty() and threat.call(tenth) > threat.call(first)
		and tenth.entries.any(func(entry): return entry.invader.is_boss)
		and not first.entries.any(func(entry): return entry.invader.is_boss)
		and game.wave_data(game.wave_number) == first,
		"Endless waves grow, and the boss returns on the 10th")
	_check(game.is_relic_wave(9) and not game.is_relic_wave(10) and game.is_relic_wave(11)
		and EndlessWaves.hp_scale(20) > 2.0 and EndlessWaves.boss_hp_scale(10) == 1.5
		and EndlessWaves.boss_hp_scale(20) == 2.0,
		"Endless: relics every 2nd wave, tougher invaders, +50% boss HP per return")
	game.start_wave()
	await process_frame
	await process_frame
	var tough: bool = game.board.hp_scale > 1.0 and game.board.invaders.all(
		func(invader): return invader.full_hp > invader.data.max_hp)
	_check(tough, "Endless invaders spawn with extra HP")
	# Stuns can't chain forever in endless, and no slow stops an invader.
	var target: Invader = game.board.invaders[0] if not game.board.invaders.is_empty() else null
	if target:
		target.apply_stun(0.2)
		for i in 20:
			await process_frame
		target.apply_stun(2.0)
		var guarded := target.stun_time == 0.0
		target.apply_slow(3.0, 1.0)
		_check(guarded and target.slow_amount <= Invader.MAX_SLOW,
			"Endless invaders get a short stun guard; slows are capped at 80%")
		# A wave that drags on enrages its invaders: no more stuns or slows.
		game._wave_time = game.ENRAGE_AFTER + 1.0
		await process_frame
		target.stun_guard = 0.0
		target.stun_time = 0.0
		target.slow_time = 0.0
		target.apply_stun(2.0)
		target.apply_slow(0.5, 2.0)
		_check(game.board.enraged and target.stun_time == 0.0 and target.slow_time == 0.0,
			"Endless waves that drag on enrage their invaders (no stuns or slows)")
	else:
		_check(false, "Endless invaders get a short stun guard; slows are capped at 80%")
	# Losing ends the run and saves the best wave for this world and pack.
	progress.reset()
	game.wave_number = 13
	game._finish(false)
	_check(progress.endless_best(biome.id, game.pack.id) == 13 and _all_texts(game.hud).has("Endless Over")
		and _all_texts(game.hud).has("NEW BEST!"), "Losing in endless saves the best wave (NEW BEST)")
	await _stop(game)
	# Relics stack once every useful relic is taken: offers become x2 copies.
	game = await _start(biome, 0, 4)
	var relics: RelicSet = game.board.relics
	for relic in RelicSet.pool():
		if RelicSet.useful_for(relic, game.unit_types):
			relics.active.append(relic)
	var offer: Array = relics.roll_offer(game.unit_types, 3, 5)
	_check(offer.size() == 3 and offer.all(func(relic): return relics.copies(relic.id) == 1),
		"When the relic pool runs dry it resets: relics can be taken again (x2)")
	relics.active.clear()
	await _stop(game)
	progress.reset()


## How far the bot gets in endless (after winning the boss level), per pack.
## Run with: tests/sim_test.gd -- endless [world=N]
func _test_endless_reach(biome: BiomeData) -> void:
	print("\nEndless reach in %s: the wave each pack's bot run ended on." % biome.display_name)
	var line := ""
	for pack_index in biome.packs.size():
		var game := await _start(biome, pack_index, biome.levels.size() - 1)
		await _play(game, AutoPlayer.new(game, 7))
		if game.phase != game.Phase.WON:
			line += "%s: lost the boss level  " % biome.packs[pack_index].display_name
			await _stop(game)
			continue
		game.start_endless()
		game.speed = 4  # endless runs are long; 4x (a speed players can pick) keeps the test quick
		await _play(game, AutoPlayer.new(game, 7))
		line += "%s: wave %d  " % [biome.packs[pack_index].display_name, game.wave_number]
		print("  %s: endless run ended on wave %d" % [biome.packs[pack_index].display_name, game.wave_number])
		_check(game.phase == game.Phase.LOST and game.wave_number < 80,
			"%s endless with %s ends before wave 80" % [biome.display_name, biome.packs[pack_index].display_name])
		await _stop(game)
	print(line)


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
		"Starting hand converts coin value into copies (%d coins of %d-coin walls = %d)" % [game.level.hand_value[0], wall.cost, expected_walls])

	# Sealing the path must be refused. Row 1 is fully open, 9 tiles wide.
	game.coins = 999
	for x in 8:
		game.try_place(wall, Vector2i(x, 1))
	_check(not game.try_place(wall, Vector2i(8, 1)) and not board.walker_path(board.spawn_cells[0]).is_empty(),
		"Placement that would seal the path is refused")

	# Same-round refunds: free units go back to the hand, bought units refund fully.
	game._select_cell(Vector2i(0, 1))  # first wall came from the hand
	game.sell_selected()
	_check(game.hand[wall.id] == 1, "Removing a free unit placed this round returns it to the hand")
	var coins_before: int = game.coins
	game._select_cell(Vector2i(7, 1))  # bought with coins
	game.sell_selected()
	_check(game.coins == coins_before + wall.cost, "Removing a bought unit placed this round refunds 100%")

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
	board.coins_dropped.connect(func(amount, _where): drops[0] += amount)
	var leaks := [0]
	board.base_hit.connect(func(_inv): leaks[0] += 1)
	coins_before = game.coins
	game.start_wave()
	while game.phase == game.Phase.WAVE:
		await process_frame
	_check(not broken.destroyed and broken.hp == broken.data.max_hp and damaged.hp == damaged.data.max_hp,
		"Units are fully repaired between waves")
	var bonus: int = game.level.coins_per_wave if leaks[0] == 0 else 0
	_check(drops[0] > 0 and game.coins == coins_before + drops[0] + bonus,
		"Kills drop coins (%d dropped, %d leaks, bonus %d)" % [drops[0], leaks[0], bonus])

	# After surviving a wave it can evolve, which costs coins.
	game.coins = 999
	game._select_cell(Vector2i(4, 5))
	game.evolve_selected(evo)
	_check(unit.data == evo and game.coins == 999 - evo.cost, "A veteran unit evolves, costing coins")
	_check(not game.can_evolve(fighter.evolutions[1]), "An evolved unit can't evolve again")

	# Older unit refunds 50%; the evolution bought this round refunds 100%.
	var value: Dictionary = game.sell_value(unit)
	_check(value.coins == int(fighter.cost * 0.5) + evo.cost and not value.to_hand,
		"Old unit refunds 50%, plus 100% of an evolution bought this round")
	value = game.sell_value(board.units[Vector2i(1, 1)])
	_check(value.coins == int(wall.cost * 0.5) and not value.to_hand,
		"Free units from earlier rounds refund 50% of their cost in coins")
	await _stop(game)

	# Store gating.
	var store: Node = root.get_node("Store")
	store.reset_test_purchases()
	game = await _start(biome, 0, 0)
	game.cycle_speed()
	game.cycle_speed()
	_check(game.speed == 1, "4x speed is skipped until it's bought")
	store.buy(store.SPEED_3X)
	game.cycle_speed()
	game.cycle_speed()
	_check(game.speed == 4 and Engine.time_scale == 1.0, "4x speed works once bought (but building stays at 1x)")
	game.start_wave()
	_check(Engine.time_scale == 4.0, "The chosen speed kicks in when the wave starts")
	game._enter_build_phase()
	_check(Engine.time_scale == 1.0, "...and the next build phase is back at 1x")
	game.cycle_speed()
	await _stop(game)
	Engine.time_scale = 1.0
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
	game = await _start(biome, 0, 4)  # Fortress, level 5 (boss)
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
