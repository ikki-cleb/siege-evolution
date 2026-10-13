"""Birthday Bash: party gear against party crashers.

Redesigned (see world_backyard.py): bigger, richly detailed party gear
(ribbons, sprinkles, stripes, shine). The party "characters" (ice cream
cake, balloons, disco ball, jelly, sour candy, lemon, moldy cake) have cute
faces; the rest are objects. Power evolutions are bigger and more over the
top (more tiers, gold trim, sparkle); utility evolutions get a visible
add-on that matches their ability (longer barrels, spikes, pumps, extra
nozzles). The clown and the goo enemies have faces; toys don't.
"""
import math

from .hefty import glow, pc_mark, puffs, ring, tier
from .kit import OUTLINE, hexc, shade
from .parts import WHITE, phase, robot

# draw_sprites.py: these designs draw their own evolutions.
TIERED = True

GOLD = hexc("#ffd23c")
SKY = hexc("#4ac0e8")
PINK = hexc("#ff7ac8")
LIME = hexc("#7fe08a")
RED = hexc("#ff5a5a")
PURPLE = hexc("#a070e0")
SILVER = hexc("#d0d4dc")
WOOD = hexc("#c89060")
PARTY = (PINK, GOLD, SKY, LIME, RED, PURPLE)


def pface(c, x, y, p, gap=3, mood=None):
    """A cute face for the living party characters."""
    c.eyes(x, y, gap, mood or p.get("mood", "calm"), 2)
    c.mouth(x, y + 3, "open" if p.get("act") == "fire" else "smile", 3)


def sprinkles(c, x0, y0, x1, y1, count, seed=0):
    """Little colored sprinkle dashes scattered over an area."""
    for k in range(count):
        t = (k * 7 + seed * 3) % 11 / 11
        u = (k * 5 + seed) % 7 / 7
        x = x0 + (x1 - x0) * ((k + 0.5) / count)
        y = y0 + (y1 - y0) * (0.15 + 0.7 * ((t + u) % 1))
        c.line([(x, y), (x + 1, y + (1 if k % 2 else -1))], PARTY[(k + seed) % len(PARTY)])


def star(c, x, y, r, color):
    """A five-pointed star."""
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, color)


def bow(c, x, y, size, color):
    """A ribbon bow (two loops and a knot)."""
    c.blob(x - size, y, size, size * 0.7, color, shine=False)
    c.blob(x + size, y, size, size * 0.7, color, shine=False)
    c.ellipse(x - size, y, size * 0.4, size * 0.3, shade(color, -0.3))
    c.ellipse(x + size, y, size * 0.4, size * 0.3, shade(color, -0.3))
    c.ellipse(x, y, size * 0.45, size * 0.45, shade(color, 0.15))


def wheel(c, x, y, r, color=None):
    c.ellipse(x, y, r, r, color or hexc("#3a3040"))
    c.ellipse(x, y, r * 0.45, r * 0.45, GOLD)


def spike(c, x, y, angle, length, color=SILVER):
    """A shiny cone spike pointing at `angle` (radians)."""
    dx, dy = math.cos(angle), math.sin(angle)
    nx, ny = -dy * 1.6, dx * 1.6
    c.poly([(x + nx, y + ny), (x - nx, y - ny), (x + dx * length, y + dy * length)], color)


# --- Fortress -------------------------------------------------------------------

def gift_box(c, p):
    b = tier(p)
    box = p["pc"]
    boxes = ((16, 30, 10, 15),) if b != 0 else ((16, 31, 12, 12), (16, 19, 8, 8))
    if b == 1:  # Prickly: silver spikes poke out of the box
        for x, y, a in ((5, 19, math.pi), (5, 26, math.pi), (27, 19, 0), (27, 26, 0),
                        (9, 15, -2.3), (23, 15, -0.85)):
            spike(c, x, y, a, 5)
    for x, y, w, h in boxes:
        c.block(x - w, y - h, x + w, y, box)
        c.rect(x - w, y - h, x + w, y - h + 2, shade(box, 0.18))  # lid
        for k in range(3):  # polka dots
            c.ellipse(x - w + 3 + k * (w - 1), y - h * 0.3, 1.2, 1.2, shade(box, 0.3))
        c.rect(x - 1.5, y - h, x + 1.5, y, GOLD)  # ribbon
        c.rect(x - w, y - h * 0.55 - 1, x + w, y - h * 0.55 + 1, GOLD)
    top = boxes[-1][1] - boxes[-1][3]
    if b == 0:  # Big: a huge gold bow with tails
        c.line([(16, top), (11, top + 6)], GOLD, 2)
        c.line([(16, top), (21, top + 6)], GOLD, 2)
        bow(c, 16, top - 2, 4.5, GOLD)
        star(c, 7, 22, 2.5, GOLD)
    else:
        bow(c, 16, top - 2, 3.5, GOLD)
    return (16, top - 5)


def party_mallet(c, p):
    b = tier(p)
    swing = -3 if p.get("act") == "fire" else 0
    w = 11 if b == 0 else (13 if b == 1 else 9)
    h = 6 if b == 0 else 5
    y = 10 + swing
    c.rect(15, y + h, 18, 31, WOOD)  # handle with a grip wrap
    for gy in (24, 27, 30):
        c.line([(15, gy), (17, gy - 1)], RED)
    c.block(16 - w, y - h, 16 + w, y + h, p["pc"])
    for k, sx in enumerate(range(int(16 - w) + 3, int(16 + w) - 1, 4)):  # candy stripes
        c.rect(sx, y - h, sx + 1.5, y + h - 1, PARTY[k % 3 + 1])
    for side in (-1, 1):  # end caps
        c.ellipse(16 + side * w, y, 1.5, h, shade(p["pc"], -0.25))
    if b == 0:  # Giant: gold bands and a star
        c.rect(16 - w, y - h, 16 + w, y - h + 1.5, GOLD)
        c.rect(16 - w, y + h - 2, 16 + w, y + h - 0.5, GOLD)
        star(c, 16, y, 3.5, GOLD)
    if b == 1:  # Wide: squeaky bellows on both ends
        for side in (-1, 1):
            for k in range(3):
                c.ellipse(16 + side * (w + 2 + k * 1.5), y, 1, h - k, (GOLD, WHITE)[k % 2])
    return (16, y - h)


def confetti_cannon(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    length = 16 if b == 1 else 11
    r = 5.5 if b == 0 else 4.5
    mx, my = 16 + 0.55 * length, 22 - length
    # barrel: angled up and to the right
    pts = [(10 - r * 0.8, 24 - r * 0.6), (10 + r * 0.8, 24 + r * 0.6),
           (mx + r * 0.8, my + r * 0.6), (mx - r * 0.8, my - r * 0.6)]
    c.poly(pts, p["pc"])
    for k in (0.35, 0.7):  # stripes
        x, y = 10 + (mx - 10) * k, 24 + (my - 24) * k
        c.line([(x - r * 0.8, y - r * 0.6), (x + r * 0.8, y + r * 0.6)], GOLD, 2)
    c.ellipse(mx, my, r * 0.8, r * 0.8, shade(p["pc"], -0.35))  # muzzle
    if b == 0:  # Mega: a gold muzzle ring
        c.ellipse(mx, my, r, r, GOLD)
        c.ellipse(mx, my, r * 0.6, r * 0.6, shade(p["pc"], -0.4))
    c.block(5, 24, 21, 29, hexc("#7a4a9a"))  # carriage
    wheel(c, 8, 28, 3.5 if b != 0 else 4)
    wheel(c, 18, 28, 3.5 if b != 0 else 4)
    if fire or b == 0:
        for k in range(6):  # confetti
            c.px(mx - 3 + k * 1.5, my - 3 - (k % 3) * 2, PARTY[k % len(PARTY)])
    return (mx, my - 2)


def balloon_arch(c, p):
    b = tier(p)
    pts = ((5, 27), (5, 19), (8, 12), (13, 8), (19, 8), (24, 12), (27, 19), (27, 27))
    r = 4.0 if b == 0 else 3.4
    if b == 1:  # Self-Inflating: a pump with a hose at the foot
        c.block(23, 23, 30, 31, hexc("#5a5a6a"))
        c.rect(25.5, 18, 27.5, 23, SILVER)
        c.rect(23, 16, 30, 18, RED)
        c.line([(23, 27), (18, 29), (12, 29), (8, 28)], hexc("#3a3a40"), 2)
    for i, (x, y) in enumerate(pts):
        col = (p["pc"], GOLD, SKY)[i % 3]
        if b == 0:  # Thick: a second ring of balloons behind
            c.blob(x + (1.5 if x < 16 else -1.5), y + 1, r * 0.8, r * 0.8, shade(col, -0.15))
        c.blob(x, y, r, r, col)
    c.ellipse(16, 30, 12, 1.5, shade(GOLD, -0.3))  # base weights
    c.blob(16, 7, r + 1.5, r + 1, PINK)  # the arch's face balloon on top
    pface(c, 16, 7, p, gap=2.5)
    return (16, 1)


def fireworks_launcher(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    crate = hexc("#3a3a58") if b != 0 else hexc("#5a2a2a")
    rockets = ((10, RED), (16, SKY), (22, GOLD)) if b != 0 else \
        ((7, RED), (12, SKY), (16, GOLD), (20, LIME), (25, PINK))
    tall = 6 if b == 1 else 0
    for x, col in rockets:
        top = 9 - tall - (3 if fire else 0) + (2 if b == 0 and x in (7, 25) else 0)
        c.rect(x - 1.8, top, x + 1.8, 22, col)
        c.rect(x - 1.8, top + 3, x + 1.8, top + 4, WHITE)
        c.poly([(x - 2.2, top), (x, top - 4), (x + 2.2, top)], shade(col, -0.25))
        if b == 1:  # Long: fins on tall rockets
            c.poly([(x - 1.8, 22), (x - 3.5, 22), (x - 1.8, 18)], shade(col, -0.3))
    c.block(5, 21, 27, 31, crate)
    c.rect(5, 24, 27, 25, p["pc"])
    if b == 0:  # Big: gold-trimmed crate with a star
        c.rect(5, 21, 27, 22, GOLD)
        star(c, 16, 27.5, 2.5, GOLD)
    else:
        c.line([(7, 27), (25, 27)], shade(crate, 0.3))
    return (16, 3 - tall)


def ice_cream_cake(c, p):
    b = tier(p)
    frost = WHITE if b != 0 else hexc("#d8f0ff")
    layers = ((16, 30, 12, 7, hexc("#f8d0e0")), (16, 23, 9, 7, hexc("#8a5030")))
    if b == 0:  # Frozen: bigger, icy blue layers
        layers = ((16, 31, 13, 8, hexc("#a8d8f0")), (16, 23, 10, 7, hexc("#d0ecff")))
    for x, y, w, h, col in layers:
        c.block(x - w, y - h, x + w, y, col)
        c.ellipse(x, y - h, w, 2.2, frost)
        for k in range(int(w // 2)):  # dripping frosting
            c.rect(x - w + 1 + k * 4, y - h, x - w + 2.5 + k * 4, y - h + 2 + k % 2 * 2, frost)
    if b == 1:  # Sprinkle Spike: giant sprinkles stuck in like spikes
        for x, a, col in ((5, -2.4, RED), (10, -2.0, SKY), (22, -1.1, LIME), (27, -0.7, GOLD), (16, -1.57, PINK)):
            spike(c, x, 18 if x != 16 else 13, a, 5, col)
    if b == 0:  # Frozen: icicles and a snowflake
        for x in (6, 11, 21, 26):
            c.poly([(x - 1, 24), (x + 1, 24), (x, 28)], hexc("#e8f8ff"))
        ring(c, 16, 9, 2.5, 2.5, WHITE, 8)
        c.ellipse(16, 9, 1, 1, WHITE)
    else:
        c.ellipse(16, 13, 2.2, 2.2, hexc("#e02040"))  # cherry
        c.line([(16, 11), (18, 8)], hexc("#3a8a3a"))
    sprinkles(c, 6, 25, 26, 29, 6, 1)
    pface(c, 16, 19, p)
    pc_mark(c, 25, 27, p, 1.2)
    return (16, 8)


# --- Swarm --------------------------------------------------------------------

def _cup(c, x, y, w, h, p):
    c.poly([(x - w, y - h), (x + w, y - h), (x + w * 0.72, y), (x - w * 0.72, y)], WHITE)
    for k in (-0.5, 0, 0.5):  # stripes in pack color
        c.line([(x + w * k, y - h + 1), (x + w * k * 0.72, y - 1)], p["pc"], 2)
    c.rect(x - w - 0.5, y - h - 1, x + w + 0.5, y - h + 1, shade(WHITE, -0.12))


def paper_cup(c, p):
    b = tier(p)
    if b == 0:  # Stacked Cups: a tower of cups
        for x, y in ((9, 31), (23, 31), (16, 20)):
            _cup(c, x, y, 6, 11, p)
        c.line([(18, 9), (21, 2)], RED, 2)
        return (20, 2)
    _cup(c, 16, 31, 9, 19, p)
    c.line([(18, 12), (22, 4), (25, 4)], (RED if b != 1 else SKY), 2)  # bendy straw
    c.ellipse(16, 12, 8, 1.6, hexc("#ff7a40"))  # soda
    if b == 1:  # Pointy: a spiky lid
        for x in range(7, 26, 3):
            c.poly([(x, 12), (x + 1.5, 6), (x + 3, 12)], SILVER)
    return (16, 6)


def party_blower(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    length = (19 if b == 1 else 14) if fire else 0
    c.block(10, 23, 22, 31, GOLD)  # mouthpiece
    c.rect(10, 26, 22, 27.5, p["pc"])
    if b == 0:  # Loud: a big flared horn bell on the mouthpiece
        c.poly([(9, 24), (23, 24), (19, 20), (13, 20)], PINK)
    if fire:  # unrolled straight up
        c.rect(14, 20 - length, 18, 24, p["pc"])
        for k in range(0, length, 4):
            c.rect(14, 20 - length + k, 18, 21 - length + k, WHITE)
        c.ellipse(16, 20 - length, 2.5, 2, shade(p["pc"], 0.2))
        tip = 18 - length
    else:  # curled up
        size = 9 if b == 1 else 8
        for k, col in enumerate((p["pc"], WHITE, p["pc"], WHITE, p["pc"])):
            c.ellipse(16, 14, size - k * 1.6, size - k * 1.6, col)
        tip = 14 - size
    if b == 0:
        c.px(10, 18, GOLD)
        c.px(22, 17, GOLD)
    return (16, tip)


def _pistol(c, x, y, p, size=1.0):
    s = size
    c.block(x - 9 * s, y - 4 * s, x + 7 * s, y + 3 * s, p["pc"])  # body
    c.rect(x - 12 * s, y - 2.5 * s, x - 9 * s, y + 0.5 * s, GOLD)  # nozzle
    c.block(x + 2 * s, y + 3 * s, x + 7 * s, y + 11 * s, shade(p["pc"], -0.15))  # grip
    c.rect(x - 1 * s, y + 3 * s, x + 1.5 * s, y + 6 * s, hexc("#3a3a40"))  # trigger
    c.ellipse(x - 2 * s, y - 5.5 * s, 3.5 * s, 2.5 * s, hexc("#4ac0e8", 220))  # water tank
    c.px(x - 3 * s, y - 6.5 * s, WHITE)


def water_pistol(c, p):
    b = tier(p)
    if b == 0:  # Twin: one in each "hand"
        _pistol(c, 15, 12, p, 0.85)
        _pistol(c, 19, 22, p, 0.85)
        return (5, 11)
    if b == 1:  # Super Soaker: long barrel, pump and a big tank
        c.block(4, 15, 28, 21, p["pc"])
        c.rect(1, 16, 4, 19, GOLD)
        c.block(20, 21, 26, 30, shade(p["pc"], -0.15))
        c.block(8, 21, 16, 24, hexc("#e0e0e8"))  # pump
        c.blob(17, 10, 7, 5, hexc("#4ac0e8", 230))  # big tank
        c.px(14, 8, WHITE)
        c.px(15, 8, WHITE)
        return (1, 17)
    _pistol(c, 17, 16, p, 1.1)
    return (4, 15)


def noisemaker(c, p):
    b = tier(p)
    spin = phase(p) % 2 if p.get("act") != "idle" else 0
    c.rect(15, 19, 18, 31, WOOD)
    c.line([(15, 23), (17, 22)], RED)
    c.line([(15, 27), (17, 26)], RED)

    def rattle(x, y, w):
        c.block(x - w + spin, y - 5, x + w + spin, y + 5, p["pc"])
        for k in range(int(w)):  # ratchet teeth
            c.px(x - w + 1 + k * 2 + spin, y - 5, GOLD)
        c.ellipse(x + spin, y, 2, 2, GOLD)
    if b == 1:  # Wide: two rattles on a cross bar
        c.rect(5, 15, 27, 17, WOOD)
        rattle(7, 11, 5)
        rattle(25, 11, 5)
        return (16, 5)
    rattle(16, 13, 9 if b == 0 else 8)
    if b == 0:  # Loud: a speaker cone and sound waves
        c.ellipse(16, 13, 4, 4, hexc("#3a3a40"))
        c.ellipse(16, 13, 2, 2, SILVER)
        if p.get("act") != "idle":
            for r in (12, 14):
                ring(c, 16, 13, r, r * 0.6, GOLD, 14)
    return (16, 7)


def sparkler(c, p):
    b = tier(p)
    tall = 7 if b == 1 else 0
    top = 10 - tall
    c.line([(16, 31), (16, top)], hexc("#8a8a90"), 2)
    c.rect(15, 25, 17.5, 31, p["pc"])  # grip
    burst = hexc("#ff8040") if b == 0 else hexc("#ffe070")
    if b == 0:
        glow(c, 16, top, 9, hexc("#ff6020"))
    rays = 12 if b == 0 else 8
    for a in range(rays):
        ang = a * math.tau / rays + phase(p) * 0.3
        r = (8 if b == 0 else 6) if p.get("act") == "idle" else (10 if b == 0 else 8)
        c.line([(16, top), (16 + math.cos(ang) * r, top + math.sin(ang) * r)], burst)
        c.px(16 + math.cos(ang) * (r + 1.5), top + math.sin(ang) * (r + 1.5), WHITE)
    c.ellipse(16, top, 2.2, 2.2, WHITE)
    return (16, top - 4)


def streamer_tangle(c, p):
    b = tier(p)
    width = 2 if b != 0 else 3
    spread = 1.0 if b != 1 else 1.4
    c.blob(16, 25, 6, 5, hexc("#e8e0d0"))  # spool
    c.ellipse(16, 25, 2, 2, WOOD)
    cols = (p["pc"], GOLD, SKY) if b != 0 else (p["pc"], GOLD, SKY, PINK)
    for i, col in enumerate(cols):
        side = -1 if i % 2 else 1
        pts = [(16 + side * x * spread, 22 - x * 1.2 + math.sin(x * 0.8 + i + phase(p) * 0.5) * 2.5)
               for x in range(0, 13)]
        c.line(pts, col, width)
    pc_mark(c, 16, 25, p, 1.0)
    return (16, 6)


# --- Precision -------------------------------------------------------------------

def _chair(c, x, y, s, color, p):
    c.block(x - 7 * s, y - 22 * s, x + 7 * s, y - 12 * s, color)  # back
    c.rect(x - 5 * s, y - 20 * s, x + 5 * s, y - 18 * s, p["pc"])
    c.block(x - 8 * s, y - 11 * s, x + 8 * s, y - 8 * s, p["pc"])  # seat
    for lx in (-6.5, 5):
        c.rect(x + lx * s, y - 8 * s, x + (lx + 1.8) * s, y, shade(color, -0.25))
    c.line([(x - 6 * s, y - 4 * s), (x + 6 * s, y - 2 * s)], shade(color, -0.25))


def folding_chair(c, p):
    b = tier(p)
    metal = SILVER if b != 1 else hexc("#9aa0a8")
    if b == 0:  # Stacked Chairs: a pile of chairs
        _chair(c, 10, 31, 0.75, metal, p)
        _chair(c, 22, 31, 0.75, metal, p)
        _chair(c, 16, 19, 0.75, metal, p)
        return (16, 2)
    _chair(c, 16, 31, 1.05, metal, p)
    if b == 1:  # Spiky: spikes on the back and legs
        for x in (9, 13, 17, 21):
            spike(c, x + 0.5, 8, -1.57, 4)
        spike(c, 8, 24, math.pi, 4)
        spike(c, 24, 24, 0, 4)
    return (16, 7)


def dart_blaster(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    orange = hexc("#f08030")
    barrel = 10 if b == 1 else 4
    c.block(8, 13, 26, 20, orange)
    c.rect(8, 15, 26, 16, p["pc"])
    c.rect(8 - barrel, 14, 8, 18, hexc("#f0e040"))  # barrel
    c.block(20, 20, 26, 29, shade(orange, -0.1))  # grip
    c.rect(17, 20, 19, 24, hexc("#3a3a40"))
    dart = (8 - barrel - (5 if fire else 2))
    c.rect(dart, 15, dart + 3, 17, SKY)  # dart with a suction tip
    c.rect(dart - 1, 14.5, dart, 17.5, hexc("#e04040"))
    if b == 0:  # Heavy: a drum magazine
        c.blob(14, 23, 5, 5, hexc("#3a3a58"))
        for k in range(4):
            a = k * math.pi / 2 + phase(p) * 0.4
            c.ellipse(14 + math.cos(a) * 2.5, 23 + math.sin(a) * 2.5, 1, 1, SKY)
    if b == 1:  # Long: a scope
        c.block(12, 8, 22, 12, hexc("#3a3a40"))
        c.ellipse(12, 10, 1.3, 2, SKY)
        c.rect(15, 12, 17, 13, hexc("#3a3a40"))
    return (dart - 1, 16)


def spotlight(c, p):
    b = tier(p)
    on = p.get("act") != "idle"
    r = 7 if b == 0 else 5.5
    length = 10 if b == 1 else 4
    for lx in (8, 24):  # tripod
        c.line([(16, 20), (lx, 31)], hexc("#3a3a40"), 2)
    c.line([(16, 20), (16, 31)], hexc("#3a3a40"), 2)
    if b == 0 and on:
        glow(c, 16, 8, 12, hexc("#fff8c0"))
    c.block(16 - r, 10 - length + 5, 16 + r, 21, hexc("#3a3a40"))  # can
    c.rect(16 - r, 18, 16 + r, 20, p["pc"])
    c.ellipse(16, 10 - length + 5, r, 2.5, hexc("#fff8c0") if not on else WHITE)  # lens
    if b == 0:  # Bright: barn doors
        c.poly([(16 - r - 4, 10 - length + 2), (16 - r, 10 - length + 5), (16 - r, 14)], hexc("#5a5a60"))
        c.poly([(16 + r + 4, 10 - length + 2), (16 + r, 10 - length + 5), (16 + r, 14)], hexc("#5a5a60"))
    for k in range(3):  # cooling fins
        c.line([(16 - r + 1, 13 + k * 2), (16 + r - 2, 13 + k * 2)], hexc("#5a5a60"))
    return (16, 10 - length + 3)


def foam_sword(c, p):
    b = tier(p)
    lift = -3 if p.get("act") == "fire" else 0
    w = 5 if b == 0 else 3.2
    top = 3 if b == 1 else 6
    if b == 1:
        top = -2
    blade = p["pc"]
    c.block(16 - w, top + lift, 16 + w, 22 + lift, blade)
    c.poly([(16 - w, top + lift), (16, top - 3 + lift), (16 + w, top + lift)], blade)
    c.line([(16 - w + 1.5, top + 1 + lift), (16 - w + 1.5, 21 + lift)], shade(blade, 0.3))
    for y in range(int(top + 4), 21, 5):  # foam dimples
        c.px(16 + 1, y + lift, shade(blade, -0.2))
    c.block(8 if b != 0 else 6, 22 + lift, 24 if b != 0 else 26, 25 + lift, GOLD)  # guard
    c.block(14.5, 25 + lift, 17.5, 31 + lift, hexc("#3a3a58"))
    c.ellipse(16, 31 + lift, 2, 1.4, GOLD)
    if b == 0:  # Big: a star gem on the guard
        star(c, 16, 23.5 + lift, 2.5, RED)
    return (16, top - 3 + lift)


def _rocket(c, x, y, s, p, col):
    c.rect(x - 0.5, y + 8 * s, x + 1, y + 18 * s, WOOD)  # stick
    c.block(x - 3 * s, y, x + 3 * s, y + 10 * s, col)
    c.rect(x - 3 * s, y + 3 * s, x + 3 * s, y + 4.5 * s, WHITE)
    c.poly([(x - 3.5 * s, y), (x, y - 5 * s), (x + 3.5 * s, y)], RED)
    c.poly([(x - 3 * s, y + 10 * s), (x - 5 * s, y + 12 * s), (x - 3 * s, y + 7 * s)], GOLD)
    c.poly([(x + 3 * s, y + 10 * s), (x + 5 * s, y + 12 * s), (x + 3 * s, y + 7 * s)], GOLD)


def bottle_rocket(c, p):
    b = tier(p)
    lift = -3 if p.get("act") == "fire" else 0
    c.block(9, 27, 23, 31, hexc("#5a3a8a"))  # launch base
    if b == 1:  # Rapid: three small rockets
        for x, y in ((9, 12), (23, 12), (16, 6)):
            _rocket(c, x, y + lift, 0.75, p, p["pc"])
        return (16, 1 + lift)
    s = 1.2 if b == 0 else 1.0
    _rocket(c, 16, 9 + lift if b != 0 else 6 + lift, s, p, p["pc"])
    if b == 0:  # Heavy: a gold warhead band
        c.rect(12.5, 9 + lift, 19.5, 10.5 + lift, GOLD)
    return (16, (4 if b != 0 else 0) + lift)


def disco_ball(c, p):
    b = tier(p)
    r = 10 if b == 0 else 8.5
    cy = 17 if b != 1 else 15
    if b == 1:  # Tall: hangs from a stand
        c.rect(26, 3, 28, 31, hexc("#5a5a60"))
        c.rect(15, 2, 28, 4, hexc("#5a5a60"))
        c.block(22, 28, 31, 31, hexc("#3a3a40"))
    c.rect(15, 2, 17, cy - r + 1, OUTLINE)
    c.blob(16, cy, r, r, hexc("#b8b8cc"))
    for x in range(int(16 - r) + 2, int(16 + r), 3):  # mirror tiles
        for y in range(int(cy - r) + 2, int(cy + r), 3):
            if (x - 16) ** 2 + (y - cy) ** 2 < (r - 1) ** 2 and (x + y + phase(p)) % 2:
                c.px(x, y, WHITE)
    if b == 0 and p.get("act") != "idle":  # Bright: light beams
        for k, col in enumerate((PINK, SKY, GOLD, LIME)):
            a = k * math.pi / 2 + 0.4 + phase(p) * 0.2
            c.line([(16 + math.cos(a) * (r + 1), cy + math.sin(a) * (r + 1)),
                    (16 + math.cos(a) * (r + 5), cy + math.sin(a) * (r + 5))], col)
    pface(c, 16, cy, p)
    pc_mark(c, 16 + r - 3, cy + r - 4, p, 1.2)
    return (16, cy - r)


# --- Control ----------------------------------------------------------------------

def jelly_wall(c, p):
    b = tier(p)
    wobble = (0, 1, 0, -1)[phase(p)] if (p.get("act") != "idle" or b == 1) else 0
    jelly = hexc("#ff6aa0", 225) if b != 0 else hexc("#e04080", 235)
    w = 12 if b == 0 else 10.5
    c.ellipse(16, 30, w + 2, 2, shade(jelly, -0.35))  # plate
    tiers = ((31, w, 9), (22, w - 3, 8)) if b != 1 else ((31, w, 8), (23, w - 2, 7), (16, w - 5, 6))
    for k, (y, tw, h) in enumerate(tiers):
        sway = wobble * (k + 1) * 0.6
        c.block(16 - tw + sway, y - h, 16 + tw + sway, y, jelly)
        c.rect(16 - tw + 2 + sway, y - h + 1, 16 - tw + 3.5 + sway, y - 2, shade(jelly, 0.3))  # shine
    top = tiers[-1][0] - tiers[-1][2]
    if b != 0:
        c.ellipse(16 + wobble, top - 2, 2.5, 2.5, hexc("#e02040"))  # cherry
        c.line([(16 + wobble, top - 4), (18 + wobble, top - 7)], hexc("#3a8a3a"))
    else:  # Thick: whipped cream crown
        puffs(c, [(10, top, 2.2), (16, top - 1, 2.6), (22, top, 2.2)], WHITE)
    pface(c, 16 + wobble * 0.6, 24, p)
    pc_mark(c, 16, 29, p, 1.2)
    return (16, top - 4)


def bubble_machine(c, p):
    b = tier(p)
    on = p.get("act") != "idle"
    c.block(7, 18, 25, 31, p["pc"])
    c.rect(7, 21, 25, 22, GOLD)
    c.ellipse(16, 26, 3.5, 3.5, hexc("#3a3a40"))  # fan
    for k in range(3):
        a = k * math.tau / 3 + phase(p) * (0.9 if b == 0 else 0.5)
        c.line([(16, 26), (16 + math.cos(a) * 3, 26 + math.sin(a) * 3)], SILVER)
    if b == 1:  # Wide: a wide wand bar
        c.rect(3, 14, 29, 16, SILVER)
        for x in (5, 12, 20, 27):
            ring(c, x, 12, 2, 2, SILVER, 10)
    else:
        c.rect(14, 12, 18, 18, SILVER)
        ring(c, 16, 10, 3, 3, SILVER, 12)
    if b == 0:  # Fast: speed stripes
        for y in (24, 27):
            c.line([(3, y), (6, y)], WHITE)
    bubbles = ((10, 9, 2.6), (19, 5, 3.2), (24, 11, 2)) if b != 1 else \
        ((5, 7, 2.4), (12, 4, 2.8), (20, 6, 2.4), (27, 5, 2.6))
    for x, y, r in bubbles:
        y -= 2 if on else 0
        ring(c, x, y, r, r, hexc("#c8f0ff"), 14)
        c.px(x - r * 0.5, y - r * 0.5, WHITE)
    return (16, 4)


def pie_launcher(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    arm = 19 if b == 1 else 14
    ang = -1.0 if fire else -0.55
    px_, py_ = 9 + math.cos(ang) * arm, 24 + math.sin(ang) * arm
    c.block(3, 24, 19, 31, p["pc"])  # base
    c.rect(3, 26, 19, 27, GOLD)
    wheel(c, 6, 30, 2.2)
    wheel(c, 16, 30, 2.2)
    c.line([(9, 25), (px_, py_)], WOOD, 2)
    pie_r = 6 if b == 0 else 5
    c.ellipse(px_, py_, pie_r, pie_r * 0.55, hexc("#d8a060"))  # crust
    c.ellipse(px_, py_ - 1, pie_r - 1, pie_r * 0.4, hexc("#f8f0e8"))  # cream
    if b == 0:  # Cream Pie: a tall swirl of cream with a cherry
        puffs(c, [(px_, py_ - 3, 3), (px_, py_ - 6, 2.2)], WHITE)
        c.ellipse(px_, py_ - 8.5, 1.5, 1.5, hexc("#e02040"))
    return (px_, py_ - 4)


def candle_stand(c, p):
    b = tier(p)
    on = p.get("act") != "idle"
    if b == 1:  # Wide Candle Ring: candles in a ring on a round cake
        c.ellipse(16, 25, 14, 6, hexc("#f0d0a0"))
        c.ellipse(16, 23, 13, 5, hexc("#f8e8d8"))
        sprinkles(c, 5, 22, 27, 26, 7, 2)
        spots = ((5, 21), (11, 18), (21, 18), (27, 21), (16, 23))
        h = 8
    else:
        c.block(5, 22, 27, 31, hexc("#f0d0a0"))
        c.rect(5, 22, 27, 25, hexc("#f8e8d8"))
        c.rect(5, 27, 27, 28, p["pc"])
        spots = ((9, 22), (16, 22), (23, 22))
        h = 10 if b != 0 else 14
    for k, (x, y) in enumerate(spots):
        col = PARTY[k % len(PARTY)]
        c.rect(x - 1.2, y - h, x + 1.2, y, col)
        c.line([(x - 1.2, y - h + 3), (x + 1.2, y - h + 2)], WHITE)
        flame = (5 if b == 0 else 3) + (1 if on else 0)
        c.poly([(x - 1.8, y - h), (x, y - h - flame - 1), (x + 1.8, y - h)], hexc("#ffb030"))
        c.px(x, y - h - 1, hexc("#fff0a0"))
    return (16, 22 - h - 6)


def party_horn(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    flare = 2 if fire else 0
    if b == 0:  # Air Horn: a can with a big red horn
        c.block(5, 16, 14, 31, SILVER)
        c.rect(5, 20, 14, 26, p["pc"])
        c.rect(7, 12, 12, 16, hexc("#3a3a40"))
        c.poly([(12, 14), (12, 11), (27, 5 - flare), (27, 20 + flare)], RED)
        c.ellipse(27, 12.5, 2, 7.5 + flare, shade(RED, -0.3))
        return (28, 12)
    horns = ((16, 18, 1.0),) if b != 1 else ((14, 10, 0.75), (14, 20, 0.75), (14, 29, 0.6))
    for x, y, s in horns:
        c.poly([(x - 9 * s, y + 2 * s), (x - 9 * s, y - 2 * s),
                (x + 10 * s, y - (7 + flare) * s), (x + 10 * s, y + (7 + flare) * s)], p["pc"])
        c.line([(x - 4 * s, y - 2.5 * s), (x - 4 * s, y + 2.5 * s)], GOLD, 2)
        c.line([(x + 3 * s, y - 4.5 * s), (x + 3 * s, y + 4.5 * s)], GOLD, 2)
        c.rect(x - 12 * s, y - 1.5 * s, x - 9 * s, y + 1.5 * s, GOLD)
    if b == 1:  # Chain: the horns are linked
        c.line([(5, 10), (5, 29)], SILVER, 2)
    return (26, 18 if b != 1 else 20)


def foam_machine(c, p):
    b = tier(p)
    on = p.get("act") != "idle"
    tank = hexc("#7a8aa0") if b != 0 else hexc("#c04a3a")
    w = 11 if b == 1 else 9
    c.block(16 - w, 17, 16 + w, 31, tank)
    c.rect(16 - w, 24, 16 + w, 26, p["pc"])
    c.ellipse(16 - w + 4, 21, 2, 2, GOLD)  # dial
    c.rect(18, 12, 22, 17, SILVER)  # nozzle
    if b == 0:  # Hot: heat lines
        for x in (10, 13):
            c.line([(x, 19), (x + 1, 21), (x, 23)], hexc("#ffb030"))
    if b == 1:  # Big: a wide hopper
        c.poly([(5, 17), (27, 17), (24, 14), (8, 14)], shade(tank, 0.2))
    foam = [(12, 12, 3), (18, 9, 3.4), (24, 12, 2.8), (15, 6, 2.6), (21, 4, 2.4)]
    puffs(c, [(x, y - (1 if on else 0), r * (1.15 if b == 1 else 1)) for x, y, r in foam],
          WHITE if b != 0 else hexc("#fff0e0"))
    return (18, 3)


# --- Toxin -----------------------------------------------------------------------

def sour_candy_wall(c, p):
    b = tier(p)
    candies = ((9, 15), (21, 15), (9, 25), (21, 25))
    size = 5.5
    if b == 0:  # Big Sour: bigger candies
        candies, size = ((9, 14), (23, 14), (9, 26), (23, 26)), 6.5
    cols = (hexc("#f0e040"), LIME, hexc("#ff7a5a"), p["pc"])
    if b == 1:  # Super Sour: acid green with dripping sour dust
        cols = (hexc("#a0f040"), hexc("#60e060"), hexc("#c0f060"), p["pc"])
    for i, (x, y) in enumerate(candies):
        c.block(x - size, y - size + 1, x + size, y + size, cols[i])
        for k in range(3):  # sugar crystals
            c.px(x - 3 + k * 3, y - size + 2 + k % 2, WHITE)
        if b == 1:
            c.rect(x - 2, y + size, x - 0.5, y + size + 2, hexc("#c0ff80"))
    pface(c, 16, 20, p, gap=4, mood="squint" if b == 1 else None)
    return (16, 7)


def lemon_squirter(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    skin = hexc("#f0e040") if b != 0 else hexc("#a8e040")
    length = 9 if b == 1 else 0
    c.blob(16, 22, 10, 8.5, skin)
    for x, y in ((9, 18), (22, 20), (14, 27), (20, 26)):  # peel dimples
        c.px(x, y, shade(skin, -0.15))
    c.ellipse(16, 30, 4, 1.2, hexc("#5a8a3a"))
    c.poly([(13, 15), (19, 15), (16, 8 - (3 if fire else 0))], shade(skin, -0.2))  # tip
    if b == 1:  # Long: a squeeze nozzle
        c.rect(14.5, 8 - length, 17.5, 9, SILVER)
        c.rect(13.5, 8 - length, 18.5, 10 - length, RED)
    c.ellipse(24, 12, 4, 2, LIME)  # leaf
    c.line([(20, 14), (24, 12)], hexc("#3a8a3a"))
    pface(c, 16, 21, p, mood="squint" if b == 0 else None)
    pc_mark(c, 9, 25, p, 1.2)
    if b == 0:  # Extra-Sour: sour sparkles
        for x, y in ((5, 10), (27, 18), (4, 22)):
            c.px(x, y, hexc("#e0ff60"))
    return (16, 6 - length)


def silly_string(c, p):
    b = tier(p)
    fire = p.get("act") == "fire"
    w = 6 if b == 0 else 5
    length = 8 if b == 1 else 0
    c.block(16 - w, 13, 16 + w, 31, p["pc"])
    c.rect(16 - w, 16, 16 + w, 18, GOLD)
    c.rect(16 - w, 26, 16 + w, 28, GOLD)
    star(c, 16, 22, 2.5, WHITE)
    c.block(16 - w + 1, 9, 16 + w - 1, 13, hexc("#e8e8f0"))  # cap
    c.rect(14, 7, 18, 9, RED)  # nozzle
    if b == 1:
        c.rect(15, 7 - length, 17, 7, RED)
    tip = 6 - length
    if fire or b == 0:
        col = PINK if b != 0 else hexc("#80f040")
        c.line([(16, tip), (12, tip - 4), (19, tip - 6), (14, tip - 9)], col, 1 if b != 0 else 2)
    if b == 0:  # Sticky: drips down the can
        for x in (11, 20):
            c.rect(x, 13, x + 1.5, 16 + x % 3, hexc("#80f040"))
    return (16, tip)


def punch_bowl(c, p):
    b = tier(p)
    punch = hexc("#e04060") if b != 0 else hexc("#80d040")
    glass = hexc("#d8e8f0", 220)
    if b == 1:  # Overflowing: punch spills over the rim
        for x in (5, 26):
            c.rect(x, 19, x + 2, 28, punch)
        c.ellipse(16, 30, 13, 2, shade(punch, -0.2))
    c.ellipse(16, 22, 13, 7.5, glass)
    c.ellipse(16, 19, 11, 4, punch)
    for x, y in ((12, 18), (20, 19)):
        c.ellipse(x, y, 2, 1.4, hexc("#f0e040"))  # lemon slices
    c.rect(13, 28, 19, 31, glass)
    c.line([(23, 16), (27, 6)], SILVER, 2)  # ladle
    c.ellipse(27, 5, 2, 1.4, SILVER)
    if b == 0:  # Sour: fizzing bubbles
        for x, y in ((9, 13), (15, 11), (19, 13)):
            ring(c, x, y - phase(p) % 2, 1.5, 1.5, hexc("#c0ff80"), 8)
    c.ellipse(16, 25, 1.4, 1.2, p["pc"])
    return (16, 12)


def stink_bomb(c, p):
    b = tier(p)
    on = p.get("act") != "idle"
    r = 9 if b == 0 else 7.5
    cx, cy = 16, 22 if b != 1 else 23
    if b == 1:  # Long: sits in a slingshot
        c.line([(6, 31), (9, 18)], WOOD, 2)
        c.line([(26, 31), (23, 18)], WOOD, 2)
        c.line([(9, 18), (16, 27), (23, 18)], hexc("#c04040"))
    c.blob(cx, cy, r, r, hexc("#5a5a6a"))
    c.ellipse(cx - 3, cy - 3, 2, 1.5, hexc("#8a8a9a"))
    c.rect(cx - 2, cy - r - 3, cx + 2, cy - r + 1, SILVER)  # cap
    c.line([(cx, cy - r - 3), (cx + 2, cy - r - 7)], WOOD)  # fuse
    c.px(cx + 2, cy - r - 8, hexc("#ffb030"))
    c.ellipse(cx, cy + 1, 3, 3, p["pc"])
    c.ellipse(cx, cy + 1, 1.5, 1.5, WHITE)
    if b == 0:  # Super: green stripes
        c.line([(cx - r + 1, cy - 2), (cx + r - 1, cy - 2)], LIME, 2)
    if on or b == 0:
        for x, y in ((cx - r - 2, cy - r), (cx + r + 2, cy - r + 1)):
            c.blob(x, y - phase(p) % 2, 2.5, 2, hexc("#a0e040", 200), shine=False)
    return (cx + 2, cy - r - 8)


def moldy_cake(c, p):
    b = tier(p)
    sponge_col = hexc("#e8c8a8") if b != 0 else hexc("#b8a890")
    frost = hexc("#f8f0f0") if b != 0 else hexc("#d0d0b8")
    c.block(4, 15, 28, 31, sponge_col)
    c.rect(4, 22, 28, 24, hexc("#c05070") if b != 0 else hexc("#806060"))  # jam layer
    c.ellipse(16, 15, 12, 3, frost)
    for k in range(5):
        c.rect(5 + k * 5, 15, 6.5 + k * 5, 18 + k % 2 * 2, frost)
    spots = ((9, 27), (22, 26), (25, 18), (7, 19))
    if b == 1:  # Fuzzy: lots of fuzzy mold
        spots = spots + ((14, 13), (20, 12), (12, 29), (26, 29), (17, 27))
    mold = hexc("#8aa060") if b != 0 else hexc("#6a8a7a")
    for x, y in spots:
        c.blob(x, y, 2.6, 2, mold, shine=False)
        c.px(x - 1, y - 1, hexc("#c0e090"))
    c.rect(15, 6, 17, 13, hexc("#a0c0a0"))  # droopy candle
    c.poly([(14.5, 6), (16, 3), (17.5, 6)], hexc("#8aa060"))
    if b == 0:  # Stale: cracks
        c.line([(10, 16), (12, 20), (11, 22)], shade(sponge_col, -0.35))
    pface(c, 16, 20, p, mood="squint" if b == 0 else None)
    pc_mark(c, 25, 29, p, 1.2)
    return (16, 4)


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
