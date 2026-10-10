"""World 5 (Galactic Siege): robots and tech (faceless); aliens have faces."""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, bug, legs, phase, robot, turret

HULL = hexc("#8a94a8")
CYAN = hexc("#60f0ff")


def _plate(c, p, color, glow=None):
    c.block(4, 10, 28, 30, color)
    for x, y in ((7, 13), (24, 13), (7, 26), (24, 26)):
        c.px(x, y, shade(color, -0.3))
    if glow:
        c.rect(8, 18, 24, 21, glow)
    c.ellipse(16, 15, 1.4, 1.4, p["pc"])
    return (16, 10)


def hull_plate(c, p):
    return _plate(c, p, HULL)


def scrap_barrier(c, p):
    for x, y, w in ((6, 16, 10), (15, 12, 9), (22, 18, 8), (9, 23, 12)):
        c.block(x - w / 2, y - 3, x + w / 2, y + 4, shade(HULL, (x % 3 - 1) * 0.08))
    c.ellipse(20, 25, 1.4, 1.4, p["pc"])
    return (16, 9)
def energy_barrier(c, p):
    return _plate(c, p, hexc("#5a6a9a"), CYAN)


def radioactive_plate(c, p):
    top = _plate(c, p, hexc("#6a7a50"), hexc("#c8f040"))
    c.ellipse(16, 25, 2.5, 2.5, hexc("#e0d040"))
    return top
def nanite_wall(c, p):
    for x, y in ((9, 22), (16, 17), (23, 22), (12, 27), (20, 27)):
        c.blob(x, y, 5, 4.5, hexc("#6a7a8a"))
    for i in range(10):
        c.px(6 + (i * 7) % 20, 15 + (i * 5) % 14, CYAN)
    c.ellipse(16, 24, 1.4, 1.4, p["pc"])
    return (16, 12)
def force_field(c, p):
    c.ellipse(16, 20, 12, 10, hexc("#60c0ff", 120))
    c.rect(6, 28, 26, 31, HULL)
    c.ellipse(16, 18, 9, 7, hexc("#a0e0ff", 160))
    c.ellipse(16, 29, 1.4, 1.2, p["pc"])
    return (16, 10)
def contamination_zone(c, p):
    c.ellipse(16, 24, 13, 6, hexc("#3a4a2a"))
    c.ellipse(16, 23, 11, 4.5, hexc("#a0e040"))
    for x in (9, 23):
        c.rect(x - 0.5, 12, x + 1, 24, hexc("#e0d040"))
        c.rect(x - 2, 11, x + 3, 13, hexc("#2a2a2a"))
    c.ellipse(16, 23, 1.4, 1.2, p["pc"])
    return (16, 11)
def gravity_well(c, p):
    for r, col in ((11, "#3a2a6a"), (8, "#5a3a9a"), (5, "#8a5ad0"), (2, "#e0c8ff")):
        c.ellipse(16, 21, r, r * 0.7, hexc(col))
    c.ellipse(16, 21, 1.2, 1.2, p["pc"])
    return (16, 13)

def mech_brawler(c, p):
    top = robot(c, p, HULL, CYAN, size=1.15)
    c.rect(4, 17, 8, 23 - (p["act"] == "fire") * 3, shade(HULL, -0.15))
    c.rect(24, 17, 28, 23 - (p["act"] == "fire") * 3, shade(HULL, -0.15))
    c.rect(12, 21, 20, 23, p["pc"])
    return top
def buzz_bot(c, p):
    top = robot(c, p, hexc("#c0c8d0"), CYAN, size=0.85)
    c.rect(11, 20, 21, 21, p["pc"])
    return top
def blade_bot(c, p):
    top = robot(c, p, hexc("#4a5060"), hexc("#ff5050"), size=0.95)
    for side in (-1, 1):
        c.poly([(16 + side * 6, 18), (16 + side * 11, 12 - (p["act"] == "fire") * 2), (16 + side * 7, 22)], hexc("#e0e0e8"))
    c.rect(12, 21, 20, 22, p["pc"])
    return top
def acid_bot(c, p):
    top = robot(c, p, hexc("#6a8a50"), hexc("#c8f040"))
    c.rect(12, 21, 20, 22, p["pc"])
    return top

def _gun(base, head, n=1, length=9, wide=False):
    def design(c, p):
        top = turret(c, p, hexc(base), hexc(head), barrels=n, barrel_len=length, barrel_color=shade(hexc(head), -0.3), wide=wide)
        c.ellipse(16, 20, 1.6, 1.6, p["pc"])
        if p["act"] == "fire":
            c.ellipse(16, top[1] - 1, 1.8, 1.8, CYAN)
        return top
    return design

plasma_cannon = _gun("#5a6070", "#8a94a8", 1, 10, True)
rail_cannon = _gun("#4a5060", "#a0a8b8", 2, 13)
laser_turret = _gun("#5a6070", "#c04040", 1, 9)
ion_cannon = _gun("#4a5a70", "#5a8ad0", 1, 10, True)
orbital_lance = _gun("#3a4050", "#c0c8d8", 1, 16)
arc_thrower = _gun("#5a5070", "#9a70d0", 2, 8)

def gun_drone(c, p):
    hover = (0, -1, 0, -1)[phase(p)] if p["act"] == "idle" else 0
    c.dy += hover
    c.ellipse(16, 19, 8, 5, HULL)
    for x in (6, 26):
        c.rect(x - 3, 13, x + 3, 14, hexc("#c0c0c8"))
        c.rect(x - 0.5, 14, x + 1, 18, OUTLINE)
    c.rect(15, 22, 17, 27 - (p["act"] == "fire"), shade(HULL, -0.3))
    c.ellipse(16, 18, 2, 2, p["pc"])
    c.dy -= hover
    return (16, 13)
def fortress_core(c, p):
    c.block(5, 10, 27, 30, hexc("#5a6070"))
    c.ellipse(16, 20, 6, 6, hexc("#2a3040"))
    c.ellipse(16, 20, 4, 4, CYAN if p["act"] == "idle" else p["pc"])
    return (16, 10)
def tesla_coil(c, p):
    c.block(9, 23, 23, 30, hexc("#5a5a68"))
    c.rect(14, 10, 18, 23, hexc("#b08040"))
    for y in (12, 15, 18, 21):
        c.ellipse(16, y, 4, 1.4, hexc("#d0a050"))
    c.ellipse(16, 8, 4, 3, hexc("#c0c8d0"))
    c.ellipse(16, 8, 1.6, 1.4, p["pc"])
    return (16, 5)
def targeting_beacon(c, p):
    c.rect(15, 12, 17, 30, HULL)
    c.ellipse(16, 10, 5, 5, hexc("#ff5050") if p["act"] != "idle" else hexc("#a03030"))
    c.rect(10, 27, 22, 30, p["pc"])
    return (16, 5)
def scanner_array(c, p):
    c.rect(15, 16, 17, 30, HULL)
    c.ellipse(16, 13, 9, 4, hexc("#c0c8d8"))
    c.ellipse(16, 13, 6, 2.5, hexc("#8a94a8"))
    c.ellipse(16, 13, 1.6, 1.6, p["pc"])
    return (16, 9)
def cryo_emitter(c, p):
    c.block(8, 18, 24, 30, hexc("#7a8aa0"))
    c.ellipse(16, 15, 6, 5, hexc("#a0e0ff"))
    for a in range(6):
        ang = a * math.pi / 3
        c.line([(16, 15), (16 + math.cos(ang) * 4, 15 + math.sin(ang) * 4)], WHITE)
    c.rect(12, 24, 20, 26, p["pc"])
    return (16, 10)
def plasma_vent(c, p):
    c.ellipse(16, 25, 11, 5, hexc("#4a4a58"))
    c.ellipse(16, 24, 7, 3, hexc("#ff7030"))
    big = 1.3 if p["act"] == "fire" else 1.0
    c.poly([(12, 24), (16, 24 - 12 * big), (20, 24)], hexc("#ffb040", 220))
    c.ellipse(24, 26, 1.4, 1.2, p["pc"])
    return (16, 10)
def emp_tower(c, p):
    c.line([(10, 30), (16, 10), (22, 30)], HULL, 2)
    c.line([(12, 22), (20, 22)], HULL)
    c.ellipse(16, 9, 3.5, 3.5, hexc("#f0e050"))
    c.ellipse(16, 9, 1.4, 1.4, p["pc"])
    return (16, 5)
def tractor_beam(c, p):
    c.block(8, 8, 24, 16, HULL)
    c.poly([(11, 16), (21, 16), (25, 30), (7, 30)], hexc("#a0f0c0", 110 if p["act"] == "idle" else 180))
    c.ellipse(16, 12, 1.6, 1.6, p["pc"])
    return (16, 8)
def nanite_sprayer(c, p):
    top = turret(c, p, hexc("#5a6070"), hexc("#7aa070"), barrels=1, barrel_len=7)
    for i in range(5):
        c.px(12 + i * 2, top[1] - 1 - (i % 2), CYAN)
    c.ellipse(16, 20, 1.5, 1.5, p["pc"])
    return top
def toxic_reactor(c, p):
    c.block(8, 12, 24, 30, hexc("#5a6a50"))
    c.ellipse(16, 12, 8, 3, hexc("#a0e040"))
    c.ellipse(16, 21, 3, 3, hexc("#e0d040"))
    c.ellipse(16, 27, 1.4, 1.2, p["pc"])
    return (16, 9)
def plague_drone(c, p):
    top = gun_drone(c, p)
    c.ellipse(16, 18, 3, 2, hexc("#a0e040"))
    return top

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
