class_name Hud
extends CanvasLayer
## The in-level interface: status at the top, a footnote under the board,
## and the unit bar and buttons at the bottom. Tapping a placed unit swaps the
## unit bar for its evolve/remove options. Prototype styling only; the sleek
## design comes later.

const WIDTH := 360
const TOP_HEIGHT := 80
const FOOTNOTE_TOP := 531
const BOTTOM_TOP := 578
const SMALL_FONT := 11
const FONT := 14
const PANEL_COLOR := Color(0.09, 0.05, 0.08)

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


func setup(p_game) -> void:
	game = p_game
	_build_top_bar()
	_build_bottom_bar()


func refresh() -> void:
	_level_label.text = "%s · %s" % [game.level.display_name, game.pack.display_name]
	_wave_label.text = "Wave %d/%d" % [game.wave_number, game.level.waves.size()]
	_hp_label.text = "Base %d/%d" % [game.base_hp, game.level.base_hp]
	_atp_label.text = "ATP %d" % game.atp
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


func show_end_screen(won: bool) -> void:
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.75)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	box.grow_vertical = Control.GROW_DIRECTION_BOTH
	box.add_theme_constant_override("separation", 12)
	dim.add_child(box)

	var title := Label.new()
	if won and game.is_last_level():
		title.text = "Biome Cleared!"
	else:
		title.text = "Level Cleared!" if won else "Infection Spread..."
	title.add_theme_font_size_override("font_size", 28)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)

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


# --- Layout -----------------------------------------------------------------

func _build_top_bar() -> void:
	_add_panel(Vector2.ZERO, Vector2(WIDTH, TOP_HEIGHT))
	_level_label = _make_label(Vector2(12, 8), Vector2(260, 20), FONT)
	var menu := _make_button("Menu", game.quit_to_menu)
	menu.position = Vector2(WIDTH - 72, 6)
	menu.custom_minimum_size = Vector2(60, 26)
	menu.add_theme_font_size_override("font_size", SMALL_FONT)
	add_child(menu)
	_hp_label = _make_label(Vector2(12, 34), Vector2(110, 20), FONT)
	_wave_label = _make_label(Vector2(125, 34), Vector2(110, 20), FONT, HORIZONTAL_ALIGNMENT_CENTER)
	_atp_label = _make_label(Vector2(238, 34), Vector2(110, 20), FONT, HORIZONTAL_ALIGNMENT_RIGHT)
	_next_label = _make_label(Vector2(12, 57), Vector2(336, 20), SMALL_FONT)
	_hp_label.modulate = Color(1, 0.55, 0.6)
	_atp_label.modulate = Color(1, 0.9, 0.4)
	_next_label.modulate = Color(1, 0.8, 0.8)


func _build_bottom_bar() -> void:
	_footnote_label = _make_label(Vector2(12, FOOTNOTE_TOP), Vector2(336, 46), 10, HORIZONTAL_ALIGNMENT_CENTER)
	_footnote_label.modulate = Color(0.85, 0.75, 0.8)

	_add_panel(Vector2(0, BOTTOM_TOP), Vector2(WIDTH, 720 - BOTTOM_TOP))
	_message_label = _make_label(Vector2(12, BOTTOM_TOP + 2), Vector2(336, 24), SMALL_FONT)

	_unit_row = HBoxContainer.new()
	_unit_row.position = Vector2(12, BOTTOM_TOP + 26)
	_unit_row.add_theme_constant_override("separation", 4)
	add_child(_unit_row)
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
	add_child(_selection_row)
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
	add_child(control_row)
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


func _add_panel(pos: Vector2, size: Vector2) -> void:
	var panel := ColorRect.new()
	panel.color = PANEL_COLOR
	panel.position = pos
	panel.size = size
	add_child(panel)


func _make_label(pos: Vector2, size: Vector2, font_size: int, align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var label := Label.new()
	label.position = pos
	label.size = size
	label.horizontal_alignment = align
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)
	return label


func _make_button(text: String, action: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.add_theme_font_size_override("font_size", FONT)
	button.custom_minimum_size = Vector2(64, 40)
	button.pressed.connect(action)
	return button
