class_name BiomeData
extends Resource
## One world: 5 levels at one scale, played with one chosen starter pack.

@export var id: String = ""
@export var display_name: String = ""
@export_multiline var description: String = ""
@export var packs: Array[PackData] = []
## Exactly 5 levels. The first teaches; the last ends with a boss.
@export var levels: Array[LevelData] = []

@export_group("Tiles")
@export var floor_texture: Texture2D
@export var rock_texture: Texture2D
@export var spawn_texture: Texture2D
@export var base_texture: Texture2D
## Only needed by worlds with sea levels.
@export var water_texture: Texture2D
@export var sea_spawn_texture: Texture2D


func find_pack(pack_id: String) -> PackData:
	for pack in packs:
		if pack.id == pack_id:
			return pack
	return null
