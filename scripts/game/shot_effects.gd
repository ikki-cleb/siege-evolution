class_name ShotEffects
extends Node2D
## Draws short-lived lines from attackers to their targets.

const SHOT_DURATION := 0.12

var _shots: Array[Dictionary] = []


func add_shot(from: Vector2, to: Vector2, color: Color) -> void:
	_shots.append({"from": from, "to": to, "color": color, "time": SHOT_DURATION})
	queue_redraw()


func _process(delta: float) -> void:
	if _shots.is_empty():
		return
	for shot in _shots:
		shot.time -= delta
	_shots = _shots.filter(func(shot): return shot.time > 0.0)
	queue_redraw()


func _draw() -> void:
	for shot in _shots:
		var color: Color = shot.color
		color.a = shot.time / SHOT_DURATION
		draw_line(shot.from, shot.to, color, 1.0)
