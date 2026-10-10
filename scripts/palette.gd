class_name Palette
## The game's colors and shared panel style. A plain class, so any script can
## use it (Palette.GOLD, Palette.panel()) even before the autoloads exist.

const BG := Color("#140c12")
const SURFACE := Color("#22151e")
const SURFACE_HI := Color("#2e1d29")
const BORDER := Color("#4a2f40")
const TEXT := Color("#f3e3ea")
const TEXT_DIM := Color("#b79aa8")
const GOLD := Color("#ffd23c")
const HEART := Color("#ff4d6d")
const GOOD := Color("#7fe08a")

## The in-game currency's icon: a coin drawn into the game font (see
## tools/make_font.py), so it can sit right inside any text: "%s 25" % Palette.COIN
const COIN := "\uE000"

## One accent color per world, used for titles and highlights.
const ACCENTS := {
	"immune_system": Color("#ff5a7a"),
	"backyard_bugs": Color("#8fd04a"),
	"wild_kingdom": Color("#e8a03a"),
	"total_war": Color("#6fb3e8"),
	"galactic_siege": Color("#b07aff"),
	"kitchen_defense": Color("#5ad1b8"),
	"birthday_bash": Color("#ff7ac8"),
}
## The red tag that warns a bonus world is post-game hard.
const WARNING := Color("#ff5a4a")


static func accent(world_id: String) -> Color:
	return ACCENTS.get(world_id, HEART)


## A rounded panel. `edge` adds a colored stripe down the left side.
static func panel(color := SURFACE, edge := Color.TRANSPARENT, radius := 8) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(radius)
	style.set_content_margin_all(12)
	style.border_color = BORDER if edge.a == 0.0 else edge
	style.set_border_width_all(1)
	if edge.a > 0.0:
		style.border_width_left = 4
	return style
