"""Birthday Bash: party gear (faceless) against party crashers. The clown and
the goo creatures have faces; toys don't."""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, phase, robot, turret


def gift_box(c, p):
    c.block(6, 12, 26, 30, p["pc"])
    c.rect(14, 12, 18, 30, hexc("#ffd23c"))
    c.rect(6, 19, 26, 22, hexc("#ffd23c"))
    c.ellipse(12, 10, 3.5, 2.5, hexc("#ffd23c"))
    c.ellipse(20, 10, 3.5, 2.5, hexc("#ffd23c"))
    return (16, 8)


def party_mallet(c, p):
    swing = -3 if p["act"] == "fire" else 0
    c.rect(15, 16, 17, 30, hexc("#e0b060"))
    c.block(7, 6 + swing, 25, 16 + swing, p["pc"])
    c.rect(7, 9 + swing, 25, 11 + swing, hexc("#ffd23c"))
    return (16, 6 + swing)


def confetti_cannon(c, p):
    top = turret(c, p, hexc("#ff7ac8"), hexc("#ffd23c"), barrels=1, barrel_len=11, wide=True)
    if p["act"] == "fire":
        for x, col in ((12, "#4ac0e8"), (16, "#ff5a5a"), (20, "#7fe08a")):
            c.px(x, top[1] - 3, hexc(col))
    c.ellipse(16, 20, 1.6, 1.6, p["pc"])
    return top


def balloon_arch(c, p):
    for i, (x, y) in enumerate(((5, 27), (6, 19), (10, 12), (16, 9), (22, 12), (26, 19), (27, 27))):
        c.blob(x, y, 3.6, 3.6, (p["pc"], hexc("#ffd23c"), hexc("#4ac0e8"))[i % 3])
    return (16, 6)


def fireworks_launcher(c, p):
    c.block(8, 22, 24, 30, hexc("#3a3a50"))
    for x, col in ((11, "#ff5a5a"), (16, "#4ac0e8"), (21, "#ffd23c")):
        c.rect(x - 1.5, 10, x + 1.5, 22, hexc(col))
        c.poly([(x - 2, 10), (x, 6 - (p["act"] == "fire") * 3), (x + 2, 10)], hexc(col))
    c.rect(8, 25, 24, 26, p["pc"])
    return (16, 6)


def ice_cream_cake(c, p):
    c.block(4, 16, 28, 30, hexc("#f8d0e0"))
    c.rect(4, 22, 28, 24, hexc("#8a5030"))
    c.ellipse(16, 16, 12, 3, WHITE)
    for x in (8, 14, 20, 25):
        c.px(x, 15, (p["pc"], hexc("#4ac0e8"))[x % 2])
    return (16, 13)


def paper_cup(c, p):
    c.poly([(8, 12), (24, 12), (21, 30), (11, 30)], WHITE)
    for x in (11, 16, 21):
        c.line([(x, 13), (x - (x - 16) * 0.3, 29)], p["pc"])
    c.rect(7, 11, 25, 13, shade(WHITE, -0.1))
    return (16, 11)


def party_blower(c, p):
    out = 8 if p["act"] == "fire" else 0
    c.rect(14, 22, 18, 30, hexc("#ffd23c"))
    c.rect(14, 14 - out, 18, 22, p["pc"])
    c.ellipse(16, 14 - out, 3, 2, p["pc"])
    return (16, 12 - out)


def water_pistol(c, p):
    c.block(6, 14, 24, 21, p["pc"])
    c.rect(20, 21, 25, 30, p["pc"])
    c.rect(4, 15, 6, 17, hexc("#4ac0e8"))
    c.ellipse(13, 12, 3, 2.4, hexc("#4ac0e8", 200))
    return (14, 11)


def noisemaker(c, p):
    spin = phase(p) % 2 if p["act"] != "idle" else 0
    c.rect(15, 18, 17, 30, hexc("#e0b060"))
    c.block(8 + spin, 9, 24 + spin, 18, p["pc"])
    for x in (11, 16, 21):
        c.px(x + spin, 13, hexc("#ffd23c"))
    return (16, 9)


def sparkler(c, p):
    c.line([(16, 30), (16, 10)], hexc("#8a8a90"), 2)
    for a in range(8):
        ang = a * math.pi / 4 + phase(p) * 0.3
        r = 5 if p["act"] == "idle" else 7
        c.line([(16, 9), (16 + math.cos(ang) * r, 9 + math.sin(ang) * r)], hexc("#ffe070"))
    c.ellipse(16, 9, 1.6, 1.6, p["pc"])
    return (16, 4)


def streamer_tangle(c, p):
    for i, col in enumerate((p["pc"], hexc("#ffd23c"), hexc("#4ac0e8"))):
        pts = [(4 + x * 3, 15 + i * 5 + math.sin(x + i) * 3) for x in range(9)]
        c.line(pts, col, 2)
    return (16, 11)


def folding_chair(c, p):
    c.block(8, 6, 24, 18, hexc("#8a8a90"))
    c.rect(8, 18, 24, 21, p["pc"])
    for x in (9, 22):
        c.rect(x, 21, x + 2, 30, hexc("#5a5a60"))
    return (16, 6)


def dart_blaster(c, p):
    c.block(6, 15, 24, 21, hexc("#f08030"))
    c.rect(19, 21, 24, 29, hexc("#f08030"))
    c.rect(3 if p["act"] != "fire" else 0, 17, 7, 19, p["pc"])
    return (15, 13)


def spotlight(c, p):
    c.rect(15, 20, 17, 30, OUTLINE)
    c.block(10, 8, 22, 20, hexc("#3a3a40"))
    c.ellipse(16, 14, 4.5, 4.5, hexc("#fff8c0") if p["act"] == "idle" else WHITE)
    c.rect(10, 18, 22, 20, p["pc"])
    return (16, 8)


def foam_sword(c, p):
    lift = -3 if p["act"] == "fire" else 0
    c.rect(13, 3 + lift, 19, 22 + lift, p["pc"])
    c.rect(9, 22 + lift, 23, 24 + lift, hexc("#ffd23c"))
    c.rect(15, 24 + lift, 17, 30 + lift, hexc("#3a3a40"))
    return (16, 3 + lift)


def bottle_rocket(c, p):
    lift = -3 if p["act"] == "fire" else 0
    c.rect(15, 18, 17, 30, hexc("#c09060"))
    c.block(12, 7 + lift, 20, 20 + lift, p["pc"])
    c.poly([(12, 7 + lift), (16, 2 + lift), (20, 7 + lift)], hexc("#ff5a5a"))
    return (16, 2 + lift)


def disco_ball(c, p):
    c.rect(15, 2, 17, 7, OUTLINE)
    c.blob(16, 16, 9, 9, hexc("#c8c8d8"))
    for x in range(9, 24, 3):
        for y in range(10, 23, 3):
            if (x + y + phase(p)) % 2:
                c.px(x, y, WHITE)
    c.ellipse(16, 16, 1.6, 1.6, p["pc"])
    return (16, 6)


def jelly_wall(c, p):
    jelly = hexc("#ff6aa0", 220)
    wobble = 1 if p["act"] != "idle" else 0
    c.block(5 - wobble, 12, 27 + wobble, 30, jelly)
    c.rect(8, 15, 11, 25, shade(jelly, 0.25))
    c.ellipse(20, 22, 1.6, 1.6, p["pc"])
    return (16, 12)


def bubble_machine(c, p):
    c.block(7, 18, 25, 30, p["pc"])
    c.ellipse(16, 18, 5, 2, hexc("#3a3a40"))
    for x, y, r in ((10, 12, 2.6), (19, 8, 3.2), (24, 14, 2)):
        c.ellipse(x, y - (p["act"] != "idle") * 2, r, r, hexc("#c8f0ff", 150))
    return (16, 6)


def pie_launcher(c, p):
    c.line([(8, 29), (24, 14 if p["act"] != "fire" else 10)], hexc("#a07040"), 2)
    c.ellipse(24, 13 if p["act"] != "fire" else 9, 5, 3, hexc("#f0e8d8"))
    c.block(5, 24, 15, 30, p["pc"])
    return (22, 9)


def candle_stand(c, p):
    c.block(6, 24, 26, 30, hexc("#f0d0a0"))
    for x, col in ((10, "#4ac0e8"), (16, "#ff7ac8"), (22, "#7fe08a")):
        c.rect(x - 1, 14, x + 1, 24, hexc(col))
        flame = 3 if p["act"] != "idle" else 2
        c.poly([(x - 1.5, 14), (x, 14 - flame - 2), (x + 1.5, 14)], hexc("#ffb030"))
    c.rect(6, 26, 26, 27, p["pc"])
    return (16, 9)


def party_horn(c, p):
    c.poly([(8, 24), (8, 18), (26, 12 if p["act"] != "fire" else 10), (26, 28 if p["act"] != "fire" else 30)], p["pc"])
    c.rect(4, 19, 8, 23, hexc("#ffd23c"))
    return (17, 12)


def foam_machine(c, p):
    c.block(7, 18, 25, 30, hexc("#7a8aa0"))
    for x, y in ((10, 14), (16, 11), (22, 14), (13, 9), (19, 8)):
        c.ellipse(x, y - (p["act"] != "idle"), 3, 2.6, WHITE)
    c.rect(7, 24, 25, 26, p["pc"])
    return (16, 6)


def sour_candy_wall(c, p):
    for i, (x, y) in enumerate(((9, 15), (21, 15), (9, 25), (21, 25))):
        c.block(x - 5, y - 4, x + 5, y + 5, (hexc("#f0e040"), hexc("#7fe08a"), hexc("#ff7a5a"), p["pc"])[i])
        for k in range(3):
            c.px(x - 3 + k * 3, y - 2, WHITE)
    return (16, 11)


def lemon_squirter(c, p):
    c.blob(16, 21, 9, 7.5, hexc("#f0e040"))
    c.poly([(14, 14), (18, 14), (16, 8 if p["act"] != "fire" else 5)], hexc("#c0b020"))
    c.ellipse(16, 23, 2, 1.6, p["pc"])
    return (16, 6)


def silly_string(c, p):
    c.block(11, 14, 21, 30, p["pc"])
    c.rect(13, 10, 19, 14, hexc("#e8e8f0"))
    if p["act"] == "fire":
        c.line([(16, 9), (12, 5), (18, 3), (14, 1)], hexc("#ff7ac8"), 1)
    return (16, 9)


def punch_bowl(c, p):
    c.ellipse(16, 22, 12, 7, hexc("#d8e8f0", 220))
    c.ellipse(16, 20, 10, 4, hexc("#e04060"))
    c.ellipse(13, 19, 2, 1.4, hexc("#f0e040"))
    c.rect(13, 27, 19, 30, hexc("#d8e8f0", 220))
    c.ellipse(20, 20, 1.4, 1.2, p["pc"])
    return (16, 14)


def stink_bomb(c, p):
    c.blob(16, 21, 7.5, 7.5, hexc("#5a5a6a"))
    c.rect(15, 11, 17, 14, hexc("#c09060"))
    if p["act"] != "idle":
        for x in (10, 22):
            c.ellipse(x, 11, 2.5, 2, hexc("#a0e040", 180))
    c.ellipse(16, 22, 2, 2, p["pc"])
    return (16, 11)


def moldy_cake(c, p):
    c.block(5, 14, 27, 30, hexc("#e8c8a8"))
    c.rect(5, 14, 26, 17, hexc("#f8f0f0"))
    for x, y in ((10, 20), (20, 22), (14, 26), (23, 16)):
        c.ellipse(x, y, 2.4, 1.8, hexc("#8aa060"))
    c.ellipse(9, 26, 1.4, 1.2, p["pc"])
    return (16, 14)


DESIGNS = {
    "platelet_clot": gift_box, "macrophage": party_mallet, "dendritic_cell": confetti_cannon, "fibroblast": balloon_arch,
    "eosinophil": fireworks_launcher, "granuloma": ice_cream_cake, "epithelial_cell": paper_cup, "neutrophil": party_blower,
    "monocyte": water_pistol, "basophil": noisemaker, "nk_cell": sparkler, "net_trap": streamer_tangle,
    "keratin_plate": folding_chair, "b_cell": dart_blaster, "antibody_tagger": spotlight, "cytotoxic_t": foam_sword,
    "opsonin_lance": bottle_rocket, "interferon_beacon": disco_ball, "mucus_wall": jelly_wall, "mast_cell": bubble_machine,
    "histamine_spitter": pie_launcher, "fever_node": candle_stand, "cytokine_storm": party_horn,
    "inflammation_zone": foam_machine, "toxic_membrane": sour_candy_wall, "killer_t": lemon_squirter,
    "complement_sprayer": silly_string, "lysozyme_pool": punch_bowl, "perforin_lancer": stink_bomb,
    "necrosis_bloom": moldy_cake,
}


# --- Enemies ---------------------------------------------------------------------

def gumdrop(c, p):
    bob = (0, -1, 0, 0)[phase(p)]
    for y in range(16, 28):
        half = 2 + (y - 16) * 0.5
        c.rect(16 - half, y + bob, 16 + half, y + 1 + bob, hexc("#ff6ab0"))


def _windup(body, size=1.0):
    def design(c, p):
        b = hexc(body)
        c.blob(15, 22, 8 * size, 5.5 * size, b)
        c.blob(22, 20, 4 * size, 3.5 * size, b)
        c.ellipse(21, 16, 1.8, 1.8, shade(b, 0.2))
        c.px(24, 20, OUTLINE)
        turn = phase(p) % 2
        c.rect(9, 14 - turn, 11, 18, hexc("#c8c8d0"))
        c.rect(7 - turn, 13 - turn, 13 + turn, 15 - turn, hexc("#c8c8d0"))
        for x in (10, 19):
            c.ellipse(x, 28, 1.6, 1.6, OUTLINE)
    return design


def _bag(body, spots):
    def design(c, p):
        sway = (0, 1, 0, -1)[phase(p)]
        c.block(7 + sway * 0.5, 13, 25 + sway * 0.5, 30, hexc(body))
        c.rect(13, 9, 19, 13, shade(hexc(body), -0.2))
        for x, y in ((11, 18), (20, 21), (15, 26)):
            c.ellipse(x, y, 1.6, 1.6, hexc(spots))
    return design


def bouncy_ball(c, p):
    bounce = (0, -4, -6, -3)[phase(p)]
    c.blob(16, 21 + bounce, 8, 8 - (phase(p) == 0) * 1.5, hexc("#ff5a5a"))
    c.rect(8, 20 + bounce, 24, 22 + bounce, WHITE)


def _car(body, size=1.0):
    def design(c, p):
        roll = phase(p) % 2
        b = hexc(body)
        c.block(16 - 10 * size, 18, 16 + 10 * size, 25, b)
        c.block(16 - 5 * size, 13, 16 + 5 * size, 18, shade(b, 0.15))
        for x in (16 - 6 * size, 16 + 6 * size):
            c.ellipse(x, 26, 2.6, 2.6, hexc("#2a2a2a"))
            c.px(x + roll, 26, hexc("#8a8a8a"))
    return design


def _toy_robot(body, visor, size=1.0):
    def design(c, p):
        robot(c, p, hexc(body), hexc(visor), size=size)
    return design


def _balloon(body, size=1.0, bomb=False):
    def design(c, p):
        sway = (0, 1, 0, -1)[phase(p)]
        b = hexc(body)
        c.line([(16, 22), (16 + sway, 27), (16, 31)], hexc("#e0e0e0"))
        c.blob(16 + sway * 0.5, 13, 7 * size, 8 * size, b)
        c.poly([(15, 21), (17, 21), (16, 23)], b)
        if bomb:
            c.ellipse(16, 13, 2, 2, hexc("#a0e0ff"))
    return design


def _goo(body, spots=None):
    def design(c, p):
        stretch = (0, 1, 0, -1)[phase(p)]
        b = hexc(body)
        c.ellipse(16, 25, 11 + stretch, 5, shade(b, -0.1))
        c.blob(16, 21, 8 - stretch * 0.5, 7, b)
        if spots:
            for x, y in ((12, 19), (20, 18), (17, 23)):
                c.px(x, y, hexc(spots))
        c.eyes(16, 20, 2.5, "angry")
    return design


def _pinata(body, size=1.0):
    def design(c, p):
        bob = (0, -1, 0, -1)[phase(p)]
        c.dy += bob
        b = hexc(body)
        s = size
        c.block(16 - 8 * s, 15, 16 + 6 * s, 25, b)
        c.block(16 + 3 * s, 7, 16 + 8 * s, 16, b)
        for y, col in ((17, "#ffd23c"), (20, "#4ac0e8"), (23, "#7fe08a")):
            c.rect(16 - 8 * s, y, 16 + 6 * s, y + 1, hexc(col))
        for x in (16 - 7 * s, 16 + 4 * s):
            c.rect(x, 25, x + 2, 30, shade(b, -0.2))
        c.dy -= bob
    return design


def clown(c, p):
    bob = (0, -1, 0, -1)[phase(p)]
    c.dy += bob
    c.blob(16, 26, 9, 5, hexc("#4ac0e8"))
    for x, col in ((12, "#ff5a5a"), (20, "#ffd23c")):
        c.ellipse(x, 26, 1.6, 1.6, hexc(col))
    c.blob(16, 15, 8, 7.5, hexc("#f8f0f0"))
    c.ellipse(8, 13, 3, 3.5, hexc("#ff6a1a"))
    c.ellipse(24, 13, 3, 3.5, hexc("#ff6a1a"))
    c.eyes(16, 13, 3, "angry")
    c.ellipse(16, 16, 2, 2, hexc("#ff2a2a"))
    c.mouth(16, 19, "smile", 6)
    c.poly([(12, 8), (16, 1), (20, 8)], hexc("#4ac0e8"))
    c.dy -= bob


ENEMIES = {
    "gumdrop": gumdrop, "windup_mouse": _windup("#a8a8b8", 0.85), "windup_racer": _windup("#e04040", 1.0),
    "party_bag": _bag("#4ac0e8", "#ffd23c"), "goodie_bag": _bag("#7a4ac0", "#ff7ac8"), "bouncy_ball": bouncy_ball,
    "toy_car": _car("#40a0ff", 0.8), "toy_robot": _toy_robot("#a0a8b8", "#ff4040"), "mega_robot": _toy_robot("#6a7080", "#ffd040", 1.2),
    "balloon": _balloon("#ff7ac8", 0.85), "big_balloon": _balloon("#a040e0", 1.0), "water_balloon": _balloon("#40b0ff", 0.95, True),
    "soda_spill": _goo("#9a5a2a", "#e8d0b0"), "frosting_blob": _goo("#ffb0d8", "#4ac0e8"),
    "pinata": _pinata("#ff7ac8"), "mini_pinata": _pinata("#ffa040", 0.75), "clown": clown,
}
