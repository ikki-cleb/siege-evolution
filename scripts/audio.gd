extends Node
## Sound effects and music. Loaded automatically at startup as "Audio".
##   Audio.play("kill")             plays assets/sfx/kill.wav
##   Audio.play_music("menu")       loops assets/music/menu.wav
## Sound and music can each be switched off; the choice is saved.

const SETTINGS_PATH := "user://settings.json"
const SFX_DIR := "res://assets/sfx/"
const MUSIC_DIR := "res://assets/music/"
const VOICES := 10
## The same sound won't restart more often than this (seconds), so a big
## wave doesn't turn into noise.
const MIN_GAP := 0.06
## Quieter sounds that happen constantly.
const VOLUME := {"shoot": -14.0, "coins": -8.0, "kill": -6.0, "button": -6.0}

var sound_on := true
var music_on := true

var _players: Array[AudioStreamPlayer] = []
var _next := 0
var _streams := {}
var _last_played := {}
var _music: AudioStreamPlayer
var _music_name := ""


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in VOICES:
		var player := AudioStreamPlayer.new()
		add_child(player)
		_players.append(player)
	_music = AudioStreamPlayer.new()
	_music.volume_db = -10.0
	add_child(_music)
	_load_settings()


func play(sound: String, pitch_jitter := 0.05) -> void:
	if not sound_on:
		return
	var now := Time.get_ticks_msec() / 1000.0
	if now - _last_played.get(sound, -1.0) < MIN_GAP:
		return
	_last_played[sound] = now
	var stream := _stream(SFX_DIR + sound + ".wav")
	if stream == null:
		return
	var player := _players[_next]
	_next = (_next + 1) % _players.size()
	player.stream = stream
	player.volume_db = VOLUME.get(sound, -3.0)
	player.pitch_scale = 1.0 + randf_range(-pitch_jitter, pitch_jitter)
	player.play()


## Starts a looping track (does nothing if it's already playing).
func play_music(track: String) -> void:
	_music_name = track
	if not music_on:
		_music.stop()
		return
	var stream := _stream(MUSIC_DIR + track + ".wav") as AudioStreamWAV
	if stream == null or (_music.playing and _music.stream == stream):
		return
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_end = stream.get_length() * stream.mix_rate
	_music.stream = stream
	_music.play()


func set_sound(on: bool) -> void:
	sound_on = on
	_save_settings()


func set_music(on: bool) -> void:
	music_on = on
	_save_settings()
	if on:
		play_music(_music_name)
	else:
		_music.stop()


func _stream(path: String) -> AudioStream:
	if not _streams.has(path):
		_streams[path] = load(path) if ResourceLoader.exists(path) else null
	return _streams[path]


func _load_settings() -> void:
	if not FileAccess.file_exists(SETTINGS_PATH):
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(SETTINGS_PATH))
	if parsed is Dictionary:
		sound_on = parsed.get("sound", true)
		music_on = parsed.get("music", true)


func _save_settings() -> void:
	var file := FileAccess.open(SETTINGS_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify({"sound": sound_on, "music": music_on}))
