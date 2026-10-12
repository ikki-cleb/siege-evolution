class_name EndlessWaves
extends RefCounted
## Endless mode's waves. After a world's boss falls, the player can keep going
## on the same board: wave 9, 10, 11... never stop, and they get harder until
## the defense breaks.
##
## Waves are built in the game from the same rules as the world's level 5
## (data/endless.json, written by the content build):
##   - the threat budget starts at level 5's final wave and grows each wave,
##   - invaders get 16% more HP each wave (it compounds),
##   - every 10th endless wave the world's boss returns, +50% HP each time.
## `n` below is the endless wave number: 1 for the first one (game wave 9).

const RULES_PATH := "res://data/endless.json"
## Each endless wave's budget is this many times the one before.
const BUDGET_GROWTH := 1.08
## Invader HP is this many times the wave before's (wave 10: about 4.4x).
## Tuned with the bot (tests/sim_test.gd -- endless): the first, gentler
## curve let strong bot defenses reach wave 60-100; the target is 25-35.
const HP_GROWTH := 1.16
## The boss returns every this many endless waves.
const BOSS_EVERY := 10
## Each return the boss has this much more HP (1.5x, 2x, 2.5x...).
const BOSS_HP_STEP := 0.5
## More invaders than this in one wave would slow phones down, so bigger
## waves send fewer, tougher invaders instead.
const MAX_INVADERS := 90
## Elites make up this share of each category (the most a level ever uses).
const ELITE_SHARE := 0.6

var _rules: Dictionary = {}
var _biome_id := ""
var _cache := {}  ## n -> WaveData (the preview and the wave itself must match)


func _init(biome_id: String) -> void:
	_biome_id = biome_id
	var all = JSON.parse_string(FileAccess.get_file_as_string(RULES_PATH))
	if all is Dictionary:
		_rules = all.get(biome_id, {})


static func hp_scale(n: int) -> float:
	return pow(HP_GROWTH, n)


static func is_boss_wave(n: int) -> bool:
	return n > 0 and n % BOSS_EVERY == 0


## The returning boss's HP multiplier on endless wave `n` (1.5x the first time).
static func boss_hp_scale(n: int) -> float:
	return 1.0 + BOSS_HP_STEP * (n / BOSS_EVERY)


## The wave for endless wave `n` (always the same wave for the same n).
## Its "hp_boost" meta is extra HP when the invader cap kicked in.
func wave(n: int) -> WaveData:
	if not _cache.has(n):
		_cache[n] = _build(n)
	return _cache[n]


func _build(n: int) -> WaveData:
	var wave_data := WaveData.new()
	wave_data.set_meta("hp_boost", 1.0)
	if _rules.is_empty():
		return wave_data
	var budget: float = _rules.budget * pow(BUDGET_GROWTH, n)
	var delay := 0.0
	if is_boss_wave(n) and _rules.boss != "":
		wave_data.entries.append(_entry(_rules.boss, 1, 1.0, 6.0, 0))
		budget *= 0.5  # the boss brings minions, so fewer escorts
	# Cycle through the later (heavier) wave mixes for variety.
	var mixes: Array = _rules.sea_mix if _rules.sea and not _rules.sea_mix.is_empty() else _rules.mix
	var mix: Dictionary = mixes[mixes.size() - 4 + n % 4] if mixes.size() >= 4 else mixes[-1]
	var groups := []  # [invader id, count]
	for category in mix:
		var info: Dictionary = _rules.categories[category]
		var share: float = budget * mix[category]
		var elite: String = info.get("elite", "")
		var elite_share := ELITE_SHARE if elite != "" else 0.0
		for pair in [[info.normal, share * (1.0 - elite_share)], [elite, share * elite_share]]:
			if pair[0] == "":
				continue
			var count := int(round(pair[1] / _rules.threat[pair[0]]))
			if count > 0:
				groups.append([pair[0], count])
	# Too many invaders: send fewer, with that much more HP each.
	var total := 0
	for group in groups:
		total += group[1]
	if total > MAX_INVADERS:
		var factor := float(total) / MAX_INVADERS
		wave_data.set_meta("hp_boost", factor)
		for group in groups:
			group[1] = maxi(1, int(round(group[1] / factor)))
	for group in groups:
		var spacing := clampf(16.0 / group[1], 0.35, 5.0)
		wave_data.entries.append(_entry(group[0], group[1], spacing, delay))
		delay += 2.5
	return wave_data


func _entry(invader_id: String, count: int, spacing: float, delay: float, spawn := -1) -> WaveEntry:
	var entry := WaveEntry.new()
	entry.invader = load("res://data/invaders/%s/%s.tres" % [_biome_id, invader_id])
	entry.count = count
	entry.spacing = snappedf(spacing, 0.05)
	entry.delay = delay
	entry.spawn_point = spawn
	return entry
