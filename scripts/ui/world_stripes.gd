class_name WorldStripes
extends Control
## The title screen's backdrop: slanted slices of every world's painted map,
## side by side, slowly drifting sideways and looping. Each slice has a thin
## line in its world's accent color, and the bottom fades into the menu color.

const SPEED := 9.0  ## Pixels per second.
const SLANT := 0.28  ## How far a slice leans (x shift per pixel of height).
const DARKEN := Color(0.5, 0.46, 0.5)  ## Multiplied into the pictures.

## [texture, accent color] per world.
var _slices: Array = []
var _offset := 0.0
var fade_color := Color.BLACK


## `slices`: an array of [Texture2D, Color].
func setup(slices: Array, p_fade_color: Color) -> WorldStripes:
	_slices = slices
	fade_color = p_fade_color
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	return self


func _process(delta: float) -> void:
	_offset += SPEED * delta
	queue_redraw()


func _draw() -> void:
	if _slices.is_empty():
		return
	var w := size.x / 4.5  ## Each slice's width (about 4.5 visible at once).
	var lean := size.y * SLANT
	var total := w * _slices.size()
	var start := fposmod(_offset, total) - total
	# Draw enough loops to cover the screen, including the leaning overhang.
	var x := start - lean
	var i := 0
	while x < size.x + lean:
		var slice: Array = _slices[i % _slices.size()]
		_draw_slice(slice[0], slice[1], x, w, lean)
		x += w
		i += 1
	_draw_fade()


## One slanted slice: a parallelogram showing the middle of the picture.
func _draw_slice(texture: Texture2D, accent: Color, x: float, w: float, lean: float) -> void:
	var top_left := Vector2(x + lean, 0)
	var points := PackedVector2Array([top_left, top_left + Vector2(w, 0),
		Vector2(x + w, size.y), Vector2(x, size.y)])
	# Map the screen shape onto the picture (it covers the full height).
	var tex_size := texture.get_size()
	var scale := tex_size.y / size.y
	var uvs := PackedVector2Array()
	for p in points:
		var u := (p.x - x - lean * 0.5) * scale + tex_size.x * 0.5 - w * scale * 0.5
		uvs.append(Vector2(u / tex_size.x, p.y / size.y))
	draw_polygon(points, PackedColorArray([DARKEN, DARKEN, DARKEN, DARKEN]), uvs, texture)
	draw_line(points[0], points[3], Color(accent, 0.8), 2.0)


## Fades the lower part of the screen into the menu color (so buttons read).
func _draw_fade() -> void:
	var top := size.y * 0.45
	var clear := Color(fade_color, 0.0)
	draw_polygon(PackedVector2Array([Vector2(0, top), Vector2(size.x, top), Vector2(size.x, size.y * 0.72),
		Vector2(0, size.y * 0.72)]), PackedColorArray([clear, clear, fade_color, fade_color]))
	draw_rect(Rect2(0, size.y * 0.72, size.x, size.y * 0.28 + 1), fade_color)
	draw_rect(Rect2(Vector2.ZERO, size), Color(fade_color, 0.25))
