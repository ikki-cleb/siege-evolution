extends SceneTree
## Creates the unit, invader, and level .tres files in data/ from the tables
## below. This was used to make the starting content quickly.
##
## Run from the project folder:
##   godot --headless --script tools/build_content.gd
##
## WARNING: re-running overwrites data/. Once you start editing the .tres
## files in the Godot Inspector, treat those files as the real source and
## stop using this script (or update the tables here to match first).

const WALL := UnitData.Role.WALL
const ATTACKER := UnitData.Role.ATTACKER
const PATHER := InvaderData.Movement.PATHER
const SMASHER := InvaderData.Movement.SMASHER
const FLIER := InvaderData.Movement.FLIER

var units := {}
var invaders := {}


func _initialize() -> void:
	# --- Units: id, name, role, cost, hp, damage, range, interval, hits_air, shot color
	_unit("membrane", "Membrane", WALL, 4, 20, 0, 0, 0, false, Color.WHITE,
		"Cheap wall. Shapes the invaders' path.")
	_unit("clot", "Platelet Clot", WALL, 10, 90, 0, 0, 0, false, Color.WHITE,
		"Tough wall that holds back smashers.")
	_unit("neutrophil", "Neutrophil", ATTACKER, 12, 30, 3, 1.5, 0.5, false, Color("#e0c8ff"),
		"Fast short-range hits. Ground only.")
	_unit("b_cell", "B-Cell", ATTACKER, 16, 15, 4, 3.0, 1.0, true, Color("#9fd3ff"),
		"Long-range antibodies. Hits fliers.")

	# --- Invaders: id, name, movement, hp, speed, base damage, smash dps
	_invader("bacterium_half", "Bacterium", PATHER, 5, 1.2, 1, 0)
	_invader("rhinovirus", "Rhinovirus", PATHER, 6, 1.6, 1, 0)
	_invader("bacterium", "Bacterium", PATHER, 14, 1.0, 2, 0, "bacterium_half", 2)
	_invader("worm", "Parasite Worm", SMASHER, 40, 0.7, 3, 6)
	_invader("spore", "Spore", FLIER, 8, 1.0, 1, 0)

	# --- Levels. Waves: [invader, count, spacing, delay, spawn (-1 = alternate)]
	_level("level_01", "1. First Infection", [
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
	], 20, ["membrane", "membrane", "membrane", "membrane", "membrane", "membrane",
		"neutrophil", "neutrophil", "b_cell"],
		["membrane", "clot", "neutrophil", "b_cell"], 12, 10, [
		[["rhinovirus", 6, 1.2, 0, -1]],
		[["rhinovirus", 10, 0.9, 0, -1]],
		[["bacterium", 4, 2.5, 0, -1], ["rhinovirus", 6, 1.0, 3, -1]],
		[["rhinovirus", 16, 0.6, 0, -1]],
		[["bacterium", 4, 2.2, 0, -1], ["rhinovirus", 8, 0.8, 4, -1]],
		[["worm", 2, 6.0, 0, -1], ["rhinovirus", 10, 0.8, 2, -1]],
		[["spore", 6, 1.5, 0, -1], ["rhinovirus", 12, 0.7, 1, -1]],
		[["bacterium", 8, 1.4, 0, -1], ["worm", 3, 5.0, 3, -1]],
		[["rhinovirus", 24, 0.4, 0, -1], ["spore", 8, 1.0, 4, -1]],
		[["worm", 3, 4.0, 0, -1], ["bacterium", 6, 1.6, 2, -1],
			["rhinovirus", 14, 0.5, 6, -1], ["spore", 8, 1.2, 8, -1]],
	])

	_level("level_02", "2. Two Wounds", [
		"S.......S",
		".........",
		".........",
		"...###...",
		".........",
		".........",
		".........",
		"#.......#",
		".........",
		".........",
		"...#.#...",
		".........",
		".........",
		".B.......",
	], 20, ["membrane", "membrane", "membrane", "membrane", "membrane", "membrane",
		"membrane", "membrane", "neutrophil", "neutrophil", "b_cell", "b_cell", "clot"],
		["membrane", "clot", "neutrophil", "b_cell"], 12, 10, [
		[["rhinovirus", 8, 1.0, 0, -1]],
		[["rhinovirus", 12, 0.7, 0, -1]],
		[["bacterium", 6, 2.0, 0, -1], ["rhinovirus", 6, 0.8, 4, 1]],
		[["worm", 2, 4.0, 0, 0], ["rhinovirus", 12, 0.6, 1, 1]],
		[["spore", 8, 1.2, 0, -1], ["bacterium", 4, 2.0, 3, -1]],
		[["rhinovirus", 24, 0.4, 0, -1]],
		[["worm", 3, 4.0, 0, 1], ["bacterium", 8, 1.4, 2, 0]],
		[["spore", 10, 0.9, 0, -1], ["rhinovirus", 14, 0.5, 3, -1]],
		[["bacterium", 12, 1.0, 0, -1], ["worm", 4, 3.5, 4, -1]],
		[["worm", 5, 3.0, 0, -1], ["bacterium", 10, 1.2, 2, -1],
			["rhinovirus", 20, 0.4, 6, -1], ["spore", 10, 1.0, 8, -1]],
	])

	print("Content written to data/")
	quit()


func _unit(id: String, name: String, role: UnitData.Role, cost: int, hp: int, damage: int,
		attack_range: float, interval: float, hits_air: bool, shot_color: Color, text: String) -> void:
	var unit := UnitData.new()
	unit.id = id
	unit.display_name = name
	unit.role = role
	unit.cost = cost
	unit.max_hp = hp
	unit.damage = damage
	unit.attack_range = attack_range
	unit.attack_interval = interval
	unit.hits_air = hits_air
	unit.shot_color = shot_color
	unit.description = text
	unit.texture = load("res://art/units/%s.png" % id)
	units[id] = _save(unit, "res://data/units/%s.tres" % id)


func _invader(id: String, name: String, movement: InvaderData.Movement, hp: int, speed: float,
		base_damage: int, smash_damage: float, split_into := "", split_count := 0) -> void:
	var invader := InvaderData.new()
	invader.id = id
	invader.display_name = name
	invader.movement = movement
	invader.max_hp = hp
	invader.speed = speed
	invader.base_damage = base_damage
	invader.smash_damage = smash_damage
	if split_into != "":
		invader.split_into = invaders[split_into]
		invader.split_count = split_count
	invader.texture = load("res://art/invaders/%s.png" % id)
	invaders[id] = _save(invader, "res://data/invaders/%s.tres" % id)


func _level(id: String, name: String, layout: Array, base_hp: int, hand: Array, shop: Array,
		starting_atp: int, atp_per_wave: int, waves: Array) -> void:
	var level := LevelData.new()
	level.display_name = name
	level.layout = PackedStringArray(layout)
	level.base_hp = base_hp
	for unit_id in hand:
		level.starting_hand.append(units[unit_id])
	for unit_id in shop:
		level.shop.append(units[unit_id])
	level.starting_atp = starting_atp
	level.atp_per_wave = atp_per_wave
	for wave_table in waves:
		var wave := WaveData.new()
		for row in wave_table:
			var entry := WaveEntry.new()
			entry.invader = invaders[row[0]]
			entry.count = row[1]
			entry.spacing = row[2]
			entry.delay = row[3]
			entry.spawn_point = row[4]
			wave.entries.append(entry)
		level.waves.append(wave)
	_save(level, "res://data/levels/%s.tres" % id)


func _save(resource: Resource, path: String) -> Resource:
	var error := ResourceSaver.save(resource, path)
	assert(error == OK, "Could not save " + path)
	# Reload so later files reference this one by path instead of copying it.
	return load(path)
