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
## Bosses are drawn this many times bigger than a normal invader (their
## 64x64 strips are scaled by height, so they keep the same detail).
const BOSS_SCALE := 2.0
const KNOCKBACK_COOLDOWN := 2.0
var _knockback_cooldown := 0.0
## The tiles this invader will walk through, ending at the base.
var path: Array[Vector2i] = []
## Which tile in `path` it is currently heading toward.
var path_index := 0
## Carries a relic: glows gold, and drops the relic when killed.
var carries_relic := false
const RELIC_GLOW := Color(1.0, 0.82, 0.3)
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
## Teleporters glow and show where they'll land for this long before a blink.
const BLINK_CHARGE := 0.6
const BLINK_COLOR := Color(0.7, 0.4, 1.0)
## Pieces from a split or a toss fly from their parent to their spot.
const TOSS_TIME := 0.35
var _toss_time := 0.0
var _toss_offset := Vector2.ZERO
## Seconds left on a grab wall's hold (draws a "grabbed" hand).
var _grab_time := 0.0
## How many poison doses are stacked (1-3 bubbles).
var _poison_doses := 0
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
	var size := BOSS_SCALE if data.is_boss else 1.0
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
		return position.distance_to(board.base_center()) / Board.TILE
	var to_next := position.distance_to(board.cell_center(path[path_index])) / Board.TILE
	return (path.size() - 1 - path_index) + to_next


## A hit from a unit. Armor reduces each hit unless it pierces.
## `flash` is false for damage over time (poison, zones), which ticks every
## frame: a constant white flash would hide the poison tint.
func take_damage(amount: float, pierce := false, flash := true) -> void:
	if not alive:
		return
	var armor := maxi(0, data.armor - armor_lost)
	if not pierce and armor > 0:
		amount = max(1.0, amount - armor)
	if mark_time > 0.0:
		amount *= 1.0 + mark_bonus
	hp -= amount
	if flash:
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
	_poison_doses = mini(3, (_poison_doses if poison_time > 0.0 else 0) + 1)
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
	var from := position
	position = board.cell_center(path[landing])
	# A white shove streak shows how far it was pushed back.
	board.fx.add_streak(from, position, Color.WHITE, 0.35)
	board.fx.add_puff(position, Color(0.9, 0.9, 0.9))
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
		take_damage(poison_dps * delta, true, false)

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
	# Teleporters flicker purple while charging up a blink.
	if data.blink_interval > 0.0 and _blink_timer < BLINK_CHARGE and not underground:
		tint = tint.lerp(BLINK_COLOR, 0.35 + 0.35 * sin(Time.get_ticks_msec() / 40.0))
	_sprite.modulate = tint
	_grab_time = maxf(0.0, _grab_time - delta)
	if poison_time <= 0.0:
		_poison_doses = 0
	_update_pose(delta)
	# Walkers bob as they move (fliers glide, hops have their own arc).
	_update_burrow_visuals(delta)
	if not is_flying() and not _hopping and stun_time <= 0.0 and _dig_time <= 0.0 and _rise_time <= 0.0 and _toss_time <= 0.0:
		_sprite.position.y = sin(Time.get_ticks_msec() / 90.0 + _bob_offset) * 0.8
	queue_redraw()


func _fly(tiles: float) -> void:
	var target := board.base_center()
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
	# Arrives as soon as it's over any base tile (like walkers do).
	var over := Vector2i((position / Board.TILE).floor())
	if position.distance_to(target) < 0.5 or board.is_base(over):
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
			board.fx.add_puff(position + Vector2(0, 5), Color(0.85, 0.78, 0.65))


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
	var from := position
	# A fading purple "ghost" where it was, a streak to where it went, and a
	# bright flash where it arrives.
	board.fx.add_puff(from, BLINK_COLOR)
	board.fx.add_pulse(from, Board.TILE * 0.8, BLINK_COLOR)
	Sfx.play("blink")
	position = board.cell_center(path[landing])
	path_index = landing + 1
	board.fx.add_streak(from, position, BLINK_COLOR)
	board.fx.add_pulse(position, Board.TILE * 1.3, BLINK_COLOR)
	board.fx.add_puff(position, Color(0.9, 0.8, 1.0))


## Where the next blink will land (for the charge-up preview).
func _blink_landing() -> Vector2:
	if path.is_empty() or path_index >= path.size() - 1:
		return position
	var landing := mini(path_index + data.blink_distance - 1, path.size() - 2)
	return board.cell_center(path[maxi(landing, path_index)])


## A piece of a split (or a tossed minion) flies from `from` to its own spot.
func toss_in(from: Vector2) -> void:
	_toss_offset = from - position
	_toss_time = TOSS_TIME


## Called by a grab wall: shows a gold "grabbed" hand while it's held.
func show_grabbed(seconds: float) -> void:
	_grab_time = seconds * (0.3 if data.is_boss else 1.0)


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


## Crouching before a hop, and flying in after a split or toss.
func _update_pose(delta: float) -> void:
	if _dig_time > 0.0 or _rise_time > 0.0:
		return
	if _toss_time > 0.0:
		_toss_time = maxf(0.0, _toss_time - delta)
		var left := _toss_time / TOSS_TIME  # 1 -> 0
		_sprite.position = _toss_offset * left + Vector2(0, -sin(left * PI) * 5.0)
		_sprite.scale = _base_scale * (1.0 - 0.5 * left)
		if _toss_time <= 0.0:
			_sprite.position = Vector2.ZERO
			_sprite.scale = _base_scale
		return
	var crouching := _hopping and _hop_wait > 0.0
	_sprite.scale = _base_scale * (Vector2(1.12, 0.84) if crouching else Vector2.ONE)


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
	var half := 10.5 if data.is_boss else 6.0
	if carries_relic:
		# A pulsing gold aura and a little gem above its head.
		var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 160.0)
		draw_circle(Vector2.ZERO, half + 3.0, Color(RELIC_GLOW, 0.18 + 0.15 * pulse))
		draw_arc(Vector2.ZERO, half + 3.0 + pulse, 0, TAU, 20, Color(RELIC_GLOW, 0.8), 1.0)
		var gem := Vector2(0, -half - 5.0 - pulse)
		draw_colored_polygon(PackedVector2Array([gem + Vector2(0, -3), gem + Vector2(2.5, 0),
			gem + Vector2(0, 3), gem + Vector2(-2.5, 0)]), RELIC_GLOW)
		draw_colored_polygon(PackedVector2Array([gem + Vector2(0, -2), gem + Vector2(1, 0),
			gem + Vector2(0, 0.5), gem + Vector2(-1, 0)]), Color.WHITE)
	_draw_move_hints(half)
	if hp < data.max_hp:
		draw_rect(Rect2(-half, -half - 4, half * 2, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-half, -half - 4, half * 2 * hp / data.max_hp, 2), Color(1, 0.3, 0.3))
	_draw_status(half)


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


## Previews for special moves: where a teleporter will land, where a jumper
## will land, and a shadow under a jumper in mid-air.
func _draw_move_hints(half: float) -> void:
	if data.blink_interval > 0.0 and _blink_timer < BLINK_CHARGE and not underground:
		var charge := 1.0 - _blink_timer / BLINK_CHARGE  # 0 -> 1
		draw_arc(Vector2.ZERO, half + 4.0 * (1.0 - charge), 0, TAU, 20, Color(BLINK_COLOR, 0.4 + 0.5 * charge), 1.0)
		var landing := _blink_landing() - position
		if landing.length() > 2.0:
			draw_dashed_line(Vector2.ZERO, landing, Color(BLINK_COLOR, 0.6 * charge), 0.75, 2.0)
			draw_circle(landing, 3.0 + 2.0 * charge, Color(BLINK_COLOR, 0.3 * charge))
	if _hopping and path_index < path.size():
		var target := board.cell_center(path[path_index]) - position
		if _hop_wait > 0.0:
			_draw_brackets(target, Color(1, 0.65, 0.2, 0.9))
		else:
			# Shadow on the ground under the leaping sprite.
			draw_set_transform(Vector2(0, 5), 0.0, Vector2(1.0, 0.4))
			draw_circle(Vector2.ZERO, 5.0, Color(0, 0, 0, 0.35))
			draw_set_transform(Vector2.ZERO)


## Corner brackets around a tile, centered on `at`.
func _draw_brackets(at: Vector2, color: Color) -> void:
	var size := Board.TILE * 0.5 - 1.0
	for corner in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
		var tip: Vector2 = at + corner * size
		draw_line(tip, tip - Vector2(corner.x * 3.0, 0), color, 1.0)
		draw_line(tip, tip - Vector2(0, corner.y * 3.0), color, 1.0)


## Icons for what the player's units are doing to this invader.
func _draw_status(half: float) -> void:
	var now := Time.get_ticks_msec() / 1000.0
	# Stunned: two little stars circling above its head.
	if stun_time > 0.0:
		for i in 2:
			var angle := now * 6.0 + i * PI
			var spot := Vector2(cos(angle) * 4.0, -half - 2.0 + sin(angle) * 1.5)
			draw_rect(Rect2(spot - Vector2(1, 0), Vector2(3, 1)), Color(1, 0.95, 0.4))
			draw_rect(Rect2(spot - Vector2(0, 1), Vector2(1, 3)), Color(1, 0.95, 0.4))
	# Slowed: pale blue frost specks drifting around it.
	if slow_time > 0.0:
		for i in 3:
			var angle := now * 1.5 + i * TAU / 3.0
			var spot := Vector2(cos(angle) * (half + 1.0), sin(angle) * (half - 1.0))
			draw_rect(Rect2(spot, Vector2(1.5, 1.5)), Color(0.75, 0.9, 1.0, 0.9))
	# Poisoned: green bubbles rising, one per stacked dose.
	for i in _poison_doses:
		var rise := fmod(now * 0.9 + i * 0.33, 1.0)
		var spot := Vector2(-3.0 + i * 3.0, -half * rise)
		draw_circle(spot, 1.6, Color(0.45, 1.0, 0.35, 0.85 * (1.0 - rise)))
		draw_circle(spot + Vector2(-0.5, -0.5), 0.5, Color(1, 1, 1, 0.8 * (1.0 - rise)))
	# Marked: a red target reticle.
	if mark_time > 0.0:
		var r := half + 2.0
		draw_arc(Vector2.ZERO, r, 0, TAU, 24, Color(1, 0.25, 0.25, 0.85), 0.75)
		for dir in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
			draw_line(dir * (r - 2.0), dir * (r + 1.5), Color(1, 0.25, 0.25), 1.0)
	# Grabbed by a grab wall: a gold hand above it.
	if _grab_time > 0.0:
		var top := Vector2(0, -half - 4.0)
		draw_rect(Rect2(top + Vector2(-2.5, 0), Vector2(5, 3)), Palette.GOLD)
		for x in [-2.5, -1.0, 0.5, 2.0]:
			draw_rect(Rect2(top + Vector2(x, -2), Vector2(1, 2)), Palette.GOLD)
