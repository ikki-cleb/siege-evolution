"""World 2 (Wild Kingdom): farm animals defend the farmhouse. Animals have
faces; walls and objects don't.

Redesigned bigger and sturdier (see world_backyard.py): animals are
full-body chibis (big cute head on a sturdy body); evolutions are breeds
and gear (power branch) or a new pose/feature (utility branch); farm
structures are chunky and textured. Every unit draws its own evolutions
(p["branch"]), and draw_sprites.py scales evolutions up.
"""
import math

from .hefty import glow, head, pc_mark, plump_bird, puffs, quadruped, ring, tier
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, animal, bird, legs, phase

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True

STONE = hexc("#9a968e")
WOOD = hexc("#8a5a32")
STRAW = hexc("#e0c060")
MUD = hexc("#7a5434")


def stones(c, rows, top=12, bottom=30, color=STONE, mortar=None):
    """A dry-stone wall: rows of irregular stones."""
    if mortar:
        c.block(3, top, 29, bottom, mortar)
    h = (bottom - top) / rows
    for r in range(rows):
        y = top + r * h
        x = 3 - (r % 2) * 3
        while x < 29:
            w = 6 + (x * 7 + r * 3) % 3
            col = shade(color, ((x + r * 5) % 4 - 1.5) * 0.04)
            c.blob(max(4, x + w / 2), y + h / 2, w / 2, h / 2 - 0.3, col)
            x += w


# --- Fortress -------------------------------------------------------------------

def stone_wall(c, p):
    b = tier(p)
    if b == 0:  # Fieldstone Wall: taller, mortared
        stones(c, 4, 9, 30, STONE, mortar=hexc("#6a665e"))
        c.rect(3, 8, 29, 10, hexc("#b8b4ac"))  # capstones
    else:
        stones(c, 3, 13, 30)
        if b == 1:  # Spiked: iron spikes along the top
            for x in (6, 11, 16, 21, 26):
                c.poly([(x - 1.5, 13), (x + 1.5, 13), (x, 7)], hexc("#606874"))
    c.px(16, 22, p["pc"])
    pc_mark(c, 25, 27, p, 1.3)
    return (16, 9)


def bull(c, p):
    b = tier(p)
    fur = hexc("#5a3a28") if b != 0 else hexc("#3a2418")
    act = p.get("act") == "fire"
    top = quadruped(c, p, fur, size=1.15 if b == 0 else 1.05, ears="side", snout=hexc("#c89880"),
                    horns=hexc("#f0e8d0"), tail=fur, head_y=14 + (2 if b == 1 or act else 0))
    if b == 0:  # Prize Bull: brass nose ring and a blue rosette
        c.ellipse(16, 21, 2, 1.6, hexc("#e0b040"))
        c.ellipse(16, 21, 1, 0.6, shade(fur, 0.1))
        c.ellipse(24, 22, 2.6, 2.6, hexc("#3a6ad0"))
        c.ellipse(24, 22, 1.2, 1.2, hexc("#f0d040"))
    if b == 1:  # Stampeding: dust kicked up
        puffs(c, [(5, 29, 2.5), (27, 29, 2.5), (9, 31, 2)], hexc("#d8c8a8", 210))
    pc_mark(c, 9, 22, p, 1.4)
    return top


def llama(c, p):
    b = tier(p)
    wool = hexc("#f0e6d4")
    # A llama: long neck, so the head sits high above a woolly body.
    step = (0, 1, 0, -1)[phase(p)]
    for lx in (-6, 6, -3, 3):
        c.rect(16 + lx - 1.5, 22, 16 + lx + 1.5, 30 + (step if lx > 0 else -step) * 0.5, shade(wool, -0.15 if abs(lx) == 6 else 0))
    c.blob(16, 21, 9.5, 6.5, wool)
    if b == 0:  # Alpha Llama: a bright saddle blanket and pompoms
        c.rect(9, 18, 23, 23, hexc("#d84a6a"))
        for x in (10, 16, 22):
            c.ellipse(x, 23.5, 1.4, 1.4, hexc("#f0d040"))
    c.rect(13.5, 9, 18.5, 19, wool)  # neck
    for y in (11, 14, 17):
        c.px(14, y, shade(wool, -0.12))
    c.blob(16, 8, 5, 4.5, wool)
    for side in (-1, 1):  # banana ears
        c.ellipse(16 + side * 3.5, 2.5, 1.4, 3.2, shade(wool, -0.15))
    c.ellipse(16, 10, 2.5, 1.6, hexc("#d8c4a8"))
    c.eyes(16, 7, 2, p.get("mood", "calm"), 2)
    if b == 1 or p.get("act") == "fire":  # Long-Spit: a spit glob
        c.ellipse(16, 14 if b != 1 else 13, 1.6, 1.6, hexc("#d8f0e0"))
    pc_mark(c, 21, 25, p, 1.4)
    return (16, 3)


def hedge(c, p):
    b = tier(p)
    leaf = hexc("#3f7f30") if b != 0 else hexc("#2f6a26")
    h_top = 10 if b == 0 else 13
    c.block(3, h_top, 29, 30, shade(leaf, -0.2))
    for x in range(5, 29, 5):
        for y in range(h_top + 2, 29, 5):
            c.blob(x, y, 3.4, 3, shade(leaf, ((x + y) % 3 - 1) * 0.06))
    if b == 1:  # Growing: fresh shoots and berries
        for x in (6, 14, 22, 27):
            c.line([(x, h_top), (x + 1, h_top - 5)], hexc("#7ac050"))
            c.ellipse(x + 1, h_top - 5, 1.6, 1.4, hexc("#7ac050"))
        for x, y in ((9, 18), (20, 23), (25, 16)):
            c.ellipse(x, y, 1.3, 1.3, hexc("#d03040"))
    else:
        for x, y in ((9, 18), (20, 23)):
            c.ellipse(x, y, 1.2, 1.2, hexc("#d03040"))
    pc_mark(c, 16, 26, p, 1.4)
    return (16, h_top - 2)


def draft_horse(c, p):
    b = tier(p)
    coat = hexc("#8a5a34")
    if b == 1:  # Rearing Horse: up on its hind legs
        c.rect(10, 22, 13, 30, shade(coat, -0.2))
        c.rect(19, 22, 22, 30, shade(coat, -0.2))
        c.ellipse(16, 18, 7.5, 9, coat)
        for side in (-1, 1):  # front hooves raised
            c.line([(16 + side * 5, 14), (16 + side * 9, 9), (16 + side * 8, 6)], coat, 3)
        top = None
        hy = 9
        c.ellipse(16, hy + 1, 9, 7.5, hexc("#3a2418"))  # mane
        c.blob(16, hy, 6.5, 6, coat)
        for side in (-1, 1):
            c.poly([(16 + side * 2, hy - 4.5), (16 + side * 5.5, hy - 4), (16 + side * 4.5, hy - 9)], shade(coat, -0.2))
        c.ellipse(16, hy + 3, 3.5, 2.4, hexc("#d8b898"))
        c.eyes(16, hy - 1.5, 2.6, p.get("mood", "calm"), 2)
        pc_mark(c, 16, 24, p, 1.4)
        return (16, hy - 8)
    top = quadruped(c, p, coat if b != 0 else hexc("#6a3a1c"), size=1.12 if b == 0 else 1.05, ears="point",
                    snout=hexc("#d8b898"), mane=hexc("#3a2418"), tail=hexc("#3a2418"),
                    hoof=hexc("#f0ece4") if b == 0 else None, belly=hexc("#f0e6d4") if b == 0 else None)
    if b == 0:  # Clydesdale: a harness collar
        c.ellipse(16, 20, 7.5, 2.4, hexc("#3a2a20"))
        for x in (11, 16, 21):
            c.px(x, 20, hexc("#e0b040"))
    pc_mark(c, 23, 22, p, 1.4)
    return top


def stone_silo(c, p):
    b = tier(p)
    body = hexc("#a8a49c")
    c.block(8, 9, 24, 30, body)
    for y in range(11, 30, 3):  # stone courses
        c.line([(8, y), (23, y)], shade(body, -0.15))
    for y in range(11, 30, 6):
        c.px(12 + (y % 4), y + 1, shade(body, -0.15))
        c.px(19 - (y % 4), y + 1, shade(body, -0.15))
    c.poly([(6, 10), (16, 2), (26, 10)], hexc("#b84a3a"))  # roof
    c.poly([(16, 2), (26, 10), (21, 10)], hexc("#8a3428"))
    c.rect(14, 22, 18, 30, hexc("#5a3a20"))  # door
    if b == 0:  # Reinforced: iron bands with rivets
        for y in (14, 24):
            c.rect(8, y, 24, y + 1.5, hexc("#4a4e58"))
            for x in (10, 14, 18, 22):
                c.px(x, y + 0.5, hexc("#c8ccd4"))
    if b == 1:  # Thorned: thorny vines climbing it
        c.line([(8, 30), (12, 24), (9, 18), (13, 12)], hexc("#4a7a2a"), 2)
        c.line([(24, 30), (20, 22), (23, 15)], hexc("#4a7a2a"), 2)
        for x, y in ((11, 24), (10, 18), (21, 22), (22, 16)):
            c.px(x + 1, y, hexc("#e8e0c0"))
    pc_mark(c, 16, 16, p, 1.4)
    return (16, 2)


# --- Swarm --------------------------------------------------------------------

def hay_bale(c, p):
    b = tier(p)
    top = 10 if b == 0 else 13
    c.block(3, top, 29, 30, STRAW)
    for y in range(top + 2, 29, 3):
        c.line([(4, y), (28, y + (y % 2))], shade(STRAW, -0.12))
    for x in (9, 22):  # twine
        c.rect(x, top, x + 1.5, 29, hexc("#a06030"))
    if b == 1:  # Thistle Hay: thistles poking out
        for x, y in ((6, top), (15, top - 1), (25, top)):
            c.line([(x, y + 2), (x, y - 3)], hexc("#5a8a3a"))
            c.ellipse(x, y - 4, 1.8, 1.8, hexc("#b060c0"))
    pc_mark(c, 16, 26, p, 1.4)
    return (16, top - 2)


def hen(c, p):
    b = tier(p)
    top = plump_bird(c, p, hexc("#f4f0e8") if b != 0 else hexc("#c86a3a"), hexc("#e8a030"), size=1.05,
                     belly=hexc("#ffffff") if b != 0 else hexc("#e0905a"))
    c.poly([(14, top[1] + 0.5), (16, top[1] - 4), (18, top[1] + 0.5)], hexc("#d83a3a"))  # comb
    c.ellipse(16, top[1] + 12, 1.4, 2, hexc("#d83a3a"))  # wattle
    if b == 1:  # Scout Hen: a little spyglass under the wing
        c.rect(23, 16, 29, 18, hexc("#c8a040"))
        c.ellipse(29, 17, 1.4, 1.4, hexc("#80c8f0"))
    pc_mark(c, 16, 24, p, 1.4)
    return top


def barn_swallow(c, p):
    b = tier(p)
    navy = hexc("#2a3a7a")
    top = plump_bird(c, p, navy, hexc("#3a3030"), size=0.95, belly=hexc("#f0d8b8"), wing=shade(navy, -0.15))
    c.ellipse(16, top[1] + 8, 3, 1.6, hexc("#c84a3a"))  # red throat
    for side in (-1, 1):  # forked tail
        c.line([(16 + side * 2, 27), (16 + side * 6, 31)], navy, 2)
    if b == 0:  # Diving: swept-back wings with speed lines
        for y in (12, 16):
            c.line([(1, y), (5, y + 1)], WHITE)
            c.line([(27, y + 1), (31, y)], WHITE)
    if b == 1:  # Sentry: perched on a post
        c.rect(14, 28, 18, 32, WOOD)
    return top


def bee_skep(c, p):
    b = tier(p)
    straw = hexc("#d8a840")
    c.rect(5, 27, 27, 30, WOOD)  # stand
    for k, (w, y) in enumerate(((12, 25), (11, 21), (9.5, 17), (7.5, 13), (5, 9.5))):
        c.ellipse(16, y, w, 3, shade(straw, -0.12 if k % 2 else 0))
        c.line([(16 - w + 1, y + 1.5), (16 + w - 1, y + 1.5)], shade(straw, -0.3))
    c.ellipse(16, 25, 2.6, 2, hexc("#2a1a10"))  # entrance
    bees = ((6, 12), (26, 10), (22, 4))
    if b == 0:  # Angry Skep: more bees
        bees = bees + ((9, 4), (28, 19), (3, 20))
    for k, (x, y) in enumerate(bees):
        y += (phase(p) + k) % 2
        c.ellipse(x, y, 1.6, 1.2, hexc("#f0c040"))
        c.px(x, y, hexc("#2a1a10"))
        c.px(x, y - 1.5, hexc("#e8f0ff"))
    if b == 1:  # Buzzing: a ring of buzz
        ring(c, 16, 18, 14, 12, hexc("#fff0a0"), 20)
    pc_mark(c, 22, 22, p, 1.3)
    return (16, 6)


def barn_cat(c, p):
    b = tier(p)
    fur = hexc("#e08a3a") if b != 0 else hexc("#6a6a72")
    top = quadruped(c, p, fur, size=0.95 if b != 0 else 1.05, ears="point", snout=hexc("#f8e8d8"),
                    tail=fur, spots=shade(fur, -0.2) if b != 1 else None)
    for side in (-1, 1):  # whiskers
        c.line([(16 + side * 3, top[1] + 9), (16 + side * 7, top[1] + 8.5)], hexc("#f8f0e8"))
    if b == 0:  # Tomcat: a torn ear and a scar
        c.px(top[0] + 4, top[1] + 1, (0, 0, 0, 0))
        c.line([(top[0] - 3, top[1] + 3), (top[0] - 1, top[1] + 6)], hexc("#c8a8a0"))
    if b == 1:  # Prowling: crouched low with a swishing tail
        c.line([(24, 22), (29, 17), (28, 12)], fur, 2)
    pc_mark(c, 16, 23, p, 1.4)
    return top


def muddy_pen(c, p):
    b = tier(p)
    wide = 15 if b == 1 else 12
    c.ellipse(16, 23, wide + 1, 8, shade(MUD, -0.2))
    c.ellipse(16, 22.5, wide, 7, MUD if b != 0 else shade(MUD, -0.15))
    for x, y in ((10, 21), (21, 24), (16, 19), (13, 25)):
        c.ellipse(x, y, 2, 1.2, shade(MUD, 0.15))  # wet shine
    for x in (3, 29):  # fence posts
        c.rect(x - 1.5, 10, x + 1.5, 28, WOOD)
    c.rect(2, 13, 30, 14.5, shade(WOOD, 0.1))
    if b == 0:  # Deep Mud: bubbles
        for x, y in ((12, 22), (20, 21)):
            c.ellipse(x, y - phase(p) % 2, 1.6, 1.6, shade(MUD, 0.25))
    pc_mark(c, 16, 23, p, 1.4)
    return (16, 10)


# --- Precision ------------------------------------------------------------------

def wooden_fence(c, p):
    b = tier(p)
    for x in (5, 16, 27):  # posts
        c.block(x - 2, 9, x + 2, 30, shade(WOOD, -0.08))
        if b == 0:  # Picket: pointed white tops
            c.poly([(x - 2, 9), (x + 2, 9), (x, 5)], hexc("#f0ece4"))
    rail = hexc("#f0ece4") if b == 0 else WOOD
    for y in (13, 22):
        c.block(2, y, 30, y + 3, rail)
        c.line([(3, y + 1), (29, y + 1)], shade(rail, -0.15))
    if b == 1:  # Barbed Fence: twisted wire with barbs
        for y in (11, 19, 27):
            c.line([(2, y), (30, y)], hexc("#707880"))
            for x in range(4, 30, 5):
                c.px(x, y - 1, hexc("#c8ccd4"))
                c.px(x, y + 1, hexc("#c8ccd4"))
    pc_mark(c, 11, 26, p, 1.3)
    return (16, 7)


def barn_owl(c, p):
    b = tier(p)
    feathers = hexc("#d8a868") if b != 0 else hexc("#8a6a48")
    top = plump_bird(c, p, feathers, hexc("#7a6a5a"), size=1.08, belly=hexc("#f4ecdc"))
    if b == 0:  # Great Horned: ear tufts
        for side in (-1, 1):
            c.poly([(16 + side * 4, top[1] + 2), (16 + side * 8, top[1] - 4), (16 + side * 7, top[1] + 3)], shade(feathers, -0.2))
    c.ellipse(16, top[1] + 5.5, 7, 4.5, hexc("#f8f0e0"))  # heart-shaped face disc
    c.eyes(16, top[1] + 5.5, 3, p.get("mood", "calm"), 2)
    c.poly([(15, top[1] + 7), (17, top[1] + 7), (16, top[1] + 9.5)], hexc("#7a6a5a"))
    if b == 1:  # Far-Sighted: spectacles
        for side in (-1, 1):
            c.ellipse(16 + side * 3, top[1] + 5.5, 2.4, 2.4, hexc("#c8a040"))
            c.ellipse(16 + side * 3, top[1] + 5.5, 1.5, 1.5, hexc("#d8f0ff"))
            c.px(16 + side * 3, top[1] + 5.5, OUTLINE)
    pc_mark(c, 16, 22, p, 1.4)
    return top


def watchdog(c, p):
    b = tier(p)
    fur = hexc("#a87848")
    top = quadruped(c, p, fur, size=1.05 if b != 0 else 1.12, ears="round", snout=hexc("#e8d0b0"),
                    tail=fur, belly=hexc("#f0e0c8"))
    c.ellipse(16, top[1] + 13.5, 6, 1.6, hexc("#c83a3a"))  # red collar
    c.ellipse(16, top[1] + 15, 1.4, 1.4, hexc("#e0b040"))  # tag
    if b == 0 or p.get("act") == "fire":  # Howling: head up, a howl
        for k in range(3):
            c.px(22 + k * 2, top[1] - 1 - k, hexc("#f0f0f8"))
    if b == 1:  # Patrol: a lantern on its collar
        c.ellipse(21, top[1] + 15, 2, 2, hexc("#f0d060"))
    return top


def ferret(c, p):
    b = tier(p)
    fur = hexc("#e8dcc8") if b != 0 else hexc("#5a4030")
    # A long, low ferret curling around: a tube body with a mask.
    for k in range(6):
        x = 6 + k * 4
        y = 25 - math.sin(k * 0.9 + phase(p) * 0.5) * 2
        c.blob(x, y, 4.2, 3.6, shade(fur, -0.05 * (k % 2)))
    c.line([(28, 24), (31, 20)], shade(fur, -0.3), 2)
    top = head(c, p, 9, 17, 5.5, fur)
    c.rect(4.5, 15.5, 13.5, 17.5, hexc("#3a2a22") if b != 0 else hexc("#1a1210"))  # bandit mask
    c.eyes(9, 16.5, 2.2, p.get("mood", "calm"), 2)
    c.ellipse(9, 20, 1.6, 1.1, hexc("#e89090"))
    for side in (-1, 1):
        c.ellipse(9 + side * 4, 12, 1.6, 1.6, shade(fur, -0.2))
    if b == 1:  # Roaming: a little bandana pack
        c.ellipse(22, 20, 3, 2.4, hexc("#c83a3a"))
    pc_mark(c, 18, 26, p, 1.3)
    return (9, 11)


def falcon(c, p):
    b = tier(p)
    feathers = hexc("#5a6a7a") if b != 0 else hexc("#3a4a5a")
    top = plump_bird(c, p, feathers, hexc("#f0c040"), size=1.05, belly=hexc("#e8e0d0"))
    c.rect(11, top[1] + 4, 21, top[1] + 6, hexc("#2a3038"))  # dark "helmet" stripe
    c.eyes(16, top[1] + 5, 3, p.get("mood", "calm"), 2)
    for x in (13, 16, 19):  # barred chest
        c.px(x, 21, shade(feathers, -0.2))
        c.px(x, 24, shade(feathers, -0.2))
    if b == 0:  # Peregrine: a leather hood crest and jesses
        c.poly([(13, top[1] + 1), (16, top[1] - 4), (19, top[1] + 1)], hexc("#8a4a2a"))
    if b == 1:  # Swift: speed lines
        for y in (14, 19):
            c.line([(1, y), (5, y)], WHITE)
    return top


def scarecrow(c, p):
    b = tier(p)
    tall = b == 1
    y0 = -4 if tall else 0
    c.rect(15, 14 + y0, 17, 31, WOOD)  # pole
    c.line([(4, 15 + y0), (28, 15 + y0)], WOOD, 2)  # arms
    shirt = hexc("#4a6ab0") if b != 0 else hexc("#4a3a5a")
    c.poly([(9, 14 + y0), (23, 14 + y0), (21, 26 + y0), (11, 26 + y0)], shirt)
    c.rect(9, 18 + y0, 23, 19 + y0, shade(shirt, -0.2))
    for x, y in ((12, 21), (19, 23)):
        c.rect(x, y + y0, x + 2, y + 2 + y0, hexc("#c8a060"))  # patches
    for x in (4, 28):  # straw hands
        c.line([(x, 15 + y0), (x - (16 - x) * 0.15, 18 + y0)], STRAW)
    c.blob(16, 9 + y0, 5, 5, hexc("#e8d0a0"))  # sack head
    c.ellipse(16, 4.5 + y0, 9, 2, hexc("#a87840"))  # hat brim
    c.rect(12, 0 + y0, 20, 4.5 + y0, hexc("#a87840"))
    if b == 0:  # Spooky: glowing jack-o-lantern head
        c.blob(16, 9 + y0, 5.5, 5, hexc("#e87a20"))
        for x in (14, 18):
            c.poly([(x - 1, 8 + y0), (x + 1, 8 + y0), (x, 6.5 + y0)], hexc("#fff080"))
        c.line([(13, 11 + y0), (19, 11 + y0)], hexc("#fff080"))
    else:
        c.px(14, 9 + y0, OUTLINE)
        c.px(18, 9 + y0, OUTLINE)
        c.line([(14, 11 + y0), (18, 11 + y0)], OUTLINE)
    pc_mark(c, 16, 22 + y0, p, 1.3)
    return (16, 0 + y0)


# --- Control --------------------------------------------------------------------

def mud_wall(c, p):
    b = tier(p)
    mud = MUD if b != 1 else hexc("#5a6a3a")
    top = 9 if b == 0 else 12
    c.block(3, top, 29, 30, mud)
    for x, y in ((7, 15), (14, 19), (22, 16), (10, 25), (20, 26), (26, 22)):
        c.ellipse(x, y + top - 12, 2.4, 1.6, shade(mud, 0.12))
    for x in (6, 13, 20, 27):  # straw bits
        c.line([(x, top + 4), (x + 2, top + 6)], STRAW)
    if b == 1:  # Sludge: dripping
        for x in (8, 17, 25):
            c.rect(x, 29, x + 1.5, 31.5, mud)
    pc_mark(c, 16, 27, p, 1.3)
    return (16, top - 2)


def skunk(c, p):
    b = tier(p)
    if b is not None:  # a stink cloud
        for x, y, r in ((5, 13, 3.5), (27, 11, 4), (8, 6, 3), (24, 4, 3)):
            c.ellipse(x - phase(p) % 2, y, r, r * 0.8, hexc("#c8e070", 120 if b == 1 else 170))
    tail = [(22, 26), (28, 18), (26, 8), (21, 6)]
    c.line(tail, hexc("#1a1a22"), 6 if b == 0 else 5)  # big fluffy tail
    c.line(tail, hexc("#f4f4f4"), 2)
    top = quadruped(c, p, hexc("#22222a"), size=0.95, ears="round", snout=hexc("#3a3a44"))
    c.line([(16, top[1] + 1), (16, top[1] + 6)], hexc("#f4f4f4"), 2)  # white stripe
    pc_mark(c, 16, 22, p, 1.3)
    return top


def honking_goose(c, p):
    b = tier(p)
    honk = p.get("act") == "fire" or b == 1
    c.ellipse(16, 23, 10, 7, shade(hexc("#f4f4f4"), -0.1))
    c.blob(16, 22.5, 9.5, 6.5, hexc("#f4f4f4"))  # body
    for side in (-1, 1):
        c.ellipse(16 + side * 8, 21, 3.5, 5, hexc("#e0e0e8"))  # wings
    for side in (-1, 1):
        c.rect(16 + side * 3 - 1, 28, 16 + side * 3 + 1, 31, hexc("#e8902a"))
    c.rect(13.5, 8, 18.5, 20, hexc("#f4f4f4"))  # neck
    c.blob(16, 8, 5, 4.5, hexc("#f4f4f4"))
    beak_y = 10 + (1 if honk else 0)
    c.poly([(13, beak_y), (19, beak_y), (16, beak_y + 4 + (2 if honk else 0))], hexc("#e8902a"))
    c.eyes(16, 6.5, 2.2, "angry" if b == 0 else p.get("mood", "calm"), 2)
    if honk:  # Loud: sound waves
        for r in (3, 5):
            for side in (-1, 1):
                c.px(16 + side * (6 + r), 11, WHITE)
                c.px(16 + side * (6 + r), 9 + r * 0.3, WHITE)
    pc_mark(c, 16, 24, p, 1.4)
    return (16, 3)


def bonfire(c, p):
    b = tier(p)
    flick = phase(p) % 2
    width = 13 if b == 1 else 10
    for side in (-1, 1):  # crossed logs
        c.line([(16 - side * width, 30), (16 + side * width * 0.6, 22)], WOOD, 3)
    for x in range(16 - width, 16 + width + 1, 5):  # ring of stones
        c.blob(x, 29, 2.2, 1.6, STONE)
    big = b == 0
    glow(c, 16, 18, 13 if big else 10, hexc("#ffb040"))
    c.poly([(16 - width * 0.7, 26), (16, 4 - (5 if big else 0) - flick), (16 + width * 0.7, 26)], hexc("#e85a20"))
    c.poly([(16 - width * 0.45, 26), (16, 10 - (4 if big else 0) + flick), (16 + width * 0.45, 26)], hexc("#f0a030"))
    c.poly([(13, 26), (16, 17 - flick), (19, 26)], hexc("#fff080"))
    pc_mark(c, 16, 29, p, 1.3)
    return (16, 4)


def mule(c, p):
    b = tier(p)
    coat = hexc("#7a6a5a") if b != 0 else hexc("#5a4a3c")
    top = quadruped(c, p, coat, size=1.08, ears="long", snout=hexc("#d8c8b0"), tail=shade(coat, -0.3),
                    belly=hexc("#d8c8b0"))
    if b == 0:  # Stubborn: a saddle pack and a scowl
        c.rect(9, 17, 23, 21, hexc("#8a4a2a"))
        c.rect(14, 16, 18, 22, hexc("#c84a3a"))
        c.line([(top[0] - 4, top[1] + 4), (top[0] - 1, top[1] + 5)], OUTLINE)
        c.line([(top[0] + 4, top[1] + 4), (top[0] + 1, top[1] + 5)], OUTLINE)
    if b == 1 or p.get("act") == "fire":  # Kicking: a hoof flying out with a spark
        c.line([(24, 24), (30, 21)], coat, 3)
        c.px(31, 20, hexc("#fff080"))
    return top


def smoke_pot(c, p):
    b = tier(p)
    iron = hexc("#3a3a42")
    smoke = hexc("#c8c8d0", 210)
    clouds = ((16, 7, 4), (11, 3, 3), (21, 4, 3.5))
    if b is not None:
        clouds = clouds + ((6, 9, 3), (26, 9, 3)) if b == 1 else ((16, 6, 5.5), (10, 2, 4), (22, 2, 4.5))
    for k, (x, y, r) in enumerate(clouds):
        c.blob(x + ((phase(p) + k) % 2), y, r, r * 0.85, smoke)
    c.ellipse(16, 27, 11, 3.5, shade(iron, -0.2))
    c.blob(16, 21, 10, 8, iron)  # cauldron
    c.ellipse(16, 14, 9.5, 2.5, shade(iron, 0.2))
    c.ellipse(16, 14, 7.5, 1.6, hexc("#c84a2a"))  # embers inside
    for x in (8, 24):
        c.rect(x - 1, 28, x + 1, 31, iron)
    pc_mark(c, 16, 22, p, 1.4)
    return (16, 3)


# --- Toxin ----------------------------------------------------------------------

def bramble_fence(c, p):
    b = tier(p)
    vine = hexc("#4a3a2a")
    for x in (4, 28):
        c.block(x - 2, 10, x + 2, 30, WOOD)
    rows = (14, 20, 26) if b != 0 else (12, 17, 22, 27)
    for y in rows:
        pts = [(3 + k * 3.2, y + math.sin(k * 1.4 + y) * 1.5) for k in range(9)]
        c.line(pts, vine, 2)
        for x, yy in pts[1::2]:
            c.px(x, yy - 1.5, hexc("#e8e0c0"))
    berries = hexc("#5a2a6a") if b != 1 else hexc("#a0e040")  # Poison: sickly green berries
    for x, y in ((9, 13), (17, 19), (24, 25), (12, 26)):
        c.ellipse(x, y, 1.6, 1.6, berries)
    pc_mark(c, 16, 29, p, 1.3)
    return (16, 9)


def rattlesnake(c, p):
    b = tier(p)
    scale = hexc("#a8885a") if b != 0 else hexc("#8a7a4a")
    coil = [(16, 26, 11, 4.5), (16, 22, 8.5, 3.6)]
    if b == 1:  # Long Rattler: an extra coil
        coil = [(16, 27, 12.5, 4.5)] + coil
    for x, y, rx, ry in coil:
        c.ellipse(x, y, rx, ry, shade(scale, -0.25))
        c.ellipse(x, y - 0.6, rx - 1, ry - 1, scale)
    for x in range(7, 26, 4):  # diamond pattern
        c.poly([(x, 26), (x + 1.5, 24.5), (x + 3, 26), (x + 1.5, 27.5)], shade(scale, -0.35 if b == 0 else -0.2))
    rattle_shake = phase(p) % 2
    for k in range(3):  # the rattle
        c.ellipse(26 + k * 1.5, 19 - k * 2 - rattle_shake, 1.6, 1.2, hexc("#e8d8b0"))
    c.rect(13.5, 12, 18.5, 22, scale)  # raised neck
    c.blob(16, 10, 6, 5, scale)  # head
    c.eyes(16, 9, 2.4, p.get("mood", "calm"), 2)
    tongue = 4 if p.get("act") == "fire" else 2
    c.line([(16, 14), (16, 14 + tongue)], hexc("#d83a4a"))
    pc_mark(c, 16, 21, p, 1.3)
    return (16, 5)


def toad(c, p):
    b = tier(p)
    skin = hexc("#6a8a3a") if b != 0 else hexc("#8a6a3a")
    for side in (-1, 1):  # big back legs
        c.ellipse(16 + side * 10, 26, 4.5, 3, shade(skin, -0.15))
        c.rect(16 + side * 5 - 1.5, 26, 16 + side * 5 + 1.5, 30, shade(skin, -0.1))
    c.ellipse(16, 22, 12, 9, shade(skin, -0.2))
    c.blob(16, 21, 11.5, 8.5, skin)
    c.ellipse(16, 24, 7, 4, hexc("#d8d0a0"))  # pale belly
    for x, y in ((8, 17), (23, 18), (11, 22), (21, 23)):  # warts
        c.ellipse(x, y, 1.4, 1.2, shade(skin, 0.18))
    for side in (-1, 1):  # bulging eyes on top
        c.ellipse(16 + side * 5, 13, 3.4, 3, skin)
    c.eyes(16, 13, 5, p.get("mood", "calm"), 2)
    c.line([(10, 19), (16, 20.5), (22, 19)], OUTLINE)  # wide smile
    if b == 0:  # Cane Toad: poison glands
        for side in (-1, 1):
            c.ellipse(16 + side * 9, 15, 2.4, 1.6, hexc("#d8c060"))
    if b == 1 or p.get("act") == "fire":  # Spitting: a glob
        c.ellipse(16, 8, 1.8, 1.8, hexc("#c0f060"))
    pc_mark(c, 16, 25, p, 1.4)
    return (16, 8)


def manure_pile(c, p):
    b = tier(p)
    brown = hexc("#6a4a28") if b != 0 else hexc("#4a3a1c")
    wide = 13 if b == 1 else 11
    c.ellipse(16, 28, wide + 1, 3.5, shade(brown, -0.2))
    for w, y in ((wide, 25), (wide - 3, 20), (wide - 6, 15)):
        c.blob(16, y, w, 4, brown)
        c.line([(16 - w + 2, y + 1.5), (16 + w - 2, y + 1.5)], shade(brown, -0.2))
    c.poly([(14, 12), (16, 7), (18, 12)], brown)
    flies = ((8, 6), (24, 8)) if b != 0 else ((8, 6), (24, 8), (16, 3), (27, 15))
    for k, (x, y) in enumerate(flies):  # buzzing flies
        c.px(x + (phase(p) + k) % 2, y, OUTLINE)
        c.px(x + (phase(p) + k) % 2, y - 1, hexc("#e8f0ff"))
    if b is not None:  # stink lines
        for x in (10, 22):
            c.line([(x, 10), (x - 1, 7), (x + 1, 4)], hexc("#c8e070"))
    pc_mark(c, 16, 26, p, 1.3)
    return (16, 6)


def gila_monster(c, p):
    b = tier(p)
    skin = hexc("#e87a5a") if b != 0 else hexc("#e85a3a")
    dark = hexc("#2a1a1a")
    length = 1.25 if b == 1 else 1.0
    step = (0, 1, 0, -1)[phase(p)]
    for k, (x, y) in enumerate(((10, 25), (22, 25), (10, 17), (22, 17))):  # splayed legs
        side = -1 if x < 16 else 1
        c.line([(x, y), (x + side * 4, y + 2 + (step if k % 2 else -step))], dark, 2)
    c.line([(16, 27), (16 + 6 * length, 30), (16 + 12 * length, 29)], skin, 3)  # thick tail
    c.ellipse(16, 21, 7.5, 9 * length, shade(skin, -0.2))
    c.blob(16, 21, 7, 8.5 * length, skin)
    for x, y in ((12, 17), (19, 19), (13, 24), (20, 26), (16, 21)):  # beaded black pattern
        c.ellipse(x, y, 2, 1.4, dark)
    top = head(c, p, 16, 10, 5.5, skin)
    if b == 0:  # Venomous: dripping fangs
        c.px(14, 15, WHITE)
        c.px(18, 15, WHITE)
        c.px(18, 16.5, hexc("#a0e040"))
    pc_mark(c, 16, 22, p, 1.3)
    return (16, 4)


def hemlock_patch(c, p):
    b = tier(p)
    stem = hexc("#5a8a3a")
    if b == 1:  # Virulent: a sickly haze
        glow(c, 16, 14, 13, hexc("#c8f070"))
    c.rect(3, 27, 29, 31, hexc("#5a4a30"))
    stalks = ((8, 10), (16, 5), (24, 10)) if b != 0 else ((6, 11), (12, 6), (20, 6), (26, 11))
    for x, top_y in stalks:
        c.line([(x, 28), (x, top_y + 3)], stem, 2 if b == 0 else 1)
        for k in range(5):  # umbrella of tiny white flowers
            a = math.pi + k * math.pi / 4
            fx, fy = x + math.cos(a) * 4, top_y + 3 + math.sin(a) * 3
            c.line([(x, top_y + 3), (fx, fy)], stem)
            c.ellipse(fx, fy, 1.4, 1.4, hexc("#f4f4ec"))
        for y in (16, 22):
            c.px(x + 1, y, hexc("#9a3a5a"))  # purple stem spots
    pc_mark(c, 16, 25, p, 1.3)
    return (16, 4)


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
