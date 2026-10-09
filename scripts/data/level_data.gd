class_name LevelData
extends Resource
## Everything that defines one level. Each level lives in data/levels/.

@export var display_name: String = ""

## The map, one string per row. Every row must be the same length.
##   .  open floor (buildable)
##   #  tissue wall: blocks walkers and building, but fliers pass over it
##   S  invader spawn point (you can have more than one)
##   B  your base
@export var layout: PackedStringArray = []

@export var base_hp: int = 20

## Free units the player starts with. List a unit several times to give
## several copies.
@export var starting_hand: Array[UnitData] = []
## Units the player may buy with ATP during this level.
@export var shop: Array[UnitData] = []
@export var starting_atp: int = 0
## ATP earned after each wave is cleared.
@export var atp_per_wave: int = 8

## Exactly 10 waves per level (by design), played in order.
@export var waves: Array[WaveData] = []
