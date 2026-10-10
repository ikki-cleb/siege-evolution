extends SceneTree
## Builds the game's content files (data/) from tools/content/immune_system.json
## plus the level tables below.
##
## Run from the project folder:
##   godot --headless --script tools/build_content.gd
##
## WARNING: re-running overwrites data/. If you've edited .tres files in the
## Godot Inspector, copy those changes into the JSON / tables here first.

const CONTENT := "res://tools/content/immune_system.json"

## Invader "threat" used to fill each wave's budget (about how many
## Rhinoviruses one invader is worth).
const THREAT := {
	"rhinovirus": 1.0, "flu_virus": 1.8, "bacterium": 2.6, "biofilm": 4.5,
	"worm": 5.0, "hookworm": 9.0, "spore": 1.4, "fungal_spore": 3.2,
}
## Each wave category: [normal invader, elite version, level the elite appears].
const CATEGORIES := {
	"swarm": ["rhinovirus", "flu_virus", 2],
	"split": ["bacterium", "biofilm", 3],
	"smash": ["worm", "hookworm", 4],
	"fly": ["spore", "fungal_spore", 5],
}
## The mix of categories for waves 1-10 of generated levels.
const WAVE_MIX := [
	{"swarm": 1.0},
	{"swarm": 0.6, "split": 0.4},
	{"split": 0.7, "fly": 0.3},
	{"swarm": 0.5, "smash": 0.5},
	{"fly": 0.6, "swarm": 0.4},
	{"split": 0.5, "smash": 0.5},
	{"swarm": 0.7, "fly": 0.3},
	{"smash": 0.4, "split": 0.3, "fly": 0.3},
	{"swarm": 0.6, "split": 0.4},
	{"swarm": 0.3, "split": 0.25, "smash": 0.25, "fly": 0.2},
]

var invaders := {}


func _initialize() -> void:
	var content: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTENT))
	var biome_info: Dictionary = content.biome
	var biome_id: String = biome_info.id
	for dir in ["data/packs/" + biome_id, "data/invaders/" + biome_id, "data/levels/" + biome_id, "data/biomes"]:
		DirAccess.make_dir_recursive_absolute("res://" + dir)

	# Invaders first (in file order, so split targets exist before they're used).
	for row in content.invaders:
		_invader(biome_id, row)

	var biome := BiomeData.new()
	biome.id = biome_id
	biome.display_name = biome_info.name
	biome.description = biome_info.description
	for pack_row in content.packs:
		biome.packs.append(_pack(biome_id, pack_row))
	for i in LEVELS.size():
		biome.levels.append(_level(biome_id, i + 1, LEVELS[i]))
	_save(biome, "res://data/biomes/%s.tres" % biome_id)
	print("Content written to data/")
	quit()


# --- Levels -----------------------------------------------------------------
# hand: ATP value of free units per pack slot (see LevelData.hand_value).
# budget: threat of wave 1; each later wave grows by 32%.

const LEVELS := [
	{
		"name": "1. First Infection", "preview": true, "hand": [24, 30, 15, 0, 0, 0], "atp": 20, "income": 10,
		"layout": [
			"....S....",
			".........",
			".........",
			"..#...#..",
			".........",
			".........",
			"#.......#",
			".........",
			".........",
			"..#...#..",
			".........",
			".........",
			".........",
			"....B....",
		],
	},
	{
		"name": "2. Sinus Cavity", "hand": [24, 16, 15, 10, 0, 0], "atp": 15, "income": 10, "budget": 10.0,
		"layout": [
			"S........",
			".........",
			"...#.....",
			"...#.....",
			".........",
			"......#..",
			"......#..",
			".........",
			".##......",
			".........",
			".....#...",
			".....#...",
			".........",
			"........B",
		],
	},
	{
		"name": "3. Bloodstream", "hand": [24, 16, 15, 10, 0, 0], "atp": 20, "income": 11, "budget": 12.0,
		"layout": [
			"S.......S",
			".........",
			".........",
			"...###...",
			".........",
			".........",
			"#.......#",
			".........",
			".........",
			"...#.#...",
			".........",
			".........",
			".........",
			"....B....",
		],
	},
	{
		"name": "4. Lymph Node", "hand": [28, 16, 15, 10, 20, 0], "atp": 20, "income": 12, "budget": 16.0,
		"layout": [
			"....S....",
			".........",
			".........",
			".#.....#.",
			".........",
			"...#.#...",
			".........",
			".........",
			"...#.#...",
			".........",
			".#.....#.",
			".........",
			".........",
			"....B....",
		],
	},
	{
		"name": "5. Lung Alveoli", "hand": [32, 24, 15, 10, 20, 0], "atp": 25, "income": 12, "budget": 17.0,
		"layout": [
			"........S",
			".........",
			".##......",
			".##...#..",
			"......#..",
			"S........",
			".........",
			"....##...",
			"....##...",
			".........",
			".#.......",
			".#....##.",
			".........",
			"B........",
		],
	},
	{
		"name": "6. Gut Lining", "hand": [32, 24, 15, 20, 20, 15], "atp": 25, "income": 13, "budget": 21.0,
		"layout": [
			"S...S...S",
			".........",
			".........",
			"#.#...#.#",
			".........",
			".........",
			".........",
			"..#...#..",
			".........",
			".........",
			".........",
			"#.......#",
			".........",
			"....B....",
		],
	},
	{
		"name": "7. Bone Marrow", "hand": [40, 24, 30, 20, 20, 15], "atp": 30, "income": 14, "budget": 23.0,
		"boss": "superbug",
		"layout": [
			"S...S....",
			".........",
			".........",
			"..#...#..",
			"..#...#..",
			".........",
			".........",
			"#...#...#",
			".........",
			".........",
			"..#...#..",
			"..#...#..",
			".........",
			"....B....",
		],
	},
]

# Level 1 teaches every invader in the biome, one idea per wave.
# [invader, count, spacing, delay]
const TUTORIAL_WAVES := [
	[["rhinovirus", 6, 1.2, 0]],
	[["rhinovirus", 10, 0.9, 0]],
	[["bacterium", 4, 2.2, 0], ["rhinovirus", 6, 1.0, 3]],
	[["rhinovirus", 14, 0.6, 0]],
	[["worm", 2, 6.0, 0], ["rhinovirus", 6, 1.0, 2]],
	[["spore", 6, 1.5, 0], ["rhinovirus", 8, 0.8, 1]],
	[["bacterium", 6, 1.8, 0], ["rhinovirus", 8, 0.8, 4]],
	[["worm", 3, 5.0, 0], ["spore", 6, 1.2, 3]],
	[["rhinovirus", 20, 0.45, 0], ["bacterium", 4, 2.0, 4]],
	[["worm", 3, 4.0, 0], ["bacterium", 5, 1.6, 2], ["rhinovirus", 12, 0.5, 6], ["spore", 6, 1.2, 8]],
]
const TUTORIAL_TIPS := [
	"Rhinoviruses walk around your units. Use walls to make their route longer, and put attackers beside it.",
	"Tap a placed unit to evolve it (pick one of two branches) or remove it. Anything placed this round refunds in full.",
	"Bacteria split into two halves when killed.",
	"Units from earlier rounds only refund 50% if you remove them, so plan ahead.",
	"Parasite Worms ignore your maze and chew through any unit in their way (red line).",
	"Spores fly straight to the base (blue dashes). Only some units can hit fliers.",
	"Damaged and destroyed units are repaired for free after every wave.",
	"Smashers and fliers together: cover both the red line and the blue dashes.",
	"Big swarm incoming. Area and fast attacks shine here.",
	"Final wave! Later levels bring tougher elite versions of everything you've seen.",
]


func _level(biome_id: String, number: int, table: Dictionary) -> LevelData:
	var level := LevelData.new()
	level.display_name = table.name
	level.layout = PackedStringArray(table.layout)
	level.base_hp = 20
	level.hand_value = PackedInt32Array(table.hand)
	level.starting_atp = int(table.atp)
	level.atp_per_wave = int(table.income)
	level.show_path_preview = table.get("preview", false)
	if number == 1:
		level.wave_tips = PackedStringArray(TUTORIAL_TIPS)
		for rows in TUTORIAL_WAVES:
			var wave := WaveData.new()
			for row in rows:
				wave.entries.append(_entry(row[0], row[1], row[2], row[3]))
			level.waves.append(wave)
	else:
		for w in 10:
			level.waves.append(_generated_wave(number, w, table))
	return _save(level, "res://data/levels/%s/level_%02d.tres" % [biome_id, number])


## Fills a wave's threat budget from its category mix, swapping in a growing
## share of elites once they've been introduced.
func _generated_wave(level_number: int, wave_index: int, table: Dictionary) -> WaveData:
	var wave := WaveData.new()
	var budget: float = table.budget * (1.0 + 0.32 * wave_index)
	var delay := 0.0
	var is_boss_wave: bool = table.has("boss") and wave_index == 9
	if is_boss_wave:
		wave.entries.append(_entry(table.boss, 1, 1.0, 6.0, 0))
		budget *= 0.5  # The boss brings minions, so fewer escorts.
	var mix: Dictionary = WAVE_MIX[wave_index]
	for category in mix:
		var normal: String = CATEGORIES[category][0]
		var elite: String = CATEGORIES[category][1]
		var elite_level: int = CATEGORIES[category][2]
		var share: float = budget * mix[category]
		var elite_share := 0.0
		if level_number >= elite_level:
			elite_share = min(0.6, 0.2 + 0.1 * (level_number - elite_level) + 0.02 * wave_index)
		for pair in [[normal, share * (1.0 - elite_share)], [elite, share * elite_share]]:
			var count := int(round(pair[1] / THREAT[pair[0]]))
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
	var dir := "res://data/packs/%s/%s" % [biome_id, row.id]
	DirAccess.make_dir_recursive_absolute(dir)
	for unit_row in row.units:
		var art_dir := "res://art/units/%s/%s" % [biome_id, row.id]
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
