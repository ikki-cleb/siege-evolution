class_name SpawnerView
extends Node2D
## An animated spawner on one spawn tile: plays a 4-frame 32x32 strip in a
## loop (drawn by tools/draw_spawners.py). The board is drawn at 2x, so the
## 32x32 art fills one 16-unit tile with every pixel showing.

const FRAMES := 4
const FPS := 5.0

var strip: Texture2D
var _time := randf() * 2.0  # spawners don't all move in step


func setup(p_strip: Texture2D, cell: Vector2i) -> SpawnerView:
	strip = p_strip
	position = Vector2(cell * Board.TILE)
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	return self


func _process(delta: float) -> void:
	_time += delta
	queue_redraw()


func _draw() -> void:
	var frame := int(_time * FPS) % FRAMES
	var side := float(strip.get_height())
	draw_texture_rect_region(strip, Rect2(0, 0, Board.TILE, Board.TILE), Rect2(frame * side, 0, side, side))


## The spawner strip that goes with a spawn tile: "spawner.png" in the same
## folder (or "sea_spawner.png" for a sea spawn). Null if there is none.
static func strip_for(tile: Texture2D, sea := false) -> Texture2D:
	if tile == null or tile.resource_path == "":
		return null
	var path := tile.resource_path.get_base_dir().path_join("sea_spawner.png" if sea else "spawner.png")
	return load(path) if ResourceLoader.exists(path) else null
