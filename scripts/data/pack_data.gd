class_name PackData
extends Resource
## A starter pack: a themed set of six units the player picks at the start
## of a biome. The same pack plays the same way in every biome; each biome
## just gives its units new names and art to fit the scale.

## Pack slots unlock as the player clears levels in the biome:
## slots 0-2 on level 1, slot 3 on level 2, slot 4 on level 4, slot 5 on level 6.
const UNLOCK_LEVELS: Array[int] = [1, 1, 1, 2, 4, 6]

@export var id: String = ""
@export var display_name: String = ""
@export_multiline var description: String = ""
@export var color: Color = Color.WHITE
## Store item that unlocks this pack in every world ("" = free).
@export var product_id: String = ""
## Exactly six units, in slot order.
@export var units: Array[UnitData] = []


## The units available on a level (1-based level number in the biome).
func units_for_level(level_number: int) -> Array[UnitData]:
	var result: Array[UnitData] = []
	for slot in units.size():
		if UNLOCK_LEVELS[slot] <= level_number:
			result.append(units[slot])
	return result


## The unit that first unlocks on this level, if any.
func unit_unlocked_on(level_number: int) -> UnitData:
	for slot in units.size():
		if UNLOCK_LEVELS[slot] == level_number and level_number > 1:
			return units[slot]
	return null
