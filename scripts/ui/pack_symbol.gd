class_name PackSymbol
extends Control
## A pack's symbol (castle, honeycomb, crosshair, snowflake, poison drop)
## that fills with the pack's color from the bottom up as it beats levels.
## fill = 0 shows an empty silhouette, 1 the full color symbol, 0.4 the
## bottom 40% colored.
##
## The pictures are made by tools/draw_pack_symbols.py:
##   art/packs/<pack>.png        the colored symbol
##   art/packs/<pack>_empty.png  its empty silhouette

const ART_DIR := "res://art/packs/"
## Every pack, in the order the menus show them.
const ORDER := ["fortress", "swarm", "precision", "control", "toxin"]
const PIXELS := 16

var _full: Texture2D
var _empty: Texture2D
## The rows the symbol actually covers (fill is measured over these, so
## 1/5 always colors a fair share of the shape).
var _top_row := 0
var _bottom_row := PIXELS
## How much of the symbol is colored in (0 to 1).
var fill := 0.0:
	set(value):
		fill = clampf(value, 0.0, 1.0)
		queue_redraw()


## `size_px` is how big to draw it on screen (square).
func setup(pack_id: String, p_fill: float, size_px := 20.0) -> PackSymbol:
	_full = load(ART_DIR + pack_id + ".png") if ResourceLoader.exists(ART_DIR + pack_id + ".png") else null
	_empty = load(ART_DIR + pack_id + "_empty.png") if ResourceLoader.exists(ART_DIR + pack_id + "_empty.png") else null
	if _full:
		var used := _full.get_image().get_used_rect()
		_top_row = used.position.y
		_bottom_row = used.end.y
	fill = p_fill
	custom_minimum_size = Vector2(size_px, size_px)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST  # crisp pixels
	return self


func _draw() -> void:
	if _full == null or _empty == null:
		return
	var side := minf(size.x, size.y)
	var rect := Rect2((size - Vector2(side, side)) / 2.0, Vector2(side, side))
	draw_texture_rect(_empty, rect, false)
	# Color in whole pixel rows from the bottom of the shape up.
	var rows := roundi(fill * (_bottom_row - _top_row)) + (PIXELS - _bottom_row)
	if fill <= 0.0:
		return
	var top := PIXELS - rows
	var px := side / PIXELS
	var dest := Rect2(rect.position + Vector2(0, top * px), Vector2(side, rows * px))
	draw_texture_rect_region(_full, dest, Rect2(0, top, PIXELS, rows))
