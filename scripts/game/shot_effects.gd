class_name ShotEffects
extends Node2D
## Draws short-lived attack visuals: lines from attackers to their targets,
## and expanding rings for pulse attacks.

const SHOT_DURATION := 0.12
const PULSE_DURATION := 0.3

const PUFF_DURATION := 0.35

var _shots: Array[Dictionary] = []
var _pulses: Array[Dictionary] = []
var _puffs: Array[Dictionary] = []


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


func _process(delta: float) -> void:
	if _shots.is_empty() and _pulses.is_empty() and _puffs.is_empty():
		return
	for effect in _shots + _pulses + _puffs:
		effect.time -= delta
	_shots = _shots.filter(func(effect): return effect.time > 0.0)
	_pulses = _pulses.filter(func(effect): return effect.time > 0.0)
	_puffs = _puffs.filter(func(effect): return effect.time > 0.0)
	queue_redraw()


func _draw() -> void:
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
