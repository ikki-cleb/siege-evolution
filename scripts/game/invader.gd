class_name Invader
extends Node2D
## One invader moving toward the base. How it moves depends on its type:
## walkers follow their path around units, smashers stop to chew through
## units on their path, and fliers go in a straight line.
##
## Units can put effects on invaders: slow, stun, poison, and mark (takes
## extra damage). Each effect shows as a tint on the sprite.

var data: InvaderData
var board: Board
var hp: float
var alive := true
## False for boss minions, so bosses can't be farmed for coins.
var drops_coins := true
## Piñatas only: decides what's inside (same seed = same surprise).
var pinata_seed := 0
## The unit that hit it last (bounty capstones pay out on kills).
var last_hitter: Node = null
## Armor stripped by shredding capstones.
var armor_lost := 0
## Knockback can't shove the same invader again for this long.
const KNOCKBACK_COOLDOWN := 2.0
var _knockback_cooldown := 0.0
## The tiles this invader will walk through, ending at the base.
var path: Array[Vector2i] = []
## Which tile in `path` it is currently heading toward.
var path_index := 0
## True while tunneling (can't be hit). Burrowers dig in only once.
var underground := false
var _has_burrowed := false
## Burrowing visuals: the sprite sinks in over DIG_TIME, a bump of soil (or
## ripple, for boats) travels underground leaving a trail, and it pops back
## out over RISE_TIME. A dashed line shows where it will come up.
const DIG_TIME := 0.45
const RISE_TIME := 0.4
const TRAIL_LIFE := 1.4
const DIRT := Color(0.45, 0.3, 0.18)
const DIRT_LIGHT := Color(0.62, 0.45, 0.28)
const DIRT_DARK := Color(0.24, 0.15, 0.08)
const WATER_FOAM := Color(0.85, 0.95, 1.0)
const SHIELD_COLOR := Color(0.85, 0.9, 1.0)
var _dig_time := 0.0
var _rise_time := 0.0
var _spray_timer := 0.0
var _exit_pos := Vector2.ZERO
var _base_scale := Vector2.ONE
## Churned-up ground behind the tunneler: {pos (board space), age}.
var _trail: Array[Dictionary] = []
var _start_index := 0
var _emerge_index := 0
## Bombers look for a target once they've flown this share of the way...
const BOMB_AFTER := 0.3
## ...and only bomb units within this many tiles of them.
const BOMB_REACH := 2.5
var _has_bombed := false
var _bomb_timer := 0.0
var _flight_start := Vector2.ZERO
var _blink_timer := 0.0
## Tiles walked so far (spillers splash goo every few tiles).
var _tiles_walked := 0

## Jumpers crouch for this long before each hop.
const HOP_PAUSE := 0.45
var _hopping := false
var _hop_wait := 0.0
var _hop_length := 0.0

# Active effects. Each has a strength and the seconds it has left.
var slow_amount := 0.0
var slow_time := 0.0
var stun_time := 0.0
var poison_dps := 0.0
var poison_time := 0.0
var poison_spreads := false
var mark_bonus := 0.0
var mark_time := 0.0

const POISON_STACK_LIMIT := 2.5

var _minion_timer := 0.0
var _sprite: Sprite2D
## Every enemy gets a thin red edge (shaders/enemy_outline.gdshader) so it
## never looks like one of the player's units.
const OUTLINE_SHADER := preload("res://shaders/enemy_outline.gdshader")
## 1.0 = solid red edge, lower = softer.
const OUTLINE_STRENGTH := 1.0
var _outline: ShaderMaterial
## Plays the move animation when the invader has one (see StripPlayer).
var _strips := StripPlayer.new()
## Seconds left on the white "just got hit" flash.
var _hit_flash := 0.0
## Each invader bobs at its own rhythm while walking.
var _bob_offset := randf() * TAU


func setup(p_data: InvaderData, p_board: Board, start: Vector2, p_path: Array[Vector2i], p_index: int) -> void:
	data = p_data
	board = p_board
	hp = data.max_hp
	position = start
	path = p_path
	path_index = p_index
	_start_index = p_index
	_flight_start = start
	_minion_timer = data.minion_interval
	_blink_timer = data.blink_interval
	_sprite = Sprite2D.new()
	_sprite.texture = data.texture
	_outline = ShaderMaterial.new()
	_outline.shader = OUTLINE_SHADER
	_outline.set_shader_parameter("outline_color", Color(1.0, 0.18, 0.18, OUTLINE_STRENGTH))
	_sprite.material = _outline
	var size := 1.75 if data.is_boss else 1.0
	if data.anim_move:
		# Strips are drawn at 64x64 per frame; shrink them to the 16x16 tile.
		add_child(_strips)
		_strips.start_loop(_sprite, data.anim_move, StripPlayer.ACTION_FPS)
		size *= float(Board.TILE) / data.anim_move.get_height()
	_sprite.scale = Vector2(size, size)
	_base_scale = _sprite.scale
	add_child(_sprite)
	# Fliers are drawn above everything else on the board.
	z_index = 5 if is_flying() else 1


func is_flying() -> bool:
	return data.movement == InvaderData.Movement.FLIER


## Roughly how many tiles are left before this invader reaches the base.
## Attackers use this to target whoever is most dangerous.
func distance_to_base() -> float:
	if is_flying() or path_index >= path.size():
		return position.distance_to(board.cell_center(board.base_cell)) / Board.TILE
	var to_next := position.distance_to(board.cell_center(path[path_index])) / Board.TILE
	return (path.size() - 1 - path_index) + to_next


## A hit from a unit. Armor reduces each hit unless it pierces.
func take_damage(amount: float, pierce := false) -> void:
	if not alive:
		return
	var armor := maxi(0, data.armor - armor_lost)
	if not pierce and armor > 0:
		amount = max(1.0, amount - armor)
	if mark_time > 0.0:
		amount *= 1.0 + mark_bonus
	hp -= amount
	_hit_flash = 0.08
	queue_redraw()
	if hp <= 0.0:
		alive = false
		board.on_invader_killed(self)


func apply_slow(amount: float, duration: float) -> void:
	# A weaker slow never replaces a stronger one that's still running.
	if amount >= slow_amount or slow_time <= 0.0:
		slow_amount = amount
	slow_time = max(slow_time, duration)


func apply_stun(duration: float) -> void:
	# Bosses shrug off most of a stun.
	stun_time = max(stun_time, duration * (0.3 if data.is_boss else 1.0))


## Poison stacks: each new dose adds on top of what's already there, up to
## 2.5 times the strength of the dose.
func apply_poison(dps: float, duration: float, spreads: bool) -> void:
	var current := poison_dps if poison_time > 0.0 else 0.0
	poison_dps = max(current, min(current + dps, dps * POISON_STACK_LIMIT))
	poison_time = max(poison_time, duration)
	poison_spreads = poison_spreads or spreads


## Permanently strips armor (down to 0).
func shred_armor(amount: int) -> void:
	armor_lost = mini(armor_lost + amount, data.armor)


## Shoves a ground invader back along its route. Bosses, fliers and
## tunneling invaders can't be shoved, and nothing gets shoved twice in a row.
func knock_back(tiles: int) -> void:
	if data.is_boss or is_flying() or underground or _knockback_cooldown > 0.0 or path.is_empty():
		return
	_knockback_cooldown = KNOCKBACK_COOLDOWN
	var landing := maxi(0, mini(path_index, path.size()) - 1 - tiles)
	position = board.cell_center(path[landing])
	path_index = landing + 1
	_hopping = false
	_sprite.position.y = 0.0


func apply_mark(bonus: float, duration: float) -> void:
	mark_bonus = max(mark_bonus if mark_time > 0.0 else 0.0, bonus)
	mark_time = max(mark_time, duration)


## Walkers find a new route when the maze changes (a smasher broke a unit).
func repath() -> void:
	if data.movement != InvaderData.Movement.PATHER or path_index >= path.size() or underground:
		return
	var new_path := board.route_for(data, path[path_index])
	if not new_path.is_empty():
		path = new_path
		path_index = 0


func _process(delta: float) -> void:
	if not alive:
		return
	_update_effects(delta)
	if not alive:
		return
	if data.minion and data.minion_interval > 0.0:
		_minion_timer -= delta
		if _minion_timer <= 0.0:
			_minion_timer = data.minion_interval
			board.spawn_from(self, data.minion, data.minion_count, false, data.minion_throw)
	if stun_time > 0.0:
		return
	if data.blink_interval > 0.0 and not underground:
		_blink_timer -= delta
		if _blink_timer <= 0.0:
			_blink_timer = data.blink_interval
			_blink()
	var speed := data.speed * (1.0 - slow_amount if slow_time > 0.0 else 1.0)
	if is_flying():
		_fly(speed * delta)
	else:
		_walk(speed * delta, delta)


func _update_effects(delta: float) -> void:
	slow_time = max(0.0, slow_time - delta)
	stun_time = max(0.0, stun_time - delta)
	mark_time = max(0.0, mark_time - delta)
	_knockback_cooldown = max(0.0, _knockback_cooldown - delta)
	if data.regen > 0.0:
		hp = min(hp + data.regen * delta, data.max_hp)
	if poison_time > 0.0:
		poison_time = max(0.0, poison_time - delta)
		take_damage(poison_dps * delta, true)

	# Tint shows the strongest active effect.
	var tint := Color.WHITE
	if poison_time > 0.0:
		tint = Color(0.6, 1.0, 0.5)
	if slow_time > 0.0:
		tint = Color(0.6, 0.8, 1.0)
	if stun_time > 0.0:
		tint = Color(1.0, 1.0, 0.5)
	if _hit_flash > 0.0:
		_hit_flash -= delta
		tint = Color(2.2, 2.2, 2.2)  # brighter than white = a flash
	_sprite.modulate = tint
	# Walkers bob as they move (fliers glide, hops have their own arc).
	_update_burrow_visuals(delta)
	if not is_flying() and not _hopping and stun_time <= 0.0 and _dig_time <= 0.0 and _rise_time <= 0.0:
		_sprite.position.y = sin(Time.get_ticks_msec() / 90.0 + _bob_offset) * 0.8
	queue_redraw()


func _fly(tiles: float) -> void:
	var target := board.cell_center(board.base_cell)
	position = position.move_toward(target, tiles * Board.TILE)
	# Bosses with a bomb interval re-arm after each bomb.
	if _has_bombed and data.bomb_interval > 0.0:
		_bomb_timer -= tiles / maxf(0.01, data.speed)
		if _bomb_timer <= 0.0:
			_has_bombed = false
	if data.bomb_damage > 0.0 and not _has_bombed:
		var flown := _flight_start.distance_to(position) / maxf(1.0, _flight_start.distance_to(target))
		if flown >= BOMB_AFTER:
			_try_bomb()
	if position.distance_to(target) < 0.5:
		alive = false
		board.on_invader_reached_base(self)


func _walk(tiles: float, delta: float) -> void:
	var step := tiles * Board.TILE
	if underground:
		_tunnel(step)
		return
	while step > 0.0:
		if path_index >= path.size():
			alive = false
			board.on_invader_reached_base(self)
			return
		if _should_burrow():
			_start_tunnel()
			return
		var next_cell := path[path_index]
		# Smashers stop and chew on any unit standing on their next tile.
		if data.movement == InvaderData.Movement.SMASHER:
			var blocker := board.intact_unit_at(next_cell)
			if blocker:
				blocker.take_damage(data.smash_damage * delta, self)
				return
		var target := board.cell_center(next_cell)
		var distance := position.distance_to(target)
		# A waypoint 2 tiles away is a hop: crouch, then leap in an arc.
		if data.jumps and not _hopping and distance > Board.TILE * 1.5:
			_hopping = true
			_hop_wait = HOP_PAUSE
			_hop_length = distance
		if _hopping and _hop_wait > 0.0:
			_hop_wait -= delta
			return
		if distance > step:
			position = position.move_toward(target, step)
			_update_hop_arc(target)
			return
		position = target
		step -= distance
		path_index += 1
		_tiles_walked += 1
		if data.spill_every > 0 and _tiles_walked % data.spill_every == 0:
			board.spill(next_cell, data.spill_slow)
		if _hopping:
			_hopping = false
			_sprite.position.y = 0.0


func _update_hop_arc(target: Vector2) -> void:
	if not _hopping:
		return
	var progress := 1.0 - position.distance_to(target) / _hop_length
	_sprite.position.y = -sin(progress * PI) * 6.0


## Teleports forward along the route, skipping `blink_distance` tiles (but
## never straight onto the base).
func _blink() -> void:
	if path.is_empty() or path_index >= path.size() - 1:
		return
	var landing := mini(path_index + data.blink_distance - 1, path.size() - 2)
	if landing < path_index:
		return
	board.fx.add_pulse(position, Board.TILE * 0.8, Color(0.7, 0.4, 1.0))
	Sfx.play("blink")
	position = board.cell_center(path[landing])
	path_index = landing + 1
	board.fx.add_pulse(position, Board.TILE * 0.8, Color(0.7, 0.4, 1.0))


## Drops the bomb on the most valuable unit in reach (if any).
func _try_bomb() -> void:
	var best: Unit = null
	var best_value := 0
	for cell in board.units:
		var unit: Unit = board.units[cell]
		if unit.destroyed or unit.position.distance_to(position) > BOMB_REACH * Board.TILE:
			continue
		var value := unit.total_cost()
		if value > best_value:
			best_value = value
			best = unit
	if best:
		_has_bombed = true
		_bomb_timer = data.bomb_interval
		board.drop_bomb(position, best.cell, data.bomb_damage)


func _should_burrow() -> bool:
	return (data.burrow_after > 0 and not _has_burrowed
		and path_index - _start_index >= data.burrow_after
		and path_index + 1 < path.size() - 1)


## Digs in: heads straight for a tile further along the route, underground.
## (It can't be hit from this moment; the sinking is just the animation.)
func _start_tunnel() -> void:
	_has_burrowed = true
	underground = true
	_emerge_index = mini(path_index + data.burrow_length, path.size() - 2)
	_exit_pos = board.cell_center(path[_emerge_index])
	_dig_time = DIG_TIME
	board.ground_fx.add_hole(position, data.naval)
	queue_redraw()


func _tunnel(step: float) -> void:
	var target := _exit_pos
	position = position.move_toward(target, step)
	# Leave churned ground (or bubbles) behind every few pixels.
	if _trail.is_empty() or _trail[-1].pos.distance_to(position) > 3.0:
		_trail.append({"pos": position, "age": 0.0})
	if position.distance_to(target) < 0.5:
		position = target
		underground = false
		path_index = _emerge_index + 1
		_surface()
	queue_redraw()


## Bursts back out of the ground with a spray of dirt (or a splash).
func _surface() -> void:
	_dig_time = 0.0
	_rise_time = RISE_TIME
	_sprite.visible = true
	var color := WATER_FOAM if data.naval else DIRT_LIGHT
	board.fx.add_puff(position + Vector2(-3, 3), color)
	board.fx.add_puff(position + Vector2(3, 3), color)
	board.fx.add_pulse(position, Board.TILE, color)
	board.ground_fx.add_hole(position, data.naval)


## Runs the sink, trail and pop-up animations.
func _update_burrow_visuals(delta: float) -> void:
	for point in _trail:
		point.age += delta
	if not _trail.is_empty() and _trail[0].age > TRAIL_LIFE:
		_trail = _trail.filter(func(point): return point.age <= TRAIL_LIFE)
	if _dig_time > 0.0:
		_dig_time -= delta
		var left := maxf(0.0, _dig_time / DIG_TIME)  # 1 -> 0 as it sinks
		_sprite.scale = Vector2(_base_scale.x, _base_scale.y * left)
		_sprite.position.y = (1.0 - left) * 6.0
		_spray_timer -= delta
		if _spray_timer <= 0.0:
			_spray_timer = 0.1
			board.fx.add_puff(position + Vector2(0, 4), WATER_FOAM if data.naval else DIRT_LIGHT)
		if _dig_time <= 0.0:
			_sprite.visible = false
			_sprite.scale = _base_scale
			_sprite.position.y = 0.0
	elif _rise_time > 0.0:
		_rise_time -= delta
		var progress := 1.0 - maxf(0.0, _rise_time / RISE_TIME)  # 0 -> 1
		_sprite.position.y = -sin(progress * PI) * 6.0
		_sprite.scale = _base_scale * Vector2(1.0 + 0.2 * (1.0 - progress), 0.8 + 0.2 * progress)
		if _rise_time <= 0.0:
			_sprite.scale = _base_scale
			_sprite.position.y = 0.0


func _draw() -> void:
	_draw_trail()
	if underground and _dig_time <= 0.0:
		_draw_tunneler()
		return
	var half := 9.0 if data.is_boss else 6.0
	if hp < data.max_hp:
		draw_rect(Rect2(-half, -half - 4, half * 2, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-half, -half - 4, half * 2 * hp / data.max_hp, 2), Color(1, 0.3, 0.3))
	if mark_time > 0.0:
		draw_circle(Vector2(half - 1, -half + 1), 1.5, Color(1, 0.2, 0.2))


## Churned dirt (or bubbles) left behind the tunneler, fading out.
func _draw_trail() -> void:
	for point in _trail:
		var fade: float = 1.0 - point.age / TRAIL_LIFE
		var spot: Vector2 = point.pos - position + Vector2(0, 3)  # board space -> ours
		if data.naval:
			draw_arc(spot, 1.2 + point.age, 0, TAU, 8, Color(WATER_FOAM, 0.7 * fade), 0.5)
		else:
			draw_circle(spot, 2.4, Color(DIRT_DARK, 0.85 * fade))
			draw_circle(spot + Vector2(-0.8, -0.6), 1.0, Color(DIRT_LIGHT, 0.85 * fade))


## While underground: a wobbling bump of soil (or a ripple), a shield
## showing it can't be hit, and a dashed line to where it will come up.
func _draw_tunneler() -> void:
	var exit := _exit_pos - position  # board space -> ours
	if exit.length() > 2.0:
		draw_dashed_line(Vector2(0, 3), exit + Vector2(0, 3), Color(1, 0.4, 0.35, 0.75), 0.75, 2.0)
	var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 150.0)
	draw_arc(exit + Vector2(0, 3), 4.0 + 1.5 * pulse, 0, TAU, 16, Color(1, 0.35, 0.3, 0.45 + 0.35 * pulse), 1.0)
	var wobble := sin(Time.get_ticks_msec() / 70.0) * 0.6
	if data.naval:
		draw_arc(Vector2(0, 3), 4.5 + wobble, 0, TAU, 16, Color(WATER_FOAM, 0.8), 1.0)
		draw_arc(Vector2(0, 3), 2.0, 0, TAU, 12, Color(WATER_FOAM, 0.5), 0.5)
	else:
		draw_circle(Vector2(0, 3), 5.0, DIRT_DARK)
		draw_circle(Vector2(0, 3), 4.2, DIRT)
		draw_circle(Vector2(-2 + wobble, 2), 2.0, DIRT_LIGHT)
		draw_circle(Vector2(2, 1.5 - wobble), 1.4, DIRT_LIGHT)
	_draw_shield(Vector2(0, -5))


## A tiny pixel shield: "can't be hit right now".
func _draw_shield(at: Vector2) -> void:
	var points := PackedVector2Array([at + Vector2(-2.5, -2.5), at + Vector2(2.5, -2.5),
		at + Vector2(2.5, 0.5), at + Vector2(0, 3), at + Vector2(-2.5, 0.5)])
	draw_colored_polygon(points, Color(0.1, 0.1, 0.15, 0.8))
	var inner := PackedVector2Array([at + Vector2(-1.7, -1.8), at + Vector2(1.7, -1.8),
		at + Vector2(1.7, 0.2), at + Vector2(0, 2), at + Vector2(-1.7, 0.2)])
	draw_colored_polygon(inner, SHIELD_COLOR)
