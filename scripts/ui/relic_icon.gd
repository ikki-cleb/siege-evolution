class_name RelicIcon
extends Control
## Draws a relic's 16x16 pixel icon on its rarity badge (20x20 pixels in all,
## scaled up to fit the control without blurring).
##
## The pictures are made by tools/draw_relics.py:
##   art/relics/<relic id>.png      the icon itself
##   art/relics/badge_<rarity>.png  the grey / blue / purple backing

const ART_DIR := "res://art/relics/"
## The badge is 20 pixels wide; the icon sits 2 pixels in from its edge.
const BADGE_PIXELS := 20.0
const ICON_INSET := 2.0

var _icon: Texture2D
var _badge: Texture2D
## Dim the icon (e.g. a relic that isn't active yet).
var dimmed := false:
	set(value):
		dimmed = value
		queue_redraw()


func setup(relic: Dictionary) -> RelicIcon:
	_icon = _load(ART_DIR + relic.id + ".png")
	_badge = _load(ART_DIR + "badge_" + relic.rarity + ".png")
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST  # crisp pixels
	queue_redraw()
	return self


## True if a relic has its icon picture (the rules tests check every relic).
static func has_art(relic_id: String) -> bool:
	return ResourceLoader.exists(ART_DIR + relic_id + ".png")


static func _load(path: String) -> Texture2D:
	return load(path) if ResourceLoader.exists(path) else null


func _draw() -> void:
	# Fit the badge in the middle of the control, square.
	var side := minf(size.x, size.y)
	var px := side / BADGE_PIXELS
	var origin := (size - Vector2(side, side)) / 2.0
	var tint := Color(1, 1, 1, 0.45) if dimmed else Color.WHITE
	if _badge:
		draw_texture_rect(_badge, Rect2(origin, Vector2(side, side)), false, tint)
	if _icon:
		var inset := Vector2(ICON_INSET, ICON_INSET) * px
		draw_texture_rect(_icon, Rect2(origin + inset, Vector2(side, side) - inset * 2.0), false, tint)
