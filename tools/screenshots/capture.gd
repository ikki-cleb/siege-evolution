extends SceneTree
## Captures the raw store screenshots from the real game (run by
## tools/screenshots/make_screenshots.sh, which frames them with captions).
##   godot --resolution WxH --script tools/screenshots/capture.gd -- <out_dir>
## Uses the auto-player from the tests to build real defenses.

const AutoPlayerScript := preload("res://tests/auto_player.gd")
var out := "build/screenshots/raw/"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		out = args[0].trim_suffix("/") + "/"
	DirAccess.make_dir_recursive_absolute(out)
	_run.call_deferred()


func _snap(name: String) -> void:
	for i in 2:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out + name + ".png")


func _frames(count: int) -> void:
	for i in count:
		await process_frame


## A level with the auto-player's defenses built over a few waves.
func _game(world: int, level: int, pack: int, waves: int) -> Node:
	var progress = root.get_node("Progress")
	var biome = progress.load_biome(world)
	progress.biome = biome
	progress.pack = biome.packs[pack]
	progress.level_index = level
	var game = load("res://scenes/game.tscn").instantiate()
	root.add_child(game)
	await _frames(3)
	var bot = AutoPlayerScript.new(game, 7)
	game.coins += 200
	while game.wave_number < waves and game.phase != game.Phase.LOST:
		if game.phase == game.Phase.BUILD:
			if not game.relic_offer.is_empty():
				game.pick_relic(0)
			bot.build_phase()
			game.start_wave()
		Engine.time_scale = 4.0
		await process_frame
	# Let the last wave finish, so the next one can be started.
	while game.phase == game.Phase.WAVE:
		await process_frame
	Engine.time_scale = 1.0
	if not game.relic_offer.is_empty():
		game.pick_relic(0)
	return game


## Waits until the wave has lots of invaders on screen (or a time limit).
func _busy(game: Node, wanted: int) -> void:
	for i in 1500:
		if game.board.invaders.size() >= wanted:
			return
		await process_frame


func _run() -> void:
	var progress = root.get_node("Progress")
	var achievements = root.get_node("Achievements")
	progress.reset()
	achievements._layer.visible = false  # no unlock banners in the shots

	# 1. Title: the evolution tree mid-flash.
	var menu = load("res://scenes/menu.tscn").instantiate()
	root.add_child(menu)
	await _frames(3)
	for child in menu._content.get_children():
		if child is EvolutionShowcase:
			child._pool = child._pool.filter(func(e): return e.name == "Praying Mantis")
			child._order = []
			child._next()
			child._time = 2.2
	await _snap("01_title")

	# 6. World postcards (with a few worlds beaten).
	for id in ["backyard_bugs", "wild_kingdom", "immune_system", "total_war"]:
		progress._data.biomes[id] = {"cleared": 5}
		progress.mark_world_seen(id)
	progress.record_endless("backyard_bugs", "fortress", 31)
	menu._show(menu._show_biomes)
	await _frames(30)
	await _snap("06_worlds")
	menu.queue_free()
	await _frames(2)

	# 2. A busy wave: defenses built, invaders on the move.
	var game = await _game(1, 3, 0, 5)
	game.start_wave()
	await _busy(game, 8)
	await _snap("02_wave")
	# 3. Picking an evolution (after the wave, a survivor is selected).
	while game.phase == game.Phase.WAVE:
		Engine.time_scale = 4.0
		await process_frame
	Engine.time_scale = 1.0
	game.coins += 300
	for cell in game.board.units:
		var unit = game.board.units[cell]
		if unit.data.role != UnitData.Role.WALL and not unit.data.evolutions.is_empty():
			game._on_cell_tapped(cell)
			break
	await _snap("03_evolve")
	game.queue_free()
	await _frames(2)

	# 5. The relic picker.
	game = await _game(4, 2, 2, 2)
	game.relic_offer = game.board.relics.roll_offer(game.unit_types, 3, 11)
	game.hud.show_relic_picker(game.relic_offer)
	await _frames(30)
	await _snap("05_relics")
	game.queue_free()
	await _frames(2)

	# 4. The boss arrives.
	game = await _game(0, 4, 0, 7)
	game.start_wave()
	await _frames(70)  # the BOSS INCOMING banner is on screen
	await _snap("04_boss")
	quit()
