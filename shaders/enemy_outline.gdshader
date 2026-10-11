// Gives enemy sprites a thin red edge so they never look like the player's
// units. It draws a 1-pixel red ring in the empty pixels around the sprite
// (keeping the sprite's own dark outline). Where the art touches the edge of
// its frame there's no room outside, so those edge pixels are tinted red.
// (TEXTURE is read directly in fragment(): passing it to a helper function
// silently reads nothing in the web/Compatibility renderer.)
shader_type canvas_item;

// Red edge color. Its alpha sets the strength: 1.0 = solid, lower = softer.
uniform vec4 outline_color : source_color = vec4(1.0, 0.18, 0.18, 1.0);
// How many frames sit side by side in the texture (Sprite2D.hframes), so
// the edge test never peeks into the next frame of a strip.
uniform int frames = 1;

// The sprite's tint (hit flashes, stuns...). Kept separately because the
// COLOR that fragment() starts with already has the texture mixed in, which
// would make the ring see-through.
varying vec4 tint;

void vertex() {
	tint = COLOR;
}

void fragment() {
	vec4 pixel = texture(TEXTURE, UV);
	// Which frame of the strip this pixel belongs to.
	float frame_width = 1.0 / float(frames);
	float frame_left = floor(UV.x / frame_width) * frame_width;
	float frame_right = frame_left + frame_width;
	// One texel (TEXTURE_PIXEL_SIZE isn't reliable here in the Compatibility renderer).
	vec2 step = 1.0 / vec2(textureSize(TEXTURE, 0));
	vec2 offsets[4] = {vec2(step.x, 0.0), vec2(-step.x, 0.0), vec2(0.0, step.y), vec2(0.0, -step.y)};
	bool touches_sprite = false;  // an empty pixel next to the sprite
	bool touches_frame_edge = false;  // a sprite pixel on its frame's edge
	for (int i = 0; i < 4; i++) {
		vec2 next = UV + offsets[i];
		bool outside = next.x < frame_left || next.x > frame_right || next.y < 0.0 || next.y > 1.0;
		if (outside) {
			touches_frame_edge = true;
		} else if (texture(TEXTURE, next).a > 0.1) {
			touches_sprite = true;
		}
	}
	if (pixel.a < 0.1 && touches_sprite) {
		pixel = outline_color;
	} else if (pixel.a >= 0.1 && touches_frame_edge) {
		pixel.rgb = mix(pixel.rgb, outline_color.rgb, outline_color.a);
	}
	COLOR = pixel * tint;
}
