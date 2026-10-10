extends Node2D
## Runs one level from start to finish:
##   build phase -> wave -> build phase -> wave ... -> level cleared (or lost)
##
## The game owns the "rules" (coins, the player's hand, selling, evolving,
## waves). The Board owns the battlefield itself. Which biome, pack, and level
## to play comes from Progress (set by the menu).

## Selling a unit from an earlier round refunds this share of what it cost.
const OLD_UNIT_REFUND := 0.5
const BOARD_POSITION := Vector2(36, 82)
const BOARD_SCALE := 2.0
const MENU_SCENE := "res://scenes/menu.tscn"
const PREVIEW_FOOTNOTE := "Path preview is only shown in the first level of each biome."

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
	board.setup(level, Progress.biome)
	board.cell_tapped.connect(_on_cell_tapped)
	board.base_hit.connect(_on_base_hit)
	board.coins_dropped.connect(_on_coins_dropped)
	board.shake_requested.connect(shake)
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
	board.wave_active = false
	board.show_path_preview = level.show_path_preview
	var next_wave := level.waves[wave_number]
	board.preview_smashers = _wave_has(next_wave, InvaderData.Movement.SMASHER)
	board.preview_fliers = _wave_has(next_wave, InvaderData.Movement.FLIER)
	board.preview_jumpers = next_wave.entries.any(func(entry): return entry.invader.jumps)
	board.queue_redraw()
	hud.refresh()


## Footnote under the board: tutorial tips and the path preview note.
func footnote() -> String:
	var lines: Array[String] = []
	if phase == Phase.BUILD and wave_number < level.wave_tips.size() and level.wave_tips[wave_number] != "":
		lines.append(level.wave_tips[wave_number])
	if level.show_path_preview:
		lines.append(PREVIEW_FOOTNOTE)
	return "\n".join(lines)


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
			hud.show_message(describe(board.units[cell].data))
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
	if not from_hand and coins < type.cost:
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
		coins -= type.cost
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
			result.coins += unit.base_data.cost
	else:
		result.coins += int(unit.base_data.cost * OLD_UNIT_REFUND)
	if unit.is_evolved():
		if unit.evolved_round == wave_number:
			result.coins += unit.data.cost
		else:
			result.coins += int(unit.data.cost * OLD_UNIT_REFUND)
	return result


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


func can_evolve(into: UnitData) -> bool:
	var unit := selected_unit()
	return (phase == Phase.BUILD and unit != null and not unit.is_evolved()
		and is_veteran(unit) and coins >= into.cost)


func evolve_selected(into: UnitData) -> void:
	if not can_evolve(into):
		return
	var unit := selected_unit()
	coins -= into.cost
	unit.evolve(into)
	Audio.play("evolve", 0.0)
	unit.evolved_round = wave_number
	hud.show_message("Evolved into %s! %s" % [into.display_name, into.description])
	hud.refresh()


func _select_cell(cell: Vector2i) -> void:
	selected_cell = cell
	board.selected_cell = cell
	board.queue_redraw()


# --- Waves ------------------------------------------------------------------

func start_wave() -> void:
	if phase != Phase.BUILD:
		return
	phase = Phase.WAVE
	selected_type = null
	_select_cell(Board.NO_CELL)
	board.show_path_preview = false
	board.wave_active = true
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
	# Same world + level + wave = same piñata surprises.
	board.start_pinata_seeds("%s/%s/%d" % [Progress.biome.id, level.display_name, wave_number])
	Audio.play("wave_start", 0.0)
	wave_number += 1
	hud.show_message("")
	hud.refresh()


func _process(delta: float) -> void:
	if phase != Phase.WAVE:
		return
	_wave_time += delta
	while not _spawn_queue.is_empty() and _spawn_queue[0].time <= _wave_time:
		var spawn: Dictionary = _spawn_queue.pop_front()
		board.spawn_invader(spawn.invader, spawn.spawn)
	if _spawn_queue.is_empty() and board.invaders.is_empty():
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
		coins += level.coins_per_wave
		Audio.play("wave_clear", 0.0)
		hud.show_message("Clean wave! +%s %d bonus. Units repaired." % [Palette.COIN, level.coins_per_wave])
	_enter_build_phase()


func _on_coins_dropped(amount: int, where: Vector2) -> void:
	coins += amount
	hud.spawn_orb(where, amount)


func _on_base_hit(invader: InvaderData) -> void:
	_leaked = true
	Audio.play("base_hit")
	shake(3.0 + invader.base_damage)
	base_hp = max(0, base_hp - invader.base_damage)
	hud.refresh()
	if base_hp == 0 and phase == Phase.WAVE:
		_finish(false)


func _finish(won: bool) -> void:
	phase = Phase.WON if won else Phase.LOST
	board.wave_active = false
	board.process_mode = Node.PROCESS_MODE_DISABLED
	Engine.time_scale = 1.0
	if won:
		Progress.complete_level()
	hud.refresh()
	hud.show_end_screen(won)


## 1x -> 2x -> 3x (if bought in the Store) -> 1x.
## Shakes the board for a moment (bombs, base hits).
func shake(strength: float) -> void:
	var tween := create_tween()
	for i in 6:
		var offset := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * strength * (1.0 - i / 6.0)
		tween.tween_property(board, "position", BOARD_POSITION + offset, 0.03)
	tween.tween_property(board, "position", BOARD_POSITION, 0.03)


func cycle_speed() -> void:
	speed = speed % 3 + 1
	if speed == 3 and not Store.owns(Store.SPEED_3X):
		speed = 1
		hud.show_message("3x speed can be unlocked in the Store.")
	Engine.time_scale = speed
	hud.refresh()


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


## One line of stats for a unit, e.g. "Neutrophil: 2 dmg, range 1.5, ground only."
func describe(type: UnitData) -> String:
	var parts: Array[String] = []
	if type.role == UnitData.Role.WALL or not type.can_attack():
		parts.append("%d HP" % type.max_hp)
	if type.damage > 0.0:
		parts.append("%s dmg%s" % [_num(type.damage), " to all in range" if type.attack_mode == UnitData.AttackMode.PULSE else ""])
	if type.can_attack():
		parts.append("range %s" % _num(type.attack_range))
	if type.splash_radius > 0.0:
		parts.append("splash")
	if type.slow > 0.0:
		parts.append("slows %d%%" % roundi(type.slow * 100))
	if type.stun_duration > 0.0:
		parts.append("stuns %ss" % _num(type.stun_duration))
	if type.poison_dps > 0.0:
		parts.append("poison %s/s%s" % [_num(type.poison_dps), ", spreads" if type.poison_spreads else ""])
	if type.mark_bonus > 0.0:
		parts.append("marks +%d%% dmg" % roundi(type.mark_bonus * 100))
	if type.pierce:
		parts.append("pierces armor")
	if type.reflect > 0.0:
		parts.append("reflects %d%%" % roundi(type.reflect * 100))
	if type.regen > 0.0:
		parts.append("regen %s/s" % _num(type.regen))
	if type.adjacency_bonus > 0.0:
		parts.append("faster in groups")
	if type.can_attack():
		parts.append("hits fliers" if type.hits_air else "ground only")
	return "%s: %s." % [type.display_name, ", ".join(parts)]


func _num(value: float) -> String:
	return str(snappedf(value, 0.1)).trim_suffix(".0")


func _wave_has(wave: WaveData, movement: InvaderData.Movement) -> bool:
	for entry in wave.entries:
		if entry.invader.movement == movement:
			return true
	return false
