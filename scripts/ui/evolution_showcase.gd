class_name EvolutionShowcase
extends Control
## The title screen's "hero": a random unit appears on the left, arrows light
## up, and it evolves with a flash into one of its evolutions on the right
## (bigger, with its name in gold). Then a new random unit. Units come from
## data/showcase.json (written by the content build), from unlocked worlds.

const CYCLE := 4.6  ## Seconds per unit.
const EVOLVE_AT := 1.7  ## When the evolution flashes in.
const FADE := 0.35

## Entries: {"name", "idle", "color", "evolutions": [{"name", "idle"}]}.
var _pool: Array = []
var _rng := RandomNumberGenerator.new()
var _time := 0.0
var _last := -1

var _base: AnimIcon
var _evolved: AnimIcon
var _base_name: Label
var _evolved_name: Label
var _glow_color := Color.WHITE


func setup(pool: Array, seed_value := -1) -> EvolutionShowcase:
	_pool = pool
	if seed_value >= 0:
		_rng.seed = seed_value
	else:
		_rng.randomize()
	custom_minimum_size.y = 250
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_base = AnimIcon.new().setup(null)
	_evolved = AnimIcon.new().setup(null)
	add_child(_base)
	add_child(_evolved)
	_base_name = _name_label(Palette.TEXT_DIM, 11)
	_evolved_name = _name_label(Palette.GOLD, 12)
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


## Picks a new random unit (not the same as last time) and one of its evolutions.
func _next() -> void:
	_time = 0.0
	if _pool.is_empty():
		return
	var index := _rng.randi_range(0, _pool.size() - 1)
	if index == _last and _pool.size() > 1:
		index = (index + 1) % _pool.size()
	_last = index
	var entry: Dictionary = _pool[index]
	var evolution: Dictionary = entry.evolutions[_rng.randi_range(0, entry.evolutions.size() - 1)]
	_base.strip = load(entry.idle)
	_evolved.strip = load(evolution.idle)
	_base_name.text = entry.name
	_evolved_name.text = evolution.name
	_glow_color = Color(entry.get("color", "ffffff"))


func _process(delta: float) -> void:
	if _pool.is_empty():
		return
	_time += delta
	if _time >= CYCLE:
		_next()
	_layout()
	queue_redraw()


## Positions and fades everything for the current moment of the cycle.
func _layout() -> void:
	var fade_in := clampf(_time / FADE, 0, 1)
	var fade_out := clampf((CYCLE - _time) / FADE, 0, 1)
	var alpha := minf(fade_in, fade_out)
	var small := size.y * 0.36
	var big := size.y * 0.62
	_base.size = Vector2(small, small)
	_base.position = Vector2(size.x * 0.22 - small / 2, size.y * 0.78 - small)
	_base.modulate.a = alpha
	# The evolution pops in: grows past full size, then settles.
	var t := _time - EVOLVE_AT
	var grow := 1.0
	if t < 0.2:
		grow = maxf(t, 0.0) / 0.2 * 1.18  # grows to 118%...
	elif t < 0.4:
		grow = lerpf(1.18, 1.0, (t - 0.2) / 0.2)  # ...then settles back
	var side := big * grow
	_evolved.size = Vector2(side, side)
	_evolved.position = Vector2(size.x * 0.68 - side / 2, size.y * 0.86 - side)
	_evolved.modulate.a = fade_out if t > 0 else 0.0
	_base_name.position = Vector2(size.x * 0.22 - 80, size.y * 0.8)
	_base_name.size = Vector2(160, 20)
	_base_name.modulate.a = alpha
	_evolved_name.position = Vector2(size.x * 0.68 - 100, size.y * 0.88)
	_evolved_name.size = Vector2(200, 20)
	_evolved_name.modulate.a = fade_out if t > 0.1 else 0.0


func _draw() -> void:
	if _pool.is_empty():
		return
	var t := _time - EVOLVE_AT
	var center := Vector2(size.x * 0.68, size.y * 0.52)
	var fade_out := clampf((CYCLE - _time) / FADE, 0, 1)
	var fade_in := clampf(_time / FADE, 0, 1)
	# Spotlit floor ovals under both units, so dark units still stand out.
	for spot in [[Vector2(size.x * 0.22, size.y * 0.76), size.y * 0.2, minf(fade_in, fade_out)],
			[Vector2(size.x * 0.68, size.y * 0.84), size.y * 0.3, fade_out if t > 0 else 0.0]]:
		draw_set_transform(spot[0], 0, Vector2(1, 0.3))
		for i in 4:
			draw_circle(Vector2.ZERO, spot[1] * (1.0 - i * 0.2), Color(1, 0.93, 0.85, 0.07 * spot[2]))
		draw_set_transform(Vector2.ZERO)
	# A glow in the unit's pack color behind the evolution.
	if t > 0:
		for i in 6:
			var r := size.y * (0.44 - i * 0.06)
			draw_circle(center, r, Color(_glow_color.lightened(0.2), 0.085 * fade_out))
	# Three arrows that light up one after another before the evolution.
	for i in 3:
		var lit := clampf((_time - 0.6 - i * 0.25) * 4.0, 0, 1) * clampf((CYCLE - _time) / FADE, 0, 1)
		var x := size.x * 0.4 + i * 14
		var y := size.y * 0.55
		draw_colored_polygon(PackedVector2Array([Vector2(x, y - 8), Vector2(x + 10, y), Vector2(x, y + 8)]),
			Color(Palette.GOLD, 0.2 + 0.8 * lit))
	# The flash: a bright ring bursting outward as it evolves.
	if t > 0 and t < 0.5:
		var k := t / 0.5
		draw_circle(center, size.y * 0.1 * (1.0 - k) + 4, Color(1, 1, 1, 0.9 * (1.0 - k)))
		draw_arc(center, size.y * (0.12 + 0.4 * k), 0, TAU, 40, Color(1, 1, 1, 1.0 - k), 3.0)
	# Twinkling sparkles around the evolved unit.
	if t > 0.2:
		for i in 5:
			var a := i * TAU / 5 + 0.7
			var r := size.y * (0.3 + 0.06 * (i % 2))
			var twinkle := absf(sin(_time * 3.0 + i * 1.7)) * fade_out
			var p := center + Vector2(cos(a), sin(a)) * r
			var s := 3.0 + 3.0 * twinkle
			draw_line(p - Vector2(s, 0), p + Vector2(s, 0), Color(1, 1, 1, twinkle), 1.5)
			draw_line(p - Vector2(0, s), p + Vector2(0, s), Color(1, 1, 1, twinkle), 1.5)
