"""Draws the Settings screen's "More Ad Free Games" banner (Trivia Ladder,
the developer's other game, in its own look: deep indigo stage, gold
marquee lights).

    python3 tools/draw_more_games.py   -> art/more_games/banner.png

Trivia Ladder's icon (art/more_games/trivia_ladder_icon_src.png) is copied
from that game's repo (assets/images/icon.png). To feature another game,
swap the icon and the texts below.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "more_games" / "banner.png"
ICON = ROOT / "art" / "more_games" / "trivia_ladder_icon_src.png"
TITLE = "Trivia Ladder"
TAGLINE = "How high can you climb?"
W, H = 720, 200  # 2x the banner's size on screen (360 wide), for crisp text
STAGE_TOP, STAGE_BOTTOM = (30, 22, 82), (11, 9, 32)
GOLD, GOLD_DEEP = (247, 201, 72), (201, 143, 18)


def main():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(STAGE_TOP[i] + (STAGE_BOTTOM[i] - STAGE_TOP[i]) * t) for i in range(3)) + (255,))
    # A soft spotlight behind the icon.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((20, -40, 260, 240), fill=GOLD + (70,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
    # Marquee light bulbs along the top and bottom edges.
    for x in range(14, W, 28):
        for y in (10, H - 10):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=GOLD if (x // 28) % 2 else GOLD_DEEP)
    icon = Image.open(ICON).convert("RGBA").resize((140, 140), Image.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 139, 139), 32, fill=255)
    img.paste(icon, (40, 30), mask)
    title = ImageFont.truetype(str(ROOT / "assets/fonts/SiegeTitle.ttf"), 52)
    small = ImageFont.truetype(str(ROOT / "assets/fonts/SiegeText.ttf"), 24)
    d.text((206, 64), TITLE, font=title, fill=(245, 243, 255), stroke_width=4, stroke_fill=(11, 9, 32))
    d.text((208, 128), TAGLINE, font=small, fill=GOLD)
    img.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
