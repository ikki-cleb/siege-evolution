class_name Hud
extends CanvasLayer
## The on-screen interface: status at the top, unit bar and buttons at the
## bottom, and the win/lose screen. Prototype styling only; the sleek menu
## design comes later.

const TOP_HEIGHT := 88
const BOTTOM_TOP := 552
const SMALL_FONT := 12
const FONT := 14

var game  # The Game node (game.gd)

var _level_label: Label
var _wave_label: Label
var _hp_label: Label
var _atp_label: Label
var _next_label: Label
var _message_label: Label
var _unit_buttons := {}  # UnitData -> Button
var _undo_button: Button
var _sell_button: Button
var _speed_button: Button
var _start_button: Button


func setup(p_game) -> void:
	game = p_game
	_build_top_bar()
	_build_bottom_bar()


func refresh() -> void:
	_level_label.text = game.level.display_name
	_wave_label.text = "Wave %d/%d" % [game.wave_number, game.level.waves.size()]
	_hp_label.text = "Base HP %d/%d" % [game.base_hp, game.level.base_hp]
	_atp_label.text = "ATP %d" % game.atp
	_next_label.text = game.next_wave_summary()

	var building: bool = game.phase == game.Phase.BUILD
	for type in _unit_buttons:
		var button: Button = _unit_buttons[type]
		var free_left: int = game.hand.get(type.id, 0)
		if free_left > 0:
			button.text = "x%d" % free_left
		elif game.level.shop.has(type):
			button.text = "%d ATP" % type.cost
		else:
			button.text = "-"
		button.disabled = not building
		button.set_pressed_no_signal(game.selected_type == type)

	_undo_button.disabled = not game.can_undo()
	_sell_button.disabled = not game.can_sell()
	_speed_button.text = "%dx" % game.speed
	_start_button.disabled = not building
	_start_button.text = "Start Wave" if building else "Wave %d..." % game.wave_number


func show_message(text: String) -> void:
	_message_label.text = text


func show_end_screen(won: bool, can_continue: bool) -> void:
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.7)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	box.grow_vertical = Control.GROW_DIRECTION_BOTH
	box.add_theme_constant_override("separation", 12)
	dim.add_child(box)

	var title := Label.new()
	title.text = "Level Cleared!" if won else "Infection Spread..."
	title.add_theme_font_size_override("font_size", 28)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)

	if can_continue:
		box.add_child(_make_button("Next Level", game.next_level))
	box.add_child(_make_button("Play Again" if won else "Retry", game.retry))


# --- Layout -----------------------------------------------------------------

func _build_top_bar() -> void:
	var panel := ColorRect.new()
	panel.color = Color(0.09, 0.05, 0.08)
	panel.position = Vector2.ZERO
	panel.size = Vector2(360, TOP_HEIGHT)
	add_child(panel)

	_level_label = _make_label(Vector2(12, 8), FONT)
	_wave_label = _make_label(Vector2(240, 8), FONT, HORIZONTAL_ALIGNMENT_RIGHT)
	_hp_label = _make_label(Vector2(12, 32), FONT)
	_atp_label = _make_label(Vector2(240, 32), FONT, HORIZONTAL_ALIGNMENT_RIGHT)
	_next_label = _make_label(Vector2(12, 58), SMALL_FONT)
	_next_label.size.x = 336
	_next_label.modulate = Color(1, 0.8, 0.8)
	_hp_label.modulate = Color(1, 0.55, 0.6)
	_atp_label.modulate = Color(1, 0.9, 0.4)


func _build_bottom_bar() -> void:
	var panel := ColorRect.new()
	panel.color = Color(0.09, 0.05, 0.08)
	panel.position = Vector2(0, BOTTOM_TOP)
	panel.size = Vector2(360, 720 - BOTTOM_TOP)
	add_child(panel)

	_message_label = _make_label(Vector2(12, BOTTOM_TOP + 4), SMALL_FONT)
	_message_label.size.x = 336

	var unit_row := HBoxContainer.new()
	unit_row.position = Vector2(12, BOTTOM_TOP + 26)
	unit_row.add_theme_constant_override("separation", 6)
	add_child(unit_row)
	for type in game.unit_types:
		var button := Button.new()
		button.toggle_mode = true
		button.icon = type.texture
		button.expand_icon = true
		button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		button.custom_minimum_size = Vector2(60, 72)
		button.add_theme_font_size_override("font_size", SMALL_FONT)
		button.tooltip_text = type.display_name
		button.pressed.connect(game.select_type.bind(type))
		unit_row.add_child(button)
		_unit_buttons[type] = button

	var control_row := HBoxContainer.new()
	control_row.position = Vector2(12, BOTTOM_TOP + 108)
	control_row.size = Vector2(336, 48)
	control_row.add_theme_constant_override("separation", 6)
	add_child(control_row)
	_undo_button = _make_button("Undo", game.undo)
	_sell_button = _make_button("Sell 75%", game.sell_selected)
	_speed_button = _make_button("1x", game.cycle_speed)
	_start_button = _make_button("Start Wave", game.start_wave)
	_start_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for button in [_undo_button, _sell_button, _speed_button, _start_button]:
		button.custom_minimum_size.y = 48
		control_row.add_child(button)


func _make_label(pos: Vector2, font_size: int, align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var label := Label.new()
	label.position = pos
	label.size = Vector2(108 if align == HORIZONTAL_ALIGNMENT_RIGHT else 220, 20)
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
