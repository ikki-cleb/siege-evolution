class_name LevelData
extends Resource
## Everything that defines one level. Each level lives in data/levels/<biome>/.
## Levels don't name specific units: the player's chosen pack decides those.

@export var display_name: String = ""

## The map, one string per row. Every row must be the same length.
##   .  open floor (buildable)
##   #  tissue wall: blocks walkers and building, but fliers pass over it
##   S  invader spawn point (you can have more than one)
##   B  your base
##   ~  water (boats only; only units that allow it can be placed here)
##   N  sea spawn point for boats (on water)
@export var layout: PackedStringArray = []

@export var base_hp: int = 20

## Free units in the starting hand, given as an ATP value per pack slot:
## [wall, attacker 1, attacker 2, level-2 unit, level-4 unit, level-6 unit].
## The value is turned into copies of that pack's unit (e.g. 24 = three
## 8-ATP walls or eight 3-ATP walls), so every pack gets a fair hand.
@export var hand_value: PackedInt32Array = [0, 0, 0, 0, 0, 0]
@export var starting_atp: int = 0
## Bonus ATP for clearing a wave without anything reaching the base.
## (Most ATP comes from invaders dropping it when they die.)
@export var atp_per_wave: int = 5

## Show the invaders' predicted route (first level of each biome only).
@export var show_path_preview: bool = false
## Optional footnote shown before each wave (tutorial hints). Index 0 = wave 1.
@export var wave_tips: PackedStringArray = []

@export_group("Tiles")
## Optional tile art for this level (e.g. a station level in a moon world).
## Empty means "use the world's tiles".
@export var floor_texture: Texture2D
@export var rock_texture: Texture2D
@export var spawn_texture: Texture2D
@export var base_texture: Texture2D

## Exactly 10 waves per level (by design), played in order.
@export var waves: Array[WaveData] = []
