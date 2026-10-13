"""Spawner designs: where invaders come from, one per world (plus variants).

Each design draws one 32x32 frame of a 4-frame idle loop: design(c, t)
where t is the frame (0-3). Art sits on a see-through background with a
soft shadow, so it works on painted level backgrounds and floor tiles alike.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites"))

from kit import hexc, shade  # noqa: E402

FRAMES = 4
DARK = (22, 12, 20, 255)
SHADOW = (0, 0, 0, 70)

# Spawner file -> design function name. Paths are under art/tiles/.
SPAWNERS = {}


def spawner(*paths):
    def wrap(func):
        for path in paths:
            SPAWNERS[path] = func
        return func
    return wrap


# --- shared parts --------------------------------------------------------------

def shadow(c, cx=16, cy=27, rx=12, ry=3.5):
    c.ellipse(cx, cy, rx, ry, SHADOW)


def eyes(c, cx, cy, t, color="#ffe060", gap=3, blink_frame=3):
    """Two glinting eyes in the dark; they blink on one frame."""
    glow = hexc(color)
    for side in (-1, 1):
        x = cx + side * gap
        if t == blink_frame:
            c.rect(x - 1, cy + 0.5, x + 1, cy + 1, shade(glow, -0.3))
        else:
            c.rect(x - 1, cy - 0.5, x + 1, cy + 1.5, glow)
            c.px(x - 0.5, cy - 0.5, (255, 255, 255, 255))


def vortex(c, cx, cy, r, t, colors=("#3a1a6a", "#7a40d0", "#c090ff")):
    """A swirling portal: spiral arms that turn each frame."""
    deep, mid, bright = (hexc(x) for x in colors)
    c.ellipse(cx, cy, r, r, deep)
    for arm in range(3):
        for k in range(10):
            a = t * (math.tau / 12) + arm * math.tau / 3 + k * 0.32
            d = r * (0.95 - k * 0.085)
            c.px(cx + math.cos(a) * d - 0.5, cy + math.sin(a) * d - 0.5, mid if k < 6 else bright)
    c.ellipse(cx, cy, 1.6, 1.6, bright)
    c.px(cx - 0.5, cy - 0.5, (255, 255, 255, 255))


def mouse_hole(c, t, wall, wall_dark, trim):
    """A mouse hole in a strip of wall: an arch, a nose and eyes peeking."""
    shadow(c, ry=2.5)
    c.rect(2, 8, 30, 28, wall_dark)
    c.rect(2, 8, 29, 26, wall)
    c.rect(2, 8, 29, 9, shade(wall, 0.12))
    c.rect(2, 23, 30, 28, trim)               # skirting board
    c.rect(2, 23, 29, 24, shade(trim, 0.15))
    c.ellipse(16, 20, 8, 9, DARK)             # the arch
    c.rect(8, 20, 24, 28, DARK)
    c.line([(9, 15), (12, 12), (16, 11), (20, 12), (23, 15)], shade(wall, -0.3))
    eyes(c, 16, 20, t, "#fff0c0", gap=2.5)
    # A pink nose that twitches, and whiskers.
    nose_y = 23 + (1 if t == 1 else 0)
    c.rect(15, nose_y, 17, nose_y + 1, (240, 140, 160, 255))
    for side in (-1, 1):
        c.line([(16 + side * 2, nose_y + 0.5), (16 + side * 5, nose_y - 0.5 + (t % 2))], (200, 190, 180, 255))


# --- the spawners --------------------------------------------------------------

@spawner("backyard_bugs/spawner.png")
def bug_burrow(c, t):
    # A tall dirt mound with a burrow on top; crumbs trickle in, eyes glint.
    shadow(c, rx=13, ry=3.5)
    dirt = hexc("#8a5a32")
    c.blob(16, 19, 13.5, 10, dirt)
    c.ellipse(15, 15, 9, 5, shade(dirt, 0.08))
    c.ellipse(16, 15.5, 7.5, 4.5, shade(dirt, -0.2))
    c.ellipse(16, 16, 6, 3.5, DARK)
    for x, y in ((5, 22), (26, 21), (10, 26), (22, 26), (19, 24)):
        c.ellipse(x, y, 1.5, 1.1, hexc("#b0a090"))
    for x in (3, 28):  # grass tufts at the foot
        c.line([(x, 27), (x - 1, 24)], hexc("#5a9a3a"))
        c.line([(x + 1, 27), (x + 2, 23)], hexc("#6ab04a"))
    eyes(c, 16, 16, t, "#ffd040", gap=2.5)
    c.px(10 + t, 11 + t * 1.2, shade(dirt, 0.2))
    c.px(22 - (t % 2), 11 + ((t + 2) % 4), shade(dirt, 0.15))


@spawner("wild_kingdom/spawner.png")
def thicket_den(c, t):
    # A dark den under a leafy thicket; the leaves rustle.
    shadow(c, rx=13)
    leaf = hexc("#3f7a34")
    sway = (0, 1, 0, -1)[t]
    for x, y, r in ((7, 15, 6), (25, 15, 6), (11, 9, 6.5), (21, 9, 6.5), (16, 6, 6)):
        c.blob(x + sway * (1 if y < 12 else 0), y, r, r * 0.85, leaf)
    c.blob(16, 19, 12, 8, shade(leaf, -0.08))
    c.ellipse(16, 22, 8, 6, (16, 26, 14, 255))
    c.rect(8, 22, 24, 28, (16, 26, 14, 255))
    c.rect(6, 26, 26, 28, hexc("#6a4a2a"))
    eyes(c, 16, 22, t, "#d0ff60", gap=3, blink_frame=2)
    for x, y in ((6, 12), (24, 6), (14, 4)):
        c.px(x + sway, y, shade(leaf, 0.25))


@spawner("immune_system/spawner.png")
def pore(c, t):
    # A pulsing pore in soft tissue, spores bubbling out.
    pulse = (0, 0.6, 1.0, 0.6)[t]
    flesh = hexc("#c05068")
    c.ellipse(16, 18, 13 + pulse, 10 + pulse * 0.7, shade(flesh, -0.15))
    c.ellipse(15.5, 17.5, 12 + pulse, 9 + pulse * 0.7, flesh)
    c.ellipse(16, 18, 8 + pulse * 0.5, 6 + pulse * 0.4, shade(flesh, -0.3))
    c.ellipse(16, 18.5, 5.5, 4, (60, 10, 30, 255))
    c.ellipse(16, 19, 3, 2, (110, 30, 70, 255))
    for k in range(6):  # wrinkles around the rim
        a = k * math.tau / 6 + 0.3
        c.px(16 + math.cos(a) * 10.5, 18 + math.sin(a) * 8, shade(flesh, 0.18))
    # A spore rising and fading out.
    sy = 14 - t * 3
    c.ellipse(16 + (t % 2), sy, 1.5, 1.5, hexc("#b0e070"))
    c.px(15.5 + (t % 2), sy - 0.5, (240, 255, 220, 255))


@spawner("total_war/spawner.png")
def toy_box(c, t):
    # A red toy chest; the lid lifts and eyes peek out of the gap.
    shadow(c, rx=13)
    red = hexc("#c83a32")
    lift = (0, 1, 2, 1)[t]
    c.block(4, 15, 29, 28, red)
    c.rect(4, 20, 28, 21, hexc("#f0c040"))      # trim band
    c.rect(14, 18, 18, 23, hexc("#f0c040"))     # latch plate
    c.rect(15, 19, 17, 22, hexc("#a07020"))
    c.rect(5, 15 - lift, 28, 16, DARK)          # the dark gap
    c.block(3, 9 - lift, 30, 15 - lift, shade(red, 0.06))
    c.rect(3, 13 - lift, 29, 14 - lift, hexc("#f0c040"))
    if lift > 0:
        eyes(c, 16, 15.5 - lift / 2, t, "#ffffff", gap=4, blink_frame=-1)


@spawner("total_war/sea_spawner.png")
def bath_drain(c, t):
    # A bathtub drain with water swirling around it.
    c.ellipse(16, 16, 12, 12, (90, 150, 200, 120))
    for ring in range(2):
        r = 10 - ring * 3
        for k in range(8):
            a = t * (math.tau / 16) + k * math.tau / 8 + ring * 0.4
            c.px(16 + math.cos(a) * r, 16 + math.sin(a) * r, (210, 240, 255, 220))
    c.ellipse(16, 16, 6, 6, hexc("#9aa4b0"))
    c.ellipse(15.5, 15.5, 5.2, 5.2, hexc("#c8d0d8"))
    for y in (13, 15.5, 18):
        c.rect(12.5, y, 19.5, y + 1, (40, 50, 60, 255))


@spawner("galactic_siege/spawner.png")
def space_gate(c, t):
    # A metal warp ring with a swirling purple portal and blinking lights.
    shadow(c, ry=3)
    metal = hexc("#8890a0")
    c.ellipse(16, 17, 12.5, 12.5, shade(metal, -0.2))
    c.ellipse(15.5, 16.5, 12, 12, metal)
    vortex(c, 16, 17, 9, t)
    for k in range(4):
        a = k * math.tau / 4 + math.tau / 8
        on = (k + t) % 4 == 0
        c.rect(16 + math.cos(a) * 11 - 1, 17 + math.sin(a) * 11 - 1, 16 + math.cos(a) * 11 + 1,
               17 + math.sin(a) * 11 + 1, (120, 255, 160, 255) if on else (40, 90, 60, 255))


@spawner("galactic_siege/asteroid/spawner.png")
def crater_gate(c, t):
    # A rocky crater with a warp portal glowing at the bottom.
    shadow(c, rx=13)
    rock = hexc("#7a6a5a")
    c.blob(16, 18, 14, 11, rock)
    for x, y in ((6, 13), (25, 14), (9, 25), (23, 25)):
        c.ellipse(x, y, 2, 1.5, shade(rock, -0.15))
    c.ellipse(16, 18, 10, 8, shade(rock, -0.25))
    vortex(c, 16, 18.5, 7.5, t)


@spawner("galactic_siege/station/spawner.png")
def hatch_gate(c, t):
    # A floor hatch with hazard stripes, the portal swirling inside.
    shadow(c, rx=13)
    c.rect(3, 4, 30, 30, (40, 44, 52, 255))
    for k in range(-30, 30, 6):  # hazard stripes on the frame
        c.line([(3 + k, 30), (3 + k + 26, 4)], hexc("#f0c030"), 2)
    c.rect(7, 8, 26, 26, (40, 44, 52, 255))
    c.rect(8, 9, 25, 25, hexc("#5c6470"))
    vortex(c, 16.5, 17, 7.5, t)
    for x, y in ((5, 6), (28, 6), (5, 28), (28, 28)):
        c.px(x, y, (200, 205, 215, 255))


@spawner("kitchen_defense/spawner.png")
def mouse_hole_wood(c, t):
    mouse_hole(c, t, hexc("#c8b090"), hexc("#a08868"), hexc("#8a5a32"))


@spawner("kitchen_defense/floor/spawner.png")
def mouse_hole_plaster(c, t):
    mouse_hole(c, t, hexc("#ece6da"), hexc("#c8c0b0"), hexc("#b07a48"))


@spawner("kitchen_defense/counter/spawner.png")
def mouse_hole_tiles(c, t):
    mouse_hole(c, t, hexc("#9cc4e0"), hexc("#6a94b4"), hexc("#e8eef4"))
    # Grout lines on the tiles (around the hole).
    for x in (9, 16, 23):
        c.line([(x, 9), (x, 11)], (240, 248, 255, 255))
    c.line([(3, 15), (7, 15)], (240, 248, 255, 255))
    c.line([(25, 15), (29, 15)], (240, 248, 255, 255))


@spawner("birthday_bash/spawner.png")
def party_present(c, t):
    # A giant present: the lid hops, eyes peek out, confetti puffs.
    shadow(c, rx=13)
    box = hexc("#e05a9a")
    ribbon = hexc("#f0d040")
    hop = (0, 2, 3, 1)[t]
    c.block(5, 15, 28, 29, box)
    c.rect(15, 15, 18, 28, ribbon)
    c.rect(5, 15 - hop, 28, 16, DARK)
    eyes(c, 16, 15.5 - hop / 2, t, "#ffffff", gap=5, blink_frame=-1) if hop >= 2 else None
    c.block(3, 10 - hop, 30, 15 - hop, shade(box, 0.08))
    c.rect(15, 10 - hop, 18, 14 - hop, ribbon)
    c.ellipse(13, 8 - hop, 3, 2.2, ribbon)  # bow
    c.ellipse(20, 8 - hop, 3, 2.2, ribbon)
    for k, color in enumerate(("#60c0ff", "#80e060", "#ff8040")):
        if hop >= 2:
            c.px(6 + k * 9 + t, 7 - hop - k % 2, hexc(color))


@spawner("birthday_bash/bouncy/spawner.png")
def bounce_castle(c, t):
    # A bouncy castle door that wobbles.
    shadow(c, rx=13)
    squash = (0, 0.5, 1, 0.5)[t]
    blue, red, yellow = hexc("#5aa0e8"), hexc("#e85a5a"), hexc("#f0d040")
    for x in (5, 27):  # turrets
        c.blob(x, 15 + squash, 3.5, 10 - squash, red)
        c.ellipse(x, 5 + squash * 2, 3.5, 2, yellow)
    c.blob(16, 19 + squash, 11, 9 - squash, blue)
    c.ellipse(16, 21 + squash, 6, 6 - squash * 0.5, DARK)
    c.rect(10, 21 + squash, 22, 28, DARK)
    c.rect(4, 26, 28, 29, yellow)
    eyes(c, 16, 22, t, "#ffffff", gap=2.5)


@spawner("birthday_bash/living/spawner.png")
def party_doorway(c, t):
    # A doorway with bobbing balloons tied to the frame.
    shadow(c, rx=12)
    frame = hexc("#f4ece0")
    c.rect(6, 7, 26, 29, shade(frame, -0.15))
    c.rect(6, 7, 25, 28, frame)
    c.rect(9, 10, 23, 29, DARK)
    eyes(c, 16, 19, t, "#ffe060", gap=3)
    bob = (0, -1, -1, 0)
    for side, color, off in ((-1, "#e85a8a", 0), (1, "#5ac0e8", 2)):
        bx = 16 + side * 11
        by = 6 + bob[(t + off) % 4]
        c.line([(bx, by + 3), (16 + side * 9, 11)], (230, 230, 230, 255))
        c.ellipse(bx, by, 3.2, 3.8, hexc(color))
        c.px(bx - 1.5, by - 1.5, (255, 255, 255, 230))
