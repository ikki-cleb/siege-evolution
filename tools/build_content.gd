extends SceneTree
## Builds the game's content files (data/) from the world files in
## tools/content/*.json (one file per world).
##
## Run from the project folder:
##   godot --headless --script tools/build_content.gd
##
## WARNING: re-running overwrites data/. If you've edited .tres files in the
## Godot Inspector, copy those changes into the JSON first.
##
## A world's JSON can say "packs_from": "<other world id>" plus a "renames"
## table to reuse that world's packs with new names and art. That keeps every
## pack playing exactly the same at every scale.

const CONTENT_DIR := "res://tools/content/"
## Build order matters: worlds that borrow packs come after their source.
const WORLD_FILES: Array[String] = ["immune_system.json", "backyard_bugs.json", "wild_kingdom.json",
	"total_war.json", "galactic_siege.json", "kitchen_defense.json"]

var invaders := {}
var _content_by_id := {}


func _initialize() -> void:
	for file_name in WORLD_FILES:
		var content: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTENT_DIR + file_name))
		_content_by_id[content.biome.id] = content
		_build_world(content)
	print("Content written to data/")
	quit()


func _build_world(content: Dictionary) -> void:
	var info: Dictionary = content.biome
	var biome_id: String = info.id
	for dir in ["data/packs/" + biome_id, "data/invaders/" + biome_id, "data/levels/" + biome_id, "data/biomes"]:
		DirAccess.make_dir_recursive_absolute("res://" + dir)
	invaders.clear()

	# Invaders first (in file order, so split and minion targets exist first).
	for row in content.invaders:
		_invader(biome_id, row)

	var biome := BiomeData.new()
	biome.id = biome_id
	biome.display_name = info.name
	biome.description = info.description
	var tiles := "res://art/tiles/%s/" % biome_id
	biome.floor_texture = load(tiles + "floor.png")
	biome.rock_texture = load(tiles + "rock.png")
	biome.spawn_texture = load(tiles + "spawn.png")
	biome.base_texture = load(tiles + "base.png")
	if ResourceLoader.exists(tiles + "water.png"):
		biome.water_texture = load(tiles + "water.png")
		biome.sea_spawn_texture = load(tiles + "sea_spawn.png")
	for pack_row in pack_rows(content, _content_by_id):
		biome.packs.append(_pack(biome_id, pack_row))
	for i in content.levels.size():
		biome.levels.append(_level(biome_id, i + 1, content.levels[i], content))
	_save(biome, "res://data/biomes/%s.tres" % biome_id)


## The packs for a world: its own, or another world's with units renamed.
## (Static so the art script's logic can mirror it.)
static func pack_rows(content: Dictionary, all_content: Dictionary) -> Array:
	if not content.has("packs_from"):
		return content.packs
	var source: Dictionary = all_content[content.packs_from]
	var renames: Dictionary = content.renames
	var result := []
	for pack in source.packs:
		var copy: Dictionary = pack.duplicate(true)
		for unit in copy.units:
			_apply_rename(unit, renames)
			for evolution in unit.evolutions:
				_apply_rename(evolution, renames)
		result.append(copy)
	return result


static func _apply_rename(row: Dictionary, renames: Dictionary) -> void:
	var entry: Array = renames[row.id]
	row.id = entry[0]
	row.name = entry[1]


# --- Levels -----------------------------------------------------------------
# Each level row in the JSON:
#   hand: coin value of free units per pack slot (see LevelData.hand_value)
#   coins: starting coins. income: bonus coins for a wave where nothing leaks
#   budget: threat of wave 1 (levels 2-7); later waves grow by growth_per_wave
#   boss: invader id that arrives on wave 10 (optional)
# Level 1 uses the handwritten "tutorial" waves and tips instead.

func _level(biome_id: String, number: int, table: Dictionary, content: Dictionary) -> LevelData:
	var level := LevelData.new()
	level.display_name = table.name
	level.layout = PackedStringArray(table.layout)
	level.base_hp = 20
	level.hand_value = PackedInt32Array(table.hand)
	level.starting_coins = int(table.coins)
	level.coins_per_wave = int(table.income)
	level.show_path_preview = table.get("preview", false)
	if table.has("tips"):
		level.wave_tips = PackedStringArray(table.tips)
	if table.has("tiles"):
		var tiles := "res://art/tiles/%s/%s/" % [biome_id, table.tiles]
		level.floor_texture = load(tiles + "floor.png")
		level.rock_texture = load(tiles + "rock.png")
		level.spawn_texture = load(tiles + "spawn.png")
		level.base_texture = load(tiles + "base.png")
	if number == 1:
		level.wave_tips = PackedStringArray(content.tutorial.tips)
		for rows in content.tutorial.waves:
			var wave := WaveData.new()
			for row in rows:
				wave.entries.append(_entry(row[0], int(row[1]), row[2], row[3]))
			level.waves.append(wave)
	else:
		for w in 10:
			level.waves.append(_generated_wave(number, w, table, content.waves))
	return _save(level, "res://data/levels/%s/level_%02d.tres" % [biome_id, number])


## Fills a wave's threat budget from its category mix, swapping in a growing
## share of elites once they've been introduced.
func _generated_wave(level_number: int, wave_index: int, table: Dictionary, rules: Dictionary) -> WaveData:
	var wave := WaveData.new()
	var budget: float = table.budget * (1.0 + rules.growth_per_wave * wave_index)
	var delay := 0.0
	if table.has("boss") and wave_index == 9:
		wave.entries.append(_entry(table.boss, 1, 1.0, 6.0, 0))
		budget *= 0.5  # The boss brings minions, so fewer escorts.
	# Sea levels use their own mix (boats plus landing troops).
	var mix: Dictionary = (rules.sea_mix if table.get("sea", false) else rules.mix)[wave_index]
	for category in mix:
		var info: Dictionary = rules.categories[category]
		var share: float = budget * mix[category]
		var elite_share := 0.0
		var elite: String = info.get("elite", "")
		if elite != "" and level_number >= info.elite_level:
			elite_share = min(0.6, 0.2 + 0.1 * (level_number - info.elite_level) + 0.02 * wave_index)
		for pair in [[info.normal, share * (1.0 - elite_share)], [elite, share * elite_share]]:
			if pair[0] == "":
				continue
			var count := int(round(pair[1] / rules.threat[pair[0]]))
			if count <= 0:
				continue
			var spacing := clampf(16.0 / count, 0.35, 5.0)
			wave.entries.append(_entry(pair[0], count, spacing, delay))
			delay += 2.5
	return wave


func _entry(invader_id: String, count: int, spacing: float, delay: float, spawn := -1) -> WaveEntry:
	var entry := WaveEntry.new()
	entry.invader = invaders[invader_id]
	entry.count = count
	entry.spacing = snappedf(spacing, 0.05)
	entry.delay = delay
	entry.spawn_point = spawn
	return entry


# --- Packs and units --------------------------------------------------------

func _pack(biome_id: String, row: Dictionary) -> PackData:
	var pack := PackData.new()
	pack.id = row.id
	pack.display_name = row.name
	pack.description = row.description
	pack.color = Color(row.color)
	pack.product_id = row.get("product", "")
	var dir := "res://data/packs/%s/%s" % [biome_id, row.id]
	DirAccess.make_dir_recursive_absolute(dir)
	var art_dir := "res://art/units/%s/%s" % [biome_id, row.id]
	for unit_row in row.units:
		var unit := _unit(unit_row, {}, art_dir, pack.color)
		for evo_row in unit_row.evolutions:
			# Evolutions start as a copy of the base unit, then apply changes.
			var evolution := _unit(evo_row, unit_row, art_dir, pack.color)
			unit.evolutions.append(_save(evolution, "%s/%s.tres" % [dir, evo_row.id]))
		pack.units.append(_save(unit, "%s/%s.tres" % [dir, unit_row.id]))
	return _save(pack, "%s/%s_pack.tres" % [dir, row.id])


func _unit(row: Dictionary, base: Dictionary, art_dir: String, pack_color: Color) -> UnitData:
	var merged := base.duplicate()
	merged.merge(row, true)
	var value := func(key, default): return merged.get(key, default)
	var unit := UnitData.new()
	unit.id = row.id
	unit.display_name = row.name
	unit.role = {"wall": UnitData.Role.WALL, "attacker": UnitData.Role.ATTACKER,
		"support": UnitData.Role.SUPPORT}[merged.role]
	unit.cost = int(row.cost)
	unit.max_hp = int(value.call("hp", 20))
	unit.regen = value.call("regen", 0.0)
	unit.reflect = value.call("reflect", 0.0)
	unit.attack_mode = UnitData.AttackMode.PULSE if value.call("mode", "single") == "pulse" else UnitData.AttackMode.SINGLE
	unit.damage = value.call("damage", 0.0)
	unit.attack_range = value.call("range", 1.5)
	unit.attack_interval = value.call("interval", 1.0)
	unit.hits_air = value.call("air", false)
	unit.pierce = value.call("pierce", false)
	unit.splash_radius = value.call("splash", 0.0)
	unit.adjacency_bonus = value.call("adjacency", 0.0)
	unit.slow = value.call("slow", 0.0)
	unit.slow_duration = value.call("slow_dur", 0.0)
	unit.stun_duration = value.call("stun", 0.0)
	unit.poison_dps = value.call("poison", 0.0)
	unit.poison_duration = value.call("poison_dur", 0.0)
	unit.poison_spreads = value.call("spreads", false)
	unit.mark_bonus = value.call("mark", 0.0)
	unit.mark_duration = value.call("mark_dur", 0.0)
	unit.description = row.get("desc", "")
	unit.shot_color = pack_color.lightened(0.4)
	unit.texture = load("%s/%s.png" % [art_dir, row.id])
	unit.can_place_on_water = value.call("water", false)
	var water_art := "%s/%s_water.png" % [art_dir, row.id]
	if ResourceLoader.exists(water_art):
		unit.water_texture = load(water_art)
	return unit


# --- Invaders ---------------------------------------------------------------

func _invader(biome_id: String, row: Dictionary) -> void:
	var invader := InvaderData.new()
	invader.id = row.id
	invader.display_name = row.name
	invader.movement = {"pather": InvaderData.Movement.PATHER, "smasher": InvaderData.Movement.SMASHER,
		"flier": InvaderData.Movement.FLIER}[row.movement]
	invader.max_hp = int(row.hp)
	invader.armor = int(row.get("armor", 0))
	invader.regen = row.get("regen", 0.0)
	invader.speed = row.speed
	invader.base_damage = int(row.base_damage)
	invader.smash_damage = row.get("smash", 0.0)
	invader.coin_drop = int(row.get("drop", 1))
	invader.burrow_after = int(row.get("burrow_after", 0))
	invader.jumps = row.get("jumps", false)
	invader.naval = row.get("naval", false)
	invader.bomb_damage = row.get("bomb", 0.0)
	invader.bomb_interval = row.get("bomb_interval", 0.0)
	invader.blink_interval = row.get("blink_interval", 0.0)
	invader.blink_distance = int(row.get("blink_distance", 0))
	invader.burrow_length = int(row.get("burrow_length", 0))
	invader.spill_every = int(row.get("spill_every", 0))
	invader.spill_slow = row.get("spill_slow", 0.0)
	invader.is_elite = row.get("elite", false)
	invader.is_boss = row.get("boss", false)
	if row.has("split_into"):
		invader.split_into = invaders[row.split_into]
		invader.split_count = int(row.split_count)
	if row.has("minion"):
		invader.minion = invaders[row.minion]
		invader.minion_count = int(row.minion_count)
		invader.minion_interval = row.minion_interval
	invader.description = row.get("desc", "")
	invader.texture = load("res://art/invaders/%s/%s.png" % [biome_id, row.id])
	invaders[row.id] = _save(invader, "res://data/invaders/%s/%s.tres" % [biome_id, row.id])


func _save(resource: Resource, path: String) -> Resource:
	var error := ResourceSaver.save(resource, path)
	assert(error == OK, "Could not save " + path)
	# Reload so later files reference this one by path instead of copying it.
	return load(path)
