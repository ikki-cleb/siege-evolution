class_name BossMarker
extends Node2D
## Marks the tile the boss will come from on a boss level: a pulsing purple
## glow with a little pixel skull on it. Shown for the whole level so the
## player can plan for the boss from wave 1.

const GLOW_COLOR := Color(0.75, 0.4, 1.0)
const SKULL_COLOR := Color(0.95, 0.92, 1.0)
const EYE_COLOR := Color(0.25, 0.05, 0.35)

## The skull, one string per row ("#" = bone, "o" = eye socket).
const SKULL := [
	" ##### ",
	"#######",
	"#oo#oo#",
	"#oo#oo#",
	" ##### ",
	" # # # ",
]

## Centers of the boss spawn tiles (in board pixels).
var spots: Array[Vector2] = []


func _process(_delta: float) -> void:
	# Redraw every frame so the glow can pulse.
	if not spots.is_empty():
		queue_redraw()


func _draw() -> void:
	var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 250.0)
	var half := Board.TILE * 0.5
	for spot in spots:
		# Glow: a soft filled tile and a bright outline that breathe.
		draw_rect(Rect2(spot - Vector2(half, half), Vector2(half, half) * 2.0), Color(GLOW_COLOR, 0.15 + 0.2 * pulse))
		draw_rect(Rect2(spot - Vector2(half, half), Vector2(half, half) * 2.0), Color(GLOW_COLOR, 0.6 + 0.4 * pulse), false, 1.0)
		# Skull in the middle of the tile, bobbing gently. (Inside the tile,
		# not above it, so it never pokes off the top of the board.)
		var top_left := (spot + Vector2(-3.5, -3.0 - pulse)).floor()
		for row in SKULL.size():
			var line: String = SKULL[row]
			for column in line.length():
				var pixel := line[column]
				if pixel == " ":
					continue
				var color := EYE_COLOR if pixel == "o" else SKULL_COLOR
				draw_rect(Rect2(top_left + Vector2(column, row), Vector2(1, 1)), color)
