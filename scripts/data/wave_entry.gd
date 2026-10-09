class_name WaveEntry
extends Resource
## One group of identical invaders inside a wave, e.g. "6 Rhinovirus, one
## every 1.2 seconds, starting 3 seconds into the wave".

@export var invader: InvaderData
@export var count: int = 5
## Seconds between each invader in this group.
@export var spacing: float = 1.0
## Seconds after the wave starts before the first one appears.
@export var delay: float = 0.0
## Which spawn point to use (0 = first 'S' in the layout, reading left to
## right, top to bottom). -1 alternates between all spawn points.
@export var spawn_point: int = -1
