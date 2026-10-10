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
	if data.is_boss:
		_sprite.scale = Vector2(1.75, 1.75)
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
	if not is_flying() and not _hopping and stun_time <= 0.0:
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
		board.bomb(best.cell, data.bomb_damage)


func _should_burrow() -> bool:
	return (data.burrow_after > 0 and not _has_burrowed
		and path_index - _start_index >= data.burrow_after
		and path_index + 1 < path.size() - 1)


## Digs in: heads straight for a tile further along the route, underground.
func _start_tunnel() -> void:
	_has_burrowed = true
	underground = true
	_emerge_index = mini(path_index + data.burrow_length, path.size() - 2)
	_sprite.visible = false
	queue_redraw()


func _tunnel(step: float) -> void:
	var target := board.cell_center(path[_emerge_index])
	position = position.move_toward(target, step)
	if position.distance_to(target) < 0.5:
		position = target
		underground = false
		path_index = _emerge_index + 1
		_sprite.visible = true
	queue_redraw()


func _draw() -> void:
	if underground:
		# A little moving mound of dirt.
		draw_circle(Vector2(0, 3), 4.0, Color(0.45, 0.3, 0.18))
		draw_circle(Vector2(-2, 2), 1.5, Color(0.6, 0.42, 0.25))
		return
	var half := 9.0 if data.is_boss else 6.0
	if hp < data.max_hp:
		draw_rect(Rect2(-half, -half - 4, half * 2, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-half, -half - 4, half * 2 * hp / data.max_hp, 2), Color(1, 0.3, 0.3))
	if mark_time > 0.0:
		draw_circle(Vector2(half - 1, -half + 1), 1.5, Color(1, 0.2, 0.2))
