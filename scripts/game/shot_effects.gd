class_name ShotEffects
extends Node2D
## Draws short-lived attack visuals: lines from attackers to their targets,
## and expanding rings for pulse attacks. Also falling bombs (with a warning
## on their target tile) and the explosions when they land.

const SHOT_DURATION := 0.12
const PULSE_DURATION := 0.3

const PUFF_DURATION := 0.35
const EXPLOSION_DURATION := 0.6
const WARNING_COLOR := Color(1, 0.2, 0.2)
const BOMB_COLOR := Color(0.12, 0.1, 0.14)
const FUSE_COLOR := Color(1, 0.85, 0.3)

var _shots: Array[Dictionary] = []
var _pulses: Array[Dictionary] = []
var _puffs: Array[Dictionary] = []
## {from, to, time, duration}
var _bombs: Array[Dictionary] = []
## {center, radius, time, smoke}
var _explosions: Array[Dictionary] = []
## Burrow holes / water splashes: {center, water, time, duration}
var _holes: Array[Dictionary] = []
const HOLE_COLOR := Color(0.16, 0.1, 0.06)
const HOLE_RIM := Color(0.5, 0.34, 0.2)
const SPLASH_COLOR := Color(0.85, 0.95, 1.0)


func add_shot(from: Vector2, to: Vector2, color: Color) -> void:
	_shots.append({"from": from, "to": to, "color": color, "time": SHOT_DURATION})
	queue_redraw()


func add_pulse(center: Vector2, radius: float, color: Color) -> void:
	_pulses.append({"center": center, "radius": radius, "color": color, "time": PULSE_DURATION})
	queue_redraw()


## A little burst of pixels where an invader died.
func add_puff(center: Vector2, color: Color) -> void:
	var bits: Array[Vector2] = []
	for i in 6:
		bits.append(Vector2.from_angle(randf() * TAU) * randf_range(10, 22))
	_puffs.append({"center": center, "color": color, "bits": bits, "time": PUFF_DURATION})
	queue_redraw()


## A bomb falling from `from` to `to` over `duration` seconds. The target
## tile blinks red until it lands. (The board applies the damage.)
func add_falling_bomb(from: Vector2, to: Vector2, duration: float) -> void:
	_bombs.append({"from": from, "to": to, "time": duration, "duration": duration})
	queue_redraw()


## A big blast: a bright flash, a fireball, a shockwave ring, a glow over
## the 3x3 tiles it hits, and smoke drifting up. `radius` is in pixels.
func add_explosion(center: Vector2, radius: float) -> void:
	var smoke: Array[Vector2] = []
	for i in 8:
		smoke.append(Vector2.from_angle(randf() * TAU) * randf_range(4, radius * 0.8))
	_explosions.append({"center": center, "radius": radius, "time": EXPLOSION_DURATION, "smoke": smoke})
	queue_redraw()


## A hole in the ground where a burrower dug in or came up (or, in water,
## rings of foam). It fades out over `duration` seconds.
func add_hole(center: Vector2, water: bool, duration := 3.0) -> void:
	_holes.append({"center": center, "water": water, "time": duration, "duration": duration})
	queue_redraw()


func _process(delta: float) -> void:
	if _shots.is_empty() and _pulses.is_empty() and _puffs.is_empty() \
			and _bombs.is_empty() and _explosions.is_empty() and _holes.is_empty():
		return
	for effect in _shots + _pulses + _puffs + _bombs + _explosions + _holes:
		effect.time -= delta
	_shots = _shots.filter(func(effect): return effect.time > 0.0)
	_pulses = _pulses.filter(func(effect): return effect.time > 0.0)
	_puffs = _puffs.filter(func(effect): return effect.time > 0.0)
	_bombs = _bombs.filter(func(effect): return effect.time > 0.0)
	_explosions = _explosions.filter(func(effect): return effect.time > 0.0)
	_holes = _holes.filter(func(effect): return effect.time > 0.0)
	queue_redraw()


func _draw() -> void:
	for hole in _holes:
		_draw_hole(hole)
	for shot in _shots:
		var color: Color = shot.color
		color.a = shot.time / SHOT_DURATION
		draw_line(shot.from, shot.to, color, 1.0)
	for puff in _puffs:
		var progress: float = 1.0 - puff.time / PUFF_DURATION
		var color: Color = puff.color
		color.a = 1.0 - progress
		for bit in puff.bits:
			draw_rect(Rect2(puff.center + bit * progress - Vector2(1, 1), Vector2(2, 2)), color)
	for pulse in _pulses:
		var progress: float = 1.0 - pulse.time / PULSE_DURATION
		var color: Color = pulse.color
		color.a = 0.6 * (1.0 - progress)
		draw_arc(pulse.center, pulse.radius * (0.3 + 0.7 * progress), 0, TAU, 32, color, 1.0)
	for bomb in _bombs:
		_draw_falling_bomb(bomb)
	for explosion in _explosions:
		_draw_explosion(explosion)


func _draw_hole(hole: Dictionary) -> void:
	var fade: float = minf(1.0, hole.time / 0.8)  # fades out in the last 0.8s
	var center: Vector2 = hole.center
	if hole.water:
		# Foam rings spreading out on the water.
		var age: float = hole.duration - hole.time
		for i in 2:
			var radius := 3.0 + fmod(age * 6.0 + i * 3.0, 7.0)
			draw_arc(center, radius, 0, TAU, 20, Color(SPLASH_COLOR, 0.6 * fade), 1.0)
		return
	# A dark oval hole with a lighter rim of dug-up dirt.
	draw_set_transform(center + Vector2(0, 3), 0.0, Vector2(1.0, 0.55))
	draw_circle(Vector2.ZERO, 5.0, Color(HOLE_RIM, 0.9 * fade))
	draw_circle(Vector2.ZERO, 3.6, Color(HOLE_COLOR, 0.95 * fade))
	draw_set_transform(Vector2.ZERO)


func _draw_falling_bomb(bomb: Dictionary) -> void:
	var progress: float = 1.0 - bomb.time / bomb.duration
	var to: Vector2 = bomb.to
	# Warning on the target: the 3x3 blast area tinted red, plus corner
	# brackets on the target tile, blinking faster as the bomb gets close.
	var blink := 0.5 + 0.5 * sin(progress * progress * 40.0)
	var tile := float(Board.TILE)
	draw_rect(Rect2(to - Vector2(tile, tile) * 1.5, Vector2(tile, tile) * 3.0), Color(WARNING_COLOR, 0.12 + 0.12 * blink))
	var half := tile * 0.5
	var arm := 4.0
	var bracket := Color(WARNING_COLOR, 0.5 + 0.5 * blink)
	for corner in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
		var tip: Vector2 = to + corner * half
		draw_line(tip, tip - Vector2(corner.x * arm, 0), bracket, 1.0)
		draw_line(tip, tip - Vector2(0, corner.y * arm), bracket, 1.0)
	# A shadow that grows as the bomb comes down.
	draw_circle(to, 1.5 + 3.5 * progress, Color(0, 0, 0, 0.35))
	# The bomb itself speeds up as it falls (ease-in), with a lit fuse.
	var pos: Vector2 = (bomb.from as Vector2).lerp(to, progress * progress)
	draw_circle(pos, 3.0, BOMB_COLOR)
	draw_circle(pos + Vector2(-1, -1), 1.0, Color(1, 1, 1, 0.5))
	draw_rect(Rect2(pos + Vector2(1, -5), Vector2(1, 2)), FUSE_COLOR if blink > 0.5 else Color.WHITE)


func _draw_explosion(explosion: Dictionary) -> void:
	var progress: float = 1.0 - explosion.time / EXPLOSION_DURATION
	var center: Vector2 = explosion.center
	var radius: float = explosion.radius
	var fade := 1.0 - progress
	# The 3x3 tiles that took damage glow orange.
	var tile := float(Board.TILE)
	draw_rect(Rect2(center - Vector2(tile, tile) * 1.5, Vector2(tile, tile) * 3.0), Color(1, 0.5, 0.1, 0.35 * fade))
	# A white flash for the first moment, then a shrinking fireball.
	if progress < 0.15:
		draw_circle(center, radius, Color(1, 1, 0.9, 0.8))
	draw_circle(center, radius * 0.7 * (1.0 - progress * 0.6), Color(1, 0.55, 0.15, 0.8 * fade))
	draw_circle(center, radius * 0.4 * (1.0 - progress * 0.8), Color(1, 0.95, 0.5, fade))
	# A shockwave ring racing outward.
	draw_arc(center, radius * (0.4 + 1.0 * progress), 0, TAU, 32, Color(1, 0.8, 0.4, 0.7 * fade), 1.5)
	# Smoke puffs drifting outward and up.
	for bit in explosion.smoke:
		var puff_pos: Vector2 = center + bit * (0.4 + progress) + Vector2(0, -8.0 * progress)
		draw_circle(puff_pos, 2.0 + 2.0 * progress, Color(0.35, 0.33, 0.38, 0.6 * fade))
