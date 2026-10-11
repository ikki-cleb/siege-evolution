class_name ObstacleLayer
extends Node2D
## Draws the map objects: every obstacle tile (in one of its world's 3
## looks) and animated water. The art is 32x32 per tile (the board is drawn
## at 2x, so every pixel shows), made by tools/draw_objects.py:
##   obstacle.png    3 rows (looks) x 1 column, or x 4 columns if animated
##   water_anim.png  1 row x 4 frames

const LOOKS := 3
const FPS := 4.0

var board: Board
var obstacles: Texture2D  # null = the board draws its old still tiles
var water: Texture2D
var _frames := 1
var _time := 0.0


func setup(p_board: Board, p_obstacles: Texture2D, p_water: Texture2D) -> ObstacleLayer:
	board = p_board
	obstacles = p_obstacles
	water = p_water
	if obstacles:
		_frames = obstacles.get_width() / (obstacles.get_height() / LOOKS)
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	return self


## True if this layer needs to redraw every frame (something animates).
func _animated() -> bool:
	return _frames > 1 or (water != null and not board.water.is_empty())


func _process(delta: float) -> void:
	if _animated():
		_time += delta
		queue_redraw()


func _draw() -> void:
	var frame := int(_time * FPS)
	var tile := Vector2(Board.TILE, Board.TILE)
	if water:
		var side := float(water.get_height())
		for cell in board.water:
			draw_texture_rect_region(water, Rect2(Vector2(cell * Board.TILE), tile),
				Rect2((frame % 4) * side, 0, side, side))
	if obstacles:
		var side := float(obstacles.get_height()) / LOOKS
		for cell in board.rocks:
			draw_texture_rect_region(obstacles, Rect2(Vector2(cell * Board.TILE), tile),
				Rect2((frame % _frames) * side, look_for(cell) * side, side, side))


## Which of the 3 looks an obstacle tile uses: mixed up, but always the
## same for the same tile.
static func look_for(cell: Vector2i) -> int:
	return posmod(hash(cell), LOOKS)


## A map-object sheet that sits next to a tile ("obstacle.png" next to
## rock.png, "water_anim.png" next to water.png), or null.
static func art_next_to(tile: Texture2D, file: String) -> Texture2D:
	if tile == null or tile.resource_path == "":
		return null
	var path := tile.resource_path.get_base_dir().path_join(file)
	return load(path) if ResourceLoader.exists(path) else null
