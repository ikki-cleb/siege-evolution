class_name RelicSet
extends RefCounted
## The relics picked in the current level, and the rules for offering them.
##
## The full pool lives in data/relics.json. Each relic has:
##   "filter":  which units it helps (see matches() below), or "economy"
##   "mult":    stats multiplied, e.g. {"damage": 0.15} = +15% damage
##   "add":     stats added, e.g. {"attack_range": 0.4}
##   "grant":   abilities given, e.g. ["pierce"]
##   "economy": coin/base rules, e.g. {"kill_coins": 1} (see the game script)
## New relics can be added to the JSON without changing any code, as long as
## they use the filters, stats and economy keys that already exist.
##
## A picked relic is "pending" until the next wave starts, then "active".

const POOL_PATH := "res://data/relics.json"
const RARITY_ORDER := ["common", "rare", "epic"]
const RARITY_COLORS := {"common": Color("#c8c0c8"), "rare": Color("#60a8ff"), "epic": Color("#c070ff")}
## Waves (counted from 1) whose relic carrier drops a relic.
const RELIC_WAVES := [1, 3, 5, 7]
## Chance of each rarity for the 1st, 2nd, 3rd and 4th relic of a level:
## later relics roll better. [common, rare, epic]
const ODDS := [[0.75, 0.22, 0.03], [0.65, 0.28, 0.07], [0.55, 0.33, 0.12], [0.45, 0.37, 0.18]]

static var _pool: Array = []

var active: Array = []
var pending: Array = []


static func pool() -> Array:
	if _pool.is_empty():
		var file := FileAccess.open(POOL_PATH, FileAccess.READ)
		if file:
			_pool = JSON.parse_string(file.get_as_text())
	return _pool


static func find(id: String) -> Dictionary:
	for relic in pool():
		if relic.id == id:
			return relic
	return {}


## True if a relic with this filter helps a unit like `data`.
static func matches(filter: String, data: UnitData) -> bool:
	match filter:
		"all":
			return true
		"attackers":
			return data.can_attack()
		"walls":
			return data.role == UnitData.Role.WALL
		"anti_air":
			return data.can_attack() and data.hits_air
		"ground_only":
			return data.can_attack() and not data.hits_air
		"single":
			return data.can_attack() and data.attack_mode == UnitData.AttackMode.SINGLE
		"pulse":
			return data.can_attack() and data.attack_mode == UnitData.AttackMode.PULSE
		"splash":
			return data.splash_radius > 0.0
		"slow":
			return data.slow > 0.0
		"stun":
			return data.stun_duration > 0.0
		"poison":
			return data.poison_dps > 0.0
		"mark":
			return data.mark_bonus > 0.0
		"swarm":
			return data.adjacency_bonus > 0.0
		"regen":
			return data.regen > 0.0
		"reflect":
			return data.reflect > 0.0
		"chain":
			return data.chain_count > 0
		"multishot":
			return data.multishot > 1
		"knockback":
			return data.knockback > 0
		"long_range":
			return data.can_attack() and data.attack_range >= 2.5
		"short_range":
			return data.can_attack() and data.attack_range < 2.0
	return false


## True if a relic would do something with these units (some unit the
## player can build this level, or evolve one into, matches). Economy relics
## always help.
static func useful_for(relic: Dictionary, types: Array[UnitData]) -> bool:
	if relic.filter == "economy":
		return true
	for type in _with_evolutions(types):
		if matches(relic.filter, type):
			return true
	return false


static func _with_evolutions(types: Array[UnitData]) -> Array[UnitData]:
	var result: Array[UnitData] = []
	var todo: Array[UnitData] = types.duplicate()
	while not todo.is_empty():
		var type: UnitData = todo.pop_back()
		if result.has(type):
			continue
		result.append(type)
		todo.append_array(type.evolutions)
	return result


## Three different relics to choose from. `number` is which relic of the level
## this is (0-3); later ones roll better rarities. Same seed = same offer.
##
## Relics you already have aren't offered again until you've taken every
## relic that helps your units; then the pool "resets" and each can be taken
## a second time (x2), then a third (x3), and so on. Copies stack: a unit's
## stats add up every active relic. (Only endless mode lasts long enough.)
func roll_offer(types: Array[UnitData], number: int, seed_value: int) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var useful := pool().filter(func(relic): return useful_for(relic, types))
	if useful.is_empty():
		return []
	# The current "round" of the pool: the fewest copies of any useful relic.
	var round_now := 1000
	for relic in useful:
		round_now = mini(round_now, copies(relic.id))
	var offer := []
	var odds: Array = ODDS[clampi(number, 0, ODDS.size() - 1)]
	for card in 3:
		# Roll a rarity, then try lower rarities, then higher, if none are left.
		var roll := rng.randf()
		var rarity := 0
		if roll > odds[0]:
			rarity = 1 if roll <= odds[0] + odds[1] else 2
		var tiers := range(rarity, -1, -1) + range(rarity + 1, RARITY_ORDER.size())
		var pick := {}
		# Prefer this round's relics; if fewer than 3 remain, take from the next.
		for round_try in [round_now, round_now + 1]:
			for tier in tiers:
				var choices := useful.filter(func(relic): return relic.rarity == RARITY_ORDER[tier] \
					and copies(relic.id) == round_try and not offer.has(relic))
				if not choices.is_empty():
					pick = choices[rng.randi() % choices.size()]
					break
			if not pick.is_empty():
				break
		if not pick.is_empty():
			offer.append(pick)
	return offer


## How many copies of a relic you have (active or waiting for the next wave).
func copies(id: String) -> int:
	var count := 0
	for relic in active + pending:
		if relic.id == id:
			count += 1
	return count


func add_pending(relic: Dictionary) -> void:
	pending.append(relic)


## Called when a wave starts: pending relics start working. Returns the
## relics that just turned on (for one-time effects like gifts).
func activate_pending() -> Array:
	var turned_on := pending
	active.append_array(pending)
	pending = []
	return turned_on


## A unit's stat with every active relic that helps it applied:
## base * (1 + all "mult") + all "add".
func stat(data: UnitData, name: String, base: float) -> float:
	var mult := 0.0
	var add := 0.0
	for relic in active:
		if relic.filter == "economy" or not matches(relic.filter, data):
			continue
		mult += relic.get("mult", {}).get(name, 0.0)
		add += relic.get("add", {}).get(name, 0.0)
	return base * (1.0 + mult) + add


## True if an active relic gives units like this an ability (e.g. "pierce").
func grants(data: UnitData, ability: String) -> bool:
	for relic in active:
		if relic.filter != "economy" and matches(relic.filter, data) and relic.get("grant", []).has(ability):
			return true
	return false


## The total of an economy rule over the active relics (0 if none).
func economy(key: String) -> float:
	var total := 0.0
	for relic in active:
		total += relic.get("economy", {}).get(key, 0.0)
	return total
