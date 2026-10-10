class_name Hud
extends CanvasLayer
## The in-level interface: status at the top, a footnote under the board,
## and the unit bar and buttons at the bottom. Tapping a placed unit swaps the
## unit bar for its evolve/remove options. Colors and styles come from Palette.

const WIDTH := 360
const TOP_HEIGHT := 80
const FOOTNOTE_TOP := 531
const BOTTOM_TOP := 578
const SMALL_FONT := 11
const FONT := 14
const ATP_COLOR := Palette.GOLD
const FINAL_WORLD := "galactic_siege"
const ORB_FLIGHT_TIME := 0.6


## A small glowing ATP orb that flies from a kill to the ATP counter.
class Orb extends Node2D:
	func _draw() -> void:
		draw_circle(Vector2.ZERO, 8.0, Color(1, 0.85, 0.3, 0.3))
		draw_circle(Vector2.ZERO, 4.5, Color(1, 0.95, 0.55))
		draw_circle(Vector2(-1.5, -1.5), 1.5, Color.WHITE)

var game  # The Game node (game.gd)

var _level_label: Label
var _wave_label: Label
var _hp_label: Label
var _atp_label: Label
var _next_label: Label
var _footnote_label: Label
var _message_label: Label
var _unit_row: HBoxContainer
var _unit_buttons := {}  # UnitData -> Button
var _selection_row: HBoxContainer
var _evolve_buttons: Array[Button] = []
var _sell_button: Button
var _speed_button: Button
var _start_button: Button
## Parent of every HUD control (carries the theme).
var _root: Control
## ATP still flying toward the counter (already added to the game's total).
var _orb_atp := 0


func setup(p_game) -> void:
	game = p_game
	# CanvasLayer children don't inherit the game-wide theme, so the HUD gets
	# its own root Control carrying Look's theme.
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.theme = get_node("/root/Look").theme
	add_child(_root)
	_build_top_bar()
	_build_bottom_bar()


func refresh() -> void:
	_level_label.text = "%s · %s" % [game.level.display_name, game.pack.display_name]
	_wave_label.text = "Wave %d/%d" % [game.wave_number, game.level.waves.size()]
	_hp_label.text = "Base %d/%d" % [game.base_hp, game.level.base_hp]
	_atp_label.text = "ATP %d" % (game.atp - _orb_atp)
	_next_label.text = game.next_wave_summary()
	_footnote_label.text = game.footnote()

	var building: bool = game.phase == game.Phase.BUILD
	for type in _unit_buttons:
		var button: Button = _unit_buttons[type]
		var free_left: int = game.hand.get(type.id, 0)
		button.text = "x%d free" % free_left if free_left > 0 else "%d ATP" % type.cost
		button.disabled = not building
		button.set_pressed_no_signal(game.selected_type == type)

	# A tapped unit replaces the unit bar with its options.
	var unit: Unit = game.selected_unit()
	var show_options := unit != null and building
	_unit_row.visible = not show_options
	_selection_row.visible = show_options
	if show_options:
		var evolutions: Array[UnitData] = unit.base_data.evolutions
		for i in _evolve_buttons.size():
			var button := _evolve_buttons[i]
			if unit.is_evolved() or i >= evolutions.size():
				button.text = "Evolved" if unit.is_evolved() else "-"
				button.disabled = true
				button.icon = unit.data.texture if unit.is_evolved() else null
			elif not game.is_veteran(unit):
				button.text = "%s\nafter 1 wave" % evolutions[i].display_name
				button.icon = evolutions[i].texture
				button.disabled = true
			else:
				button.text = "%s\n%d ATP" % [evolutions[i].display_name, evolutions[i].cost]
				button.icon = evolutions[i].texture
				button.disabled = not game.can_evolve(evolutions[i])
		var value: Dictionary = game.sell_value(unit)
		_sell_button.text = "Remove\nto hand" if value.to_hand else "Remove\n+%d ATP" % value.atp

	_speed_button.text = "%dx" % game.speed
	_start_button.disabled = not building
	_start_button.text = "Start Wave" if building else "Wave %d..." % game.wave_number


func show_message(text: String) -> void:
	_message_label.text = text


## Launches an ATP orb from a screen position to the ATP counter. The counter
## only counts it once it lands.
func spawn_orb(from: Vector2, amount: int) -> void:
	_orb_atp += amount
	var orb := Orb.new()
	orb.position = from
	_root.add_child(orb)
	var target := _atp_label.position + Vector2(_atp_label.size.x - 24, _atp_label.size.y / 2)
	var tween := create_tween()
	tween.tween_property(orb, "position", target, ORB_FLIGHT_TIME) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func():
		orb.queue_free()
		_orb_atp -= amount
		_atp_label.modulate = Color.WHITE
		create_tween().tween_property(_atp_label, "modulate", ATP_COLOR, 0.25)
		Sfx.play("atp")
		refresh())


func show_end_screen(won: bool) -> void:
	var final_victory: bool = won and game.is_last_level() and _progress().biome.id == FINAL_WORLD
	if final_victory:
		_show_final_victory()
		return
	Sfx.play("win" if won else "lose")
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.0)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(dim)
	create_tween().tween_property(dim, "color:a", 0.7, 0.3)

	var card := PanelContainer.new()
	card.add_theme_stylebox_override("panel", Palette.panel(Palette.SURFACE, _accent() if won else Palette.BORDER, 12))
	card.position = Vector2(40, 230)
	card.custom_minimum_size = Vector2(280, 0)
	dim.add_child(card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	card.add_child(box)

	var title := Label.new()
	if won and game.is_last_level():
		title.text = "World Cleared!"
	else:
		title.text = "Level Cleared!" if won else "Defenses Broken..."
	title.add_theme_font_size_override("font_size", 26)
	title.modulate = _accent() if won else Palette.TEXT_DIM
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)
	card.scale = Vector2(0.85, 0.85)
	card.pivot_offset = Vector2(140, 80)
	create_tween().tween_property(card, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

	if won and not game.is_last_level():
		var unlock: UnitData = game.pack.unit_unlocked_on(game.level_number + 1)
		if unlock:
			var note := Label.new()
			note.text = "Next level unlocks: %s" % unlock.display_name
			note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			note.add_theme_font_size_override("font_size", FONT)
			box.add_child(note)
		box.add_child(_make_button("Next Level", game.next_level))
	if not won:
		box.add_child(_make_button("Retry", game.retry))
	box.add_child(_make_button("Back to Map" if won and game.is_last_level() else "Level Select", game.quit_to_menu))
	for button in box.get_children():
		if button is Button:
			button.custom_minimum_size = Vector2(200, 48)


## The big finish after beating the Mothership, with a nudge toward the bonus
## worlds the player doesn't own yet.
func _show_final_victory() -> void:
	Sfx.play("victory", 0.0)
	var dim := ColorRect.new()
	dim.color = Color(Palette.BG, 0.0)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(dim)
	create_tween().tween_property(dim, "color:a", 0.93, 0.6)
	var confetti := Confetti.new()
	dim.add_child(confetti)

	var box := VBoxContainer.new()
	box.position = Vector2(24, 110)
	box.custom_minimum_size = Vector2(312, 0)
	box.add_theme_constant_override("separation", 14)
	dim.add_child(box)

	var title := _end_label("VICTORY!", 40, Palette.GOLD)
	var subtitle := _end_label("The Mothership is down and the galaxy is safe.", 16, Palette.TEXT)
	var detail := _end_label("From a single cell to the stars, you defended every scale. Congratulations, Commander!", 13, Palette.TEXT_DIM)
	for label in [title, subtitle, detail]:
		box.add_child(label)

	var missing: Array[String] = []
	for index in _progress().WORLDS.size():
		var world: Dictionary = _progress().WORLDS[index]
		if _progress().is_bonus(index) and not _store().owns(world.product):
			missing.append(world.name)
	if not missing.is_empty():
		var pitch := PanelContainer.new()
		pitch.add_theme_stylebox_override("panel", Palette.panel(Palette.SURFACE, Palette.GOLD, 10))
		box.add_child(pitch)
		var inner := VBoxContainer.new()
		inner.add_theme_constant_override("separation", 8)
		pitch.add_child(inner)
		inner.add_child(_end_label("Ready for more?", 18, Palette.GOLD))
		inner.add_child(_end_label("Bonus worlds: %s. Brand-new places to defend." % " and ".join(missing), 13, Palette.TEXT))
		var store := _make_button("See bonus worlds", game.open_store)
		store.custom_minimum_size.y = 48
		inner.add_child(store)

	var back := _make_button("Back to Map", game.quit_to_menu)
	back.custom_minimum_size.y = 48
	box.add_child(back)
	box.modulate.a = 0.0
	create_tween().tween_property(box, "modulate:a", 1.0, 0.8).set_delay(0.4)


func _end_label(text: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", size)
	label.modulate = color
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = 300
	return label


## The autoloads, looked up at runtime (see Sfx for why).
func _progress() -> Node:
	return get_node("/root/Progress")


func _store() -> Node:
	return get_node("/root/Store")


func _accent() -> Color:
	return Palette.accent(_progress().biome.id)


## Falling confetti for the final victory screen.
class Confetti extends Node2D:
	var _bits: Array[Dictionary] = []

	func _ready() -> void:
		var colors := [Palette.GOLD, Palette.HEART, Palette.GOOD, Color("#6fb3e8"), Color("#b07aff")]
		for i in 90:
			_bits.append({"pos": Vector2(randf_range(0, 360), randf_range(-720, 0)),
				"speed": randf_range(60, 140), "drift": randf_range(-20, 20),
				"color": colors[i % colors.size()], "size": randf_range(2, 4)})

	func _process(delta: float) -> void:
		for bit in _bits:
			bit.pos += Vector2(bit.drift, bit.speed) * delta
			if bit.pos.y > 730:
				bit.pos.y = -10
		queue_redraw()

	func _draw() -> void:
		for bit in _bits:
			draw_rect(Rect2(bit.pos, Vector2(bit.size, bit.size)), bit.color)


# --- Layout -----------------------------------------------------------------

func _build_top_bar() -> void:
	_add_panel(Vector2.ZERO, Vector2(WIDTH, TOP_HEIGHT))
	_level_label = _make_label(Vector2(12, 8), Vector2(260, 20), FONT)
	var menu := _make_button("Menu", game.quit_to_menu)
	menu.position = Vector2(WIDTH - 72, 6)
	menu.custom_minimum_size = Vector2(60, 26)
	menu.add_theme_font_size_override("font_size", SMALL_FONT)
	_root.add_child(menu)
	_hp_label = _make_label(Vector2(12, 34), Vector2(110, 20), FONT)
	_wave_label = _make_label(Vector2(125, 34), Vector2(110, 20), FONT, HORIZONTAL_ALIGNMENT_CENTER)
	_atp_label = _make_label(Vector2(238, 34), Vector2(110, 20), FONT, HORIZONTAL_ALIGNMENT_RIGHT)
	_next_label = _make_label(Vector2(12, 57), Vector2(336, 20), SMALL_FONT)
	_level_label.modulate = _accent()
	_hp_label.modulate = Palette.HEART
	_atp_label.modulate = ATP_COLOR
	_next_label.modulate = Palette.TEXT_DIM


func _build_bottom_bar() -> void:
	_footnote_label = _make_label(Vector2(12, FOOTNOTE_TOP), Vector2(336, 46), 10, HORIZONTAL_ALIGNMENT_CENTER)
	_footnote_label.modulate = Palette.TEXT_DIM

	_add_panel(Vector2(0, BOTTOM_TOP), Vector2(WIDTH, 720 - BOTTOM_TOP), true)
	_message_label = _make_label(Vector2(12, BOTTOM_TOP + 2), Vector2(336, 24), SMALL_FONT)

	_unit_row = HBoxContainer.new()
	_unit_row.position = Vector2(12, BOTTOM_TOP + 26)
	_unit_row.add_theme_constant_override("separation", 4)
	_root.add_child(_unit_row)
	for type in game.unit_types:
		var button := Button.new()
		button.toggle_mode = true
		button.icon = type.texture
		button.expand_icon = true
		button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		button.custom_minimum_size = Vector2(52, 64)
		button.add_theme_font_size_override("font_size", 10)
		button.pressed.connect(game.select_type.bind(type))
		_unit_row.add_child(button)
		_unit_buttons[type] = button

	_selection_row = HBoxContainer.new()
	_selection_row.position = Vector2(12, BOTTOM_TOP + 26)
	_selection_row.add_theme_constant_override("separation", 4)
	_selection_row.visible = false
	_root.add_child(_selection_row)
	for i in 2:
		var button := _make_button("", func(): _on_evolve_pressed(i))
		button.custom_minimum_size = Vector2(124, 64)
		button.add_theme_font_size_override("font_size", 10)
		button.expand_icon = true
		button.add_theme_constant_override("icon_max_width", 20)
		button.clip_text = true
		button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_selection_row.add_child(button)
		_evolve_buttons.append(button)
	_sell_button = _make_button("Remove", game.sell_selected)
	_sell_button.custom_minimum_size = Vector2(80, 64)
	_sell_button.add_theme_font_size_override("font_size", SMALL_FONT)
	_selection_row.add_child(_sell_button)

	var control_row := HBoxContainer.new()
	control_row.position = Vector2(12, BOTTOM_TOP + 96)
	control_row.size = Vector2(336, 40)
	control_row.add_theme_constant_override("separation", 6)
	_root.add_child(control_row)
	_speed_button = _make_button("1x", game.cycle_speed)
	_start_button = _make_button("Start Wave", game.start_wave)
	_start_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for button in [_speed_button, _start_button]:
		button.custom_minimum_size.y = 40
		control_row.add_child(button)


func _on_evolve_pressed(index: int) -> void:
	var unit: Unit = game.selected_unit()
	if unit and index < unit.base_data.evolutions.size():
		game.evolve_selected(unit.base_data.evolutions[index])


## A bar across the screen with a thin accent line on the side facing the board.
func _add_panel(pos: Vector2, size: Vector2, line_on_top := false) -> void:
	var panel := Panel.new()
	var style := Palette.panel(Palette.SURFACE, Color.TRANSPARENT, 0)
	style.set_border_width_all(0)
	style.border_color = _accent().darkened(0.3)
	if line_on_top:
		style.border_width_top = 2
	else:
		style.border_width_bottom = 2
	panel.add_theme_stylebox_override("panel", style)
	panel.position = pos
	panel.size = size
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_root.add_child(panel)


func _make_label(pos: Vector2, size: Vector2, font_size: int, align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var label := Label.new()
	label.position = pos
	label.size = size
	label.horizontal_alignment = align
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(label)
	return label


func _make_button(text: String, action: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.add_theme_font_size_override("font_size", FONT)
	button.custom_minimum_size = Vector2(64, 40)
	button.pressed.connect(func(): Sfx.play("button"))
	button.pressed.connect(action)
	return button
