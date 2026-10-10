"""World 2 (Backyard Bugs): bugs defend the anthill. Bugs have faces; plants and
objects don't. Attack styles come from World 1's slots (draw_sprites.py)."""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, bug, legs, phase


def pebble_wall(c, p):
    for x, y, r, col in ((9, 25, 5, "#9a9aa0"), (22, 25, 5.5, "#8a8a92"), (15, 17, 5.5, "#a8a8b0"), (24, 15, 3.5, "#9090a0"), (7, 15, 3.5, "#a0a0a8")):
        c.blob(x, y, r, r * 0.85, hexc(col))
    c.ellipse(15, 26, 1.5, 1.2, p["pc"])
    return (16, 11)


def stag_beetle(c, p):
    return bug(c, p, hexc("#7a3a20"), hexc("#5a2a18"), pincers=True, spots=p["pc"])


def bombardier_beetle(c, p):
    top = bug(c, p, hexc("#e07030"), hexc("#2a2a30"), spots=hexc("#2a2a30"))
    c.ellipse(16, 27, 2.4, 1.6, p["pc"])
    return top


def moss_clump(c, p):
    for x, y in ((9, 22), (16, 18), (23, 22), (12, 26), (20, 26), (16, 24)):
        c.blob(x, y, 5, 4.5, hexc("#5aa040"))
    for x, y in ((11, 20), (19, 19), (16, 25)):
        c.px(x, y, hexc("#8ad060"))
    c.ellipse(24, 26, 1.4, 1.4, p["pc"])
    return (16, 13)


def praying_mantis(c, p):
    green = hexc("#7ac850")
    c.ellipse(16, 24, 4, 6, shade(green, -0.1))
    up = -2 if p["act"] == "fire" else 0
    c.line([(13, 18), (9, 13 + up), (11, 10 + up)], shade(green, -0.2), 2)
    c.line([(19, 18), (23, 13 + up), (21, 10 + up)], shade(green, -0.2), 2)
    c.poly([(11, 13), (21, 13), (16, 20)], green)
    c.eyes(16, 14, 3, p["mood"])
    c.ellipse(16, 25, 1.5, 1.5, p["pc"])
    return (16, 11)


def tree_stump(c, p):
    bark = hexc("#7a5030")
    c.block(6, 14, 26, 30, bark)
    c.ellipse(16, 14, 10, 4, hexc("#d8b078"))
    c.ellipse(16, 14, 6, 2.4, hexc("#c09060"))
    c.ellipse(16, 14, 2.5, 1, hexc("#a87850") if p["act"] == "idle" else p["pc"])
    return (16, 10)


def twig_wall(c, p):
    for y, tilt in ((16, 2), (21, -2), (26, 1)):
        c.line([(4, y), (28, y + tilt)], hexc("#8a6038"), 3)
        c.line([(4, y - 1), (28, y + tilt - 1)], hexc("#a87848"))
    c.ellipse(23, 13, 2, 1.4, p["pc"])
    return (16, 13)


def worker_ant(c, p):
    return bug(c, p, hexc("#a03a2a"), rx=6, ry=5.5, spots=p["pc"])


def acid_ant(c, p):
    top = bug(c, p, hexc("#5a9a3a"), rx=6, ry=5.5)
    c.ellipse(16, 24, 2, 2, p["pc"])
    return top


def honeybee(c, p):
    top = bug(c, p, hexc("#f0c040"), hexc("#3a2a20"), wings=hexc("#d0e8ff", 200), stinger=hexc("#2a2a20"))
    for y in (19, 23):
        c.rect(10, y, 23, y + 1.5, hexc("#3a2a20"))
    c.ellipse(16, 21, 1.5, 1.5, p["pc"])
    return top


def bullet_ant(c, p):
    return bug(c, p, hexc("#2a2228"), stinger=p["pc"], spots=shade(p["pc"], -0.2))


def sap_blob(c, p):
    amber = hexc("#e0a030", 235)
    c.ellipse(16, 22, 11, 8, shade(amber, -0.15))
    c.ellipse(15, 21, 10, 7, amber)
    c.ellipse(12, 19, 2.5, 1.6, shade(amber, 0.25))
    c.rect(20, 27, 22, 31, amber)
    c.ellipse(19, 22, 1.4, 1.4, p["pc"])
    return (16, 14)


def acorn_shell(c, p):
    c.blob(16, 22, 9, 8, hexc("#b07840"))
    c.ellipse(16, 15, 10, 4.5, hexc("#6a4a28"))
    for x in (9, 13, 17, 21):
        c.px(x, 14, hexc("#8a6038"))
    c.rect(15, 9, 17, 12, hexc("#6a4a28"))
    c.ellipse(16, 25, 1.6, 1.6, p["pc"])
    return (16, 9)


def _spider(c, p, body, eyes4=False):
    for i in range(4):
        for side in (-1, 1):
            a = -0.5 + i * 0.45
            c.line([(16 + side * 5, 21), (16 + side * (9 + i % 2), 21 + math.sin(a) * 6), (16 + side * 12, 24 + i)], shade(body, -0.3))
    c.blob(16, 21, 7, 6.5, body)
    if eyes4:
        for ex in (12.5, 15, 17, 19.5):
            c.ellipse(ex, 18, 1.2, 1.2, WHITE)
            c.px(ex, 18, OUTLINE)
    else:
        c.eyes(16, 19, 2.5, p["mood"])
    return (16, 14)


def spitting_spider(c, p):
    top = _spider(c, p, hexc("#c09060"))
    c.ellipse(16, 24, 1.8, 1.6, p["pc"])
    return top


def firefly(c, p):
    top = bug(c, p, hexc("#5a4a3a"), hexc("#c04030"), wings=hexc("#c0c8d0", 200))
    glow = p["pc"] if p["act"] != "idle" else hexc("#e8f070")
    c.ellipse(16, 26, 4, 2.6, glow)
    return top


def assassin_bug(c, p):
    top = bug(c, p, hexc("#8a5a30"), hexc("#5a3820"), antennae=False)
    c.line([(16, top[1] + 1), (16, top[1] - 4 - (p["act"] == "fire") * 2)], OUTLINE)
    c.ellipse(16, 22, 1.5, 1.5, p["pc"])
    return top


def jumping_spider(c, p):
    top = _spider(c, p, hexc("#3a3a40"), eyes4=True)
    c.rect(12, 24, 20, 25, p["pc"])
    return top


def glowworm_lantern(c, p):
    c.rect(14, 6, 18, 9, hexc("#5a5a60"))
    c.block(9, 9, 23, 28, hexc("#6a5a40"))
    c.rect(11, 11, 21, 26, hexc("#f0e080") if p["act"] == "idle" else p["pc"])
    c.ellipse(16, 18, 3, 3, hexc("#fff8c0"))
    return (16, 6)


def spiderweb(c, p):
    silk = hexc("#e8e8f0", 220)
    for a in range(8):
        ang = a * math.pi / 4
        c.line([(16, 19), (16 + math.cos(ang) * 13, 19 + math.sin(ang) * 11)], silk)
    for r in (4, 8, 12):
        pts = [(16 + math.cos(a * math.pi / 4) * r, 19 + math.sin(a * math.pi / 4) * r * 0.85) for a in range(9)]
        c.line(pts, silk)
    c.ellipse(16, 19, 1.6, 1.6, p["pc"])
    return (16, 8)


def stink_bug(c, p):
    green = hexc("#6a9a50")
    c.poly([(16, 10), (26, 18), (22, 29), (10, 29), (6, 18)], shade(green, -0.15))
    c.poly([(16, 11), (25, 18), (21, 28), (11, 28), (7, 18)], green)
    legs(c, 16, 22, 9, 6, shade(green, -0.4), 3, p)
    c.eyes(16, 16, 3, p["mood"])
    c.ellipse(16, 23, 2, 2, p["pc"])
    return (16, 10)


def spittlebug(c, p):
    for x, y in ((8, 26), (24, 26), (12, 28), (20, 28)):
        c.ellipse(x, y, 3, 2.4, hexc("#f0f4f8"))
    return bug(c, p, hexc("#a0c040"), rx=7, ry=6, spots=p["pc"])


def magnifying_glass(c, p):
    c.line([(20, 22), (27, 29)], hexc("#6a4020"), 3)
    c.ellipse(13, 15, 8, 8, hexc("#8a8a90"))
    c.ellipse(13, 15, 6.5, 6.5, hexc("#c8e8f8") if p["act"] == "idle" else hexc("#fff0a0"))
    c.ellipse(10, 12, 1.6, 1.6, WHITE)
    c.ellipse(16, 18, 1.5, 1.5, p["pc"])
    return (13, 7)


def click_beetle(c, p):
    top = bug(c, p, hexc("#3a3040"), spots=shade(p["pc"], 0.1))
    if p["act"] == "fire":
        c.line([(10, 8), (8, 5)], hexc("#ffe060"))
        c.line([(22, 8), (24, 5)], hexc("#ffe060"))
    return top


def sprinkler(c, p):
    c.ellipse(16, 27, 9, 3, hexc("#4a7a3a"))
    c.rect(14, 14, 18, 27, hexc("#9aa0a8"))
    spin = phase(p) if p["act"] != "idle" else 0
    c.rect(8, 13, 24, 15, p["pc"])
    for x in (7, 25):
        c.ellipse(x, 12 - spin, 1.4, 1.4, hexc("#80c8f0"))
    return (16, 12)


def nettle_patch(c, p):
    leaf = hexc("#4a8a3a")
    for x, y, a in ((9, 22, -0.4), (16, 18, 0), (23, 22, 0.4), (12, 27, -0.2), (21, 27, 0.2)):
        c.poly([(x, y - 6), (x - 3.5, y), (x, y + 3), (x + 3.5, y)], leaf)
        c.line([(x, y - 5), (x, y + 2)], shade(leaf, -0.2))
        for s in (-1, 1):
            c.px(x + s * 3, y - 3, hexc("#e8f0d0"))
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return (16, 12)


def paper_wasp(c, p):
    top = bug(c, p, hexc("#e0b030"), hexc("#3a2a1a"), wings=hexc("#d0d8e8", 200), stinger=OUTLINE, rx=6, ry=6.5)
    for y in (20, 24):
        c.rect(11, y, 21, y + 1.4, hexc("#3a2a1a"))
    c.ellipse(16, 22, 1.4, 1.4, p["pc"])
    return top


def blister_beetle(c, p):
    return bug(c, p, hexc("#3a8a8a"), hexc("#2a5a6a"), spots=p["pc"])


def toxic_mushroom(c, p):
    c.rect(13, 19, 19, 29, hexc("#f0e8d8"))
    puff = 1 if p["act"] == "fire" else 0
    c.ellipse(16, 16 - puff, 11, 7, hexc("#d03a3a"))
    for x, y in ((11, 14), (18, 12), (21, 17), (14, 18)):
        c.ellipse(x, y - puff, 1.6, 1.4, WHITE)
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return (16, 9)


def scorpion(c, p):
    sting = -2 if p["act"] == "fire" else 0
    c.line([(16, 26), (22, 28), (26, 22), (24, 15 + sting)], hexc("#7a4a2a"), 2)
    c.poly([(23, 14 + sting), (26, 15 + sting), (24, 11 + sting)], p["pc"])
    return bug(c, p, hexc("#a06a3a"), pincers=True, rx=6.5, ry=5.5)


def poison_ivy(c, p):
    leaf = hexc("#3a7a2a")
    for cx, cy in ((10, 21), (22, 21), (16, 15)):
        for a in (-0.9, 0.9, math.pi / 2 + math.pi):
            lx, ly = cx + math.cos(a - math.pi / 2) * 3, cy + math.sin(a - math.pi / 2) * 3
            c.ellipse(lx, ly, 3, 2.2, leaf)
        c.px(cx, cy, hexc("#9ad070"))
    c.rect(4, 27, 28, 30, hexc("#5a4a30"))
    c.ellipse(16, 26, 1.4, 1.4, p["pc"])
    return (16, 9)


DESIGNS = {
    "platelet_clot": pebble_wall, "macrophage": stag_beetle, "dendritic_cell": bombardier_beetle, "fibroblast": moss_clump,
    "eosinophil": praying_mantis, "granuloma": tree_stump, "epithelial_cell": twig_wall, "neutrophil": worker_ant,
    "monocyte": acid_ant, "basophil": honeybee, "nk_cell": bullet_ant, "net_trap": sap_blob, "keratin_plate": acorn_shell,
    "b_cell": spitting_spider, "antibody_tagger": firefly, "cytotoxic_t": assassin_bug, "opsonin_lance": jumping_spider,
    "interferon_beacon": glowworm_lantern, "mucus_wall": spiderweb, "mast_cell": stink_bug, "histamine_spitter": spittlebug,
    "fever_node": magnifying_glass, "cytokine_storm": click_beetle, "inflammation_zone": sprinkler,
    "toxic_membrane": nettle_patch, "killer_t": paper_wasp, "complement_sprayer": blister_beetle,
    "lysozyme_pool": toxic_mushroom, "perforin_lancer": scorpion, "necrosis_bloom": poison_ivy,
}


# --- Enemies ---------------------------------------------------------------------

def _enemy_bug(color, **kw):
    def design(c, p):
        bob = (0, -1, 0, 0)[phase(p)]
        c.dy += bob
        bug(c, dict(p, mood="angry"), hexc(color), **kw)
        c.dy -= bob
    return design


def aphid_cluster(c, p):
    for x, y in ((10, 22), (21, 22), (16, 16)):
        c.blob(x, y, 5, 4, hexc("#9fd44a"))
        c.eyes(x, y - 1, 1.6, "calm")


def scale_colony(c, p):
    for x, y in ((10, 22), (21, 22), (16, 16)):
        c.blob(x, y, 5.5, 4.5, hexc("#a0886a"))
        c.line([(x - 4, y), (x + 4, y)], hexc("#6a5a40"))
    c.eyes(16, 15, 1.6, "angry")


def giant_centipede(c, p):
    for i in range(6):
        wave = math.sin(phase(p) * math.pi / 2 + i * 1.1) * 1.5
        x, y = 3 + i * 5, 21 + wave
        legs(c, x, y, 2, 2, hexc("#5a1a10"), 3, p)
        c.blob(x, y, 3.8 if i < 5 else 5, 3.6 if i < 5 else 4.6, hexc("#b0402a") if i % 2 else hexc("#8a3020"))
    c.eyes(28, 19, 2, "angry")
    c.line([(29, 24), (31, 27)], hexc("#f0e0d0"))


ENEMIES = {
    "aphid": _enemy_bug("#9fd44a", rx=5, ry=4, legs_n=4, antennae=False),
    "termite": _enemy_bug("#e8d2a8", head=hexc("#b07a3a"), rx=5.5, ry=5),
    "soldier_termite": _enemy_bug("#d8b888", head=hexc("#7a3a1a"), horns=hexc("#5a2a10"), rx=6, ry=5.5),
    "aphid_cluster": aphid_cluster, "scale_colony": scale_colony,
    "mole_cricket": _enemy_bug("#8a5a32", head=hexc("#5a3a1a"), pincers=True, rx=6.5, ry=6),
    "rhino_beetle": _enemy_bug("#5a3a22", horns=hexc("#3a2414"), rx=8, ry=7),
    "hercules_beetle": _enemy_bug("#a0a050", head=hexc("#2a2a14"), horns=hexc("#2a2a14"), rx=8.5, ry=7.5),
    "mosquito": _enemy_bug("#6a6a72", wings=hexc("#d0d8e8", 200), rx=4, ry=5, stinger=OUTLINE),
    "hornet": _enemy_bug("#e8b830", head=hexc("#5a3a10"), wings=hexc("#d0d8e8", 200), stinger=OUTLINE, spots=hexc("#2a1a08")),
    "giant_centipede": giant_centipede,
}
