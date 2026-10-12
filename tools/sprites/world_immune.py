"""World 3 (Microscopic): friendly cells and their germy invaders.

Each unit design draws one pose on a Canvas. `p` carries the pose:
  p["mood"]   eyes (calm, angry, squint, closed, wide)
  p["mouth"]  mouth shape
  p["pc"]     the pack color (an accent on every unit)
  p["act"]    "idle", "wind" (about to attack) or "fire"
  p["branch"] None (base), 0 (power evolution) or 1 (utility evolution)
Enemy designs get p["phase"] 0-3 for their walk cycle.

Redesigned (see world_backyard.py): every cell has the silhouette of the
real cell it's based on, with cute faces and soft colors. Power evolutions
get an armored membrane, a glowing nucleus and receptor spikes; utility
evolutions reach further (pseudopods, flagella, long receptors).
"""
import math

from .hefty import antibody, cell_body, glow, pc_mark, pseudopods, ring, tier
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, phase

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True


def _face(c, x, y, p, gap=3, size=2):
    c.eyes(x, y, gap, p["mood"], size)
    c.mouth(x, y + 3, p["mouth"])


def receptors(c, x, y, rx, ry, color, count=8, length=3.5):
    """Receptor spikes around a cell (power evolutions)."""
    for k in range(count):
        a = k * math.tau / count + 0.2
        bx, by = x + math.cos(a) * rx, y + math.sin(a) * ry
        c.line([(bx, by), (bx + math.cos(a) * length, by + math.sin(a) * length)], color, 2)
        c.px(bx + math.cos(a) * (length + 0.5), by + math.sin(a) * (length + 0.5), shade(color, 0.3))


def flagella(c, p, x, y, color, count=2, length=10):
    """Wavy tails (utility evolutions that reach further)."""
    wave = (0, 1, 0, -1)[phase(p)]
    for k in range(count):
        side = -1 if k == 0 else 1
        pts = [(x + side * (4 + i * length / 5), y + math.sin(i * 1.3 + wave) * 2 + i * 0.6) for i in range(6)]
        c.line(pts, color)


def tissue_wall(c, top, color, rows=3):
    """A fleshy wall block of rounded tissue lumps."""
    c.block(3, top, 29, 30, shade(color, -0.2))
    h = (30 - top) / rows
    for r in range(rows):
        for k in range(4):
            x = 6.5 + k * 6.3 + (r % 2) * 2
            c.blob(min(26.5, x), top + h * (r + 0.5), 3.4, h / 2 - 0.2, shade(color, ((k + r) % 3 - 1) * 0.05))


# --- Fortress -----------------------------------------------------------------

def scab(c, p):
    b = tier(p)
    crust = hexc("#8a2a2a") if b != 0 else hexc("#6a1e22")
    top = 9 if b == 0 else 12
    tissue_wall(c, top, crust, 4 if b == 0 else 3)
    for x, y in ((8, 16), (19, 20), (25, 26), (12, 26)):
        c.ellipse(x, y + top - 12, 2, 1.2, shade(crust, 0.2))
    if b == 1:  # Spiky Scab: hard crystal spikes
        for x in (6, 12, 18, 24):
            c.poly([(x - 2, top + 1), (x + 2, top + 1), (x + 0.5, top - 6)], hexc("#d8a0a0"))
    pc_mark(c, 16, 27, p, 1.3)
    return (16, top - 2)


def germ_eater(c, p):
    b = tier(p)
    body = hexc("#e8c070")
    chomp = p.get("act") == "fire"
    pseudopods(c, 16, 19, shade(body, -0.05), reach=1.25 if b == 1 else 0.95, count=5 if b == 1 else 4, p=p)
    top = cell_body(c, p, body, rx=11 if b == 0 else 9.5, ry=9.5 if b == 0 else 8.5, nucleus=hexc("#b07a3a"),
                    granules=hexc("#c89a50"), armored=b == 0, face_y=16)
    if chomp or b == 0:  # Giant: germs it has swallowed, inside
        for x, y in ((12, 22), (20, 23)):
            c.ellipse(x, y, 1.8, 1.2, hexc("#9ad040"))
    if chomp:
        c.mouth(16, 20, "open", 3)
    pc_mark(c, 16, 25, p, 1.4)
    return top


def scout_cell(c, p):
    b = tier(p)
    body = hexc("#c890f0")
    arms = 5
    reach = 1.35 if b == 1 else 1.0
    for k in range(arms):  # branching dendrite arms
        a = -math.pi / 2 + k * math.tau / arms
        tip = (16 + math.cos(a) * 12 * reach, 19 + math.sin(a) * 11 * reach)
        c.line([(16, 19), tip], shade(body, -0.1), 3 if b == 0 else 2)
        for side in (-0.5, 0.5):
            c.line([tip, (tip[0] + math.cos(a + side) * 3, tip[1] + math.sin(a + side) * 3)], shade(body, -0.1))
    top = cell_body(c, p, body, rx=7.5, ry=7, nucleus=hexc("#8a5ab0"), armored=b == 0)
    pc_mark(c, 16, 23, p, 1.3)
    return top


def scar_tissue(c, p):
    b = tier(p)
    pink = hexc("#e8a0b0")
    top = 9 if b == 0 else 12
    c.block(3, top, 29, 30, pink)
    for y in range(top + 2, 30, 3):  # fibers
        c.line([(4, y), (28, y + (1 if y % 2 else -1))], shade(pink, -0.12))
    stitches = (8, 16, 24) if b != 0 else (6, 11, 16, 21, 26)
    for x in stitches:  # stitches
        c.line([(x, top + 3), (x, 27)], hexc("#5a3a4a"))
        for y in range(top + 4, 27, 4):
            c.line([(x - 1.5, y), (x + 1.5, y + 1)], hexc("#5a3a4a"))
    if b == 1:  # Quick-Heal: a plaster with a green cross
        c.block(10, top + 4, 22, top + 12, hexc("#f4e8d0"))
        c.rect(15, top + 5, 17, top + 11, hexc("#5ac060"))
        c.rect(13, top + 7, 19, top + 9, hexc("#5ac060"))
    pc_mark(c, 26, 27, p, 1.3)
    return (16, top - 2)


def blaster_cell(c, p):
    b = tier(p)
    body = hexc("#f0a080")
    barrel = 4 if b == 0 else 3
    length = 11 if b == 1 else 7
    recoil = 2 if p.get("act") == "fire" else 0
    c.rect(16 - barrel / 2 - 1, 11 - length + recoil, 16 + barrel / 2 + 1, 14, shade(body, -0.35))  # cannon snout
    c.rect(16 - barrel / 2, 11 - length + recoil, 16 + barrel / 2, 13, shade(body, -0.15))
    top = cell_body(c, p, body, rx=10.5 if b == 0 else 9.5, ry=9, nucleus=hexc("#c05a50"), lobes=2,
                    granules=hexc("#e86a30"), n_granules=9, armored=b == 0, face_y=18)
    pc_mark(c, 16, 25, p, 1.4)
    return (16, 11 - length)


def hard_lump(c, p):
    b = tier(p)
    lump = hexc("#b08a7a") if b != 0 else hexc("#8a8a92")
    for x, y, r in ((9, 23, 6), (23, 23, 6), (16, 16, 7.5), (16, 25, 6.5), (7, 15, 4), (25, 15, 4)):
        c.blob(x, y, r, r * 0.9, shade(lump, ((x + y) % 3 - 1) * 0.05))
    if b == 1:  # Spiky Lump: spikes
        for x, y, dx, dy in ((4, 12, -2, -3), (28, 12, 2, -3), (16, 7, 0, -4), (3, 24, -3, 0), (29, 24, 3, 0)):
            c.poly([(x - 1.5, y), (x + 1.5, y), (x + dx, y + dy)], hexc("#e8d8d0"))
    zap = p.get("act") != "idle"
    if zap:
        ring(c, 16, 20, 14, 12, hexc("#fff080"))
    c.eyes(16, 15, 3, p.get("mood", "calm"), 2)
    c.mouth(16, 18.5, "smile", 3)
    pc_mark(c, 16, 25, p, 1.4)
    return (16, 8)


# --- Swarm --------------------------------------------------------------------

def skin_cell(c, p):
    b = tier(p)
    skin = hexc("#f0c8a8")
    rows = ((9, 13), (16, 13), (23, 13), (12.5, 20), (19.5, 20), (9, 27), (16, 27), (23, 27))
    for x, y in rows:
        pts = [(x + math.cos(a * math.pi / 3) * 4.2, y + math.sin(a * math.pi / 3) * 3.8) for a in range(6)]
        c.poly(pts, shade(skin, ((int(x) + int(y)) % 3 - 1) * 0.05))
        c.ellipse(x + 0.5, y + 0.5, 1, 0.8, shade(skin, -0.25))  # little nucleus
    if b == 0:  # Tough: a thick outer layer
        c.rect(3, 29, 29, 31, shade(skin, -0.3))
        c.rect(3, 8, 29, 9.5, shade(skin, -0.3))
    if b == 1:  # Prickly: hairs
        for x in (6, 12, 18, 24):
            c.line([(x, 9), (x + 1, 4)], hexc("#a07a5a"))
    pc_mark(c, 16, 20, p, 1.3)
    return (16, 8)


def white_blood_cell(c, p):
    b = tier(p)
    body = hexc("#f4f0f8")
    if b == 1:  # Long-Reach: a long pseudopod arm
        pseudopods(c, 16, 19, shade(body, -0.05), reach=1.3, count=2, start=-0.3, p=p)
    if b == 0:
        receptors(c, 16, 19, 11, 10, hexc("#c8b8e8"))
    top = cell_body(c, p, body, rx=10.5 if b == 0 else 9.5, ry=9.5 if b == 0 else 8.5, nucleus=hexc("#9a7ac8"),
                    lobes=3, granules=hexc("#d8d0e8"), armored=b == 0, face_y=15.5)
    pc_mark(c, 16, 26, p, 1.4)
    return top


def spike_shooter(c, p):
    b = tier(p)
    body = hexc("#d8e0f0")
    fire = p.get("act") == "fire"
    spikes = 2 if b == 0 else 1
    long_ = b == 1
    for k in range(spikes):
        x = 16 + (k - (spikes - 1) / 2) * 6
        c.poly([(x - 2, 11), (x + 2, 11), (x, 11 - (12 if long_ else 8) - fire * 2)], hexc("#a0b8d8"))
        c.line([(x, 10), (x, 4 if long_ else 6)], WHITE)
    top = cell_body(c, p, body, rx=9.5, ry=8.5, nucleus=hexc("#7a8ab0"), armored=b == 0, face_y=18)
    pc_mark(c, 16, 25, p, 1.4)
    return (16, 3)


def itch_cell(c, p):
    b = tier(p)
    body = hexc("#b08ad8")
    if b == 1:  # Wide: an itchy ring
        ring(c, 16, 19, 14.5, 12, hexc("#e0c0ff"), 24)
    top = cell_body(c, p, body, rx=10.5 if b == 0 else 9.5, ry=9, granules=hexc("#4a2a6a"),
                    n_granules=12 if b == 0 else 8, armored=b == 0, nucleus=None)
    pc_mark(c, 16, 25, p, 1.4)
    return top


def killer_cell(c, p):
    b = tier(p)
    body = hexc("#4a4a6a")
    if b == 1:  # Hunter: a tail to chase germs
        flagella(c, p, 16, 27, shade(body, 0.2), count=2, length=9)
    claw = 1.4 if b == 0 else 1.0
    for side in (-1, 1):  # claws
        c.line([(16 + side * 8, 17), (16 + side * 12 * claw, 12), (16 + side * 11 * claw, 8)], hexc("#d8d8e8"), 2)
        c.line([(16 + side * 12 * claw, 12), (16 + side * 14 * claw, 9)], hexc("#d8d8e8"))
    top = cell_body(c, p, body, rx=9.5 if b != 0 else 10.5, ry=9, nucleus=hexc("#2a2a40"), granules=hexc("#8a8ab0"),
                    armored=b == 0)
    pc_mark(c, 16, 26, p, 1.4)
    return top


def sticky_net(c, p):
    b = tier(p)
    strand = hexc("#e8d090")
    spread = 14 if b == 1 else 12
    for k in range(9 if b == 0 else 7):
        a = k * math.pi / (8 if b == 0 else 6)
        c.line([(16 - math.cos(a) * spread, 19 - math.sin(a) * 10), (16 + math.cos(a) * spread, 19 + math.sin(a) * 10)], strand)
    for r in (4, 8, 12) if b != 0 else (3, 6, 9, 12):
        pts = [(16 + math.cos(a * math.pi / 6) * r * spread / 12, 19 + math.sin(a * math.pi / 6) * r * 0.85) for a in range(13)]
        c.line(pts, strand)
    for x, y in ((10, 15), (22, 22), (14, 25), (21, 13)):  # trapped germ bits
        c.ellipse(x, y, 1.6, 1.3, hexc("#9ad040"))
    pc_mark(c, 16, 19, p, 1.4)
    return (16, 7)


# --- Precision ----------------------------------------------------------------

def nail_plate(c, p):
    b = tier(p)
    nail = hexc("#f4e8e0")
    top = 9 if b == 0 else 12
    c.ellipse(16, top + 2, 13, 4, shade(nail, -0.1))
    c.block(3, top + 2, 29, 30, nail)
    c.rect(3, top + 2, 29, top + 5, hexc("#fff8f4"))  # the white tip
    for x in (8, 14, 20, 25):  # glossy streaks
        c.line([(x, top + 7), (x + 1, 27)], (255, 255, 255, 200))
    if b == 0:  # Thick: layered plates
        c.line([(3, top + 12), (29, top + 12)], shade(nail, -0.2))
    if b == 1:  # Spiked: ridges
        for x in (6, 12, 18, 24):
            c.poly([(x - 2, top + 2), (x + 2, top + 2), (x, top - 5)], hexc("#e0d0c8"))
    pc_mark(c, 16, 26, p, 1.3)
    return (16, top - 2)


def antibody_shooter(c, p):
    b = tier(p)
    body = hexc("#8ab8f0")
    for k in range(7 if b != 0 else 9):  # antibodies on the surface
        a = math.pi + k * math.pi / (6 if b != 0 else 8)
        antibody(c, 16 + math.cos(a) * 11, 19 + math.sin(a) * 10, hexc("#f0e070"), 0.8)
    if b == 0:  # Heavy: a big antibody cannon on top
        antibody(c, 16, 5, hexc("#f0e070"), 1.6)
    if b == 1:  # Long: a long launcher tube
        c.rect(14, 1, 18, 11, hexc("#5a7ab0"))
    top = cell_body(c, p, body, rx=9.5, ry=8.5, nucleus=hexc("#4a6aa0"), armored=b == 0, face_y=18)
    pc_mark(c, 16, 25, p, 1.4)
    return (16, 3)


def germ_tagger(c, p):
    b = tier(p)
    body = hexc("#90e0c0")
    pole = 16 if b == 1 else 10
    wave = phase(p) % 2
    c.line([(24, 19), (24, 19 - pole)], hexc("#7a6a5a"), 2)  # flag pole
    flag = p["pc"]
    c.poly([(25, 19 - pole), (31, 21 - pole + wave), (25, 24 - pole)], flag)
    if b == 0:  # Strong: a bigger flag and a sash
        c.poly([(25, 19 - pole), (31, 22 - pole + wave), (25, 26 - pole)], flag)
    top = cell_body(c, p, body, rx=9, ry=8.5, nucleus=hexc("#4aa080"), armored=b == 0)
    if b == 0:
        c.line([(9, 15), (23, 25)], hexc("#e05a5a"), 2)
    return top


def germ_stabber(c, p):
    b = tier(p)
    body = hexc("#60c8c0")
    thrust = -3 if p.get("act") == "fire" else 0
    lance = 13 if b == 0 else 10
    c.line([(23, 25), (23, 25 - lance - 8 + thrust)], hexc("#c8c8d8"), 2 if b != 0 else 3)  # lance
    c.poly([(21, 25 - lance - 8 + thrust), (25, 25 - lance - 8 + thrust), (23, 25 - lance - 13 + thrust)], hexc("#f0f0f8"))
    if b == 1:  # Patrol: little flagella feet
        flagella(c, p, 16, 28, shade(body, -0.2), 2, 6)
    if b == 0:
        receptors(c, 16, 19, 10, 9, shade(body, -0.3), 6, 3)
    top = cell_body(c, p, body, rx=9.5, ry=9, nucleus=hexc("#2a7a78"), armored=b == 0)
    pc_mark(c, 12, 25, p, 1.3)
    return top


def antibody_sniper(c, p):
    b = tier(p)
    body = hexc("#5a8ad0")
    recoil = 2 if p.get("act") == "fire" else 0
    barrels = (16,) if b != 1 else (13.5, 18.5)
    for x in barrels:  # long barrel(s)
        c.rect(x - 2.5 if b == 0 else x - 1.5, 0 + recoil, x + 2.5 if b == 0 else x + 1.5, 12, shade(body, -0.35))
        c.rect(x - 1, 0 + recoil, x + 1, 11, shade(body, -0.1))
    cell_body(c, p, body, rx=10, ry=9, nucleus=None, armored=b == 0, face=False)
    c.ellipse(16, 18, 5.5, 5.5, WHITE)  # one big eye
    c.ellipse(16, 18, 3, 3, hexc("#3a5aa0"))
    c.ellipse(16, 18, 1.4, 1.4, OUTLINE)
    c.px(14.5, 16.5, WHITE)
    pc_mark(c, 16, 26, p, 1.4)
    return (16, 0)


def alarm_signal(c, p):
    b = tier(p)
    body = hexc("#f0d050")
    tall = 5 if b == 1 else 0
    if b == 1:  # Tall: on a stalk
        c.rect(14.5, 22, 17.5, 31, shade(body, -0.35))
    c.poly([(9, 25 - tall), (11, 11 - tall), (21, 11 - tall), (23, 25 - tall)], body)  # bell
    c.ellipse(16, 11 - tall, 5.5, 3.5, body)
    c.rect(8, 24 - tall, 24, 26.5 - tall, shade(body, -0.25))
    c.ellipse(16, 28 - tall, 2.2, 2, shade(body, -0.35))  # clapper
    c.eyes(16, 16 - tall, 2.5, p.get("mood", "calm"), 2)
    c.mouth(16, 19.5 - tall, "open" if p.get("act") != "idle" else "smile", 3)
    if b == 0 or p.get("act") != "idle":  # Loud: sound rings
        for r in (12, 15):
            ring(c, 16, 17 - tall, r, r * 0.8, hexc("#fff4a0"), 18)
    pc_mark(c, 20, 22 - tall, p, 1.3)
    return (16, 6 - tall)


# --- Control ------------------------------------------------------------------

def mucus_wall(c, p):
    b = tier(p)
    goo = hexc("#a0d070", 235) if b != 1 else hexc("#c0e070", 240)
    top = 9 if b == 0 else 12
    c.ellipse(16, top + 3, 13, 4.5, goo)
    c.block(3, top + 2, 29, 29, goo)
    for x, y, r in ((8, 18, 2), (19, 22, 2.5), (24, 15, 1.6), (12, 26, 1.8)):
        c.ellipse(x, y + top - 12, r, r, shade(goo, 0.2))  # bubbles
        c.px(x - 0.5, y + top - 12.5, WHITE)
    drips = (7, 15, 24) if b != 1 else (5, 10, 15, 20, 25)
    for x in drips:
        c.rect(x, 28, x + 2, 31 - (x % 2), goo)
    pc_mark(c, 16, 26, p, 1.3)
    return (16, top - 2)


def allergy_cell(c, p):
    b = tier(p)
    body = hexc("#f4a0c8")
    puff = 1 if p.get("act") != "idle" else 0
    for k in range(7):  # puffy lobes
        a = k * math.tau / 7
        c.blob(16 + math.cos(a) * 8, 19 + math.sin(a) * 7, 4 + puff, 3.6 + puff, body)
    if b == 1:  # Wide: pollen puffs around
        for x, y in ((3, 10), (29, 12), (4, 28), (28, 28)):
            c.ellipse(x, y, 1.8, 1.8, hexc("#f8e070"))
    top = cell_body(c, p, body, rx=8, ry=7.5, granules=hexc("#c05a8a"), n_granules=7, armored=b == 0)
    pc_mark(c, 16, 25, p, 1.3)
    return top


def sneeze_blaster(c, p):
    b = tier(p)
    skin = hexc("#f0b8a0")
    big = 1.2 if b == 0 else 1.0
    if b == 1:  # Far: a long nozzle
        c.rect(13, 0, 19, 8, shade(skin, -0.1))
    c.blob(16, 20, 11 * big, 9 * big, skin)
    c.blob(16, 12, 6 * big, 7 * big, shade(skin, 0.05))  # the nose
    for side in (-1, 1):
        c.ellipse(16 + side * 3, 17 * (1 if big == 1 else 1.02), 2.2 * big, 1.6 * big, hexc("#8a4a4a"))  # nostrils
    c.eyes(16, 22 if b != 0 else 24, 4, p.get("mood", "calm"), 2)
    if p.get("act") == "fire":
        for x, y in ((12, 4), (20, 4), (16, 1)):
            c.ellipse(x, y, 2, 1.6, hexc("#d0f0a0"))
    pc_mark(c, 16, 28, p, 1.3)
    return (16, 3)


def fever_spot(c, p):
    b = tier(p)
    body = hexc("#f07850")
    flick = phase(p) % 2
    glow(c, 16, 18, 14 if b == 0 else 11, hexc("#ffb060"))
    if b == 1:  # Wide: heat waves
        for x in (4, 28):
            c.line([(x, 26), (x - 1, 22), (x + 1, 18), (x - 1, 14)], hexc("#ffb060"))
    c.poly([(11, 13), (16, 2 - (4 if b == 0 else 0) - flick), (21, 13)], hexc("#f0c030"))  # flame tuft
    c.poly([(13, 13), (16, 7 - (3 if b == 0 else 0) + flick), (19, 13)], hexc("#fff080"))
    top = cell_body(c, p, body, rx=10 if b == 0 else 9, ry=9 if b == 0 else 8, nucleus=None, armored=b == 0,
                    granules=hexc("#ffb060"), n_granules=5)
    if b == 0:  # High Fever: a thermometer
        c.rect(25, 16, 27, 28, WHITE)
        c.ellipse(26, 28, 2, 2, hexc("#e03030"))
        c.rect(25.5, 19, 26.5, 28, hexc("#e03030"))
    return (16, 2)


def stun_cell(c, p):
    b = tier(p)
    body = hexc("#f0e060")
    zap = p.get("act") != "idle" or b == 0
    length = 9 if b == 0 else 6
    for side in (-1, 1):  # lightning tendrils
        c.line([(16 + side * 4, 12), (16 + side * 7, 12 - length * 0.5), (16 + side * 5, 12 - length * 0.7),
                (16 + side * 9, 12 - length)], hexc("#c8a020") if not zap else hexc("#fff8a0"), 2)
    if b == 1:  # Wide: shock rings
        ring(c, 16, 19, 14, 12, hexc("#fff8a0"), 22)
    top = cell_body(c, p, body, rx=9.5, ry=9, nucleus=hexc("#c8a020"), armored=b == 0)
    pc_mark(c, 16, 25, p, 1.4)
    return (16, 12 - length)


def swelling(c, p):
    b = tier(p)
    red = hexc("#e05a5a") if b != 0 else hexc("#f04030")
    big = 1.18 if b == 1 else 1.0
    throb = (0, 0.6, 1, 0.6)[phase(p)] if p.get("act") != "idle" else 0
    if b == 0:  # Hot: a glow
        glow(c, 16, 20, 14, hexc("#ffa060"))
    c.ellipse(16, 27, 13 * big, 3.5, shade(red, -0.3))
    c.blob(16, 20, (10 + throb) * big, (8.5 + throb) * big, red)
    c.ellipse(13, 16, 3 * big, 1.8, shade(red, 0.25))
    c.eyes(16, 19, 3, p.get("mood", "calm"), 2)
    c.mouth(16, 22.5, "smile", 3)
    pc_mark(c, 16, 26, p, 1.3)
    return (16, 11)


# --- Toxin --------------------------------------------------------------------

def toxic_skin(c, p):
    b = tier(p)
    skin = hexc("#8a6aa0")
    top = 9 if b == 0 else 12
    tissue_wall(c, top, skin, 4 if b == 0 else 3)
    for x, y in ((8, 17), (16, 21), (23, 16), (12, 26), (22, 26)):  # pores
        c.ellipse(x, y + top - 12, 1.6, 1.2, hexc("#9ad050"))
    if b == 1:  # Venom: dripping
        for x in (7, 16, 25):
            c.rect(x, 29, x + 1.5, 32, hexc("#9ad050"))
    pc_mark(c, 16, 27, p, 1.3)
    return (16, top - 2)


def poison_cell(c, p):
    b = tier(p)
    body = hexc("#8ad060")
    if b == 1:  # Long: a long spitting tube
        c.rect(14.5, 1, 17.5, 10, shade(body, -0.25))
    if b == 0:
        receptors(c, 16, 19, 10.5, 9.5, shade(body, -0.35), 8, 3)
    top = cell_body(c, p, body, rx=10 if b == 0 else 9.5, ry=9, nucleus=hexc("#4a8a3a"), armored=b == 0, face_y=16)
    for side in (-1, 1):  # dripping fangs
        c.poly([(16 + side * 2.5, 20), (16 + side * 1, 20), (16 + side * 1.8, 23)], WHITE)
    c.px(17.8, 24, hexc("#c0f060"))
    pc_mark(c, 16, 26, p, 1.3)
    return (16, 1) if b == 1 else top


def poison_sprayer(c, p):
    b = tier(p)
    body = hexc("#a0e080")
    squeeze = 1 if p.get("act") != "idle" else 0
    c.rect(14.5, 2, 17.5, 11, hexc("#707a80"))  # nozzle
    c.rect(13, 1, 19, 3, hexc("#505a60"))
    if b == 1 or p.get("act") == "fire":  # Misting: a mist cloud
        for x, y in ((10, 0), (16, -1), (22, 0)):
            c.ellipse(x, y + 2, 3, 2, hexc("#d0f0b0", 200))
    c.blob(16, 20, (10.5 if b == 0 else 9.5) - squeeze, 9, body)  # squeeze bulb
    c.ellipse(13, 15, 3, 1.8, shade(body, 0.25))
    c.eyes(16, 18, 3, p.get("mood", "calm"), 2)
    c.mouth(16, 21.5, "smile", 3)
    if b == 0:  # Strong: a reinforced band
        c.rect(6, 23, 26, 25, hexc("#5a7a4a"))
    pc_mark(c, 16, 26, p, 1.3)
    return (16, 1)


def acid_puddle(c, p):
    b = tier(p)
    acid = hexc("#b8f040") if b != 0 else hexc("#90e020")
    wide = 14.5 if b == 1 else 12
    c.ellipse(16, 23, wide + 1, 7.5, shade(acid, -0.35))
    c.ellipse(16, 22.5, wide, 6.5, acid)
    for k, (x, y) in enumerate(((10, 21), (20, 23), (15, 25), (23, 20))):
        c.ellipse(x, y - (phase(p) + k) % 2, 1.8, 1.8, shade(acid, 0.25))  # bubbles
    if b == 1:  # Spilling: spill fingers
        for x in (2, 30):
            c.ellipse(x, 25, 2.5, 1.5, acid)
    c.eyes(16, 21, 3, p.get("mood", "calm"), 2)
    pc_mark(c, 16, 26, p, 1.3)
    return (16, 15)


def plague_cell(c, p):
    b = tier(p)
    body = hexc("#9a6ac0")
    length = 6 if b == 1 else 4
    c.spikes(16, 19, 9, 12 if b == 0 else 10, hexc("#d8c0f0"), length)
    top = cell_body(c, p, body, rx=9.5, ry=9, nucleus=hexc("#5a3a80"), granules=hexc("#c0e060"), n_granules=5,
                    armored=b == 0)
    pc_mark(c, 16, 25, p, 1.3)
    return (16, 19 - 9 - length)


def rot_patch(c, p):
    b = tier(p)
    mold = hexc("#6a7a4a")
    wide = 14 if b == 1 else 12
    c.ellipse(16, 25, wide + 1, 6, shade(mold, -0.3))
    c.ellipse(16, 24.5, wide, 5.5, mold)
    for x, y in ((9, 24), (19, 26), (23, 23)):
        c.ellipse(x, y, 2, 1.2, hexc("#a8b870"))
    shrooms = ((10, 19, 4), (19, 15, 5), (24, 21, 3)) if b != 0 else ((9, 18, 4.5), (17, 12, 6), (25, 19, 4))
    for x, y, r in shrooms:  # little mushrooms
        c.rect(x - 1, y, x + 1, y + 6, hexc("#e8e0c8"))
        c.ellipse(x, y, r, r * 0.6, hexc("#c86a4a") if b != 1 else hexc("#a04ac0"))
        c.px(x - 1, y - 1, WHITE)
    pc_mark(c, 16, 27, p, 1.3)
    return (16, 7)


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
