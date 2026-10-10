"""World 4 (Total War): a toy war. Toys are objects, so nothing has a face."""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, phase, robot, soldier, turret

OLIVE = hexc("#6a7a40")
STEEL = hexc("#7a8088")


def sandbags(c, p):
    for row, y in enumerate((26, 20, 14)):
        for i in range(3 - (row == 2)):
            x = 8 + i * 8 + (row % 2) * 4
            c.blob(x, y, 4.5, 3, hexc("#c8b080"))
    c.ellipse(16, 26, 1.4, 1.2, p["pc"])
    return (16, 11)


def tank_turret(c, p):
    return turret(c, p, OLIVE, shade(OLIVE, 0.1), barrels=1, barrel_len=10, wide=True)


def field_gun(c, p):
    top = turret(c, p, hexc("#5a5a48"), OLIVE, barrels=1, barrel_len=12)
    for x in (8, 24):
        c.ellipse(x, 28, 3.5, 3.5, hexc("#3a3a30"))
    c.ellipse(16, 20, 1.6, 1.6, p["pc"])
    return top


def repair_depot(c, p):
    c.block(5, 12, 27, 30, hexc("#8a8a90"))
    c.poly([(4, 13), (16, 5), (28, 13)], hexc("#a04030"))
    c.rect(13, 16, 19, 18, hexc("#e8e8e8"))
    c.rect(15, 14, 17, 20, hexc("#e8e8e8"))
    c.rect(11, 24, 21, 30, p["pc"])
    return (16, 5)


def howitzer(c, p):
    top = turret(c, p, hexc("#4a5a3a"), OLIVE, barrels=1, barrel_len=14, wide=True)
    c.rect(12, 24, 20, 26, p["pc"])
    return top


def concrete_bunker(c, p):
    c.ellipse(16, 24, 13, 7, hexc("#8a8a88"))
    c.ellipse(16, 20, 11, 7, hexc("#a8a8a4"))
    c.rect(9, 19, 23, 21, hexc("#2a2a2a") if p["act"] == "idle" else p["pc"])
    return (16, 13)


def barbed_wire(c, p):
    for x in (6, 16, 26):
        c.line([(x - 4, 28), (x + 4, 14)], hexc("#7a5a3a"), 2)
        c.line([(x + 4, 28), (x - 4, 14)], hexc("#7a5a3a"), 2)
    for y in (17, 23):
        c.line([(2, y), (30, y)], hexc("#b0b0b8"))
        for x in range(4, 30, 4):
            c.px(x, y - 1, hexc("#d8d8e0"))
    c.ellipse(16, 21, 1.4, 1.4, p["pc"])
    return (16, 13)


def rifleman(c, p):
    return soldier(c, p, OLIVE, weapon="rifle", helmet=shade(p["pc"], -0.2))


def aa_gunner(c, p):
    return turret(c, p, hexc("#5a6a40"), shade(p["pc"], -0.1), barrels=2, barrel_len=11)


def grenadier(c, p):
    return soldier(c, p, hexc("#7a6a40"), weapon="grenade", weapon_color=p["pc"])


def commando(c, p):
    top = soldier(c, p, hexc("#3a4a3a"), weapon="knife", helmet=hexc("#2a2a2a"))
    c.rect(11, 15, 21, 16, p["pc"])
    return top


def tank_trap(c, p):
    steel = hexc("#5a5a60")
    c.line([(8, 28), (24, 12)], steel, 3)
    c.line([(24, 28), (8, 12)], steel, 3)
    c.line([(16, 30), (16, 10)], steel, 3)
    c.ellipse(16, 20, 1.6, 1.6, p["pc"])
    return (16, 10)


def concrete_barrier(c, p):
    c.poly([(4, 30), (8, 12), (24, 12), (28, 30)], hexc("#9a9a98"))
    c.poly([(6, 29), (9, 13), (23, 13), (26, 29)], hexc("#b8b8b4"))
    for x in (10, 18):
        c.rect(x, 20, x + 4, 23, p["pc"])
    return (16, 12)


def sniper(c, p):
    top = soldier(c, p, hexc("#5a6a50"), weapon="rifle", helmet=hexc("#4a5a40"))
    c.ellipse(20, 12, 1.5, 1.5, p["pc"])
    return top


def spotter(c, p):
    top = soldier(c, p, hexc("#6a7050"), weapon=None)
    c.rect(12, 13, 20, 15, OUTLINE)
    c.ellipse(13, 14, 1.6, 1.6, p["pc"])
    c.ellipse(19, 14, 1.6, 1.6, p["pc"])
    return top


def bazooka_trooper(c, p):
    return soldier(c, p, OLIVE, weapon="bazooka", weapon_color=shade(p["pc"], -0.2))


def long_tom(c, p):
    top = turret(c, p, hexc("#4a4a40"), hexc("#6a6a50"), barrels=1, barrel_len=17)
    c.rect(12, 25, 20, 27, p["pc"])
    return top


def radar_tower(c, p):
    c.line([(10, 30), (16, 12), (22, 30)], STEEL, 2)
    c.line([(12, 24), (20, 24)], STEEL)
    spin = phase(p) % 2 if p["act"] != "idle" else 0
    c.ellipse(16, 10, 8 - spin * 3, 3, hexc("#c8c8d0"))
    c.ellipse(16, 10, 2, 2, p["pc"])
    return (16, 6)


def sticky_barricade(c, p):
    c.block(4, 12, 28, 30, hexc("#8a6a40"))
    goo = hexc("#c8e040", 230)
    for x, y in ((8, 14), (16, 13), (24, 15)):
        c.ellipse(x, y, 3.5, 2, goo)
        c.rect(x - 0.5, y, x + 1, y + 5, goo)
    c.ellipse(16, 24, 1.4, 1.4, p["pc"])
    return (16, 11)


def smoke_launcher(c, p):
    top = turret(c, p, hexc("#5a5a50"), hexc("#7a7a70"), barrels=3, barrel_len=7)
    if p["act"] == "fire":
        c.ellipse(16, 6, 4, 3, hexc("#d0d0d8", 220))
    c.ellipse(16, 20, 1.5, 1.5, p["pc"])
    return top


def mortar_team(c, p):
    c.rect(18, 12, 22, 26, hexc("#4a4a40"))
    c.ellipse(20, 27, 4, 1.6, hexc("#3a3a30"))
    return soldier(c, p, OLIVE, x=10, weapon=None, helmet=shade(p["pc"], -0.2))


def flame_turret(c, p):
    top = turret(c, p, hexc("#5a4a3a"), hexc("#a04030"), barrels=1, barrel_len=9, wide=True)
    if p["act"] == "fire":
        c.poly([(13, top[1]), (16, top[1] - 6), (19, top[1])], hexc("#ffb030"))
    c.ellipse(16, 20, 1.5, 1.5, p["pc"])
    return top


def shock_turret(c, p):
    c.block(8, 22, 24, 30, STEEL)
    c.rect(14, 10, 18, 22, hexc("#9aa0a8"))
    for y in (12, 16, 20):
        c.ellipse(16, y, 5, 1.6, hexc("#c08030"))
    c.ellipse(16, 8, 3, 3, p["pc"] if p["act"] != "idle" else hexc("#a0e0ff"))
    return (16, 5)


def water_cannon(c, p):
    top = turret(c, p, hexc("#3a5a8a"), hexc("#5a7aaa"), barrels=1, barrel_len=10, wide=True)
    c.ellipse(16, 26, 3, 1.4, p["pc"])
    return top


def barrel_wall(c, p):
    for x in (9, 23):
        c.block(x - 5, 12, x + 5, 30, hexc("#4a6a3a"))
        for y in (16, 25):
            c.rect(x - 5, y, x + 5, y + 1, hexc("#2a3a20"))
    c.ellipse(16, 20, 1.6, 1.6, p["pc"])
    return (16, 12)


def chem_trooper(c, p):
    top = soldier(c, p, hexc("#c8b040"), weapon="rifle", helmet=hexc("#e0d060"))
    c.rect(13, 15, 19, 17, hexc("#3a3a3a"))
    c.ellipse(16, 22, 1.5, 1.5, p["pc"])
    return top


def gas_mortar(c, p):
    top = turret(c, p, hexc("#5a5a40"), hexc("#8a9a40"), barrels=1, barrel_len=8, wide=True)
    c.ellipse(16, 20, 1.6, 1.6, p["pc"])
    return top


def gas_canister(c, p):
    c.block(10, 10, 22, 30, hexc("#7a9a3a"))
    c.rect(13, 6, 19, 10, hexc("#5a5a5a"))
    c.rect(10, 18, 22, 21, hexc("#e0d040"))
    if p["act"] == "fire":
        c.ellipse(16, 4, 4, 2.5, hexc("#c8e070", 200))
    c.ellipse(16, 26, 1.5, 1.5, p["pc"])
    return (16, 5)


def toxic_drone(c, p):
    c.ellipse(16, 20, 7, 4, hexc("#5a6a50"))
    for x in (7, 25):
        c.rect(x - 0.5, 14, x + 1, 19, hexc("#3a3a3a"))
        c.rect(x - 4, 13 - phase(p) % 2, x + 4, 14 - phase(p) % 2, hexc("#c0c0c8"))
    c.ellipse(16, 25, 2, 2, p["pc"])
    return (16, 14)


def sludge_pit(c, p):
    c.ellipse(16, 24, 13, 6, hexc("#4a4a3a"))
    c.ellipse(16, 23, 11, 4.5, hexc("#8aa040"))
    for x, y in ((11, 22), (19, 23), (15, 24)):
        c.ellipse(x, y, 1.6, 1.4, hexc("#b8d060"))
    c.ellipse(24, 23, 1.4, 1.2, p["pc"])
    return (16, 17)


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
