extends Control
## The menus: title -> world select -> pack select -> level select, plus the
## Store. Colors and styles come from Look.

const GAME_SCENE := "res://scenes/game.tscn"
const BG_COLOR := Look.BG
const CARD_COLOR := Look.SURFACE
const DIM_TEXT := Look.TEXT_DIM
const GOLD := Look.GOLD

var _content: VBoxContainer
var _scroll: ScrollContainer
var _biome: BiomeData
## Drag-to-scroll: a press that moves further than this is a scroll, not a tap.
const DRAG_THRESHOLD := 10.0
var _press_position := Vector2.ZERO
var _pressing := false
var _dragged := false
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
	scroll.scroll_deadzone = int(DRAG_THRESHOLD)
	add_child(scroll)
	_scroll = scroll
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
	_let_drags_through(_content)


## Cards and buttons normally swallow a finger press, so only the screen's
## edges could scroll. Passing presses on lets a drag anywhere scroll the list.
func _let_drags_through(node: Node) -> void:
	for child in node.get_children():
		if child is Control and not child is Label:
			child.mouse_filter = Control.MOUSE_FILTER_PASS
		_let_drags_through(child)


## Tells taps from drags. Phones scroll the list on their own once presses
## pass through; with a mouse (desktop browsers) we scroll it here.
func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		_pressing = event.pressed
		if event.pressed:
			_press_position = event.position
			_dragged = false
	elif event is InputEventMouseMotion and _pressing:
		if event.position.distance_to(_press_position) > DRAG_THRESHOLD:
			_dragged = true
		if _dragged and not DisplayServer.is_touchscreen_available():
			_scroll.scroll_vertical -= int(event.relative.y)


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
	_label("From the backyard to the stars.", 14, DIM_TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	_spacer(36)
	var play := _button("Play", _show.bind(_show_biomes))
	play.custom_minimum_size.y = 56
	play.add_theme_font_size_override("font_size", 20)
	_button("Store", _show.bind(_show_store))
	_button("Achievements (%d/%d)" % [Achievements.earned_count(), Achievements.list.size()],
		_show.bind(_show_achievements))
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
	_label("Fonts: Coiny and Space Mono (SIL Open Font License)", 10, Color(Look.TEXT_DIM, 0.6), HORIZONTAL_ALIGNMENT_CENTER)


func _show_biomes() -> void:
	_header("Choose a World", _show.bind(_show_title))
	_label("Each world brings new invaders. Beat a world's boss to unlock the next one.", 12, DIM_TEXT)
	for index in Progress.WORLDS.size():
		if index == 5:
			_label("Bonus Worlds", 18, GOLD)
		_world_card(index)


func _world_card(index: int) -> void:
	var world: Dictionary = Progress.WORLDS[index]
	var edge := Look.accent(Progress.world_id(index)) if Progress.has_content(index) else Look.BORDER
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
	var id := Progress.world_id(index)
	if Progress.cleared(id) > 0:
		_label("%d/%d levels cleared" % [Progress.cleared(id), Progress.LEVELS_PER_BIOME],
			12, GOLD, HORIZONTAL_ALIGNMENT_LEFT, card)
	# One symbol per pack, filling up as that pack beats this world's levels.
	if unlocked:
		var symbols := _symbol_row(card)
		for pack_id in PackSymbol.ORDER:
			var beaten := Progress.levels_beaten_by(id, pack_id)
			symbols.add_child(PackSymbol.new().setup(pack_id, float(beaten) / Progress.LEVELS_PER_BIOME, 26))
	var enter := _button("Enter" if unlocked else "Locked: beat World %d first" % index,
		_open_biome.bind(index), card)
	enter.disabled = not unlocked


## Enters a world with the pack picked there last time (or the first pack).
func _open_biome(index: int) -> void:
	var biome := Progress.load_biome(index)
	var pack := biome.find_pack(Progress.run_pack(biome.id))
	if pack == null or not Store.owns(pack.product_id):
		pack = biome.packs[0]
	Progress.choose_pack(biome, pack)
	_show(_show_levels)


## Picks a different pack. Nothing is lost: world progress is shared.
func _pick_pack(pack: PackData) -> void:
	Progress.choose_pack(Progress.biome, pack)
	_show(_show_levels)


## The level list, with the pack picker at the top. Each level shows which
## packs have beaten it (for pack mastery).
func _show_levels() -> void:
	_biome = Progress.biome
	var current: PackData = Progress.pack
	_header(_biome.display_name, _show.bind(_show_biomes))
	_label("Pack (swap any time, progress is shared):", 12, DIM_TEXT)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 4)
	_content.add_child(row)
	for pack in _biome.packs:
		var owned := Store.owns(pack.product_id)
		var button := _button(pack.display_name if owned else "%s\n%s" % [pack.display_name, Store.price(pack.product_id)],
			_pick_pack.bind(pack) if owned else Store.buy.bind(pack.product_id), row)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.custom_minimum_size = Vector2(0, 58)
		button.add_theme_font_size_override("font_size", 11)
		# The pack's symbol above its name.
		button.icon = load(PackSymbol.ART_DIR + pack.id + ".png")
		button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		button.add_theme_constant_override("icon_max_width", 20)
		button.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		button.autowrap_mode = TextServer.AUTOWRAP_OFF  # never split a name
		button.add_theme_font_size_override("font_size", 10)
		button.modulate = pack.color.lightened(0.45) if pack == current else Color(1, 1, 1, 0.75)
		if pack == current:
			button.add_theme_stylebox_override("normal", Look.panel(Look.SURFACE_HI, pack.color))
	var card := _card(CARD_COLOR, current.color)
	_label(current.display_name, 16, current.color.lightened(0.3), HORIZONTAL_ALIGNMENT_LEFT, card)
	_label(current.description, 12, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
	_label("Mastery: %d/%d main-world levels beaten with %s" % [Progress.main_levels_beaten(current.id),
		Progress.main_level_count(), current.display_name], 11, GOLD, HORIZONTAL_ALIGNMENT_LEFT, card)

	var cleared := Progress.cleared(_biome.id)
	for i in _biome.levels.size():
		var text := _biome.levels[i].display_name
		if i > cleared:
			text += " · locked"
		var unlock := current.unit_unlocked_on(i + 1)
		if unlock:
			text += "\nNew unit: %s" % unlock.display_name
		var button := _button("", _play_level.bind(i))
		button.disabled = i > cleared
		# Inside the button: the level's text, then its 5 pack symbols,
		# filled for each pack that has beaten this level.
		var inside := VBoxContainer.new()
		inside.mouse_filter = Control.MOUSE_FILTER_IGNORE
		inside.alignment = BoxContainer.ALIGNMENT_CENTER
		inside.add_theme_constant_override("separation", 4)
		button.add_child(inside)
		inside.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_KEEP_SIZE, 6)
		var title := _label(text, 14, Look.TEXT, HORIZONTAL_ALIGNMENT_CENTER, inside)
		title.mouse_filter = Control.MOUSE_FILTER_IGNORE
		title.theme_type_variation = "TitleLabel"  # same font as button text
		var beaten_by := Progress.packs_that_beat(_biome.id, i)
		var symbols := HBoxContainer.new()
		symbols.alignment = BoxContainer.ALIGNMENT_CENTER
		symbols.add_theme_constant_override("separation", 6)
		symbols.mouse_filter = Control.MOUSE_FILTER_IGNORE
		inside.add_child(symbols)
		for pack_id in PackSymbol.ORDER:
			symbols.add_child(PackSymbol.new().setup(pack_id, 1.0 if beaten_by.has(pack_id) else 0.0, 20))
		button.custom_minimum_size.y = 84 if unlock else 66
		inside.modulate.a = 0.45 if button.disabled else 1.0


func _play_level(index: int) -> void:
	Progress.level_index = index
	get_tree().change_scene_to_file(GAME_SCENE)


## Every achievement: earned ones in gold, locked ones dimmed with progress.
func _show_achievements() -> void:
	_header("Achievements", _show.bind(_show_title))
	_label("%d of %d earned" % [Achievements.earned_count(), Achievements.list.size()], 13, GOLD)
	var group := ""
	for item in Achievements.list:
		if item.group != group:
			group = item.group
			_label(group, 16, Look.TEXT)
		var done := Achievements.is_earned(item.id)
		var card := _card(Color(0.3, 0.22, 0.08) if done else CARD_COLOR, GOLD if done else Color.TRANSPARENT)
		_label(("★ " if done else "") + item.name, 15, GOLD if done else Look.TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		_label(item.desc, 11, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)
		var amounts: Array = Achievements.progress_of(item)
		if not done and amounts[1] > 1:
			_label("%s / %s" % [_count(amounts[0]), _count(amounts[1])], 11, Look.TEXT, HORIZONTAL_ALIGNMENT_LEFT, card)


## 12345 -> "12,345"
func _count(value: int) -> String:
	var text := str(value)
	var result := ""
	for i in text.length():
		if i > 0 and (text.length() - i) % 3 == 0:
			result += ","
		result += text[i]
	return result


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
	back_button.pressed.connect(func():
		if not _dragged:
			back.call())
	row.add_child(back_button)
	var label := _label(title, 20, Color.WHITE, HORIZONTAL_ALIGNMENT_LEFT, row)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL


## A rounded card; `edge` adds a colored stripe down its left side.
## A row for pack symbols inside a card.
func _symbol_row(parent: Control) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	parent.add_child(row)
	return row


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
	if font_size >= Look.TITLE_SIZE:
		label.theme_type_variation = "TitleLabel"  # big text uses the title font
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
	# A press that turned into a scroll doesn't count as a tap.
	button.pressed.connect(func():
		if _dragged:
			return
		Audio.play("button")
		action.call())
	(parent if parent else _content).add_child(button)
	return button


func _spacer(height: float) -> void:
	var spacer := Control.new()
	spacer.custom_minimum_size.y = height
	_content.add_child(spacer)
