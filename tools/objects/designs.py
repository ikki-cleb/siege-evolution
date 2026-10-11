"""Map object designs: the obstacles that block a level (one set of 3 looks
per world or variant) and Total War's bathtub water.

Each obstacle design draws one 32x32 frame: design(c, v, t), where v is the
look (0-2) and t the animation frame (0-3; most obstacles ignore it). Art
sits on a see-through background with a soft shadow, so it works on
painted level backgrounds and floor tiles alike.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites"))

from kit import hexc, shade  # noqa: E402

FRAMES = 4
LOOKS = 3
SHADOW = (0, 0, 0, 95)
WHITE = (255, 255, 255, 255)

# Obstacle file (under art/tiles/) -> (design, animated?)
OBSTACLES = {}


def obstacle(path, animated=False):
    def wrap(func):
        OBSTACLES[path] = (func, animated)
        return func
    return wrap


def shadow(c, cx=16, cy=27, rx=12, ry=3.5):
    c.ellipse(cx, cy, rx, ry, SHADOW)


def speckles(c, points, color):
    for x, y in points:
        c.px(x, y, color)


# --- Backyard Bugs: garden stones --------------------------------------------

@obstacle("backyard_bugs/obstacle.png")
def garden_stone(c, v, t):
    stone = hexc("#8e8a84")
    if v == 0:  # a round boulder with moss on top
        shadow(c)
        c.blob(16, 18, 12, 10, stone)
        c.ellipse(13, 10, 7, 3, hexc("#5e9a3a"))
        c.ellipse(12, 9.5, 5, 2, hexc("#7cb84a"))
        speckles(c, [(20, 20), (11, 22), (22, 15)], shade(stone, -0.15))
    elif v == 1:  # stacked flat stones
        shadow(c, ry=3)
        c.blob(16, 23, 13, 5, shade(stone, -0.05))
        c.blob(15, 16, 10, 4.5, stone)
        c.blob(17, 10, 7, 3.5, shade(stone, 0.06))
        speckles(c, [(9, 23), (22, 16), (15, 10)], shade(stone, -0.18))
    else:  # a rock with a little mushroom and clover
        shadow(c)
        c.blob(15, 19, 11, 9, shade(stone, 0.03))
        c.rect(23, 14, 25, 21, hexc("#f0e6d0"))
        c.ellipse(24, 13, 4.5, 3, hexc("#d04a3a"))
        speckles(c, [(22, 12), (25, 11)], WHITE)
        for x, y in ((7, 25), (9, 24), (8, 26)):
            c.ellipse(x, y, 1.6, 1.4, hexc("#5aa03a"))


# --- Wild Kingdom: farm obstacles --------------------------------------------

@obstacle("wild_kingdom/obstacle.png")
def farm_obstacle(c, v, t):
    if v == 0:  # a lichen-spotted boulder
        stone = hexc("#9a948c")
        shadow(c)
        c.blob(16, 18, 13, 10, stone)
        speckles(c, [(10, 14), (11, 14), (20, 19), (21, 19), (14, 22)], hexc("#b8c070"))
        c.line([(18, 10), (21, 14)], shade(stone, -0.2))
    elif v == 1:  # a tree stump with rings
        bark = hexc("#7a5030")
        shadow(c, rx=11)
        c.rect(6, 14, 26, 26, bark)
        c.rect(6, 14, 8, 26, shade(bark, 0.08))
        c.rect(24, 14, 26, 26, shade(bark, -0.12))
        c.ellipse(16, 14, 10, 5, hexc("#d8b078"))
        c.ellipse(16, 14, 6.5, 3.2, hexc("#c09060"))
        c.ellipse(16, 14, 3, 1.5, hexc("#d8b078"))
        c.line([(16, 14), (21, 12)], hexc("#a07040"))
    else:  # a hay bale
        hay = hexc("#e0c060")
        shadow(c, rx=13)
        c.block(4, 10, 29, 27, hay)
        for y in (13, 17, 21, 25):
            c.line([(5, y), (27, y + 1)], shade(hay, -0.12))
        c.rect(10, 10, 11, 26, hexc("#a06030"))
        c.rect(21, 10, 22, 26, hexc("#a06030"))


# --- Microscopic: cells (they pulse gently) -----------------------------------

@obstacle("immune_system/obstacle.png", animated=True)
def tissue_cell(c, v, t):
    pulse = (0, 0.5, 1, 0.5)[t]
    if v == 0:  # a red blood cell with its dimple
        red = hexc("#c83848")
        shadow(c, ry=3)
        c.ellipse(16, 17, 12 + pulse, 10 + pulse, shade(red, -0.15))
        c.ellipse(15.5, 16.5, 11.5 + pulse, 9.5 + pulse, red)
        c.ellipse(16, 17, 6, 4.5, shade(red, -0.2))
        c.ellipse(14, 13, 3, 1.5, shade(red, 0.18))
    elif v == 1:  # a yellow fat cell with a nucleus
        fat = hexc("#e8c860")
        shadow(c)
        c.blob(16, 17, 12 + pulse * 0.6, 10 + pulse * 0.6, fat)
        c.ellipse(20, 20, 3, 2.5, hexc("#a08030"))
        c.px(19, 19, shade(fat, 0.2))
    else:  # a cluster of purple membrane bubbles
        purple = hexc("#8a4a8a")
        shadow(c, rx=13)
        for x, y, r in ((10, 19, 6), (21, 18, 7), (15, 11, 5.5)):
            c.blob(x, y, r + pulse * 0.4, r + pulse * 0.4, purple)
        speckles(c, [(9, 18), (20, 16), (14, 10)], shade(purple, 0.25))


# --- Total War: toys -----------------------------------------------------------

@obstacle("total_war/obstacle.png")
def toy_obstacle(c, v, t):
    if v == 0:  # a wooden alphabet block
        blue = hexc("#3a6ad0")
        shadow(c, rx=12)
        c.block(5, 6, 28, 28, blue)
        c.rect(5, 6, 27, 7, shade(blue, 0.2))
        c.rect(9, 10, 23, 23, hexc("#f4ecd8"))
        c.poly([(12, 21), (16, 11), (20, 21), (18, 21), (17, 18), (15, 18), (14, 21)], hexc("#d03a32"))
    elif v == 1:  # a building brick with studs
        red = hexc("#d83a32")
        shadow(c, rx=13)
        c.block(3, 11, 30, 27, red)
        for x in (8, 16, 24):
            c.ellipse(x, 10, 3, 2, shade(red, -0.1))
            c.ellipse(x - 0.5, 9, 3, 2, shade(red, 0.12))
    else:  # a toy drum
        shadow(c)
        c.rect(5, 12, 27, 26, hexc("#e8b030"))
        for x in range(6, 27, 4):
            c.line([(x, 13), (x + 2, 25)], hexc("#f4f0e0"))
        c.ellipse(16, 12, 11, 4, hexc("#f4f0e0"))
        c.rect(5, 24, 27, 26, hexc("#c03030"))
        c.line([(9, 4), (14, 10)], hexc("#a06030"), 2)


# --- Galactic Siege: space debris (some twinkle or blink) ---------------------

def asteroid(c, v, t, rock, glint=True):
    shadow(c, ry=3)
    shapes = (((16, 17, 12, 10),), ((13, 18, 9, 8), (22, 14, 6, 5)), ((16, 16, 11, 11),))
    for x, y, rx, ry in shapes[v]:
        c.blob(x, y, rx, ry, rock)
    for x, y, r in (((11, 15, 2.5), (20, 21, 2)), ((12, 19, 2.5), (22, 14, 1.5)), ((13, 13, 3), (20, 20, 2.5)))[v]:
        c.ellipse(x, y, r, r * 0.8, shade(rock, -0.18))
        c.px(x - 1, y - 1, shade(rock, -0.3))
    if glint and t == v % FRAMES:
        c.px(8 + v * 6, 9, WHITE)
        c.px(7 + v * 6, 9, (200, 220, 255, 255))
        c.px(9 + v * 6, 9, (200, 220, 255, 255))
        c.px(8 + v * 6, 8, (200, 220, 255, 255))
        c.px(8 + v * 6, 10, (200, 220, 255, 255))


@obstacle("galactic_siege/asteroid/obstacle.png", animated=True)
def space_rock(c, v, t):
    asteroid(c, v, t, hexc("#6a5a4c"))


@obstacle("galactic_siege/obstacle.png", animated=True)
def moon_obstacle(c, v, t):
    if v == 0:  # a grey moon rock
        asteroid(c, 0, t, hexc("#8a8c94"))
    elif v == 1:  # a small crater
        dust = hexc("#9a9ca4")
        c.ellipse(16, 18, 13, 9, (0, 0, 0, 60))
        c.ellipse(16, 17, 12.5, 8.5, shade(dust, 0.08))
        c.ellipse(16, 18, 9, 6, shade(dust, -0.15))
        c.ellipse(16, 19, 7, 4, shade(dust, -0.3))
    else:  # a cluster of glowing crystals
        shadow(c)
        glow = (0, 0.06, 0.12, 0.06)[t]
        for x, h, w in ((10, 14, 3), (17, 20, 4), (23, 12, 3)):
            crystal = shade(hexc("#70c8e0"), glow)
            c.poly([(x - w, 26), (x + w, 26), (x + w, 26 - h + 3), (x, 26 - h), (x - w, 26 - h + 3)], crystal)
            c.line([(x, 25), (x, 27 - h)], shade(crystal, 0.2))


@obstacle("galactic_siege/station/obstacle.png", animated=True)
def station_obstacle(c, v, t):
    metal = hexc("#6a7280")
    if v == 0:  # a cargo crate
        shadow(c, rx=13)
        c.block(4, 7, 29, 28, hexc("#a87838"))
        c.rect(4, 15, 28, 17, hexc("#7a5020"))
        c.line([(6, 9), (26, 26)], hexc("#8a6028"))
        c.line([(26, 9), (6, 26)], hexc("#8a6028"))
    elif v == 1:  # a heap of scrap metal, sparking
        shadow(c, rx=13)
        c.poly([(3, 26), (8, 14), (14, 18), (19, 9), (25, 16), (29, 26)], metal)
        c.line([(8, 14), (12, 25)], shade(metal, -0.2))
        c.line([(19, 9), (22, 25)], shade(metal, -0.2))
        c.rect(14, 20, 20, 22, hexc("#a87838"))
        if t in (1, 3):
            sparkle_x = 19 if t == 1 else 9
            c.px(sparkle_x, 11 if t == 1 else 15, (255, 240, 140, 255))
            c.px(sparkle_x + 1, 10 if t == 1 else 14, (255, 255, 255, 255))
    else:  # a collapsed floor panel
        shadow(c, rx=13)
        c.poly([(4, 24), (6, 10), (27, 13), (28, 26)], shade(metal, 0.06))
        c.line([(6, 10), (27, 13)], shade(metal, 0.2))
        c.line([(10, 18), (24, 20)], shade(metal, -0.2))
        for x, y in ((8, 12), (25, 15), (9, 23), (26, 24)):
            c.px(x, y, hexc("#c8ccd4"))


# --- Kitchen Defense: things in the way ---------------------------------------



def heap(c, color, cx=16, cy=19, rx=12, ry=8):
    """A soft heap of loose stuff (flour, sugar, crumbs, confetti)."""
    shadow(c, cx, cy + 7, rx, 3)
    c.blob(cx, cy, rx, ry, color)
    c.blob(cx - 1, cy - ry * 0.5, rx * 0.6, ry * 0.5, shade(color, 0.08))


@obstacle("kitchen_defense/obstacle.png")
def shelf_clutter(c, v, t):
    if v == 0:  # a heap of spilled flour
        heap(c, hexc("#ece6dc"))
        speckles(c, [(8, 24), (25, 25), (12, 27)], hexc("#ece6dc"))
    elif v == 1:  # a heap of spilled dry spaghetti
        shadow(c, ry=3)
        pasta = hexc("#f0cc60")
        for k, (a, b) in enumerate((((4, 22), (27, 14)), ((5, 15), (28, 22)), ((7, 25), (25, 9)),
                                    ((3, 18), (29, 18)), ((9, 10), (24, 26)), ((6, 12), (26, 25)))):
            c.line([a, b], pasta if k % 2 == 0 else shade(pasta, -0.1), 2)
            c.line([a, b], shade(pasta, 0.15))
    else:  # a crumpled paper towel
        paper = hexc("#e8ecf0")
        heap(c, paper, rx=11, ry=9)
        c.line([(9, 15), (14, 19), (12, 23)], shade(paper, -0.2))
        c.line([(18, 12), (22, 18), (19, 24)], shade(paper, -0.2))


@obstacle("kitchen_defense/floor/obstacle.png")
def floor_clutter(c, v, t):
    if v == 0:  # a puddle of spilled milk
        milk = hexc("#f4f2ec")
        c.ellipse(16, 20, 13, 8, (0, 0, 0, 60))
        for x, y, rx, ry in ((14, 18, 11, 6.5), (22, 22, 6, 4), (7, 21, 5, 3.5)):
            c.ellipse(x, y, rx, ry, milk)
        c.ellipse(11, 16, 3, 1.2, (255, 255, 255, 255))
    elif v == 1:  # a pile of spilled cereal
        shadow(c, ry=3)
        for x, y in ((8, 21), (13, 18), (18, 20), (23, 22), (11, 24), (17, 25), (21, 16),
                     (15, 13), (25, 19), (9, 16)):
            c.ellipse(x, y, 2.6, 2, hexc("#d8a040"))
            c.px(x - 1, y - 1, hexc("#f0c870"))
    else:  # a dust bunny
        dust = hexc("#a8a4a0")
        heap(c, dust, rx=11, ry=8)
        for x, y in ((5, 18), (27, 17), (10, 11), (22, 10), (16, 9)):
            c.line([(16, 18), (x, y)], shade(dust, 0.1))


@obstacle("kitchen_defense/counter/obstacle.png")
def counter_clutter(c, v, t):
    if v == 0:  # a coffee spill
        coffee = hexc("#6a4228")
        for x, y, rx, ry in ((15, 18, 11, 7), (23, 22, 5, 4), (7, 15, 4, 3)):
            c.ellipse(x, y, rx, ry, coffee)
        c.ellipse(12, 16, 3, 1.2, shade(coffee, 0.2))
    elif v == 1:  # a pile of bread crumbs
        heap(c, hexc("#c89058"), rx=11, ry=7)
        speckles(c, [(9, 18), (14, 15), (19, 17), (22, 21), (12, 21)], hexc("#e8c088"))
        speckles(c, [(5, 25), (27, 24), (24, 27)], hexc("#c89058"))
    else:  # a ball of crumpled foil
        foil = hexc("#c8ccd4")
        shadow(c)
        c.blob(16, 17, 10, 9, foil)
        c.line([(10, 14), (15, 18), (13, 23)], shade(foil, -0.25))
        c.line([(18, 11), (21, 17), (24, 19)], shade(foil, -0.25))
        speckles(c, [(12, 12), (20, 21)], (255, 255, 255, 255))


# --- Birthday Bash: party clutter ---------------------------------------------

@obstacle("birthday_bash/obstacle.png")
def party_mess(c, v, t):
    if v == 0:  # a heap of torn wrapping paper
        paper = hexc("#e070a8")
        heap(c, paper, rx=12, ry=8)
        for x, y in ((10, 15), (16, 18), (22, 14), (13, 21)):
            c.px(x, y, hexc("#f4e060"))
            c.px(x + 1, y, hexc("#f4e060"))
        c.poly([(18, 9), (26, 12), (21, 16)], hexc("#60b0f0"))
    elif v == 1:  # a mound of confetti
        heap(c, hexc("#f4e8f0"), rx=12, ry=8)
        colors = ("#f06060", "#40a8f0", "#f0c030", "#60c050", "#b060f0")
        for k in range(22):
            x = 6 + (k * 7) % 21
            y = 13 + (k * 5) % 12
            c.rect(x, y, x + 1, y + 1, hexc(colors[k % 5]))
    else:  # a tangle of ribbon
        shadow(c)
        for k, color in enumerate(("#f06090", "#60b0f0")):
            points = [(6 + i * 2.2, 18 + math.sin(i * 1.3 + k * 2) * 7) for i in range(10)]
            c.line(points, hexc(color), 2)


@obstacle("birthday_bash/bouncy/obstacle.png")
def bouncy_clutter(c, v, t):
    if v == 0:  # a heap of ball-pit balls
        shadow(c, rx=13)
        colors = ("#e84040", "#40a0e8", "#f0c030", "#60c060")
        for k, (x, y) in enumerate(((7, 22), (14, 23), (21, 22), (26, 21), (10, 16), (17, 16), (23, 15), (14, 10))):
            c.ellipse(x, y, 3.6, 3.6, hexc(colors[k % 4]))
            c.px(x - 1, y - 1, (255, 255, 255, 220))
    elif v == 1:  # a beach ball
        shadow(c)
        c.ellipse(16, 16, 11.5, 11.5, hexc("#f4f0f0"))
        for k, color in enumerate(("#e84040", "#40a0e8", "#f0c030")):
            a = k * math.tau / 3
            c.poly([(16, 16), (16 + math.cos(a) * 11, 16 + math.sin(a) * 11),
                    (16 + math.cos(a + 1.05) * 11, 16 + math.sin(a + 1.05) * 11)], hexc(color))
        c.ellipse(16, 16, 2, 2, WHITE)
    else:  # a deflated balloon
        rubber = hexc("#e05080")
        c.ellipse(16, 21, 12, 5, (0, 0, 0, 60))
        c.blob(14, 19, 11, 6, rubber)
        c.ellipse(26, 19, 2, 1.5, shade(rubber, -0.2))
        c.line([(27, 19), (30, 24)], (230, 230, 230, 255))


@obstacle("birthday_bash/living/obstacle.png")
def living_clutter(c, v, t):
    if v == 0:  # a sofa cushion
        blue = hexc("#4a70c8")
        shadow(c, rx=13)
        c.blob(16, 17, 13, 10, blue)
        c.line([(16, 9), (16, 25)], shade(blue, -0.15))
        c.ellipse(16, 17, 1.5, 1.5, shade(blue, -0.25))
    elif v == 1:  # a bunched-up rug
        rug = hexc("#c05040")
        shadow(c, rx=13)
        for y in (11, 17, 23):
            c.blob(16, y, 13, 4, rug)
            c.line([(5, y), (27, y)], hexc("#f0d080"))
    else:  # a heap of streamers
        shadow(c)
        for k, color in enumerate(("#f06080", "#60c0f0", "#f0d040")):
            points = [(5 + i * 2.5, 20 - k * 4 + math.sin(i + k) * 3) for i in range(10)]
            c.line(points, hexc(color), 3)


# --- water --------------------------------------------------------------------

WATER = {"total_war/water_anim.png": "#68b8e8"}


def water(c, t, color):
    """A seamless 32x32 water tile with ripples drifting sideways."""
    base = hexc(color)
    c.rect(0, 0, 32, 32, base)
    for x0, y in ((2, 5), (18, 12), (6, 21), (22, 27)):
        x = (x0 + t * 2) % 32
        for k in range(5):
            c.px((x + k) % 32, y, shade(base, 0.2))
        c.px((x + 1) % 32, y - 1, shade(base, 0.12))
    for x0, y in ((12, 9), (28, 18), (3, 30)):
        c.px((x0 + t) % 32, y, WHITE)
