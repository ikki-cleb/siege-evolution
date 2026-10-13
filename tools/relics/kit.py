"""A tiny drawing kit for 16x16 relic icons.

Each icon is drawn with simple shapes on a 16x16 canvas; finish() then adds
a dark 1-pixel outline around everything. Keep art inside pixels 1..14 so
the outline fits.
"""
import colorsys

from PIL import Image, ImageDraw

SIZE = 16
OUTLINE = (24, 14, 22, 255)
CLEAR = (0, 0, 0, 0)


def hexc(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def shade(color, amount):
    """Lighter (>0) or darker (<0), same hue. Takes a hex string or a tuple."""
    if isinstance(color, str):
        color = hexc(color)
    r, g, b = (c / 255 for c in color[:3])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l + amount)), s)
    return (int(r * 255), int(g * 255), int(b * 255), color[3])


def ramp(color):
    """(light, base, dark, darker) shades of one color."""
    return shade(color, 0.16), shade(color, 0.0), shade(color, -0.15), shade(color, -0.3)


# Shared materials.
WOOD = "#a0703c"
METAL = "#b8c0cc"
GOLD = "#f0c040"
WHITE = (255, 255, 255, 255)
SHINE = (255, 255, 255, 230)
INK = (40, 24, 36, 255)


class Icon:
    def __init__(self):
        self.img = Image.new("RGBA", (SIZE, SIZE), CLEAR)
        self.d = ImageDraw.Draw(self.img)

    @staticmethod
    def _c(color):
        return hexc(color) if isinstance(color, str) else color

    # --- plain shapes (corners inclusive) ---
    def rect(self, x0, y0, x1, y1, color):
        if x1 < x0 or y1 < y0:
            return
        self.d.rectangle((x0, y0, x1, y1), fill=self._c(color))

    def ell(self, x0, y0, x1, y1, color):
        if x1 < x0 or y1 < y0:
            return
        self.d.ellipse((x0, y0, x1, y1), fill=self._c(color))

    def poly(self, points, color):
        self.d.polygon(points, fill=self._c(color))

    def line(self, points, color, width=1):
        self.d.line(points, fill=self._c(color), width=width)

    def px(self, x, y, color):
        if 0 <= x < SIZE and 0 <= y < SIZE:
            self.img.putpixel((x, y), self._c(color))

    def pxs(self, points, color):
        for x, y in points:
            self.px(x, y, color)

    def grid(self, x, y, rows, colors):
        """Paint a small pixel pattern: each character maps to a color in
        `colors`; '.' is skipped."""
        for dy, row in enumerate(rows):
            for dx, key in enumerate(row):
                if key != ".":
                    self.px(x + dx, y + dy, colors[key])

    # --- shaded shapes ---
    def ball(self, x0, y0, x1, y1, color, shine=True):
        """A round shape lit from the top-left."""
        light, base, dark, _ = ramp(color)
        self.ell(x0, y0, x1, y1, dark)
        self.ell(x0, y0, x1 - 1, y1 - 1, base)
        if shine:
            w, h = x1 - x0, y1 - y0
            self.ell(x0 + w // 5, y0 + h // 5, x0 + w // 5 + max(1, w // 4), y0 + h // 5 + max(1, h // 4), light)

    def box(self, x0, y0, x1, y1, color):
        """A block lit from the top-left: light top edge, dark bottom/right."""
        light, base, dark, _ = ramp(color)
        self.rect(x0, y0, x1, y1, base)
        self.rect(x0, y0, x1, y0, light)
        self.rect(x0, y1, x1, y1, dark)
        self.rect(x1, y0 + 1, x1, y1, dark)

    def finish(self):
        """Add the dark outline around every drawn pixel."""
        src = self.img.copy()
        for y in range(SIZE):
            for x in range(SIZE):
                if src.getpixel((x, y))[3] > 0:
                    continue
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < SIZE and 0 <= ny < SIZE and src.getpixel((nx, ny))[3] > 0:
                        self.img.putpixel((x, y), OUTLINE)
                        break
        return self.img
