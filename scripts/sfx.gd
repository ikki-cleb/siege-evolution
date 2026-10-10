class_name Sfx
## Plays a sound through the Audio autoload. Gameplay scripts use this
## instead of "Audio" directly, because they can be loaded (e.g. by tests)
## before the autoloads exist.

static func play(sound: String, pitch_jitter := 0.05) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var audio := tree.root.get_node_or_null("Audio") if tree else null
	if audio:
		audio.play(sound, pitch_jitter)
