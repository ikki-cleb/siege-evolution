extends Node
## Remembers the player's progress (saved to disk) and what they picked in
## the menus. Loaded automatically at startup as "Progress", so any script
## can use it, e.g. Progress.pack.

const SAVE_PATH := "user://save.json"
const LEVELS_PER_BIOME := 7

## Every world on the map. Main worlds unlock in order by beating the
## previous one; bonus worlds unlock by buying them in the Store. A world
## with no "path" yet shows as "coming soon".
const WORLDS: Array[Dictionary] = [
	{"name": "Microscopic", "path": "res://data/biomes/immune_system.tres",
		"theme": "Inside the body: viruses, bacteria, parasites and spores."},
	{"name": "Backyard Bugs", "path": "res://data/biomes/backyard_bugs.tres",
		"theme": "Protect the anthill from termites, beetles, mosquitoes and burrowing mole crickets."},
	{"name": "Wild Kingdom", "path": "res://data/biomes/wild_kingdom.tres",
		"theme": "Keep foxes, wolves, boars, crows and leaping deer away from the farmhouse."},
	{"name": "Total War", "path": "res://data/biomes/total_war.tres",
		"theme": "A toy war across the playroom and the bathtub: tanks, boats and bombers."},
	{"name": "Galactic Siege", "path": "res://data/biomes/galactic_siege.tres",
		"theme": "Defend the colony reactor on the moon, a space station and an asteroid field from the alien armada."},
	{"name": "Kitchen Defense", "path": "res://data/biomes/kitchen_defense.tres", "bonus": true,
		"product": "world_kitchen",
		"theme": "Ants, slugs, mice and roaches raid the kitchen. Defend the cookie jar."},
	{"name": "Birthday Bash", "path": "", "bonus": true, "product": "world_birthday",
		"theme": "Protect the cake at a kid's birthday party."},
]

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
	var path: String = WORLDS[index].path
	return load(path) if path != "" else null


func has_content(index: int) -> bool:
	return WORLDS[index].path != ""


func is_bonus(index: int) -> bool:
	return WORLDS[index].get("bonus", false)


## True if this biome id belongs to a bonus world.
func is_bonus_biome(biome_id: String) -> bool:
	for index in WORLDS.size():
		if is_bonus(index) and WORLDS[index].path.ends_with("/%s.tres" % biome_id):
			return true
	return false


## The world's number among main worlds (1-5), or 0 for bonus worlds.
func main_number(index: int) -> int:
	return 0 if is_bonus(index) else index + 1


## How many levels of this biome the current run has cleared (0-7).
func cleared(biome_id: String) -> int:
	return int(_run(biome_id).get("cleared", 0))


## The pack id of this biome's current run, or "" if none was started.
func run_pack(biome_id: String) -> String:
	return _run(biome_id).get("pack", "")


func is_biome_unlocked(index: int) -> bool:
	if is_bonus(index):
		return Store.owns(WORLDS[index].product)
	if index == 0:
		return true
	var previous := load_biome(index - 1)
	return previous != null and cleared(previous.id) >= LEVELS_PER_BIOME


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
	_data = {"biomes": {}}
	_save()
