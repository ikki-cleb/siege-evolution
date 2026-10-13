class_name CalmBackground
extends RefCounted
## The background filter ("Fog + Mute", shaders/background_calm.gdshader).
## Busy pictures (lots of small detail and contrast) get a stronger filter
## automatically; the player's Background setting scales it all (0 = off,
## 1 = Medium, 1.5 = Strong). Used by the Board and the Settings preview.

const SHADER := preload("res://shaders/background_calm.gdshader")
## A typical background's busyness (the middle of all 35 painted
## backgrounds). Busier ones get more filter, calmer ones less.
const BUSY_REFERENCE := 38.0
## How far the busyness can push the strength, as a multiplier.
const BUSY_MIN := 0.75
const BUSY_MAX := 1.4


## A filter material for this picture at the player's chosen strength.
static func make_material(image: Image, player_strength: float) -> ShaderMaterial:
	var small := _shrink(image)
	var material := ShaderMaterial.new()
	material.shader = SHADER
	var average := _average(small)
	material.set_meta("busy_factor", busy_factor(small))
	material.set_shader_parameter("avg_color", Vector3(average.r, average.g, average.b))
	material.set_shader_parameter("avg_lum", average.get_luminance())
	set_strength(material, player_strength)
	return material


## Changes the strength live (the Settings slider).
static func set_strength(material: ShaderMaterial, player_strength: float) -> void:
	var factor: float = material.get_meta("busy_factor", 1.0)
	material.set_shader_parameter("strength", player_strength * factor)


## How much stronger (or weaker) this picture's filter is: 1.0 for a
## typical background, up to BUSY_MAX for the busiest.
static func busy_factor(small: Image) -> float:
	return clamp(busyness(small) / BUSY_REFERENCE, BUSY_MIN, BUSY_MAX)


## Busyness: how much each pixel differs from its 8 neighbors (edges and
## fine texture), plus how spread out the brightness is (contrast), on a
## 0-255 scale. Measured on a small copy so it's quick.
static func busyness(small: Image) -> float:
	var w := small.get_width()
	var h := small.get_height()
	var lum := PackedFloat32Array()
	lum.resize(w * h)
	var total := 0.0
	for y in h:
		for x in w:
			var v := small.get_pixel(x, y).get_luminance() * 255.0
			lum[y * w + x] = v
			total += v
	var mean := total / (w * h)
	var spread := 0.0
	var edges := 0.0
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			var i := y * w + x
			var around := lum[i - w - 1] + lum[i - w] + lum[i - w + 1] + lum[i - 1] \
				+ lum[i + 1] + lum[i + w - 1] + lum[i + w] + lum[i + w + 1]
			edges += clamp(8.0 * lum[i] - around, 0.0, 255.0)
	for v in lum:
		spread += (v - mean) * (v - mean)
	edges /= (w - 2) * (h - 2)
	spread = sqrt(spread / (w * h))
	return 0.7 * edges + 0.3 * spread


## A 180x280-ish copy, halved step by step (each halving averages pixels).
static func _shrink(image: Image) -> Image:
	var small := image.duplicate() as Image
	if small.is_compressed():
		small.decompress()
	small.clear_mipmaps()
	while small.get_width() > 200:
		small.resize(small.get_width() / 2, small.get_height() / 2, Image.INTERPOLATE_BILINEAR)
	return small


static func _average(small: Image) -> Color:
	var sum := Color(0, 0, 0, 0)
	for y in small.get_height():
		for x in small.get_width():
			sum += small.get_pixel(x, y)
	var count := float(small.get_width() * small.get_height())
	return Color(sum.r / count, sum.g / count, sum.b / count)
