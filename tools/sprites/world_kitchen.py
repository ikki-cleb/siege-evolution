"""Kitchen Defense: enchanted kitchen gear against pantry pests (faces).

Redesigned (see world_backyard.py): bigger, richly detailed tools (shiny
metal, wood grain, labels). The creature-like helpers (sponge, sugar cube,
egg beater, toaster, soap bar, moldy bread) have cute faces; the rest are
objects. Power evolutions are pro-grade (marble, chrome, copper, cast iron,
bigger); utility evolutions get add-ons (handles, nozzles, longer reach).
"""
import math

from .hefty import glow, pc_mark, puffs, ring, tier
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, animal, bug, legs, phase, turret

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True

METAL = hexc("#b8bcc4")
CHROME = hexc("#d8dce4")
COPPER = hexc("#d07a40")
WOOD = hexc("#b08050")
MARBLE = hexc("#e8e4e0")


def shine(c, x, y0, y1, color=WHITE):
    """A vertical highlight streak on shiny metal."""
    c.line([(x, y0), (x, y1)], color)


def kface(c, x, y, p, gap=3):
    """A cute face for the living kitchen helpers."""
    c.eyes(x, y, gap, p.get("mood", "calm"), 2)
    c.mouth(x, y + 3, "open" if p.get("act") == "fire" else "smile", 3)


# --- Fortress -------------------------------------------------------------------

def tin_can(c, p):
    b = tier(p)
    cans = ((16, 30, 8, 18),) if b != 0 else ((9.5, 30, 6, 12), (22.5, 30, 6, 12), (16, 18, 6, 11))
    for x, y, w, h in cans:  # Stacked Cans: a pyramid of cans
        c.block(x - w, y - h, x + w, y, METAL)
        c.ellipse(x, y - h, w, 2, CHROME)
        c.rect(x - w, y - h * 0.7, x + w, y - h * 0.3, hexc("#c84a3a"))  # label
        c.ellipse(x, y - h * 0.5, w * 0.35, h * 0.12, hexc("#f0d040"))
        shine(c, x - w + 2, y - h + 2, y - 2)
    if b == 1:  # Jagged: the lid torn open in jagged teeth
        for x in range(9, 24, 3):
            c.poly([(x, 12), (x + 1.5, 6 - (x % 2) * 2), (x + 3, 12)], CHROME)
    pc_mark(c, 16, 26 if b != 0 else 28, p, 1.3)
    return (16, 11)


def rolling_pin(c, p):
    b = tier(p)
    body = WOOD if b != 0 else MARBLE
    length = 13 if b == 1 else 10
    roll = 1 if p.get("act") == "fire" else 0
    c.ellipse(16, 27, length + 4, 2.5, (0, 0, 0, 60))
    for side in (-1, 1):  # handles
        c.rect(16 + side * (length + 2) - 2, 17, 16 + side * (length + 2) + 2, 22, shade(WOOD, -0.15))
    c.block(16 - length, 13 - roll, 16 + length, 25 - roll, body)
    c.ellipse(16 - length, 19 - roll, 2, 6, shade(body, -0.15))
    c.ellipse(16 + length, 19 - roll, 2, 6, shade(body, -0.2))
    for x in range(16 - length + 3, 16 + length - 2, 4):  # grain / veins
        c.line([(x, 15 - roll), (x + 1, 23 - roll)], shade(body, -0.12) if b != 0 else hexc("#a8a8b8"))
    c.line([(16 - length + 1, 15 - roll), (16 + length - 1, 15 - roll)], shade(body, 0.2))
    pc_mark(c, 16, 21, p, 1.4)
    return (16, 11)


def cork_popper(c, p):
    b = tier(p)
    bottle = hexc("#3a6a3a") if b != 0 else hexc("#2a4a2a")
    pop = p.get("act") == "fire"
    c.block(10, 14, 22, 30, bottle)
    c.rect(13, 7, 19, 15, bottle)  # neck
    if b == 0:  # Champagne: gold foil and a label
        c.rect(12.5, 6, 19.5, 11, hexc("#e0b040"))
        c.rect(10, 19, 22, 25, hexc("#f4ecd8"))
        c.rect(12, 21, 20, 22, hexc("#c8a040"))
    else:
        c.rect(10, 20, 22, 25, hexc("#f4ecd8"))
    shine(c, 12, 15, 28, hexc("#80b080"))
    cork_y = 1 if pop else 4
    c.block(13.5, cork_y, 18.5, cork_y + 4, hexc("#c89a60"))  # cork
    if b == 1:  # Long: a long launch tube on top
        c.rect(14, -4 + cork_y, 18, cork_y, METAL)
    if pop:
        puffs(c, [(12, 3, 1.5), (20, 3, 1.5)], hexc("#f4f4f4", 220))
    pc_mark(c, 16, 28, p, 1.2)
    return (16, cork_y)


def sponge(c, p):
    b = tier(p)
    yellow = hexc("#f0d050") if b != 0 else hexc("#e0b030")
    top = 10 if b == 0 else 13
    if b == 1:  # Soaked: drips and bubbles
        for x in (7, 16, 25):
            c.rect(x, 29, x + 1.5, 32, hexc("#80c8f0"))
        for x, y in ((5, top - 2), (26, top - 4), (16, top - 6)):
            c.ellipse(x, y, 1.8, 1.8, hexc("#c8ecff"))
    c.block(4, top, 28, 30, yellow)
    c.rect(4, top, 28, top + 4, hexc("#4a9a4a"))  # green scrubber
    for x, y in ((8, top + 8), (20, top + 10), (13, top + 13), (24, top + 15), (9, top + 15)):
        c.ellipse(x, y, 1.4, 1.1, shade(yellow, -0.2))  # pores
    kface(c, 16, top + 9, p)
    pc_mark(c, 24, top + 6, p, 1.2)
    return (16, top - 2)


def pressure_cooker(c, p):
    b = tier(p)
    pot = METAL if b != 0 else CHROME
    w = 12 if b == 0 else 10.5
    c.ellipse(16, 29, w + 1, 2.5, shade(pot, -0.3))
    c.block(16 - w, 14, 16 + w, 29, pot)
    shine(c, 16 - w + 3, 16, 27)
    c.ellipse(16, 14, w, 3, shade(pot, 0.15))  # lid
    c.rect(14, 8, 18, 13, hexc("#3a3a40"))  # valve
    for side in (-1, 1):  # handles
        c.rect(16 + side * (w + 1) - 2, 17, 16 + side * (w + 1) + 2, 20, hexc("#2a2a30"))
    c.ellipse(16, 22, 3.5, 3.5, hexc("#2a2a30"))  # pressure gauge
    c.ellipse(16, 22, 2.4, 2.4, WHITE)
    c.line([(16, 22), (17.5, 20.5)], hexc("#e03030"))
    steam = p.get("act") != "idle" or b == 1
    if steam:  # Steam Jet: a steam column
        puffs(c, [(16, 5, 2.5), (14, 1, 2.2), (18, 0, 2)] if b == 1 else [(16, 5, 2.2)], hexc("#f4f4f8", 220))
    pc_mark(c, 9, 25, p, 1.2)
    return (16, 4)


def cast_iron_pan(c, p):
    b = tier(p)
    iron = hexc("#3a3a42") if b != 0 else hexc("#24242a")
    c.line([(25, 16), (31, 9)], iron, 4)  # handle
    c.ellipse(15, 20, 13, 9, shade(iron, -0.2))
    c.ellipse(14.5, 19.5, 12.5, 8.5, iron)
    c.ellipse(14.5, 19.5, 10, 6.5, shade(iron, 0.12))  # cooking surface
    if b == 1:  # Spiked Grill: grill ridges and spikes
        for x in range(7, 23, 3):
            c.line([(x, 15), (x + 1, 24)], shade(iron, 0.3))
        for x, y in ((3, 18), (27, 21), (14, 10)):
            c.poly([(x - 1.5, y + 1), (x + 1.5, y + 1), (x, y - 4)], CHROME)
    else:
        c.ellipse(11, 16, 3, 1.4, shade(iron, 0.35))  # oily shine
    pc_mark(c, 15, 21, p, 1.4)
    return (15, 11)


# --- Swarm --------------------------------------------------------------------

def sugar_cube(c, p):
    b = tier(p)
    sugar = hexc("#f8f8fc")
    cubes = ((16, 21, 10),) if b == 0 else ((10, 24, 6.5), (22, 24, 6.5), (16, 13, 6.5))
    if b == 1:  # Rock Candy: a crystal cluster
        for x, h, col in ((8, 14, "#f0a0d0"), (16, 20, "#a0d0f0"), (24, 15, "#d0b0f0")):
            c.poly([(x - 4, 30), (x + 4, 30), (x + 3, 30 - h), (x, 30 - h - 3), (x - 3, 30 - h)], hexc(col))
            c.line([(x - 1, 28), (x - 1, 30 - h)], WHITE)
        kface(c, 16, 18, p)
        pc_mark(c, 16, 25, p, 1.2)
        return (16, 7)
    for x, y, h in cubes:
        c.block(x - h, y - h, x + h, y + h, sugar)
        c.poly([(x - h, y - h), (x - h + 3, y - h - 3), (x + h + 3, y - h - 3), (x + h, y - h)], shade(sugar, -0.05))
        for k in range(4):
            c.px(x - h + 2 + k * 3, y - h + 2 + (k % 2) * 3, hexc("#e0e0ec"))  # sparkle grains
    kface(c, 16, 20 if b == 0 else 12, p)
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 9)


def fork(c, p):
    b = tier(p)
    metal = CHROME if b == 0 else METAL
    stab = -3 if p.get("act") == "fire" else 0
    length = 6 if b == 1 else 0
    c.block(13, 18 + stab, 19, 31, hexc("#5a3a2a"))  # handle
    for y in (21, 25, 29):
        c.px(16, y + stab, hexc("#e0b040"))  # rivets
    c.block(11, 12 + stab, 21, 19 + stab, metal)
    tines = (11.5, 14.5, 17.5, 20.5) if b != 0 else (11, 13.5, 16, 18.5, 21)
    for x in tines:
        c.rect(x - 0.8, 1 - length + stab, x + 0.8, 13 + stab, metal)
        c.px(x, 1 - length + stab, WHITE)
    shine(c, 12, 13 + stab, 18 + stab)
    pc_mark(c, 16, 15 + stab, p, 1.2)
    return (16, 1 - length + stab)


def spray_bottle(c, p):
    b = tier(p)
    bottle = hexc("#80c8f0", 235)
    nozzles = 2 if b == 0 else 1
    for k in range(nozzles):
        x = 16 + (k - (nozzles - 1) / 2) * 8
        c.block(x - 4, 5, x + 4, 11, hexc("#e0e0e8"))  # trigger head
        c.rect(x + 3, 6, x + 7 if b != 1 else x + 11, 8, hexc("#c84a3a"))  # nozzle (Jet: long)
        c.rect(x - 1, 11, x + 1, 15, hexc("#e0e0e8"))
    c.block(8, 14, 24, 30, bottle)
    c.rect(8, 18, 24, 26, hexc("#f4f4f8"))  # label
    c.rect(10, 21, 22, 22, hexc("#3a8ac8"))
    shine(c, 10, 15, 28)
    if p.get("act") == "fire":
        puffs(c, [(28, 7, 2)], hexc("#c8ecff", 220))
    pc_mark(c, 16, 28, p, 1.2)
    return (16, 4)


def egg_beater(c, p):
    b = tier(p)
    metal = CHROME if b == 0 else METAL
    spin = phase(p) if p.get("act") != "idle" else 0
    wide = 1.4 if b == 1 else 1.0
    for side in (-1, 1):  # whisk loops
        c.ellipse(16 + side * 4 * wide, 23 + (spin % 2), 4 * wide, 7, (0, 0, 0, 0))
        for a in range(14):
            ang = a * math.tau / 14
            c.px(16 + side * 4 * wide + math.cos(ang) * 3.5 * wide, 23 + math.sin(ang) * 6.5, metal)
    c.rect(14.5, 9, 17.5, 17, metal)
    c.ellipse(16, 8, 6.5, 6, hexc("#c84a3a") if b != 0 else COPPER)  # the face hub
    kface(c, 16, 7.5, p, 2.5)
    c.line([(22, 8), (27, 4)], WOOD, 2)  # crank
    c.ellipse(27, 4, 1.6, 1.6, shade(WOOD, -0.2))
    pc_mark(c, 16, 14, p, 1.2)
    return (16, 2)


def pizza_cutter(c, p):
    b = tier(p)
    blade = CHROME if b == 0 else METAL
    r = 10 if b == 0 else 8.5
    spin = phase(p)
    c.line([(16, 18), (26, 30)], hexc("#c84a3a"), 4)  # handle
    c.ellipse(13, 15, r, r, shade(blade, -0.2))
    c.ellipse(13, 15, r - 1, r - 1, blade)
    c.ellipse(13, 15, 3, 3, hexc("#5a5a60"))
    for a in range(4):  # spinning shine
        ang = a * math.pi / 2 + spin * 0.4
        c.px(13 + math.cos(ang) * (r - 2.5), 15 + math.sin(ang) * (r - 2.5), WHITE)
    if b == 1:  # Rolling: little wheels on the handle
        c.ellipse(25, 30, 2, 2, hexc("#3a3a40"))
    pc_mark(c, 22, 25, p, 1.2)
    return (13, 15 - r)


def cling_wrap(c, p):
    b = tier(p)
    film = hexc("#d8ecf4", 200)
    wide = 14 if b == 1 else 11
    c.block(3, 22, 29, 30, hexc("#c84a3a"))  # the box
    c.rect(3, 22, 29, 23, hexc("#e8a090"))
    c.rect(5, 25, 15, 27, WHITE)
    for k in range(2 if b == 0 else 1):  # sheets of film stretched up
        y = 8 - k * 3
        c.poly([(16 - wide, 22), (16 + wide, 22), (16 + wide - 2, y), (16 - wide + 2, y)], film)
        c.line([(16 - wide + 3, y + 2), (16 - wide + 5, 20)], WHITE)
    pc_mark(c, 24, 26, p, 1.2)
    return (16, 4)


# --- Precision ------------------------------------------------------------------

def cutting_board(c, p):
    b = tier(p)
    if b == 1:  # Cheese Grater: a steel grater
        c.poly([(7, 30), (10, 8), (22, 8), (25, 30)], CHROME)
        for y in range(11, 29, 4):
            for x in range(11, 22, 3):
                c.rect(x, y, x + 1.5, y + 1, OUTLINE)
        c.block(12, 3, 20, 8, hexc("#3a3a40"))
        pc_mark(c, 16, 26, p, 1.2)
        return (16, 2)
    wood = WOOD if b != 0 else hexc("#8a5a30")
    top = 9 if b == 0 else 12
    c.block(3, top, 29, 30, wood)
    for y in range(top + 2, 30, 3):
        c.line([(4, y), (28, y + (y % 2))], shade(wood, -0.12))
    if b == 0:  # Butcher Block: end-grain squares
        for x in range(5, 28, 6):
            c.line([(x, top), (x, 29)], shade(wood, -0.2))
    c.ellipse(24, top + 3, 2, 2, shade(wood, -0.35))  # hanging hole
    for x, y in ((9, top + 8), (15, top + 12)):  # knife marks
        c.line([(x, y), (x + 5, y + 2)], shade(wood, -0.25))
    pc_mark(c, 16, top + 14, p, 1.2)
    return (16, top - 2)


def pepper_grinder(c, p):
    b = tier(p)
    wood = hexc("#5a3a2a") if b != 0 else hexc("#8a2a2a")
    tall = 5 if b == 1 else 0
    turn = phase(p) % 2 if p.get("act") != "idle" else 0
    c.ellipse(16, 30, 7, 2, (0, 0, 0, 70))
    c.block(10, 14 - tall, 22, 30, wood)
    c.ellipse(16, 22, 7, 4, shade(wood, 0.1))  # waist bulge
    c.block(11, 6 - tall + turn, 21, 14 - tall, shade(wood, -0.1))  # cap
    c.ellipse(16, 4 - tall + turn, 2, 2, CHROME)  # finial
    shine(c, 12, 15 - tall, 28, shade(wood, 0.3))
    if b == 0:  # Ghost Pepper: a fiery red with chili mark
        c.poly([(14, 19), (19, 18), (16, 24)], hexc("#f05030"))
    if p.get("act") == "fire":
        for x in (13, 16, 19):
            c.px(x, 31, OUTLINE)
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 3 - tall)


def flour_sifter(c, p):
    b = tier(p)
    metal = CHROME if b == 0 else METAL
    w = 11 if b == 0 else 9.5
    c.block(16 - w, 9, 16 + w, 24, metal)
    c.ellipse(16, 9, w, 2.5, shade(metal, 0.15))
    c.ellipse(16, 9, w - 2, 1.6, hexc("#f4f0e8"))  # flour inside
    shine(c, 16 - w + 2, 11, 22)
    c.line([(16 + w, 12), (16 + w + 5, 14), (16 + w, 20)], hexc("#c84a3a"), 2)  # crank handle
    reach = 7 if b == 1 else 3
    for k in range(5):  # flour falling
        c.px(9 + k * 3.5, 25 + (phase(p) + k) % reach, hexc("#f4f0e8"))
    pc_mark(c, 16, 18, p, 1.3)
    return (16, 7)


def mousetrap(c, p):
    b = tier(p)
    wood = hexc("#c89a60")
    big = b == 0
    w = 13 if big else 11
    c.block(16 - w, 17, 16 + w, 29, wood)  # base
    c.line([(16 - w + 2, 19), (16 + w - 2, 19)], shade(wood, 0.15))
    snap = p.get("act") == "fire"
    bar_y = 18 if snap else 10
    c.line([(16 - w + 3, 27), (16 - w + 3, bar_y), (16 + w - 3, bar_y), (16 + w - 3, 27)], CHROME, 2)  # snap bar
    c.ellipse(16, 23, 3, 2, hexc("#f0d050"))  # cheese bait
    if b == 1:  # Swatter: a fly swatter attached
        c.line([(28, 28), (28, 10)], hexc("#3a8a3a"), 2)
        c.block(24, 2, 31, 10, hexc("#4ab04a"))
    pc_mark(c, 16 - w + 4, 22, p, 1.2)
    return (16, 9)


def toaster(c, p):
    b = tier(p)
    body = CHROME if b == 0 else METAL
    w = 13 if b == 0 else 11
    pop = -4 if p.get("act") == "fire" else 0
    slots = 4 if b == 0 else 2
    for k in range(slots):  # toast popping out
        x = 16 + (k - (slots - 1) / 2) * (2 * w / slots)
        c.block(x - 2.5, 8 + pop, x + 2.5, 14, hexc("#d8a060"))
        c.rect(x - 2.5, 8 + pop, x + 2.5, 9 + pop, hexc("#a06030"))
    c.block(16 - w, 12, 16 + w, 30, body)
    shine(c, 16 - w + 2, 14, 28)
    kface(c, 16, 21, p)
    c.rect(16 + w, 16, 16 + w + 2, 19, OUTLINE)  # lever
    if b == 1:  # Turbo: flame decals
        for x in (8, 22):
            c.poly([(x - 2, 28), (x, 23), (x + 2, 28)], hexc("#f08030"))
    pc_mark(c, 16 - w + 3, 27, p, 1.2)
    return (16, 7 + pop)


def kitchen_lamp(c, p):
    b = tier(p)
    tall = 5 if b == 1 else 0
    bright = b == 0 or p.get("act") != "idle"
    if bright:
        glow(c, 16, 19 - tall, 13, hexc("#fff0a0"))
    c.line([(16, 0), (16, 9 - tall)], OUTLINE)  # cord
    c.poly([(5, 20 - tall), (10, 9 - tall), (22, 9 - tall), (27, 20 - tall)], COPPER if b == 0 else hexc("#3a8a6a"))
    c.line([(10, 10 - tall), (22, 10 - tall)], shade(COPPER, 0.25))
    c.ellipse(16, 21 - tall, 4, 2.5, hexc("#fff8c0"))  # bulb
    if bright:
        c.poly([(9, 22 - tall), (23, 22 - tall), (27, 31), (5, 31)], hexc("#fff4b0", 120))
    pc_mark(c, 16, 14 - tall, p, 1.2)
    return (16, 6 - tall)


# --- Control --------------------------------------------------------------------

def flypaper(c, p):
    b = tier(p)
    paper = hexc("#e8c860")
    strips = 2 if b == 0 else 1
    for k in range(strips):
        x = 16 + (k - (strips - 1) / 2) * 10
        c.line([(x, 0), (x, 4)], OUTLINE)
        c.block(x - 4, 4, x + 4, 30, paper)
        for y in range(7, 29, 4):
            c.line([(x - 4, y), (x + 3, y + 1)], shade(paper, -0.12))
        for fx, fy in ((x - 2, 12), (x + 2, 20), (x - 1, 26)):  # stuck flies
            c.ellipse(fx, fy, 1.4, 1, OUTLINE)
            c.px(fx, fy - 1.2, hexc("#e8f0ff"))
    if b == 1:  # Extra-Sticky: glue drips
        for x in (13, 19):
            c.rect(x, 29, x + 1.5, 32, hexc("#f0d070", 230))
    pc_mark(c, 16, 9, p, 1.2)
    return (16, 1)


def ice_tray(c, p):
    b = tier(p)
    tray = hexc("#80b8e8")
    wide = 14 if b == 1 else 12
    c.block(16 - wide, 15, 16 + wide, 29, tray)
    cols = 4 if b == 1 else 3
    for row in range(2):
        for k in range(cols):
            x = 16 - wide + 2 + k * (2 * wide - 2) / cols
            c.block(x, 16 + row * 6.5, x + (2 * wide - 6) / cols, 21 + row * 6.5, hexc("#e8f8ff"))
            c.px(x + 1, 17 + row * 6.5, WHITE)
    if b == 0:  # Frosty: frost spikes and a cold mist
        for x in (6, 16, 26):
            c.poly([(x - 2, 15), (x + 2, 15), (x, 9)], hexc("#e8f8ff"))
    for k in range(3):
        c.px(8 + k * 8, 10 + (phase(p) + k) % 3, WHITE)
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 8)


def ketchup_squirter(c, p):
    b = tier(p)
    sauce = hexc("#d83a2a") if b != 0 else hexc("#e05010")
    squeeze = 1 if p.get("act") != "idle" else 0
    nozzle = 8 if b == 1 else 4
    c.poly([(14, 8), (18, 8), (17, 8 - nozzle), (15, 8 - nozzle)], hexc("#f4f4f4"))  # nozzle (Long: longer)
    c.block(10, 8, 22, 12, hexc("#f4f4f4"))  # cap
    c.blob(16, 21, 8 - squeeze, 10, sauce)  # squeeze bottle
    c.rect(9, 18, 23, 24, hexc("#f4ecd8"))  # label
    if b == 0:  # Hot Sauce: a chili on the label
        c.poly([(13, 20), (19, 19), (16, 23)], hexc("#3a8a3a"))
    else:
        c.ellipse(16, 21, 2.5, 1.6, hexc("#3a8a3a"))
    shine(c, 11, 13, 29, shade(sauce, 0.3))
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 8 - nozzle)


def stove_burner(c, p):
    b = tier(p)
    wide = 13 if b == 1 else 11
    lit = p.get("act") != "idle" or b == 0
    c.ellipse(16, 23, wide + 2, 6, hexc("#2a2a30"))  # grate
    for a in range(6):
        ang = a * math.pi / 3
        c.line([(16, 23), (16 + math.cos(ang) * (wide + 1), 23 + math.sin(ang) * 5.5)], hexc("#5a5a60"), 2)
    flame_h = 9 if b == 0 else 5
    for k in range(8):  # ring of blue flames
        ang = k * math.tau / 8
        x, y = 16 + math.cos(ang) * (wide - 4), 23 + math.sin(ang) * 3
        h = flame_h if lit else 2
        c.poly([(x - 1.5, y), (x, y - h - (phase(p) + k) % 2), (x + 1.5, y)], hexc("#60a8ff"))
        c.px(x, y - 1, hexc("#c0e0ff"))
    c.rect(26, 28, 30, 31, hexc("#5a5a60"))  # knob
    return (16, 23 - flame_h - 6)


def bug_zapper(c, p):
    b = tier(p)
    glow(c, 16, 17, 12 if b == 0 else 9, hexc("#a080ff"))
    w = 9 if b == 0 else 7.5
    c.block(16 - w, 6, 16 + w, 28, hexc("#3a3a42"))  # cage
    for x in range(int(16 - w + 2), int(16 + w - 1), 2):
        c.line([(x, 8), (x, 26)], hexc("#c0a8ff"))
    c.rect(14, 2, 18, 6, hexc("#3a3a42"))  # hanger ring
    zap = p.get("act") != "idle" or b == 0
    if zap:
        c.line([(10, 12), (14, 16), (12, 20), (17, 24)], WHITE)
    if b == 1:  # Chain: arcs jumping out
        for d in (-1, 1):
            c.line([(16 + d * w, 15), (16 + d * (w + 4), 12), (16 + d * (w + 6), 16)], hexc("#c0a8ff"))
    pc_mark(c, 16, 26, p, 1.2)
    return (16, 2)


def hot_griddle(c, p):
    b = tier(p)
    iron = hexc("#3a3a42")
    wide = 14 if b == 1 else 12
    hot = b == 0 or p.get("act") != "idle"
    if hot:
        glow(c, 16, 21, 14, hexc("#ff8040"))
    c.block(16 - wide, 17, 16 + wide, 27, iron)
    c.rect(16 - wide, 17, 16 + wide, 18, shade(iron, 0.3))
    for x in range(int(16 - wide + 3), int(16 + wide), 4):  # sear lines
        c.line([(x, 19), (x + 2, 25)], hexc("#c84a2a") if hot else shade(iron, 0.2))
    for x in (16 - wide, 16 + wide):  # legs
        c.rect(x - 1, 27, x + 1, 30, iron)
    if hot:  # heat shimmer
        for x in (9, 16, 23):
            c.line([(x, 15), (x - 1, 12), (x + 1, 9)], hexc("#ffb060"))
    pc_mark(c, 16, 22, p, 1.2)
    return (16, 10)


# --- Toxin ----------------------------------------------------------------------

def soap_bar(c, p):
    b = tier(p)
    soap = hexc("#f0a0c8") if b != 1 else hexc("#e8d8a0")  # Lye: yellowish
    big = b == 0
    w, top = (13, 11) if big else (11, 14)
    for x, y, r in ((5, top - 2, 2.2), (26, top - 4, 2.8), (16, top - 7, 2)):  # bubbles
        c.ellipse(x, y, r, r, hexc("#e8f4ff", 220))
        c.px(x - 0.6, y - 0.6, WHITE)
    c.blob(16, top + 8, w, 8, soap)
    c.ellipse(11, top + 4, 3.5, 1.4, shade(soap, 0.25))
    kface(c, 16, top + 8, p)
    pc_mark(c, 24, top + 11, p, 1.2)
    return (16, top - 9)


def bug_spray(c, p):
    b = tier(p)
    can = hexc("#3aa04a") if b != 0 else hexc("#e8c030")
    c.block(9, 9, 23, 30, can)
    c.ellipse(16, 9, 7, 2, shade(can, 0.2))
    c.rect(13, 4, 19, 9, CHROME)  # cap and nozzle
    nozzle = 9 if b == 1 else 4
    c.rect(19, 5, 19 + nozzle, 7, OUTLINE)
    c.rect(9, 15, 23, 24, hexc("#f4f4f4"))  # label with a crossed-out bug
    c.ellipse(16, 19.5, 3, 2.2, OUTLINE)
    c.line([(11, 15), (21, 24)], hexc("#e03030"), 2)
    shine(c, 11, 10, 28)
    if p.get("act") == "fire":
        puffs(c, [(19 + nozzle + 3, 5, 2.2)], hexc("#c8f070", 210))
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 3)


def pest_mister(c, p):
    b = tier(p)
    tank = hexc("#5a8ac8") if b != 0 else hexc("#3a5a8a")
    c.blob(16, 21, 10, 9, tank)  # pump tank
    c.rect(14.5, 6, 17.5, 13, CHROME)  # pump handle
    c.rect(11, 5, 21, 7, OUTLINE)
    c.line([(24, 18), (29, 12), (28, 6)], OUTLINE, 2)  # wand
    shine(c, 10, 15, 27, shade(tank, 0.3))
    mist = b is not None or p.get("act") == "fire"
    if mist:  # Fine/Caustic mist
        col = hexc("#c8f070", 200) if b == 0 else hexc("#d8ecf4", 200)
        puffs(c, [(28, 3, 2.5), (24, 1, 2), (31, 6, 2)], col)
    pc_mark(c, 16, 24, p, 1.3)
    return (16, 4)


def vinegar_bowl(c, p):
    b = tier(p)
    bowl = hexc("#f4f0e8") if b != 0 else hexc("#a8c8e8")
    wide = 14 if b == 1 else 12
    c.ellipse(16, 29, wide - 3, 2.5, (0, 0, 0, 60))
    c.poly([(16 - wide, 17), (16 + wide, 17), (16 + wide - 4, 28), (16 - wide + 4, 28)], bowl)
    c.ellipse(16, 17, wide, 3.5, shade(bowl, -0.1))
    c.ellipse(16, 17, wide - 1.5, 2.5, hexc("#e8d870"))  # vinegar
    if b == 0:  # Pickling: pickles floating
        for x in (11, 20):
            c.ellipse(x, 16.5, 2.5, 1.2, hexc("#5a8a3a"))
    if b == 1:  # Overflowing: running over the rim
        for x in (4, 27):
            c.rect(x, 17, x + 1.5, 25, hexc("#e8d870"))
    for x in (10, 22):  # sour fumes
        c.line([(x, 13), (x - 1, 9), (x + 1, 6)], hexc("#e8e8a0"))
    pc_mark(c, 16, 23, p, 1.2)
    return (16, 6)


def ant_bait_station(c, p):
    b = tier(p)
    shell = hexc("#2a2a30") if b != 0 else hexc("#c84a3a")
    wide = 13 if b == 0 else 11
    c.ellipse(16, 28, wide + 1, 3, (0, 0, 0, 70))
    c.blob(16, 22, wide, 7, shell)  # the bait disc
    for a in range(4):  # entry holes
        ang = a * math.pi / 2 + 0.4
        c.ellipse(16 + math.cos(ang) * (wide - 3), 22 + math.sin(ang) * 4, 1.6, 1.2, OUTLINE)
    c.ellipse(16, 20, 4, 2.5, hexc("#e8c040"))  # bait window
    if b == 1:  # Long: a tall spike stake
        c.rect(15, 4, 17, 16, CHROME)
        c.poly([(13, 4), (19, 4), (16, 0)], CHROME)
    pc_mark(c, 22, 25, p, 1.2)
    return (16, 12)


def moldy_bread(c, p):
    b = tier(p)
    crust = hexc("#c08040") if b != 0 else hexc("#8a6030")
    c.block(5, 13, 27, 30, crust)
    c.ellipse(16, 13, 11, 6, crust)  # domed top
    c.block(7, 15, 25, 28, hexc("#f0dcb0") if b != 0 else hexc("#d8c090"))  # crumb face
    spots = ((10, 18), (20, 23), (13, 25), (22, 17))
    if b == 1:  # Fuzzy: a lot of fuzzy mold
        spots = spots + ((8, 24), (17, 19), (24, 26), (12, 11), (20, 10))
    for x, y in spots:
        c.blob(x, y, 2.5, 2, hexc("#7ac050") if b != 0 else hexc("#5a7a8a"))
        c.px(x - 1, y - 1, hexc("#b0e080"))
    kface(c, 16, 20, p)
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 7)


DESIGNS = {
    "platelet_clot": tin_can, "macrophage": rolling_pin, "dendritic_cell": cork_popper, "fibroblast": sponge,
    "eosinophil": pressure_cooker, "granuloma": cast_iron_pan, "epithelial_cell": sugar_cube, "neutrophil": fork,
    "monocyte": spray_bottle, "basophil": egg_beater, "nk_cell": pizza_cutter, "net_trap": cling_wrap,
    "keratin_plate": cutting_board, "b_cell": pepper_grinder, "antibody_tagger": flour_sifter, "cytotoxic_t": mousetrap,
    "opsonin_lance": toaster, "interferon_beacon": kitchen_lamp, "mucus_wall": flypaper, "mast_cell": ice_tray,
    "histamine_spitter": ketchup_squirter, "fever_node": stove_burner, "cytokine_storm": bug_zapper,
    "inflammation_zone": hot_griddle, "toxic_membrane": soap_bar, "killer_t": bug_spray, "complement_sprayer": pest_mister,
    "lysozyme_pool": vinegar_bowl, "perforin_lancer": ant_bait_station, "necrosis_bloom": moldy_bread,
}


# --- Enemies: pantry pests (faces) -------------------------------------------------

def _pest_bug(color, **kw):
    def design(c, p):
        bob = (0, -1, 0, 0)[phase(p)]
        c.dy += bob
        bug(c, dict(p, mood="angry"), hexc(color), **kw)
        c.dy -= bob
    return design


def _rodent(fur, size=0.8, crown=False):
    def design(c, p):
        bob = (0, -1, 0, -1)[phase(p)]
        c.dy += bob
        animal(c, dict(p, mood="angry"), hexc(fur), ears="round", snout=hexc("#f0b8c0"), size=size)
        c.line([(16 + 6 * size, 27), (16 + 11 * size, 25 - bob)], hexc("#e0a0a8"))
        if crown:
            c.poly([(10, 7), (12, 3), (14, 6), (16, 2), (18, 6), (20, 3), (22, 7)], hexc("#ffd23c"))
        c.dy -= bob
    return design


def slug(c, p):
    stretch = (0, 1, 0, -1)[phase(p)]
    c.ellipse(16, 25, 11 + stretch, 4.5, hexc("#a89a5a"))
    c.blob(23 + stretch, 21, 4.5, 4, hexc("#b8aa6a"))
    c.line([(22 + stretch, 17), (21 + stretch, 13)], hexc("#7a6a3a"))
    c.line([(25 + stretch, 17), (26 + stretch, 13)], hexc("#7a6a3a"))
    c.eyes(23 + stretch, 20, 1.6, "angry")
    c.rect(4, 29, 14, 30, hexc("#d8c890", 160))


def honey_ant(c, p):
    bob = (0, -1, 0, 0)[phase(p)]
    c.dy += bob
    bug(c, dict(p, mood="angry"), hexc("#e8a830"), head=hexc("#6a4a20"), rx=8.5, ry=7.5, spots=hexc("#ffe080"))
    c.dy -= bob


def _nest(color):
    def design(c, p):
        c.blob(16, 21, 11, 9, hexc("#c8a868"))
        for x, y in ((10, 19), (21, 18), (16, 25)):
            c.ellipse(x, y, 2.6, 2.4, hexc(color))
            c.eyes(x, y - 0.5, 1, "calm", 1)
    return design


ENEMIES = {
    "mouse": _rodent("#a89888", 0.65), "rat": _rodent("#6a6070", 0.8),
    "sugar_ant": _pest_bug("#3a2a20", rx=5.5, ry=5), "fire_ant": _pest_bug("#c03a20", rx=6, ry=5.5),
    "slug": slug, "honey_ant": honey_ant,
    "mouse_nest": _nest("#a89888"), "rat_nest": _nest("#5a5060"),
    "cockroach": _pest_bug("#7a4a22", rx=8, ry=7), "giant_roach": _pest_bug("#4a2a12", rx=9.5, ry=8),
    "fruit_fly": _pest_bug("#c08040", rx=4, ry=4, wings=hexc("#d8eaf8", 200), legs_n=4),
    "housefly": _pest_bug("#3a3a40", rx=5.5, ry=5, wings=hexc("#d8eaf8", 200), legs_n=4),
    "rat_king": _rodent("#6a6070", 1.2, crown=True),
}
