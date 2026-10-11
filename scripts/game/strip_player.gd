class_name StripPlayer
extends Node
## Plays animation strips on a Sprite2D. A strip is one PNG with square
## frames side by side (e.g. 4 frames of 64x64 = 256x64), so the number of
## frames is simply width / height.
##
## One strip loops (idle for units, move for invaders); another can play once
## on top of it (an attack) and then the loop comes back.

signal finished  ## A play_once() strip ended (and nothing loops).

const IDLE_FPS := 4.0
const ACTION_FPS := 10.0

var sprite: Sprite2D
var _loop: Texture2D
var _loop_fps := IDLE_FPS
var _fps := IDLE_FPS
var _looping := true
var _time := 0.0


static func frames_in(strip: Texture2D) -> int:
	return maxi(1, strip.get_width() / strip.get_height())


## Starts looping `strip` (or plays nothing if it's null).
func start_loop(p_sprite: Sprite2D, strip: Texture2D, fps := IDLE_FPS) -> void:
	sprite = p_sprite
	_loop = strip
	_loop_fps = fps
	if strip:
		_show(strip, fps, true)


## Plays `strip` once, then returns to the loop (if there is one).
func play_once(p_sprite: Sprite2D, strip: Texture2D, fps := ACTION_FPS) -> void:
	sprite = p_sprite
	if strip:
		_show(strip, fps, false)


func _show(strip: Texture2D, fps: float, looping: bool) -> void:
	sprite.texture = strip
	sprite.hframes = frames_in(strip)
	# The enemy outline shader needs the frame count too (see invader.gd).
	if sprite.material is ShaderMaterial:
		sprite.material.set_shader_parameter("frames", sprite.hframes)
	sprite.frame = 0
	_fps = fps
	_looping = looping
	_time = 0.0


func _process(delta: float) -> void:
	if sprite == null or sprite.hframes <= 1 and _looping:
		return
	_time += delta
	if _time < 1.0 / _fps:
		return
	_time = 0.0
	if sprite.frame + 1 < sprite.hframes:
		sprite.frame += 1
	elif _looping:
		sprite.frame = 0
	elif _loop:
		_show(_loop, _loop_fps, true)
	else:
		finished.emit()
		sprite = null
