extends Node2D
## Runs one level from start to finish:
##   build phase -> wave -> build phase -> wave ... -> level cleared (or lost)
##
## The game owns the "rules" (coins, the player's hand, selling, evolving,
## waves). The Board owns the battlefield itself. Which biome, pack, and level
## to play comes from Progress (set by the menu).

## Selling a unit from an earlier round refunds this share of what it cost.
const OLD_UNIT_REFUND := 0.5
## The most coins the interest relic can pay after one wave.
const INTEREST_CAP := 15
const BOARD_POSITION := Vector2(36, 82)
const BOARD_SCALE := 2.0
const MENU_SCENE := "res://scenes/menu.tscn"

enum Phase { BUILD, WAVE, WON, LOST }

var level: LevelData
var pack: PackData
## 1-based level number inside the biome.
var level_number := 1
var board: Board
var hud: Hud

var phase := Phase.BUILD
## How many waves have been started so far (shown as "Wave 3/10"). During a
## build phase this is also the "round" number used for refunds.
var wave_number := 0
var base_hp := 0
var coins := 0
## Free units left in the player's hand: unit id -> count.
var hand := {}
## Every unit type shown in the bottom bar.
var unit_types: Array[UnitData] = []
## The unit type chosen in the bar (what a tap on an empty tile will place).
var selected_type: UnitData = null
## A placed unit the player tapped (can be evolved or sold).
var selected_cell := Board.NO_CELL
var speed := 1

# Invaders still to appear this wave: {"time", "invader", "spawn"}, sorted by time.
var _spawn_queue: Array[Dictionary] = []
var _wave_time := 0.0
## True once anything reaches the base this wave (no clean-wave bonus).
var _leaked := false
# For achievements: evolutions bought this level, and whether paths were
# ever shown.
var _evolutions := 0
var _paths_seen := false

# --- Relics (see RelicSet and data/relics.json) ---
## The three relics on offer right now (empty when nothing is being offered).
## While an offer is open, the next wave can't start.
var relic_offer: Array = []
## True once this wave's relic carrier was killed.
var _relic_earned := false
## How many relics have been offered this level (later ones roll better).
var _relics_offered := 0


func _ready() -> void:
	Engine.time_scale = 1.0
	if Progress.biome == null:
		# Started directly from the editor: play level 1 with the first pack.
		var biome := Progress.load_biome(0)
		Progress.choose_pack(biome, biome.packs[0])
	pack = Progress.pack
	level_number = Progress.level_index + 1
	level = Progress.biome.levels[Progress.level_index]

	board = Board.new()
	board.position = BOARD_POSITION
	board.scale = Vector2(BOARD_SCALE, BOARD_SCALE)
	add_child(board)
	board.pack_color = pack.color
	board.calm_strength = Progress.calm_strength()
	board.setup(level, Progress.biome)
	board.cell_tapped.connect(_on_cell_tapped)
	board.base_hit.connect(_on_base_hit)
	board.coins_dropped.connect(_on_coins_dropped)
	board.invader_killed.connect(_on_invader_killed)
	board.shake_requested.connect(shake)
	board.relic_dropped.connect(_on_relic_dropped)
	board.relic_lost.connect(_on_relic_lost)
	# Mark where the boss will come from for the whole level.
	var boss_cells: Array[Vector2i] = []
	for wave in level.waves:
		for cell in _boss_spawn_cells(wave):
			if not boss_cells.has(cell):
				boss_cells.append(cell)
	board.show_boss_spawns(boss_cells)
	Audio.play_music(Progress.biome.id)

	base_hp = level.base_hp
	coins = level.starting_coins
	unit_types = pack.units_for_level(level_number)
	for slot in unit_types.size():
		if slot < level.hand_value.size() and level.hand_value[slot] > 0:
			# At least one free copy, then as many as the value buys.
			var copies := maxi(1, roundi(float(level.hand_value[slot]) / unit_types[slot].cost))
			hand[unit_types[slot].id] = copies

	hud = Hud.new()
	add_child(hud)
	hud.setup(self)
	var new_unit := pack.unit_unlocked_on(level_number)
	if new_unit:
		hud.show_message("New unit unlocked: %s. %s" % [new_unit.display_name, new_unit.description])
	_enter_build_phase()


# --- Build phase ------------------------------------------------------------

func _enter_build_phase() -> void:
	phase = Phase.BUILD
	_apply_speed()  # building happens at 1x
	board.wave_active = false
	board.show_path_preview = Progress.show_paths()
	board.show_grid = true
	_paths_seen = _paths_seen or Progress.show_paths()
	var next_wave := level.waves[wave_number]
	board.preview_smashers = _wave_has(next_wave, InvaderData.Movement.SMASHER)
	board.preview_fliers = _wave_has(next_wave, InvaderData.Movement.FLIER)
	board.preview_jumpers = next_wave.entries.any(func(entry): return entry.invader.jumps)
	# Right before the boss wave, show the boss's own route in purple.
	board.preview_boss = null
	for entry in next_wave.entries:
		if entry.invader.is_boss:
			board.preview_boss = entry.invader
	board.preview_boss_spawns = _boss_spawn_cells(next_wave)
	board.queue_redraw()
	hud.refresh()


## Footnote under the board: tutorial tips.
func footnote() -> String:
	if phase == Phase.BUILD and wave_number < level.wave_tips.size():
		return level.wave_tips[wave_number]
	if phase == Phase.BUILD and board.preview_boss:
		return "Boss wave! If %s reaches your base, you lose. Its route is shown in purple." % board.preview_boss.display_name
	return ""


## The "Paths" button: shows or hides the invaders' routes (saved).
func toggle_paths() -> void:
	Progress.set_show_paths(not Progress.show_paths())
	board.show_path_preview = phase == Phase.BUILD and Progress.show_paths()
	_paths_seen = _paths_seen or board.show_path_preview
	board.queue_redraw()
	hud.refresh()


func select_type(type: UnitData) -> void:
	# Tapping the selected type again deselects it.
	selected_type = null if selected_type == type else type
	_select_cell(Board.NO_CELL)
	if selected_type:
		hud.show_message(describe(selected_type))
	Audio.play("button")
	hud.refresh()


## The Cancel button: drops the unit type being placed and any tapped unit.
func cancel_selection() -> void:
	selected_type = null
	_select_cell(Board.NO_CELL)
	hud.show_message("")
	hud.refresh()


## True while something is selected (so the HUD shows the Cancel button).
func has_selection() -> bool:
	return phase == Phase.BUILD and (selected_type != null or selected_cell != Board.NO_CELL)


func _on_cell_tapped(cell: Vector2i) -> void:
	if phase == Phase.WON or phase == Phase.LOST:
		return
	if board.units.has(cell):
		_select_cell(Board.NO_CELL if selected_cell == cell else cell)
		if selected_cell != Board.NO_CELL:
			hud.show_message(describe(board.units[cell].data, board.units[cell]))
	elif phase == Phase.BUILD and selected_type:
		try_place(selected_type, cell)
	else:
		_select_cell(Board.NO_CELL)
	hud.refresh()


## Places a unit, paying from the hand if possible, otherwise with coins.
## Returns true if it was placed.
func try_place(type: UnitData, cell: Vector2i) -> bool:
	_select_cell(Board.NO_CELL)
	var on_water: bool = board.water.has(cell)
	if phase != Phase.BUILD or (not on_water and not board.is_buildable(cell)):
		board.flash(cell)
		Audio.play("deny")
		return false
	if on_water and not type.can_place_on_water:
		board.flash(cell)
		Audio.play("deny")
		hud.show_message("Only your basic wall can go on water (as a net or mine).")
		return false
	var from_hand: bool = hand.get(type.id, 0) > 0
	if not from_hand and coins < unit_cost(type):
		board.flash(cell)
		Audio.play("deny")
		hud.show_message("Not enough coins.")
		return false
	if not board.can_place_unit(type, cell):
		board.flash(cell)
		Audio.play("deny")
		hud.show_message("Can't seal the path completely!")
		return false

	if from_hand:
		hand[type.id] -= 1
	else:
		coins -= unit_cost(type)
	var unit := board.place_unit(type, cell)
	Audio.play("place")
	unit.placed_round = wave_number
	unit.from_hand = from_hand
	return true


func selected_unit() -> Unit:
	return board.units.get(selected_cell)


## Units bought or evolved during this build phase refund fully (free units
## go back to the hand). Anything older refunds half its coin cost.
## Returns {"coins": int, "to_hand": bool}.
func sell_value(unit: Unit) -> Dictionary:
	var result := {"coins": 0, "to_hand": false}
	if unit.placed_round == wave_number:
		if unit.from_hand:
			result.to_hand = true
		else:
			result.coins += unit_cost(unit.base_data)
	elif unit.base_data.role == UnitData.Role.WALL and board.relics.economy("wall_refund") > 0.0:
		result.coins += unit_cost(unit.base_data)  # Flat Pack: walls always refund fully
	else:
		result.coins += int(unit_cost(unit.base_data) * old_refund())
	# Each evolution refunds by the same rule, by the round it was bought in.
	if unit.tier1_data:
		result.coins += _refund(evolve_cost(unit.tier1_data), unit.evolved_round)
	if unit.is_capstone():
		result.coins += _refund(evolve_cost(unit.data), unit.capstone_round)
	return result


func _refund(cost: int, bought_round: int) -> int:
	return cost if bought_round == wave_number else int(cost * old_refund())


## What placing a unit costs right now. Wall relics (Bulk Bricks, Labyrinth)
## make walls cheaper, down to 1 coin; a few epics (Labyrinth, Philosopher's
## Stone) make every other unit pricier.
func unit_cost(type: UnitData) -> int:
	if type.role == UnitData.Role.WALL:
		return maxi(1, type.cost - roundi(board.relics.economy("wall_discount")))
	return roundi(type.cost * (1.0 + board.relics.economy("unit_markup")))


## Share refunded for units from earlier rounds (a relic can raise it).
func old_refund() -> float:
	return maxf(OLD_UNIT_REFUND, board.relics.economy("refund_old"))


## What an evolution costs right now (relics can discount it).
func evolve_cost(into: UnitData) -> int:
	var discount := minf(0.75, board.relics.economy("evolve_discount"))
	return roundi(into.cost * (1.0 - discount))


func can_sell() -> bool:
	return phase == Phase.BUILD and selected_unit() != null


func sell_selected() -> void:
	if not can_sell():
		return
	var unit := selected_unit()
	var value := sell_value(unit)
	coins += value.coins
	if value.to_hand:
		hand[unit.base_data.id] = hand.get(unit.base_data.id, 0) + 1
	var unit_name := unit.data.display_name
	board.remove_unit(selected_cell)
	Audio.play("sell")
	_select_cell(Board.NO_CELL)
	if value.to_hand:
		hud.show_message("%s returned to your hand." % unit_name)
	else:
		hud.show_message("Removed %s for %s %d." % [unit_name, Palette.COIN, value.coins])
	hud.refresh()


## True once a unit has survived a wave (it can't evolve the round it's placed).
func is_veteran(unit: Unit) -> bool:
	return unit.placed_round < wave_number


## True once a unit has survived a wave since it was placed (for its first
## evolution) or since its first evolution (for a capstone).
func is_ready_to_evolve(unit: Unit) -> bool:
	if unit.data.tier == 0:
		return is_veteran(unit)
	return unit.evolved_round < wave_number


func can_evolve(into: UnitData) -> bool:
	var unit := selected_unit()
	return (phase == Phase.BUILD and unit != null and unit.data.evolutions.has(into)
		and is_ready_to_evolve(unit) and coins >= evolve_cost(into))


func evolve_selected(into: UnitData) -> void:
	if not can_evolve(into):
		return
	var unit := selected_unit()
	coins -= evolve_cost(into)
	unit.evolve(into)
	Audio.play("evolve", 0.0)
	_evolutions += 1
	Achievements.on_evolved(into)
	if into.tier == 2:
		unit.capstone_round = wave_number
		hud.show_message("Capstone: %s! %s" % [into.display_name, into.description])
	else:
		unit.evolved_round = wave_number
		hud.show_message("Evolved into %s! %s" % [into.display_name, into.description])
	hud.refresh()


func _select_cell(cell: Vector2i) -> void:
	selected_cell = cell
	board.selected_cell = cell
	board.queue_redraw()


# --- Waves ------------------------------------------------------------------

func start_wave() -> void:
	if phase != Phase.BUILD or not relic_offer.is_empty():
		return
	phase = Phase.WAVE
	selected_type = null
	_select_cell(Board.NO_CELL)
	board.show_path_preview = false
	board.show_grid = false
	board.preview_boss = null
	board.wave_active = true
	_apply_speed()
	board.queue_redraw()

	# Turn the wave's groups into a single timeline of spawns.
	_spawn_queue.clear()
	var alternate := 0
	for entry in level.waves[wave_number].entries:
		for i in entry.count:
			var spawn: int = entry.spawn_point
			if spawn < 0:
				spawn = alternate
				alternate += 1
			_spawn_queue.append({"time": entry.delay + i * entry.spacing, "invader": entry.invader, "spawn": spawn})
	_spawn_queue.sort_custom(func(a, b): return a.time < b.time)
	_wave_time = 0.0
	_leaked = false
	_relic_earned = false
	_activate_relics()
	if RelicSet.RELIC_WAVES.has(wave_number + 1):
		_pick_relic_carrier()
	# Same world + level + wave = same piñata surprises.
	board.start_pinata_seeds("%s/%s/%d" % [Progress.biome.id, level.display_name, wave_number])
	Audio.play("wave_start", 0.0)
	wave_number += 1
	hud.show_message("A glowing invader carries a relic! Defeat it to choose an upgrade." \
		if _spawn_queue.any(func(spawn): return spawn.get("carrier", false)) else "")
	hud.refresh()


func _process(delta: float) -> void:
	if phase != Phase.WAVE:
		return
	_wave_time += delta
	while not _spawn_queue.is_empty() and _spawn_queue[0].time <= _wave_time:
		var spawn: Dictionary = _spawn_queue.pop_front()
		var invader := board.spawn_invader(spawn.invader, spawn.spawn)
		invader.carries_relic = spawn.get("carrier", false)
	# The wave ends once everything has spawned, died or arrived, and any
	# falling bomb has landed.
	if _spawn_queue.is_empty() and board.invaders.is_empty() and not board.has_falling_bombs():
		_end_wave()


func _end_wave() -> void:
	board.wave_active = false
	board.restore_units()
	if wave_number >= level.waves.size():
		_finish(true)
		return
	if _leaked:
		hud.show_message("Wave cleared. Units repaired. (No bonus: something got through.)")
	else:
		var bonus := roundi(level.coins_per_wave * (1.0 + board.relics.economy("clean_bonus_mult")))
		_earn_coins(bonus)
		Audio.play("wave_clear", 0.0)
		hud.show_message("Clean wave! +%s %d bonus. Units repaired." % [Palette.COIN, bonus])
	# Flat Pack: free walls for the next build phase.
	var walls := roundi(board.relics.economy("wave_walls"))
	if walls > 0:
		hand[unit_types[0].id] = hand.get(unit_types[0].id, 0) + walls
	# Interest relic: a share of the coins you saved.
	var interest := board.relics.economy("interest")
	if interest > 0.0:
		_earn_coins(mini(INTEREST_CAP, int(coins * interest)))
	_enter_build_phase()
	if _relic_earned:
		_offer_relics()


func _on_coins_dropped(amount: int, where: Vector2) -> void:
	_earn_coins(amount)
	hud.spawn_orb(where, amount)


## Coins earned by playing (drops and bonuses, not refunds) count toward
## achievements.
func _earn_coins(amount: int) -> void:
	coins += amount
	Achievements.add_stat("coins", amount)
	Achievements.coins_now(coins)


func _on_invader_killed(invader: Invader) -> void:
	Achievements.add_stat("kills", 1)
	# Coin relics: extra coins per kill.
	var extra := roundi(board.relics.economy("kill_coins"))
	if extra > 0 and invader.drops_coins:
		_on_coins_dropped(extra, board.to_global(invader.position))
	if not invader.data.pinata_pool.is_empty():
		Achievements.add_stat("pinatas", 1)


func _on_base_hit(invader: InvaderData) -> void:
	_leaked = true
	Audio.play("base_hit")
	shake(3.0 + invader.base_damage)
	if invader.is_boss:
		# A boss reaching the base is always an instant loss.
		base_hp = 0
	else:
		base_hp = max(0, base_hp - invader.base_damage)
	board.hit_base(float(base_hp) / level.base_hp)
	hud.refresh()
	if base_hp == 0 and phase == Phase.WAVE:
		_finish(false)


## Levels of this world the pack had beaten before the current win.
var pack_levels_before := 0


func _finish(won: bool) -> void:
	phase = Phase.WON if won else Phase.LOST
	board.wave_active = false
	board.process_mode = Node.PROCESS_MODE_DISABLED
	Engine.time_scale = 1.0
	if won:
		# How full the pack's symbol was before this win (the victory screen
		# animates it filling up).
		pack_levels_before = Progress.levels_beaten_by(Progress.biome.id, pack.id)
		Progress.complete_level()
		Achievements.on_level_won({"base_hp": base_hp, "max_hp": level.base_hp,
			"boss_level": is_last_level(), "evolutions": _evolutions,
			"paths_seen": _paths_seen, "units": board.units.size()})
	hud.refresh()
	hud.show_end_screen(won)


## Shakes the board for a moment (bombs, base hits).
func shake(strength: float) -> void:
	var tween := create_tween()
	for i in 6:
		var offset := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * strength * (1.0 - i / 6.0)
		tween.tween_property(board, "position", BOARD_POSITION + offset, 0.03)
	tween.tween_property(board, "position", BOARD_POSITION, 0.03)


## The speeds the speed button cycles through. The fastest needs the Store
## upgrade (its product id is still "speed_3x" so old purchases keep working).
const SPEEDS := [1, 2, 4]


## 1x -> 2x -> 4x (if bought in the Store) -> 1x. The chosen speed only runs
## during waves: building always happens at 1x, so starting a wave visibly
## speeds things up.
func cycle_speed() -> void:
	speed = SPEEDS[(SPEEDS.find(speed) + 1) % SPEEDS.size()]
	if speed == SPEEDS[-1] and not Store.owns(Store.SPEED_3X):
		speed = 1
		hud.show_message("4x speed can be unlocked in the Store.")
	_apply_speed()
	hud.refresh()


## Waves run at the chosen speed; the build phase always runs at 1x.
func _apply_speed() -> void:
	Engine.time_scale = speed if phase == Phase.WAVE else 1


# --- Relics -------------------------------------------------------------------
## Relics drop on every level, teaching levels included (the user wants
## them introduced early; a weak pick never hurts).

## Picks which invader of this wave carries the relic: the toughest one that
## isn't a boss (the latest of equals), so it's a real target.
func _pick_relic_carrier() -> void:
	var best := -1
	for i in _spawn_queue.size():
		var invader: InvaderData = _spawn_queue[i].invader
		if invader.is_boss:
			continue
		if best < 0 or invader.max_hp >= _spawn_queue[best].invader.max_hp:
			best = i
	if best >= 0:
		_spawn_queue[best]["carrier"] = true


func _on_relic_dropped(where: Vector2) -> void:
	_relic_earned = true
	Audio.play("coins")
	board.fx.add_pulse(where, Board.TILE * 1.6, RelicSet.RARITY_COLORS.epic)
	board.fx.add_puff(where, Palette.GOLD)
	hud.show_message("Relic dropped! Choose one when the wave ends.")


func _on_relic_lost() -> void:
	hud.show_message("The relic carrier got through. That relic is lost!")


## Rolls three random relics and opens the picker. Offers are truly random
## (different every time), for variety and replayability.
func _offer_relics() -> void:
	relic_offer = board.relics.roll_offer(unit_types, _relics_offered, randi())
	_relics_offered += 1
	if relic_offer.is_empty():
		return
	hud.show_relic_picker(relic_offer)
	hud.refresh()


## The player chose relic `index` from the offer. It starts working when the
## next wave starts.
func pick_relic(index: int) -> void:
	if index < 0 or index >= relic_offer.size():
		return
	var relic: Dictionary = relic_offer[index]
	board.relics.add_pending(relic)
	relic_offer = []
	hud.close_relic_picker()
	Audio.play("evolve", 0.0)
	# One-time rewards (coins, healing, free walls) pay out right away;
	# lasting effects start with the next wave.
	if _apply_instant_relic(relic):
		hud.show_message("%s: %s" % [relic.name, relic.desc])
	else:
		hud.show_message("%s: %s It starts working next wave." % [relic.name, relic.desc])
	hud.refresh()


## Pays out a relic's one-time rewards. Returns true if it had any.
func _apply_instant_relic(relic: Dictionary) -> bool:
	var economy: Dictionary = relic.get("economy", {})
	var any := false
	if economy.has("gift_coins"):
		_earn_coins(int(economy.gift_coins))
		any = true
	if economy.has("base_heal"):
		base_hp = mini(level.base_hp, base_hp + int(economy.base_heal))
		board.set_base_health(float(base_hp) / level.base_hp)
		any = true
	if economy.has("free_walls"):
		var wall := unit_types[0]
		hand[wall.id] = hand.get(wall.id, 0) + int(economy.free_walls)
		any = true
	return any


## At the start of a wave: picked relics turn on, and every unit is topped up
## to its (possibly higher) health.
func _activate_relics() -> void:
	board.relics.activate_pending()
	var per_wave := roundi(board.relics.economy("wave_coins"))
	if per_wave > 0:
		_earn_coins(per_wave)
	for cell in board.units:
		var unit: Unit = board.units[cell]
		unit.hp = unit.max_hp()
		unit.queue_redraw()


func is_last_level() -> bool:
	return Progress.level_index + 1 >= Progress.biome.levels.size()


func retry() -> void:
	get_tree().reload_current_scene()


func next_level() -> void:
	Progress.level_index += 1
	get_tree().reload_current_scene()


## From the final victory screen: straight to the Store's bonus worlds.
func open_store() -> void:
	Engine.time_scale = 1.0
	Progress.return_screen = "store"
	get_tree().change_scene_to_file(MENU_SCENE)


func quit_to_menu() -> void:
	Engine.time_scale = 1.0
	Progress.return_screen = "biomes" if phase == Phase.WON and is_last_level() else "levels"
	get_tree().change_scene_to_file(MENU_SCENE)


# --- Text helpers -----------------------------------------------------------

## A short summary of the next wave, e.g. "6 Rhinovirus, 2 Parasite Worm".
func next_wave_summary() -> String:
	if wave_number >= level.waves.size() or phase != Phase.BUILD:
		return ""
	var counts := {}
	var order: Array[String] = []
	for entry in level.waves[wave_number].entries:
		var invader_name := entry.invader.display_name
		if not counts.has(invader_name):
			order.append(invader_name)
		counts[invader_name] = counts.get(invader_name, 0) + entry.count
	var parts: Array[String] = []
	for invader_name in order:
		parts.append("%d %s" % [counts[invader_name], invader_name])
	return "Next: " + ", ".join(parts)


## One line of stats for a unit, e.g.
## "White Blood Cell: 2 dmg, range 1.5, 1.2 shots/s, ground only."
## Pass the placed `unit` to show its current fire rate (with bonuses).
func describe(type: UnitData, unit: Unit = null) -> String:
	var parts: Array[String] = []
	if type.role == UnitData.Role.WALL or not type.can_attack():
		parts.append("%d HP" % _stat(type, unit, "max_hp"))
	if _stat(type, unit, "damage") > 0.0:
		parts.append("%s dmg%s" % [_num(_stat(type, unit, "damage")), " to all in range" if type.attack_mode == UnitData.AttackMode.PULSE else ""])
	if type.can_attack():
		parts.append("range %s" % _num(_stat(type, unit, "attack_range")))
		parts.append(_fire_rate(type, unit))
	if _stat(type, unit, "splash_radius") > 0.0:
		parts.append("splash")
	if _stat(type, unit, "slow") > 0.0:
		parts.append("slows %d%%" % roundi(minf(0.8, _stat(type, unit, "slow")) * 100))
	if _stat(type, unit, "stun_duration") > 0.0:
		parts.append("stuns %ss" % _num(_stat(type, unit, "stun_duration")))
	if _stat(type, unit, "poison_dps") > 0.0:
		parts.append("poison %s/s%s" % [_num(_stat(type, unit, "poison_dps")), ", spreads" if _has(type, unit, "poison_spreads") else ""])
	if _stat(type, unit, "mark_bonus") > 0.0:
		parts.append("marks +%d%% dmg" % roundi(_stat(type, unit, "mark_bonus") * 100))
	if _has(type, unit, "pierce"):
		parts.append("pierces armor")
	if _stat(type, unit, "reflect") > 0.0:
		parts.append("reflects %d%%" % roundi(_stat(type, unit, "reflect") * 100))
	if _stat(type, unit, "regen") > 0.0:
		parts.append("regen %s/s" % _num(_stat(type, unit, "regen")))
	if type.adjacency_bonus > 0.0:
		parts.append("faster in groups")
	# Capstone mechanics.
	if roundi(_stat(type, unit, "chain_count")) > 0:
		parts.append("chains to %d" % roundi(_stat(type, unit, "chain_count")))
	if roundi(_stat(type, unit, "multishot")) > 1:
		parts.append("hits %d targets" % roundi(_stat(type, unit, "multishot")))
	if type.line_pierce:
		parts.append("pierces the line")
	if type.execute_below > 0.0:
		parts.append("executes below %d%%" % roundi(type.execute_below * 100))
	if type.knockback > 0:
		parts.append("knocks back %d" % type.knockback)
	if type.armor_shred > 0:
		parts.append("shreds %d armor" % type.armor_shred)
	if type.bounty > 0:
		parts.append("kills +%s %d" % [Palette.COIN, type.bounty])
	if type.zone_kind != "":
		parts.append("leaves %s patches" % {"burn": "burning", "freeze": "freezing", "toxic": "toxic"}[type.zone_kind])
	if type.grab_stun > 0.0:
		parts.append("grabs smashers %ss" % _num(type.grab_stun))
	if type.explode_damage > 0.0:
		parts.append("explodes for %s" % _num(type.explode_damage))
	if _has(type, unit, "rebuild"):
		parts.append("rebuilds once")
	if type.aura_speed > 0.0:
		parts.append("neighbors +%d%% speed" % roundi(type.aura_speed * 100))
	if type.aura_shield > 0.0:
		parts.append("neighbors -%d%% damage" % roundi(type.aura_shield * 100))
	if type.aura_cleanse:
		parts.append("neighbors ignore goo")
	# Wall relics (only on placed units: they come from relics, not data).
	if unit and unit.stat("wall_slow") > 0.0:
		parts.append("slows neighbors %d%%" % roundi(minf(0.6, unit.stat("wall_slow")) * 100))
	if unit and unit.stat("wall_burn") > 0.0:
		parts.append("burns neighbors %s/s" % _num(unit.stat("wall_burn")))
	# Relics that depend on where it stands or whether it evolved
	# (walls, neighbors, evolutions), added up: "relics +25% dmg here".
	if unit and type.can_attack() and absf(unit.self_bonus()) > 0.001:
		parts.append("relics %+d%% dmg here" % roundi(unit.self_bonus() * 100))
	if type.can_attack():
		parts.append("hits fliers" if _has(type, unit, "hits_air") else "ground only")
	return "%s: %s." % [type.display_name, ", ".join(parts)]


## A stat for the info line: a placed unit shows it with relics applied.
func _stat(type: UnitData, unit: Unit, name: String) -> float:
	return unit.stat(name) if unit else float(type.get(name))


func _has(type: UnitData, unit: Unit, ability: String) -> bool:
	return unit.has_ability(ability) if unit else bool(type.get(ability))


## Fire rate as "1.5 shots/s". For a placed unit whose speed is changed by
## neighbors, auras or goo: "2.1 shots/s (base 1.5)".
func _fire_rate(type: UnitData, unit: Unit) -> String:
	var base := 1.0 / type.attack_interval
	var now := base * unit.speed_multiplier() if unit else base
	if _num(now) == _num(base):
		return "%s shots/s" % _num(base)
	return "%s shots/s (base %s)" % [_num(now), _num(base)]


## What changes when `from` evolves into `to`, e.g.
## "dmg 9 → 17, HP 60 → 80, new: chains to 2." Used by the upgrade preview.
func stat_changes(from: UnitData, to: UnitData) -> String:
	var parts: Array[String] = []
	var numbers := [["HP", from.max_hp, to.max_hp], ["dmg", from.damage, to.damage],
		["range", from.attack_range, to.attack_range],
		["shots/s", 1.0 / from.attack_interval, 1.0 / to.attack_interval],
		["splash", from.splash_radius, to.splash_radius], ["regen", from.regen, to.regen],
		["slow %", from.slow * 100, to.slow * 100], ["stun", from.stun_duration, to.stun_duration],
		["poison", from.poison_dps, to.poison_dps], ["mark %", from.mark_bonus * 100, to.mark_bonus * 100],
		["reflect %", from.reflect * 100, to.reflect * 100]]
	for row in numbers:
		if not is_equal_approx(row[1], row[2]):
			parts.append("%s %s \u2192 %s" % [row[0], _num(row[1]), _num(row[2])])
	if to.hits_air and not from.hits_air:
		parts.append("now hits fliers")
	if to.pierce and not from.pierce:
		parts.append("now pierces armor")
	# Anything describe() mentions that the old unit didn't have (new mechanics).
	var before := describe(from).split(": ", true, 1)[1].trim_suffix(".").split(", ")
	for part in describe(to).split(": ", true, 1)[1].trim_suffix(".").split(", "):
		if not before.has(part) and not _is_number_part(part):
			parts.append("new: " + part)
	return ", ".join(parts) if not parts.is_empty() else "no stat changes"


## describe() parts that stat_changes() already shows as numbers.
func _is_number_part(part: String) -> bool:
	for prefix in ["HP", "range", "slows", "stuns", "poison", "marks", "reflects", "regen", "splash",
			"hits fliers", "ground only", "pierces armor"]:
		if part.begins_with(prefix):
			return true
	return part.contains(" dmg") or part.contains("shots/s")


func _num(value: float) -> String:
	return str(snappedf(value, 0.1)).trim_suffix(".0")


## The spawn tiles the bosses in a wave come from. Uses the same rule as
## start_wave(): entries with spawn_point -1 take turns between spawns.
func _boss_spawn_cells(wave: WaveData) -> Array[Vector2i]:
	var cells: Array[Vector2i] = []
	var alternate := 0
	for entry in wave.entries:
		for i in entry.count:
			var spawn: int = entry.spawn_point
			if spawn < 0:
				spawn = alternate
				alternate += 1
			if entry.invader.is_boss:
				var cell := board.spawn_cell_for(entry.invader, spawn)
				if not cells.has(cell):
					cells.append(cell)
	return cells


func _wave_has(wave: WaveData, movement: InvaderData.Movement) -> bool:
	for entry in wave.entries:
		if entry.invader.movement == movement:
			return true
	return false
