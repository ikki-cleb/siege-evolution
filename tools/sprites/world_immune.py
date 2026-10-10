"""World 1 (Microscopic): friendly cells and their germy invaders.

Each unit design draws one pose on a Canvas. `p` carries the pose:
  p["mood"]   eyes (calm, angry, squint, closed, wide)
  p["mouth"]  mouth shape
  p["pc"]     the pack color (an accent on every unit)
  p["act"]    "idle", "wind" (about to attack) or "fire"
Each returns the point at the top of its head, for evolution decorations.
Enemy designs get p["phase"] 0-3 for their walk cycle.
"""
import math

from .kit import hexc, shade


def _face(c, x, y, p, gap=3, size=2):
    c.eyes(x, y, gap, p["mood"], size)
    c.mouth(x, y + 3, p["mouth"])


# --- Fortress -----------------------------------------------------------------

def scab(c, p):  # crusty dark-red wall
    c.block(4, 9, 28, 30, hexc("#8a2c2c"))
    for x0, y0 in ((7, 12), (17, 11), (11, 19), (21, 20), (6, 24)):
        c.ellipse(x0 + 2, y0 + 2, 2.6, 2.0, hexc("#a8463c"))
    c.line([(9, 17), (13, 15), (16, 18)], hexc("#5a1818"))
    c.line([(18, 24), (22, 26), (25, 24)], hexc("#5a1818"))
    c.rect(4, 9, 27, 10, p["pc"])
    return (16, 9)


def germ_eater(c, p):  # big hungry amoeba
    body = hexc("#f2d38a")
    for lx, ly in ((7, 24), (25, 23), (9, 14), (24, 13)):
        c.ellipse(lx, ly, 3.5, 3.2, shade(body, -0.06))
    c.blob(16, 19, 10.5, 10, body)
    c.ellipse(21, 23, 2.5, 2.2, p["pc"])
    c.eyes(14, 15, 3, p["mood"], 3)
    c.mouth(14, 21, "open" if p["act"] != "idle" else "smile", 5)
    return (16, 9)


def scout_cell(c, p):  # star-shaped cell with branching arms
    body = hexc("#c9b4f0")
    for a in range(5):
        ang = -math.pi / 2 + a * math.tau / 5
        tip = (16 + math.cos(ang) * 12, 19 + math.sin(ang) * 10)
        c.line([(16, 19), tip], shade(body, -0.1), 3)
        c.ellipse(tip[0], tip[1], 1.8, 1.8, p["pc"])
    c.blob(16, 19, 7, 7, body)
    _face(c, 16, 17, p)
    return (16, 9)


def scar_tissue(c, p):  # pink fibrous wall with stitches
    c.block(4, 9, 28, 30, hexc("#e48aa0"))
    for y in (13, 18, 23):
        c.line([(6, y), (26, y + 1)], hexc("#c86a82"))
    c.line([(16, 11), (16, 27)], hexc("#7a2a3c"))
    for y in (12, 16, 20, 24):
        c.line([(14, y), (18, y + 1)], hexc("#7a2a3c"))
    c.ellipse(9, 26, 1.6, 1.4, p["pc"])
    return (16, 9)


def blaster_cell(c, p):  # round cell full of orange granules, cannon snout
    body = hexc("#f07a8a")
    c.rect(13, 4 if p["act"] == "fire" else 6, 19, 12, shade(p["pc"], -0.1))
    c.blob(16, 20, 10, 9.5, body)
    for gx, gy in ((9, 20), (12, 25), (20, 25), (23, 20), (16, 27)):
        c.ellipse(gx, gy, 1.4, 1.4, hexc("#ffb040"))
    _face(c, 16, 18, p)
    return (16, 6)


def hard_lump(c, p):  # big knobbly lump that zaps neighbors
    body = hexc("#9a8a78")
    for kx, ky in ((7, 14), (25, 14), (10, 9), (22, 9), (5, 22), (27, 22)):
        c.ellipse(kx, ky, 3.4, 3.2, shade(body, -0.05))
    c.blob(16, 19, 12, 11, body)
    c.ellipse(16, 20, 4, 3.4, p["pc"] if p["act"] != "idle" else shade(p["pc"], -0.25))
    return (16, 8)


# --- Swarm --------------------------------------------------------------------

def skin_cell(c, p):  # hexagonal skin tile
    body = hexc("#f0c8a0")
    pts = [(16 + math.cos(a) * 12, 19 + math.sin(a) * 10.5) for a in [i * math.tau / 6 for i in range(6)]]
    c.poly(pts, shade(body, -0.14))
    c.poly([(x - 0.8, y - 1) for x, y in pts], body)
    c.ellipse(16, 19, 3.5, 3.2, p["pc"])
    c.px(15, 18, shade(p["pc"], 0.3))
    return (16, 9)


def white_blood_cell(c, p):  # round white cell, three-lobed nucleus
    body = hexc("#f4f0f6")
    c.blob(16, 20, 9.5, 9.5, body)
    for nx, ny in ((12, 23), (16, 25), (20, 23)):
        c.ellipse(nx, ny, 2.2, 2.0, p["pc"])
    _face(c, 16, 17, p)
    return (16, 10)


def spike_shooter(c, p):  # pale cell with a launching spike on its head
    body = hexc("#a8d8f0")
    if p["act"] != "fire":
        c.poly([(14, 11), (18, 11), (16, 4)], p["pc"])
    c.blob(16, 20, 9, 9, body)
    _face(c, 16, 18, p)
    return (16, 6)


def itch_cell(c, p):  # purple cell peppered with dark granules
    body = hexc("#9a70c8")
    c.blob(16, 20, 10, 9.5, body)
    for gx, gy in ((9, 16), (23, 16), (8, 23), (24, 23), (12, 27), (20, 27), (16, 12)):
        c.ellipse(gx, gy, 1.3, 1.3, hexc("#3a2058"))
    _face(c, 16, 19, p)
    c.ellipse(16, 13, 1.5, 1.5, p["pc"])
    return (16, 10)


def killer_cell(c, p):  # dark cell with claws
    body = hexc("#58688a")
    for side in (-1, 1):
        c.poly([(16 + side * 9, 20), (16 + side * 13, 15), (16 + side * 11, 22)], p["pc"])
    c.blob(16, 20, 9, 9, body)
    c.eyes(16, 18, 3, "angry" if p["mood"] == "calm" else p["mood"])
    c.mouth(16, 22, "fangs")
    return (16, 11)


def sticky_net(c, p):  # web of sticky strands
    strand = hexc("#e8d070")
    for y in (10, 16, 22, 28):
        c.line([(4, y), (28, y - 1)], strand)
    for x in (6, 12, 18, 24):
        c.line([(x, 8), (x + 2, 30)], strand)
    for dx, dy in ((7, 12), (19, 19), (13, 25), (24, 11)):
        c.ellipse(dx, dy, 1.5, 1.8, p["pc"])
    return (16, 8)


# --- Precision ----------------------------------------------------------------

def nail_plate(c, p):  # glossy nail-like plate
    body = hexc("#f2e0c8")
    c.block(5, 9, 27, 30, body)
    c.rect(7, 11, 10, 27, shade(body, 0.14))
    c.rect(5, 26, 26, 28, p["pc"])
    return (16, 9)


def antibody_shooter(c, p):  # blue cell wearing Y-shaped antibodies
    body = hexc("#7ab0f0")
    for ax in (10, 16, 22):
        top = 6 if (p["act"] == "fire" and ax == 16) else 8
        c.line([(ax, 13), (ax, top + 3)], p["pc"], 1)
        c.line([(ax, top + 3), (ax - 2, top)], p["pc"], 1)
        c.line([(ax, top + 3), (ax + 2, top)], p["pc"], 1)
    c.blob(16, 21, 9, 8.5, body)
    _face(c, 16, 19, p)
    return (16, 8)


def germ_tagger(c, p):  # cell waving a little flag
    body = hexc("#90e0c0")
    c.line([(24, 22), (25, 7)], hexc("#6a4a30"), 1)
    wave = 1 if p["act"] == "fire" else 0
    c.poly([(25, 7), (30, 9 + wave), (25, 11)], p["pc"])
    c.blob(15, 21, 9, 8.5, body)
    _face(c, 15, 19, p)
    return (15, 12)


def germ_stabber(c, p):  # teal cell with a lance
    body = hexc("#5ac0b0")
    reach = 3 if p["act"] == "fire" else 7
    c.poly([(22, 20), (24, 20), (23, reach)], hexc("#e8e8f0"))
    c.blob(15, 21, 9, 8.5, body)
    c.eyes(15, 19, 3, "angry" if p["act"] != "idle" else p["mood"])
    c.mouth(15, 23, p["mouth"])
    c.rect(21, 19, 26, 21, p["pc"])
    return (15, 12)


def antibody_sniper(c, p):  # one big eye and a long barrel
    body = hexc("#88a0e8")
    c.rect(14, 2 if p["act"] == "fire" else 4, 18, 13, shade(p["pc"], -0.15))
    c.blob(16, 21, 9, 8.5, body)
    c.ellipse(16, 19, 3.5, 3.5, (250, 250, 250, 255))
    c.ellipse(16, 19, 1.6, 1.6, (24, 14, 22, 255) if p["mood"] != "closed" else (250, 250, 250, 255))
    return (16, 4)


def alarm_signal(c, p):  # bell-shaped beacon cell
    body = hexc("#f0e070")
    c.poly([(9, 27), (11, 13), (16, 10), (21, 13), (23, 27)], shade(body, -0.14))
    c.poly([(10, 26), (12, 13), (16, 11), (20, 13), (22, 26)], body)
    c.rect(8, 26, 24, 29, p["pc"])
    c.ellipse(16, 8, 2, 2, p["pc"])
    _face(c, 16, 19, p)
    return (16, 7)


# --- Control ------------------------------------------------------------------

def mucus_wall(c, p):  # translucent green goo with bubbles and drips
    goo = hexc("#88c860", 230)
    c.ellipse(16, 21, 13, 10, shade(goo, -0.15))
    c.ellipse(15, 20, 12, 9, goo)
    for bx, by in ((10, 18), (20, 22), (15, 15)):
        c.ellipse(bx, by, 1.6, 1.6, shade(goo, 0.2))
    c.rect(7, 27, 9, 31, goo)
    c.rect(22, 27, 24, 30, goo)
    c.ellipse(21, 16, 1.5, 1.5, p["pc"])
    return (16, 11)


def allergy_cell(c, p):  # puffy pink cell
    body = hexc("#f4a0c0")
    for px_, py_ in ((8, 15), (24, 15), (16, 11), (9, 25), (23, 25)):
        c.ellipse(px_, py_, 4, 3.6, shade(body, -0.05))
    c.blob(16, 20, 10, 9.5, body)
    _face(c, 16, 19, p)
    c.ellipse(16, 13, 1.5, 1.5, p["pc"])
    return (16, 8)


def sneeze_blaster(c, p):  # a big nose that blasts goo
    body = hexc("#f0b090")
    c.blob(16, 21, 10, 9, body)
    c.ellipse(16, 12 if p["act"] != "fire" else 11, 5, 5, shade(body, -0.05))
    c.ellipse(14, 13, 1.2, 1.4, hexc("#6a2a2a"))
    c.ellipse(18, 13, 1.2, 1.4, hexc("#6a2a2a"))
    c.eyes(16, 21, 4, p["mood"])
    c.rect(10, 26, 22, 27, p["pc"])
    return (16, 7)


def fever_spot(c, p):  # hot glowing blob with a flame tuft
    body = hexc("#f06a40")
    flick = 1 if p["act"] == "fire" else 0
    c.poly([(12, 13), (16, 3 - flick), (20, 13)], hexc("#ffd23c"))
    c.blob(16, 20, 10, 9.5, body)
    c.ellipse(16, 22, 5, 4, hexc("#ffa040"))
    _face(c, 16, 18, p)
    c.ellipse(9, 26, 1.4, 1.4, p["pc"])
    return (16, 5)


def stun_cell(c, p):  # yellow cell with lightning antennae
    body = hexc("#f0e050")
    for side in (-1, 1):
        x = 16 + side * 5
        c.line([(x, 13), (x + side * 2, 9), (x - side, 8), (x + side * 2, 3)], p["pc"], 1)
    c.blob(16, 21, 9, 8.5, body)
    _face(c, 16, 19, p)
    return (16, 4)


def swelling(c, p):  # throbbing red bump
    body = hexc("#e05050")
    puff = 1.08 if p["act"] == "fire" else 1.0
    c.blob(16, 21, 12 * puff, 9 * puff, body)
    for a in (-0.6, 0, 0.6):
        c.line([(16 + math.sin(a) * 9, 11 - math.cos(a) * 2), (16 + math.sin(a) * 11, 9 - math.cos(a) * 3)], p["pc"])
    _face(c, 16, 20, p)
    return (16, 10)


# --- Toxin --------------------------------------------------------------------

def toxic_skin(c, p):  # purple-green skin patch with pores and drips
    c.block(4, 10, 28, 30, hexc("#7a8a50"))
    for px_, py_ in ((8, 14), (15, 13), (22, 15), (11, 21), (19, 22), (25, 25)):
        c.ellipse(px_, py_, 1.5, 1.3, hexc("#4a3a5a"))
    c.rect(9, 29, 11, 31, p["pc"])
    c.rect(20, 29, 22, 32, p["pc"])
    return (16, 10)


def poison_cell(c, p):  # green cell with dripping fangs
    body = hexc("#80d070")
    c.blob(16, 20, 9.5, 9, body)
    c.eyes(16, 17, 3, "angry" if p["act"] != "idle" else p["mood"])
    c.mouth(16, 22, "fangs", 5)
    c.rect(19, 24, 20, 26, p["pc"])
    return (16, 11)


def poison_sprayer(c, p):  # cell with a squeeze bulb and nozzle
    body = hexc("#b0e080")
    c.rect(14, 6, 18, 12, hexc("#c0c0c8"))
    c.ellipse(16, 5, 2.4, 1.6 if p["act"] != "wind" else 1.0, p["pc"])
    c.blob(16, 21, 9, 8.5, body)
    _face(c, 16, 19, p)
    return (16, 4)


def acid_puddle(c, p):  # wide bubbling puddle
    acid = hexc("#a0e040")
    c.ellipse(16, 25, 14, 6, shade(acid, -0.18))
    c.ellipse(15, 24, 13, 5, acid)
    pop = 2 if p["act"] == "fire" else 0
    for bx, by, r in ((10, 22, 2), (19, 21 - pop, 2.4), (24, 24, 1.5)):
        c.ellipse(bx, by, r, r, shade(acid, 0.2))
    c.eyes(15, 25, 3, p["mood"])
    c.ellipse(6, 25, 1.4, 1.2, p["pc"])
    return (16, 18)


def plague_cell(c, p):  # spiky purple cell with needle spines
    body = hexc("#8a5ab0")
    c.spikes(16, 20, 8, 8, p["pc"], 3.5 if p["act"] != "fire" else 4.5, start=0.2)
    c.blob(16, 20, 8.5, 8.5, body)
    _face(c, 16, 19, p)
    return (16, 8)


def rot_patch(c, p):  # moldy patch with little mushrooms
    c.block(4, 14, 28, 30, hexc("#6a5038"))
    for mx, my in ((9, 13), (21, 12), (15, 18)):
        c.rect(mx - 0.5, my, mx + 1.5, my + 4, hexc("#e8e0c8"))
        c.ellipse(mx + 0.5, my, 3, 2, p["pc"])
    for fx, fy in ((7, 24), (14, 26), (22, 23), (25, 27)):
        c.ellipse(fx, fy, 1.6, 1.2, hexc("#9aa060"))
    return (16, 10)


# unit id: (design, style). Styles: wall, melee, ranged, pulse, support.
UNITS = {
    "platelet_clot": (scab, "wall"), "macrophage": (germ_eater, "melee"), "dendritic_cell": (scout_cell, "ranged"),
    "fibroblast": (scar_tissue, "wall"), "eosinophil": (blaster_cell, "ranged"), "granuloma": (hard_lump, "pulse"),
    "epithelial_cell": (skin_cell, "wall"), "neutrophil": (white_blood_cell, "melee"), "monocyte": (spike_shooter, "ranged"),
    "basophil": (itch_cell, "pulse"), "nk_cell": (killer_cell, "melee"), "net_trap": (sticky_net, "pulse"),
    "keratin_plate": (nail_plate, "wall"), "b_cell": (antibody_shooter, "ranged"), "antibody_tagger": (germ_tagger, "support"),
    "cytotoxic_t": (germ_stabber, "melee"), "opsonin_lance": (antibody_sniper, "ranged"), "interferon_beacon": (alarm_signal, "pulse"),
    "mucus_wall": (mucus_wall, "pulse"), "mast_cell": (allergy_cell, "pulse"), "histamine_spitter": (sneeze_blaster, "ranged"),
    "fever_node": (fever_spot, "pulse"), "cytokine_storm": (stun_cell, "ranged"), "inflammation_zone": (swelling, "pulse"),
    "toxic_membrane": (toxic_skin, "wall"), "killer_t": (poison_cell, "ranged"), "complement_sprayer": (poison_sprayer, "ranged"),
    "lysozyme_pool": (acid_puddle, "pulse"), "perforin_lancer": (plague_cell, "ranged"), "necrosis_bloom": (rot_patch, "pulse"),
}


# --- Enemies (p["phase"] 0-3 = walk cycle) -------------------------------------

def _virus(c, p, body, spike, size=7.0, angry=False):
    bob = (0, -1, 0, 1)[p["phase"]]
    c.dy += bob
    c.spikes(16, 19, size, 8, spike, 2.6, start=p["phase"] * 0.2)
    c.blob(16, 19, size, size, body)
    c.eyes(16, 18, 2.5, "angry" if angry else "calm")
    c.dy -= bob


def _rod(c, p, body, armor=None):
    wiggle = (0, 1, 0, -1)[p["phase"]]
    c.line([(6, 22), (3, 24 + wiggle), (1, 21 - wiggle)], shade(body, -0.25))
    c.blob(16, 21, 10, 5.5, body)
    if armor:
        for x in (11, 16, 21):
            c.rect(x - 1.5, 16, x + 1.5, 18, armor)
    c.eyes(20, 20, 2, "angry")


def bacterium_half(c, p):
    bob = (0, -1, 0, 0)[p["phase"]]
    c.dy += bob
    c.blob(16, 24, 6, 4.5, hexc("#c6d84a"))
    c.eyes(16, 23, 2, "calm")
    c.dy -= bob


def rhinovirus(c, p):
    _virus(c, p, hexc("#7bd24a"), hexc("#b6f58a"))


def flu_virus(c, p):
    _virus(c, p, hexc("#4ad2b0"), hexc("#ff8a8a"), 7.5, True)
    c.line([(2, 16), (6, 16)], hexc("#c8fff0"))
    c.line([(1, 20), (5, 20)], hexc("#c8fff0"))


def bacterium(c, p):
    _rod(c, p, hexc("#c6d84a"))


def biofilm(c, p):
    _rod(c, p, hexc("#9aa83a"), hexc("#5d6b9a"))


def _worm(c, p, body, alt, hooks=False):
    for i in range(5):
        wave = math.sin(p["phase"] * math.pi / 2 + i * 1.2) * 1.5
        x, y = 6 + i * 5, 22 + wave
        c.ellipse(x, y, 3.6 if i < 4 else 4.4, 3.4 if i < 4 else 4, body if i % 2 else alt)
    c.eyes(27, 20, 1.6, "angry")
    c.mouth(28, 23, "fangs", 3)
    if hooks:
        c.line([(31, 19), (30, 17)], hexc("#f0e0d0"))
        c.line([(31, 26), (30, 28)], hexc("#f0e0d0"))


def worm(c, p):
    _worm(c, p, hexc("#c28a5a"), hexc("#a8703f"))


def hookworm(c, p):
    _worm(c, p, hexc("#b0605a"), hexc("#8a3f3a"), True)


def _spore(c, p, body, edge, ring=False):
    float_ = (0, -1, -2, -1)[p["phase"]]
    c.dy += float_
    for i in range(6):
        a = i * math.tau / 6 + p["phase"] * 0.3
        c.px(16 + math.cos(a) * 10, 16 + math.sin(a) * 9, shade(body, 0.1))
    c.blob(16, 17, 6.5, 6.5, body)
    if ring:
        c.ellipse(16, 17, 9, 2, (0, 0, 0, 0))
        c.line([(7, 17), (25, 17)], edge)
    c.eyes(16, 17, 2.5, "calm")
    c.dy -= float_


def spore(c, p):
    _spore(c, p, hexc("#f0e6ff"), hexc("#a78bd6"))


def fungal_spore(c, p):
    _spore(c, p, hexc("#ffd9a8"), hexc("#b0703a"), True)


def superbug(c, p):
    bob = (0, -1, 0, -1)[p["phase"]]
    c.dy += bob
    c.spikes(16, 18, 11, 10, hexc("#e04aff"), 3.5, start=p["phase"] * 0.15)
    c.blob(16, 18, 11.5, 11.5, hexc("#5b2a86"))
    c.eyes(16, 15, 4, "angry", 3)
    c.mouth(16, 21, "fangs", 7)
    c.poly([(10, 7), (12, 3), (14, 6), (16, 2), (18, 6), (20, 3), (22, 7)], hexc("#ffd23c"))
    c.dy -= bob


ENEMIES = {
    "bacterium_half": bacterium_half, "rhinovirus": rhinovirus, "flu_virus": flu_virus, "bacterium": bacterium,
    "biofilm": biofilm, "worm": worm, "hookworm": hookworm, "spore": spore, "fungal_spore": fungal_spore,
    "superbug": superbug,
}
