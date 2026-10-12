class_name EvolutionShowcase
extends Control
## The title screen's "hero": an evolution tree. A unit appears at the bottom,
## gold lines fork upward, and both of its evolutions flash in at once: the
## power branch on the left, the utility branch on the right, each with its
## name. Then the next unit. Units come from a hand-picked pool of 40 (see
## data/title_pool.json and menu.gd _showcase_pool()).

const CYCLE := 5.2  ## Seconds per unit.
const FADE := 0.35
const LINES_FROM := 0.55  ## When the fork lines start growing...
const LINES_TO := 1.25  ## ...and finish.
const EVOLVE_AT := 1.35  ## When both evolutions flash in.

## Entries: {"name", "idle", "color", "evolutions": [{"name", "idle"}, {...}]}.
var _pool: Array = []
var _order: Array = []  ## A shuffled order, so every unit shows before repeats.
var _rng := RandomNumberGenerator.new()
var _time := 0.0

var _base: AnimIcon
var _branches: Array[AnimIcon] = []
var _base_name: Label
var _branch_names: Array[Label] = []
var _glow_color := Color.WHITE


func setup(pool: Array, seed_value := -1) -> EvolutionShowcase:
	_pool = pool.filter(func(entry): return entry.evolutions.size() >= 2)
	if seed_value >= 0:
		_rng.seed = seed_value
	else:
		_rng.randomize()
	custom_minimum_size.y = 270
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_base = AnimIcon.new().setup(null)
	add_child(_base)
	_base_name = _name_label(Palette.TEXT_DIM, 11)
	for i in 2:
		var icon := AnimIcon.new().setup(null)
		add_child(icon)
		_branches.append(icon)
		_branch_names.append(_name_label(Palette.GOLD, 12))
	_next()
	return self


func _name_label(color: Color, font_size: int) -> Label:
	var label := Label.new()
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Palette.BG)
	label.add_theme_constant_override("outline_size", 6)
	add_child(label)
	return label


## Shows the next unit of a shuffled order (reshuffled once all have shown).
func _next() -> void:
	_time = 0.0
	if _pool.is_empty():
		return
	if _order.is_empty():
		_order = range(_pool.size())
		for i in range(_order.size() - 1, 0, -1):  # shuffle with our own RNG
			var j := _rng.randi_range(0, i)
			var swap = _order[i]
			_order[i] = _order[j]
			_order[j] = swap
	var entry: Dictionary = _pool[_order.pop_back()]
	_base.strip = load(entry.idle)
	_base_name.text = entry.name
	for i in 2:
		_branches[i].strip = load(entry.evolutions[i].idle)
		_branch_names[i].text = entry.evolutions[i].name
	_glow_color = Color(entry.get("color", "ffffff"))


func _process(delta: float) -> void:
	if _pool.is_empty():
		return
	_time += delta
	if _time >= CYCLE:
		_next()
	_layout()
	queue_redraw()


## Where things go, as fractions of this control's size.
func _base_feet() -> Vector2:
	return Vector2(size.x * 0.5, size.y * 0.94)


func _branch_feet(i: int) -> Vector2:
	return Vector2(size.x * (0.21 if i == 0 else 0.79), size.y * 0.42)


func _fade_in() -> float:
	return clampf(_time / FADE, 0, 1)


func _fade_out() -> float:
	return clampf((CYCLE - _time) / FADE, 0, 1)


## Positions and fades everything for the current moment of the cycle.
func _layout() -> void:
	var alpha := minf(_fade_in(), _fade_out())
	var small := size.y * 0.27
	var feet := _base_feet()
	_base.size = Vector2(small, small)
	_base.position = feet - Vector2(small / 2, small)
	_base.modulate.a = alpha
	_base_name.size = Vector2(160, 18)
	_base_name.position = feet + Vector2(-80, -2)
	_base_name.modulate.a = alpha
	# Both evolutions pop in: grow past full size, then settle.
	var t := _time - EVOLVE_AT
	var grow := 1.0
	if t < 0.2:
		grow = maxf(t, 0.0) / 0.2 * 1.18
	elif t < 0.4:
		grow = lerpf(1.18, 1.0, (t - 0.2) / 0.2)
	var side := size.y * 0.4 * grow
	for i in 2:
		var branch_feet := _branch_feet(i)
		_branches[i].size = Vector2(side, side)
		_branches[i].position = branch_feet - Vector2(side / 2, side)
		_branches[i].modulate.a = _fade_out() if t > 0 else 0.0
		_branch_names[i].size = Vector2(150, 18)
		_branch_names[i].position = branch_feet + Vector2(-75, 0)
		_branch_names[i].modulate.a = _fade_out() if t > 0.1 else 0.0


func _draw() -> void:
	if _pool.is_empty():
		return
	var t := _time - EVOLVE_AT
	var fade_out := _fade_out()
	var base_alpha := minf(_fade_in(), fade_out)
	# Spotlit floor ovals under each unit, so dark units still stand out.
	_floor(_base_feet(), size.y * 0.15, base_alpha)
	for i in 2:
		_floor(_branch_feet(i), size.y * 0.2, fade_out if t > 0 else 0.0)
	# Glows in the unit's pack color behind both evolutions.
	if t > 0:
		for i in 2:
			var center := _branch_feet(i) - Vector2(0, size.y * 0.2)
			for k in 5:
				draw_circle(center, size.y * (0.26 - k * 0.045), Color(_glow_color.lightened(0.2), 0.08 * fade_out))
	# The fork: gold lines growing from the base up to each branch.
	var grow := clampf((_time - LINES_FROM) / (LINES_TO - LINES_FROM), 0, 1)
	var start := _base_feet() - Vector2(0, size.y * 0.29)
	var split := start - Vector2(0, size.y * 0.04)
	if grow > 0:
		var line_color := Color(Palette.GOLD, 0.9 * fade_out)
		var stem := clampf(grow * 3.0, 0, 1)  # the short stem first...
		draw_line(start, start.lerp(split, stem), line_color, 3.0)
		var arm := clampf(grow * 1.5 - 0.5, 0, 1)  # ...then both arms together
		for i in 2:
			# Each arm ends just under its branch's name, a little toward the middle.
			var goal := _branch_feet(i) + Vector2(size.x * (0.06 if i == 0 else -0.06), size.y * 0.1)
			if arm > 0:
				draw_line(split, split.lerp(goal, arm), line_color, 3.0)
				if arm >= 1.0:
					draw_circle(goal, 3.5, line_color)
		draw_circle(split, 3.5, line_color)
	# The flash: bright rings bursting outward as both evolve.
	if t > 0 and t < 0.5:
		var k := t / 0.5
		for i in 2:
			var center := _branch_feet(i) - Vector2(0, size.y * 0.2)
			draw_circle(center, size.y * 0.08 * (1.0 - k) + 4, Color(1, 1, 1, 0.9 * (1.0 - k)))
			draw_arc(center, size.y * (0.1 + 0.3 * k), 0, TAU, 40, Color(1, 1, 1, 1.0 - k), 3.0)
	# Twinkling sparkles around both evolutions.
	if t > 0.2:
		for i in 2:
			var center := _branch_feet(i) - Vector2(0, size.y * 0.2)
			for s in 4:
				var a := s * TAU / 4 + 0.7 + i
				var r := size.y * (0.22 + 0.04 * (s % 2))
				var twinkle := absf(sin(_time * 3.0 + s * 1.7 + i)) * fade_out
				var p := center + Vector2(cos(a), sin(a)) * r
				var arm_len := 2.5 + 3.0 * twinkle
				draw_line(p - Vector2(arm_len, 0), p + Vector2(arm_len, 0), Color(1, 1, 1, twinkle), 1.5)
				draw_line(p - Vector2(0, arm_len), p + Vector2(0, arm_len), Color(1, 1, 1, twinkle), 1.5)


func _floor(feet: Vector2, radius: float, alpha: float) -> void:
	draw_set_transform(feet - Vector2(0, radius * 0.1), 0, Vector2(1, 0.3))
	for i in 4:
		draw_circle(Vector2.ZERO, radius * (1.0 - i * 0.2), Color(1, 0.93, 0.85, 0.07 * alpha))
	draw_set_transform(Vector2.ZERO)
