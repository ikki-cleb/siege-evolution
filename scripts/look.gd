extends Node
## The game's visual style: font, colors, and button/panel styles. Loaded
## automatically at startup as "Look"; it applies its theme to the whole game,
## so every Button, Label and panel picks the style up on its own.
##   Look.accent("galactic_siege")    -> that world's accent color
##   Look.panel(color)                -> a rounded panel style

## Two fonts (built by tools/make_font.py): a bubbly one for titles and
## buttons, and a clean one for everything else. Labels opt into the title
## font with `label.theme_type_variation = "TitleLabel"`.
const FONT := preload("res://assets/fonts/SiegeText.ttf")
const TITLE_FONT := preload("res://assets/fonts/SiegeTitle.ttf")
## Labels at least this big use the title font (see use_title_font).
const TITLE_SIZE := 18

# Colors live in Palette (scripts/palette.gd) so every script can use them.
const BG := Palette.BG
const SURFACE := Palette.SURFACE
const SURFACE_HI := Palette.SURFACE_HI
const BORDER := Palette.BORDER
const TEXT := Palette.TEXT
const TEXT_DIM := Palette.TEXT_DIM
const GOLD := Palette.GOLD
const HEART := Palette.HEART
const GOOD := Palette.GOOD
const ACCENTS := Palette.ACCENTS

var theme := Theme.new()


func _ready() -> void:
	_build_theme()
	get_tree().root.theme = theme


func accent(world_id: String) -> Color:
	return Palette.accent(world_id)


func panel(color := SURFACE, edge := Color.TRANSPARENT, radius := 8) -> StyleBoxFlat:
	return Palette.panel(color, edge, radius)


## Ligatures off: fancy letter joins (like "fi") don't suit game text.
func _no_ligatures(base: Font) -> FontVariation:
	var font := FontVariation.new()
	font.base_font = base
	font.opentype_features = {TextServerManager.get_primary_interface().name_to_tag("liga"): 0}
	return font


func _button_style(bg: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = bg
	style.border_color = border
	style.set_border_width_all(2)
	style.border_width_bottom = 3  # a little depth
	style.set_corner_radius_all(8)
	style.content_margin_left = 10
	style.content_margin_right = 10
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	return style


func _build_theme() -> void:
	theme.default_font = _no_ligatures(FONT)
	theme.default_font_size = 14
	var title := _no_ligatures(TITLE_FONT)
	theme.set_font("font", "Button", title)
	theme.set_type_variation("TitleLabel", "Label")
	theme.set_font("font", "TitleLabel", title)

	theme.set_stylebox("normal", "Button", _button_style(SURFACE_HI, BORDER))
	theme.set_stylebox("hover", "Button", _button_style(Color("#3a2434"), Color("#6a4258")))
	theme.set_stylebox("pressed", "Button", _button_style(Color("#4a2a3e"), HEART))
	theme.set_stylebox("hover_pressed", "Button", _button_style(Color("#4a2a3e"), HEART))
	theme.set_stylebox("disabled", "Button", _button_style(Color("#1a1016"), Color("#2a1a24")))
	theme.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	theme.set_color("font_color", "Button", TEXT)
	theme.set_color("font_hover_color", "Button", Color.WHITE)
	theme.set_color("font_pressed_color", "Button", Color.WHITE)
	theme.set_color("font_disabled_color", "Button", Color("#6a5560"))
	theme.set_color("font_color", "Label", TEXT)

	theme.set_stylebox("panel", "PanelContainer", panel())
	theme.set_stylebox("panel", "Panel", panel(SURFACE, Color.TRANSPARENT, 0))

	var grabber := StyleBoxFlat.new()
	grabber.bg_color = BORDER
	grabber.set_corner_radius_all(3)
	theme.set_stylebox("grabber", "VScrollBar", grabber)
	theme.set_stylebox("grabber_highlight", "VScrollBar", grabber)
	theme.set_stylebox("scroll", "VScrollBar", StyleBoxEmpty.new())
