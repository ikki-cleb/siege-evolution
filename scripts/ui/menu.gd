extends Control
## The menus: title -> world select -> pack select -> level select, plus the
## Store. Colors and styles come from Look.

const GAME_SCENE := "res://scenes/game.tscn"
const BG_COLOR := Look.BG
const CARD_COLOR := Look.SURFACE
const DIM_TEXT := Look.TEXT_DIM
const GOLD := Look.GOLD

var _content: VBoxContainer
var _biome: BiomeData
## The screen being shown, so it can redraw itself after a purchase.
var _current_screen: Callable


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

	Store.purchases_changed.connect(func(): _show(_current_screen))
	Audio.play_music("menu")
	_biome = Progress.biome
	match Progress.return_screen:
		"levels":
			_show(_show_levels)
		"biomes":
			_show(_show_biomes)
		"store":
			_show(_show_store)
		_:
			_show(_show_title)


func _show(screen: Callable) -> void:
	_current_screen = screen
	_clear()
	screen.call()


# --- Screens ----------------------------------------------------------------

func _show_title() -> void:
	_spacer(120)
	_label("SIEGE", 54, Look.TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	var evolution := _label("EVOLUTION", 30, Look.HEART, HORIZONTAL_ALIGNMENT_CENTER)
	# The subtitle color cycles through every world's accent.
	var tween := evolution.create_tween().set_loops()
	for color in Look.ACCENTS.values():
		tween.tween_property(evolution, "modulate", color, 0.4)
		tween.tween_interval(1.4)
	_label("From a single cell to the stars.", 14, DIM_TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	_spacer(36)
	var play := _button("Play", _show.bind(_show_biomes))
	play.custom_minimum_size.y = 56
	play.add_theme_font_size_override("font_size", 20)
	_button("Store", _show.bind(_show_store))
	var toggles := HBoxContainer.new()
	toggles.add_theme_constant_override("separation", 8)
	_content.add_child(toggles)
	var sound := _button("Sound: %s" % ("On" if Audio.sound_on else "Off"), func():
		Audio.set_sound(not Audio.sound_on)
		_show(_show_title), toggles)
	var music := _button("Music: %s" % ("On" if Audio.music_on else "Off"), func():
		Audio.set_music(not Audio.music_on)
		_show(_show_title), toggles)
	for button in [sound, music]:
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_spacer(80)
	_label("Font: Pixelify Sans (SIL Open Font License)", 10, Color(Look.TEXT_DIM, 0.6), HORIZONTAL_ALIGNMENT_CENTER)


func _show_biomes() -> void:
	_header("Choose a World", _show.bind(_show_title))
	_label("Each world is bigger than the last. Beat a world's boss to unlock the next one.", 12, DIM_TEXT)
	for index in Progress.WORLDS.size():
		if index == 5:
			_label("Bonus Worlds", 18, GOLD)
		_world_card(index)


func _world_card(index: int) -> void:
	var world: Dictionary = Progress.WORLDS[index]
	var world_biome := Progress.load_biome(index)
	var edge := Look.accent(world_biome.id) if world_biome else Look.BORDER
	var card := _card(CARD_COLOR, edge)
	var title: String = world.name
	if not Progress.is_bonus(index):
		title = "World %d: %s" % [Progress.main_number(index), world.name]
	_label(title, 18, Color.WHITE, HORIZONTAL_ALIGNMENT_LEFT, card)
	_label(world.theme, 12, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)

	var unlocked := Progress.is_biome_unlocked(index)
	if Progress.is_bonus(index) and not unlocked:
		var product: String = world.product
		# Warn before buying here too, not just in the Store.
		_warning(Store.product(product), card)
		_button("Unlock for %s" % Store.price(product), Store.buy.bind(product), card)
		return
	if not Progress.has_content(index):
		_label("Coming soon" + (" (owned)" if Progress.is_bonus(index) else ""), 12, GOLD,
			HORIZONTAL_ALIGNMENT_LEFT, card)
		return
	var biome := Progress.load_biome(index)
	var pack := biome.find_pack(Progress.run_pack(biome.id))
	if pack:
		_label("%d/%d cleared with %s" % [Progress.cleared(biome.id), biome.levels.size(), pack.display_name],
			12, GOLD, HORIZONTAL_ALIGNMENT_LEFT, card)
	var enter := _button("Enter" if unlocked else "Locked: beat World %d first" % index,
		_open_biome.bind(index), card)
	enter.disabled = not unlocked


func _open_biome(index: int) -> void:
	_biome = Progress.load_biome(index)
	_show(_show_packs)


func _show_packs() -> void:
	_header(_biome.display_name, _show.bind(_show_biomes))
	var current := _biome.find_pack(Progress.run_pack(_biome.id))
	if current and Store.owns(current.product_id):
		_button("Continue with %s (%d/%d cleared)" % [current.display_name,
			Progress.cleared(_biome.id), _biome.levels.size()], _pick_pack.bind(current))
	_label("Pick a starter pack. You keep it for all %d levels of this world, and it gains a new unit as you progress." % _biome.levels.size(),
		12, DIM_TEXT)
	for pack in _biome.packs:
		var card := _card(CARD_COLOR, pack.color)
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
			icons.add_child(icon)
		var names := ", ".join(pack.units_for_level(1).map(func(u): return u.display_name))
		_label("Starts with: " + names, 11, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		if not Store.owns(pack.product_id):
			_button("Unlock %s · %s (all worlds)" % [pack.display_name, Store.price(pack.product_id)],
				Store.buy.bind(pack.product_id), card)
		elif pack != current:
			_button("Choose %s" % pack.display_name, _confirm_pack.bind(pack), card)


func _confirm_pack(pack: PackData) -> void:
	var current := _biome.find_pack(Progress.run_pack(_biome.id))
	if current == null or Progress.cleared(_biome.id) == 0:
		_pick_pack(pack)
		return
	_clear()
	_header("Switch packs?", _show.bind(_show_packs))
	_label("Starting %s with %s restarts this world from level 1. Your %s run (%d/%d cleared) will be lost." % [
		_biome.display_name, pack.display_name, current.display_name,
		Progress.cleared(_biome.id), _biome.levels.size()], 14, Color.WHITE)
	_button("Restart with %s" % pack.display_name, _pick_pack.bind(pack))
	_button("Keep %s" % current.display_name, _show.bind(_show_packs))


func _pick_pack(pack: PackData) -> void:
	Progress.choose_pack(_biome, pack)
	_show(_show_levels)


func _show_levels() -> void:
	_biome = Progress.biome
	_header("%s · %s" % [_biome.display_name, Progress.pack.display_name], _show.bind(_show_packs))
	var cleared := Progress.cleared(_biome.id)
	for i in _biome.levels.size():
		var text := _biome.levels[i].display_name
		if i < cleared:
			text += " · cleared"
		elif i > cleared:
			text += " · locked"
		var unlock := Progress.pack.unit_unlocked_on(i + 1)
		if unlock:
			text += "\nNew unit: %s" % unlock.display_name
		var button := _button(text, _play_level.bind(i))
		button.disabled = i > cleared
		button.custom_minimum_size.y = 56


func _play_level(index: int) -> void:
	Progress.level_index = index
	get_tree().change_scene_to_file(GAME_SCENE)


func _show_store() -> void:
	_header("Store", _show.bind(_show_title))
	_label("Siege Evolution is free with no ads. These optional extras support development.", 12, DIM_TEXT)
	if Store.test_mode:
		_label("TEST MODE: purchases are free and instant in this build.", 12, GOLD)
	for item in Store.PRODUCTS:
		var is_bundle: bool = item.id == Store.BUNDLE_ALL
		var card := _card(Color(0.3, 0.22, 0.08) if is_bundle else CARD_COLOR)
		_label(item.name, 18, GOLD if is_bundle else Color.WHITE, HORIZONTAL_ALIGNMENT_LEFT, card)
		_warning(item, card)
		_label(item.description, 12, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		if Store.owns(item.id):
			_label("Owned", 14, Color(0.5, 1, 0.6), HORIZONTAL_ALIGNMENT_LEFT, card)
		else:
			var buy := _button("Buy · %s" % item.price, Store.buy.bind(item.id), card)
			buy.disabled = not Store.is_available()
	_button("Restore Purchases", Store.restore_purchases)
	if Store.test_mode:
		_button("Reset test purchases", Store.reset_test_purchases)
		_button("Test: unlock all worlds", func():
			Progress.unlock_all_for_testing()
			_show(_show_store))


# --- Building blocks --------------------------------------------------------

## A red "POST-GAME: HARD" tag plus one line, for store items that have a
## "warning" (the bonus worlds). Does nothing for other items.
func _warning(item: Dictionary, card: Control) -> void:
	if not item.has("warning"):
		return
	_label(item.warning, 13, Palette.WARNING, HORIZONTAL_ALIGNMENT_LEFT, card)
	_label(item.warning_detail, 12, Palette.WARNING.lightened(0.35), HORIZONTAL_ALIGNMENT_LEFT, card)


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


## A rounded card; `edge` adds a colored stripe down its left side.
func _card(color := CARD_COLOR, edge := Color.TRANSPARENT) -> VBoxContainer:
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", Look.panel(color, edge))
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
	button.pressed.connect(func(): Audio.play("button"))
	button.pressed.connect(action)
	(parent if parent else _content).add_child(button)
	return button


func _spacer(height: float) -> void:
	var spacer := Control.new()
	spacer.custom_minimum_size.y = height
	_content.add_child(spacer)
