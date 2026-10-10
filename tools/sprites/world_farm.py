"""World 3 (Wild Kingdom): farm animals defend the farmhouse. Animals have
faces; walls and objects don't."""
import math

from .kit import OUTLINE, hexc, shade
from .parts import WHITE, animal, bird, legs, phase


def stone_wall(c, p):
    for row, y in enumerate((14, 20, 26)):
        for i in range(4):
            x = 6 + i * 7 + (row % 2) * 3
            c.block(x - 3, y - 3, x + 3, y + 3, hexc("#9a9488"))
    c.ellipse(16, 27, 1.4, 1.4, p["pc"])
    return (16, 10)


def bull(c, p):
    top = animal(c, p, hexc("#5a3a2a"), ears="round", snout=hexc("#d8a888"), horns=hexc("#f0e8d0"))
    c.ellipse(16, 22, 1.4, 1.4, p["pc"])
    return top


def llama(c, p):
    spit = p["act"] == "fire"
    top = animal(c, p, hexc("#f0e8d8"), ears="long", snout=hexc("#e0c8b0"), size=0.95)
    c.rect(11, 24, 21, 26, p["pc"])
    return top


def hedge(c, p):
    for x, y in ((8, 20), (16, 16), (24, 20), (10, 26), (22, 26), (16, 23)):
        c.blob(x, y, 5.5, 5, hexc("#3a7a30"))
    for x, y in ((9, 18), (20, 15), (14, 24)):
        c.ellipse(x, y, 1.2, 1.2, hexc("#e04050"))
    c.ellipse(24, 25, 1.4, 1.4, p["pc"])
    return (16, 11)


def draft_horse(c, p):
    top = animal(c, p, hexc("#8a5a3a"), ears="point", snout=hexc("#b08060"), mane=hexc("#3a2a1a"))
    c.rect(12, 26, 20, 27, p["pc"])
    return top


def stone_silo(c, p):
    c.block(9, 9, 23, 30, hexc("#a8a098"))
    c.ellipse(16, 9, 7, 4, hexc("#8a4030"))
    for y in (15, 21, 26):
        c.line([(9, y), (22, y)], hexc("#8a847c"))
    c.rect(14, 24, 18, 30, hexc("#5a3a2a") if p["act"] == "idle" else p["pc"])
    return (16, 5)


def hay_bale(c, p):
    c.block(4, 12, 28, 29, hexc("#e0c060"))
    for x in (9, 23):
        c.rect(x, 12, x + 2, 28, hexc("#a87830"))
    for y in (16, 21, 25):
        c.line([(5, y), (27, y + 1)], hexc("#c8a848"))
    c.ellipse(16, 20, 1.4, 1.4, p["pc"])
    return (16, 12)


def hen(c, p):
    top = bird(c, p, hexc("#f4f0e8"), hexc("#f0a030"), tuft=hexc("#e03030"))
    c.ellipse(16, 24, 1.4, 1.4, p["pc"])
    return top


def barn_swallow(c, p):
    top = bird(c, p, hexc("#304a8a"), hexc("#3a2a20"), size=0.9)
    c.ellipse(16, 22, 3, 2.4, hexc("#e0905a"))
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return top


def bee_skep(c, p):
    for i, y in enumerate((12, 16, 20, 24)):
        w = 6 + i * 2.5
        c.ellipse(16, y, w, 2.6, hexc("#d8a848"))
        c.line([(16 - w + 1, y + 1), (16 + w - 1, y + 1)], hexc("#a87830"))
    c.ellipse(16, 25, 2.5, 2, hexc("#3a2a1a"))
    for bx, by in ((9, 9), (24, 11)):
        c.ellipse(bx, by - (p["act"] != "idle"), 1.5, 1.2, hexc("#f0c040"))
    c.ellipse(22, 18, 1.4, 1.4, p["pc"])
    return (16, 9)


def barn_cat(c, p):
    top = animal(c, p, hexc("#e09040"), ears="point", snout=hexc("#f8e0c0"))
    for side in (-1, 1):
        c.line([(16 + side * 3, 20), (16 + side * 8, 19)], OUTLINE)
    c.ellipse(16, 26, 1.4, 1.4, p["pc"])
    return top


def muddy_pen(c, p):
    c.ellipse(16, 23, 13, 7, hexc("#6a4a2a"))
    c.ellipse(15, 22, 11, 5.5, hexc("#8a6038"))
    for x in (5, 27):
        c.rect(x - 1, 13, x + 1, 28, hexc("#a07040"))
    c.line([(4, 15), (28, 15)], hexc("#a07040"), 2)
    c.ellipse(19, 23, 1.5, 1.5, p["pc"])
    return (16, 13)


def wooden_fence(c, p):
    for x in (6, 13, 20, 27):
        c.block(x - 2.5, 10, x + 2.5, 30, hexc("#b08050"))
        c.poly([(x - 2.5, 10), (x, 7), (x + 2.5, 10)], hexc("#b08050"))
    for y in (15, 24):
        c.rect(3, y, 29, y + 2, hexc("#8a6038"))
    c.ellipse(16, 20, 1.4, 1.4, p["pc"])
    return (16, 7)


def barn_owl(c, p):
    top = bird(c, p, hexc("#e8d0a8"), hexc("#c09060"), size=1.05)
    c.ellipse(16, 17, 5.5, 4.5, hexc("#f8f0e0"))
    c.eyes(16, 17, 3, p["mood"])
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return top


def watchdog(c, p):
    top = animal(c, p, hexc("#c89060"), ears="long", snout=hexc("#e8c8a0"))
    c.rect(11, 25, 21, 26, p["pc"])
    return top


def ferret(c, p):
    top = animal(c, p, hexc("#e8dcc8"), ears="round", snout=hexc("#f8f0e8"), size=0.9)
    c.rect(11, 17, 21, 19, hexc("#5a4a3a"))
    c.eyes(16, 17.5, 2.7, p["mood"])
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return top


def falcon(c, p):
    top = bird(c, p, hexc("#6a7080"), hexc("#f0c040"))
    c.ellipse(16, 22, 3.5, 3, hexc("#e8e0d0"))
    c.eyes(16, 16, 3, "angry" if p["mood"] == "calm" else p["mood"])
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return top


def scarecrow(c, p):
    c.rect(15, 14, 17, 30, hexc("#8a6038"))
    c.rect(5, 16, 27, 18, hexc("#8a6038"))
    c.block(10, 16, 22, 26, p["pc"])
    c.ellipse(16, 11, 5, 5, hexc("#e8c070"))
    c.poly([(8, 8), (24, 8), (16, 2)], hexc("#7a5a30"))
    c.rect(7, 7, 25, 9, hexc("#7a5a30"))
    for x in (5, 27):
        c.line([(x, 17), (x + (2 if x < 16 else -2), 20)], hexc("#e8d070"))
    return (16, 2)


def mud_wall(c, p):
    c.block(4, 12, 28, 30, hexc("#7a5434"))
    for x, y in ((9, 16), (20, 15), (14, 22), (24, 24)):
        c.ellipse(x, y, 3, 2, hexc("#9a6a40"))
    c.rect(8, 29, 10, 32, hexc("#7a5434"))
    c.ellipse(16, 26, 1.4, 1.4, p["pc"])
    return (16, 12)


def skunk(c, p):
    c.ellipse(24, 15, 4, 6, hexc("#2a2a30"))
    c.line([(24, 10), (24, 19)], WHITE, 2)
    top = animal(c, p, hexc("#2a2a30"), ears="round", snout=hexc("#3a3a40"))
    c.line([(16, 11), (16, 16)], WHITE, 2)
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return top


def honking_goose(c, p):
    honk = p["act"] == "fire"
    top = bird(c, p, hexc("#f8f8f8"), hexc("#f08030"))
    if honk:
        c.ellipse(16, 21, 3, 2, hexc("#f08030"))
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return top


def bonfire(c, p):
    for a in (-0.5, 0.5):
        c.line([(16 + math.sin(a) * 10, 29), (16 - math.sin(a) * 10, 23)], hexc("#6a4020"), 3)
    big = 1.2 if p["act"] == "fire" else 1.0
    c.poly([(9, 25), (16, 25 - 16 * big), (23, 25)], hexc("#f06a30"))
    c.poly([(12, 25), (16, 25 - 10 * big), (20, 25)], hexc("#ffd23c"))
    c.ellipse(16, 27, 1.4, 1.2, p["pc"])
    return (16, 8)


def mule(c, p):
    top = animal(c, p, hexc("#9a8070"), ears="long", snout=hexc("#c8b0a0"))
    if p["act"] == "fire":
        c.line([(6, 28), (2, 26)], hexc("#ffe060"))
        c.line([(26, 28), (30, 26)], hexc("#ffe060"))
    c.ellipse(16, 26, 1.4, 1.4, p["pc"])
    return top


def smoke_pot(c, p):
    c.blob(16, 24, 8, 6, hexc("#5a5a60"))
    c.rect(9, 18, 23, 20, hexc("#3a3a40"))
    puff = 2 if p["act"] == "fire" else 0
    for x, y, r in ((13, 13, 3), (18, 10, 3.5), (15, 6 - puff, 2.5)):
        c.ellipse(x, y - puff, r, r, hexc("#c8c8d0", 220))
    c.ellipse(16, 25, 1.4, 1.4, p["pc"])
    return (16, 6)


def bramble_fence(c, p):
    for x in (6, 26):
        c.rect(x - 1, 12, x + 1, 30, hexc("#7a5030"))
    for y in (15, 21, 27):
        c.line([(4, y), (28, y - 1)], hexc("#5a3a20"), 2)
        for x in range(7, 27, 4):
            c.px(x, y - 1, hexc("#e8e0d0"))
    c.ellipse(16, 18, 1.6, 1.6, hexc("#8a2a4a"))
    c.ellipse(20, 24, 1.4, 1.4, p["pc"])
    return (16, 12)


def rattlesnake(c, p):
    for i in range(4):
        x = 8 + i * 4
        c.ellipse(x, 25 - (i % 2), 3.5, 3, hexc("#c0a060") if i % 2 else hexc("#8a7040"))
    c.ellipse(6, 23, 1.5, 2.5, hexc("#e8d0a0"))
    c.blob(23, 18, 5.5, 4.5, hexc("#c0a060"))
    c.eyes(23, 17, 2, "angry" if p["act"] != "idle" else p["mood"])
    c.mouth(23, 20, "fangs", 3)
    c.ellipse(13, 24, 1.3, 1.3, p["pc"])
    return (23, 13)


def toad(c, p):
    top = animal(c, p, hexc("#8a9a50"), ears=None, snout=None, size=1.05)
    for x, y in ((11, 22), (21, 22), (16, 25)):
        c.ellipse(x, y, 1.4, 1.2, hexc("#5a6a30"))
    c.mouth(16, 20, "smile", 6)
    c.ellipse(16, 13, 1.4, 1.4, p["pc"])
    return top


def manure_pile(c, p):
    for y, r in ((26, 10), (21, 7.5), (16, 5)):
        c.blob(16, y, r, 3.5, hexc("#6a4a2a"))
    for x, y in ((9, 10), (16, 7), (23, 10)):
        c.line([(x, y + 2), (x + 1, y)], hexc("#a0b070"))
    c.ellipse(20, 26, 1.4, 1.4, p["pc"])
    return (16, 9)


def gila_monster(c, p):
    c.ellipse(16, 23, 9, 5.5, hexc("#e08040"))
    for x, y in ((11, 22), (16, 24), (21, 22), (14, 20), (19, 26)):
        c.ellipse(x, y, 1.6, 1.2, hexc("#2a2020"))
    legs(c, 16, 23, 7, 4, hexc("#2a2020"), 3, p)
    c.blob(16, 15, 5, 4, hexc("#2a2020"))
    c.eyes(16, 15, 2, p["mood"])
    c.ellipse(16, 23, 1.4, 1.4, p["pc"])
    return (16, 11)


def hemlock_patch(c, p):
    for x in (8, 16, 24):
        c.line([(x, 29), (x, 15)], hexc("#5a8a3a"))
        for a in range(5):
            ang = -math.pi / 2 + (a - 2) * 0.5
            c.px(x + math.cos(ang) * 4, 14 + math.sin(ang) * 3, WHITE)
        c.ellipse(x, 13, 3.5, 2, hexc("#e8e8e0"))
    c.rect(4, 27, 28, 30, hexc("#4a6a2a"))
    c.ellipse(16, 22, 1.4, 1.4, p["pc"])
    return (16, 10)


DESIGNS = {
    "platelet_clot": stone_wall, "macrophage": bull, "dendritic_cell": llama, "fibroblast": hedge, "eosinophil": draft_horse,
    "granuloma": stone_silo, "epithelial_cell": hay_bale, "neutrophil": hen, "monocyte": barn_swallow, "basophil": bee_skep,
    "nk_cell": barn_cat, "net_trap": muddy_pen, "keratin_plate": wooden_fence, "b_cell": barn_owl, "antibody_tagger": watchdog,
    "cytotoxic_t": ferret, "opsonin_lance": falcon, "interferon_beacon": scarecrow, "mucus_wall": mud_wall, "mast_cell": skunk,
    "histamine_spitter": honking_goose, "fever_node": bonfire, "cytokine_storm": mule, "inflammation_zone": smoke_pot,
    "toxic_membrane": bramble_fence, "killer_t": rattlesnake, "complement_sprayer": toad, "lysozyme_pool": manure_pile,
    "perforin_lancer": gila_monster, "necrosis_bloom": hemlock_patch,
}


# --- Enemies ---------------------------------------------------------------------

def _beast(fur, size=1.0, ears="point", snout=None, horns=None, count=1):
    def design(c, p):
        bob = (0, -1, 0, -1)[phase(p)]
        c.dy += bob
        spots = ((16, 0),) if count == 1 else ((10, 3), (22, 3), (16, -3))
        for x, dy in spots:
            animal(c, dict(p, mood="angry"), hexc(fur), x=x, y=19 + dy, ears=ears, snout=snout and hexc(snout),
                   horns=horns and hexc(horns), size=size if count == 1 else size * 0.6)
        legs(c, 16, 28, 5, 2, OUTLINE, 2, p)
        c.dy -= bob
    return design


def _flier(feathers, beak, size=1.0):
    def design(c, p):
        bird(c, dict(p, mood="angry"), hexc(feathers), hexc(beak), size=size)
    return design


ENEMIES = {
    "coyote": _beast("#c8a070", 0.85, snout="#e8d0b0"), "wolf": _beast("#7a7a80", 0.9, snout="#a8a8b0"),
    "bear_cub": _beast("#7a5030", 0.75, "round", snout="#c09070"), "rat": _beast("#8a8088", 0.7, "round", snout="#e0b0b8"),
    "weasel": _beast("#a06a3a", 0.8, "round", snout="#f0e0c8"),
    "coyote_pack": _beast("#c8a070", 1.0, snout="#e8d0b0", count=3), "wolf_pack": _beast("#5a5a60", 1.0, snout="#8a8a90", count=3),
    "deer": _beast("#b07a48", 0.95, "long", snout="#e0c0a0"), "red_stag": _beast("#9a4a2a", 1.0, "long", snout="#e0b090", horns="#e8d8c0"),
    "gopher": _beast("#9a7048", 0.75, "round", snout="#e0c0a0"),
    "wild_boar": _beast("#6a4a3a", 1.0, "point", snout="#c09080", horns="#f0e8d8"),
    "moose": _beast("#5a3a28", 1.15, "long", snout="#9a7058", horns="#d8c8a8"),
    "crow": _flier("#2a2a38", "#3a3a40", 0.9), "hawk": _flier("#8a6040", "#f0c040"),
    "grizzly": _beast("#6a4428", 1.4, "round", snout="#c09878"),
}
