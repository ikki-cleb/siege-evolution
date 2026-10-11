class_name BaseView
extends Node2D
## Draws the home base: one big sprite over its 3x2 tiles (art from
## tools/draw_bases.py). It cracks as the base loses health and flashes red
## and shakes when an invader gets through.

## Seconds the red flash and the shake last after a hit.
const HIT_TIME := 0.35
const CRACK_COLOR := Color(0.08, 0.05, 0.06, 0.85)
## Jagged crack lines, as fractions of the sprite's size (0-1). The first
## set appears below 2/3 health, the second below 1/3.
const CRACKS_1 := [[Vector2(0.38, 0.45), Vector2(0.44, 0.55), Vector2(0.40, 0.63), Vector2(0.46, 0.74)],
	[Vector2(0.62, 0.50), Vector2(0.58, 0.58), Vector2(0.64, 0.66)]]
const CRACKS_2 := [[Vector2(0.24, 0.60), Vector2(0.30, 0.66), Vector2(0.27, 0.74), Vector2(0.33, 0.84)],
	[Vector2(0.70, 0.40), Vector2(0.75, 0.48), Vector2(0.71, 0.56), Vector2(0.77, 0.66), Vector2(0.73, 0.76)],
	[Vector2(0.50, 0.30), Vector2(0.53, 0.38), Vector2(0.49, 0.45)]]

var texture: Texture2D
## Where the sprite is drawn (board pixels): covers the base tiles plus the
## headroom above them.
var area := Rect2()
## 0-1: how healthy the base is (set by the board).
var health := 1.0
var _hit := 0.0


func hit() -> void:
	_hit = HIT_TIME
	queue_redraw()


func _process(delta: float) -> void:
	if _hit > 0.0:
		_hit = maxf(0.0, _hit - delta)
		queue_redraw()


func _draw() -> void:
	if texture == null:
		return
	var shake := Vector2.ZERO
	if _hit > 0.0:
		shake = Vector2(randf_range(-1, 1), randf_range(-1, 1)) * 1.5 * (_hit / HIT_TIME)
	var rect := Rect2(area.position + shake, area.size)
	draw_texture_rect(texture, rect, false)
	if health < 2.0 / 3.0:
		_draw_cracks(CRACKS_1, rect)
	if health < 1.0 / 3.0:
		_draw_cracks(CRACKS_2, rect)
	if _hit > 0.0:
		# A red flash over the sprite, fading out.
		draw_texture_rect(texture, rect, false, Color(1, 0.15, 0.15, 0.7 * _hit / HIT_TIME))


func _draw_cracks(cracks: Array, rect: Rect2) -> void:
	for crack in cracks:
		var points := PackedVector2Array()
		for point in crack:
			points.append(rect.position + rect.size * point)
		draw_polyline(points, CRACK_COLOR, 1.0)
