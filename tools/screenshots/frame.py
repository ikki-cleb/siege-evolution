"""Frames the raw store screenshots with a caption, and draws the Google Play
feature graphic. Run by tools/screenshots/make_screenshots.sh.

    python3 tools/screenshots/frame.py <raw_dir> <out_dir> <width> <height>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
TITLE_FONT = str(ROOT / "assets/fonts/SiegeTitle.ttf")
BG_TOP, BG_BOTTOM = (58, 22, 60), (20, 12, 18)
GOLD = (255, 210, 60)
# One caption per screenshot (store/listing.md lists them too).
CAPTIONS = {
    "01_title": "Evolve your defenders",
    "02_wave": "Build a maze. Hold the line.",
    "03_evolve": "Every unit branches two ways",
    "04_boss": "Giant boss fights",
    "05_relics": "Collect game-changing relics",
    "06_worlds": "7 worlds to defend",
}


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)))
    return img


def fit_text(draw, text, max_width, size):
    while size > 20:
        font = ImageFont.truetype(TITLE_FONT, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 4
    return ImageFont.truetype(TITLE_FONT, size)


def frame(raw: Path, caption: str, w: int, h: int) -> Image.Image:
    img = gradient(w, h)
    d = ImageDraw.Draw(img)
    band = int(h * 0.15)
    font = fit_text(d, caption, w * 0.88, int(w * 0.085))
    d.text((w / 2 + w * 0.006, band * 0.55 + w * 0.008), caption, font=font, anchor="mm", fill=(0, 0, 0))
    d.text((w / 2, band * 0.55), caption, font=font, anchor="mm", fill=GOLD,
           stroke_width=max(2, w // 180), stroke_fill=(40, 16, 30))
    shot = Image.open(raw).convert("RGB")
    scale = min((w * 0.88) / shot.width, (h - band - h * 0.03) / shot.height)
    shot = shot.resize((int(shot.width * scale), int(shot.height * scale)), Image.LANCZOS)
    x, y = (w - shot.width) // 2, band
    radius = int(w * 0.05)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width - 1, shot.height - 1), radius, fill=255)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x + 8, y + 14, x + shot.width + 8, y + shot.height + 14), radius, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(w // 70))).convert("RGB")
    ImageDraw.Draw(img).rounded_rectangle((x - 4, y - 4, x + shot.width + 3, y + shot.height + 3), radius + 4, fill=GOLD)
    img.paste(shot, (x, y), mask)
    return img


def feature_graphic(out: Path):
    """Google Play's 1024x500 banner: the title, the tagline, the Grizzly and the castle."""
    sys.path.insert(0, str(ROOT / "tools"))
    from draw_icon import background, subject
    w, h = 1024, 500
    img = background(w).crop((0, 0, w, h)).convert("RGBA")
    art = subject(500)
    img.alpha_composite(art, (w - 520, 0))
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(TITLE_FONT, 92)
    mid = ImageFont.truetype(TITLE_FONT, 52)
    small = ImageFont.truetype(str(ROOT / "assets/fonts/SiegeText.ttf"), 28)
    for text, font, y, color in (("SIEGE", big, 120, (250, 236, 242)), ("EVOLUTION", mid, 215, (255, 77, 109))):
        d.text((54, y + 6), text, font=font, fill=(0, 0, 0), stroke_width=8, stroke_fill=(0, 0, 0))
        d.text((50, y), text, font=font, fill=color, stroke_width=8, stroke_fill=(40, 16, 30))
    d.text((54, 310), "From the backyard to the stars.", font=small, fill=(243, 227, 234))
    img.convert("RGB").save(out)


def main():
    raw_dir, out_dir, w, h = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, caption in CAPTIONS.items():
        raw = raw_dir / f"{name}.png"
        if raw.exists():
            frame(raw, caption, w, h).save(out_dir / f"{name}.png")
    feature_graphic(ROOT / "store" / "screenshots" / "feature-graphic.png")
    print("framed", out_dir)


if __name__ == "__main__":
    main()
