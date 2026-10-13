"""World 4 (Total War): a toy war. The player's toy soldiers are chunky
plastic army men in their pack's color, with dot eyes (they're living toys);
vehicles, guns and structures are chunky toy plastic. Enemies stay
faceless.

Redesigned (see world_backyard.py): power evolutions get rank, armor and
bigger guns; utility evolutions get field gear (scopes, radios, packs,
longer barrels). Every unit draws its own evolutions (p["branch"]).
"""
import math

from .hefty import army_man, glow, pc_mark, plastic, puffs, ring, tier
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, phase, robot, soldier, turret

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True

OLIVE = hexc("#6a7a40")
STEEL = hexc("#7a8088")
KHAKI = hexc("#c8b080")
CONCRETE = hexc("#b0aca4")


def bolts(c, points, color=None):
    for x, y in points:
        c.px(x, y, color or hexc("#d8dce4"))


def gun_mount(c, p, color, barrel_len=10, barrel_w=3, barrels=1, wheels=False, angle_x=0.0, x=16, y=20,
              shield=False):
    """A toy gun emplacement: a sturdy base, a round turret and barrel(s).
    shield=True: a towed gun instead, with a flat gun shield (no dome)."""
    recoil = 2 if p.get("act") == "fire" else 0
    if wheels:
        for side in (-1, 1):
            c.ellipse(x + side * 9, y + 7, 4, 4, hexc("#3a3a40"))
            c.ellipse(x + side * 9, y + 7, 1.6, 1.6, STEEL)
    c.block(x - 10, y + 2, x + 10, y + 10, shade(color, -0.12))
    bolts(c, [(x - 8, y + 4), (x + 8, y + 4), (x - 8, y + 8), (x + 8, y + 8)])
    for k in range(barrels):
        bx = x + (k - (barrels - 1) / 2) * (barrel_w + 2)
        tip = (bx + angle_x, y - barrel_len + recoil)
        c.line([(bx, y), tip], shade(color, -0.4), barrel_w)
        c.line([(bx - barrel_w * 0.25, y - 1), (tip[0] - barrel_w * 0.25, tip[1])], shade(color, -0.15))
        c.rect(tip[0] - barrel_w / 2 - 0.5, tip[1], tip[0] + barrel_w / 2 + 0.5, tip[1] + 1.5, shade(color, -0.5))
    if shield:
        c.poly([(x - 8, y + 4), (x - 6, y - 4), (x + 6, y - 4), (x + 8, y + 4)], color)
        c.line([(x - 6, y - 4), (x + 6, y - 4)], shade(color, 0.25))
        bolts(c, [(x - 5, y), (x + 5, y)])
    else:
        c.blob(x, y, 7, 5.5, color)
        c.ellipse(x - 2.5, y - 2, 2, 1.2, shade(color, 0.25))
    return (x, y - barrel_len)


# --- Fortress -------------------------------------------------------------------

def sandbags(c, p):
    b = tier(p)
    rows = (27, 21, 15) if b != 0 else (28, 23, 18, 13)
    for row, y in enumerate(rows):
        for x in range(4 - (row % 2) * 4, 29, 8):
            c.blob(max(6, min(26, x + 2)), y, 4.6, 3, shade(KHAKI, ((x + row) % 3 - 1) * 0.05))
            c.line([(max(6, min(26, x + 2)) - 3, y), (max(6, min(26, x + 2)) + 3, y)], shade(KHAKI, -0.2))
    if b == 0:  # Reinforced: a steel plate
        c.block(8, 8, 24, 13, STEEL)
        bolts(c, [(10, 10), (22, 10)])
    if b == 1:  # Spiked Barricade: sharpened stakes
        for x in (6, 13, 20, 27):
            c.line([(x, 18), (x + 2, 8)], hexc("#a07040"), 2)
            c.px(x + 2, 7, hexc("#e8d8b8"))
    pc_mark(c, 16, 27, p, 1.3)
    return (16, 9)


def tank_turret(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    c.block(3, 22, 29, 30, shade(col, -0.3))  # tank hull with tracks
    for x in range(5, 28, 4):
        c.ellipse(x, 27.5, 1.6, 1.6, hexc("#3a3a40"))
    if b == 0:  # Heavy: armor skirt
        c.rect(2, 21, 30, 23, shade(col, -0.1))
        bolts(c, [(5, 22), (11, 22), (21, 22), (27, 22)])
    top = gun_mount(c, p, col, barrel_len=12 if b == 0 else 10, barrel_w=4 if b == 0 else 3,
                    barrels=2 if b == 1 else 1, y=15)
    c.px(14, 14, OUTLINE)  # little dot eyes on the turret
    c.px(18, 14, OUTLINE)
    return top


def field_gun(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    top = gun_mount(c, p, col, barrel_len=15 if b == 1 else 10, barrel_w=5 if b == 0 else 3, wheels=True, y=18,
                    shield=True)
    c.block(10, 26, 22, 29, shade(col, -0.3))  # trail
    return top


def repair_depot(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    c.block(4, 13, 28, 30, hexc("#d8d0c0"))  # a garage
    c.poly([(2, 14), (16, 5), (30, 14)], shade(col, -0.1))
    c.rect(10, 19, 22, 30, hexc("#5a5a60"))  # door
    for y in (21, 24, 27):
        c.line([(10, y), (21, y)], hexc("#7a7a80"))
    c.rect(13, 8, 19, 12, WHITE)  # wrench sign
    c.line([(14, 11), (18, 9)], hexc("#c84a3a"), 2)
    if b == 0:  # Armored: steel plates
        for x in (4, 24):
            c.block(x, 15, x + 4, 30, STEEL)
            bolts(c, [(x + 2, 18), (x + 2, 26)])
    if b == 1:  # Rapid: a crane arm with a hook
        c.line([(27, 14), (27, 3), (20, 3)], hexc("#e0b030"), 2)
        c.line([(20, 3), (20, 7)], OUTLINE)
        c.poly([(19, 7), (21, 7), (20, 9)], STEEL)
    pc_mark(c, 7, 27, p, 1.3)
    return (16, 4)


def howitzer(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    for side in (-1, 1):  # split trail legs
        c.line([(16, 26), (16 + side * 12, 31)], shade(col, -0.3), 2)
    top = gun_mount(c, p, col, barrel_len=16 if b == 1 else 12, barrel_w=6 if b == 0 else 4, angle_x=6, wheels=True,
                    y=19, shield=True)
    return top


def concrete_bunker(c, p):
    b = tier(p)
    c.ellipse(16, 28, 14, 3.5, shade(CONCRETE, -0.3))
    c.blob(16, 21, 13 if b == 0 else 12, 9, CONCRETE)  # pillbox dome
    c.rect(8, 18, 24, 21, hexc("#2a2a30"))  # firing slit
    if p.get("act") != "idle":
        c.ellipse(16, 19.5, 2, 1, hexc("#ffe080"))
    for x, y in ((9, 25), (21, 14), (24, 25)):  # cracks and chips
        c.px(x, y, shade(CONCRETE, -0.25))
    if b == 0:  # Reinforced: steel rim
        c.rect(4, 25, 28, 27, STEEL)
        bolts(c, [(7, 26), (16, 26), (25, 26)])
    if b == 1:  # Spiked: steel spikes
        for x in (5, 11, 21, 27):
            c.poly([(x - 1.5, 20), (x + 1.5, 20), (x, 13)], STEEL)
    pc_mark(c, 16, 25, p, 1.3)
    return (16, 11)


# --- Swarm --------------------------------------------------------------------

def barbed_wire(c, p):
    b = tier(p)
    wire = hexc("#9aa0a8")
    for x in (4, 28):  # posts
        c.block(x - 1.5, 10, x + 1.5, 30, hexc("#8a6a40"))
    coils = (20,) if b != 0 else (15, 24)
    for cy in coils:
        for k in range(7):  # coiled loops
            c.ellipse(5 + k * 3.7, cy, 3, 4.5, (0, 0, 0, 0))
            for a in range(10):
                ang = a * math.tau / 10
                c.px(5 + k * 3.7 + math.cos(ang) * 2.8, cy + math.sin(ang) * 4.2, wire)
    if b == 1:  # Razor: shiny blades
        for x in range(5, 29, 4):
            c.poly([(x, 14), (x + 1.5, 16), (x, 18), (x - 1.5, 16)], hexc("#e8eef4"))
    pc_mark(c, 16, 29, p, 1.3)
    return (16, 9)


def rifleman(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    top = army_man(c, p, col, weapon="rifle", size=1.05 if b != 0 else 1.12)
    if b == 0:  # Veteran: sergeant stripes and a medal
        c.line([(9, 18), (11, 17), (13, 18)], hexc("#f0d040"))
        c.ellipse(13, 21, 1.4, 1.4, hexc("#f0d040"))
    if b == 1:  # Scout: backpack and binoculars
        c.block(6, 16, 10, 24, shade(col, -0.35))
        c.rect(12, 9.5, 20, 11, OUTLINE)
    pc_mark(c, 16, 29, p, 1.2)
    return top


def aa_gunner(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    recoil = 1 if p.get("act") == "fire" else 0
    barrels = (13, 19) if b == 0 else (16,)
    c.block(7, 24, 25, 30, shade(col, -0.3))  # gun platform
    for x in barrels:
        c.line([(x, 24), (x + 4, 6 + recoil)], shade(col, -0.45), 2)
    if b == 1:  # Sentry: a little radar dish
        c.ellipse(26, 14, 4, 2.5, STEEL)
        c.line([(26, 16), (26, 24)], STEEL)
    top = army_man(c, p, col, weapon=None, size=0.9, base=False, y=16)
    return (18, 5)


def grenadier(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    top = army_man(c, p, col, weapon="grenade" if b != 1 else None, size=1.05 if b != 0 else 1.12)
    if b == 0:  # Heavy: a bandolier of grenades
        c.line([(10, 15), (22, 22)], shade(col, -0.4), 2)
        for x, y in ((12, 16), (16, 18.5), (20, 21)):
            c.ellipse(x, y, 1.4, 1.4, shade(col, -0.5))
    if b == 1:  # Wide: a grenade launcher
        c.rect(19, 9, 25, 14, shade(col, -0.45))
        c.ellipse(25, 11.5, 1.6, 2.5, OUTLINE)
    pc_mark(c, 16, 29, p, 1.2)
    return top


def commando(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    if b == 1:  # Ranger: a hooded cape
        c.poly([(9, 12), (23, 12), (26, 28), (6, 28)], shade(col, -0.25))
    top = army_man(c, p, col, weapon="knife", helmet="beret", size=1.05 if b != 0 else 1.12)
    if b == 0:  # Elite: face paint and a second knife
        c.line([(13, 13), (19, 13)], shade(col, -0.45))
        c.poly([(4, 20), (6, 20), (5, 13)], hexc("#d8dce4"))
    pc_mark(c, 16, 29, p, 1.2)
    return top


def tank_trap(c, p):
    b = tier(p)
    metal = STEEL if b != 0 else hexc("#5a5e66")
    traps = ((16, 20),) if b != 1 else ((10, 21), (23, 21))
    for x, y in traps:
        s = 1.0 if b != 1 else 0.75
        for a in (0.5, 2.6, -1.3):  # a steel hedgehog of crossed beams
            dx, dy = math.cos(a) * 11 * s, math.sin(a) * 9 * s
            c.line([(x - dx, y - dy), (x + dx, y + dy)], shade(metal, -0.2), 4)
            c.line([(x - dx, y - dy - 1), (x + dx, y + dy - 1)], metal, 2)
        bolts(c, [(x, y)], hexc("#f0e070"))
    pc_mark(c, 16, 29, p, 1.2)
    return (16, 9)


# --- Precision ------------------------------------------------------------------

def concrete_barrier(c, p):
    b = tier(p)
    top = 11 if b == 0 else 13
    c.poly([(3, 30), (6, top + 6), (10, top), (22, top), (26, top + 6), (29, 30)], CONCRETE)
    c.rect(10, top, 22, top + 2, shade(CONCRETE, 0.15))
    for x in range(5, 28, 5):  # hazard stripes
        c.poly([(x, 28), (x + 2.5, 28), (x + 4, 24), (x + 1.5, 24)], hexc("#e8c030"))
    if b == 1:  # Spiked: rebar spikes
        for x in (11, 16, 21):
            c.line([(x, top), (x + 1, top - 6)], hexc("#7a5040"), 2)
    pc_mark(c, 16, top + 6, p, 1.3)
    return (16, top - 2)


def sniper(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    if b == 0:  # Veteran: a ghillie suit of leaves
        for x, y in ((8, 16), (24, 16), (10, 23), (22, 23), (16, 12)):
            c.ellipse(x, y, 3, 2.2, hexc("#5a7a3a"))
    top = army_man(c, p, col, weapon="long_rifle", helmet="cap", size=1.05 if b != 0 else 1.1)
    if b == 1:  # Marksman: a big glinting scope
        c.ellipse(22, 8, 2.4, 2.4, hexc("#80c8f0"))
        c.px(21, 7, WHITE)
    pc_mark(c, 16, 29, p, 1.2)
    return top


def spotter(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    c.block(6, 15, 11, 24, shade(col, -0.35))  # radio pack
    antenna = 13 if b == 1 else 7
    c.line([(7, 15), (5, 15 - antenna)], OUTLINE)
    c.ellipse(5, 15 - antenna, 1.2, 1.2, hexc("#e03030"))
    top = army_man(c, p, col, weapon="binoculars", size=1.05 if b != 0 else 1.1)
    if b == 0 or p.get("act") == "fire":  # Laser: a red designator beam
        c.line([(19, 12), (29, 2)], hexc("#ff4040"))
    pc_mark(c, 16, 29, p, 1.2)
    return top


def bazooka_trooper(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    if b == 1:  # Roaming: an ammo backpack
        c.block(5, 15, 10, 25, shade(col, -0.35))
        for y in (17, 21):
            c.ellipse(7.5, y, 1.5, 1.2, hexc("#c84a3a"))
    top = army_man(c, p, col, weapon="bazooka", size=1.05 if b != 0 else 1.15)
    if b == 0:  # Heavy: a bigger tube with a sight
        c.rect(21, 4, 27, 20, shade(col, -0.45))
        c.rect(26, 10, 29, 12, shade(col, -0.2))
    pc_mark(c, 16, 29, p, 1.2)
    return top


def long_tom(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    top = gun_mount(c, p, col, barrel_len=20 if b != 0 else 18, barrel_w=5 if b == 0 else 3,
                    barrels=2 if b == 1 else 1, wheels=True, y=21, shield=True)
    return top


def radar_tower(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    tall = 5 if b == 1 else 0
    for side in (-1, 1):  # lattice legs
        c.line([(16 + side * 9, 30), (16 + side * 2, 13 - tall)], STEEL, 2)
    for y in (26, 21, 17):
        c.line([(16 - (30 - y) * 0.42, y - tall * 0.3), (16 + (30 - y) * 0.42, y - tall * 0.3)], STEEL)
    spin = phase(p) if p.get("act") != "idle" else 0
    dish_w = 10 if b == 0 else 7
    c.ellipse(16, 10 - tall, dish_w, 3.5, shade(col, 0.1))  # dish
    c.ellipse(16 + (spin - 1.5), 10 - tall, dish_w * 0.5, 2, shade(col, -0.2))
    c.line([(16, 10 - tall), (16, 5 - tall)], OUTLINE)
    c.ellipse(16, 4.5 - tall, 1.4, 1.4, hexc("#e03030") if phase(p) % 2 else hexc("#ff8080"))
    if b == 0:  # Advanced: radar waves
        ring(c, 16, 10, 14, 7, hexc("#a0f0a0"), 20)
    return (16, 3 - tall)


# --- Control --------------------------------------------------------------------

def sticky_barricade(c, p):
    b = tier(p)
    wood = hexc("#a07a48")
    top = 10 if b == 0 else 13
    for x in (5, 27):
        c.block(x - 2, top, x + 2, 30, shade(wood, -0.2))
    for y in range(top + 2, 29, 5):
        c.block(3, y, 29, y + 3, wood)
    glue = hexc("#c8e070", 230)
    for x, y in ((9, top + 4), (19, top + 10), (24, top + 3)):
        c.ellipse(x, y, 3, 2, glue)
    if b == 1:  # Gluey: drips
        for x in (8, 16, 24):
            c.rect(x, 28, x + 2, 32, glue)
    pc_mark(c, 16, 27, p, 1.3)
    return (16, top - 2)


def smoke_launcher(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    tubes = 3 if b != 0 else 5
    c.block(5, 22, 27, 30, shade(col, -0.2))
    for k in range(tubes):
        x = 16 + (k - (tubes - 1) / 2) * 4.5
        c.rect(x - 1.8, 10, x + 1.8, 23, shade(col, -0.4))
        c.ellipse(x, 10, 1.8, 1, OUTLINE)
    if p.get("act") != "idle" or b == 1:  # Wide: smoke clouds
        puffs(c, [(9, 6, 3.5), (16, 4, 4), (23, 6, 3.5)] if b == 1 else [(16, 5, 3.5)], hexc("#d8d8e0", 220))
    c.px(13, 26, OUTLINE)
    c.px(19, 26, OUTLINE)
    return (16, 3)


def mortar_team(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    tube = 4 if b == 0 else 3
    length = 14 if b == 1 else 10
    c.ellipse(23, 28, 6, 2, shade(col, -0.4))  # base plate
    c.line([(23, 28), (26, 28 - length)], shade(col, -0.45), tube)  # mortar tube
    top = army_man(c, p, col, weapon=None, size=0.95, x=11, y=17)
    if p.get("act") == "fire":
        puffs(c, [(26, 28 - length - 2, 2.5)], hexc("#e8e0d8", 220))
    return top


def flame_turret(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    fire = p.get("act") != "idle"
    top = gun_mount(c, p, col, barrel_len=9, barrel_w=5 if b == 1 else 3, y=19)
    c.ellipse(16, 25, 4, 3, hexc("#c84a3a"))  # fuel tank
    flame = 6 if b == 0 else 4
    if fire or b == 0:  # Hot: a flame always flickering at the nozzle
        c.poly([(13, 10), (16, 10 - flame - phase(p) % 2), (19, 10)], hexc("#f08030"))
        c.poly([(14.5, 10), (16, 10 - flame * 0.5), (17.5, 10)], hexc("#fff080"))
    c.px(14, 18, OUTLINE)
    c.px(18, 18, OUTLINE)
    return top


def shock_turret(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    c.block(7, 23, 25, 30, shade(col, -0.2))
    coil = hexc("#c88a40")
    for y in range(9, 23, 2):  # a tesla coil
        c.ellipse(16, y, 4, 1.4, coil)
    c.ellipse(16, 8, 5 if b == 0 else 4, 4 if b == 0 else 3, hexc("#d8dce4"))
    zap = p.get("act") != "idle" or b == 0
    if zap:  # Overcharged: crackling arcs
        for d in (-1, 1):
            c.line([(16 + d * 4, 7), (16 + d * 8, 4), (16 + d * 7, 1), (16 + d * 11, -1)], hexc("#a0e0ff"))
    if b == 1:  # Chain: arcs jumping sideways
        for d in (-1, 1):
            c.line([(16 + d * 5, 9), (16 + d * 10, 12), (16 + d * 13, 10)], hexc("#a0e0ff"))
    c.px(13, 26, OUTLINE)
    c.px(19, 26, OUTLINE)
    return (16, 3)


def water_cannon(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    c.block(4, 21, 28, 30, shade(col, -0.15))  # water tank
    c.rect(4, 24, 28, 26, hexc("#5aa0e0"))
    top = gun_mount(c, p, col, barrel_len=11 if b != 1 else 9, barrel_w=4 if b == 0 else 3, y=15)
    if b == 1:  # Wide: a fan nozzle
        c.poly([(12, 4), (20, 4), (17, 7), (15, 7)], shade(col, -0.4))
    if p.get("act") == "fire":
        for x in (13, 16, 19):
            c.ellipse(x, 2, 1.6, 1.6, hexc("#80c8f0"))
    return top


# --- Toxin ----------------------------------------------------------------------

def barrel(c, x, y, color, h=10, w=6):
    c.block(x - w, y - h, x + w, y, color)
    c.ellipse(x, y - h, w, 2, shade(color, 0.15))
    for yy in (y - h + 3, y - 3):
        c.line([(x - w, yy), (x + w - 1, yy)], shade(color, -0.3))
    c.ellipse(x, y - h * 0.5, 2.2, 2.2, hexc("#f0d030"))  # hazard sign
    c.px(x, y - h * 0.5, OUTLINE)


def barrel_wall(c, p):
    b = tier(p)
    drum = hexc("#4a7a3a")
    barrel(c, 9, 30, drum)
    barrel(c, 23, 30, shade(drum, -0.08))
    if b == 0:  # Stacked: a third barrel on top
        barrel(c, 16, 20, shade(drum, 0.05))
    if b == 1:  # Leaky: green ooze
        c.ellipse(16, 30, 8, 2, hexc("#a0e040"))
        c.rect(22, 22, 23.5, 30, hexc("#a0e040"))
    pc_mark(c, 16, 29, p, 1.2)
    return (16, 9)


def chem_trooper(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    c.block(5, 14, 10, 26, hexc("#d8d040"))  # chemical tank on the back
    c.line([(8, 14), (8, 10)], OUTLINE)
    if b == 0:  # Hazard: a yellow hazard suit
        col = hexc("#d8c030")
    top = army_man(c, p, col, weapon=None, helmet="mask", size=1.05 if b != 0 else 1.12)
    hose = 16 if b == 1 else 9
    c.line([(10, 22), (21, 20), (21 + hose * 0.4, 20 - hose * 0.6)], OUTLINE, 2)  # spray hose
    if p.get("act") == "fire":
        c.ellipse(21 + hose * 0.4, 18 - hose * 0.6, 2.5, 2, hexc("#c0f060"))
    pc_mark(c, 16, 29, p, 1.2)
    return top


def gas_mortar(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    top = gun_mount(c, p, col, barrel_len=13 if b != 0 else 11, barrel_w=5 if b == 0 else 4, angle_x=4, y=20)
    if b == 1 or p.get("act") == "fire":  # Misting: a gas cloud
        puffs(c, [(20, 4, 3.5), (25, 7, 3)], hexc("#c8f070", 200))
    c.px(14, 19, OUTLINE)
    c.px(18, 19, OUTLINE)
    return top


def gas_canister(c, p):
    b = tier(p)
    can = hexc("#d8d040")
    c.ellipse(16, 29, 9, 2.5, shade(can, -0.4))
    c.block(9, 10, 23, 29, can)
    c.ellipse(16, 10, 7, 2, shade(can, 0.2))
    c.rect(14, 5, 18, 10, STEEL)  # valve
    c.rect(12, 5, 20, 6.5, STEEL)
    c.poly([(16, 15), (21, 24), (11, 24)], OUTLINE)  # hazard triangle
    c.poly([(16, 17), (19.5, 23), (12.5, 23)], hexc("#f0e070"))
    gas = 1 if b is None else 3
    puffs(c, [(9 + k * 7, 4 - (phase(p) + k) % 2, 2 + gas * 0.4) for k in range(gas)], hexc("#c8f070", 190))
    if b == 1:  # Spreading: a wide cloud at the base
        puffs(c, [(4, 27, 3), (28, 27, 3)], hexc("#c8f070", 170))
    pc_mark(c, 16, 26, p, 1.2)
    return (16, 3)


def toxic_drone(c, p):
    b = tier(p)
    col = plastic(p["pc"])
    hover = (0, -1, 0, 1)[phase(p)]
    for x in (6, 26):  # rotor arms and spinning rotors
        c.line([(16, 16 + hover), (x, 11 + hover)], STEEL, 2)
        c.ellipse(x, 10 + hover, 5, 1.4, (220, 228, 236, 200))
    c.block(9, 13 + hover, 23, 22 + hover, col)  # body
    c.px(13, 16 + hover, OUTLINE)
    c.px(19, 16 + hover, OUTLINE)
    tank = 5 if b == 0 else 3.5
    c.ellipse(16, 25 + hover, tank, tank * 0.8, hexc("#a0e040"))  # toxic tank
    if b == 1:  # Long-Range: an antenna
        c.line([(16, 13 + hover), (16, 4 + hover)], OUTLINE)
        c.ellipse(16, 4 + hover, 1.2, 1.2, hexc("#e03030"))
    c.ellipse(16, 31, 6, 1.4, (0, 0, 0, 90))
    return (16, 6)


def sludge_pit(c, p):
    b = tier(p)
    sludge = hexc("#7ac040") if b != 0 else hexc("#5a8a3a")
    if b == 1:  # Virulent: a sickly glow (drawn first: shapes replace what's under them)
        glow(c, 16, 19, 15, hexc("#c8f070"))
    c.ellipse(16, 23, 14, 8, hexc("#5a5a60"))  # concrete rim
    c.ellipse(16, 22.5, 12, 6.5, sludge)
    for k, (x, y) in enumerate(((11, 21), (20, 23), (16, 25))):
        c.ellipse(x, y - (phase(p) + k) % 2, 1.8, 1.8, shade(sludge, 0.25))
    c.px(13, 21, OUTLINE)
    c.px(19, 21, OUTLINE)
    pc_mark(c, 16, 29, p, 1.2)
    return (16, 15)


DESIGNS = {
    "platelet_clot": sandbags, "macrophage": tank_turret, "dendritic_cell": field_gun, "fibroblast": repair_depot,
    "eosinophil": howitzer, "granuloma": concrete_bunker, "epithelial_cell": barbed_wire, "neutrophil": rifleman,
    "monocyte": aa_gunner, "basophil": grenadier, "nk_cell": commando, "net_trap": tank_trap, "keratin_plate": concrete_barrier,
    "b_cell": sniper, "antibody_tagger": spotter, "cytotoxic_t": bazooka_trooper, "opsonin_lance": long_tom,
    "interferon_beacon": radar_tower, "mucus_wall": sticky_barricade, "mast_cell": smoke_launcher, "histamine_spitter": mortar_team,
    "fever_node": flame_turret, "cytokine_storm": shock_turret, "inflammation_zone": water_cannon, "toxic_membrane": barrel_wall,
    "killer_t": chem_trooper, "complement_sprayer": gas_mortar, "lysozyme_pool": gas_canister, "perforin_lancer": toxic_drone,
    "necrosis_bloom": sludge_pit,
}


# --- Enemies (toys: faceless) -----------------------------------------------------

def _trooper(uniform, helmet, weapon="rifle"):
    def design(c, p):
        bob = (0, -1, 0, -1)[phase(p)]
        c.dy += bob
        soldier(c, p, hexc(uniform), helmet=hexc(helmet), weapon=weapon)
        c.dy -= bob
    return design


def _vehicle(body, size=1.0, turret_on=False, boat=False, wheels=True):
    def design(c, p):
        b = hexc(body)
        w, h = 11 * size, 6 * size
        if boat:
            c.poly([(16 - w, 20), (16 + w, 20), (16 + w - 3, 27), (16 - w + 3, 27)], b)
            c.rect(12, 14, 20, 20, shade(b, 0.15))
            wave = phase(p) % 2
            c.line([(16 - w - 1, 28 + wave), (16 + w + 1, 28 - wave)], hexc("#a0d8f0"))
            return
        c.block(16 - w, 22 - h, 16 + w, 22 + h * 0.6, b)
        if turret_on:
            c.blob(16, 18 - h * 0.5, 4.5 * size, 3.5 * size, shade(b, 0.1))
            c.rect(15, 18 - h * 0.5 - 8 * size, 17, 18 - h * 0.5, shade(b, -0.25))
        if wheels:
            roll = phase(p) % 2
            for x in (16 - w + 3, 16, 16 + w - 3):
                c.ellipse(x, 22 + h * 0.6, 2.4, 2.4, hexc("#2a2a2a"))
                c.px(x + roll, 22 + h * 0.6, hexc("#8a8a8a"))
    return design


def _plane(body, size=1.0, bomb=False, paper=False):
    def design(c, p):
        b = hexc(body)
        bank = (0, 1, 0, -1)[phase(p)]
        if paper:
            c.poly([(16, 6), (4, 26 + bank), (16, 22), (28, 26 - bank)], b)
            c.line([(16, 6), (16, 22)], shade(b, -0.2))
            return
        c.ellipse(16, 18, 3.5 * size, 11 * size, b)
        c.poly([(16 - 13 * size, 19 + bank), (16 + 13 * size, 19 - bank), (16, 14)], shade(b, -0.1))
        c.poly([(12, 28), (20, 28), (16, 24)], shade(b, -0.1))
        if bomb:
            c.ellipse(16, 22, 2, 2.5, hexc("#2a2a2a"))
    return design


ENEMIES = {
    "toy_recruit": _trooper("#c8a878", "#a88858"), "toy_soldier": _trooper("#b88a50", "#8a6030"),
    "ranger": _trooper("#8a5a30", "#5a3a20"),
    "troop_truck": _vehicle("#9a8a60"), "armored_carrier": _vehicle("#6a6a58", 1.1, turret_on=True),
    "motorbike": _vehicle("#d04040", 0.55),
    "toy_tank": _vehicle("#8a8a50", 1.0, turret_on=True), "heavy_tank": _vehicle("#5a5a40", 1.25, turret_on=True),
    "paper_plane": _plane("#f0f0f0", paper=True), "jet": _plane("#8a96a8"),
    "toy_bomber": _plane("#7a8a6a", 1.1, bomb=True), "heavy_bomber": _plane("#4a5a3a", 1.25, bomb=True),
    "patrol_boat": _vehicle("#e8e8e8", 0.8, boat=True), "destroyer": _vehicle("#9aa0aa", 1.1, boat=True),
    "submarine": _vehicle("#4a4a5a", 0.9, boat=True), "battleship": _vehicle("#6a707a", 1.35, boat=True),
    "mega_tank": _vehicle("#4a4a30", 1.4, turret_on=True),
}
