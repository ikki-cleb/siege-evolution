"""World 1 (Backyard Bugs): bugs defend the anthill. Bugs have faces; plants and
objects don't. Attack styles come from Immune Defense's slots (draw_sprites.py).

Redesigned to look bigger and tougher (the user found the first designs
flimsy): every unit draws its own two evolutions (p["branch"] 0 = power,
1 = utility), and draw_sprites.py scales evolutions up. Faces stay cute;
gadgets (lens, sprinkler, lantern) get more detail instead of menace.
"""
import math

from .hefty import (ant, antennae, beetle, glow, head, heavy_legs, mandibles, pc_mark, puffs, ring, shell,
                    spider, tier, wings)
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, bug, legs, phase

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True

GREY = hexc("#9a9aa2")
BARK = hexc("#7a5030")
LEAF = hexc("#4a8a3a")


# --- Fortress -------------------------------------------------------------------

def pebble_wall(c, p):
    b = tier(p)
    if b == 0:  # Cobblestone: squared stones set in mortar
        c.block(3, 12, 29, 30, hexc("#6a6a72"))
        for row, y in enumerate((13, 19, 25)):
            for x in range(3 - row % 2 * 4, 29, 8):
                c.block(max(4, x), y, min(28, x + 7), y + 5, hexc("#a4a4ac") if (x + row) % 3 else hexc("#8e8e98"))
    else:
        stones = ((8, 24, 6), (22, 24, 6.5), (15, 15, 6.5), (25, 14, 4.2), (6, 14, 4.2), (15, 26, 4))
        for x, y, r in stones:
            col = shade(GREY, ((x * 7 + y) % 5 - 2) * 0.04)
            c.blob(x, y, r, r * 0.85, col)
            c.px(x - r * 0.3, y - r * 0.3, shade(col, 0.25))
        if b == 1:  # Thorned Pebble: thorns poking out between the stones
            for x, y, dx, dy in ((4, 20, -3, -2), (28, 19, 3, -2), (11, 9, -1, -4), (20, 8, 1, -4), (16, 30, 0, 0)):
                c.poly([(x - 1.5, y), (x + 1.5, y), (x + dx, y + dy)], hexc("#6a8a3a"))
    pc_mark(c, 16, 27 if b != 0 else 28, p)
    return (16, 9)


def stag_beetle(c, p):
    b = tier(p)
    body = hexc("#7a3a20") if b != 0 else hexc("#4a2a1c")
    top = beetle(c, p, body, hexc("#5a2a18"), rx=10.5 if b == 0 else 9.5, ry=9 if b == 0 else 8,
                 spots=p["pc"] if b is None else None)
    x, y = top
    jaw = hexc("#3a1a10")
    open_ = 1.2 if p.get("act") == "fire" else 1.0
    if b == 0:  # Goliath: huge armored jaws and shoulder plates
        mandibles(c, x, y + 4, jaw, 1.25 * open_)
        for side in (-1, 1):
            c.poly([(16 + side * 6, 14), (16 + side * 12, 15), (16 + side * 10, 20)], shade(body, 0.12))
        pc_mark(c, 16, 22, p, 2)
    elif b == 1:  # Sweeping: long curved jaws that span the tile
        mandibles(c, x, y + 4, jaw, 1.0 * open_, wide=True)
        pc_mark(c, 16, 22, p)
    else:
        mandibles(c, x, y + 4, jaw, 0.95 * open_)
    return (x, y - 5)


def bombardier_beetle(c, p):
    b = tier(p)
    top = beetle(c, p, hexc("#e07030"), hexc("#2a2a30"), spots=hexc("#2a2a30"))
    nozzle = hexc("#3a3a42")
    if b == 0:  # Blast: twin smoking vents
        for x in (11, 21):
            c.rect(x - 2, 26, x + 2, 30, nozzle)
            puffs(c, [(x, 31 - phase(p) % 2, 2)], hexc("#e8e0d8", 200))
    elif b == 1:  # Long-Shot: a long barrel
        c.rect(14, 25, 18, 31, nozzle)
        c.rect(13, 30, 19, 31, shade(nozzle, 0.2))
    else:
        c.rect(14, 26, 18, 29, nozzle)
    pc_mark(c, 16, 20, p)
    return top


def moss_clump(c, p):
    b = tier(p)
    moss = hexc("#5aa040") if b != 0 else hexc("#3f7f30")
    if b == 0:  # Dense: a mossy boulder
        c.blob(16, 22, 13, 9, GREY)
    clumps = ((8, 23, 6), (16, 18, 7), (24, 23, 6), (11, 27, 5), (21, 27, 5), (16, 25, 6))
    for x, y, r in clumps:
        c.blob(x, y - (3 if b == 0 else 0), r, r * 0.85, moss)
    for x, y in ((10, 19), (18, 15), (23, 21), (14, 24), (20, 25)):
        c.px(x, y - (3 if b == 0 else 0), shade(moss, 0.25))
    if b == 1:  # Lush: ferns and little flowers
        for x, col in ((7, "#f0d040"), (16, "#f080b0"), (25, "#f0d040")):
            c.line([(x, 20), (x - 1, 12)], hexc("#3a7a2a"))
            c.ellipse(x - 1, 11, 1.8, 1.8, hexc(col))
    pc_mark(c, 24, 27, p)
    return (16, 10)


def praying_mantis(c, p):
    b = tier(p)
    green = hexc("#7ac850") if b != 1 else hexc("#f0a0c8")
    dark = shade(green, -0.25)
    up = -3 if p.get("act") == "fire" else 0
    heavy_legs(c, 16, 26, 3, 2, dark, p, 6, 3)
    c.ellipse(16, 25, 5, 6.5, shade(green, -0.1))  # abdomen
    c.rect(14, 14, 18, 21, green)  # thorax
    for side in (-1, 1):  # raptor arms
        arm = [(16 + side * 3, 17), (16 + side * 9, 12 + up), (16 + side * 7, 6 + up)]
        c.line(arm, dark, 3 if b == 0 else 2)
        if b == 0:  # Giant: spiked arms
            for t in (0.4, 0.75):
                sx_ = arm[1][0] + (arm[2][0] - arm[1][0]) * t
                sy_ = arm[1][1] + (arm[2][1] - arm[1][1]) * t
                c.px(sx_ - side, sy_, WHITE)
        if b == 1:  # Orchid: petal flaps on the legs
            c.ellipse(16 + side * 9, 13 + up, 3, 2, shade(green, 0.15))
    c.poly([(10, 13), (22, 13), (16, 20)], green)  # triangle head
    c.eyes(16, 14, 3, p.get("mood", "calm"), 2)
    if b == 1:
        c.ellipse(16, 27, 3, 2, shade(green, 0.2))
    pc_mark(c, 16, 25, p)
    return (16, 6)


def tree_stump(c, p):
    b = tier(p)
    bark = BARK if b != 0 else hexc("#8a8a90")
    for side in (-1, 1):  # roots
        c.poly([(16 + side * 8, 24), (16 + side * 14, 30), (16 + side * 6, 30)], shade(bark, -0.1))
    c.block(6, 13, 26, 30, bark)
    for x in (9, 14, 19, 23):
        c.line([(x, 17), (x + 0.5, 28)], shade(bark, -0.2))
    top_col = hexc("#d8b078") if b != 0 else hexc("#b8b8c0")
    c.ellipse(16, 13, 10, 4, top_col)
    c.ellipse(16, 13, 6.5, 2.6, shade(top_col, -0.12))
    c.ellipse(16, 13, 3, 1.2, shade(top_col, -0.25) if p.get("act") == "idle" else p["pc"])
    if b == 0:  # Petrified: stone cracks
        c.line([(9, 18), (12, 22), (10, 26)], hexc("#5a5a62"))
        c.line([(21, 16), (19, 21), (22, 25)], hexc("#5a5a62"))
    if b == 1:  # Thorny: thorny branches
        for x, y, dx in ((6, 16, -5), (26, 18, 5), (8, 24, -5), (24, 25, 5)):
            c.line([(x, y), (x + dx, y - 3)], hexc("#5a3a20"), 2)
            c.px(x + dx * 0.6, y - 3.5, hexc("#d8d0b0"))
    pc_mark(c, 22, 26, p)
    return (16, 9)


# --- Swarm --------------------------------------------------------------------

def twig_wall(c, p):
    b = tier(p)
    wood = hexc("#8a6038")
    for y, tilt in ((14, 2), (19, -2), (24, 1), (28, -1)):
        c.line([(3, y), (29, y + tilt)], wood, 3)
        c.line([(3, y - 1), (29, y + tilt - 1)], shade(wood, 0.2))
        c.px(29, y + tilt, shade(wood, -0.3))
    if b == 0:  # Twig Bundle: tied with twine
        for x in (9, 23):
            c.rect(x, 11, x + 2, 30, hexc("#d8c890"))
    if b == 1:  # Bramble: thorns and berries
        for x, y in ((6, 12), (14, 16), (22, 11), (26, 21), (10, 22), (18, 27)):
            c.px(x, y, hexc("#e8e0c0"))
        for x, y in ((12, 11), (25, 26)):
            c.ellipse(x, y, 1.6, 1.6, hexc("#5a2a6a"))
    pc_mark(c, 22, 11, p)
    return (16, 11)


def worker_ant(c, p):
    b = tier(p)
    if b == 0:  # Fire Ant: bright red, big jaws
        top = ant(c, p, hexc("#d8402a"), size=1.15, head_size=1.05)
        mandibles(c, top[0], top[1] + 7, hexc("#5a1a10"), 0.9)
    elif b == 1:  # Scout Ant: lean, long antennae
        top = ant(c, p, hexc("#a03a2a"), size=1.05)
        antennae(c, top[0], top[1] + 1, OUTLINE, 9, 6, tips=p["pc"])
    else:
        top = ant(c, p, hexc("#a03a2a"), size=1.1)
        antennae(c, top[0], top[1] + 1, OUTLINE, 5, 4)
    pc_mark(c, 16, 26, p, 1.4)
    return top


def acid_ant(c, p):
    b = tier(p)
    top = ant(c, p, hexc("#5a9a3a"), size=1.1 if b != 0 else 1.15)
    sac = hexc("#b8f060")
    if b == 0:  # Volley Ant: a swollen acid sac, dripping
        c.ellipse(16, 26, 5, 4, sac)
        c.px(16, 31, sac)
    else:
        c.ellipse(16, 26, 3.4, 2.8, sac)
    if b == 1:  # Sentry: tall antennae with lookout tips
        antennae(c, top[0], top[1] + 1, OUTLINE, 9, 5, tips=p["pc"])
    else:
        antennae(c, top[0], top[1] + 1, OUTLINE, 5, 4)
    return top


def honeybee(c, p):
    b = tier(p)
    gold = hexc("#f0c040") if b != 0 else hexc("#f0a020")
    wings(c, p, 16, 13, 5 if b != 1 else 6.5, 3.5 if b != 1 else 4.5, hexc("#d8ecff", 200), 8)
    shell(c, 16, 21, 9.5, 8.5, gold, seam=False)
    for y in (18, 22.5, 26.5):
        c.rect(7.5, y, 24.5, y + 1.6, hexc("#3a2a20"))
    stinger = 4.5 if b == 0 else 3
    c.poly([(14.5, 28.5), (17.5, 28.5), (16, 28.5 + stinger)], hexc("#2a2a20"))
    head(c, p, 16, 10, 5, hexc("#3a2a20"))
    antennae(c, 16, 6, OUTLINE, 4, 4)
    if b == 1:  # Buzzing: motion lines
        for y in (9, 13):
            c.line([(2, y), (5, y)], WHITE)
            c.line([(27, y), (30, y)], WHITE)
    pc_mark(c, 16, 21, p)
    return (16, 4)


def bullet_ant(c, p):
    b = tier(p)
    if b == 0:  # Major: a huge armored head
        top = ant(c, p, hexc("#2a2228"), size=1.1, head_size=1.3, stinger=p["pc"])
        mandibles(c, top[0], top[1] + 9, hexc("#5a4a50"), 1.1)
    elif b == 1:  # Hunting Ant: long legs, lean
        heavy_legs(c, 16, 21, 5, 2, hexc("#6a6070"), p, 9, 5)
        top = ant(c, p, hexc("#2a2228"), size=1.0, stinger=p["pc"])
    else:
        top = ant(c, p, hexc("#2a2228"), size=1.1, stinger=p["pc"])
        mandibles(c, top[0], top[1] + 7, hexc("#5a4a50"), 0.8)
    return top


def sap_blob(c, p):
    b = tier(p)
    amber = hexc("#e0a030", 240) if b != 0 else hexc("#b87020", 245)
    if b == 1:  # Spreading: a wide puddle under it
        c.ellipse(16, 28, 14, 3.5, shade(amber, -0.1))
    c.ellipse(16, 22, 12, 9, shade(amber, -0.2))
    c.ellipse(15, 21, 11, 8, amber)
    c.ellipse(11, 17, 3, 1.8, shade(amber, 0.3))
    c.ellipse(19, 23, 2.5, 1.8, hexc("#5a3a20", 200))  # a trapped bug
    for x in (7, 23):
        c.rect(x, 26, x + 2, 31 - (x % 3), amber)
    pc_mark(c, 14, 24, p)
    return (16, 12)


# --- Precision ------------------------------------------------------------------

def acorn_shell(c, p):
    b = tier(p)
    if b == 1:  # Chestnut Burr: a spiky shell
        c.blob(16, 20, 11, 10, hexc("#7a8a30"))
        for k in range(16):
            a = k * math.tau / 16
            c.line([(16 + math.cos(a) * 10, 20 + math.sin(a) * 9), (16 + math.cos(a) * 14, 20 + math.sin(a) * 12.5)],
                   hexc("#a0b048"))
        c.ellipse(16, 19, 5, 4, hexc("#8a5a30"))
    elif b == 0:  # Walnut: a big wrinkled shell
        shell(c, 16, 20, 12, 10.5, hexc("#a87a48"))
        for y in (15, 20, 25):
            c.line([(7, y), (12, y - 2), (16, y), (20, y - 2), (25, y)], hexc("#7a5030"))
    else:
        c.blob(16, 22, 10.5, 9, hexc("#b07840"))
        c.ellipse(16, 14, 11.5, 5.5, hexc("#6a4a28"))
        for x in range(7, 26, 3):
            for y in (12, 15):
                c.px(x + (y % 2), y, hexc("#8a6038"))
        c.rect(15, 6, 17, 10, hexc("#5a3a20"))
    pc_mark(c, 16, 26, p)
    return (16, 7)


def spitting_spider(c, p):
    b = tier(p)
    top = spider(c, p, hexc("#c09060"), r=8 if b != 0 else 8.5, fuzz=hexc("#d8b080"))
    if b == 0:  # Venom Spitter: dripping green fangs
        for side in (-1, 1):
            c.line([(16 + side * 2, 23), (16 + side * 1.5, 26)], WHITE)
        c.px(16.5, 27, hexc("#90e050"))
        c.px(14.5, 27.5, hexc("#90e050"))
    if b == 1:  # Sharpshooter: a red targeting eye
        c.ellipse(16, 13.5, 2, 2, hexc("#e03030"))
        c.px(16, 13.5, WHITE)
    pc_mark(c, 16, 24, p)
    return top


def firefly(c, p):
    b = tier(p)
    lit = p.get("act") != "idle"
    if b == 0:  # Bright: a huge glow around the tail (drawn first)
        glow(c, 16, 26, 10, hexc("#f8f080"))
    wings(c, p, 16, 14, 5, 3.5, hexc("#c8d0d8", 200), 8)
    body = hexc("#5a4a3a")
    shell(c, 16, 19, 8.5, 7, body)
    lamp = hexc("#f0f070") if not lit else p["pc"]
    lamp_r = 6 if b == 0 else 4.5
    c.ellipse(16, 26, lamp_r, lamp_r * 0.7, lamp)
    c.ellipse(15, 25, lamp_r * 0.4, lamp_r * 0.25, WHITE)
    head(c, p, 16, 10, 4.8, hexc("#c04030"))
    if b == 1:  # Signal: lights on the antennae
        antennae(c, 16, 6, OUTLINE, 6, 5, tips=hexc("#f0f070"))
    else:
        antennae(c, 16, 6, OUTLINE, 4, 4)
    return (16, 4)


def assassin_bug(c, p):
    b = tier(p)
    body = hexc("#8a5a30")
    if b == 1:  # Patrol: long stilt legs
        heavy_legs(c, 16, 20, 6, 3, shade(body, -0.4), p, 9, 3.5)
    top = beetle(c, p, body, hexc("#5a3820"), rx=8.5, ry=8.5, seam=True)
    c.line([(16, top[1] + 2), (16, top[1] - 4 - (p.get("act") == "fire") * 2)], OUTLINE, 2)  # beak
    if b == 0:  # Masked Hunter: a bandit mask
        c.rect(11, top[1] + 3.5, 21, top[1] + 5.5, hexc("#2a1a14"))
        c.eyes(16, top[1] + 4.5, 2.4, p.get("mood", "calm"), 2)
    for x in (9, 23):  # shoulder spikes
        c.poly([(x - 1.5, 15), (x + 1.5, 15), (x + (x - 16) * 0.3, 11)], shade(body, -0.25))
    pc_mark(c, 16, 22, p)
    return top


def jumping_spider(c, p):
    b = tier(p)
    body = hexc("#3a3a40")
    if b == 1:  # Quick: speed lines
        for y in (24, 27):
            c.line([(1, y), (5, y)], WHITE)
    top = spider(c, p, body, r=8.5 if b == 0 else 7.5, eyes4=True,
                 fuzz=hexc("#7a7a88") if b == 0 else None)
    c.rect(11, 23, 21, 24.5, p["pc"])
    return top


def glowworm_lantern(c, p):
    b = tier(p)
    lit = hexc("#f0e080") if p.get("act") == "idle" else p["pc"]
    if b == 1:  # Tall Lantern: up on a post
        c.rect(15, 22, 17, 31, hexc("#5a5a60"))
        c.rect(11, 29, 21, 31, hexc("#5a5a60"))
        ox, oy, h = 0, -6, 18
    else:
        ox, oy, h = 0, 0, 20
    w = 8 if b == 0 else 7
    glow(c, 16, 18 + oy, 12 if b == 0 else 9, hexc("#fff0a0"), 60)
    c.rect(13, 5 + oy, 19, 8 + oy, hexc("#4a4a50"))
    c.ellipse(16, 4 + oy, 2, 1.4, hexc("#4a4a50"))
    c.block(16 - w, 8 + oy, 16 + w, 8 + oy + h, hexc("#6a5a40"))
    c.rect(16 - w + 2, 10 + oy, 16 + w - 2, 6 + oy + h, lit)
    for x in (16 - w + 2, 16, 16 + w - 3):  # frame bars
        c.rect(x, 10 + oy, x + 1, 6 + oy + h, hexc("#6a5a40"))
    c.ellipse(16, 17 + oy, 3, 2, hexc("#c8e070"))  # the glowworm inside
    c.px(15, 16 + oy, OUTLINE)
    c.px(17, 16 + oy, OUTLINE)
    if b == 0:  # Blazing: flames licking out of the top
        c.poly([(13, 8 + oy), (16, 2 + oy - phase(p) % 2), (19, 8 + oy)], hexc("#f08030"))
    return (16, 4 + oy)


# --- Control --------------------------------------------------------------------

def spiderweb(c, p):
    b = tier(p)
    silk = hexc("#eef0f8", 230)
    c.line([(2, 4), (2, 31)], BARK, 2)  # the twigs it hangs between
    c.line([(30, 4), (30, 31)], BARK, 2)
    spokes = 10 if b == 0 else 8
    for a in range(spokes):
        ang = a * math.tau / spokes
        c.line([(16, 18), (16 + math.cos(ang) * 13.5, 18 + math.sin(ang) * 12.5)], silk)
    for r in ((3.5, 6.5, 9.5, 12.5) if b == 0 else (4, 8, 12)):
        pts = [(16 + math.cos(a * math.tau / spokes) * r, 18 + math.sin(a * math.tau / spokes) * r * 0.92)
               for a in range(spokes + 1)]
        c.line(pts, silk)
    if b == 1:  # Sticky: glistening glue drops
        for x, y in ((9, 13), (22, 12), (25, 22), (8, 24), (16, 28), (19, 16)):
            c.ellipse(x, y, 1.6, 1.6, hexc("#c8f0ff"))
            c.px(x - 0.5, y - 0.5, WHITE)
    pc_mark(c, 16, 18, p)
    return (16, 5)


def stink_bug(c, p):
    b = tier(p)
    green = hexc("#6a9a50")
    if b is not None:  # a stink cloud
        cloud = hexc("#c8e070", 120 if b == 1 else 170)
        for x, y, r in ((6, 26, 4), (26, 25, 4.5), (9, 30, 3), (23, 30, 3)):
            c.ellipse(x - (phase(p) % 2), y, r, r * 0.8, cloud)
    heavy_legs(c, 16, 22, 9, 3, shade(green, -0.4), p, 4)
    c.poly([(16, 9), (27, 17), (23, 30), (9, 30), (5, 17)], shade(green, -0.2))  # shield shape
    c.poly([(16, 10), (26, 17), (22, 29), (10, 29), (6, 17)], green)
    c.poly([(16, 17), (21, 24), (11, 24)], shade(green, 0.12))
    if b == 1:  # Wafting: wings spread
        wings(c, p, 16, 18, 4, 6, hexc("#d0e0c0", 170), 11)
    head(c, p, 16, 13, 4.5, shade(green, -0.15))
    pc_mark(c, 16, 25, p, 2)
    return (16, 8)


def spittlebug(c, p):
    b = tier(p)
    foam = hexc("#f4f8fc")
    piles = ((7, 26, 4.5), (25, 26, 4.5), (12, 29, 4), (20, 29, 4))
    if b == 0:  # Froth: a huge foam pile
        piles = piles + ((4, 21, 3.5), (28, 21, 3.5), (16, 30, 4.5))
    for x, y, r in piles:
        c.blob(x, y, r, r * 0.8, foam)
    if b == 1:  # Long: long hind legs
        heavy_legs(c, 16, 22, 7, 1, hexc("#5a7a2a"), p, 8)
    top = beetle(c, p, hexc("#a0c040"), rx=8, ry=7, spots=None)
    pc_mark(c, 16, 21, p)
    return top


def magnifying_glass(c, p):
    b = tier(p)
    burning = p.get("act") != "idle"
    r = 9.5 if b == 1 else 8
    c.line([(21, 22), (29, 30)], hexc("#6a4020"), 4)  # wooden handle
    c.line([(22, 22), (29, 29)], hexc("#8a5a30"), 1)
    c.rect(19, 19, 23, 23, hexc("#c8a040"))  # brass collar
    c.ellipse(13, 14, r + 1.5, r + 1.5, hexc("#c8a040"))  # brass rim
    c.ellipse(13, 14, r + 0.5, r + 0.5, hexc("#8a6a20"))
    c.ellipse(13, 14, r - 0.5, r - 0.5, hexc("#cfeaf8") if not burning else hexc("#fff4b0"))
    c.ellipse(10, 11, 2.5, 1.5, WHITE)
    c.ellipse(16, 17, 1, 1, WHITE)
    if b == 0:  # Focused: a bright sunbeam point below the lens
        glow(c, 13, 27, 4, hexc("#ffd040"), 120)
        c.ellipse(13, 27, 1.6, 1.6, hexc("#fff8c0"))
    pc_mark(c, 26, 27, p, 1.4)
    return (13, 4)


def click_beetle(c, p):
    b = tier(p)
    top = beetle(c, p, hexc("#3a3040"), spots=shade(p["pc"], 0.1))
    if p.get("act") == "fire" or b == 0:  # Thunder: lightning crackles
        for x, d in ((7, -1), (25, 1)):
            c.line([(x, 9), (x + d * 2, 6), (x, 4), (x + d * 2, 1)], hexc("#ffe060"))
    if b == 1:  # Shockwave: rings around it
        ring(c, 16, 20, 14.5, 11.5, hexc("#ffe060"))
        ring(c, 16, 20, 12.5, 10, hexc("#fff0a0"), 22)
    return top


def sprinkler(c, p):
    b = tier(p)
    spin = phase(p) if p.get("act") != "idle" else 0
    c.ellipse(16, 28, 11, 3.5, hexc("#3a6a2a"))  # wet grass
    c.ellipse(16, 27, 7, 2.6, hexc("#5a8a3a"))
    c.rect(13, 13, 19, 28, hexc("#9aa0a8"))  # post
    c.rect(13, 13, 14, 28, hexc("#c8ccd4"))
    c.rect(11, 24, 21, 28, hexc("#c84a3a"))  # red base
    arm = 11 if b == 1 else 8
    c.rect(16 - arm, 11, 16 + arm, 14, p["pc"])  # spinning arm
    c.ellipse(16, 12.5, 3, 3, hexc("#707880"))
    jets = (16 - arm, 16 + arm)
    for x in jets:
        c.ellipse(x, 10 - spin, 1.6, 1.6, hexc("#80c8f0"))
        c.px(x, 7 - spin, hexc("#c0e8ff"))
    if b == 0:  # Power: a second head and stronger jets
        c.rect(14, 4, 18, 11, hexc("#9aa0a8"))
        for x in (11, 21):
            c.line([(x, 5), (x - (16 - x) * 0.4, 1)], hexc("#80c8f0"))
    return (16, 6)


# --- Toxin ----------------------------------------------------------------------

def nettle_patch(c, p):
    b = tier(p)
    leaf = LEAF if b != 0 else hexc("#2f6a2a")
    spots = ((8, 22), (16, 16), (24, 22), (11, 27), (21, 27), (16, 24))
    if b == 0:  # Dense: more, bigger leaves
        spots = spots + ((5, 16), (27, 16), (16, 9))
    for x, y in spots:
        c.poly([(x, y - 7), (x - 4, y), (x, y + 3), (x + 4, y)], leaf)
        c.line([(x, y - 6), (x, y + 2)], shade(leaf, -0.25))
        for s_ in (-1, 1):
            c.px(x + s_ * 3, y - 3, hexc("#e8f0d0"))
            if b == 1:  # Stinging: long white hairs
                c.px(x + s_ * 4.5, y - 4.5, WHITE)
    pc_mark(c, 16, 28, p)
    return (16, 8)


def paper_wasp(c, p):
    b = tier(p)
    gold = hexc("#e0b030") if b != 0 else hexc("#f0c818")
    wings(c, p, 16, 13, 5.5, 3.5, hexc("#d0d8e8", 200), 8)
    c.ellipse(16, 23, 7.5, 8.5, shade(gold, -0.25))
    c.blob(16, 22.5, 7, 8, gold)
    for y in (19, 23, 27):
        c.rect(9.5, y, 22.5, y + (2 if b == 0 else 1.4), hexc("#2a1a0a"))
    sting = 6 if b == 1 else 3.5
    c.poly([(14.8, 30), (17.2, 30), (16, 30 + sting)], OUTLINE)
    c.blob(16, 13.5, 3.5, 3, shade(gold, -0.1))  # thorax
    head(c, p, 16, 8.5, 4.5, hexc("#3a2a1a"))
    antennae(c, 16, 5, OUTLINE, 4, 4)
    pc_mark(c, 16, 21, p)
    return (16, 3)


def blister_beetle(c, p):
    b = tier(p)
    body = hexc("#3a8a8a") if b != 0 else hexc("#2a9a7a")
    if b == 1:  # Misting: a mist cloud
        for x, y in ((5, 24), (27, 24), (16, 31)):
            c.ellipse(x, y, 4, 3, hexc("#a0f0d0", 110))
    top = beetle(c, p, body, hexc("#2a5a6a"), spots=p["pc"])
    if b == 0:  # Caustic: dripping blisters
        for x in (9, 23):
            c.ellipse(x, 27, 1.6, 2.2, hexc("#c0f060"))
    return top


def toxic_mushroom(c, p):
    b = tier(p)
    puff = 1 if p.get("act") == "fire" else 0
    stem = hexc("#f0e8d8")
    c.rect(12, 18, 20, 30, stem)
    c.rect(12, 18, 13, 30, shade(stem, 0.1))
    c.ellipse(16, 21, 6, 1.5, shade(stem, -0.15))  # the ring on the stem
    if b == 1:  # Spore Puff: a round puffball with a cloud
        c.blob(16, 14 - puff, 11, 9, hexc("#e8dcc0"))
        for x, y in ((10, 6), (16, 3), (22, 6)):
            c.ellipse(x, y - puff * 2, 2.2, 2.2, hexc("#c8e070", 170))
    else:
        cap = hexc("#d03a3a") if b is None else hexc("#c8d8a0")  # Deathcap: pale green-white
        c.ellipse(16, 16 - puff, 13, 8.5, shade(cap, -0.2))
        c.ellipse(16, 15 - puff, 12.5, 8, cap)
        c.ellipse(11, 11 - puff, 4, 2, shade(cap, 0.2))
        if b is None:
            for x, y in ((10, 13), (17, 10), (22, 15), (14, 17)):
                c.ellipse(x, y - puff, 1.8, 1.5, WHITE)
    pc_mark(c, 16, 26, p)
    return (16, 6)


def scorpion(c, p):
    b = tier(p)
    body = hexc("#a06a3a") if b != 0 else hexc("#d8b040")
    sting = -2 if p.get("act") == "fire" else 0
    tail = [(16, 26), (23, 29), (28, 23), (27, 15), (24, 10 + sting)]
    if b == 1:  # Long-Tail: an extra-long tail
        tail = [(16, 26), (24, 30), (30, 23), (29, 12), (25, 5 + sting)]
    c.line(tail, shade(body, -0.15), 3)
    tip = tail[-1]
    c.poly([(tip[0] - 2, tip[1]), (tip[0] + 2, tip[1]), (tip[0], tip[1] - 4)], p["pc"])
    claw = 4.5 if b == 0 else 3.2
    for side in (-1, 1):  # big pincers
        c.line([(16 + side * 5, 17), (16 + side * 9, 11)], shade(body, -0.2), 2)
        c.ellipse(16 + side * 10, 9, claw, claw * 0.8, shade(body, -0.1))
        c.line([(16 + side * 10, 9), (16 + side * 12, 6)], OUTLINE)
    top = beetle(c, p, body, shade(body, -0.2), rx=7.5, ry=6.5, y=21)
    return top


def poison_ivy(c, p):
    b = tier(p)
    leaf = hexc("#3a7a2a") if b != 1 else hexc("#6ab03a")
    if b == 1:  # Virulent: a sickly glow behind the leaves
        for x, y in ((9, 21), (23, 21), (16, 13)):
            glow(c, x, y, 7, hexc("#c8f070"))
    if b == 0:  # Woody: a thick vine trunk
        c.line([(16, 30), (15, 20), (17, 10)], hexc("#6a4a28"), 3)
    c.rect(3, 27, 29, 31, hexc("#5a4a30"))
    for cx, cy in ((9, 21), (23, 21), (16, 13)):
        for a in (-0.9, 0.9, math.pi):
            lx, ly = cx + math.cos(a - math.pi / 2) * 3.5, cy + math.sin(a - math.pi / 2) * 3.5
            c.ellipse(lx, ly, 3.6, 2.6, leaf)
            c.px(lx, ly, shade(leaf, 0.2))
        c.px(cx, cy, hexc("#9ad070"))
    if b == 1:  # Virulent: glowing spores
        for x, y in ((5, 12), (27, 11), (16, 5)):
            c.px(x, y, hexc("#e8ff90"))
    pc_mark(c, 16, 25, p)
    return (16, 7)


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
