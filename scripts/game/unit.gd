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

## Regeneration pauses for this many seconds after taking damage, so a
## healing wall can't hold off a smasher forever.
const REGEN_PAUSE := 2.0

var _cooldown := 0.0
var _regen_pause := 0.0
var _sprite: Sprite2D


func setup(p_data: UnitData, p_cell: Vector2i, p_board: Board) -> void:
	data = p_data
	base_data = p_data
	cell = p_cell
	board = p_board
	hp = data.max_hp
	position = board.cell_center(cell)
	_sprite = Sprite2D.new()
	add_child(_sprite)
	_update_sprite()
	_pop()


## A quick bounce when the unit appears or evolves.
func _pop() -> void:
	_sprite.scale = Vector2(0.4, 0.4)
	create_tween().tween_property(_sprite, "scale", Vector2.ONE, 0.25) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## Units on water use their water look (nets and mines).
func _update_sprite() -> void:
	var on_water := board.water.has(cell) and data.water_texture != null
	_sprite.texture = data.water_texture if on_water else data.texture


func is_evolved() -> bool:
	return data != base_data


## Turns this unit into one of its evolutions, at full health.
func evolve(into: UnitData) -> void:
	data = into
	hp = data.max_hp
	_update_sprite()
	_pop()
	board.fx.add_pulse(position, Board.TILE * 1.2, Palette.GOLD)
	board.fx.add_puff(position, Palette.GOLD)
	queue_redraw()


## Damage from a smasher. Reflect bounces part of it back at the attacker.
func take_damage(amount: float, attacker: Invader = null) -> void:
	if destroyed:
		return
	if attacker and data.reflect > 0.0:
		attacker.take_damage(amount * data.reflect, true)
	hp -= amount
	_regen_pause = REGEN_PAUSE
	if hp <= 0.0:
		hp = 0.0
		destroyed = true
		visible = false
		board.on_unit_destroyed(self)
	queue_redraw()


## Covered in a spiller's goo: attacks slower until the wave ends.
## A weaker spill never replaces a stronger one.
func make_sticky(amount: float) -> void:
	if amount > sticky:
		sticky = amount
		queue_redraw()


## Back to full health and clean of goo (called between waves).
func restore() -> void:
	hp = data.max_hp
	destroyed = false
	sticky = 0.0
	visible = true
	_cooldown = 0.0
	queue_redraw()


func _process(delta: float) -> void:
	if destroyed or not board.wave_active:
		return
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
		# Swarm units attack faster for every unit packed around them.
		var speed_up := 1.0 + data.adjacency_bonus * board.neighbor_count(cell)
		# Goo slows it down (0.4 sticky = attacks at 60% of normal speed).
		speed_up *= 1.0 - sticky
		_cooldown = data.attack_interval / speed_up


## Attacks if anything is in range. Returns false if there was nothing to hit.
func _attack() -> bool:
	if data.attack_mode == UnitData.AttackMode.PULSE:
		var targets := _invaders_in_range(position, data.attack_range)
		if targets.is_empty():
			return false
		board.fx.add_pulse(position, data.attack_range * Board.TILE, data.shot_color)
		for invader in targets:
			_hit(invader)
		return true

	var target := _find_target()
	if target == null:
		return false
	board.fx.add_shot(position, target.position, data.shot_color)
	Sfx.play("shoot", 0.15)
	var victims: Array[Invader] = [target]
	if data.splash_radius > 0.0:
		board.fx.add_pulse(target.position, data.splash_radius * Board.TILE, data.shot_color)
		for other in _invaders_in_range(target.position, data.splash_radius):
			if other != target:
				victims.append(other)
	for invader in victims:
		_hit(invader)
	return true


func _hit(invader: Invader) -> void:
	if data.mark_bonus > 0.0:
		invader.apply_mark(data.mark_bonus, data.mark_duration)
	if data.slow > 0.0:
		invader.apply_slow(data.slow, data.slow_duration)
	if data.stun_duration > 0.0:
		invader.apply_stun(data.stun_duration)
	if data.poison_dps > 0.0:
		invader.apply_poison(data.poison_dps, data.poison_duration, data.poison_spreads)
	if data.damage > 0.0:
		invader.take_damage(data.damage, data.pierce)


func _can_target(invader: Invader) -> bool:
	return invader.alive and not invader.underground and (data.hits_air or not invader.is_flying())


func _invaders_in_range(center: Vector2, tiles: float) -> Array[Invader]:
	var result: Array[Invader] = []
	for invader in board.invaders:
		if _can_target(invader) and center.distance_to(invader.position) <= tiles * Board.TILE:
			result.append(invader)
	return result


## Picks the invader in range that is closest to reaching the base.
func _find_target() -> Invader:
	var best: Invader = null
	var best_distance := INF
	for invader in _invaders_in_range(position, data.attack_range):
		var distance := invader.distance_to_base()
		if distance < best_distance:
			best_distance = distance
			best = invader
	return best


func _draw() -> void:
	# Goo drips over sticky units.
	if sticky > 0.0:
		var goo := Color(Board.SPILL_COLOR, 0.85)
		draw_rect(Rect2(-6, -7, 12, 3), goo)
		for x in [-5, -1, 3]:
			draw_rect(Rect2(x, -4, 2, 3 + (x + 5) % 3), goo)
	# Health bar, only shown while damaged.
	if hp < data.max_hp:
		draw_rect(Rect2(-7, -9, 14, 2), Color(0.1, 0.1, 0.1))
		draw_rect(Rect2(-7, -9, 14.0 * hp / data.max_hp, 2), Color(0.3, 1, 0.4))
