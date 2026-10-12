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
## The title screen's drifting world-map backdrop (hidden on other screens).
var _stripes: WorldStripes
## True while a Back button is changing screens (the new one slides in
## from the left instead of the right).
var _going_back := false
## How far and how long a new screen slides in.
const SLIDE_DISTANCE := 120.0
const SLIDE_TIME := 0.22
const GRAYSCALE := preload("res://shaders/grayscale.gdshader")
## Boss/invader strips per world for the postcards (loaded once).
var _cards_cache := {}


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = BG_COLOR
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_stripes = WorldStripes.new().setup(_stripe_slices(), BG_COLOR)
	_stripes.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_stripes)

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
	var same_screen := _current_screen == screen
	_current_screen = screen
	_clear()
	_stripes.visible = screen == _show_title
	screen.call()
	_let_drags_through(_content)
	# Slide the new screen in: from the right going deeper, from the left
	# going back. (Redrawing the same screen, e.g. after a toggle, doesn't slide.)
	if not same_screen:
		_scroll.scroll_vertical = 0
		_scroll.position.x = -SLIDE_DISTANCE if _going_back else SLIDE_DISTANCE
		_scroll.modulate.a = 0.0
		var tween := create_tween().set_parallel().set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		tween.tween_property(_scroll, "position:x", 0.0, SLIDE_TIME)
		tween.tween_property(_scroll, "modulate:a", 1.0, SLIDE_TIME * 0.8)
	_going_back = false


## Cards and buttons normally swallow a finger press, so only the screen's
## edges could scroll. Passing presses on lets a drag anywhere scroll the list.
func _let_drags_through(node: Node) -> void:
	for child in node.get_children():
		# Sliders keep their presses (dragging one shouldn't scroll the list).
		if child is Control and not child is Label and not child is Range:
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

## Title: the logo over drifting world maps, a unit evolving in the middle
## (random units from unlocked worlds), then the buttons.
func _show_title() -> void:
	_spacer(24)
	_logo_label("SIEGE", 58, Look.TEXT)
	var evolution := _logo_label("EVOLUTION", 30, Look.HEART)
	# The subtitle color cycles through every world's accent.
	var tween := evolution.create_tween().set_loops()
	for color in Look.ACCENTS.values():
		tween.tween_property(evolution, "modulate", color, 0.4)
		tween.tween_interval(1.4)
	var tagline := _label("From the backyard to the stars.", 13, Look.TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	tagline.add_theme_color_override("font_outline_color", BG_COLOR)
	tagline.add_theme_constant_override("outline_size", 6)
	_content.add_child(EvolutionShowcase.new().setup(_showcase_pool()))
	var play := _button("Play", _show.bind(_show_biomes))
	play.custom_minimum_size = Vector2(0, 62)
	play.add_theme_font_size_override("font_size", 24)
	_juice(play, Look.HEART, Color("#8a1f36"), Color.WHITE, 7)
	for button in [
		_button("Store", _show.bind(_show_store)),
		_button("Achievements  %d/%d" % [Achievements.earned_count(), Achievements.list.size()],
			_show.bind(_show_achievements)),
		_button("Settings", _show.bind(_show_settings))]:
		button.custom_minimum_size.y = 42
	_spacer(30)
	_label("Fonts: Coiny and Space Mono (SIL Open Font License)", 10, Color(Look.TEXT_DIM, 0.6), HORIZONTAL_ALIGNMENT_CENTER)


## A big logo word with a dark outline and a drop shadow.
func _logo_label(text: String, font_size: int, color: Color) -> Label:
	var label := _label(text, font_size, color, HORIZONTAL_ALIGNMENT_CENTER)
	label.add_theme_color_override("font_outline_color", Color("#28101e"))
	label.add_theme_constant_override("outline_size", 10)
	label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.75))
	label.add_theme_constant_override("shadow_offset_x", 3)
	label.add_theme_constant_override("shadow_offset_y", 5)
	label.add_theme_constant_override("shadow_outline_size", 10)
	label.add_theme_constant_override("line_spacing", -8)
	return label


## One slice per world for the title backdrop: [painted map, accent color].
func _stripe_slices() -> Array:
	var slices := []
	for index in Progress.WORLDS.size():
		if not Progress.has_content(index):
			continue
		var id := Progress.world_id(index)
		var path := "res://art/backgrounds/%s/level_03.webp" % id
		if ResourceLoader.exists(path):
			slices.append([load(path), Look.accent(id)])
	return slices


## Units the title showcase can pick from: the 40 hand-picked base units in
## data/title_pool.json (the user chose them), shown whatever is unlocked.
## Their art comes from data/showcase.json (written by the content build).
func _showcase_pool() -> Array:
	var showcase = JSON.parse_string(FileAccess.get_file_as_string("res://data/showcase.json"))
	var picks = JSON.parse_string(FileAccess.get_file_as_string("res://data/title_pool.json"))
	var pool := []
	if not (showcase is Dictionary and picks is Dictionary):
		return pool
	for pick in picks.get("units", []):
		for entry in showcase.get(pick.world, []):
			if entry.get("id", "") == pick.unit:
				pool.append(entry)
	return pool


## Settings: sound, music and the Background filter (with a live preview).
func _show_settings() -> void:
	_header("Settings", _show.bind(_show_title))
	var toggles := HBoxContainer.new()
	toggles.add_theme_constant_override("separation", 8)
	_content.add_child(toggles)
	var sound := _button("Sound: %s" % ("On" if Audio.sound_on else "Off"), func():
		Audio.set_sound(not Audio.sound_on)
		_show(_show_settings), toggles)
	var music := _button("Music: %s" % ("On" if Audio.music_on else "Off"), func():
		Audio.set_music(not Audio.music_on)
		_show(_show_settings), toggles)
	for button in [sound, music]:
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_spacer(8)
	_label("Background", 18)
	_label("Calms the painted maps so units and invaders stand out. Busy maps get a little extra.",
		12, DIM_TEXT)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	_content.add_child(row)
	var slider := HSlider.new()
	slider.min_value = 0.0
	slider.max_value = Progress.CALM_MAX
	slider.step = 0.05
	slider.value = Progress.calm_strength()
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	slider.custom_minimum_size.y = 32
	row.add_child(slider)
	var name_label := _label(_calm_name(slider.value), 14, GOLD, HORIZONTAL_ALIGNMENT_RIGHT, row)
	name_label.custom_minimum_size.x = 80
	var material := _calm_preview()
	slider.value_changed.connect(func(value: float):
		Progress.set_calm_strength(value)
		name_label.text = _calm_name(value)
		if material:
			CalmBackground.set_strength(material, value))


## A name for a Background strength: Off, Light, Medium or Strong.
func _calm_name(value: float) -> String:
	if value < 0.05:
		return "Off"
	if value < 0.75:
		return "Light"
	if value < 1.25:
		return "Medium"
	return "Strong"


## A slice of one of the busiest maps with a few units and invaders on it,
## filtered like in a level. Returns its filter so the slider can change it.
func _calm_preview() -> ShaderMaterial:
	var path := "res://art/backgrounds/backyard_bugs/level_04.webp"
	if not ResourceLoader.exists(path):
		return null
	var image := (load(path) as Texture2D).get_image()
	if image.is_compressed():
		image.decompress()
	var material := CalmBackground.make_material(image, Progress.calm_strength())
	var slice := image.get_region(Rect2i(0, image.get_height() / 4, image.get_width(), image.get_width() * 3 / 4))
	var frame := PanelContainer.new()
	frame.add_theme_stylebox_override("panel", Look.panel(CARD_COLOR))
	_content.add_child(frame)
	var preview := Control.new()
	preview.custom_minimum_size.y = 230
	preview.clip_contents = true
	frame.add_child(preview)
	var picture := TextureRect.new()
	picture.texture = ImageTexture.create_from_image(slice)
	picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	picture.set_anchors_preset(Control.PRESET_FULL_RECT)
	picture.material = material
	preview.add_child(picture)
	# Sprites on top, placed by fractions of the preview's size.
	for spot in [["units/fortress/bombardier_beetle_idle", 0.2, 0.3],
			["units/precision/assassin_bug_idle", 0.62, 0.55],
			["invaders/aphid_cluster_move", 0.4, 0.12], ["invaders/aphid_cluster_move", 0.78, 0.18]]:
		_preview_sprite(preview, "res://art/anim/backyard_bugs/%s.png" % spot[0], spot[1], spot[2])
	return material


func _preview_sprite(parent: Control, path: String, x: float, y: float) -> void:
	if not ResourceLoader.exists(path):
		return
	var strip: Texture2D = load(path)
	var frame := AtlasTexture.new()  # the strip's first frame (frames are square)
	frame.atlas = strip
	frame.region = Rect2(0, 0, strip.get_height(), strip.get_height())
	var sprite := TextureRect.new()
	sprite.texture = frame
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sprite.anchor_left = x
	sprite.anchor_right = x
	sprite.anchor_top = y
	sprite.anchor_bottom = y
	sprite.offset_right = 64
	sprite.offset_bottom = 64
	parent.add_child(sprite)


func _show_biomes() -> void:
	_header("Choose a World", _show.bind(_show_title))
	_label("Each world brings new invaders. Beat a world's boss to unlock the next one.", 12, DIM_TEXT)
	for index in Progress.WORLDS.size():
		if index == 5:
			_label("Bonus Worlds", 18, GOLD)
		_world_card(index)


## A world "postcard": a painted banner of the world with its boss and one of
## its invaders on it, then pack progress. Tap an unlocked card to enter.
## Locked worlds are grey; bonus worlds you don't own show their price.
func _world_card(index: int) -> void:
	var world: Dictionary = Progress.WORLDS[index]
	var id := Progress.world_id(index) if Progress.has_content(index) else ""
	var unlocked := Progress.is_biome_unlocked(index) and id != ""
	var accent := Look.accent(id) if id != "" else Look.BORDER
	var panel := PanelContainer.new()
	var style := Look.panel(CARD_COLOR, Color.TRANSPARENT, 12)
	style.set_content_margin_all(0)
	style.border_color = accent if unlocked else Look.BORDER
	style.set_border_width_all(2)
	style.border_width_bottom = 5  # 3D edge, like the buttons
	panel.add_theme_stylebox_override("panel", style)
	_content.add_child(panel)
	var card := VBoxContainer.new()
	card.add_theme_constant_override("separation", 0)
	panel.add_child(card)
	var banner := _postcard_banner(index, id, unlocked, accent)
	card.add_child(banner)
	var below := VBoxContainer.new()
	below.add_theme_constant_override("separation", 6)
	var margin := MarginContainer.new()
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 10)
	margin.add_child(below)
	card.add_child(margin)

	if Progress.is_bonus(index) and not Progress.is_biome_unlocked(index):
		_label(world.theme, 11, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, below)
		var product: String = world.product
		_warning(Store.product(product), below)  # warn before buying here too
		_button("Unlock for %s" % Store.price(product), Store.buy.bind(product), below)
		return
	if id == "":
		_label("Coming soon" + (" (owned)" if Progress.is_bonus(index) else ""), 12, GOLD,
			HORIZONTAL_ALIGNMENT_LEFT, below)
		return
	if not unlocked:
		_label("Beat World %d's boss to unlock." % index, 11, DIM_TEXT, HORIZONTAL_ALIGNMENT_LEFT, below)
		return
	# One symbol per pack, filling up as that pack beats this world's levels.
	var row := _symbol_row(below)
	for pack_id in PackSymbol.ORDER:
		var beaten := Progress.levels_beaten_by(id, pack_id)
		row.add_child(PackSymbol.new().setup(pack_id, float(beaten) / Progress.LEVELS_PER_BIOME, 24))
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(spacer)
	var cleared := Progress.cleared(id)
	var status := "%d/%d cleared" % [cleared, Progress.LEVELS_PER_BIOME] if cleared > 0 else "Tap to play"
	var status_label := _label(status, 13, GOLD, HORIZONTAL_ALIGNMENT_RIGHT, row)
	status_label.theme_type_variation = "TitleLabel"
	status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_make_tappable(panel, _open_biome.bind(index))
	# A newly unlocked world: a NEW tag and a confetti pop (once).
	if Progress.is_world_new(id):
		Progress.mark_world_seen(id)
		var tag := _outlined("NEW!", 18, Look.GOLD)
		_pin_right(tag, 150, 60, 8, 26)
		tag.rotation = 0.12
		banner.add_child(tag)
		var pulse := tag.create_tween().set_loops()
		pulse.tween_property(tag, "modulate", Look.HEART, 0.5)
		pulse.tween_property(tag, "modulate", Color.WHITE, 0.5)
		var pop := func():
			ConfettiBurst.pop(self, panel.global_position + Vector2(panel.size.x / 2, 40),
				50, [accent, GOLD, Color.WHITE, accent.lightened(0.3)])
			Audio.play("evolve")
		get_tree().create_timer(SLIDE_TIME + 0.1).timeout.connect(pop)


## The postcard's picture: a slice of the world's painted map, its name in
## big outlined letters, and (if unlocked) the boss and an invader walking.
func _postcard_banner(index: int, id: String, unlocked: bool, accent: Color) -> Control:
	var world: Dictionary = Progress.WORLDS[index]
	var banner := Control.new()
	banner.custom_minimum_size.y = 100
	# No clipping: the boss is big and breaks out over the top of its card.
	var path := "res://art/backgrounds/%s/level_02.webp" % id
	if id != "" and ResourceLoader.exists(path):
		var picture: Texture2D = load(path)
		var slice := AtlasTexture.new()  # a band from the middle of the map
		slice.atlas = picture
		var band := picture.get_width() * 100.0 / 320.0
		slice.region = Rect2(0, picture.get_height() * 0.42, picture.get_width(), band)
		var rect := TextureRect.new()
		rect.texture = slice
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		rect.set_anchors_preset(Control.PRESET_FULL_RECT)
		rect.modulate = Color(0.78, 0.74, 0.78) if unlocked else Color.WHITE
		if not unlocked:
			var grey := ShaderMaterial.new()
			grey.shader = GRAYSCALE
			rect.material = grey
		banner.add_child(rect)
	else:
		var flat := ColorRect.new()
		flat.color = Look.SURFACE_HI
		flat.set_anchors_preset(Control.PRESET_FULL_RECT)
		banner.add_child(flat)
	# Darken the top-left behind the name so it always reads.
	var shade := TextureRect.new()
	var gradient := GradientTexture2D.new()
	gradient.gradient = Gradient.new()
	gradient.gradient.set_color(0, Color(0, 0, 0, 0.55))
	gradient.gradient.set_color(1, Color(0, 0, 0, 0.0))
	gradient.fill_to = Vector2(0.8, 0.9)
	shade.texture = gradient
	shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	banner.add_child(shade)
	if unlocked:
		var art: Dictionary = _card_art().get(id, {})
		if art.has("invader") and ResourceLoader.exists(art.invader):
			var walker := AnimIcon.new().setup(load(art.invader), 8.0)
			_pin_right(walker, 118, 48, 50)
			banner.add_child(walker)
		if art.has("boss") and ResourceLoader.exists(art.boss):
			var boss := AnimIcon.new().setup(load(art.boss), 6.0)
			_pin_right(boss, 0, 124, -26)
			banner.add_child(boss)
	var number := "BONUS WORLD" if Progress.is_bonus(index) else "WORLD %d" % Progress.main_number(index)
	var small := _outlined(number, 12, accent if unlocked else DIM_TEXT)
	small.position = Vector2(12, 10)
	banner.add_child(small)
	var name := _outlined(world.name, 25, Look.TEXT if unlocked else DIM_TEXT)
	name.position = Vector2(12, 26)
	banner.add_child(name)
	if not unlocked and id != "" and not Progress.is_bonus(index):
		var lock := _outlined("LOCKED", 16, DIM_TEXT)
		_pin_right(lock, 14, 80, 66, 24)
		lock.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		banner.add_child(lock)
	return banner


## Places `control` inside its parent, measured from the parent's right
## edge (so it stays put whatever the screen width): `right` pixels in from
## the edge, `width` wide, `top` down, `height` tall (default: square).
func _pin_right(control: Control, right: float, width: float, top: float, height := -1.0) -> void:
	control.anchor_left = 1.0
	control.anchor_right = 1.0
	control.offset_left = -right - width
	control.offset_right = -right
	control.offset_top = top
	control.offset_bottom = top + (width if height < 0 else height)


## A free-floating title-font label with a thick dark outline.
func _outlined(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.theme_type_variation = "TitleLabel"
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color("#1a0a12"))
	label.add_theme_constant_override("outline_size", 8)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


## Each world's boss and familiar invader strips (from data/showcase.json).
func _card_art() -> Dictionary:
	if _cards_cache.is_empty():
		var showcase = JSON.parse_string(FileAccess.get_file_as_string("res://data/showcase.json"))
		if showcase is Dictionary:
			_cards_cache = showcase.get("_cards", {})
	return _cards_cache


## Makes a whole card act like a button: squashes when pressed, and a tap
## (not a drag) calls `action`.
func _make_tappable(card: Control, action: Callable) -> void:
	card.resized.connect(func(): card.pivot_offset = card.size / 2)
	card.gui_input.connect(func(event: InputEvent):
		if not (event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT):
			return
		var tween := card.create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		if event.pressed:
			tween.tween_property(card, "scale", Vector2(0.97, 0.97), 0.06)
		else:
			tween.tween_property(card, "scale", Vector2.ONE, 0.25)
			if not _dragged and card.get_global_rect().has_point(event.global_position):
				Audio.play("button")
				action.call())


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
			Audio.play("button")
			_going_back = true
			back.call())
	row.add_child(back_button)
	_juice(back_button)
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
	_juice(button)
	return button


## Button juice: a chunky 3D edge that presses down, and a little squash
## when pressed that springs back on release.
func _juice(button: Button, fill := Look.SURFACE_HI, edge := Color("#120a10"), ink := Color.TRANSPARENT,
		depth := 5) -> void:
	var up := Look.panel(fill, Color.TRANSPARENT, 10)
	up.border_color = edge
	up.set_border_width_all(2)
	up.border_width_bottom = depth
	up.border_color = edge
	var hover := up.duplicate()
	hover.bg_color = fill.lightened(0.08)
	var down := up.duplicate()
	down.bg_color = fill.darkened(0.1)
	down.border_width_bottom = 2
	down.expand_margin_top = -float(depth - 2)  # the face moves down, the edge stays
	for style in [up, hover, down]:
		style.content_margin_top = 6
		style.content_margin_bottom = 6
	down.content_margin_top = 6 + depth - 2  # the label moves down with the face
	var off := up.duplicate()
	off.bg_color = Color("#1a1016")
	off.border_color = Color("#0e080c")
	button.add_theme_stylebox_override("normal", up)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", down)
	button.add_theme_stylebox_override("hover_pressed", down)
	button.add_theme_stylebox_override("disabled", off)
	if ink != Color.TRANSPARENT:
		for key in ["font_color", "font_hover_color", "font_pressed_color"]:
			button.add_theme_color_override(key, ink)
		button.add_theme_color_override("font_outline_color", edge)
		button.add_theme_constant_override("outline_size", 6)
	if button.has_meta("juiced"):
		return  # already squashes (restyled again, e.g. the Play button)
	button.set_meta("juiced", true)
	# Squash and spring back (scaled around the middle).
	button.resized.connect(func(): button.pivot_offset = button.size / 2)
	button.button_down.connect(func():
		if button.disabled:
			return
		var tween := button.create_tween()
		tween.tween_property(button, "scale", Vector2(0.96, 0.92), 0.06))
	button.button_up.connect(func():
		var tween := button.create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tween.tween_property(button, "scale", Vector2.ONE, 0.25))


func _spacer(height: float) -> void:
	var spacer := Control.new()
	spacer.custom_minimum_size.y = height
	_content.add_child(spacer)
