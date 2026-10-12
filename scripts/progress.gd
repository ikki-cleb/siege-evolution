extends Node
## Remembers the player's progress (saved to disk) and what they picked in
## the menus. Loaded automatically at startup as "Progress", so any script
## can use it, e.g. Progress.pack.

const SAVE_PATH := "user://save.json"
const LEVELS_PER_BIOME := 5
## Save versions: 1 = 7 levels per world, 2 = 5 levels, 3 = packs can be
## swapped freely and each pack remembers the levels it has beaten.
## Old saves are converted when loaded (see _convert_old_save).
const SAVE_VERSION := 3
const OLD_LEVELS_KEPT: Array[int] = [1, 2, 4, 6, 7]

## Every world on the map, in play order (Backyard Bugs is first; the
## order changed in v1.1, saves are keyed by world id so nothing is lost).
## Main worlds unlock in order by beating the previous one; bonus worlds unlock by buying them in the Store. A world
## with no "path" yet shows as "coming soon".
const WORLDS: Array[Dictionary] = [
	{"name": "Backyard Bugs", "path": "res://data/biomes/backyard_bugs.tres",
		"theme": "Protect the anthill from termites, beetles, mosquitoes and burrowing mole crickets."},
	{"name": "Wild Kingdom", "path": "res://data/biomes/wild_kingdom.tres",
		"theme": "Keep foxes, wolves, boars, crows and leaping deer away from the farmhouse."},
	{"name": "Microscopic", "path": "res://data/biomes/immune_system.tres",
		"theme": "Inside the body: viruses, bacteria, parasites and spores."},
	{"name": "Total War", "path": "res://data/biomes/total_war.tres",
		"theme": "A toy war across the playroom and the bathtub: tanks, boats and bombers."},
	{"name": "Galactic Siege", "path": "res://data/biomes/galactic_siege.tres",
		"theme": "Defend the colony reactor on the moon, a space station and an asteroid field from the alien armada."},
	{"name": "Kitchen Defense", "path": "res://data/biomes/kitchen_defense.tres", "bonus": true,
		"product": "world_kitchen",
		"theme": "Ants, slugs, mice and roaches raid the kitchen. Defend the cookie jar."},
	{"name": "Birthday Bash", "path": "res://data/biomes/birthday_bash.tres", "bonus": true,
		"product": "world_birthday",
		"theme": "Wind-up toys, balloons, piñatas and a clown crash the party. Protect the cake."},
]

## What the game scene should play next (set by the menu).
var biome: BiomeData
var pack: PackData
var level_index := 0
## Which menu screen to open when returning from a level.
var return_screen := "title"

# Saved data: { "biomes": { biome_id: {
#     "cleared": how many levels are unlocked-and-beaten (shared by all packs),
#     "pack": the pack picked last time,
#     "beaten": { pack_id: [level indices that pack has beaten] } } } }
var _data := {"biomes": {}, "version": SAVE_VERSION}


func _ready() -> void:
	_load()


func load_biome(index: int) -> BiomeData:
	var path: String = WORLDS[index].path
	return load(path) if path != "" else null


## A world's id without loading it: "res://data/biomes/wild_kingdom.tres" ->
## "wild_kingdom". Loading a whole world (every unit, sprite and level) takes
## a while, so code that only needs the id uses this instead.
func world_id(index: int) -> String:
	return String(WORLDS[index].path).get_file().get_basename()


func has_content(index: int) -> bool:
	return WORLDS[index].path != ""


func is_bonus(index: int) -> bool:
	return WORLDS[index].get("bonus", false)


## Path preview (the invaders' routes, shown during the build phase).
## On by default; the "Paths" button in a level turns it off. Saved.
func show_paths() -> bool:
	return _data.get("show_paths", true)


func set_show_paths(on: bool) -> void:
	_data["show_paths"] = on
	_save()


## The Background filter strength (Settings slider): 0 = off, 1 = Medium
## (the default), 1.5 = Strong. Busy maps get a bit more on top.
const CALM_DEFAULT := 1.0
const CALM_MAX := 1.5


func calm_strength() -> float:
	return clamp(float(_data.get("calm_strength", CALM_DEFAULT)), 0.0, CALM_MAX)


func set_calm_strength(value: float) -> void:
	_data["calm_strength"] = clamp(value, 0.0, CALM_MAX)
	_save()


## True if this biome id belongs to a bonus world.
func is_bonus_biome(biome_id: String) -> bool:
	for index in WORLDS.size():
		if is_bonus(index) and WORLDS[index].path.ends_with("/%s.tres" % biome_id):
			return true
	return false


## The world's number among main worlds (1-5), or 0 for bonus worlds.
func main_number(index: int) -> int:
	return 0 if is_bonus(index) else index + 1


## How many levels of this biome are cleared, by any pack (0-5).
func cleared(biome_id: String) -> int:
	return int(_run(biome_id).get("cleared", 0))


## The pack picked last time in this biome, or "" if none yet.
func run_pack(biome_id: String) -> String:
	return _run(biome_id).get("pack", "")


## The ids of the packs that have beaten this level (0-based index).
func packs_that_beat(biome_id: String, index: int) -> Array[String]:
	var result: Array[String] = []
	var beaten: Dictionary = _run(biome_id).get("beaten", {})
	for pack_id in beaten:
		if beaten[pack_id].has(float(index)) or beaten[pack_id].has(index):
			result.append(pack_id)
	return result


## How many of a world's levels this pack has beaten (0-5). The pack
## symbols on the world cards fill up by this.
func levels_beaten_by(biome_id: String, pack_id: String) -> int:
	return _run(biome_id).get("beaten", {}).get(pack_id, []).size()


## How many of the 25 main-world levels this pack has beaten (pack mastery).
func main_levels_beaten(pack_id: String) -> int:
	var total := 0
	for index in WORLDS.size():
		if has_content(index) and not is_bonus(index):
			total += _run(world_id(index)).get("beaten", {}).get(pack_id, []).size()
	return total


## How many levels the main worlds have in all (5 worlds x 5 levels).
func main_level_count() -> int:
	var total := 0
	for index in WORLDS.size():
		if not is_bonus(index) and has_content(index):
			total += LEVELS_PER_BIOME
	return total


func is_biome_unlocked(index: int) -> bool:
	if is_bonus(index):
		return Store.owns(WORLDS[index].product)
	if index == 0:
		return true
	return has_content(index - 1) and cleared(world_id(index - 1)) >= LEVELS_PER_BIOME


## Picks the pack for the next level. Packs can be swapped any time: world
## progress is shared, and nothing is lost by switching.
func choose_pack(p_biome: BiomeData, p_pack: PackData) -> void:
	biome = p_biome
	pack = p_pack
	var run := _run(p_biome.id)
	if run.get("pack", "") != p_pack.id:
		run["pack"] = p_pack.id
		_data.biomes[p_biome.id] = run
		_save()


## Records a won level: it unlocks the next level for every pack, and the
## pack that won it remembers it (for pack mastery).
func complete_level() -> void:
	var run := _run(biome.id)
	run["cleared"] = max(run.get("cleared", 0), level_index + 1)
	_mark_beaten(run, pack.id, level_index)
	_data.biomes[biome.id] = run
	_save()


func _mark_beaten(run: Dictionary, pack_id: String, index: int) -> void:
	var beaten: Dictionary = run.get("beaten", {})
	var levels: Array = beaten.get(pack_id, [])
	if not levels.has(index) and not levels.has(float(index)):
		levels.append(index)
	beaten[pack_id] = levels
	run["beaten"] = beaten


## This biome's saved record (a fresh empty one if it's never been played).
func _run(biome_id: String) -> Dictionary:
	return _data.biomes.get(biome_id, {})


func _load() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed = JSON.parse_string(file.get_as_text())
	if parsed is Dictionary and parsed.get("biomes") is Dictionary:
		_data = parsed
		if int(_data.get("version", 1)) < SAVE_VERSION:
			_convert_old_save()


func _convert_old_save() -> void:
	var version := int(_data.get("version", 1))
	for biome_id in _data.biomes:
		var run: Dictionary = _data.biomes[biome_id]
		var cleared_levels := int(run.get("cleared", 0))
		# Version 1 counted 7 levels per world. A player who had cleared, say,
		# 4 old levels keeps every kept level up to old level 4 (new 1-3).
		if version < 2:
			cleared_levels = OLD_LEVELS_KEPT.filter(func(old_level): return old_level <= cleared_levels).size()
			run["cleared"] = cleared_levels
		# Before version 3 a world had one pack: it beat every cleared level.
		if version < 3 and run.get("pack", "") != "":
			for index in cleared_levels:
				_mark_beaten(run, run.pack, index)
	_data["version"] = SAVE_VERSION
	_save()


func _save() -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(_data))


## Test mode only: marks every built world as cleared, so all worlds open.
func unlock_all_for_testing() -> void:
	for index in WORLDS.size():
		var world := load_biome(index)
		if world and not is_bonus(index):
			var run := _run(world.id)
			run["cleared"] = LEVELS_PER_BIOME
			if not run.has("pack"):
				run["pack"] = world.packs[0].id
			_data.biomes[world.id] = run
	_save()


## Wipes all progress (used by tests).
func reset() -> void:
	_data = {"biomes": {}, "version": SAVE_VERSION, "show_paths": true}
	_save()
