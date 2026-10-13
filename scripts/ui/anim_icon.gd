class_name AnimIcon
extends Control
## An animated sprite for menus: plays a strip (square frames side by side,
## like StripPlayer) scaled up with crisp pixels, fitted to this control's
## size and standing on its bottom edge. Optional soft shadow under it.

var strip: Texture2D
var fps := 4.0
var flip := false
var shadow := true
## Grey and dark, for locked things.
var dimmed := false
var _time := 0.0


func setup(p_strip: Texture2D, p_fps := 4.0, p_flip := false) -> AnimIcon:
	strip = p_strip
	fps = p_fps
	flip = p_flip
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	queue_redraw()
	return self


func _process(delta: float) -> void:
	if strip and strip.get_width() > strip.get_height():
		_time += delta
		queue_redraw()


func _draw() -> void:
	if strip == null:
		return
	var frames := StripPlayer.frames_in(strip)
	var frame := int(_time * fps) % frames
	var side := float(strip.get_height())
	var draw_side := minf(size.x, size.y)
	var rect := Rect2(Vector2((size.x - draw_side) / 2, size.y - draw_side), Vector2(draw_side, draw_side))
	if shadow:
		var foot := Vector2(size.x / 2, size.y - draw_side * 0.06)
		draw_set_transform(foot, 0, Vector2(1, 0.28))
		draw_circle(Vector2.ZERO, draw_side * 0.32, Color(0, 0, 0, 0.32))
		draw_set_transform(Vector2.ZERO)
	var source := Rect2(frame * side, 0, side, side)
	if flip:  # mirror left-right around the middle of this control
		draw_set_transform(Vector2(size.x, 0), 0, Vector2(-1, 1))
	var tint := Color(0.35, 0.33, 0.36) if dimmed else Color.WHITE
	draw_texture_rect_region(strip, rect, source, tint)
	draw_set_transform(Vector2.ZERO)
