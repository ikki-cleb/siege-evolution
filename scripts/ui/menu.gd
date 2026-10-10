extends Control
## The menus: title -> biome (world) select -> pack select -> level select.
## Plain functional layout for now; the sleek menu design comes later.

const GAME_SCENE := "res://scenes/game.tscn"
const BG_COLOR := Color(0.09, 0.05, 0.08)
const CARD_COLOR := Color(0.16, 0.09, 0.13)
const DIM_TEXT := Color(0.8, 0.68, 0.74)

var _content: VBoxContainer
var _biome_index := 0
var _biome: BiomeData


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = BG_COLOR
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_preset(Control.PRESET_FULL_RECT)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	add_child(scroll)
	var margin := MarginContainer.new()
	margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 20)
	scroll.add_child(margin)
	_content = VBoxContainer.new()
	_content.add_theme_constant_override("separation", 12)
	margin.add_child(_content)

	if Progress.biome:
		_biome = Progress.biome
		_biome_index = max(0, Progress.BIOMES.find(_biome.resource_path))
	match Progress.return_screen:
		"levels":
			_show_levels()
		"biomes":
			_show_biomes()
		_:
			_show_title()


# --- Screens ----------------------------------------------------------------

func _show_title() -> void:
	_clear()
	_spacer(160)
	_label("SIEGE EVOLUTION", 34, Color(1, 0.35, 0.45), HORIZONTAL_ALIGNMENT_CENTER)
	_label("A microscopic puzzle defense", 14, DIM_TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	_spacer(40)
	_button("Play", _show_biomes)


func _show_biomes() -> void:
	_clear()
	_header("Choose a World", _show_title)
	for i in Progress.BIOMES.size():
		var biome := Progress.load_biome(i)
		var unlocked := Progress.is_biome_unlocked(i)
		var cleared := Progress.cleared(biome.id)
		var pack := biome.find_pack(Progress.run_pack(biome.id))
		var status := "Not started"
		if pack:
			status = "%d/%d cleared with %s" % [cleared, biome.levels.size(), pack.display_name]
		var card := _card()
		_label("World %d: %s" % [i + 1, biome.display_name], 18, Color.WHITE, HORIZONTAL_ALIGNMENT_LEFT, card)
		_label(biome.description, 12, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		_label(status, 12, Color(1, 0.9, 0.4), HORIZONTAL_ALIGNMENT_LEFT, card)
		var open := _button("Enter" if unlocked else "Locked", _open_biome.bind(i), card)
		open.disabled = not unlocked
	var next := _card()
	_label("World %d: ???" % (Progress.BIOMES.size() + 1), 18, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, next)
	_label("Beat the last world's boss to zoom out to a bigger scale. Coming soon.", 12, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, next)


func _open_biome(index: int) -> void:
	_biome_index = index
	_biome = Progress.load_biome(index)
	_show_packs()


func _show_packs() -> void:
	_clear()
	_header(_biome.display_name, _show_biomes)
	var current := _biome.find_pack(Progress.run_pack(_biome.id))
	if current:
		var cleared := Progress.cleared(_biome.id)
		_button("Continue with %s (%d/%d cleared)" % [current.display_name, cleared, _biome.levels.size()],
			_pick_pack.bind(current))
	_label("Pick a starter pack. You keep it for all %d levels of this world, and it gains a new unit as you progress." % _biome.levels.size(),
		12, DIM_TEXT)
	for pack in _biome.packs:
		var card := _card(pack.color.darkened(0.75))
		_label(pack.display_name, 18, pack.color.lightened(0.3), HORIZONTAL_ALIGNMENT_LEFT, card)
		_label(pack.description, 12, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		var icons := HBoxContainer.new()
		icons.add_theme_constant_override("separation", 6)
		card.add_child(icons)
		for unit in pack.units_for_level(1):
			var icon := TextureRect.new()
			icon.texture = unit.texture
			icon.custom_minimum_size = Vector2(32, 32)
			icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			icon.tooltip_text = unit.display_name
			icons.add_child(icon)
		var names := ", ".join(pack.units_for_level(1).map(func(u): return u.display_name))
		_label("Starts with: " + names, 11, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		if pack != current:
			_button("Choose %s" % pack.display_name, _confirm_pack.bind(pack), card)


func _confirm_pack(pack: PackData) -> void:
	var current := _biome.find_pack(Progress.run_pack(_biome.id))
	if current == null or Progress.cleared(_biome.id) == 0:
		_pick_pack(pack)
		return
	_clear()
	_header("Switch packs?", _show_packs)
	_label("Starting %s with %s restarts this world from level 1. Your %s run (%d/%d cleared) will be lost." % [
		_biome.display_name, pack.display_name, current.display_name,
		Progress.cleared(_biome.id), _biome.levels.size()], 14, Color.WHITE)
	_button("Restart with %s" % pack.display_name, _pick_pack.bind(pack))
	_button("Keep %s" % current.display_name, _show_packs)


func _pick_pack(pack: PackData) -> void:
	Progress.choose_pack(_biome, pack)
	_show_levels()


func _show_levels() -> void:
	_clear()
	_biome = Progress.biome
	_header("%s · %s" % [_biome.display_name, Progress.pack.display_name], _show_packs)
	var cleared := Progress.cleared(_biome.id)
	for i in _biome.levels.size():
		var level := _biome.levels[i]
		var text := level.display_name
		if i < cleared:
			text += "   ✓ cleared"
		elif i > cleared:
			text += "   locked"
		var unlock := Progress.pack.unit_unlocked_on(i + 1)
		if unlock:
			text += "\nNew unit: %s" % unlock.display_name
		var button := _button(text, _play_level.bind(i))
		button.disabled = i > cleared
		button.custom_minimum_size.y = 56


func _play_level(index: int) -> void:
	Progress.level_index = index
	get_tree().change_scene_to_file(GAME_SCENE)


# --- Building blocks --------------------------------------------------------

func _clear() -> void:
	for child in _content.get_children():
		child.queue_free()


func _header(title: String, back: Callable) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	_content.add_child(row)
	var back_button := Button.new()
	back_button.text = "Back"
	back_button.custom_minimum_size = Vector2(64, 36)
	back_button.pressed.connect(back)
	row.add_child(back_button)
	var label := _label(title, 20, Color.WHITE, HORIZONTAL_ALIGNMENT_LEFT, row)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL


func _card(color := CARD_COLOR) -> VBoxContainer:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(6)
	style.set_content_margin_all(12)
	panel.add_theme_stylebox_override("panel", style)
	_content.add_child(panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)
	return box


func _label(text: String, font_size: int, color := Color.WHITE,
		align := HORIZONTAL_ALIGNMENT_LEFT, parent: Control = null) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = align
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	label.modulate = color
	label.custom_minimum_size.x = 100
	(parent if parent else _content).add_child(label)
	return label


func _button(text: String, action: Callable, parent: Control = null) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(0, 44)
	button.add_theme_font_size_override("font_size", 14)
	button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	button.pressed.connect(action)
	(parent if parent else _content).add_child(button)
	return button


func _spacer(height: float) -> void:
	var spacer := Control.new()
	spacer.custom_minimum_size.y = height
	_content.add_child(spacer)
