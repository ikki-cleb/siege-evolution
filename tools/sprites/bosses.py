"""The 7 bosses, drawn on a 64x64 canvas (twice the detail of other sprites).

The user asked for bosses that look threatening and detailed now that they
star on the world postcards: menacing but still cartoony (angry glowing
eyes, fangs, scars, spikes, battle damage; no gore). Each boss also has its
own death animation (6 frames) instead of the shared burst.

    frames(boss_id) -> (move frames, death frames)

The game shows bosses 2x the size of a normal enemy; it scales strips by
their height, so 64x64 frames need no game changes.
"""
import math
import random

from PIL import Image, ImageDraw

from .kit import Canvas, hexc, shade

B = 64  # canvas size
WHITE = (250, 250, 250, 255)
BLACK = (20, 12, 18, 255)


# --- Helpers ----------------------------------------------------------------

def phase(p):
    return p.get("phase", 0)


def bob(p, amount=1.0):
    return (0, -1, 0, 1)[phase(p)] * amount


def halo(img, x, y, r, color, alpha=90):
    """A soft glow blended onto the image (unlike shapes, which replace
    pixels). Used after the outline for glowing eyes, cores and beams."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(3):
        rr = r * (1 - k * 0.3)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color[:3] + (int(alpha * (0.4 + 0.3 * k)),))
    img.alpha_composite(layer)


def post(c, fn):
    """Runs `fn(img)` after the outline is added (glows, beams, sparks)."""
    if not hasattr(c, "post"):
        c.post = []
    c.post.append(fn)


def glowing_eye(c, x, y, r, color, angry_side=0):
    """A bright glowing eye with a dark slit, and an angry brow."""
    c.ellipse(x, y, r, r * 0.8, shade(color, 0.25))
    c.ellipse(x, y, r * 0.6, r * 0.5, WHITE)
    c.rect(x - 0.5, y - r * 0.5, x + 0.8, y + r * 0.5, BLACK)
    if angry_side:  # a slim, gently slanted brow (the user found the first ones too angry)
        s = angry_side  # -1 = left eye, 1 = right eye
        c.poly([(x + s * r * 1.4, y - r * 1.9), (x + s * r * 1.4, y - r * 1.5),
                (x - s * r * 1.2, y - r * 1.0), (x - s * r * 1.2, y - r * 1.4)], BLACK)
    post(c, lambda img, x=x, y=y, r=r, col=color: halo(img, c.T(x, y)[0], c.T(x, y)[1], r * 1.6, col, 35))


def fang(c, x, y, length, color=WHITE, down=True):
    d = 1 if down else -1
    c.poly([(x - 1.2, y), (x + 1.2, y), (x, y + length * d)], color)


def rivets(c, points, color):
    for x, y in points:
        c.px(x, y, shade(color, 0.3))
        c.px(x + 1, y + 1, shade(color, -0.3))


# --- 1. Giant Centipede (Backyard Bugs): rearing up ------------------------------

def giant_centipede(c, p):
    shell = hexc("#9a2a1e")
    plate = hexc("#c84a2a")
    leg = hexc("#e0a040")
    wob = phase(p)
    # The body path: tail coiled at the bottom right, rising to the head.
    path = []
    for i in range(11):
        t = i / 10
        x = 50 - 36 * math.sin(t * 2.2) + math.sin(t * 9 + wob * 1.6) * 1.6
        y = 56 - 40 * t + 6 * math.sin(t * 3.1)
        path.append((x, y))
    for i, (x, y) in enumerate(path[:-1]):
        r = 5.0 + i * 0.35
        # legs: a pair per segment, alternating with the walk
        swing = 2.5 if (i + wob) % 2 else -2.5
        for side in (-1, 1):
            c.line([(x, y), (x + side * (r + 4), y + 2 + swing * side * 0.4), (x + side * (r + 6), y + 6)], shade(leg, -0.2), 2)
            c.px(x + side * (r + 6), y + 6, leg)
        c.ellipse(x, y + 1, r + 0.5, r * 0.8, shade(shell, -0.25))
        c.ellipse(x, y, r, r * 0.75, shell)
        c.ellipse(x - r * 0.25, y - r * 0.25, r * 0.7, r * 0.4, plate)  # armor plate
        c.line([(x - r * 0.7, y + r * 0.2), (x + r * 0.7, y + r * 0.2)], shade(shell, -0.35))  # seam
        c.px(x - r * 0.4, y - r * 0.4, shade(plate, 0.3))
    # The head: big, with long antennae and huge curved pincers.
    hx, hy = path[-1][0], path[-1][1] - 2
    for side in (-1, 1):
        c.line([(hx + side * 3, hy - 6), (hx + side * 10, hy - 16), (hx + side * 16, hy - 18 + wob % 2)], shade(leg, -0.1), 2)
    c.ellipse(hx, hy, 11, 9, shade(shell, -0.2))
    c.ellipse(hx, hy - 1, 10, 8, shell)
    c.ellipse(hx - 3, hy - 4, 5, 2.5, plate)
    for side in (-1, 1):  # pincers
        open_ = 1.5 if wob in (1, 2) else 0
        pts = [(hx + side * 5, hy + 5), (hx + side * (13 + open_), hy + 7), (hx + side * (14 + open_), hy + 14),
               (hx + side * (9 + open_), hy + 18), (hx + side * (11 + open_), hy + 13), (hx + side * 6, hy + 9)]
        c.poly(pts, hexc("#3a1a14"))
        c.line([(hx + side * (12 + open_), hy + 9), (hx + side * (12 + open_), hy + 14)], hexc("#e8d0a0"))
    for side in (-1, 1):
        glowing_eye(c, hx + side * 4.5, hy - 1, 2.6, hexc("#ffd23c"), side)
        c.px(hx + side * 8, hy - 4, hexc("#ffd23c"))  # extra small eyes
    c.rect(hx - 4, hy + 4, hx + 4.5, hy + 6, BLACK)  # mouth
    for x in (-3, -1, 1, 3):
        fang(c, hx + x, hy + 4, 2.5)


def centipede_death(frames_move):
    """Crumbles segment by segment from the tail, in puffs of dust."""
    return _crumble(frames_move[0], hexc("#c8a080"), from_bottom=True)


# --- 2. Grizzly (Wild Kingdom): rearing up on hind legs, roaring ------------------

def grizzly(c, p):
    fur = hexc("#6a4428")
    dark = shade(fur, -0.18)
    light = hexc("#a87850")
    claw = hexc("#f0e8d0")
    b = bob(p)
    sway = (0, 2, 0, -2)[phase(p)]
    # hind legs and feet
    for side in (-1, 1):
        c.ellipse(32 + side * 9, 52, 7, 8, dark)
        c.ellipse(32 + side * 10, 59, 8, 3.5, shade(fur, -0.3))
        for k in range(3):
            c.px(32 + side * 10 + (k - 1) * 3, 61, claw)
    # body
    c.ellipse(32, 38 + b, 17, 18, dark)
    c.ellipse(31, 37 + b, 16, 17, fur)
    c.ellipse(32, 41 + b, 10, 11, light)  # belly
    for x, y in ((22, 26), (42, 26), (18, 34), (46, 34)):  # shaggy tufts
        c.poly([(x - 3, y + b), (x, y - 5 + b), (x + 3, y + b)], dark)
    # arms raised, claws out
    for side in (-1, 1):
        ax = 32 + side * 18
        ay = 20 + b - (sway * side)
        c.line([(32 + side * 11, 32 + b), (ax, ay)], dark, 8)
        c.ellipse(ax, ay, 5.5, 5, fur)
        for k in range(3):  # three hooked claws
            cx = ax + (k - 1) * 3
            c.line([(cx, ay - 3), (cx + side * 0.5, ay - 7), (cx + side * 2, ay - 9)], claw)
    # head
    hy = 18 + b
    for side in (-1, 1):
        c.ellipse(32 + side * 10, hy - 9, 4.5, 4.5, dark)
        c.ellipse(32 + side * 10, hy - 9, 2.2, 2.2, light)
    c.ellipse(32, hy, 13, 11, dark)
    c.ellipse(31.5, hy - 0.5, 12, 10, fur)
    c.ellipse(32, hy + 5, 7.5, 5.5, light)  # muzzle
    c.ellipse(32, hy + 1.5, 3, 2, BLACK)  # nose
    c.px(31, hy + 1, (120, 110, 120, 255))
    # roaring mouth with fangs
    c.ellipse(32, hy + 7, 5, 3.2, hexc("#5a1020"))
    c.ellipse(32, hy + 8, 3, 1.6, hexc("#c84060"))  # tongue
    fang(c, 28.5, hy + 4.5, 3)
    fang(c, 35.5, hy + 4.5, 3)
    fang(c, 29.5, hy + 10, 2.5, down=False)
    fang(c, 34.5, hy + 10, 2.5, down=False)
    glowing_eye(c, 26.5, hy - 3, 2.2, hexc("#ff5a2a"), -1)
    glowing_eye(c, 37.5, hy - 3, 2.2, hexc("#ff5a2a"), 1)
    # a scar across the right eye
    c.line([(35, hy - 9), (41, hy + 1)], hexc("#e08080"), 1)
    c.line([(36, hy - 7), (38, hy - 8)], hexc("#e08080"))
    c.line([(38, hy - 4), (40, hy - 5)], hexc("#e08080"))


def grizzly_death(frames_move):
    """Topples over backwards with dust, little stars circling, then fades."""
    base = frames_move[0]
    frames = [_flash(base)]
    for k, (angle, fade) in enumerate(((12, 1.0), (30, 1.0), (45, 0.95), (48, 0.6), (48, 0.25))):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        r = base.rotate(angle, resample=Image.NEAREST, center=(32, 60))
        f.alpha_composite(_faded(r, fade), (min(14, k * 4), 0))
        d = ImageDraw.Draw(f)
        if k >= 1:  # dust where it lands
            for x in (12, 22, 40, 52):
                rr = 3 + k
                d.ellipse((x - rr, 56 - rr / 2, x + rr, 56 + rr / 2), fill=(200, 180, 150, int(160 * fade)))
        if k >= 2:  # dizzy stars
            for i in range(3):
                a = k * 1.2 + i * 2.1
                sx, sy = 20 + math.cos(a) * 10, 34 + math.sin(a) * 4
                _star(d, sx, sy, 2.5, (255, 220, 80, int(255 * fade)))
        frames.append(f)
    return frames


# --- 3. Superbug (Microscopic): spiked virus king -------------------------------

def superbug(c, p):
    body = hexc("#5a2a8a")
    spike = hexc("#8a4ac0")
    tip = hexc("#7fff60")
    b = bob(p, 1.5)
    cx, cy = 32, 34 + b
    # writhing tendrils underneath
    for i in range(5):
        x0 = 20 + i * 6
        wig = math.sin(i * 1.3 + phase(p) * 1.6) * 3
        c.line([(x0, cy + 12), (x0 + wig, cy + 20), (x0 - wig, cy + 26)], shade(body, -0.1), 2)
        c.px(x0 - wig, cy + 27, tip)
    # spikes with glowing tips, all around
    for i in range(14):
        a = i * math.tau / 14 + phase(p) * 0.04
        bx, by = cx + math.cos(a) * 16, cy + math.sin(a) * 15
        tx, ty = cx + math.cos(a) * 24, cy + math.sin(a) * 23
        nx, ny = -math.sin(a) * 2, math.cos(a) * 2
        c.poly([(bx + nx, by + ny), (bx - nx, by - ny), (tx, ty)], spike)
        c.ellipse(tx, ty, 2, 2, tip)
        post(c, lambda img, x=tx, y=ty: halo(img, c.T(x, y)[0], c.T(x, y)[1], 4, tip, 50))
    c.ellipse(cx, cy + 1, 18, 17, shade(body, -0.25))
    c.ellipse(cx - 0.5, cy - 0.5, 17, 16, body)
    for x, y, r in ((-9, -7, 3), (9, -9, 2.5), (-11, 6, 2.2), (11, 7, 2.8)):  # glowing core blotches
        c.ellipse(cx + x, cy + y, r, r, hexc("#b070e0"))
        c.px(cx + x - 1, cy + y - 1, hexc("#e0b0ff"))
    # the face: angry glowing eyes and a big fanged mouth
    glowing_eye(c, cx - 6, cy - 3, 3.2, hexc("#ffe040"))  # no brows (user)
    glowing_eye(c, cx + 6, cy - 3, 3.2, hexc("#ffe040"))
    c.ellipse(cx, cy + 7, 9, 4.5, hexc("#2a0a20"))
    c.ellipse(cx, cy + 9, 6, 2, hexc("#a03060"))
    for x in (-6, -3, 0, 3, 6):
        fang(c, cx + x, cy + 3.5, 3 if x % 2 else 2)
    for x in (-4, 2):
        fang(c, cx + x, cy + 11, 2, down=False)
    c.rect(cx + 4, cy + 11, cx + 5, cy + 14 + phase(p) % 2, hexc("#9aff60"))  # drool
    # a jagged gold crown with gems
    crown = hexc("#ffd23c")
    c.rect(cx - 9, cy - 19, cx + 9, cy - 15, crown)
    for x in (-9, -4.5, 0, 4.5, 9):
        c.poly([(cx + x - 2.2, cy - 19), (cx + x, cy - 26 - (x == 0) * 2), (cx + x + 2.2, cy - 19)], crown)
    for x, col in ((-5, "#ff3a5a"), (0, "#3ac0ff"), (5, "#ff3a5a")):
        c.ellipse(cx + x, cy - 17, 1.4, 1.4, hexc(col))
    c.line([(cx - 9, cy - 15), (cx + 9, cy - 15)], shade(crown, -0.3))


def superbug_death(frames_move):
    """Swells up, then bursts into a splash of goo droplets."""
    base = frames_move[0]
    frames = [_flash(base)]
    for s in (1.12, 1.22):  # swell
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        big = base.resize((int(B * s), int(B * s)), Image.NEAREST)
        f.alpha_composite(big, (int((B - big.width) / 2), int((B - big.height) / 2)))
        frames.append(f)
    rnd = random.Random(7)
    drops = [(rnd.uniform(0, math.tau), rnd.uniform(0.6, 1.0), rnd.choice(["#7fff60", "#8a4ac0", "#b070e0"])) for _ in range(26)]
    for k, fade in ((1, 1.0), (2, 0.7), (3, 0.35)):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        d = ImageDraw.Draw(f)
        rr = 8 + k * 6
        d.ellipse((32 - rr, 36 - rr * 0.8, 32 + rr, 36 + rr * 0.8), outline=(200, 255, 160, int(200 * fade)), width=2)
        for a, sp, col in drops:
            dist = (6 + k * 8) * sp
            x, y = 32 + math.cos(a) * dist, 36 + math.sin(a) * dist * 0.85 + k * k * 0.8
            size = 3 - k * 0.6
            d.ellipse((x - size, y - size, x + size, y + size), fill=hexc(col)[:3] + (int(255 * fade),))
        frames.append(f)
    return frames


# --- 4. Mega Tank (Total War): an angry machine ---------------------------------

def mega_tank(c, p):
    hull = hexc("#4a4a30")
    plate = hexc("#62623e")
    tread = hexc("#2a2a26")
    ph = phase(p)
    b = (0, -0.5, 0, 0.5)[ph]
    # treads with moving spiked links and wheels
    c.block(5, 44, 59, 58, tread)
    for i in range(10):
        x = 6 + ((i * 6 + ph * 1.5) % 54)
        c.rect(x, 44, x + 2, 45.5, hexc("#5a5a50"))
        c.rect(x, 56.5, x + 2, 58, hexc("#5a5a50"))
        c.poly([(x, 58), (x + 2, 58), (x + 1, 61)], hexc("#8a8a80"))  # tread spikes
    for x in (12, 22, 32, 42, 52):
        c.ellipse(x, 51, 4, 4, hexc("#3a3a34"))
        c.ellipse(x, 51, 1.6, 1.6, hexc("#8a8a70"))
    # the hull: sloped armor with rivets
    c.poly([(3, 44 + b), (8, 32 + b), (56, 32 + b), (61, 44 + b)], hull)
    c.poly([(8, 32 + b), (56, 32 + b), (54, 35 + b), (10, 35 + b)], plate)
    rivets(c, [(10 + i * 6, 41 + b) for i in range(8)], hull)
    # glowing red headlights and a viewport slit (they read as angry eyes)
    for x in (8, 15):
        c.ellipse(x, 39 + b, 2.4, 1.8, hexc("#ff3020"))
        post(c, lambda img, x=x: halo(img, c.T(x, 39 + b)[0], c.T(x, 39 + b)[1], 4, hexc("#ff3020"), 50))
    c.poly([(20, 37 + b), (30, 38.5 + b), (30, 40 + b), (20, 39 + b)], hexc("#ff6040"))
    # scorch marks and dents
    for x, y, r in ((40, 38, 3), (49, 36, 2), (24, 42, 2)):
        c.ellipse(x, y + b, r, r * 0.6, shade(hull, -0.25))
    # the turret: twin cannons, a skull emblem
    c.block(18, 18 + b, 48, 33 + b, plate)
    c.rect(18, 18 + b, 48, 20 + b, shade(plate, 0.18))
    for y in (22, 27):  # twin cannons pointing forward-left
        c.block(-2, y + b, 20, y + 3.5 + b, hexc("#3a3a28"))
        c.rect(-2, y - 0.5 + b, 2, y + 4 + b, hexc("#2a2a20"))  # muzzle brake
    sx, sy = 36, 25 + b  # skull
    c.ellipse(sx, sy, 4.5, 4, WHITE)
    c.rect(sx - 2.5, sy + 2, sx + 3, sy + 5, WHITE)
    c.ellipse(sx - 1.8, sy, 1.3, 1.4, BLACK)
    c.ellipse(sx + 1.8, sy, 1.3, 1.4, BLACK)
    for x in (-1.5, 0.5, 2.5):
        c.px(sx + x, sy + 4, BLACK)
    for side in (-1, 1):  # crossed bones
        c.line([(sx - 6, sy + 4 + side * 3), (sx + 6, sy + 4 - side * 3)], WHITE)
    rivets(c, [(21, 30 + b), (45, 30 + b), (21, 21 + b), (45, 21 + b)], plate)
    # hatch, antenna with a tattered flag, exhaust puff
    c.ellipse(40, 17 + b, 5, 2, shade(plate, -0.1))
    c.line([(46, 18 + b), (50, 2 + b)], hexc("#2a2a20"))
    flap = ph % 2
    c.poly([(50, 2 + b), (58, 3 + flap + b), (55, 5 + b), (58, 7 - flap + b), (50, 8 + b)], hexc("#c03030"))
    c.ellipse(52.5, 5 + b, 1.4, 1.4, WHITE)
    post(c, lambda img: halo(img, c.T(60, 30)[0], c.T(60, 30 - ph * 2)[1], 4 + ph, (160, 160, 150, 255), 60))


def mega_tank_death(frames_move):
    """Explodes: a flash, a fireball, the turret flying off, then smoke."""
    base = frames_move[0]
    turret = base.crop((0, 0, B, 34))
    hull = base.copy()
    ImageDraw.Draw(hull).rectangle((0, 0, B, 33), fill=(0, 0, 0, 0))
    frames = [_flash(base)]
    for k in range(5):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        f.alpha_composite(_faded(_darken(hull, 0.5), 1.0 - k * 0.18))
        if k < 3:  # the turret flies up and spins
            t = turret.rotate(-25 * (k + 1), resample=Image.NEAREST, center=(33, 25))
            f.alpha_composite(_faded(_darken(t, 0.3), 1.0 - k * 0.25), (6 * (k + 1), -10 * (k + 1)))
        _fireball(f, 32, 40, k)
        frames.append(f)
    return frames


# --- 5. Mothership (Galactic Siege): armored saucer with a pilot -----------------

def mothership(c, p):
    hull = hexc("#5a5a7a")
    rim_c = hexc("#8a8aaa")
    dark = hexc("#34344a")
    ph = phase(p)
    b = bob(p)
    # the glass dome with the alien pilot
    c.ellipse(32, 22 + b, 13, 12, hexc("#a0e8ff", 230))
    c.ellipse(32, 25 + b, 7, 6.5, hexc("#6ad070"))  # head
    for side in (-1, 1):
        c.ellipse(32 + side * 6, 18 + b, 1.2, 1.2, hexc("#6ad070"))  # antenna bulbs
        c.line([(32 + side * 3, 21 + b), (32 + side * 6, 18 + b)], hexc("#4aa050"))
    glowing_eye(c, 29, 25 + b, 2, hexc("#ff3050"))  # no brows (user)
    glowing_eye(c, 35, 25 + b, 2, hexc("#ff3050"))
    c.line([(30, 29 + b), (32, 28.5 + b), (34, 29 + b)], BLACK)
    c.px(26, 16 + b, WHITE)  # glass glint
    c.px(27, 15 + b, WHITE)
    # the saucer: armored disc, plates, spikes, a ring of lights
    c.ellipse(32, 36 + b, 30, 9, dark)
    c.ellipse(32, 34 + b, 30, 8, hull)
    c.ellipse(32, 32 + b, 24, 4.5, rim_c)
    for i in range(7):  # armor plate seams
        x = 12 + i * 6.7
        c.line([(x, 31 + b), (x - 1, 39 + b)], dark)
    for side in (-1, 1):  # side spikes
        c.poly([(32 + side * 28, 33 + b), (32 + side * 36, 35 + b), (32 + side * 28, 37 + b)], rim_c)
    lights = ["#ff3050", "#ffd23c", "#3ae0ff", "#b07aff"]
    for i in range(8):
        x = 9 + i * 6.6
        col = hexc(lights[(i + ph) % 4])
        c.ellipse(x, 37 + b, 1.6, 1.4, col)
        post(c, lambda img, x=x, col=col: halo(img, c.T(x, 37 + b)[0], c.T(x, 37 + b)[1], 3.5, col, 60))
    c.ellipse(32, 42 + b, 9, 3, dark)  # underside hatch
    c.ellipse(32, 42 + b, 5, 1.6, hexc("#3ae0ff"))

    # the tractor beam (drawn after the outline so it stays see-through)
    def beam(img):
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        top = c.T(32, 43 + b)[1]
        d.polygon([(27, top), (37, top), (46, 63), (18, 63)], fill=(120, 230, 255, 55))
        for i in range(3):
            y = top + 5 + ((i * 7 + ph * 2) % 18)
            w = 5 + (y - top) * 0.45
            d.line([(32 - w, y), (32 + w, y)], fill=(200, 250, 255, 90))
        img.alpha_composite(layer)
    post(c, beam)


def mothership_death(frames_move):
    """Sparks, tilts, then blows apart in a ring with falling debris."""
    base = frames_move[0]
    frames = []
    for k, angle in ((0, 8), (1, 18)):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        f.alpha_composite(base.rotate(angle, resample=Image.NEAREST, center=(32, 34)), (0, k * 3))
        d = ImageDraw.Draw(f)
        for x, y in ((14, 30), (46, 36), (30, 24)):
            _star(d, x + k * 3, y, 3, (255, 240, 120, 255))
        frames.append(f)
    frames.append(_flash(base.rotate(25, resample=Image.NEAREST, center=(32, 34))))
    rnd = random.Random(3)
    bits = [(rnd.uniform(0, math.tau), rnd.uniform(0.5, 1.0)) for _ in range(14)]
    for k, fade in ((1, 1.0), (2, 0.65), (3, 0.3)):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        d = ImageDraw.Draw(f)
        rr = 10 + k * 8
        d.ellipse((32 - rr, 34 - rr * 0.45, 32 + rr, 34 + rr * 0.45), outline=(150, 230, 255, int(220 * fade)), width=3)
        for a, sp in bits:
            x = 32 + math.cos(a) * rr * sp
            y = 34 + math.sin(a) * rr * 0.6 * sp + k * k * 1.5
            d.rectangle((x - 1.5, y - 1, x + 1.5, y + 1), fill=(110, 110, 140, int(255 * fade)))
        _fireball(f, 32, 34, k - 1, scale=0.7)
        frames.append(f)
    return frames


# --- 6. Rat King (Kitchen Defense): fat rat with cape, crown and scepter ---------

def rat_king(c, p):
    fur = hexc("#6a6070")
    dark = shade(fur, -0.18)
    belly = hexc("#9a90a0")
    pink = hexc("#e8a0b0")
    cape = hexc("#a02030")
    gold = hexc("#ffd23c")
    b = bob(p)
    sway = (0, 2, 0, -2)[phase(p)]
    # a heap of crumbs and a cheese wedge to stand on
    c.ellipse(32, 59, 26, 5, hexc("#c89050"))
    for x, y in ((10, 57), (20, 60), (44, 59), (54, 57), (30, 61)):
        c.ellipse(x, y, 2.5, 1.6, hexc("#e0b070"))
    c.poly([(42, 60), (58, 60), (58, 51)], hexc("#ffd060"))
    c.ellipse(52, 57, 1.4, 1.2, hexc("#d0a030"))
    # the long scarred tail
    pts = [(14, 54), (6, 46 + sway * 0.5), (5, 36), (9, 28 + sway)]
    c.line(pts, pink, 3)
    for x, y in ((6, 44), (5, 37)):
        c.line([(x - 2, y), (x + 2, y + 1)], hexc("#a05060"))  # scars
    # the cape behind the body, with an ermine trim
    c.poly([(16, 26 + b), (48, 26 + b), (54, 58), (10, 58)], cape)
    c.poly([(16, 26 + b), (20, 26 + b), (16, 58), (10, 58)], shade(cape, -0.15))
    for y in range(30, 57, 5):
        c.rect(10 + (y - 30) * 0.12, y, 13 + (y - 30) * 0.12, y + 2, WHITE)
        c.px(11 + (y - 30) * 0.12, y + 1, BLACK)
    # the fat body
    c.ellipse(32, 44 + b, 15, 14, dark)
    c.ellipse(31.5, 43.5 + b, 14, 13, fur)
    c.ellipse(32, 46 + b, 9, 9, belly)
    for side in (-1, 1):  # feet
        c.ellipse(32 + side * 8, 57, 5, 2.5, pink)
    # the scepter in one paw
    c.line([(46, 52 + b), (52, 18 + b)], gold, 2)
    c.ellipse(52.5, 16 + b, 3.4, 3.4, gold)
    c.ellipse(52.5, 16 + b, 1.8, 1.8, hexc("#ff3a5a"))
    post(c, lambda img: halo(img, c.T(52.5, 16 + b)[0], c.T(52.5, 16 + b)[1], 6, hexc("#ff3a5a"), 60))
    c.ellipse(45, 40 + b, 4, 3.5, fur)  # paw on the scepter
    c.ellipse(19, 41 + b, 4, 3.5, fur)  # the other paw
    # the head: ears, red eyes, snarl, buck teeth, whiskers
    hy = 24 + b
    for side in (-1, 1):
        c.ellipse(32 + side * 10, hy - 8, 5.5, 5.5, dark)
        c.ellipse(32 + side * 10, hy - 8, 3.2, 3.2, pink)
    c.ellipse(32, hy, 12, 10, dark)
    c.ellipse(31.5, hy - 0.5, 11, 9, fur)
    c.ellipse(32, hy + 5, 6, 4, belly)  # snout
    c.ellipse(32, hy + 3, 2.2, 1.6, pink)  # nose
    glowing_eye(c, 27, hy - 2, 2.3, hexc("#ff2a2a"), -1)
    glowing_eye(c, 37, hy - 2, 2.3, hexc("#ff2a2a"), 1)
    c.line([(28, hy + 7), (32, hy + 6), (36, hy + 7)], BLACK)  # snarl
    c.rect(30.5, hy + 6.5, 33.5, hy + 9.5, hexc("#f0e0a0"))  # buck teeth
    c.line([(32, hy + 6.5), (32, hy + 9.5)], hexc("#c0a060"))
    for side in (-1, 1):
        for k in (-1, 1):
            c.line([(32 + side * 5, hy + 5), (32 + side * 13, hy + 4 + k * 2)], hexc("#d0d0d8"))
    # a tilted crown with gems
    c.poly([(22, hy - 9), (40, hy - 12), (41, hy - 7), (23, hy - 4)], gold)
    for x, y in ((22, -9), (28, -10.5), (34, -11.5), (40, -12)):
        c.poly([(x - 2, hy + y + 0.5), (x, hy + y - 6), (x + 2, hy + y - 0.5)], gold)
    for x, col in ((26, "#3ac0ff"), (31.5, "#ff3a5a"), (37, "#7fe08a")):
        c.ellipse(x, hy - 7.5 - (x - 22) * 0.16, 1.3, 1.3, hexc(col))


def rat_king_death(frames_move):
    """Poofs into smoke; the crown drops, bounces and is left behind."""
    base = frames_move[0]
    frames = [_flash(base)]
    crown = base.crop((18, 4, 46, 22))
    px = crown.load()
    for y in range(crown.height):  # keep only the gold and the gems
        for x in range(crown.width):
            r, g, bl, a = px[x, y]
            gold = r > 180 and g > 120 and bl < 110
            gem = max(r, g, bl) - min(r, g, bl) > 120 and a > 0
            if not (gold or gem):
                px[x, y] = (0, 0, 0, 0)
    for k, fade in ((0, 0.8), (1, 0.45), (2, 0.15), (3, 0.0), (4, 0.0)):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        if fade:
            f.alpha_composite(_faded(base, fade))
        d = ImageDraw.Draw(f)
        for i in range(7):  # smoke puffs
            a = i * math.tau / 7 + k * 0.3
            rr = 6 + k * 2
            x, y = 32 + math.cos(a) * (8 + k * 5), 40 + math.sin(a) * (6 + k * 3) - k * 2
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(190, 185, 200, max(0, 200 - k * 45)))
        cy = [10, 30, 44, 38, 44][k]  # the crown falls and bounces
        f.alpha_composite(crown.rotate(-20 * k, resample=Image.NEAREST, expand=False), (18 + k * 2, cy))
        frames.append(f)
    return frames


# --- 7. The Clown (Birthday Bash): a mischievous villain juggling bombs ----------

def clown(c, p):
    suit = hexc("#3a8ad8")
    ph = phase(p)
    b = bob(p)
    # big shoes
    for side in (-1, 1):
        c.ellipse(32 + side * 9, 59, 9, 3.5, hexc("#e02040"))
        c.ellipse(32 + side * 11, 58, 3, 1.2, shade(hexc("#e02040"), 0.3))
    # baggy polka-dot suit
    c.poly([(18, 34 + b), (46, 34 + b), (50, 56), (14, 56)], suit)
    c.line([(32, 36 + b), (32, 56)], shade(suit, -0.25))
    for x, y, col in ((22, 42, "#ffd23c"), (40, 40, "#ff3a5a"), (26, 51, "#ff3a5a"), (42, 50, "#ffd23c"), (35, 46, "#7fe08a")):
        c.ellipse(x, y + b * 0.5, 2.2, 2.2, hexc(col))
    for x in (32,):  # big buttons
        for y in (40, 46):
            c.ellipse(x, y + b, 1.6, 1.6, WHITE)
    # arms up, juggling
    hand_y = 30 + b
    for side in (-1, 1):
        hx = 32 + side * 17
        c.line([(32 + side * 12, 37 + b), (hx, hand_y + (ph % 2) * side * 2)], suit, 5)
        c.ellipse(hx, hand_y + (ph % 2) * side * 2, 3.2, 3.2, WHITE)  # gloves
    # the ruffled collar
    for i in range(7):
        x = 20 + i * 4
        c.ellipse(x, 34 + b, 3.2, 2.5, hexc("#ff9ad0") if i % 2 else WHITE)
    # the head: white face paint, wild orange hair, red nose, wicked grin
    hy = 24 + b
    for side in (-1, 1):
        for k in range(3):
            c.ellipse(32 + side * (12 + k * 2), hy - 4 + k * 4, 5, 4.5, hexc("#ff7a1a"))
    c.ellipse(32, hy, 11, 11, shade(WHITE, -0.12))
    c.ellipse(31.5, hy - 0.5, 10.5, 10.5, WHITE)
    for side in (-1, 1):
        ex = 32 + side * 4.5
        c.poly([(ex - 2, hy - 6), (ex + 2, hy - 6), (ex, hy - 11)], hexc("#7ac0ff"))  # paint above the eye
        c.ellipse(ex, hy - 3.5, 2.2, 2.2, WHITE)
        c.ellipse(ex - side * 0.6, hy - 3, 1.2, 1.4, BLACK)  # looking sideways, scheming
        c.line([(ex + side * 3, hy - 8.5), (ex - side * 2.5, hy - 6.5)], BLACK)  # sly brows
    c.ellipse(32, hy + 0.5, 3, 2.8, hexc("#ff2a2a"))  # nose
    c.px(31, hy - 0.5, hexc("#ffa0a0"))
    # a wide wicked grin curling up into the cheeks, teeth showing
    c.poly([(21, hy + 1), (26, hy + 4), (38, hy + 4), (43, hy + 1), (40, hy + 7), (32, hy + 9.5), (24, hy + 7)],
           hexc("#c01030"))
    c.poly([(25, hy + 4), (39, hy + 4), (38, hy + 6), (26, hy + 6)], WHITE)
    for x in range(27, 38, 3):
        c.px(x, hy + 5, shade(WHITE, -0.35))
    c.ellipse(32, hy + 7.5, 3, 1.3, hexc("#ff7a90"))  # tongue
    # a tiny tilted party hat
    c.poly([(26, hy - 10), (36, hy - 12), (33, hy - 24)], hexc("#b07aff"))
    c.ellipse(33, hy - 24, 2, 2, hexc("#ffd23c"))
    # three bombs juggled in an arc above (they move each frame)
    for i in range(3):
        a = math.pi * (0.15 + 0.7 * ((i / 3 + ph / 12) % 1))
        bx, by = 32 - math.cos(a) * 22, 24 - math.sin(a) * 15 + b
        c.ellipse(bx, by, 3.6, 3.6, hexc("#2a2a34"))
        c.px(bx - 1.2, by - 1.2, hexc("#7a7a8a"))
        c.line([(bx + 1.5, by - 3), (bx + 3, by - 5)], hexc("#c09060"))
        spark = (bx + 3.5, by - 6)
        c.px(spark[0], spark[1], hexc("#ffd23c"))
        post(c, lambda img, s=spark: halo(img, c.T(*s)[0], c.T(*s)[1], 3, hexc("#ffb030"), 90))


def clown_death(frames_move):
    """Pops like a balloon into a burst of confetti; his hat flies off."""
    base = frames_move[0]
    hat = base.crop((24, 0, 40, 16))
    frames = [_flash(base)]
    f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
    big = base.resize((int(B * 1.12), int(B * 1.12)), Image.NEAREST)
    f.alpha_composite(big, (-4, -6))
    frames.append(f)
    rnd = random.Random(11)
    bits = [(rnd.uniform(0, math.tau), rnd.uniform(0.4, 1.0),
             rnd.choice(["#ffd23c", "#ff3a5a", "#3a8ad8", "#7fe08a", "#ff9ad0", "#b07aff"])) for _ in range(40)]
    for k, fade in ((1, 1.0), (2, 0.85), (3, 0.55), (4, 0.25)):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        d = ImageDraw.Draw(f)
        if k == 1:
            d.ellipse((12, 12, 52, 52), outline=(255, 255, 255, 230), width=2)  # the pop
        for a, sp, col in bits:
            dist = (8 + k * 7) * sp
            x, y = 32 + math.cos(a) * dist, 30 + math.sin(a) * dist + k * k * 1.2
            w = 2 if (k + int(a * 10)) % 2 else 1
            d.rectangle((x - w, y - 1, x + w, y + 1), fill=hexc(col)[:3] + (int(255 * fade),))
        f.alpha_composite(_faded(hat.rotate(40 * k, resample=Image.NEAREST), fade), (24 + k * 5, max(0, -k * 2)))
        frames.append(f)
    return frames


# --- Shared death effects --------------------------------------------------------

def _faded(img, fade):
    out = img.copy()
    out.putalpha(out.getchannel("A").point(lambda a: int(a * fade)))
    return out


def _darken(img, amount):
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * (1 - amount)), int(g * (1 - amount)), int(b * (1 - amount)), a)
    return out


def _flash(img):
    """The first death frame: the boss flashes white."""
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flash = Image.composite(white, Image.new("RGBA", img.size, (0, 0, 0, 0)), img.getchannel("A"))
    return Image.blend(img, flash, 0.75)


def _star(d, x, y, r, color):
    d.line([(x - r, y), (x + r, y)], fill=color, width=1)
    d.line([(x, y - r), (x, y + r)], fill=color, width=1)
    d.point([(x - 1, y - 1), (x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1)], fill=color)


def _fireball(img, x, y, k, scale=1.0):
    """Explosion puffs: yellow-orange fire turning to grey smoke."""
    if k < 0:
        return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(5 + k)
    fire = [(255, 240, 140), (255, 170, 50), (230, 80, 30)]
    smoke = (90, 85, 90)
    for i in range(16):
        a = rnd.uniform(0, math.tau)
        dist = rnd.uniform(2, 13) * scale * (1 + k * 0.4)
        r = (2.5 + rnd.uniform(0, 4)) * scale * (1 + k * 0.25)
        cx, cy = x + math.cos(a) * dist, y + math.sin(a) * dist * 0.8 - k * 3
        col = fire[min(2, i % 3 + k // 2)] if k < 3 else smoke
        alpha = max(0, 255 - k * 50)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (alpha,))
    img.alpha_composite(layer)


def _crumble(base, dust, from_bottom=True):
    """Breaks a sprite into chunks that drop and fade, with dust puffs."""
    frames = [_flash(base)]
    step = 8
    for k, fade in ((1, 0.95), (2, 0.8), (3, 0.6), (4, 0.35), (5, 0.12)):
        f = Image.new("RGBA", (B, B), (0, 0, 0, 0))
        d = ImageDraw.Draw(f)
        for gy in range(B // step):
            for gx in range(B // step):
                piece = base.crop((gx * step, gy * step, (gx + 1) * step, (gy + 1) * step))
                if piece.getbbox() is None:
                    continue
                # Lower chunks fall apart first (like a body crumbling).
                start = (B // step - gy) * 0.45 if from_bottom else gy * 0.45
                t = max(0.0, k - start * 0.35)
                ox = int((gx * step - 32) * 0.1 * t)
                oy = int(t * t * 3.2)
                f.alpha_composite(_faded(piece, fade if t > 0 else 1.0),
                                  (max(0, min(B - step, gx * step + ox)), max(0, min(B - step, gy * step + oy))))
        for i in range(5):
            x = 10 + i * 11
            rr = 2 + k * 1.2
            d.ellipse((x - rr, 58 - rr * 0.6, x + rr, 58 + rr * 0.6), fill=dust[:3] + (int(170 * fade),))
        frames.append(f)
    return frames


# --- The table ---------------------------------------------------------------------

BOSSES = {
    "giant_centipede": (giant_centipede, centipede_death),
    "grizzly": (grizzly, grizzly_death),
    "superbug": (superbug, superbug_death),
    "mega_tank": (mega_tank, mega_tank_death),
    "mothership": (mothership, mothership_death),
    "rat_king": (rat_king, rat_king_death),
    "clown": (clown, clown_death),
}


def frames(boss_id):
    """Move (4 frames) and death (6 frames) strips for one boss."""
    design, death = BOSSES[boss_id]
    move = []
    for ph in range(4):
        c = Canvas(size=B)
        design(c, {"phase": ph})
        c.finish()
        for fn in getattr(c, "post", []):
            fn(c.img)
        move.append(c.img)
    return move, death(move)
