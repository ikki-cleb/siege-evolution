"""Reusable body parts for the world designs (all drawn front-facing, 3/4 top-down).

Every part takes the Canvas `c` and the pose `p` (see world_immune.py). Parts
that walk or flap use p.get("phase", 0) (0-3) so enemies animate.
"""
import math

from .kit import OUTLINE, hexc, shade

WHITE = (250, 250, 250, 255)


def phase(p):
    return p.get("phase", 0)


def legs(c, x, y, spread, count, color, length=4, p=None):
    """Little legs on both sides, stepping with the walk phase."""
    step = (0, 1, 0, -1)[phase(p or {})]
    for i in range(count // 2):
        oy = y + i * 3 - (count // 2 - 1) * 1.5
        for side in (-1, 1):
            lift = step if (i + (side > 0)) % 2 else -step
            c.line([(x + side * spread, oy), (x + side * (spread + length), oy + 2 + lift)], color)


def bug(c, p, body, head=None, x=16, y=21, rx=8, ry=6.5, legs_n=6, face=True, antennae=True,
        wings=None, horns=None, pincers=False, stinger=None, spots=None):
    """A round bug seen from above-front: abdomen, head, legs, antennae."""
    head = head or shade(body, -0.15)
    legs(c, x, y, rx - 1, legs_n, shade(body, -0.35), 3, p)
    if wings:
        flap = (0, 1, 0, -1)[phase(p)]
        c.ellipse(x - rx + 1, y - ry - flap, 4, 3, wings)
        c.ellipse(x + rx - 1, y - ry - flap, 4, 3, wings)
    c.blob(x, y, rx, ry, body)
    if spots:
        for sx_, sy_ in ((-3, 0), (3, 1), (0, 3)):
            c.ellipse(x + sx_, y + sy_, 1.4, 1.2, spots)
    if stinger:
        c.poly([(x - 1.5, y + ry - 1), (x + 1.5, y + ry - 1), (x, y + ry + 3)], stinger)
    hy = y - ry - 2
    if antennae:
        c.line([(x - 2, hy - 2), (x - 4, hy - 6)], OUTLINE)
        c.line([(x + 2, hy - 2), (x + 4, hy - 6)], OUTLINE)
    if horns:
        c.poly([(x - 1.5, hy - 2), (x + 1.5, hy - 2), (x, hy - 8)], horns)
    if pincers:
        c.line([(x - 3, hy), (x - 6, hy - 4), (x - 3, hy - 6)], shade(head, -0.2), 1)
        c.line([(x + 3, hy), (x + 6, hy - 4), (x + 3, hy - 6)], shade(head, -0.2), 1)
    c.blob(x, hy, 4.5, 4, head)
    if face:
        c.eyes(x, hy - 0.5, 2, p.get("mood", "calm"))
    return (x, hy - 4)


def animal(c, p, fur, x=16, y=19, ears="round", snout=None, horns=None, mane=None, size=1.0, face=True):
    """A chibi animal: a big head over a small body."""
    r = 7.5 * size
    c.blob(x, y + r * 0.9, r * 0.8, r * 0.6, shade(fur, -0.08))
    if mane:
        c.ellipse(x, y, r + 2, r + 1.5, mane)
    if ears == "round":
        c.ellipse(x - r * 0.75, y - r * 0.75, 2.6, 2.6, shade(fur, -0.12))
        c.ellipse(x + r * 0.75, y - r * 0.75, 2.6, 2.6, shade(fur, -0.12))
    elif ears == "point":
        for side in (-1, 1):
            c.poly([(x + side * r * 0.35, y - r * 0.6), (x + side * r * 0.95, y - r * 0.5), (x + side * r * 0.8, y - r * 1.25)],
                   shade(fur, -0.12))
    elif ears == "long":
        for side in (-1, 1):
            c.ellipse(x + side * r * 0.45, y - r * 1.05, 1.8, 3.6, shade(fur, -0.12))
    if horns:
        for side in (-1, 1):
            c.line([(x + side * r * 0.5, y - r * 0.6), (x + side * r * 1.1, y - r * 1.0), (x + side * r * 1.0, y - r * 1.4)], horns, 2)
    c.blob(x, y, r, r * 0.9, fur)
    if snout:
        c.ellipse(x, y + r * 0.4, r * 0.45, r * 0.32, snout)
        c.px(x - 1, y + r * 0.35, OUTLINE)
        c.px(x + 1, y + r * 0.35, OUTLINE)
    if face:
        c.eyes(x, y - r * 0.15, r * 0.38, p.get("mood", "calm"))
    return (x, y - r)


def bird(c, p, feathers, beak, x=16, y=19, size=1.0, tuft=None, face=True):
    flap = (0, -1, 0, 1)[phase(p)]
    r = 7 * size
    c.ellipse(x - r - 1, y + 1 + flap, 3, 4, shade(feathers, -0.15))
    c.ellipse(x + r + 1, y + 1 + flap, 3, 4, shade(feathers, -0.15))
    c.blob(x, y, r, r, feathers)
    if tuft:
        c.poly([(x - 2, y - r + 1), (x, y - r - 4), (x + 2, y - r + 1)], tuft)
    c.poly([(x - 2, y + 1), (x + 2, y + 1), (x, y + 4)], beak)
    if face:
        c.eyes(x, y - 2, 3, p.get("mood", "calm"))
    return (x, y - r)


def soldier(c, p, uniform, x=16, y=18, helmet=None, weapon="rifle", weapon_color=None):
    """A faceless toy soldier figure."""
    helmet = helmet or shade(uniform, -0.1)
    weapon_color = weapon_color or hexc("#5a5a5a")
    c.rect(x - 4, y, x + 4, y + 9, uniform)
    c.rect(x - 4, y + 9, x - 1, y + 13, shade(uniform, -0.2))
    c.rect(x + 1, y + 9, x + 4, y + 13, shade(uniform, -0.2))
    c.ellipse(x, y - 3, 4, 4, hexc("#e8c8a0"))
    c.ellipse(x, y - 5, 5, 3, helmet)
    c.rect(x - 5, y - 5, x + 5, y - 4, shade(helmet, -0.15))
    fire = p.get("act") == "fire"
    if weapon == "rifle":
        c.rect(x + 3, y - 2 - fire, x + 5, y + 8, weapon_color)
    elif weapon == "bazooka":
        c.rect(x + 2, y - 4 - fire, x + 6, y + 6, weapon_color)
    elif weapon == "grenade":
        c.ellipse(x + 6, y - 1 - fire * 2, 2, 2, weapon_color)
    elif weapon == "knife":
        c.poly([(x + 5, y + 4), (x + 7, y + 4), (x + 6, y - 2 - fire)], hexc("#d8d8e0"))
    return (x, y - 8)


def turret(c, p, base, head, x=16, y=20, barrels=1, barrel_len=8, barrel_color=None, wide=False):
    """A turret: a base block, a round head and barrels pointing up."""
    barrel_color = barrel_color or shade(head, -0.3)
    c.block(x - 9, y + 2, x + 9, y + 10, base)
    recoil = 2 if p.get("act") == "fire" else 0
    w = 3 if wide else 2
    for i in range(barrels):
        bx = x + (i - (barrels - 1) / 2) * (w + 1)
        c.rect(bx - w / 2, y - barrel_len + recoil, bx + w / 2, y - 2, barrel_color)
    c.blob(x, y, 6, 5, head)
    return (x, y - barrel_len)


def robot(c, p, body, visor, x=16, y=17, size=1.0, antenna=True, legs_style="legs"):
    s = size
    c.block(x - 6 * s, y + 3, x + 6 * s, y + 11 * s, shade(body, -0.05))
    c.block(x - 5 * s, y - 6 * s, x + 5 * s, y + 3, body)
    c.rect(x - 4 * s, y - 3 * s, x + 4 * s, y - 1 * s, visor)
    if antenna:
        c.line([(x, y - 6 * s), (x, y - 9 * s)], OUTLINE)
        c.ellipse(x, y - 9.5 * s, 1.3, 1.3, visor)
    step = (0, 1, 0, -1)[phase(p)]
    if legs_style == "legs":
        c.rect(x - 5 * s, y + 11 * s, x - 2 * s, y + 13 * s + step, shade(body, -0.25))
        c.rect(x + 2 * s, y + 11 * s, x + 5 * s, y + 13 * s - step, shade(body, -0.25))
    return (x, y - 6 * s)
