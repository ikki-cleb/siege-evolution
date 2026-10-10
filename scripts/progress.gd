extends Node
## Remembers the player's progress (saved to disk) and what they picked in
## the menus. Loaded automatically at startup as "Progress", so any script
## can use it, e.g. Progress.pack.

const SAVE_PATH := "user://save.json"
const BIOMES: Array[String] = [
	"res://data/biomes/immune_system.tres",
]
const LEVELS_PER_BIOME := 7

## What the game scene should play next (set by the menu).
var biome: BiomeData
var pack: PackData
var level_index := 0
## Which menu screen to open when returning from a level.
var return_screen := "title"

# Saved data: { "biomes": { biome_id: { "pack": pack_id, "cleared": int } } }
var _data := {"biomes": {}}


func _ready() -> void:
	_load()


func load_biome(index: int) -> BiomeData:
	return load(BIOMES[index])


## How many levels of this biome the current run has cleared (0-7).
func cleared(biome_id: String) -> int:
	return int(_run(biome_id).get("cleared", 0))


## The pack id of this biome's current run, or "" if none was started.
func run_pack(biome_id: String) -> String:
	return _run(biome_id).get("pack", "")


func is_biome_unlocked(index: int) -> bool:
	if index == 0:
		return true
	var previous := load_biome(index - 1)
	return cleared(previous.id) >= LEVELS_PER_BIOME


## Starts a biome with a pack. Choosing a different pack restarts the biome.
func choose_pack(p_biome: BiomeData, p_pack: PackData) -> void:
	biome = p_biome
	pack = p_pack
	if run_pack(p_biome.id) != p_pack.id:
		_data.biomes[p_biome.id] = {"pack": p_pack.id, "cleared": 0}
		_save()


func complete_level() -> void:
	var run := _run(biome.id)
	run["cleared"] = max(run.get("cleared", 0), level_index + 1)
	_data.biomes[biome.id] = run
	_save()


func _run(biome_id: String) -> Dictionary:
	return _data.biomes.get(biome_id, {})


func _load() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed = JSON.parse_string(file.get_as_text())
	if parsed is Dictionary and parsed.get("biomes") is Dictionary:
		_data = parsed


func _save() -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(_data))


## Wipes all progress (used by tests).
func reset() -> void:
	_data = {"biomes": {}}
	_save()
