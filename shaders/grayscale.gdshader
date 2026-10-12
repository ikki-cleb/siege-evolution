shader_type canvas_item;
// Grey and dark: for locked worlds' postcard banners (scripts/ui/menu.gd).

uniform float brightness = 0.55;

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	float lum = dot(tex.rgb, vec3(0.299, 0.587, 0.114)) * brightness;
	COLOR = vec4(vec3(lum), tex.a);
}
