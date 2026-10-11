class_name RelicIcon
extends Control
## Draws a relic's little pixel icon (9x9 pixels, scaled to fit the control).
## Each relic in data/relics.json names one of the SHAPES below plus a color.
## Picture key: "#" relic color, "l" lighter, "d" darker, "w" white shine,
## "." empty. A dark outline is added around every shape automatically.

const OUTLINE := Color(0.09, 0.05, 0.08)

const SHAPES := {
	"sword": ["......l#.", ".....l#d.", "....l#d..", "...l#d...", "d.l#d....", ".dld.....", "..dd.....", ".d..d....", "d........"],
	"eye": [".........", "...###...", ".##lll##.", "#lldddll#", "#lld.dll#", "#lldddll#", ".##lll##.", "...###...", "........."],
	"gear": ["...#.#...", "..#####..", ".##ldl##.", "##ld.dl##", ".#d...d#.", "##ld.dl##", ".##ldl##.", "..#####..", "...#.#..."],
	"brick": [".........", "#########", "l##d#l##d", "ddddddddd", "#d#l##d##", "l#dd#l#dd", "ddddddddd", "##l##d#l#", "ddddddddd"],
	"leaf": [".......l#", ".....l##.", "...l###d.", "..l##d#d.", ".l#d#dd..", ".##d#d...", ".#d#d....", "d#dd.....", "d........"],
	"thorn": ["....l....", "....#....", "...l#d...", "l..##d..l", ".#l##d#d.", "..####d..", "..l##dd..", ".l#d.#d..", "l#d...#d."],
	"helmet": [".........", "...lll...", "..l###d..", ".l#####d.", ".l#####d.", ".ddddddd.", ".#.....#.", ".d.....d.", "........."],
	"bullet": ["....l....", "...l#d...", "...l#d...", "...l#d...", "...ddd...", "...l#d...", "...l#d...", "...l#d...", "...ddd..."],
	"lens": [".........", "...lll...", "..lwww#..", ".lww###d.", ".lw####d.", ".l####dd.", "..##ddd..", "....d#d..", ".....d#d."],
	"bomb": [".....l#..", "......d..", "...###...", "..#lll#..", ".#lw###d.", ".#l####d.", ".#####dd.", "..#dddd..", "...ddd..."],
	"snowflake": ["....l....", ".l..#..l.", "..l.#.l..", "...l#l...", "l###w###l", "...l#l...", "..l.#.l..", ".l..#..l.", "....l...."],
	"hourglass": ["ddddddddd", ".l#####d.", "..l###d..", "...l#d...", "....#....", "...l#d...", "..l###d..", ".l#####d.", "ddddddddd"],
	"bell": ["....#....", "...l#d...", "..l###d..", "..l###d..", ".l#####d.", ".l#####d.", "l#######d", "ddddddddd", "....d...."],
	"drop": ["....#....", "....#....", "...l#d...", "..l###d..", ".lw####d.", ".lw####d.", ".l#####d.", "..dd#dd..", "...ddd..."],
	"target": ["..#####..", ".#lllll#.", "#l#####l#", "#l#lll#l#", "#l#l#l#l#", "#l#lll#l#", "#l#####l#", ".#lllll#.", "..#####.."],
	"scroll": [".ll####d.", "l#d###d#d", ".d#lll#d.", "..#ddd#..", "..#lll#..", "..#ddd#..", ".l#lll#d.", "l#d###d#d", ".dd###dd."],
	"hive": ["...lll...", "..l###d..", ".ldddddd.", ".l#####d.", "ldddddddd", ".l#####d.", ".ldd.ddd.", "..l###d..", "...ddd..."],
	"feather": [".......l#", "......l#d", ".....l#d.", "....l#d..", "...l#d...", "..l#d....", ".l#d.....", ".dd......", "d........"],
	"fist": [".........", ".l#l#l#..", "l#######.", "l########", "l#######d", ".l######d", ".l#####d.", "..#####d.", "..ddddd.."],
	"cross": ["...lll...", "...l#d...", "...l#d...", "lll###lll", "l#######d", "ddd###ddd", "...l#d...", "...l#d...", "...ddd..."],
	"net": ["#.#.#.#.#", ".l.l.l.l.", "#.#.#.#.#", ".l.l.l.l.", "#.#.#.#.#", ".l.l.l.l.", "#.#.#.#.#", ".l.l.l.l.", "#.#.#.#.#"],
	"key": [".........", ".lll.....", "l###d....", "l#.#d####", "l###d#d#d", ".ddd.d.d.", ".........", ".........", "........."],
	"bag": ["...l#d...", "....#....", "..l###d..", ".l#####d.", "l###l###d", "l##l#d##d", "l###d###d", ".l#####d.", "..ddddd.."],
	"box": [".........", ".lllllll.", "l#######d", "l###l###d", "ddddddddd", "l###l###d", "l###l###d", "l#######d", "ddddddddd"],
	"gift": ["..l#.#d..", "...l#d...", "lllllllll", "l###l###d", "ddddddddd", "l###l###d", "l###l###d", "l###l###d", "ddddddddd"],
	"heart": [".........", ".ll...ll.", "lw#d.l##d", "lw##l###d", "l#######d", ".l#####d.", "..l###d..", "...l#d...", "....d...."],
	"coin": ["..lllll..", ".l#####d.", "l##lll##d", "l#l###d#d", "l#l###d#d", "l#l###d#d", "l##ddd##d", ".l#####d.", "..ddddd.."],
	"gem": [".........", "..lllll..", ".lw###dd.", "lw#####dd", ".l#####d.", "..l###d..", "...l#d...", "....d....", "........."],
	"shield": ["lllllllll", "l#######d", "l###l###d", "l##lll##d", "l###l###d", ".l#####d.", ".l#####d.", "..l###d..", "...ddd..."],
	"potion": ["...ddd...", "...l#d...", "...l#d...", "..l###d..", ".lw####d.", "l#######d", "l#######d", ".l#####d.", "..ddddd.."],
	"chain": ["..lll....", ".l#.#d...", ".l#.#d...", "..d#ll...", "...l#.#d.", "...ldd#d.", "....l#.#d", "....l#.#d", ".....ddd."],
	"arrows": ["l.l.l....", ".#.#.#...", "..d#d#d..", "...#.#.#.", "....#.#.#", ".....#.#.", "......#.#", "......ld.", ".......ld"],
	"drum": ["..lllll..", ".l#####d.", "ldddddddd", "l#d#d#d#d", "l#d#d#d#d", "l#d#d#d#d", "ldddddddd", ".l#####d.", "..ddddd.."],
	"axe": [".l#d.....", "l###d....", "l####d...", "l###dd...", ".l##ld...", "....ld...", "....ld...", "....ld...", "....dd..."],
	"hook": ["....l#d..", "....l#d..", "....l#d..", "....l#d..", "....l#d..", "l...l#d..", "l#..l#d..", ".l#l##d..", "..dddd..."],
	"egg": ["...lll...", "..lw##d..", ".lw####d.", ".l#####d.", "l#######d", "l#######d", "l#######d", ".l#####d.", "..ddddd.."],
	"bolt": [".....l#d.", "....l#d..", "...l#d...", "..l####d.", ".l####d..", "...l#d...", "..l#d....", ".l#d.....", ".dd......"],
	"flame": ["....l....", "...l#....", "...l#d.l.", "..l##d.#.", ".l##ld#d.", ".l#lwl#d.", "l##lwl##d", ".l##l##d.", "..ddddd.."],
}


var shape := "gem"
var color := Color.WHITE
## Dim the icon (e.g. a relic that isn't active yet).
var dimmed := false


func setup(p_shape: String, p_color: Color) -> RelicIcon:
	shape = p_shape
	color = p_color
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()
	return self


func _draw() -> void:
	var rows: Array = SHAPES.get(shape, SHAPES.gem)
	var px := minf(size.x, size.y) / 11.0  # 9 pixels plus a 1-pixel outline each side
	var origin := (size - Vector2(px, px) * 11.0) / 2.0 + Vector2(px, px)
	var colors := {"#": color, "l": color.lightened(0.35), "d": color.darkened(0.4), "w": Color.WHITE}
	var alpha := 0.45 if dimmed else 1.0
	# Outline: every empty pixel next to a filled one.
	for y in range(-1, 10):
		for x in range(-1, 10):
			if _filled(rows, x, y):
				continue
			if _filled(rows, x + 1, y) or _filled(rows, x - 1, y) or _filled(rows, x, y + 1) or _filled(rows, x, y - 1):
				draw_rect(Rect2(origin + Vector2(x, y) * px, Vector2(px, px)), Color(OUTLINE, alpha))
	for y in 9:
		for x in 9:
			var key: String = rows[y][x]
			if key != ".":
				draw_rect(Rect2(origin + Vector2(x, y) * px, Vector2(px, px)), Color(colors[key], alpha))


func _filled(rows: Array, x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < 9 and y < 9 and rows[y][x] != "."
