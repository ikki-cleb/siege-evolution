class_name BiomeData
extends Resource
## One world: 7 levels at one scale, played with one chosen starter pack.

@export var id: String = ""
@export var display_name: String = ""
@export_multiline var description: String = ""
@export var packs: Array[PackData] = []
## Exactly 7 levels. The first teaches; the last ends with a boss.
@export var levels: Array[LevelData] = []


func find_pack(pack_id: String) -> PackData:
	for pack in packs:
		if pack.id == pack_id:
			return pack
	return null
