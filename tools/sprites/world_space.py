"""World 5 (Galactic Siege): a chunky armored sci-fi defense force against
aliens (the aliens have faces).

Redesigned (see world_backyard.py): heavy armor plates, glowing energy
cores, hazard stripes and distinct silhouettes (walking mechs, tracked
turrets, hovering drones, tall pylons). Robots, mechs, drones and turrets
have cute LED eyes on a dark visor; walls, pylons and vents are faceless.
Power evolutions add armor, bigger cores and heavier cannons; utility
evolutions add antennas, longer barrels, thrusters and dishes.
"""
import math

from .hefty import glow, pc_mark, puffs, ring, tier
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, bug, legs, phase, robot, turret

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True

HULL = hexc("#8a94a8")
DARK = hexc("#3a4050")
CYAN = hexc("#60f0ff")
HAZARD = hexc("#f0c030")


def rivets(c, points):
    for x, y in points:
        c.px(x, y, shade(HULL, 0.35))


def visor(c, x, y, w=4.5, color=CYAN, mood="calm"):
    """A dark visor with two glowing LED eyes."""
    c.rect(x - w, y - 1.8, x + w, y + 1.8, hexc("#14181f"))
    if mood in ("closed", "squint"):
        c.rect(x - 2.5, y, x - 1, y + 0.6, color)
        c.rect(x + 1, y, x + 2.5, y + 0.6, color)
    else:
        c.rect(x - 2.6, y - 0.8, x - 1.2, y + 0.8, color)
        c.rect(x + 1.2, y - 0.8, x + 2.6, y + 0.8, color)


def core(c, x, y, r, color=CYAN, p=None):
    """A glowing energy core."""
    c.ellipse(x, y, r + 1, r + 1, DARK)
    c.ellipse(x, y, r, r, shade(color, -0.25))
    pulse = 0.4 if p and phase(p) % 2 else 0
    c.ellipse(x, y, r * (0.6 + pulse * 0.3), r * (0.6 + pulse * 0.3), color)
    c.px(x - r * 0.3, y - r * 0.3, WHITE)


def hazard_stripes(c, x0, y0, x1, y1):
    c.rect(x0, y0, x1, y1, OUTLINE)
    for x in range(int(x0), int(x1), 4):
        c.poly([(x, y1), (x + 2, y1), (x + 4, y0), (x + 2, y0)], HAZARD)


def armor_plate(c, top, color, double=False):
    c.block(3, top, 29, 30, color)
    c.rect(3, top, 29, top + 1, shade(color, 0.2))
    rivets(c, [(5, top + 2), (27, top + 2), (5, 28), (27, 28), (16, top + 2)])
    if double:
        c.block(6, top + 4, 26, 27, shade(color, -0.1))
        rivets(c, [(8, top + 6), (24, top + 6), (8, 25), (24, 25)])


def tracked_turret(c, p, hull, barrel_len=10, barrel_w=4, barrels=1, core_color=CYAN, core_r=2.5, y=17, armor=False):
    """A tracked turret: a tank-tread base, an armored head with a visor,
    and barrel(s)."""
    recoil = 2 if p.get("act") == "fire" else 0
    c.block(3, y + 7, 29, y + 13, DARK)  # treads
    for x in range(5, 28, 4):
        c.ellipse(x, y + 10, 1.4, 1.4, shade(DARK, 0.3))
    for k in range(barrels):
        bx = 16 + (k - (barrels - 1) / 2) * (barrel_w + 2)
        c.rect(bx - barrel_w / 2, y - barrel_len + recoil, bx + barrel_w / 2, y, shade(hull, -0.35))
        c.rect(bx - barrel_w / 2 + 0.5, y - barrel_len + recoil, bx - barrel_w / 2 + 1.5, y, shade(hull, 0.1))
        c.rect(bx - barrel_w / 2 - 1, y - barrel_len + recoil, bx + barrel_w / 2 + 1, y - barrel_len + 2 + recoil,
               shade(hull, -0.5))
    c.block(6, y - 3, 26, y + 8, hull)  # armored head
    if armor:
        c.block(4, y - 1, 8, y + 8, shade(hull, -0.15))
        c.block(24, y - 1, 28, y + 8, shade(hull, -0.15))
    visor(c, 16, y + 1, 5, mood=p.get("mood", "calm"))
    core(c, 16, y + 5.5, core_r, core_color, p)
    if p.get("act") == "fire":
        c.ellipse(16, y - barrel_len - 1, 2, 2, core_color)
    return (16, y - barrel_len)


def mech(c, p, hull, x=16, y=16, size=1.0, arms="fists", armor=False):
    """A walking mech: thick legs, a boxy armored body, a visor, arms."""
    s = size
    step = (0, 1, 0, -1)[phase(p)] * 0.6
    for side, lift in ((-1, step), (1, -step)):
        c.block(x + side * 5 * s - 2.5 * s, y + 7 * s, x + side * 5 * s + 2.5 * s, y + 14 * s + lift, shade(hull, -0.2))
        c.rect(x + side * 5 * s - 3.5 * s, y + 13 * s + lift, x + side * 5 * s + 3.5 * s, y + 14.5 * s + lift, DARK)
    c.block(x - 8 * s, y - 4 * s, x + 8 * s, y + 8 * s, hull)
    hazard_stripes(c, x - 8 * s, y + 6 * s, x + 8 * s, y + 8 * s)
    visor(c, x, y - 0.5 * s, 5.5 * s, mood=p.get("mood", "calm"))
    core(c, x, y + 3.5 * s, 2 * s, CYAN, p)
    punch = -3 if p.get("act") == "fire" else 0
    for side in (-1, 1):
        if armor:
            c.block(x + side * 9 * s - 3.5 * s, y - 6 * s, x + side * 9 * s + 3.5 * s, y - 1 * s, shade(hull, -0.1))
            rivets(c, [(x + side * 9 * s, y - 4 * s)])
        if arms == "fists":
            c.rect(x + side * 10 * s - 1.5, y - 2 * s, x + side * 10 * s + 1.5, y + 5 * s, shade(hull, -0.25))
            c.block(x + side * 10 * s - 3 * s, y + 4 * s + punch * (side > 0), x + side * 10 * s + 3 * s,
                    y + 9 * s + punch * (side > 0), shade(hull, 0.05))
        elif arms == "blades":
            c.line([(x + side * 9 * s, y), (x + side * 13 * s, y - 8 * s + punch)], hexc("#e0e8f4"), 2)
        elif arms == "tank":
            c.block(x + side * 10 * s - 2.5, y - 2 * s, x + side * 10 * s + 2.5, y + 6 * s, hexc("#9ad040"))
    return (x, y - 4 * s)


def drone(c, p, hull, x=16, y=14, size=1.0, rotors=True):
    """A hovering drone with rotors and a visor."""
    s = size
    hover = (0, -1, 0, 1)[phase(p)]
    if rotors:
        for side in (-1, 1):
            c.line([(x, y + hover), (x + side * 10 * s, y - 4 * s + hover)], DARK, 2)
            c.ellipse(x + side * 10 * s, y - 5 * s + hover, 5 * s, 1.4, (220, 230, 240, 200))
    c.blob(x, y + 2 * s + hover, 8 * s, 6.5 * s, hull)
    visor(c, x, y + 1.5 * s + hover, 5 * s, mood=p.get("mood", "calm"))
    c.ellipse(x, 31, 7 * s, 1.4, (0, 0, 0, 90))
    return (x, y - 6 * s + hover)


# --- Fortress -------------------------------------------------------------------

def hull_plate(c, p):
    b = tier(p)
    top = 9 if b == 0 else 12
    armor_plate(c, top, HULL, double=b == 0)
    hazard_stripes(c, 3, 27, 29, 30)
    if b == 1:  # Spiked: steel spikes on top
        for x in (6, 12, 20, 26):
            c.poly([(x - 2, top), (x + 2, top), (x, top - 6)], hexc("#c8d0dc"))
    pc_mark(c, 16, top + 7, p, 1.4)
    return (16, top - 2)


def mech_brawler(c, p):
    b = tier(p)
    top = mech(c, p, HULL if b != 0 else hexc("#6a7488"), armor=b == 0, size=1.0)
    if b == 1:  # Shockwave: shock rings around the fists
        ring(c, 6, 21, 4, 3, CYAN, 12)
        ring(c, 26, 21, 4, 3, CYAN, 12)
    pc_mark(c, 16, 12, p, 1.2)
    return top


def plasma_cannon(c, p):
    b = tier(p)
    return tracked_turret(c, p, HULL, barrel_len=14 if b == 1 else 9, barrel_w=6 if b == 0 else 5,
                          core_color=hexc("#c070ff"), core_r=3 if b == 0 else 2.2, armor=b == 0)


def nanite_wall(c, p):
    b = tier(p)
    top = 9 if b == 0 else 12
    c.block(3, top, 29, 30, DARK)
    for y in range(top + 1, 29, 4):  # a wall of little nanite cubes
        for x in range(4 + (y // 4 % 2) * 2, 28, 4):
            c.rect(x, y, x + 3, y + 3, shade(HULL, ((x + y) % 3 - 1) * 0.08))
            c.px(x + 1, y + 1, CYAN if (x * 3 + y + phase(p)) % 11 == 0 else shade(HULL, 0.25))
    if b == 1:  # Rapid: loose nanites swirling above
        for k in range(5):
            c.rect(6 + k * 5, top - 4 - (k + phase(p)) % 3, 8 + k * 5, top - 2 - (k + phase(p)) % 3, HULL)
    pc_mark(c, 16, 27, p, 1.3)
    return (16, top - 2)


def rail_cannon(c, p):
    b = tier(p)
    top = tracked_turret(c, p, hexc("#a0a8b8"), barrel_len=17 if b == 1 else 13, barrel_w=3 if b != 0 else 4,
                         barrels=2, armor=b == 0)
    for x in (13.5, 18.5):  # charged rails
        c.px(x, 6 if b == 1 else 9, CYAN)
    return top


def fortress_core(c, p):
    b = tier(p)
    glow(c, 16, 15, 13, CYAN)
    c.block(4, 22, 28, 30, DARK)  # cradle
    hazard_stripes(c, 4, 27, 28, 30)
    for side in (-1, 1):
        c.block(16 + side * 11 - 2.5, 8, 16 + side * 11 + 2.5, 24, HULL if b != 0 else hexc("#6a7488"))
    r = 8 if b == 0 else 7
    core(c, 16, 15, r, CYAN, p)
    if b == 0:  # Hardened: armor bands across the core
        c.rect(7, 14, 25, 16, hexc("#6a7488"))
    if b == 1:  # Spiked: spikes on the pylons
        for side in (-1, 1):
            c.poly([(16 + side * 11 - 2, 8), (16 + side * 11 + 2, 8), (16 + side * 11, 2)], hexc("#c8d0dc"))
    pc_mark(c, 16, 25, p, 1.3)
    return (16, 6)


# --- Swarm --------------------------------------------------------------------

def scrap_barrier(c, p):
    b = tier(p)
    pieces = ((9, 24, 6, 4, "#7a8090"), (22, 24, 6, 4.5, "#8a7a6a"), (15, 17, 7, 4, "#6a7080"), (24, 15, 4, 3, "#9a8a7a"),
              (7, 15, 4, 3, "#7a8a9a"))
    for x, y, w, h, col in pieces:
        c.block(x - w, y - h, x + w, y + h, hexc(col))
        c.px(x - w + 1, y - h + 1, shade(hexc(col), 0.3))
    if b == 0:  # Welded: weld seams
        for x, y in ((15, 21), (19, 19), (11, 17)):
            c.line([(x - 2, y), (x + 2, y)], hexc("#f0c060"))
    if b == 1:  # Spiked: jagged metal spikes
        for x in (5, 12, 20, 27):
            c.poly([(x - 1.5, 13), (x + 1.5, 13), (x + 0.5, 6)], hexc("#c8d0dc"))
    pc_mark(c, 16, 27, p, 1.3)
    return (16, 10)


def buzz_bot(c, p):
    b = tier(p)
    body = HULL if b != 0 else hexc("#c85a4a")
    spin = phase(p)
    saws = 2 if b == 0 else 1
    for k in range(saws):  # buzz saws
        sx = 16 + (k - (saws - 1) / 2) * 12
        c.ellipse(sx, 9, 5, 5, hexc("#c8d0dc"))
        for a in range(6):
            ang = a * math.pi / 3 + spin * 0.4
            c.px(sx + math.cos(ang) * 5.5, 9 + math.sin(ang) * 5.5, hexc("#e8eef4"))
        c.ellipse(sx, 9, 1.4, 1.4, DARK)
    c.block(9, 13, 23, 26, body)
    visor(c, 16, 18, 4.5, hexc("#ff6060") if b == 0 else CYAN, p.get("mood", "calm"))
    for x in (11, 21):  # wheels
        c.ellipse(x, 28, 3, 3, DARK)
    if b == 1:  # Scout: an antenna
        c.line([(22, 13), (26, 5)], OUTLINE)
        c.ellipse(26, 5, 1.4, 1.4, hexc("#ff6060"))
    return (16, 4)


def gun_drone(c, p):
    b = tier(p)
    top = drone(c, p, HULL, size=1.05 if b == 0 else 1.0)
    recoil = 1 if p.get("act") == "fire" else 0
    guns = (12, 20) if b == 0 else (16,)
    for x in guns:  # underslung guns
        c.rect(x - 1, 20 + recoil, x + 1, 26, DARK)
    if b == 1:  # Sentry: a radar dish on top
        c.ellipse(16, 6, 4, 1.6, hexc("#c8d0dc"))
        c.line([(16, 6), (16, 9)], OUTLINE)
    return top


def tesla_coil(c, p):
    b = tier(p)
    c.block(7, 24, 25, 30, DARK)
    hazard_stripes(c, 7, 28, 25, 30)
    coil = hexc("#c88a40")
    for y in range(8, 24, 2):
        c.ellipse(16, y, 4.5, 1.5, coil)
    r = 6 if b == 0 else 4.5
    c.blob(16, 6, r, r * 0.8, hexc("#c8d0dc"))  # the top ball
    zap = p.get("act") != "idle" or b == 0
    if zap:
        for d in (-1, 1):
            c.line([(16 + d * r, 6), (16 + d * (r + 4), 3), (16 + d * (r + 3), 0)], CYAN)
    if b == 1:  # Wide: charge rings
        ring(c, 16, 16, 14, 12, CYAN, 22)
    pc_mark(c, 16, 26, p, 1.2)
    return (16, 1)


def blade_bot(c, p):
    b = tier(p)
    if b == 1:  # Hunter: thrusters
        for x in (11, 21):
            c.poly([(x - 2, 29), (x + 2, 29), (x, 32)], hexc("#ffa040"))
    top = mech(c, p, HULL if b != 0 else hexc("#5a6478"), arms="blades", size=0.95)
    if b == 0:  # Razor: extra blades on the shoulders
        for side in (-1, 1):
            c.line([(16 + side * 7, 11), (16 + side * 12, 4)], hexc("#e0e8f4"), 2)
    return top


def gravity_well(c, p):
    b = tier(p)
    wide = 14 if b == 1 else 11
    c.ellipse(16, 22, wide + 1, 7.5, DARK)  # emitter ring
    c.ellipse(16, 21.5, wide, 6.5, hexc("#5a4a7a"))
    spin = phase(p)
    for arm in range(3):  # a swirling vortex
        for k in range(8):
            a = spin * 0.5 + arm * math.tau / 3 + k * 0.45
            d = (wide - 1) * (1 - k / 9)
            c.px(16 + math.cos(a) * d, 21.5 + math.sin(a) * d * 0.55, hexc("#c090ff"))
    core(c, 16, 21.5, 2.5 if b == 0 else 1.8, hexc("#c090ff"), p)
    for x in (16 - wide, 16 + wide):  # pylons
        c.block(x - 1.5, 14, x + 1.5, 23, HULL)
    pc_mark(c, 16, 28, p, 1.2)
    return (16, 13)


# --- Precision ------------------------------------------------------------------

def energy_barrier(c, p):
    b = tier(p)
    top = 9 if b == 0 else 12
    for x in (5, 27):  # emitter posts
        c.block(x - 2.5, top, x + 2.5, 30, HULL)
        c.ellipse(x, top + 2, 1.6, 1.6, CYAN)
    field = hexc("#80e8ff", 200) if b != 1 else hexc("#e0e8ff", 220)
    c.rect(8, top + 3, 24, 28, field)
    for y in range(top + 5, 28, 4):
        c.line([(8, y), (23, y)], (255, 255, 255, 160))
    if b == 0:  # Reinforced: a steel base
        c.block(3, 27, 29, 31, HULL)
    if b == 1:  # Reflector: a mirror sheen
        c.line([(10, top + 6), (16, top + 12)], WHITE)
    pc_mark(c, 16, top + 14, p, 1.3)
    return (16, top - 2)


def laser_turret(c, p):
    b = tier(p)
    for side in (-1, 1):  # tripod legs
        c.line([(16, 20), (16 + side * 10, 30)], DARK, 2)
    c.line([(16, 20), (16, 30)], DARK, 2)
    c.blob(16, 15, 7, 6, HULL)
    lenses = (16,) if b != 0 else (12.5, 19.5)
    length = 13 if b == 1 else 8
    for x in lenses:
        c.rect(x - 1.5, 15 - length, x + 1.5, 13, shade(HULL, -0.3))
        c.ellipse(x, 15 - length, 2, 2, hexc("#ff4040"))
    visor(c, 16, 16, 4.5, hexc("#ff6060"), p.get("mood", "calm"))
    if p.get("act") == "fire":
        c.line([(16, 15 - length), (16, 0)], hexc("#ff8080"))
    return (16, 15 - length)


def targeting_beacon(c, p):
    b = tier(p)
    tall = 6 if b == 1 else 0
    c.block(9, 24, 23, 30, DARK)
    c.rect(14.5, 8 - tall, 17.5, 24, HULL)
    blink = phase(p) % 2
    c.ellipse(16, 7 - tall, 4, 4, hexc("#ff4040") if blink else hexc("#a02020"))
    c.px(15, 6 - tall, WHITE)
    if b == 0:  # Lock-On: a crosshair projection
        ring(c, 16, 7, 8, 8, hexc("#ff6060"), 20)
        c.line([(16, -2), (16, 1)], hexc("#ff6060"))
        c.line([(6, 7), (9, 7)], hexc("#ff6060"))
        c.line([(23, 7), (26, 7)], hexc("#ff6060"))
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 3 - tall)


def ion_cannon(c, p):
    b = tier(p)
    if b == 1:  # Patrol: walker legs instead of a hover base
        for side in (-1, 1):
            c.line([(16 + side * 5, 24), (16 + side * 9, 27), (16 + side * 8, 31)], DARK, 2)
    else:
        c.ellipse(16, 28, 10, 2.5, hexc("#60c8ff", 160))  # hover glow
    return tracked_turret(c, p, hexc("#5a8ad0"), barrel_len=10, barrel_w=6 if b == 0 else 5,
                          core_color=CYAN, core_r=3 if b == 0 else 2.2, y=15, armor=b == 0)


def orbital_lance(c, p):
    b = tier(p)
    c.block(5, 24, 27, 30, DARK)
    hazard_stripes(c, 5, 27, 27, 30)
    emitters = (16,) if b != 1 else (12, 20)
    w = 4 if b == 0 else 3
    for x in emitters:  # tall uplink emitters
        c.block(x - w, 6, x + w, 25, HULL)
        c.rect(x - w + 1, 6, x - w + 2, 25, shade(HULL, 0.2))
        core(c, x, 5, w * 0.7, CYAN, p)
    if p.get("act") == "fire":
        c.line([(16, 4), (16, 0)], CYAN, 2)
    return (16, 1)


def scanner_array(c, p):
    b = tier(p)
    tall = 5 if b == 1 else 0
    c.block(10, 24, 22, 30, DARK)
    c.rect(14.5, 12 - tall, 17.5, 25, HULL)
    spin = phase(p) if p.get("act") != "idle" else 0
    w = 11 if b == 0 else 8
    c.ellipse(16, 10 - tall, w, 3.5, hexc("#c8d0dc"))
    c.ellipse(16 + spin - 1.5, 10 - tall, w * 0.5, 2, HULL)
    c.ellipse(16, 10 - tall, 1.4, 1.4, CYAN)
    if b == 0:  # Deep: scan waves
        ring(c, 16, 10, 15, 7, CYAN, 22)
    return (16, 6 - tall)


# --- Control --------------------------------------------------------------------

def force_field(c, p):
    b = tier(p)
    shimmer = hexc("#9ad8ff", 190) if b != 1 else hexc("#c8b0ff", 200)
    top = 8 if b == 0 else 11
    c.ellipse(16, top + 10, 14, 11, shimmer)  # dome
    for k in range(5):
        c.line([(4 + k * 6, top + 14), (6 + k * 6, top + 2)], (255, 255, 255, 140))
    c.block(3, 26, 29, 31, HULL)  # generator base
    for x in (6, 16, 26):
        c.ellipse(x, 28, 1.6, 1.6, CYAN)
    if b == 1:  # Stasis: a frozen clock face
        ring(c, 16, top + 9, 4, 4, WHITE, 14)
        c.line([(16, top + 9), (16, top + 6)], WHITE)
        c.line([(16, top + 9), (18, top + 9)], WHITE)
    pc_mark(c, 16, 25, p, 1.2)
    return (16, top - 1)


def cryo_emitter(c, p):
    b = tier(p)
    ice = hexc("#a0e8ff")
    if b == 1:  # Wide: a frost ring
        ring(c, 16, 22, 14, 7, ice, 22)
    c.block(7, 20, 25, 30, HULL)
    c.ellipse(16, 13, 8 if b == 0 else 7, 7 if b == 0 else 6, shade(ice, -0.2))  # cryo dome
    c.ellipse(16, 12.5, 6.5, 5.5, ice)
    visor(c, 16, 24, 5, hexc("#a0e8ff"), p.get("mood", "calm"))
    if b == 0:  # Deep: ice crystals growing on it
        for x, y, h in ((6, 20, 6), (26, 20, 6), (16, 6, 5)):
            c.poly([(x - 2, y), (x + 2, y), (x, y - h)], WHITE)
    for k in range(3):
        c.px(9 + k * 7, 5 + (phase(p) + k) % 3, WHITE)
    return (16, 6)


def arc_thrower(c, p):
    b = tier(p)
    top = tracked_turret(c, p, hexc("#7a6a9a"), barrel_len=13 if b == 1 else 8, barrel_w=4 if b == 0 else 3,
                         barrels=2, core_color=hexc("#c090ff"), armor=b == 0)
    if p.get("act") != "idle":
        c.line([(13, 17 - (13 if b == 1 else 8)), (16, 0), (19, 17 - (13 if b == 1 else 8))], hexc("#e0c8ff"))
    return top


def plasma_vent(c, p):
    b = tier(p)
    wide = 13 if b == 1 else 10
    flick = phase(p) % 2
    glow(c, 16, 16, 12 if b == 0 else 9, hexc("#ffa060"))
    c.ellipse(16, 25, wide + 2, 5, DARK)  # floor vent
    c.ellipse(16, 24.5, wide, 3.8, hexc("#5a2a2a"))
    for x in range(int(16 - wide + 2), int(16 + wide - 1), 3):
        c.line([(x, 23), (x, 26)], DARK)
    h = 16 if b == 0 else 11
    c.poly([(16 - wide * 0.6, 24), (16, 24 - h - flick), (16 + wide * 0.6, 24)], hexc("#f08040"))
    c.poly([(16 - wide * 0.3, 24), (16, 24 - h * 0.6 + flick), (16 + wide * 0.3, 24)], hexc("#fff080"))
    pc_mark(c, 16, 29, p, 1.2)
    return (16, 24 - h)


def emp_tower(c, p):
    b = tier(p)
    c.block(9, 24, 23, 30, DARK)
    c.block(12, 8, 20, 25, HULL)  # pylon
    for y in (12, 16, 20):
        c.rect(10, y, 22, y + 1.5, hexc("#5a6478"))  # rings
    core(c, 16, 6, 3.5 if b == 0 else 2.8, hexc("#80f0ff"), p)
    if b == 0 or p.get("act") != "idle":  # Overloaded: arcs
        for d in (-1, 1):
            c.line([(16 + d * 3, 5), (16 + d * 8, 2), (16 + d * 10, 6)], CYAN)
    if b == 1:  # Chain: side arcs
        for d in (-1, 1):
            c.line([(16 + d * 6, 14), (16 + d * 11, 17), (16 + d * 14, 13)], CYAN)
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 2)


def tractor_beam(c, p):
    b = tier(p)
    wide = 1.4 if b == 1 else 1.0
    beam = hexc("#a0ffb0", 150 if b != 0 else 200)
    c.poly([(16 - 4, 12), (16 + 4, 12), (16 + 12 * wide, 30), (16 - 12 * wide, 30)], beam)  # beam cone
    for y in (17, 22, 27):
        c.line([(16 - (y - 10) * 0.6 * wide, y), (16 + (y - 10) * 0.6 * wide, y)], (255, 255, 255, 120))
    top = drone(c, p, HULL, y=7, size=1.0, rotors=False)  # the hovering emitter
    c.ellipse(16, 12, 4, 1.6, hexc("#a0ffb0"))
    return top


# --- Toxin ----------------------------------------------------------------------

def trefoil(c, x, y, r, color, bg):
    c.ellipse(x, y, r, r, bg)
    for k in range(3):
        a = -math.pi / 2 + k * math.tau / 3
        c.poly([(x, y), (x + math.cos(a - 0.5) * r * 0.9, y + math.sin(a - 0.5) * r * 0.9),
                (x + math.cos(a + 0.5) * r * 0.9, y + math.sin(a + 0.5) * r * 0.9)], color)
    c.ellipse(x, y, r * 0.22, r * 0.22, color)


def radioactive_plate(c, p):
    b = tier(p)
    top = 9 if b == 0 else 12
    if b == 1:  # Hot: a radioactive glow
        glow(c, 16, top + 9, 15, hexc("#c0ff60"))
    armor_plate(c, top, hexc("#5a6a50") if b != 0 else hexc("#4a4e58"), double=b == 0)
    trefoil(c, 16, top + 9, 5, OUTLINE, HAZARD)
    pc_mark(c, 25, 27, p, 1.2)
    return (16, top - 2)


def acid_bot(c, p):
    b = tier(p)
    top = mech(c, p, hexc("#6a8a5a") if b != 0 else hexc("#4a7a3a"), arms="tank", size=0.95)
    nozzle = 10 if b == 1 else 5
    c.line([(16, 10), (16, 10 - nozzle)], DARK, 2)
    if p.get("act") == "fire" or b == 0:  # Corrosive: dripping
        c.ellipse(16, 9 - nozzle, 1.8, 1.8, hexc("#c0f060"))
    return (16, 9 - nozzle)


def nanite_sprayer(c, p):
    b = tier(p)
    c.block(8, 18, 24, 30, HULL)
    c.ellipse(16, 18, 8, 3, shade(HULL, 0.15))
    c.rect(14.5, 7, 17.5, 18, DARK)  # nozzle
    visor(c, 16, 24, 5, hexc("#a0f060"), p.get("mood", "calm"))
    count = 7 if b == 0 else 4
    for k in range(count):  # a cloud of nanites
        x = 16 + math.cos(k * 1.7 + phase(p)) * (5 + k)
        y = 5 + math.sin(k * 1.3) * 3
        c.rect(x, y, x + 1.5, y + 1.5, hexc("#a0f060"))
    if b == 1:  # Misting: a mist
        puffs(c, [(10, 5, 3), (22, 5, 3)], hexc("#c8f0b0", 170))
    return (16, 3)


def toxic_reactor(c, p):
    b = tier(p)
    glow(c, 16, 17, 13 if b == 0 else 9, hexc("#c0ff60"))
    c.block(7, 8, 25, 30, hexc("#5a6a50"))  # reactor drum
    c.ellipse(16, 8, 9, 2.6, shade(hexc("#5a6a50"), 0.2))
    c.rect(10, 12, 22, 24, hexc("#a0e040"))  # glowing window
    c.rect(10, 12, 22, 13, shade(hexc("#a0e040"), 0.3))
    trefoil(c, 16, 18, 4, OUTLINE, HAZARD)
    if b == 0:  # Meltdown: cracks
        c.line([(8, 14), (11, 18), (9, 22)], hexc("#c0ff60"))
        c.line([(24, 11), (21, 16)], hexc("#c0ff60"))
    if b == 1:  # Leaking: ooze
        c.ellipse(16, 30, 10, 2, hexc("#a0e040"))
    pc_mark(c, 16, 27, p, 1.2)
    return (16, 5)


def plague_drone(c, p):
    b = tier(p)
    if b == 0:  # Plague Swarm: two little escort drones
        for x in (5, 27):
            c.blob(x, 22, 3, 2.5, HULL)
            c.px(x, 22, hexc("#c0ff60"))
    top = drone(c, p, hexc("#7a8a6a"), size=0.95)
    c.ellipse(16, 22, 3.5, 3, hexc("#a0e040"))  # plague canister
    if b == 1:  # Long: an antenna
        c.line([(16, top[1] + 2), (16, top[1] - 5)], OUTLINE)
        c.ellipse(16, top[1] - 5, 1.2, 1.2, hexc("#c0ff60"))
    return top


def contamination_zone(c, p):
    b = tier(p)
    wide = 14 if b == 1 else 12
    if b == 1:  # Virulent: a glow
        glow(c, 16, 21, 15, hexc("#c0ff60"))
    c.ellipse(16, 23, wide, 7, hexc("#3a4a2a"))
    c.ellipse(16, 22.5, wide - 1.5, 5.8, hexc("#7ac040"))
    for k, (x, y) in enumerate(((11, 21), (20, 23), (16, 25))):
        c.ellipse(x, y - (phase(p) + k) % 2, 1.6, 1.6, hexc("#c0ff60"))
    for x in (16 - wide + 2, 16 + wide - 2):  # warning posts
        c.rect(x - 1, 12, x + 1, 22, HAZARD)
        c.rect(x - 3, 10, x + 3, 13, HAZARD)
        c.px(x, 11.5, OUTLINE)
    if b == 0:  # Hardened: a crusted rim
        c.line([(16 - wide, 25), (16 + wide, 25)], hexc("#8a8a70"), 2)
    pc_mark(c, 16, 28, p, 1.2)
    return (16, 9)


DESIGNS = {
    "platelet_clot": hull_plate, "macrophage": mech_brawler, "dendritic_cell": plasma_cannon, "fibroblast": nanite_wall,
    "eosinophil": rail_cannon, "granuloma": fortress_core, "epithelial_cell": scrap_barrier, "neutrophil": buzz_bot,
    "monocyte": gun_drone, "basophil": tesla_coil, "nk_cell": blade_bot, "net_trap": gravity_well, "keratin_plate": energy_barrier,
    "b_cell": laser_turret, "antibody_tagger": targeting_beacon, "cytotoxic_t": ion_cannon, "opsonin_lance": orbital_lance,
    "interferon_beacon": scanner_array, "mucus_wall": force_field, "mast_cell": cryo_emitter, "histamine_spitter": arc_thrower,
    "fever_node": plasma_vent, "cytokine_storm": emp_tower, "inflammation_zone": tractor_beam, "toxic_membrane": radioactive_plate,
    "killer_t": acid_bot, "complement_sprayer": nanite_sprayer, "lysozyme_pool": toxic_reactor, "perforin_lancer": plague_drone,
    "necrosis_bloom": contamination_zone,
}


# --- Enemies: aliens (faces) and their machines --------------------------------------

def _alien(body, size=1.0, eye="#ff4060", legs_n=4, pods=0, hop=False, dig=False):
    def design(c, p):
        bob = (0, -2 if hop else -1, 0, 0)[phase(p)]
        c.dy += bob
        b = hexc(body)
        if pods:
            for x, y in ((10, 22), (22, 22), (16, 15)):
                c.blob(x, y, 5.5 * size, 5 * size, b)
                c.ellipse(x, y, 1.4, 1.4, hexc(eye))
        else:
            legs(c, 16, 24, 6 * size, legs_n, shade(b, -0.35), 3, p)
            c.blob(16, 20, 8 * size, 7.5 * size, b)
            c.ellipse(16, 18, 2.6, 2.2, WHITE)
            c.ellipse(16, 18, 1.3, 1.3, hexc(eye))
            if dig:
                c.poly([(9, 24), (6, 28), (11, 27)], hexc("#c0c0c8"))
                c.poly([(23, 24), (26, 28), (21, 27)], hexc("#c0c0c8"))
        c.dy -= bob
    return design


def _mech(body, visor):
    def design(c, p):
        robot(c, p, hexc(body), hexc(visor), size=1.15)
    return design


def _ufo(body, size=1.0, bomb=False):
    def design(c, p):
        tilt = (0, 1, 0, -1)[phase(p)]
        b = hexc(body)
        c.ellipse(16, 20 + tilt * 0.5, 13 * size, 4.5 * size, b)
        c.ellipse(16, 15, 6 * size, 5 * size, hexc("#a0e8ff"))
        c.eyes(16, 15, 2.5, "angry")
        for i in range(4):
            c.px(16 + (i - 1.5) * 6 * size, 21, hexc("#ffe060") if (i + phase(p)) % 2 else hexc("#ff6060"))
        if bomb:
            c.ellipse(16, 27, 2, 2, hexc("#2a2a2a"))
    return design


ENEMIES = {
    "spawnling": _alien("#9ad84a", 0.6, legs_n=2), "grub": _alien("#7ac83a", 0.8), "drone": _alien("#3a9a5a", 0.9, "#ffd040"),
    "brood_pod": _alien("#b8a05a", pods=3), "hive_pod": _alien("#7a6a3a", pods=3, eye="#ffd040"),
    "blinker": _alien("#a060f0", 0.9, "#ffffff", legs_n=0), "phase_stalker": _alien("#6a30c0", 1.0, "#ff60ff", legs_n=2),
    "hopper": _alien("#d88a3a", 0.85, legs_n=2, hop=True), "tunneler": _alien("#8a6a4a", 0.9, legs_n=6, dig=True),
    "crusher": _mech("#6a7a8a", "#ff4060"), "assault_mech": _mech("#4a5260", "#ffd040"),
    "saucer": _ufo("#a0a8b8", 0.8), "interceptor": _ufo("#6a7a9a", 0.9), "ufo_bomber": _ufo("#7a8090", 1.0, True),
    "mothership": _ufo("#5a5a7a", 1.2, True),
}
