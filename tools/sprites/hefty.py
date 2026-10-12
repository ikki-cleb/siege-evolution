"""Beefier body parts for the redesigned units (the user found the first
designs flimsy): thick jointed legs, shaded shells with a seam, bigger
heads, three-part ants and chunky spiders. Faces stay cute.

Every part takes the Canvas `c` and the pose `p`. A unit's evolution
branch is p["branch"]: None for the base unit, 0 for the power branch and 1
for the utility branch (the canvas is also scaled up for both branches).
"""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, phase


def tier(p):
    """None (base), 0 (power) or 1 (utility)."""
    return p.get("branch")


def heavy_legs(c, x, y, spread, pairs, color, p, length=5.0, gap=3.2):
    """Thick, jointed legs on both sides: out to a knee, then down."""
    step = (0, 1, 0, -1)[phase(p)]
    for i in range(pairs):
        ly = y + (i - (pairs - 1) / 2) * gap
        for side in (-1, 1):
            lift = step if (i + (side > 0)) % 2 else -step
            hip = (x + side * spread, ly)
            knee = (x + side * (spread + length * 0.6), ly - 2.5)
            foot = (x + side * (spread + length), ly + 2.5 + lift)
            c.line([hip, knee, foot], color, 2)
            c.px(foot[0], foot[1] + 0.5, shade(color, -0.3))


def shell(c, x, y, rx, ry, color, seam=True, shine=True):
    """A hard, shiny shell: dark rim, highlight, and a center seam."""
    c.ellipse(x, y + 0.5, rx + 0.5, ry + 0.5, shade(color, -0.3))
    c.blob(x, y, rx, ry, color, shine=False)
    if shine:
        c.ellipse(x - rx * 0.45, y - ry * 0.45, rx * 0.28, ry * 0.2, shade(color, 0.28))
        c.ellipse(x + rx * 0.45, y - ry * 0.45, rx * 0.18, ry * 0.14, shade(color, 0.18))
    if seam:
        c.line([(x, y - ry + 1.5), (x, y + ry - 1)], shade(color, -0.35))


def head(c, p, x, y, r, color, eye_gap=2.4, eye_size=2):
    """A round head with the cute face."""
    c.blob(x, y, r, r * 0.88, color)
    c.eyes(x, y - 0.3, eye_gap, p.get("mood", "calm"), eye_size)
    if p.get("mouth") == "open":
        c.mouth(x, y + r * 0.45, "open", 2)


def antennae(c, x, y, color=OUTLINE, length=6, spread=4, tips=None):
    for side in (-1, 1):
        c.line([(x + side * 1.5, y), (x + side * spread * 0.6, y - length * 0.6), (x + side * spread, y - length)], color)
        if tips:
            c.ellipse(x + side * spread, y - length, 1.3, 1.3, tips)


def mandibles(c, x, y, color, size=1.0, wide=False):
    """Pincers in front of the head, opening on the attack frame."""
    w = 7 if wide else 5
    for side in (-1, 1):
        pts = [(x + side * 2.5, y), (x + side * w * size, y - 3.5 * size), (x + side * (w - 2.5) * size, y - 7 * size)]
        c.line(pts, color, 2)
        c.px(pts[-1][0], pts[-1][1], shade(color, 0.3))


def wings(c, p, x, y, rx, ry, color, spread=7):
    flap = (0, -1, 0, 1)[phase(p)] + (-1 if p.get("act") == "fire" else 0)
    for side in (-1, 1):
        c.ellipse(x + side * spread, y + flap, rx, ry, color)
        c.line([(x + side * 2, y + 1), (x + side * (spread + rx - 1), y - 1 + flap)], (255, 255, 255, 120))


def beetle(c, p, body, head_color=None, x=16, y=20, rx=10, ry=8.5, legs_color=None, spots=None,
           seam=True, head_r=5.2):
    """A big beetle seen from above-front."""
    head_color = head_color or shade(body, -0.2)
    legs_color = legs_color or limb_color(body)
    heavy_legs(c, x, y + 1, rx - 1.5, 3, legs_color, p, 5)
    shell(c, x, y, rx, ry, body, seam)
    if spots:
        for sx_, sy_, r in ((-4.5, -1, 1.8), (4.5, -1, 1.8), (-3.5, 3.5, 1.4), (3.5, 3.5, 1.4)):
            c.ellipse(x + sx_, y + sy_, r, r * 0.9, spots)
    hy = y - ry - 2.5
    head(c, p, x, hy, head_r, head_color)
    return (x, hy - head_r)


def ant(c, p, color, x=16, y=19, size=1.0, head_size=1.0, stinger=None, legs_color=None):
    """An ant: big abdomen at the back, small waist, head in front."""
    s = size
    legs_color = legs_color or limb_color(color)
    heavy_legs(c, x, y + 1 * s, 3.5 * s, 3, legs_color, p, 6 * s, 2.6 * s)
    c.ellipse(x, y + 7 * s, 6.2 * s, 5.2 * s, shade(color, -0.3))
    c.blob(x, y + 6.5 * s, 6 * s, 5 * s, color)
    for k in (-1, 1):  # abdomen bands
        c.line([(x - 5 * s, y + 6.5 * s + k * 2 * s), (x + 5 * s, y + 6.5 * s + k * 2 * s)], shade(color, -0.2))
    if stinger:
        c.poly([(x - 1.2, y + 11.5 * s), (x + 1.2, y + 11.5 * s), (x, y + 14 * s)], stinger)
    c.blob(x, y, 3.2 * s, 3 * s, shade(color, -0.08))
    hr = 5 * s * head_size
    hy = y - 3.5 * s - hr * 0.8
    head(c, p, x, hy, hr, shade(color, -0.12), eye_gap=2.2 * s * head_size)
    return (x, hy - hr)


def spider(c, p, body, x=16, y=19, r=7.5, eyes4=False, fuzz=None, legs_color=None):
    """A chunky spider: eight thick legs, round body, big cute eyes."""
    legs_color = legs_color or limb_color(body)
    step = (0, 1, 0, -1)[phase(p)]
    for i in range(4):
        for side in (-1, 1):
            a = -0.7 + i * 0.5
            hip = (x + side * r * 0.6, y + i * 1.6 - 2)
            knee = (x + side * (r + 3.5), y - 4 + i * 3.2 + (step if i % 2 else -step))
            foot = (x + side * (r + 5.5), y + 1 + i * 3.4)
            c.line([hip, knee, foot], legs_color, 2)
    c.ellipse(x, y + r * 0.9, r * 0.75, r * 0.6, shade(body, -0.15))  # abdomen behind
    c.blob(x, y, r, r * 0.9, body)
    if fuzz:
        for k in range(10):
            a = k * math.tau / 10
            c.px(x + math.cos(a) * r, y + math.sin(a) * r * 0.9, fuzz)
    if eyes4:
        for ex, er in ((x - 3, 1.9), (x + 3, 1.9), (x - 6, 1.1), (x + 6, 1.1)):
            c.ellipse(ex, y - 2, er, er, WHITE)
            c.px(ex, y - 1.5, OUTLINE)
    else:
        c.eyes(x, y - 2, 2.6, p.get("mood", "calm"), 2)
    return (x, y - r)


def glow(c, x, y, r, color, alpha=34):
    """A soft glow behind the art. Kept faint (under the outline's 40 alpha
    cut-off) so it stays a haze instead of becoming a solid outlined disc."""
    c.ellipse(x, y, r, r, color[:3] + (min(alpha, 38),))


def ring(c, x, y, rx, ry, color, dots=28):
    """A thin ring of dots (a shockwave), not a filled disc."""
    for k in range(dots):
        a = k * math.tau / dots
        c.px(x + math.cos(a) * rx, y + math.sin(a) * ry, color)


def limb_color(body):
    """Legs a bit darker than the body, but lighter on very dark bodies so
    their shape still reads."""
    r, g, b = body[:3]
    if 0.3 * r + 0.59 * g + 0.11 * b < 70:
        return shade(body, 0.22)
    return shade(body, -0.4)


def puffs(c, points, color):
    for x, y, r in points:
        c.blob(x, y, r, r * 0.85, color)


def pc_mark(c, x, y, p, r=1.6):
    """The small pack-color mark every unit carries."""
    c.ellipse(x, y, r, r, p["pc"])
