"""A tiny pixel-art drawing kit for 32x32 sprites.

Designs draw on a Canvas in "design space" (32x32 pixels, origin top-left).
The canvas can squash/stretch everything around the sprite's feet (the
bottom center), which is how frames breathe, wind up and lunge. After the
body is drawn, `finish()` adds a dark outline; effects (flashes, shots) are
drawn after that so they glow instead of looking solid.
"""
import colorsys
import math

from PIL import Image, ImageDraw

SIZE = 32
FEET = (16.0, 30.0)  # squash and stretch pivot around this point
OUTLINE = (24, 14, 22, 255)


def hexc(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def shade(color, amount):
    """Lighter (>0) or darker (<0), same hue."""
    r, g, b = (c / 255 for c in color[:3])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l + amount)), s)
    return (int(r * 255), int(g * 255), int(b * 255), color[3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


class Canvas:
    def __init__(self, sx=1.0, sy=1.0, dx=0.0, dy=0.0, size=SIZE):
        # `size`: 32 for normal sprites; bosses use 64 (twice the detail).
        self.size = size
        self.feet = (FEET[0] * size / SIZE, FEET[1] * size / SIZE)
        self.img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.sx, self.sy, self.dx, self.dy = sx, sy, dx, dy

    # --- transforms ---
    def T(self, x, y):
        fx, fy = self.feet
        return (fx + (x - fx) * self.sx + self.dx, fy + (y - fy) * self.sy + self.dy)

    # --- shapes (all in design space) ---
    def ellipse(self, cx, cy, rx, ry, color):
        x, y = self.T(cx, cy)
        rx, ry = rx * self.sx, ry * self.sy
        x0, y0 = round(x - rx), round(y - ry)
        self.draw.ellipse((x0, y0, max(x0, round(x + rx) - 1), max(y0, round(y + ry) - 1)), fill=color)

    def rect(self, x0, y0, x1, y1, color):
        a, b = self.T(x0, y0), self.T(x1, y1)
        left, top = round(a[0]), round(a[1])
        # Squashing can shrink a thin shape to nothing; keep at least 1 pixel.
        right, bottom = max(left, round(b[0]) - 1), max(top, round(b[1]) - 1)
        self.draw.rectangle((left, top, right, bottom), fill=color)

    def poly(self, points, color):
        self.draw.polygon([tuple(round(v) for v in self.T(x, y)) for x, y in points], fill=color)

    def line(self, points, color, width=1):
        self.draw.line([tuple(round(v) for v in self.T(x, y)) for x, y in points], fill=color, width=width)

    def px(self, x, y, color):
        x, y = self.T(x, y)
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.size and 0 <= y < self.size:
            self.img.putpixel((x, y), color)

    # --- shaded parts ---
    def blob(self, cx, cy, rx, ry, color, shine=True):
        """A rounded body with a dark lower-right and a light highlight."""
        self.ellipse(cx, cy, rx, ry, shade(color, -0.16))
        self.ellipse(cx - 0.7, cy - 0.9, rx - 0.8, ry - 1.0, color)
        if shine:
            self.ellipse(cx - rx * 0.42, cy - ry * 0.45, max(1.2, rx * 0.28), max(1.0, ry * 0.22), shade(color, 0.18))

    def block(self, x0, y0, x1, y1, color):
        """A chunky block: darker bottom/right edge, lighter top/left edge."""
        self.rect(x0, y0, x1, y1, shade(color, -0.16))
        self.rect(x0, y0, x1 - 1, y1 - 2, color)
        self.rect(x0, y0, x1 - 1, y0 + 1, shade(color, 0.14))

    def spikes(self, cx, cy, r, count, color, length=3.0, start=0.0):
        for i in range(count):
            a = start + i * math.tau / count
            bx, by = cx + math.cos(a) * r, cy + math.sin(a) * r
            tx, ty = cx + math.cos(a) * (r + length), cy + math.sin(a) * (r + length)
            side = 1.2
            nx, ny = -math.sin(a) * side, math.cos(a) * side
            self.poly([(bx + nx, by + ny), (bx - nx, by - ny), (tx, ty)], color)

    def eyes(self, cx, cy, gap=3, mood="calm", size=2):
        """Two eyes. mood: calm, angry, squint, closed, wide."""
        for side in (-1, 1):
            ex = cx + side * gap
            if mood in ("closed", "squint"):
                self.rect(ex - size / 2, cy, ex + size / 2 + 0.5, cy + 1, OUTLINE)
                continue
            self.rect(ex - size / 2, cy - size / 2, ex + size / 2 + 0.5, cy + size / 2 + 1, (250, 250, 250, 255))
            self.px(ex + (0 if size < 3 else 0.5), cy + 0.5, OUTLINE)
            if size >= 3:
                self.px(ex - 0.5, cy + 0.5, OUTLINE)
            if mood == "angry":
                self.line([(ex - side * 2, cy - size), (ex + side * 1, cy - size + 1.5)], OUTLINE)
            if mood == "wide":
                self.px(ex - 0.5, cy - 0.5, (250, 250, 250, 255))

    def mouth(self, cx, cy, kind="smile", width=3):
        if kind == "open":
            self.ellipse(cx, cy + 1, width / 2 + 0.5, 1.6, (90, 20, 30, 255))
        elif kind == "fangs":
            self.rect(cx - width / 2, cy, cx + width / 2 + 0.5, cy + 1, OUTLINE)
            self.px(cx - width / 2 + 0.5, cy + 1, (250, 250, 250, 255))
            self.px(cx + width / 2 - 0.5, cy + 1, (250, 250, 250, 255))
        elif kind == "frown":
            self.line([(cx - width / 2, cy + 1), (cx, cy), (cx + width / 2, cy + 1)], OUTLINE)
        else:
            self.line([(cx - width / 2, cy), (cx, cy + 1), (cx + width / 2, cy)], OUTLINE)

    # --- finishing ---
    def finish(self):
        """Adds a 1-pixel dark outline around everything drawn so far."""
        src = self.img.copy()
        w, h = src.size
        pix = src.load()
        out = self.img.load()
        for y in range(h):
            for x in range(w):
                if pix[x, y][3] > 40:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < w and 0 <= ny < h and pix[nx, ny][3] > 40:
                        out[x, y] = OUTLINE
                        break
        return self

    # --- effects (after finish) ---
    def glow(self, cx, cy, r, color):
        x, y = cx + self.dx, cy + self.dy
        for rr, alpha in ((r, 70), (r * 0.6, 150), (r * 0.3, 255)):
            self.draw.ellipse((round(x - rr), round(y - rr), round(x + rr) - 1, round(y + rr) - 1),
                              fill=color[:3] + (alpha,))

    def ring(self, cx, cy, r, color, alpha=200):
        x, y = cx + self.dx, cy + self.dy
        self.draw.ellipse((round(x - r), round(y - r), round(x + r) - 1, round(y + r) - 1),
                          outline=color[:3] + (alpha,), width=1)


def death_frames(base):
    """A generic 4-frame death from a finished sprite: flash, burst apart, fade."""
    frames = []
    white = Image.new("RGBA", base.size, (255, 255, 255, 0))
    alpha = base.getchannel("A")
    flash = Image.composite(Image.new("RGBA", base.size, (255, 255, 255, 255)), white, alpha)
    frames.append(Image.blend(base, flash, 0.7))
    cells = 4
    step = SIZE // cells
    for t, fade in ((1, 0.85), (2, 0.55), (3.2, 0.25)):
        frame = Image.new("RGBA", base.size, (0, 0, 0, 0))
        for gy in range(cells):
            for gx in range(cells):
                piece = base.crop((gx * step, gy * step, (gx + 1) * step, (gy + 1) * step))
                if piece.getbbox() is None:
                    continue
                cx, cy = gx * step + step / 2 - 16, gy * step + step / 2 - 18
                ox, oy = int(cx * 0.35 * t), int(cy * 0.35 * t - t)
                shrink = max(2, int(step * (1 - 0.22 * t)))
                piece = piece.resize((shrink, shrink), Image.NEAREST)
                piece.putalpha(piece.getchannel("A").point(lambda a, f=fade: int(a * f)))
                frame.alpha_composite(piece, (max(0, min(SIZE - shrink, gx * step + ox)), max(0, min(SIZE - shrink, gy * step + oy))))
        frames.append(frame)
    return frames
