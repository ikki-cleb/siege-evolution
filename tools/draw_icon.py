"""Draws the app icon and store art from the game's own sprites.

    python3 tools/draw_icon.py [--preview out.png]

The user picked a boss looming over a base: the Grizzly over the castle,
on deep purple with a red glow. Writes:
  art/icons/icon_1024.png           App Store icon (square, no transparency)
  art/icons/android_foreground.png  Android adaptive icon front layer (432x432)
  art/icons/android_background.png  Android adaptive icon back layer (432x432)
  art/icons/android_monochrome.png  Android 13+ themed icon (432x432)
  art/icons/icon_192.png            Android legacy launcher icon
  art/icons/splash.png              boot splash (logo on the game's background)
  store/play-icon-512.png           Google Play listing icon
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "icons"
BOSS = ROOT / "art/anim/wild_kingdom/invaders/grizzly_move.png"
FORT = ROOT / "art/tiles/total_war/base_big.png"


def frame(path):
    strip = Image.open(path).convert("RGBA")
    return strip.crop((0, 0, strip.height, strip.height))


def background(size):
    """Deep purple fading to near-black, with a red glow behind the boss."""
    img = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / size
        d.line([(0, y), (size, y)], fill=(int(70 - 50 * t), int(20 - 8 * t), int(60 - 42 * t), 255))
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((size * 0.05, 0, size * 0.95, size * 0.6), fill=(255, 60, 60, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(size * 0.12)))
    return img


def subject(size):
    """The Grizzly looming over the castle (transparent background). The
    user picked this: a boss face looming over a base, the castle in front."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    boss = frame(BOSS)
    scale = size * 9.5 / 512
    boss = boss.resize((int(boss.width * scale), int(boss.height * scale)), Image.NEAREST)
    x0 = int((boss.width - size) / 2)
    img.alpha_composite(boss.crop((x0, 0, x0 + size, boss.height)), (0, int(-size * 70 / 512)))
    # Fade the boss's lower half into shadow so the castle stands out.
    shade = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(int(size * 0.5), size):
        sd.line([(0, y), (size, y)], fill=(10, 4, 10, int(200 * (y - size * 0.5) / (size * 0.5))))
    faded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    faded.paste(shade, (0, 0), img.getchannel("A"))
    img.alpha_composite(faded)
    fort = Image.open(FORT).convert("RGBA")
    fs = size * 2.3 / 512
    fort = fort.resize((int(fort.width * fs), int(fort.height * fs)), Image.NEAREST)
    shadow = Image.new("RGBA", fort.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 160), (0, 0), fort)
    fx = int(size / 2 - fort.width / 2)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(size / 64)), (fx + size // 85, size - fort.height - size // 128))
    img.alpha_composite(fort, (fx, size - fort.height - size * 14 // 512))
    return img


def app_icon(size):
    img = background(size)
    img.alpha_composite(subject(size))
    return img.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    big = app_icon(1024)
    big.save(OUT / "icon_1024.png")
    big.resize((192, 192), Image.LANCZOS).save(OUT / "icon_192.png")
    (ROOT / "store").mkdir(exist_ok=True)
    big.resize((512, 512), Image.LANCZOS).save(ROOT / "store" / "play-icon-512.png")
    # Android adaptive icons: 432x432 layers; only the middle 66% is always
    # visible (launchers crop to circles, squircles...), so the art shrinks.
    fg = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    fg.alpha_composite(subject(346), (43, 43))
    fg.save(OUT / "android_foreground.png")
    background(432).save(OUT / "android_background.png")
    mono = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    mono.paste(Image.new("RGBA", (432, 432), (255, 255, 255, 255)), (0, 0), fg.getchannel("A"))
    mono.save(OUT / "android_monochrome.png")
    # Boot splash: the icon art, shown centered on the game's background.
    splash = background(360)
    splash.alpha_composite(subject(360))
    mask = Image.new("L", (360, 360), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 359, 359), 80, fill=255)
    rounded = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
    rounded.paste(splash, (0, 0), mask)
    rounded.save(OUT / "splash.png")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        sheet = Image.new("RGB", (1024 + 40 + 512 + 432 * 2 + 60, 1024), (40, 40, 44))
        sheet.paste(big, (0, 0))
        x = 1044
        for s in (180, 120, 60, 40):  # how it reads at home-screen sizes
            sheet.paste(big.resize((s, s), Image.LANCZOS), (x, 20 + sum(v + 20 for v in (180, 120, 60, 40) if v > s)))
        x = 1044 + 200
        circle = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
        layered = background(432)
        layered.alpha_composite(fg)
        mask = Image.new("L", (432, 432), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 431, 431), fill=255)
        circle.paste(layered, (0, 0), mask)
        sheet.paste(circle, (x, 20), circle)
        sheet.paste(Image.new("RGB", (432, 432), (60, 90, 70)), (x + 450, 20))
        sheet.paste(mono, (x + 450, 20), mono)
        sheet.save(out)


if __name__ == "__main__":
    main()
