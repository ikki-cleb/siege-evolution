class_name ConfettiBurst
extends Node2D
## A one-shot pop of confetti from a point: bits fly up and out, tumble down
## under gravity, fade, and then the node removes itself. For small
## celebrations (a new world unlocked, a pack finishing a world).

const GRAVITY := 420.0
const LIFE := 1.6

var _bits: Array[Dictionary] = []
var _time := 0.0


## Adds a burst to `parent` at `where` (in the parent's coordinates).
static func pop(parent: Node, where: Vector2, count := 46, colors: Array = []) -> ConfettiBurst:
	var burst := ConfettiBurst.new()
	burst.position = where
	burst.z_index = 50
	if colors.is_empty():
		colors = [Palette.GOLD, Palette.HEART, Palette.GOOD, Color("#6fb3e8"), Color("#b07aff")]
	for i in count:
		var angle := randf_range(-PI * 0.92, -PI * 0.08)  # mostly upward
		var speed := randf_range(140, 330)
		burst._bits.append({"pos": Vector2.ZERO, "vel": Vector2(cos(angle), sin(angle)) * speed,
			"spin": randf_range(-12, 12), "turn": randf() * TAU, "color": colors[i % colors.size()],
			"size": randf_range(3, 5.5)})
	parent.add_child(burst)
	return burst


func _process(delta: float) -> void:
	_time += delta
	if _time > LIFE:
		queue_free()
		return
	for bit in _bits:
		bit.vel.y += GRAVITY * delta
		bit.vel *= 1.0 - 1.2 * delta  # air drag
		bit.pos += bit.vel * delta
		bit.turn += bit.spin * delta
	queue_redraw()


func _draw() -> void:
	var alpha := clampf((LIFE - _time) / 0.5, 0, 1)
	for bit in _bits:
		# A spinning paper bit: its width shrinks and grows as it tumbles.
		var w: float = bit.size * absf(cos(bit.turn))
		draw_rect(Rect2(bit.pos - Vector2(w, bit.size * 0.6) / 2, Vector2(maxf(w, 1.0), bit.size * 0.6)),
			Color(bit.color, alpha))
