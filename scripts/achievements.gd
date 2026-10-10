extends Node
## Achievements. Loaded automatically at startup as "Achievements".
##
## The list itself lives in data/achievements.json (name, goal, and a "kind"
## that says how it's earned), so new achievements need no new code unless
## they need a new kind. Progress is saved to user://achievements.json.
## When one is earned, a banner slides in at the top of the screen.

signal earned(id: String)

const LIST_PATH := "res://data/achievements.json"
const SAVE_PATH := "user://achievements.json"
## The 12 capstone mechanics counted by "Capstone Collector".
const MECHANICS := ["chain", "multishot", "line", "execute", "knockback", "shred",
	"bounty", "zone", "grab", "explode", "rebuild", "aura"]

## Every achievement, in display order (from data/achievements.json).
var list: Array = []
# Saved: {"earned": {id: unix time}, "stats": {name: count}, "mechanics": [names]}
var _data := {"earned": {}, "stats": {}, "mechanics": []}

var _banner_queue: Array[String] = []
var _banner_showing := false
var _layer: CanvasLayer


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	list = JSON.parse_string(FileAccess.get_file_as_string(LIST_PATH))
	_load()
	_layer = CanvasLayer.new()
	_layer.layer = 50
	add_child(_layer)
	# Credit anything already earned through saved progress (e.g. old saves).
	check_progress.call_deferred(false)


func find(id: String) -> Dictionary:
	for item in list:
		if item.id == id:
			return item
	return {}


func is_earned(id: String) -> bool:
	return _data.earned.has(id)


func earned_count() -> int:
	return _data.earned.size()


## How far along a locked achievement is: [current, target]. Achievements
## that happen all at once (like "Flawless") report [0, 1] or [1, 1].
func progress_of(item: Dictionary) -> Array:
	var progress := get_node("/root/Progress")
	var current := 0
	match item.kind:
		"world":
			current = progress.cleared(item.param)
		"main_game":
			current = _main_worlds_beaten()
		"mastery":
			current = progress.main_levels_beaten(item.param)
		"all_mastery":
			for pack_id in ["fortress", "swarm", "precision", "control", "toxin"]:
				if progress.main_levels_beaten(pack_id) >= progress.main_level_count():
					current += 1
		"mechanics":
			current = _data.mechanics.size()
		"stat":
			current = int(_data.stats.get(item.param, 0))
		_:
			current = 1 if is_earned(item.id) else 0
	if is_earned(item.id):
		current = int(item.target)
	return [mini(current, int(item.target)), int(item.target)]


# --- Events from the game -------------------------------------------------

## Adds to a running total ("coins", "kills", "pinatas").
func add_stat(stat: String, amount: int) -> void:
	_data.stats[stat] = int(_data.stats.get(stat, 0)) + amount
	for item in list:
		if item.kind == "stat" and item.param == stat and _data.stats[stat] >= item.target:
			unlock(item.id)
	_save_soon()


## The player's coins right now (for "Big Spender").
func coins_now(amount: int) -> void:
	for item in list:
		if item.kind == "coins_at_once" and amount >= item.target:
			unlock(item.id)


## A unit evolved (tier 1) or became a capstone (tier 2).
func on_evolved(into: UnitData) -> void:
	_unlock_kind("evolve")
	if into.tier == 2:
		_unlock_kind("capstone")
		for mechanic in mechanics_of(into):
			if not _data.mechanics.has(mechanic):
				_data.mechanics.append(mechanic)
		for item in list:
			if item.kind == "mechanics" and _data.mechanics.size() >= item.target:
				unlock(item.id)
		_save()


## A level was won. `info` has: base_hp, max_hp, boss_level, evolutions,
## paths_seen, units.
func on_level_won(info: Dictionary) -> void:
	if info.base_hp >= info.max_hp:
		_unlock_kind("flawless")
		if info.boss_level:
			_unlock_kind("flawless_boss")
	if info.base_hp == 1:
		_unlock_kind("close_call")
	if info.evolutions == 0:
		_unlock_kind("no_evolve")
	if info.boss_level and not info.paths_seen:
		_unlock_kind("blind_boss")
	for item in list:
		if item.kind == "minimalist" and info.units <= item.target:
			unlock(item.id)
	check_progress(true)


## Checks the achievements that come from saved progress (worlds beaten,
## pack mastery). `announce` shows the banner for newly earned ones.
func check_progress(announce := true) -> void:
	for item in list:
		if not is_earned(item.id) and item.kind in ["world", "main_game", "mastery", "all_mastery"]:
			var amounts := progress_of(item)
			if amounts[0] >= amounts[1]:
				unlock(item.id, announce)


## The capstone mechanics a unit has (for "Capstone Collector").
static func mechanics_of(unit: UnitData) -> Array[String]:
	var found: Array[String] = []
	if unit.chain_count > 0: found.append("chain")
	if unit.multishot > 1: found.append("multishot")
	if unit.line_pierce: found.append("line")
	if unit.execute_below > 0.0: found.append("execute")
	if unit.knockback > 0: found.append("knockback")
	if unit.armor_shred > 0: found.append("shred")
	if unit.bounty > 0: found.append("bounty")
	if unit.zone_kind != "": found.append("zone")
	if unit.grab_stun > 0.0: found.append("grab")
	if unit.explode_damage > 0.0: found.append("explode")
	if unit.rebuild: found.append("rebuild")
	if unit.aura_speed > 0.0 or unit.aura_shield > 0.0 or unit.aura_cleanse: found.append("aura")
	return found


# --- Earning --------------------------------------------------------------

func unlock(id: String, announce := true) -> void:
	if is_earned(id) or find(id).is_empty():
		return
	_data.earned[id] = int(Time.get_unix_time_from_system())
	_save()
	earned.emit(id)
	if announce:
		_banner_queue.append(id)
		_show_next_banner()


func _unlock_kind(kind: String) -> void:
	for item in list:
		if item.kind == kind:
			unlock(item.id)


func _main_worlds_beaten() -> int:
	var progress := get_node("/root/Progress")
	var count := 0
	for index in progress.WORLDS.size():
		if progress.has_content(index) and not progress.is_bonus(index) \
				and progress.cleared(progress.world_id(index)) >= progress.LEVELS_PER_BIOME:
			count += 1
	return count


## Test helper: forget everything.
func reset() -> void:
	_data = {"earned": {}, "stats": {}, "mechanics": []}
	_save()


# --- The banner -----------------------------------------------------------

## One banner at a time; extras wait their turn.
func _show_next_banner() -> void:
	if _banner_showing or _banner_queue.is_empty():
		return
	_banner_showing = true
	var item := find(_banner_queue.pop_front())
	var panel := PanelContainer.new()
	panel.theme = get_node("/root/Look").theme
	panel.add_theme_stylebox_override("panel", Palette.panel(Palette.SURFACE, Palette.GOLD, 10))
	panel.position = Vector2(20, -90)
	panel.custom_minimum_size = Vector2(320, 0)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var box := VBoxContainer.new()
	panel.add_child(box)
	for line in [["ACHIEVEMENT UNLOCKED", 11, Palette.GOLD], [item.name, 18, Palette.TEXT], [item.desc, 11, Palette.TEXT_DIM]]:
		var label := Label.new()
		label.text = line[0]
		label.add_theme_font_size_override("font_size", line[1])
		label.modulate = line[2]
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		box.add_child(label)
	_layer.add_child(panel)
	Sfx.play("evolve", 0.0)
	var tween := panel.create_tween()
	tween.tween_property(panel, "position:y", 12.0, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_interval(2.6)
	tween.tween_property(panel, "position:y", -110.0, 0.3)
	tween.tween_callback(func():
		panel.queue_free()
		_banner_showing = false
		_show_next_banner())


# --- Saving ---------------------------------------------------------------

var _save_pending := false


## Running totals change constantly, so they're saved at most once a frame.
func _save_soon() -> void:
	if not _save_pending:
		_save_pending = true
		_save.call_deferred()


func _save() -> void:
	_save_pending = false
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(_data))


func _load() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if parsed is Dictionary:
		for key in _data:
			if parsed.has(key):
				_data[key] = parsed[key]
