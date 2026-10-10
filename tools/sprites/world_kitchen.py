"""Kitchen Defense: kitchen gear (faceless) against pantry pests (faces)."""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, animal, bug, legs, phase, turret

METAL = hexc("#b8bcc4")
WOOD = hexc("#b08050")


def tin_can(c, p):
    c.block(8, 10, 24, 30, METAL)
    c.rect(8, 15, 24, 25, p["pc"])
    c.rect(8, 10, 24, 11, shade(METAL, 0.15))
    return (16, 10)


def rolling_pin(c, p):
    roll = -2 if p["act"] == "fire" else 0
    c.rect(2, 19 + roll, 6, 22 + roll, WOOD)
    c.rect(26, 19 + roll, 30, 22 + roll, WOOD)
    c.block(6, 16 + roll, 26, 25 + roll, hexc("#d8b080"))
    c.rect(14, 18 + roll, 18, 23 + roll, p["pc"])
    return (16, 16 + roll)


def cork_popper(c, p):
    c.block(11, 12, 21, 30, hexc("#3a6a3a"))
    c.rect(13, 7 if p["act"] != "fire" else 3, 19, 12, hexc("#c8a070"))
    c.rect(11, 20, 21, 24, p["pc"])
    return (16, 6)


def sponge(c, p):
    c.block(5, 14, 27, 30, hexc("#f0d040"))
    c.rect(5, 14, 26, 18, hexc("#3a9a4a"))
    for x, y in ((9, 22), (15, 25), (21, 21), (24, 27), (12, 27)):
        c.ellipse(x, y, 1.2, 1, hexc("#c8a830"))
    c.ellipse(19, 26, 1.4, 1.2, p["pc"])
    return (16, 14)


def pressure_cooker(c, p):
    c.blob(16, 22, 10, 8, METAL)
    c.rect(4, 20, 7, 22, OUTLINE)
    c.rect(25, 20, 28, 22, OUTLINE)
    c.rect(14, 10, 18, 14, hexc("#5a5a60"))
    if p["act"] == "fire":
        c.ellipse(16, 6, 4, 3, hexc("#e8e8f0", 210))
    c.ellipse(16, 22, 2, 2, p["pc"])
    return (16, 9)


def cast_iron_pan(c, p):
    c.line([(24, 22), (30, 28)], hexc("#3a3a40"), 3)
    c.ellipse(15, 20, 11, 9, hexc("#3a3a40"))
    c.ellipse(15, 20, 8.5, 7, hexc("#5a5a62") if p["act"] == "idle" else shade(p["pc"], -0.1))
    return (15, 11)


def sugar_cube(c, p):
    c.block(7, 12, 25, 30, hexc("#f8f8f8"))
    for x, y in ((10, 16), (18, 15), (14, 22), (21, 25), (11, 27)):
        c.px(x, y, hexc("#d8d8e0"))
    c.px(20, 20, p["pc"])
    return (16, 12)


def fork(c, p):
    jab = -3 if p["act"] == "fire" else 0
    c.rect(15, 16 + jab, 17, 30 + jab, METAL)
    c.rect(11, 12 + jab, 21, 16 + jab, METAL)
    for x in (11, 14, 17, 20):
        c.rect(x, 4 + jab, x + 1, 13 + jab, METAL)
    c.rect(14, 24 + jab, 18, 28 + jab, p["pc"])
    return (16, 4 + jab)


def spray_bottle(c, p):
    c.block(10, 14, 22, 30, hexc("#80c8f0", 230))
    c.rect(12, 9, 20, 14, p["pc"])
    c.rect(20, 10, 24, 12, p["pc"])
    c.line([(18, 14), (22, 18)], OUTLINE)
    return (16, 9)


def egg_beater(c, p):
    c.rect(15, 4, 17, 14, WOOD)
    spin = phase(p) % 2 if p["act"] != "idle" else 0
    for x in (12 + spin, 20 - spin):
        c.ellipse(x, 22, 4, 8, METAL)
        c.ellipse(x, 22, 2.6, 6.5, (0, 0, 0, 0))
    c.rect(13, 13, 19, 15, p["pc"])
    return (16, 4)


def pizza_cutter(c, p):
    c.rect(15, 18, 17, 30, hexc("#c04030"))
    c.ellipse(16, 13, 7, 7, METAL)
    c.ellipse(16, 13, 2, 2, p["pc"])
    return (16, 6)


def cling_wrap(c, p):
    wrap = hexc("#e0f0ff", 150)
    c.block(4, 12, 28, 30, wrap)
    for y in (15, 21, 26):
        c.line([(5, y), (27, y + 1)], hexc("#ffffff", 200))
    c.ellipse(16, 20, 1.6, 1.6, p["pc"])
    return (16, 12)


def cutting_board(c, p):
    c.block(5, 11, 27, 30, WOOD)
    c.ellipse(16, 14, 2, 1.4, hexc("#6a4a28"))
    for y in (18, 23, 27):
        c.line([(7, y), (25, y)], shade(WOOD, -0.1))
    c.rect(5, 27, 26, 29, p["pc"])
    return (16, 11)


def pepper_grinder(c, p):
    c.block(11, 9, 21, 30, hexc("#3a2a20"))
    c.ellipse(16, 8, 4, 2.5, METAL)
    c.rect(11, 18, 21, 20, p["pc"])
    if p["act"] == "fire":
        for x in (13, 16, 19):
            c.px(x, 4, OUTLINE)
    return (16, 5)


def flour_sifter(c, p):
    c.block(8, 12, 24, 26, METAL)
    c.rect(24, 16, 28, 18, OUTLINE)
    for x in range(9, 24, 3):
        c.px(x, 28, hexc("#f8f8f0") if p["act"] != "idle" else hexc("#e0e0d8"))
    c.rect(8, 16, 24, 18, p["pc"])
    return (16, 12)


def mousetrap(c, p):
    c.block(4, 18, 28, 29, WOOD)
    snap = p["act"] == "fire"
    c.rect(6, 19 if snap else 12, 26, 21 if snap else 14, METAL)
    c.ellipse(20, 24, 2.4, 1.8, hexc("#f0d040"))
    c.ellipse(10, 25, 1.4, 1.2, p["pc"])
    return (16, 12)


def toaster(c, p):
    c.block(6, 13, 26, 30, METAL)
    for x in (10, 18):
        c.rect(x, 13, x + 5, 15, OUTLINE)
        if p["act"] == "fire":
            c.rect(x, 8, x + 5, 13, hexc("#d8a060"))
    c.rect(26, 18, 28, 22, p["pc"])
    return (16, 8)


def kitchen_lamp(c, p):
    c.rect(15, 4, 17, 12, OUTLINE)
    c.poly([(8, 20), (12, 12), (20, 12), (24, 20)], p["pc"])
    c.ellipse(16, 21, 4, 2.5, hexc("#fff8c0") if p["act"] == "idle" else WHITE)
    return (16, 4)


def flypaper(c, p):
    c.rect(15, 4, 17, 8, OUTLINE)
    c.block(11, 8, 21, 30, hexc("#e8c840"))
    for x, y in ((14, 14), (18, 21), (14, 26)):
        c.px(x, y, OUTLINE)
    c.ellipse(16, 18, 1.4, 1.4, p["pc"])
    return (16, 4)


def ice_tray(c, p):
    c.block(5, 14, 27, 28, hexc("#a0d8f0"))
    for x in (8, 14, 20):
        for y in (16, 22):
            c.block(x, y, x + 4, y + 4, hexc("#e0f8ff"))
    c.ellipse(26, 26, 1.4, 1.2, p["pc"])
    return (16, 14)


def ketchup_squirter(c, p):
    c.block(10, 12, 22, 30, hexc("#d03030"))
    c.poly([(13, 12), (19, 12), (16, 5 if p["act"] != "fire" else 3)], hexc("#f0f0f0"))
    c.rect(12, 18, 20, 23, p["pc"])
    return (16, 4)


def stove_burner(c, p):
    c.ellipse(16, 22, 12, 7, hexc("#3a3a40"))
    hot = hexc("#ff7030") if p["act"] != "idle" else hexc("#c04030")
    for r in (9, 6, 3):
        c.ellipse(16, 21, r, r * 0.55, hot)
        c.ellipse(16, 21, r - 1.2, (r - 1.2) * 0.55, hexc("#3a3a40"))
    c.ellipse(16, 21, 1.4, 1, p["pc"])
    return (16, 15)


def bug_zapper(c, p):
    c.block(9, 8, 23, 28, hexc("#5a5a60"))
    for x in range(11, 22, 3):
        c.rect(x, 10, x + 1, 26, hexc("#8040f0") if p["act"] == "idle" else hexc("#e0d0ff"))
    c.rect(9, 27, 23, 30, p["pc"])
    return (16, 8)


def hot_griddle(c, p):
    c.block(3, 18, 29, 28, hexc("#3a3a40"))
    c.rect(5, 19, 27, 21, hexc("#ff7040") if p["act"] != "idle" else hexc("#8a4a3a"))
    for x in (9, 16, 23):
        c.line([(x, 16), (x + 1, 13), (x, 10)], hexc("#e0e0e8", 160))
    c.ellipse(16, 25, 1.4, 1.2, p["pc"])
    return (16, 12)


def soap_bar(c, p):
    c.blob(16, 22, 12, 7, hexc("#f0b8d8"))
    for x, y in ((7, 14), (24, 13), (16, 11)):
        c.ellipse(x, y, 2, 2, hexc("#e8f8ff", 200))
    c.ellipse(16, 22, 1.6, 1.4, p["pc"])
    return (16, 11)


def bug_spray(c, p):
    c.block(10, 11, 22, 30, hexc("#e8e8f0"))
    c.rect(13, 6, 19, 11, hexc("#5a5a60"))
    c.rect(10, 17, 22, 24, p["pc"])
    if p["act"] == "fire":
        c.ellipse(20, 4, 3, 2, hexc("#c8e070", 200))
    return (16, 6)


def pest_mister(c, p):
    c.blob(16, 23, 8, 7, hexc("#5a9a5a"))
    c.rect(15, 9, 17, 16, OUTLINE)
    c.rect(15, 9, 22, 11, OUTLINE)
    c.rect(11, 22, 21, 24, p["pc"])
    return (16, 9)


def vinegar_bowl(c, p):
    c.ellipse(16, 22, 12, 7, hexc("#f0f0f8"))
    c.ellipse(16, 20, 10, 4, hexc("#d8c870"))
    if p["act"] == "fire":
        for x in (11, 21):
            c.ellipse(x, 14, 1.6, 1.6, hexc("#e8e0a0", 200))
    c.rect(10, 25, 22, 27, p["pc"])
    return (16, 14)


def ant_bait_station(c, p):
    c.block(6, 18, 26, 29, hexc("#3a3a40"))
    c.ellipse(16, 17, 10, 4, hexc("#5a5a62"))
    for x in (9, 23):
        c.rect(x - 1, 25, x + 2, 28, hexc("#1a1a1a"))
    c.ellipse(16, 17, 2, 1.4, p["pc"])
    return (16, 13)


def moldy_bread(c, p):
    c.block(5, 12, 27, 30, hexc("#d8a060"))
    c.rect(7, 14, 25, 28, hexc("#f0d8a0"))
    for x, y in ((11, 18), (20, 17), (15, 24), (22, 25)):
        c.ellipse(x, y, 2.5, 2, hexc("#7aa060"))
    c.ellipse(9, 25, 1.4, 1.2, p["pc"])
    return (16, 12)


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
