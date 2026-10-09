extends Node2D
## Runs one level from start to finish:
##   build phase -> wave -> build phase -> wave ... -> level cleared (or lost)
##
## The game owns the "rules" (ATP, the player's hand, undo, selling, waves).
## The Board owns the battlefield itself.

const LEVELS: Array[String] = [
	"res://data/levels/level_01.tres",
	"res://data/levels/level_02.tres",
]
const SELL_REFUND := 0.75
const BOARD_POSITION := Vector2(36, 96)
const BOARD_SCALE := 2.0

enum Phase { BUILD, WAVE, WON, LOST }

## Which level to load. "static" so it survives reloading the scene.
static var level_index := 0

var level: LevelData
var board: Board
var hud: Hud

var phase := Phase.BUILD
## How many waves have been started so far (shown as "Wave 3/10").
var wave_number := 0
var base_hp := 0
var atp := 0
## Free units left in the player's hand: unit id -> count.
var hand := {}
## Every unit type shown in the bottom bar.
var unit_types: Array[UnitData] = []
## The unit type chosen in the bar (what a tap on an empty tile will place).
var selected_type: UnitData = null
## A placed unit the player tapped (can be sold).
var selected_cell := Board.NO_CELL
var speed := 1

# Each entry records one build action so it can be undone:
#   {"action": "place", "cell", "type", "paid_with": "hand" or "atp"}
#   {"action": "sell",  "cell", "type", "refund"}
var _undo_stack: Array[Dictionary] = []
# Invaders still to appear this wave: {"time", "invader", "spawn"}, sorted by time.
var _spawn_queue: Array[Dictionary] = []
var _wave_time := 0.0


func _ready() -> void:
	Engine.time_scale = 1.0
	level = load(LEVELS[level_index])

	board = Board.new()
	board.position = BOARD_POSITION
	board.scale = Vector2(BOARD_SCALE, BOARD_SCALE)
	add_child(board)
	board.setup(level)
	board.cell_tapped.connect(_on_cell_tapped)
	board.base_hit.connect(_on_base_hit)

	base_hp = level.base_hp
	atp = level.starting_atp
	for unit in level.starting_hand:
		hand[unit.id] = hand.get(unit.id, 0) + 1
		if not unit_types.has(unit):
			unit_types.append(unit)
	for unit in level.shop:
		if not unit_types.has(unit):
			unit_types.append(unit)

	hud = Hud.new()
	add_child(hud)
	hud.setup(self)
	_enter_build_phase()


# --- Build phase ------------------------------------------------------------

func _enter_build_phase() -> void:
	phase = Phase.BUILD
	board.wave_active = false
	board.show_path_preview = true
	var next_wave := level.waves[wave_number]
	board.preview_smashers = _wave_has(next_wave, InvaderData.Movement.SMASHER)
	board.preview_fliers = _wave_has(next_wave, InvaderData.Movement.FLIER)
	board.queue_redraw()
	hud.refresh()


func select_type(type: UnitData) -> void:
	# Tapping the selected type again deselects it.
	selected_type = null if selected_type == type else type
	_select_cell(Board.NO_CELL)
	if selected_type:
		hud.show_message(_describe(selected_type))
	hud.refresh()


func _on_cell_tapped(cell: Vector2i) -> void:
	if phase == Phase.WON or phase == Phase.LOST:
		return
	if board.units.has(cell):
		_select_cell(cell)
		hud.show_message(_describe(board.units[cell].data))
	elif phase == Phase.BUILD and selected_type:
		_try_place(selected_type, cell)
	else:
		_select_cell(Board.NO_CELL)
	hud.refresh()


func _try_place(type: UnitData, cell: Vector2i) -> void:
	_select_cell(Board.NO_CELL)
	if not board.is_buildable(cell):
		board.flash(cell)
		return
	var paid_with := ""
	if hand.get(type.id, 0) > 0:
		paid_with = "hand"
	elif level.shop.has(type) and atp >= type.cost:
		paid_with = "atp"
	else:
		board.flash(cell)
		hud.show_message("Not enough ATP." if level.shop.has(type) else "None left.")
		return
	if not board.can_place(cell):
		board.flash(cell)
		hud.show_message("Can't seal the path completely!")
		return

	if paid_with == "hand":
		hand[type.id] -= 1
	else:
		atp -= type.cost
	board.place_unit(type, cell)
	_undo_stack.append({"action": "place", "cell": cell, "type": type, "paid_with": paid_with})


func can_sell() -> bool:
	return phase == Phase.BUILD and board.units.has(selected_cell)


func sell_selected() -> void:
	if not can_sell():
		return
	var cell := selected_cell
	var type: UnitData = board.units[cell].data
	var refund := int(type.cost * SELL_REFUND)
	atp += refund
	board.remove_unit(cell)
	_undo_stack.append({"action": "sell", "cell": cell, "type": type, "refund": refund})
	_select_cell(Board.NO_CELL)
	hud.show_message("Sold %s for %d ATP." % [type.display_name, refund])
	hud.refresh()


func can_undo() -> bool:
	return phase == Phase.BUILD and not _undo_stack.is_empty()


func undo() -> void:
	if not can_undo():
		return
	var step: Dictionary = _undo_stack.pop_back()
	if step.action == "place":
		board.remove_unit(step.cell)
		if step.paid_with == "hand":
			hand[step.type.id] += 1
		else:
			atp += step.type.cost
	elif step.action == "sell":
		board.place_unit(step.type, step.cell)
		atp -= step.refund
	_select_cell(Board.NO_CELL)
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
	_undo_stack.clear()
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
	atp += level.atp_per_wave
	hud.show_message("Wave cleared! Units repaired, +%d ATP." % level.atp_per_wave)
	_enter_build_phase()


func _on_base_hit(invader: InvaderData) -> void:
	base_hp = max(0, base_hp - invader.base_damage)
	hud.refresh()
	if base_hp == 0 and phase == Phase.WAVE:
		_finish(false)


func _finish(won: bool) -> void:
	phase = Phase.WON if won else Phase.LOST
	board.wave_active = false
	board.process_mode = Node.PROCESS_MODE_DISABLED
	Engine.time_scale = 1.0
	hud.refresh()
	hud.show_end_screen(won, won and has_next_level())


func cycle_speed() -> void:
	speed = speed % 3 + 1
	Engine.time_scale = speed
	hud.refresh()


func has_next_level() -> bool:
	return level_index + 1 < LEVELS.size()


func retry() -> void:
	get_tree().reload_current_scene()


func next_level() -> void:
	level_index += 1
	get_tree().reload_current_scene()


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


func _describe(type: UnitData) -> String:
	if type.role == UnitData.Role.WALL:
		return "%s: wall, %d HP." % [type.display_name, type.max_hp]
	return "%s: %d dmg, range %.1f%s." % [type.display_name, type.damage,
		type.attack_range, ", hits fliers" if type.hits_air else ", ground only"]


func _wave_has(wave: WaveData, movement: InvaderData.Movement) -> bool:
	for entry in wave.entries:
		if entry.invader.movement == movement:
			return true
	return false
