class_name Unit
extends Node2D
## A unit the player placed on the board. Every unit blocks its tile, and
## any unit with an attack or effect uses it on invaders during waves.

var data: UnitData
## The unit as originally placed (before any evolution).
var base_data: UnitData
var cell: Vector2i
var board: Board
var hp: float
## True once a smasher breaks it. It stays broken until the wave ends.
var destroyed := false
## Goo from a spiller: attacks this much slower (0.4 = 40%) until repaired.
var sticky := 0.0

# Bookkeeping for refunds (managed by the game).
## Which build round it was placed in (the number of waves started before).
var placed_round := 0
var from_hand := false
## Which build round it evolved in (-1 = not evolved).
var evolved_round := -1
## Its first evolution (kept for refunds once it becomes a capstone).
var tier1_data: UnitData = null
## Which build round it became a capstone in (-1 = not yet).
var capstone_round := -1

## Regeneration pauses for this many seconds after taking damage, so a
## healing wall can't hold off a smasher forever.
const REGEN_PAUSE := 2.0

var _cooldown := 0.0
var _regen_pause := 0.0
var _sprite: Sprite2D
## Plays animation strips when the unit has them (see StripPlayer).
var _strips := StripPlayer.new()
## Strips are drawn at 64x64 per frame; this shrinks them to the 16x16 tile.
var _art_scale := 1.0
## Units are drawn a bit bigger than their tile's art box, so they fill it.
const ART_BOOST := 1.12
## How far above its tile a new unit starts before it drops into place.
const DROP_HEIGHT := 7.0
const SHADOW_COLOR := Color(0, 0, 0, 0.45)
const PAD_COLOR := Color(0, 0, 0, 0.18)
const PAD_EDGE := Color(0, 0, 0, 0.35)
const DUST_COLOR := Color(0.85, 0.78, 0.65)
## Draws the capstone star over animated art (still art has it built in).
var _star: CapstoneStar
## Capstone mechanics: grab cooldown, and whether "rebuild once" was used.
const GRAB_COOLDOWN := 3.0
var _grab_cooldown := 0.0
var _rebuilt := false
## Chain hits jump this far, losing this much damage per jump.
const CHAIN_RANGE := 2.0
const CHAIN_FALLOFF := 0.7


func setup(p_data: UnitData, p_cell: Vector2i, p_board: Board) -> void:
	data = p_data
	base_data = p_data
	cell = p_cell
	board = p_board
	hp = data.max_hp
	position = board.cell_center(cell)
	_sprite = Sprite2D.new()
	add_child(_sprite)
	add_child(_strips)
	_star = CapstoneStar.new()
	add_child(_star)
	_update_sprite()
	_drop_in()


## Placing: the unit falls onto its tile, squashes as it lands and kicks up
## a little ring of dust, so it feels heavy.
func _drop_in() -> void:
	var rest := Vector2.ONE * _art_scale
	_sprite.position.y = -DROP_HEIGHT
	var tween := create_tween()
	tween.tween_property(_sprite, "position:y", 0.0, 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(_land)
	tween.tween_property(_sprite, "scale", rest * Vector2(1.18, 0.82), 0.05)
	tween.tween_property(_sprite, "scale", rest, 0.18).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## The moment of landing: dust puffs out from the unit's feet.
func _land() -> void:
	board.fx.add_puff(position + Vector2(-3, 6), DUST_COLOR)
	board.fx.add_puff(position + Vector2(3, 6), DUST_COLOR)
	board.fx.add_pulse(position + Vector2(0, 6), Board.TILE * 0.9, DUST_COLOR)


## A quick bounce when the unit evolves.
func _pop() -> void:
	_sprite.scale = Vector2.ONE * 0.4 * _art_scale
	create_tween().tween_property(_sprite, "scale", Vector2.ONE * _art_scale, 0.25) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## Units on water use their water look (nets and mines); others play their
## idle animation if they have one, else show their still sprite.
func _update_sprite() -> void:
	var on_water := board.water.has(cell) and data.water_texture != null
	var animated := data.anim_idle != null and not on_water
	if animated:
		_strips.start_loop(_sprite, data.anim_idle)
		_art_scale = float(Board.TILE) / data.anim_idle.get_height() * ART_BOOST
	else:
		_strips.start_loop(_sprite, null)
		_sprite.texture = data.water_texture if on_water else data.texture
		_sprite.hframes = 1
		_sprite.frame = 0
		_art_scale = ART_BOOST
	_sprite.scale = Vector2.ONE * _art_scale
	_star.visible = animated and is_capstone()


func is_evolved() -> bool:
	return data != base_data


func is_capstone() -> bool:
	return data.tier == 2


## Everything spent on this unit (what bombers look for).
func total_cost() -> int:
	var total := base_data.cost
	if tier1_data:
		total += tier1_data.cost
	if is_capstone():
		total += data.cost
	return total


## Turns this unit into one of its evolutions, at full health.
func evolve(into: UnitData) -> void:
	if into.tier == 1:
		tier1_data = into
	data = into
	hp = data.max_hp
	_update_sprite()
	_pop()
	board.fx.add_pulse(position, Board.TILE * 1.2, Palette.GOLD)
	board.fx.add_puff(position, Palette.GOLD)
	queue_redraw()


## Damage from a smasher or a bomb. Reflect bounces part of it back at the
## attacker; a neighbor's shield aura softens it; grab walls stun the biter.
func take_damage(amount: float, attacker: Invader = null) -> void:
	if destroyed:
		return
	amount *= 1.0 - board.aura_at(cell).shield
	if attacker and data.reflect > 0.0:
		attacker.take_damage(amount * data.reflect, true)
	if attacker and data.grab_stun > 0.0 and _grab_cooldown <= 0.0:
		attacker.apply_stun(data.grab_stun)
		attacker.show_grabbed(data.grab_stun)
		_grab_cooldown = GRAB_COOLDOWN
		board.fx.add_pulse(position, Board.TILE * 0.9, Palette.GOLD)
	hp -= amount
	_regen_pause = REGEN_PAUSE
	if hp <= 0.0:
		# "Rebuild once": springs back the first time it breaks each wave.
		if data.rebuild and not _rebuilt:
			_rebuilt = true
			hp = data.max_hp
			board.fx.add_pulse(position, Board.TILE * 1.2, Palette.GOOD)
			queue_redraw()
			return
		hp = 0.0
		destroyed = true
		visible = false
		if data.explode_damage > 0.0:
			board.explode(position, data.explode_damage, data)
		board.on_unit_destroyed(self)
	queue_redraw()


## Covered in a spiller's goo: attacks slower until the wave ends.
## A weaker spill never replaces a stronger one.
func make_sticky(amount: float) -> void:
	if board.aura_at(cell).cleanse:
		return
	if amount > sticky:
		sticky = amount
		queue_redraw()


## Back to full health and clean of goo (called between waves).
func restore() -> void:
	hp = data.max_hp
	destroyed = false
	sticky = 0.0
	_rebuilt = false
	_grab_cooldown = 0.0
	visible = true
	_cooldown = 0.0
	queue_redraw()


func _process(delta: float) -> void:
	if is_capstone():
		queue_redraw()  # the glow pulses
	if destroyed or not board.wave_active:
		return
	_grab_cooldown = max(0.0, _grab_cooldown - delta)
	_regen_pause = max(0.0, _regen_pause - delta)
	if data.regen > 0.0 and hp < data.max_hp and _regen_pause <= 0.0:
		hp = min(hp + data.regen * delta, data.max_hp)
		queue_redraw()
	if not data.can_attack():
		return
	_cooldown -= delta
	if _cooldown > 0.0:
		return
	if _attack():
		_play_attack()
		_cooldown = data.attack_interval / speed_multiplier()


## How much faster than normal this unit attacks right now (1.0 = normal).
## Also shown to the player as its current shots per second.
func speed_multiplier() -> float:
	# Swarm units attack faster for every unit packed around them.
	var speed_up := 1.0 + data.adjacency_bonus * board.neighbor_count(cell)
	# A neighbor's speed aura (capstones) helps too.
	speed_up += board.aura_at(cell).speed
	# Goo slows it down (0.4 sticky = attacks at 60% of normal speed).
	speed_up *= 1.0 - sticky
	return speed_up


## Plays the attack strip once, fast enough to finish before the next shot.
func _play_attack() -> void:
	if data.anim_attack == null or (board.water.has(cell) and data.water_texture != null):
		return
	var frames := StripPlayer.frames_in(data.anim_attack)
	var fps := maxf(StripPlayer.ACTION_FPS, frames / (data.attack_interval * 0.9))
	_strips.play_once(_sprite, data.anim_attack, fps)


## Attacks if anything is in range. Returns false if there was nothing to hit.
func _attack() -> bool:
	if data.attack_mode == UnitData.AttackMode.PULSE:
		var targets := _invaders_in_range(position, data.attack_range)
		if targets.is_empty():
			return false
		board.fx.add_pulse(position, data.attack_range * Board.TILE, data.shot_color)
		for invader in targets:
			_hit(invader)
		# Pulse units with a zone keep a patch on the ground around themselves.
		if data.zone_kind != "":
			board.add_zone(position, data, self)
		return true

	# Multishot fires at several targets; most units fire at one.
	var targets := _find_targets(maxi(1, data.multishot))
	if targets.is_empty():
		return false
	Sfx.play("shoot", 0.15)
	for target in targets:
		_shoot(target)
	return true


## One shot at one target, with every effect a shot can carry: splash, line
## pierce, chain hits and lingering zones.
func _shoot(target: Invader) -> void:
	var victims: Array[Invader] = [target]
	if data.line_pierce:
		# The shot carries on through the target to the end of its range.
		var direction := position.direction_to(target.position)
		var end := position + direction * (data.attack_range + 1.0) * Board.TILE
		board.fx.add_shot(position, end, data.shot_color)
		for other in board.invaders:
			if other != target and _can_target(other) \
					and Geometry2D.get_closest_point_to_segment(other.position, position, end).distance_to(other.position) < Board.TILE * 0.5:
				victims.append(other)
	else:
		board.fx.add_shot(position, target.position, data.shot_color)
	if data.splash_radius > 0.0:
		# The blast area: a soft filled flash plus the expanding ring.
		board.fx.add_blast(target.position, data.splash_radius * Board.TILE, data.shot_color)
		board.fx.add_pulse(target.position, data.splash_radius * Board.TILE, data.shot_color)
		for other in _invaders_in_range(target.position, data.splash_radius):
			if not victims.has(other):
				victims.append(other)
	if data.zone_kind != "":
		board.add_zone(target.position, data, self)
	for invader in victims:
		_hit(invader)
	# Chain hits jump from the target to the nearest invaders not yet hit.
	var from := target.position
	var factor := 1.0
	for jump in data.chain_count:
		var next: Invader = null
		for other in _invaders_in_range(from, CHAIN_RANGE):
			if not victims.has(other) and (next == null or from.distance_to(other.position) < from.distance_to(next.position)):
				next = other
		if next == null:
			break
		factor *= CHAIN_FALLOFF
		board.fx.add_bolt(from, next.position, data.shot_color.lightened(0.3))
		victims.append(next)
		_hit(next, factor)
		from = next.position


func _hit(invader: Invader, factor := 1.0) -> void:
	if not invader.alive:
		return
	invader.last_hitter = self
	if data.armor_shred > 0:
		invader.shred_armor(data.armor_shred)
	if data.mark_bonus > 0.0:
		invader.apply_mark(data.mark_bonus, data.mark_duration)
	if data.slow > 0.0:
		invader.apply_slow(data.slow, data.slow_duration)
	if data.stun_duration > 0.0:
		invader.apply_stun(data.stun_duration)
	if data.poison_dps > 0.0:
		invader.apply_poison(data.poison_dps * factor, data.poison_duration, data.poison_spreads)
	if data.damage > 0.0:
		invader.take_damage(data.damage * factor, data.pierce)
	if not invader.alive:
		return
	# Execute: finishes off any wounded non-boss.
	if data.execute_below > 0.0 and not invader.data.is_boss \
			and invader.hp <= invader.data.max_hp * data.execute_below:
		board.fx.add_pulse(invader.position, Board.TILE * 0.7, Palette.HEART)
		invader.take_damage(invader.hp + 1.0, true)
		return
	if data.knockback > 0:
		invader.knock_back(data.knockback)


func _can_target(invader: Invader) -> bool:
	return invader.alive and not invader.underground and (data.hits_air or not invader.is_flying())


func _invaders_in_range(center: Vector2, tiles: float) -> Array[Invader]:
	var result: Array[Invader] = []
	for invader in board.invaders:
		if _can_target(invader) and center.distance_to(invader.position) <= tiles * Board.TILE:
			result.append(invader)
	return result


## Picks the `count` invaders in range that are closest to the base.
func _find_targets(count: int) -> Array[Invader]:
	var in_range := _invaders_in_range(position, data.attack_range)
	in_range.sort_custom(func(a, b): return a.distance_to_base() < b.distance_to_base())
	return in_range.slice(0, count)


func _draw() -> void:
	# A faint pad on the tile and a soft shadow under the unit, so it looks
	# planted on the ground instead of floating on the art.
	if not destroyed:
		draw_rect(Rect2(-7.5, -7.5, 15, 15), PAD_COLOR)
		draw_rect(Rect2(-7.5, -7.5, 15, 15), PAD_EDGE, false, 0.5)
		draw_set_transform(Vector2(0, 6.5), 0.0, Vector2(1.0, 0.4))
		draw_circle(Vector2.ZERO, 7.5, SHADOW_COLOR)
		draw_set_transform(Vector2.ZERO)
	# Capstones glow softly gold, so big investments stand out.
	if is_capstone() and not destroyed:
		var glow := 0.25 + 0.15 * sin(Time.get_ticks_msec() / 300.0)
		draw_circle(Vector2.ZERO, 9.5, Color(Palette.GOLD, glow * 0.5))
		draw_arc(Vector2.ZERO, 9.0, 0.0, TAU, 24, Color(Palette.GOLD, glow + 0.2), 1.0)
	# Goo drips over sticky units, with a puddle at their feet.
	if sticky > 0.0:
		var goo := Color(Board.SPILL_COLOR, 0.85)
		draw_set_transform(Vector2(0, 6), 0.0, Vector2(1.0, 0.45))
		draw_circle(Vector2.ZERO, 7.0, Color(Board.SPILL_COLOR, 0.55))
		draw_set_transform(Vector2.ZERO)
		draw_rect(Rect2(-6, -7, 12, 3), goo)
		for x in [-5, -1, 3]:
			draw_rect(Rect2(x, -4, 2, 3 + (x + 5) % 3), goo)
	# Health bar, only shown while damaged.
	if hp < data.max_hp:
		draw_rect(Rect2(-7, -9, 14, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-7, -9, 14.0 * hp / data.max_hp, 2), Color(0.3, 1, 0.4))


## A small gold star in the bottom-left corner, for capstones whose animated
## art doesn't have one drawn in.
class CapstoneStar extends Node2D:
	func _draw() -> void:
		var points := PackedVector2Array()
		for i in 10:
			var radius := 3.2 if i % 2 == 0 else 1.4
			var angle := -PI / 2 + i * PI / 5
			points.append(Vector2(-5, 5) + Vector2(cos(angle), sin(angle)) * radius)
		draw_colored_polygon(points, Palette.GOLD)
