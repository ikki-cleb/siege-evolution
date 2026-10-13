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
    cut-off) so it stays a haze instead of becoming a solid outlined disc.
    Draw it FIRST: shapes replace the pixels under them (no blending), so a
    glow drawn on top would wipe out the art."""
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


def quadruped(c, p, fur, x=16, y=17, size=1.0, ears="point", snout=None, horns=None, mane=None,
              hoof=None, tail=None, belly=None, head_y=None, spots=None):
    """A full-body chibi four-legged animal, 3/4 from the front: a sturdy
    body with four stubby legs, and a big head in front of it."""
    s = size
    dark = shade(fur, -0.22)
    hoof = hoof or shade(fur, -0.45)
    step = (0, 1, 0, -1)[phase(p)]
    # Legs: back pair (darker, behind), front pair (in front).
    for lx, col, lift in ((-7, dark, step), (7, dark, -step), (-4.5, fur, -step), (4.5, fur, step)):
        top, bottom = y + 6 * s, y + 13 * s + (lift if p.get("act") != "idle" else 0) * 0.5
        c.rect(x + lx * s - 1.8 * s, top, x + lx * s + 1.8 * s, bottom, col)
        c.rect(x + lx * s - 1.8 * s, bottom - 1.5 * s, x + lx * s + 1.8 * s, bottom, hoof)
    if tail:
        c.line([(x + 9 * s, y + 4 * s), (x + 12 * s, y + 1 * s)], tail, 2)
    c.ellipse(x, y + 5 * s, 10.5 * s, 7 * s, shade(fur, -0.15))  # body
    c.blob(x, y + 4.5 * s, 10 * s, 6.5 * s, fur)
    if belly:
        c.ellipse(x, y + 7.5 * s, 6 * s, 3 * s, belly)
    if spots:
        for sx_, sy_ in ((-6, 3), (5, 6), (7, 1)):
            c.ellipse(x + sx_ * s, y + sy_ * s, 2.2 * s, 1.6 * s, spots)
    hy = head_y if head_y is not None else y - 2 * s
    r = 6.5 * s
    if mane:
        c.ellipse(x, hy + 1, r + 2.5, r + 2, mane)
    if horns:
        for side in (-1, 1):
            c.line([(x + side * r * 0.55, hy - r * 0.55), (x + side * r * 1.25, hy - r * 0.95), (x + side * r * 1.2, hy - r * 1.5)],
                   horns, 2)
    if ears == "point":
        for side in (-1, 1):
            c.poly([(x + side * r * 0.3, hy - r * 0.65), (x + side * r * 0.95, hy - r * 0.5), (x + side * r * 0.8, hy - r * 1.3)], dark)
    elif ears == "long":
        for side in (-1, 1):
            c.ellipse(x + side * r * 0.5, hy - r * 1.05, 1.9 * s, 4 * s, dark)
    elif ears == "round":
        for side in (-1, 1):
            c.ellipse(x + side * r * 0.75, hy - r * 0.7, 2.6 * s, 2.6 * s, dark)
    elif ears == "side":
        for side in (-1, 1):
            c.ellipse(x + side * r * 1.05, hy - r * 0.2, 3 * s, 1.6 * s, dark)
    c.blob(x, hy, r, r * 0.9, fur)
    if snout:
        c.ellipse(x, hy + r * 0.42, r * 0.5, r * 0.34, snout)
        c.px(x - 1.2, hy + r * 0.38, OUTLINE)
        c.px(x + 1.2, hy + r * 0.38, OUTLINE)
    c.eyes(x, hy - r * 0.18, r * 0.36, p.get("mood", "calm"), 2)
    return (x, hy - r)


def plump_bird(c, p, feathers, beak, x=16, y=18, size=1.0, tuft=None, feet=None, belly=None, wing=None):
    """A round, full-bodied bird with wings, feet and a beak."""
    s = size
    flap = (0, -1, 0, 1)[phase(p)] + (-2 if p.get("act") == "fire" else 0)
    feet = feet or hexc("#e8a030")
    for side in (-1, 1):
        c.line([(x + side * 3 * s, y + 8 * s), (x + side * 3 * s, y + 11.5 * s)], feet, 2)
        c.line([(x + side * 1.5 * s, y + 11.5 * s), (x + side * 4.5 * s, y + 11.5 * s)], feet)
    wing = wing or shade(feathers, -0.15)
    for side in (-1, 1):
        c.ellipse(x + side * 9 * s, y + 1 * s + flap, 3.5 * s, 5.5 * s, wing)
    c.blob(x, y, 9 * s, 9 * s, feathers)
    if belly:
        c.ellipse(x, y + 3.5 * s, 5.5 * s, 4.5 * s, belly)
    if tuft:
        c.poly([(x - 2.5, y - 8.5 * s), (x, y - 13 * s), (x + 2.5, y - 8.5 * s)], tuft)
    c.poly([(x - 2.2, y - 0.5), (x + 2.2, y - 0.5), (x, y + 3.5)], beak)
    c.eyes(x, y - 3.5 * s, 3 * s, p.get("mood", "calm"), 2)
    return (x, y - 9 * s)


def cell_body(c, p, color, x=16, y=19, rx=10, ry=9, nucleus=None, lobes=1, granules=None, n_granules=6,
              armored=False, face=True, face_y=None):
    """A living cell: a double membrane, cytoplasm, a nucleus and granules.
    armored=True gives it a thick plated membrane (power evolutions)."""
    membrane = shade(color, -0.25)
    if armored:
        c.ellipse(x, y + 0.5, rx + 2, ry + 2, shade(color, -0.4))
        for k in range(10):  # armor plates around the rim
            a = k * math.tau / 10
            c.ellipse(x + math.cos(a) * (rx + 1), y + math.sin(a) * (ry + 1), 2.2, 2, shade(color, -0.1))
    c.ellipse(x, y + 0.5, rx + 0.8, ry + 0.8, membrane)
    c.blob(x, y, rx, ry, color)
    c.ellipse(x - rx * 0.4, y - ry * 0.5, rx * 0.3, ry * 0.18, shade(color, 0.25))
    if granules:
        for k in range(n_granules):
            a = k * 2.4 + 0.5
            d = 0.55 + 0.25 * ((k * 7) % 3) / 2
            c.ellipse(x + math.cos(a) * rx * d, y + math.sin(a) * ry * d, 1.2, 1.1, granules)
    if nucleus:
        if lobes == 1:
            c.ellipse(x + rx * 0.25, y + ry * 0.3, rx * 0.32, ry * 0.3, nucleus)
        else:
            for k in range(lobes):
                a = math.pi * 0.15 + k * math.pi * 0.35
                c.ellipse(x + math.cos(a) * rx * 0.35, y + ry * 0.25 + math.sin(a) * ry * 0.2, rx * 0.2, ry * 0.2, nucleus)
    if face:
        fy = face_y if face_y is not None else y - ry * 0.2
        c.eyes(x, fy, rx * 0.3, p.get("mood", "calm"), 2)
        if p.get("mouth") == "open":
            c.mouth(x, fy + 3, "open", 2)
        else:
            c.mouth(x, fy + 3, "smile", 3)
    return (x, y - ry)


def pseudopods(c, x, y, color, reach=1.0, count=4, start=0.6, p=None):
    """Blobby arms reaching out of an amoeba-like cell."""
    wave = (0, 1, 0, -1)[phase(p or {})]
    for k in range(count):
        a = start + k * (math.tau / count)
        tip = (x + math.cos(a) * 13 * reach, y + math.sin(a) * 11 * reach + wave * 0.5)
        mid = (x + math.cos(a) * 8 * reach, y + math.sin(a) * 7 * reach)
        c.ellipse(mid[0], mid[1], 3.2, 2.8, color)
        c.ellipse(tip[0], tip[1], 2.6, 2.4, color)


def antibody(c, x, y, color, size=1.0):
    """A Y-shaped antibody."""
    s = size
    c.line([(x, y + 3 * s), (x, y)], color, 2)
    c.line([(x, y), (x - 2.5 * s, y - 3 * s)], color, 2)
    c.line([(x, y), (x + 2.5 * s, y - 3 * s)], color, 2)


def plastic(pc):
    """Toy-soldier plastic in a pack's color: a bit muted, like molded toys."""
    return mix_colors(pc, hexc("#6a7a40"), 0.3)


def mix_colors(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def army_man(c, p, color, x=16, y=17, weapon="rifle", helmet="round", base=True, size=1.0):
    """A stocky plastic army man on a little base: big helmet, dot eyes,
    oversized toy weapon. Returns the top of the helmet."""
    s = size
    dark = shade(color, -0.22)
    fire = p.get("act") == "fire"
    if base:
        c.ellipse(x, y + 13 * s, 8.5 * s, 2.6 * s, shade(color, -0.35))
        c.ellipse(x, y + 12.5 * s, 8 * s, 2.2 * s, dark)
    step = (0, 1, 0, -1)[phase(p)] * 0.5
    c.rect(x - 4.5 * s, y + 6 * s, x - 0.8 * s, y + 12.5 * s + step, dark)  # legs
    c.rect(x + 0.8 * s, y + 6 * s, x + 4.5 * s, y + 12.5 * s - step, dark)
    c.block(x - 6 * s, y - 1 * s, x + 6 * s, y + 7 * s, color)  # chunky torso
    c.rect(x - 6 * s, y + 4.5 * s, x + 6 * s, y + 5.5 * s, shade(color, -0.3))  # belt
    for side in (-1, 1):  # arms
        c.rect(x + side * 6 * s - 1.6 * s, y, x + side * 6 * s + 1.6 * s, y + 5 * s, shade(color, -0.08))
    hy = y - 4.5 * s
    c.blob(x, hy, 5 * s, 4.6 * s, shade(color, 0.08))  # head
    if helmet == "round":
        c.ellipse(x, hy - 2 * s, 6.2 * s, 3.8 * s, shade(color, -0.12))
        c.rect(x - 6.5 * s, hy - 1.5 * s, x + 6.5 * s, hy - 0.5 * s, shade(color, -0.3))
    elif helmet == "beret":
        c.ellipse(x - 1, hy - 3.5 * s, 5.5 * s, 2.4 * s, shade(color, -0.35))
    elif helmet == "cap":
        c.ellipse(x, hy - 3 * s, 5 * s, 2.6 * s, shade(color, -0.12))
        c.rect(x - 1, hy - 2.5 * s, x + 6 * s, hy - 1.5 * s, shade(color, -0.3))
    elif helmet == "mask":  # a gas mask
        c.ellipse(x, hy - 2 * s, 6 * s, 3.6 * s, shade(color, -0.12))
        c.ellipse(x, hy + 2 * s, 2 * s, 1.6 * s, shade(color, -0.4))
    c.px(x - 2 * s, hy + 0.5 * s, OUTLINE)  # dot eyes
    c.px(x + 2 * s, hy + 0.5 * s, OUTLINE)
    gun = shade(color, -0.45)
    if weapon == "rifle":
        c.rect(x + 5 * s, y - 6 * s - fire, x + 7 * s, y + 6 * s, gun)
        c.rect(x + 4.5 * s, y + 2 * s, x + 7.5 * s, y + 4 * s, gun)
    elif weapon == "long_rifle":
        c.rect(x + 5 * s, y - 11 * s - fire, x + 6.8 * s, y + 6 * s, gun)
        c.rect(x + 4 * s, y - 5 * s, x + 8 * s, y - 3.5 * s, shade(gun, 0.25))  # scope
    elif weapon == "bazooka":
        c.rect(x + 3 * s, y - 7 * s - fire, x + 8 * s, y + 5 * s, gun)
        c.ellipse(x + 5.5 * s, y - 7 * s - fire, 2.5 * s, 1.2 * s, shade(gun, -0.3))
    elif weapon == "grenade":
        c.ellipse(x + 7 * s, y - 4 * s - fire * 2, 2.2 * s, 2.2 * s, gun)
        c.px(x + 7 * s, y - 6.5 * s - fire * 2, shade(gun, 0.4))
    elif weapon == "knife":
        c.poly([(x + 6 * s, y + 3 * s), (x + 8 * s, y + 3 * s), (x + 7 * s, y - 4 * s - fire)], hexc("#d8dce4"))
    elif weapon == "binoculars":
        c.rect(x - 3 * s, hy - 0.5 * s, x + 3 * s, hy + 2 * s, gun)
    return (x, hy - 5.5 * s)
