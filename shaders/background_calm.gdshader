shader_type canvas_item;
// Calms a painted level background so game sprites stand out (the user
// chose "Fog + Mute"). At strength 1.0 ("Medium"): 40% less color, 15% less
// contrast, then a 35% fade toward the picture's own average color, so each
// map keeps its overall tone. 0 = untouched; higher = stronger.
// Set up by scripts/game/calm_background.gd.

uniform float strength = 1.0;
uniform vec3 avg_color = vec3(0.5);
uniform float avg_lum = 0.5;

void fragment() {
	// Read TEXTURE directly here (a Compatibility-renderer quirk: not via a helper).
	vec4 tex = texture(TEXTURE, UV);
	float t = clamp(strength, 0.0, 1.6);
	vec3 c = tex.rgb;
	float lum = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(vec3(lum), c, 1.0 - 0.4 * t);           // mute the color
	c = mix(vec3(avg_lum), c, 1.0 - 0.15 * t);      // soften the contrast
	vec3 fog = mix(vec3(avg_lum), avg_color, 1.0 - 0.4 * t);
	c = mix(c, fog, 0.35 * t);                      // fade toward the average
	COLOR = vec4(c, tex.a);
}
