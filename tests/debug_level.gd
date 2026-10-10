extends SceneTree
## Plays one level with the auto-player and prints, wave by wave, what it
## built and what leaked. Handy for investigating balance problems.
##   godot --headless --fixed-fps 60 --script tests/debug_level.gd -- <world> <pack> <level> [seed]
## Example (World 2, Swarm, level 2):  ... -- 1 swarm 2

func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var progress: Node = root.get_node("Progress")
	var biome: BiomeData = progress.load_biome(int(args[0]))
	progress.biome = biome
	progress.pack = biome.find_pack(args[1])
	progress.level_index = int(args[2]) - 1
	var game: Node = load("res://scenes/game.tscn").instantiate()
	root.add_child(game)
	await process_frame
	var player := AutoPlayer.new(game, int(args[3]) if args.size() > 3 else 7)
	var leaks := {}
	game.board.base_hit.connect(func(invader): leaks[invader.id] = leaks.get(invader.id, 0) + 1)
	while game.phase != game.Phase.WON and game.phase != game.Phase.LOST:
		player.build_phase()
		_print_board(game)
		var wave: WaveData = game.level.waves[game.wave_number]
		print("  wave %d: %s" % [game.wave_number + 1, ", ".join(wave.entries.map(func(e): return "%d %s" % [e.count, e.invader.id]))])
		leaks.clear()
		game.start_wave()
		while game.phase == game.Phase.WAVE:
			await process_frame
		print("  leaked: %s   base %d/20, ATP %d" % [leaks, game.base_hp, game.atp])
	print("RESULT: %s" % ("WON" if game.phase == game.Phase.WON else "LOST"))
	quit()


func _print_board(game: Node) -> void:
	var board: Board = game.board
	var route := {}
	for spawn in board.spawn_cells:
		for cell in board.walker_path(spawn):
			route[cell] = true
	for y in board.grid_size.y:
		var line := ""
		for x in board.grid_size.x:
			var cell := Vector2i(x, y)
			if board.units.has(cell):
				var unit: Unit = board.units[cell]
				line += "W" if unit.base_data.role == UnitData.Role.WALL else str(game.unit_types.find(unit.base_data))
			elif board.rocks.has(cell):
				line += "#"
			elif cell in board.spawn_cells:
				line += "S"
			elif cell == board.base_cell:
				line += "B"
			else:
				line += "·" if route.has(cell) else " "
		print("   |%s|" % line)
