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
const COIN_COLOR := Palette.GOLD
const FINAL_WORLD := "galactic_siege"
const ORB_FLIGHT_TIME := 0.6


## A small glowing coin orb that flies from a kill to the coin counter.
class Orb extends Node2D:
	func _draw() -> void:
		draw_circle(Vector2.ZERO, 8.0, Color(1, 0.85, 0.3, 0.3))
		draw_circle(Vector2.ZERO, 4.5, Color(1, 0.95, 0.55))
		draw_circle(Vector2(-1.5, -1.5), 1.5, Color.WHITE)

var game  # The Game node (game.gd)

var _level_label: Label
var _wave_label: Label
var _hp_label: Label
var _coins_label: Label
var _next_label: Label
var _footnote_label: Label
var _message_label: Label
var _unit_row: HBoxContainer
var _unit_buttons := {}  # UnitData -> Button
var _selection_row: HBoxContainer
var _evolve_buttons: Array[Button] = []
## Upgrades take two taps: the first previews (this index), the second buys.
var _armed_option := -1
## The unit whose upgrade is being previewed (a new selection resets it).
var _armed_unit: Unit = null
var _sell_button: Button
## Removing takes two taps: the unit the first tap armed (null = none).
var _remove_armed_unit: Unit = null
var _speed_button: Button
## Shown while a unit is selected, so it's obvious how to deselect it.
var _cancel_button: Button
## Turns the invaders' route preview on or off.
var _paths_button: Button
var _start_button: Button
## Parent of every HUD control (carries the theme).
var _root: Control
## Coins still flying toward the counter (already added to the game's total).
var _orb_coins := 0
## Icons of the relics picked this level, in the board's left margin.
var _relic_column: VBoxContainer
var _relic_column_key := ""
## The 1-of-3 relic picker while it's open.
var _relic_picker: Control


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
	_relic_column = VBoxContainer.new()
	_relic_column.position = Vector2(5, 88)
	_relic_column.add_theme_constant_override("separation", 4)
	_root.add_child(_relic_column)


func refresh() -> void:
	_level_label.text = "%s · %s" % [game.level.display_name, game.pack.display_name]
	_wave_label.text = "Wave %d/%d" % [game.wave_number, game.level.waves.size()]
	_hp_label.text = "Base %d/%d" % [game.base_hp, game.level.base_hp]
	_coins_label.text = "%s %d" % [Palette.COIN, game.coins - _orb_coins]
	_next_label.text = game.next_wave_summary()
	_footnote_label.text = game.footnote()
	# Selecting a different unit (or nothing) cancels an upgrade preview.
	if game.selected_unit() != _armed_unit or game.phase != game.Phase.BUILD:
		_disarm()
	if game.selected_unit() != _remove_armed_unit or game.phase != game.Phase.BUILD:
		_remove_armed_unit = null
	if _armed_option >= 0:
		# The footnote area shows the before → after numbers.
		_footnote_label.text = game.stat_changes(_armed_unit.data, _armed_unit.data.evolutions[_armed_option])

	var building: bool = game.phase == game.Phase.BUILD
	for type in _unit_buttons:
		var button: Button = _unit_buttons[type]
		var free_left: int = game.hand.get(type.id, 0)
		button.text = "x%d free" % free_left if free_left > 0 else "%s %d" % [Palette.COIN, game.unit_cost(type)]
		button.disabled = not building
		button.set_pressed_no_signal(game.selected_type == type)

	# A tapped unit replaces the unit bar with its options.
	var unit: Unit = game.selected_unit()
	var show_options := unit != null and building
	_unit_row.visible = not show_options
	_selection_row.visible = show_options
	if show_options:
		# The next tier's two options: tier 1 for a placed unit, capstones for
		# a tier-1 evolution, nothing once it's a capstone.
		var options: Array[UnitData] = unit.data.evolutions
		for i in _evolve_buttons.size():
			var button := _evolve_buttons[i]
			if options.is_empty():
				button.text = "Capstone\n(maxed)" if unit.is_capstone() else "-"
				button.disabled = true
				button.icon = unit.data.icon()
			elif i >= options.size():
				button.text = "-"
				button.disabled = true
				button.icon = null
			elif not game.is_ready_to_evolve(unit):
				button.text = "%s\nafter 1 wave" % options[i].display_name
				button.icon = options[i].icon()
				button.disabled = true
			elif i == _armed_option:
				button.text = "Tap again\nto buy %s %d" % [Palette.COIN, game.evolve_cost(options[i])]
				button.icon = options[i].icon()
				button.disabled = not game.can_evolve(options[i])
			else:
				button.text = "%s\n%s %d" % [options[i].display_name, Palette.COIN, game.evolve_cost(options[i])]
				button.icon = options[i].icon()
				button.disabled = false  # tap to preview, even if it's too expensive yet
		var value: Dictionary = game.sell_value(unit)
		if _remove_armed_unit == unit:
			_sell_button.text = "Tap again\nto remove"
		else:
			_sell_button.text = "Remove\nto hand" if value.to_hand else "Remove\n+%s %d" % [Palette.COIN, value.coins]

	_cancel_button.visible = game.has_selection()
	_speed_button.text = "%dx" % game.speed
	_paths_button.text = "Paths: %s" % ("On" if _progress().show_paths() else "Off")
	_start_button.disabled = not building or not game.relic_offer.is_empty()
	_refresh_relic_column()
	_start_button.text = "Start Wave" if building else "Wave %d..." % game.wave_number


## The message line has room for one line at normal size. Longer messages
## (like a unit's full stats) switch to a smaller size so two lines fit.
const MESSAGE_SMALL_FONT := 9


func show_message(text: String) -> void:
	_message_label.text = text
	_message_label.add_theme_font_size_override("font_size", SMALL_FONT)
	if _message_label.get_line_count() > 1:
		_message_label.add_theme_font_size_override("font_size", MESSAGE_SMALL_FONT)


## Launches a coin orb from a screen position to the coin counter. The counter
## only counts it once it lands.
func spawn_orb(from: Vector2, amount: int) -> void:
	_orb_coins += amount
	var orb := Orb.new()
	orb.position = from
	_root.add_child(orb)
	var target := _coins_label.position + Vector2(_coins_label.size.x - 24, _coins_label.size.y / 2)
	var tween := create_tween()
	tween.tween_property(orb, "position", target, ORB_FLIGHT_TIME) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func():
		orb.queue_free()
		_orb_coins -= amount
		_coins_label.modulate = Color.WHITE
		create_tween().tween_property(_coins_label, "modulate", COIN_COLOR, 0.25)
		Sfx.play("coins")
		refresh())


# --- Relics -------------------------------------------------------------------

## The picked relics, top to bottom; ones waiting for the next wave are dimmed.
## Tapping one shows what it does.
func _refresh_relic_column() -> void:
	var relics: RelicSet = game.board.relics
	var key := str(relics.active.map(func(r): return r.id)) + str(relics.pending.map(func(r): return r.id))
	if key == _relic_column_key:
		return
	_relic_column_key = key
	for child in _relic_column.get_children():
		child.queue_free()
	for relic in relics.active + relics.pending:
		var waiting: bool = relics.pending.has(relic)
		var button := Button.new()
		button.custom_minimum_size = Vector2(30, 30)
		button.flat = true
		button.focus_mode = Control.FOCUS_NONE
		button.pressed.connect(func():
			show_message("%s (%s): %s%s" % [relic.name, relic.rarity, relic.desc,
				" Starts next wave." if waiting else ""]))
		var icon := RelicIcon.new().setup(relic)
		icon.dimmed = waiting
		icon.set_anchors_preset(Control.PRESET_FULL_RECT)
		button.add_child(icon)
		_relic_column.add_child(button)


## Opens the "choose 1 of 3" relic cards over the board.
func show_relic_picker(offer: Array) -> void:
	if _relic_picker:
		_relic_picker.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(Palette.BG, 0.0)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP  # the board can't be tapped meanwhile
	_root.add_child(dim)
	_relic_picker = dim
	create_tween().tween_property(dim, "color:a", 0.88, 0.25)

	var box := VBoxContainer.new()
	box.position = Vector2(20, 120)
	box.custom_minimum_size = Vector2(320, 0)
	box.add_theme_constant_override("separation", 10)
	dim.add_child(box)
	box.add_child(_end_label("Choose a Relic", 28, Palette.GOLD))
	box.add_child(_end_label("It powers up your units until the end of this level. It starts working when the next wave starts.", 12, Palette.TEXT_DIM))
	for i in offer.size():
		box.add_child(_relic_card(offer[i], i))
	Sfx.play("evolve", 0.0)


func close_relic_picker() -> void:
	if _relic_picker:
		_relic_picker.queue_free()
		_relic_picker = null


func _relic_card(relic: Dictionary, index: int) -> Button:
	var rarity_color: Color = RelicSet.RARITY_COLORS[relic.rarity]
	var card := Button.new()
	card.custom_minimum_size = Vector2(320, 100)
	card.focus_mode = Control.FOCUS_NONE
	for state in ["normal", "hover", "pressed", "hover_pressed"]:
		var style := Palette.panel(Palette.SURFACE_HI if state == "normal" else Color("#3a2434"), rarity_color, 10)
		style.set_border_width_all(2 if state == "normal" else 3)
		card.add_theme_stylebox_override(state, style)
	card.pressed.connect(func(): game.pick_relic(index))
	var row := HBoxContainer.new()
	row.position = Vector2(12, 10)
	row.size = Vector2(296, 80)
	row.add_theme_constant_override("separation", 12)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.add_child(row)
	var icon := RelicIcon.new().setup(relic)
	icon.custom_minimum_size = Vector2(56, 56)
	icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(icon)
	var text := VBoxContainer.new()
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text.add_theme_constant_override("separation", 2)
	text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(text)
	var title := Label.new()
	title.text = relic.name
	title.theme_type_variation = "TitleLabel"
	title.add_theme_font_size_override("font_size", 17)
	title.modulate = rarity_color.lightened(0.3)
	text.add_child(title)
	var rarity := Label.new()
	rarity.text = String(relic.rarity).to_upper()
	rarity.add_theme_font_size_override("font_size", 9)
	rarity.modulate = rarity_color
	text.add_child(rarity)
	var desc := Label.new()
	desc.text = relic.desc
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc.custom_minimum_size.x = 220
	desc.add_theme_font_size_override("font_size", 11)
	text.add_child(desc)
	for label in [title, rarity, desc]:
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return card


func show_end_screen(won: bool) -> void:
	var biome: BiomeData = _progress().biome
	if won and game.is_last_level() and biome.id == FINAL_WORLD:
		_show_celebration("VICTORY!", "The Mothership is down and the galaxy is safe.",
			"From the backyard to the stars, you defended every world. Congratulations, Commander!")
		return
	if won and game.is_last_level() and _progress().is_bonus_biome(biome.id):
		_show_celebration("%s cleared!" % biome.display_name, "You beat a post-game bonus world.",
			"That took real skill. The %s is safe... for now." % ("cookie jar" if biome.id == "kitchen_defense" else "birthday cake"),
			biome.display_name)
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
	title.theme_type_variation = "TitleLabel"
	title.modulate = _accent() if won else Palette.TEXT_DIM
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)
	card.scale = Vector2(0.85, 0.85)
	card.pivot_offset = Vector2(140, 80)
	create_tween().tween_property(card, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

	if won:
		box.add_child(_pack_progress())
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


## The pack's symbol filling up for this win: "Fortress: 3/5 levels of
## this world". It animates from the old fill to the new one.
func _pack_progress() -> Control:
	var progress := _progress()
	var levels: int = progress.LEVELS_PER_BIOME
	var now: int = progress.levels_beaten_by(progress.biome.id, game.pack.id)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 10)
	var symbol := PackSymbol.new().setup(game.pack.id, float(game.pack_levels_before) / levels, 48)
	row.add_child(symbol)
	var label := Label.new()
	label.text = "%s\n%d/%d levels of this world" % [game.pack.display_name, now, levels]
	label.add_theme_font_size_override("font_size", FONT)
	label.modulate = game.pack.color.lightened(0.3)
	row.add_child(label)
	if now > game.pack_levels_before:
		var tween := create_tween()
		tween.tween_interval(0.4)
		tween.tween_property(symbol, "fill", float(now) / levels, 0.8) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tween.tween_callback(func(): Sfx.play("evolve", 0.0))
	return row


## A big celebration with confetti: after the Mothership (the end of the main
## game) or a bonus world's boss. It nudges toward the bonus worlds the player
## doesn't own yet, except `this_world` (the one just beaten).
func _show_celebration(title_text: String, subtitle_text: String, detail_text: String,
		this_world := "") -> void:
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

	var title := _end_label(title_text, 40 if title_text.length() < 12 else 28, Palette.GOLD)
	var subtitle := _end_label(subtitle_text, 16, Palette.TEXT)
	var detail := _end_label(detail_text, 13, Palette.TEXT_DIM)
	for label in [title, subtitle, detail]:
		box.add_child(label)
	box.add_child(_pack_progress())

	var missing: Array[String] = []
	for index in _progress().WORLDS.size():
		var world: Dictionary = _progress().WORLDS[index]
		if _progress().is_bonus(index) and not _store().owns(world.product) and world.name != this_world:
			missing.append(world.name)
	if not missing.is_empty():
		var pitch := PanelContainer.new()
		pitch.add_theme_stylebox_override("panel", Palette.panel(Palette.SURFACE, Palette.GOLD, 10))
		box.add_child(pitch)
		var inner := VBoxContainer.new()
		inner.add_theme_constant_override("separation", 8)
		pitch.add_child(inner)
		inner.add_child(_end_label("Ready for more?", 18, Palette.GOLD))
		var noun := "Bonus world" if missing.size() == 1 else "Bonus worlds"
		inner.add_child(_end_label("%s: %s. Brand-new places to defend." % [noun, " and ".join(missing)], 13, Palette.TEXT))
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
	if size >= 18:
		label.theme_type_variation = "TitleLabel"  # big text uses the title font
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
	# The current pack's symbol, then "Level · Pack".
	var symbol := PackSymbol.new().setup(game.pack.id, 1.0, 18)
	symbol.position = Vector2(10, 9)
	symbol.size = Vector2(18, 18)
	_root.add_child(symbol)
	_level_label = _make_label(Vector2(32, 8), Vector2(240, 20), FONT)
	var menu := _make_button("Menu", game.quit_to_menu)
	menu.position = Vector2(WIDTH - 72, 6)
	menu.custom_minimum_size = Vector2(60, 26)
	menu.add_theme_font_size_override("font_size", SMALL_FONT)
	_root.add_child(menu)
	_hp_label = _make_label(Vector2(12, 34), Vector2(110, 20), FONT)
	_wave_label = _make_label(Vector2(125, 34), Vector2(110, 20), FONT, HORIZONTAL_ALIGNMENT_CENTER)
	_coins_label = _make_label(Vector2(238, 34), Vector2(110, 20), FONT, HORIZONTAL_ALIGNMENT_RIGHT)
	_next_label = _make_label(Vector2(12, 57), Vector2(336, 20), SMALL_FONT)
	_level_label.modulate = _accent()
	_hp_label.modulate = Palette.HEART
	_coins_label.modulate = COIN_COLOR
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
		button.icon = type.icon()
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
		# Long capstone names wrap onto a second line instead of being cut off.
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.clip_text = true
		button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_selection_row.add_child(button)
		_evolve_buttons.append(button)
	_sell_button = _make_button("Remove", _on_remove_pressed)
	_sell_button.custom_minimum_size = Vector2(80, 64)
	_sell_button.add_theme_font_size_override("font_size", SMALL_FONT)
	_selection_row.add_child(_sell_button)

	var control_row := HBoxContainer.new()
	control_row.position = Vector2(12, BOTTOM_TOP + 96)
	control_row.size = Vector2(336, 40)
	control_row.add_theme_constant_override("separation", 6)
	_root.add_child(control_row)
	_speed_button = _make_button("1x", game.cycle_speed)
	_paths_button = _make_button("Paths: On", game.toggle_paths)
	_paths_button.add_theme_font_size_override("font_size", SMALL_FONT)
	_cancel_button = _make_button("X  Cancel", game.cancel_selection)
	_cancel_button.modulate = Palette.HEART.lightened(0.3)
	_cancel_button.visible = false
	_start_button = _make_button("Start Wave", game.start_wave)
	_start_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for button in [_speed_button, _paths_button, _cancel_button, _start_button]:
		button.custom_minimum_size.y = 40
		control_row.add_child(button)


## First tap: preview what the upgrade does. Second tap on the same one: buy it.
func _on_evolve_pressed(index: int) -> void:
	var unit: Unit = game.selected_unit()
	if unit == null or index >= unit.data.evolutions.size():
		return
	var option: UnitData = unit.data.evolutions[index]
	if _armed_unit == unit and _armed_option == index:
		_disarm()
		game.evolve_selected(option)
		return
	_armed_unit = unit
	_armed_option = index
	var cost_note := "" if game.coins >= game.evolve_cost(option) else "  (need %s %d)" % [Palette.COIN, game.evolve_cost(option)]
	show_message("%s: %s%s" % [option.display_name, option.description, cost_note])
	refresh()
	game.board.preview_range = option.attack_range if option.can_attack() else 0.0
	game.board.queue_redraw()


## First tap on Remove asks to confirm; the second removes the unit.
func _on_remove_pressed() -> void:
	var unit: Unit = game.selected_unit()
	if unit == null:
		return
	if _remove_armed_unit == unit:
		_remove_armed_unit = null
		game.sell_selected()
		return
	_remove_armed_unit = unit
	show_message("Remove %s? Tap Remove again to confirm, or Cancel." % unit.data.display_name)
	refresh()


func _disarm() -> void:
	_armed_option = -1
	_armed_unit = null
	if game.board.preview_range > 0.0:
		game.board.preview_range = 0.0
		game.board.queue_redraw()


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
