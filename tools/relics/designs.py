"""The 65 relic icon designs (16x16). One function per relic id.

Each function gets an Icon canvas and the relic's color from
data/relics.json (most icons use it as their main color). Draw inside
pixels 1..14; the outline is added afterwards.
"""
from kit import GOLD, INK, METAL, SHINE, WHITE, WOOD, hexc, ramp, shade

DESIGNS = {}


def design(func):
    DESIGNS[func.__name__] = func
    return func


# --- small shared parts -------------------------------------------------------

def blade(i, x, y, length, color):
    """A diagonal blade going up-right from (x, y): light edge on top."""
    light, base, dark, _ = ramp(color)
    for k in range(length):
        i.px(x + k, y - k, light)
        i.px(x + k + 1, y - k, base)
        i.px(x + k + 1, y - k + 1, dark)
    i.px(x + length, y - length, light)


def sparkle(i, x, y, color=WHITE):
    i.pxs([(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], color)


def coin(i, x0, y0, x1, y1, color=GOLD):
    light, base, dark, darker = ramp(color)
    i.ell(x0, y0, x1, y1, dark)
    i.ell(x0, y0, x1 - 1, y1 - 1, base)
    i.ell(x0 + 2, y0 + 2, x1 - 2, y1 - 2, dark)
    i.ell(x0 + 2, y0 + 2, x1 - 3, y1 - 3, light)


def bell(i, color, x=0, y=0):
    light, base, dark, darker = ramp(color)
    i.rect(7 + x, 1 + y, 8 + x, 2 + y, darker)
    i.poly([(5 + x, 3 + y), (10 + x, 3 + y), (11 + x, 9 + y), (13 + x, 11 + y),
            (2 + x, 11 + y), (4 + x, 9 + y)], base)
    i.rect(10 + x, 4 + y, 10 + x, 10 + y, dark)
    i.rect(11 + x, 9 + y, 12 + x, 10 + y, dark)
    i.rect(5 + x, 4 + y, 5 + x, 8 + y, light)
    i.rect(2 + x, 11 + y, 13 + x, 11 + y, darker)
    i.rect(6 + x, 12 + y, 9 + x, 13 + y, dark)  # clapper
    i.rect(7 + x, 12 + y, 8 + x, 13 + y, darker)


def arrow(i, x, y, length, shaft="#c09060", head=METAL, feather="#e05050"):
    """A diagonal arrow pointing up-right with its tail at (x, y)."""
    for k in range(length):
        i.px(x + k, y - k, shaft)
    hx, hy = x + length, y - length
    i.pxs([(hx, hy), (hx - 1, hy), (hx, hy + 1), (hx + 1, hy - 1), (hx - 2, hy), (hx, hy + 2)], head)
    i.pxs([(x - 1, y), (x, y + 1), (x - 1, y + 1), (x - 2, y + 1), (x - 1, y + 2)], feather)


def flask(i, color, bubbles=True):
    light, base, dark, darker = ramp(color)
    glass = (200, 230, 240, 255)
    i.rect(6, 1, 9, 1, WOOD)  # cork
    i.rect(6, 2, 9, 4, glass)
    i.ell(2, 4, 13, 14, (170, 200, 215, 255))
    i.ell(3, 7, 12, 14, base)
    i.ell(3, 10, 12, 14, dark)
    i.rect(3, 8, 12, 9, base)
    i.rect(5, 7, 10, 7, light)
    i.pxs([(4, 6), (4, 7), (5, 5)], SHINE)
    if bubbles:
        i.pxs([(8, 9), (10, 11), (6, 11)], light)


# --- common ------------------------------------------------------------------

@design
def sharpening_stone(i, c):
    # Whetstone with a blade being honed (sparks fly).
    i.box(1, 10, 14, 13, "#7c8290")
    i.pxs([(4, 12), (9, 11), (12, 12), (6, 11)], shade("#7c8290", -0.12))
    blade(i, 4, 9, 8, c)
    i.pxs([(2, 11), (3, 10)], GOLD)  # guard sits behind the stone
    i.pxs([(13, 4), (14, 6), (12, 7)], (255, 230, 120, 255))


@design
def spyglass(i, c):
    # A brass spyglass, its blue lens pointing up-right.
    brass, _, brass_d, _ = ramp(GOLD)
    for k in range(9):
        i.rect(2 + k, 11 - k, 3 + k, 12 - k, GOLD)
        i.px(3 + k, 12 - k, brass_d)
        i.px(2 + k, 11 - k, brass)
    i.rect(1, 12, 3, 14, "#6a4024")
    i.rect(6, 7, 8, 9, brass_d)  # band between sections
    i.ball(10, 1, 14, 5, c)
    i.px(11, 2, WHITE)


@design
def oiled_gears(i, c):
    light, base, dark, darker = ramp(c)
    for x, y in ((6, 1), (6, 12), (1, 6), (12, 6), (2, 2), (10, 2), (2, 10), (10, 10)):
        i.rect(x, y, x + 2, y + 2, dark)
    i.ell(2, 2, 12, 12, dark)
    i.ell(2, 2, 11, 11, base)
    i.ell(5, 5, 9, 9, darker)
    i.ell(6, 6, 8, 8, (30, 20, 26, 255))
    i.pxs([(4, 4), (5, 3), (3, 5)], light)
    # Oil drop.
    i.ell(11, 10, 14, 14, "#403040")
    i.px(13, 9, "#403040")
    i.px(12, 11, "#a080c0")


@design
def heavy_rounds(i, c):
    # Two big rifle cartridges: brass case, copper pointed tip.
    copper = "#c06830"
    for x in (2, 8):
        light, base, dark, darker = ramp(c)
        i.rect(x, 7, x + 4, 14, base)
        i.rect(x, 7, x, 14, light)
        i.rect(x + 4, 7, x + 4, 14, dark)
        i.rect(x, 13, x + 4, 13, darker)
        cl, cb, cd, _ = ramp(copper)
        i.rect(x, 4, x + 4, 6, cb)
        i.rect(x + 1, 2, x + 3, 3, cb)
        i.px(x + 2, 1, cb)
        i.rect(x + 4, 4, x + 4, 6, cd)
        i.pxs([(x + 1, 3), (x + 1, 4), (x + 1, 5)], cl)


@design
def wide_lens(i, c):
    # Magnifying glass with a wide blue lens.
    i.line([(9, 10), (13, 14)], WOOD, 3)
    i.ell(1, 1, 11, 11, "#808898")
    i.ell(2, 2, 10, 10, c)
    i.ell(5, 5, 10, 10, shade(c, -0.12))
    i.pxs([(4, 4), (5, 3), (3, 5), (4, 5)], SHINE)


@design
def blast_powder(i, c):
    # Powder keg with a lit fuse.
    i.box(2, 5, 12, 14, WOOD)
    i.rect(2, 7, 12, 7, "#606870")
    i.rect(2, 12, 12, 12, "#606870")
    i.rect(5, 9, 9, 10, (30, 20, 26, 255))
    i.pxs([(6, 9), (8, 10)], c)
    i.pxs([(10, 4), (11, 3), (12, 2)], "#d8c8a0")
    i.pxs([(13, 1), (13, 2), (14, 1), (12, 1)], c)
    i.px(13, 0, (255, 240, 140, 255))


@design
def frost_charm(i, c):
    # Snowflake charm hanging from a string.
    i.line([(7, 1), (7, 3)], "#c0b090")
    light, base, dark, _ = ramp(c)
    i.ell(2, 3, 12, 13, dark)
    i.ell(3, 4, 11, 12, base)
    for points in (((7, 5), (7, 11)), ((4, 8), (10, 8)), ((5, 6), (9, 10)), ((9, 6), (5, 10))):
        i.line(list(points), WHITE)
    i.px(7, 8, light)


@design
def long_chill(i, c):
    # Hourglass with ice for sand, frost on the frame.
    light, base, dark, _ = ramp(c)
    i.box(2, 1, 13, 2, WOOD)
    i.box(2, 13, 13, 14, WOOD)
    i.poly([(4, 3), (11, 3), (8, 8), (7, 8)], (210, 235, 245, 255))
    i.poly([(7, 8), (8, 8), (11, 12), (4, 12)], (210, 235, 245, 255))
    i.poly([(5, 4), (10, 4), (8, 7), (7, 7)], base)
    i.poly([(7, 10), (8, 10), (10, 12), (5, 12)], dark)
    i.px(7, 9, base)
    i.pxs([(3, 3), (12, 12), (12, 3)], WHITE)


@design
def daze_bell(i, c):
    bell(i, c)
    i.pxs([(1, 2), (14, 3), (13, 13)], (255, 255, 200, 255))


@design
def venom_sac(i, c):
    # A snake fang dripping green venom.
    light, base, dark, darker = ramp(c)
    i.poly([(3, 1), (12, 1), (11, 4), (9, 10), (7, 12), (6, 8), (4, 4)], (245, 240, 225, 255))
    i.poly([(8, 1), (12, 1), (11, 4), (9, 10), (7, 12)], (205, 198, 180, 255))
    i.rect(3, 1, 12, 1, (220, 120, 130, 255))
    i.ell(5, 11, 9, 15, base)
    i.px(6, 12, light)
    i.px(7, 11, base)


@design
def slow_rot(i, c):
    # A rotting mushroom with spores.
    light, base, dark, darker = ramp(c)
    i.rect(6, 8, 9, 14, "#d8d0b0")
    i.rect(9, 8, 9, 14, "#a8a080")
    i.ell(1, 2, 14, 10, dark)
    i.ell(1, 2, 13, 9, base)
    i.rect(1, 8, 14, 9, darker)
    i.pxs([(4, 4), (5, 4), (9, 3), (10, 6), (6, 6)], light)
    i.pxs([(2, 1), (12, 0), (14, 4)], light)


@design
def red_ink(i, c):
    # Red ink pot with a quill.
    light, base, dark, darker = ramp(c)
    i.ell(2, 7, 11, 14, "#304050")
    i.ell(3, 8, 10, 13, "#4a6070")
    i.rect(4, 5, 9, 7, "#304050")
    i.rect(4, 5, 9, 5, base)
    i.pxs([(4, 9), (5, 9)], (140, 170, 190, 255))
    i.line([(7, 6), (13, 0)], "#f0f0f0")
    i.line([(8, 6), (14, 1)], "#d0d0e0")
    i.pxs([(12, 3), (11, 4), (13, 2)], (230, 230, 240, 255))
    i.px(7, 7, base)


@design
def long_mark(i, c):
    # A book with a long red bookmark ribbon.
    light, base, dark, darker = ramp(c)
    i.box(2, 2, 12, 12, "#8060a0")
    i.rect(3, 11, 12, 12, "#f0e8d8")
    i.rect(2, 2, 3, 12, "#604080")
    i.rect(8, 1, 10, 14, base)
    i.rect(10, 1, 10, 14, dark)
    i.pxs([(8, 14), (10, 14)], base)
    i.px(9, 14, (0, 0, 0, 0))


@design
def hive_mind(i, c):
    # A chunk of honeycomb with a bee on it.
    light, base, dark, darker = ramp(c)
    i.grid(1, 3, [
        ".dd..dd..dd.",
        "dbbddbbddbbd",
        "dlbddlbddlbd",
        "dbbddbbddbbd",
        ".dd..dd..dd.",
        "...dd..dd...",
        "..dbbddbbd..",
        "..dlbddlbd..",
        "..dbbddbbd..",
        "...dd..dd...",
    ], {"d": dark, "b": base, "l": light})
    i.pxs([(2, 8), (2, 9), (11, 8)], base)  # honey drips
    i.grid(10, 0, ["ww..", "ykyk", ".kyk"], {"w": WHITE, "y": GOLD, "k": INK})


@design
def feather_fletching(i, c):
    # A single big feather with a quill.
    light, base, dark, _ = ramp(c)
    i.poly([(13, 1), (9, 2), (4, 7), (3, 11), (5, 11), (10, 7), (14, 3)], base)
    i.poly([(14, 2), (14, 4), (10, 8), (5, 11), (9, 6)], dark)
    i.line([(13, 2), (3, 12)], light)
    i.line([(3, 12), (1, 14)], "#d0c0a0")
    for x, y in ((6, 6), (9, 3), (8, 9)):
        i.px(x, y, (0, 0, 0, 0))


@design
def ground_spikes(i, c):
    # Spikes bursting out of the dirt.
    light, base, dark, _ = ramp(c)
    i.box(1, 12, 14, 14, "#6a4a30")
    for x, h in ((2, 6), (6, 10), (10, 7)):
        i.poly([(x, 12), (x + 4, 12), (x + 2, 12 - h)], base)
        i.line([(x + 2, 12 - h), (x + 2, 11)], light)
        i.line([(x + 3, 12 - h + 2), (x + 4, 11)], dark)
    i.pxs([(4, 13), (11, 13)], "#8a6a48")


@design
def eagle_eye(i, c):
    # An eagle's head in profile with a sharp eye.
    i.grid(1, 2, [
        "....wwwww.....",
        "..wwwwwwwww...",
        ".wwwwkkwwwwYY.",
        "wwwwwkwwwwwYYY",
        "wwwwwwwwwwYYyY",
        "bbwwwwwwww.yYy",
        "bbbbwwwwww..y.",
        "bbbbbbbww.....",
        ".bbbbbbbb.....",
        "..bbbbbbbb....",
        "...bbbbbbb....",
        ".....bbbb.....",
    ], {"w": (245, 240, 230, 255), "k": INK, "Y": hexc(c), "y": shade(c, -0.2),
        "b": (120, 80, 50, 255)})
    i.px(6, 4, (255, 210, 60, 255))


@design
def close_quarters(i, c):
    # A boxing glove seen from the side, thumb tucked in front.
    light, base, dark, darker = ramp(c)
    i.grid(1, 1, [
        "....llllll....",
        "..llbbbbbbbb..",
        ".lbbbbbbbbbbd.",
        ".lbbbbbbbbbbbd",
        "lbbbbbbbbbbbbd",
        "lbbddddbbbbbbd",
        "lbbbbbbdbbbbbd",
        ".dbbbbbbdbbbd.",
        "..ddbbbbbbdd..",
        "...wwwwwwww...",
        "...wwwwwwwwg..",
        "...bbbbbbbbd..",
        "...wwwwwwwwg..",
    ], {"l": light, "b": base, "d": dark, "w": (240, 236, 228, 255), "g": (190, 184, 176, 255)})
    i.pxs([(4, 3), (5, 2)], SHINE)


@design
def bird_net(i, c):
    # A butterfly net on a pole.
    i.line([(1, 14), (7, 8)], WOOD, 2)
    i.ell(5, 1, 14, 10, hexc("#808070"))
    i.ell(6, 2, 13, 9, (0, 0, 0, 0))
    for x in range(7, 13, 2):
        i.line([(x, 3), (x, 8)], c)
    for y in range(3, 9, 2):
        i.line([(7, y), (12, y)], c)


@design
def giant_slayer(i, c):
    # A slingshot with a red stone.
    i.line([(7, 9), (7, 14)], WOOD, 2)
    i.line([(7, 9), (3, 3)], WOOD, 2)
    i.line([(8, 9), (12, 3)], WOOD, 2)
    i.pxs([(3, 2), (4, 2), (12, 2), (13, 2)], "#c09060")
    i.line([(3, 3), (7, 6)], "#d0c0b0")
    i.line([(13, 3), (9, 6)], "#d0c0b0")
    i.ball(6, 5, 9, 8, c)


@design
def can_opener(i, c):
    # A tin can with its lid peeled back.
    light, base, dark, darker = ramp(c)
    i.rect(2, 6, 11, 14, base)
    i.rect(2, 6, 3, 14, light)
    i.rect(10, 6, 11, 14, dark)
    for y in (8, 11):
        i.rect(2, y, 11, y, dark)
    i.ell(2, 4, 11, 8, darker)
    i.ell(3, 5, 10, 7, (60, 40, 40, 255))
    i.poly([(8, 5), (12, 1), (14, 3), (11, 6)], light)
    i.line([(9, 5), (13, 1)], WHITE)


@design
def tax_collector(i, c):
    # A tied money bag stamped with a coin.
    light, base, dark, darker = ramp(c)
    i.ball(2, 5, 13, 14, "#c09060")
    i.poly([(5, 2), (10, 2), (8, 5), (7, 5)], "#c09060")
    i.rect(5, 5, 10, 5, "#704020")
    coin(i, 5, 8, 10, 13, c)


@design
def spare_parts(i, c):
    # A crate with a bolt and a gear sticking out.
    i.box(1, 6, 12, 14, c)
    i.rect(1, 9, 12, 9, shade(c, -0.25))
    i.line([(2, 7), (11, 13)], shade(c, -0.15))
    i.ell(8, 1, 14, 7, "#909aa8")
    i.ell(10, 3, 12, 5, "#3a3040")
    i.rect(3, 2, 5, 6, "#c0c8d0")
    i.rect(2, 2, 6, 3, "#909aa8")


@design
def gift_box(i, c):
    light, base, dark, darker = ramp(c)
    i.box(2, 7, 13, 14, c)
    i.box(1, 5, 14, 7, c)
    i.rect(7, 5, 8, 14, GOLD)
    i.rect(8, 5, 8, 14, shade(GOLD, -0.15))
    i.ell(3, 1, 7, 5, GOLD)
    i.ell(8, 1, 12, 5, GOLD)
    i.ell(5, 3, 6, 4, darker)
    i.ell(9, 3, 10, 4, darker)


@design
def first_aid(i, c):
    # A first aid kit.
    i.rect(5, 2, 10, 4, "#808080")
    i.rect(6, 3, 9, 4, (0, 0, 0, 0))
    i.box(1, 4, 14, 14, (240, 236, 228, 255))
    i.rect(6, 6, 9, 13, c)
    i.rect(3, 8, 12, 11, c)
    i.pxs([(6, 6), (3, 8)], shade(c, 0.2))


@design
def piggy_bank(i, c):
    light, base, dark, darker = ramp(c)
    i.ell(1, 4, 13, 13, dark)
    i.ell(1, 4, 12, 12, base)
    i.rect(3, 12, 4, 14, dark)
    i.rect(9, 12, 10, 14, dark)
    i.poly([(3, 5), (4, 2), (6, 5)], base)  # ear
    i.ell(11, 7, 14, 10, light)  # snout
    i.pxs([(12, 8), (13, 8)], darker)
    i.px(9, 6, INK)
    i.rect(5, 4, 8, 4, darker)  # coin slot
    i.pxs([(3, 7), (4, 6)], light)
    coin(i, 5, 0, 8, 3)


@design
def buddy_system(i, c):
    # Two bricks side by side with a heart above (better together).
    i.box(1, 9, 7, 13, c)
    i.box(8, 9, 14, 13, c)
    i.pxs([(3, 11), (11, 11)], shade(c, -0.3))
    heart = (240, 80, 100, 255)
    i.grid(4, 1, [".hh.hh.", "hwhhhhh", "hhhhhhh", ".hhhhh.", "..hhh..", "...h..."],
           {"h": heart, "w": WHITE})


@design
def brace_posts(i, c):
    # Two wooden posts with a cross brace.
    for x in (2, 11):
        i.box(x, 1, x + 2, 14, c)
    i.line([(4, 3), (11, 12)], shade(c, -0.1), 2)
    i.line([(4, 12), (11, 3)], shade(c, 0.05), 2)
    i.pxs([(3, 3), (12, 3), (3, 12), (12, 12)], "#606870")


@design
def sticky_mortar(i, c):
    # A trowel with a glob of sticky mortar.
    light, base, dark, darker = ramp(c)
    i.ell(1, 8, 9, 14, dark)
    i.ell(1, 8, 8, 13, base)
    i.pxs([(3, 9), (4, 9)], light)
    i.px(5, 14, base)
    i.poly([(6, 6), (12, 1), (14, 3), (9, 9)], METAL)
    i.line([(7, 7), (13, 2)], WHITE)
    i.line([(9, 8), (5, 12)], WOOD, 2)


@design
def nettle_hedge(i, c):
    # A nettle leaf bristling with stinging hairs.
    light, base, dark, darker = ramp(c)
    i.poly([(2, 13), (3, 5), (8, 1), (13, 2), (12, 8), (7, 13)], base)
    i.poly([(2, 13), (12, 3), (12, 8), (7, 13)], dark)
    i.line([(2, 13), (11, 4)], light)
    i.pxs([(1, 6), (5, 1), (14, 6), (10, 13), (14, 1), (1, 10)], WHITE)


@design
def bulk_bricks(i, c):
    # A neat pyramid of bricks with a price tag.
    for x0, y0 in ((1, 11), (6, 11), (11, 11)):
        i.box(x0, y0, x0 + 4, y0 + 2, c)
    for x0, y0 in ((3, 8), (8, 8)):
        i.box(x0, y0, x0 + 4, y0 + 2, c)
    i.box(5, 5, 9, 7, c)
    i.poly([(9, 0), (14, 0), (14, 4), (11, 5), (9, 4)], (240, 236, 228, 255))
    i.px(10, 1, INK)
    i.line([(11, 2), (13, 2)], (60, 160, 60, 255))
    i.line([(13, 1), (13, 3)], (60, 160, 60, 255))


# --- rare --------------------------------------------------------------------

@design
def lucky_coin(i, c):
    coin(i, 1, 1, 14, 14, c)
    # Four-leaf clover stamped on it.
    green = (70, 150, 60, 255)
    for x, y in ((5, 5), (8, 5), (5, 8), (8, 8)):
        i.rect(x, y, x + 1, y + 1, green)
    i.px(7, 7, green)
    i.px(8, 10, green)


@design
def critical_eye(i, c):
    # A starburst "critical hit" with a "!".
    light, base, dark, _ = ramp(c)
    i.poly([(7, 0), (9, 5), (15, 4), (11, 8), (14, 14), (8, 11), (2, 15), (4, 9), (0, 5), (6, 5)], dark)
    i.poly([(7, 2), (9, 6), (13, 5), (10, 8), (12, 12), (8, 10), (4, 13), (5, 9), (2, 6), (6, 6)], base)
    i.rect(7, 4, 8, 8, (200, 40, 40, 255))
    i.rect(7, 10, 8, 10, (200, 40, 40, 255))


@design
def bargain_scroll(i, c):
    # A rolled contract with a red price seal.
    light, base, dark, _ = ramp(c)
    i.rect(3, 2, 12, 13, base)
    i.rect(12, 3, 12, 13, dark)
    i.ell(2, 1, 13, 3, light)
    i.ell(2, 12, 13, 14, dark)
    for y in (5, 7, 9):
        i.line([(5, y), (10, y)], shade(c, -0.3))
    i.ell(8, 8, 13, 13, (200, 50, 50, 255))
    i.pxs([(10, 9), (11, 10), (10, 11), (9, 10)], (255, 120, 110, 255))


@design
def recycling_bin(i, c):
    light, base, dark, darker = ramp(c)
    i.poly([(2, 4), (13, 4), (12, 14), (3, 14)], base)
    i.poly([(10, 4), (13, 4), (12, 14), (10, 14)], dark)
    i.rect(1, 2, 14, 4, light)
    i.rect(6, 1, 9, 1, light)
    # Two chasing arrows.
    i.pxs([(5, 7), (6, 6), (7, 6), (8, 6), (9, 7), (9, 8), (10, 7)], WHITE)
    i.pxs([(10, 10), (9, 11), (8, 11), (7, 11), (6, 10), (6, 9), (5, 10)], WHITE)


@design
def piercing_tips(i, c):
    # A steel arrowhead punching through a plate.
    light, base, dark, _ = ramp(c)
    i.box(1, 8, 9, 10, "#70707a")
    i.poly([(14, 1), (11, 9), (9, 7)], base)
    i.poly([(14, 1), (6, 4), (8, 6)], light)
    i.poly([(9, 7), (8, 6), (11, 9)], dark)
    i.line([(8, 7), (2, 13)], WOOD, 2)
    i.pxs([(4, 9), (5, 8), (6, 10)], (40, 30, 30, 255))


@design
def shrapnel(i, c):
    # A grenade with its pin.
    light, base, dark, darker = ramp("#70884c")
    i.ball(2, 4, 12, 14, "#70884c")
    for y in (7, 10):
        i.line([(3, y), (11, y)], dark)
    i.line([(7, 5), (7, 13)], dark)
    i.box(5, 2, 9, 4, "#909aa8")
    i.ell(10, 0, 14, 4, c)
    i.ell(11, 1, 13, 3, (0, 0, 0, 0))
    i.pxs([(4, 6), (5, 5)], light)


@design
def cold_snap(i, c):
    # A row of icicles, the middle one a fang.
    light, base, dark, _ = ramp(c)
    i.box(1, 1, 14, 3, (230, 245, 255, 255))
    for x, h in ((1, 5), (4, 9), (8, 12), (11, 7)):
        i.poly([(x, 4), (x + 3, 4), (x + 1, 4 + h)], base)
        i.line([(x, 4), (x + 1, 3 + h)], light)
        i.px(x + 2, 5, dark)
    i.px(9, 6, WHITE)


@design
def plague_jar(i, c):
    # A jar of green plague with a skull.
    i.box(4, 1, 11, 2, WOOD)
    i.rect(3, 3, 12, 14, (180, 210, 220, 255))
    light, base, dark, _ = ramp(c)
    i.rect(4, 5, 11, 13, base)
    i.rect(4, 11, 11, 13, dark)
    i.rect(3, 3, 3, 13, SHINE)
    i.grid(5, 6, [".###.", "#.#.#", "#####", ".#.#."], {"#": (240, 240, 230, 255)})


@design
def chain_link(i, c):
    light, base, dark, _ = ramp(c)
    for x, y in ((1, 9), (5, 5), (9, 1)):
        i.ell(x, y, x + 5, y + 5, dark)
        i.ell(x, y, x + 4, y + 4, base)
        i.ell(x + 2, y + 2, x + 3, y + 3, (0, 0, 0, 0))
        i.px(x + 1, y + 1, light)


@design
def spare_arrows(i, c):
    # A quiver full of arrows.
    for k, x in enumerate((4, 7, 10)):
        i.line([(x, 2), (x, 8)], "#c09060")
        i.pxs([(x - 1, 1), (x, 0), (x + 1, 1), (x, 1)], METAL)
    i.poly([(2, 7), (12, 7), (11, 14), (3, 14)], c)
    i.poly([(9, 7), (12, 7), (11, 14), (9, 14)], shade(c, -0.15))
    i.rect(2, 7, 12, 8, shade(c, -0.25))
    i.line([(3, 11), (11, 11)], shade(c, -0.25))


@design
def battering_ram(i, c):
    # A ram's head with curled horns.
    light, base, dark, darker = ramp(c)
    i.ell(4, 3, 11, 13, (230, 222, 205, 255))
    i.ell(5, 9, 10, 14, (200, 190, 175, 255))
    i.pxs([(6, 12), (9, 12)], INK)
    i.pxs([(5, 7), (10, 7)], INK)
    for x, flip in ((0, 1), (11, -1)):
        i.ell(x, 2, x + 4, 8, dark)
        i.ell(x + 1, 3, x + 3, 6, base)
        i.px(x + 2, 4, darker)


@design
def acid_flask(i, c):
    flask(i, c)
    i.pxs([(7, 15), (8, 15)], c)  # acid dripping through the bottom


@design
def colony(i, c):
    # A papery nest hanging from a branch.
    i.line([(1, 1), (14, 1)], WOOD)
    light, base, dark, _ = ramp(c)
    i.ell(3, 2, 12, 14, dark)
    i.ell(3, 2, 11, 13, base)
    for y in (5, 8, 11):
        i.line([(4, y), (11, y)], dark)
    i.ell(6, 10, 9, 13, INK)
    i.pxs([(1, 9), (14, 6)], (40, 30, 30, 255))
    i.pxs([(1, 8), (14, 5)], WHITE)


@design
def interest_ledger(i, c):
    # An open ledger with a rising graph.
    i.poly([(1, 4), (7, 5), (7, 14), (1, 13)], (240, 236, 228, 255))
    i.poly([(8, 5), (14, 4), (14, 13), (8, 14)], (225, 218, 205, 255))
    i.rect(7, 5, 8, 14, (160, 140, 120, 255))
    i.line([(2, 12), (5, 9), (8, 10), (12, 6)], (60, 160, 60, 255))
    i.pxs([(12, 5), (13, 6), (11, 5), (12, 4)], (60, 160, 60, 255))
    coin(i, 9, 0, 13, 4, c)


@design
def skyward(i, c):
    # A spread wing with gust lines.
    light, base, dark, _ = ramp(c)
    i.grid(1, 1, [
        "..........llll",
        "......llllbbbl",
        "...lllbbbbbbbl",
        ".lllbbbbbbbbdl",
        "llbbbbbbbbbdd.",
        "..ddbbbbbbdd..",
        "....ddbbbdd...",
        "......dddd....",
        "........dd....",
    ], {"l": light, "b": base, "d": dark})
    for y, x0, x1 in ((11, 2, 8), (13, 5, 12)):
        i.line([(x0, y), (x1, y)], WHITE)
    i.px(9, 12, WHITE)


@design
def flat_pack(i, c):
    # A flat cardboard box with an allen key.
    light, base, dark, _ = ramp(c)
    i.poly([(1, 8), (8, 5), (14, 8), (7, 11)], light)
    i.poly([(1, 8), (7, 11), (7, 14), (1, 11)], base)
    i.poly([(7, 11), (14, 8), (14, 11), (7, 14)], dark)
    i.line([(4, 7), (11, 10)], shade(c, -0.25))
    i.line([(9, 1), (9, 4)], "#505860", 2)
    i.line([(9, 1), (13, 1)], "#505860", 2)


# --- epic --------------------------------------------------------------------

@design
def philosophers_stone(i, c):
    # A glowing faceted stone with sparkles.
    light, base, dark, darker = ramp(c)
    i.poly([(7, 2), (12, 5), (12, 11), (7, 14), (3, 11), (3, 5)], base)
    i.poly([(7, 8), (12, 5), (12, 11), (7, 14)], dark)
    i.poly([(7, 8), (3, 5), (7, 2), (12, 5)], light)
    i.px(6, 4, WHITE)
    sparkle(i, 2, 2)
    sparkle(i, 13, 13)
    i.px(14, 2, WHITE)


@design
def executioners_axe(i, c):
    light, base, dark, darker = ramp(c)
    i.line([(3, 14), (11, 2)], WOOD, 2)
    i.poly([(7, 1), (14, 3), (14, 10), (10, 8), (8, 5)], base)
    i.poly([(11, 2), (14, 3), (14, 10), (12, 9)], light)
    i.line([(14, 3), (14, 10)], WHITE)
    i.pxs([(9, 4), (10, 6)], dark)


@design
def sky_hooks(i, c):
    # A grappling hook trailing rope.
    light, base, dark, _ = ramp(c)
    i.rect(7, 2, 8, 10, base)
    i.rect(8, 2, 8, 10, dark)
    i.ell(6, 0, 9, 3, dark)
    for side in (-1, 1):
        x = 7 if side < 0 else 8
        i.line([(x, 10), (x + 4 * side, 12), (x + 6 * side, 8)], base, 2)
        i.px(x + 6 * side, 7, light)
    i.line([(7, 2), (3, 0)], "#c0a070")


@design
def golden_goose(i, c):
    # A golden egg in a straw nest.
    light, base, dark, darker = ramp(c)
    i.ell(1, 9, 14, 14, "#a07840")
    i.ball(4, 1, 11, 11, c)
    i.ell(1, 9, 14, 14, (0, 0, 0, 0)) if False else None
    i.rect(2, 10, 13, 12, "#c09858")
    for x in (2, 5, 8, 11):
        i.line([(x, 10), (x + 3, 13)], "#806030")
    sparkle(i, 13, 3)


@design
def storm_core(i, c):
    # A glowing orb with a bolt inside.
    light, base, dark, darker = ramp(c)
    i.ball(1, 1, 14, 14, c)
    bolt = (255, 255, 210, 255)
    i.poly([(9, 2), (5, 8), (8, 8), (6, 13), (11, 6), (8, 6)], bolt)


@design
def triple_shot(i, c):
    # Three arrows fanned out from one point.
    shaft = "#c09060"
    tips = [(3, 2), (13, 2), (8, 1)]
    for tx, ty in tips:
        i.line([(7, 14), (tx, ty + 2)], shaft)
    i.grid(2, 0, [".m.", "mmm"], {"m": METAL})
    i.grid(12, 0, [".m.", "mmm"], {"m": METAL})
    i.grid(7, 0, [".m.", "mmm"], {"m": METAL})
    feather = hexc(c)
    i.grid(5, 12, ["f.f.f", ".fff.", "..f.."], {"f": feather})


@design
def doom_bell(i, c):
    bell(i, shade(c, -0.15))
    bone = (240, 235, 225, 255)
    i.grid(5, 4, [".###.", "#####", "#k#k#", "#####", ".#.#."], {"#": bone, "k": INK})


@design
def bastion(i, c):
    # A castle tower with battlements and a flag.
    light, base, dark, darker = ramp(c)
    i.box(3, 5, 12, 14, "#a0a0a8")
    for x in (3, 6, 9, 12):
        i.rect(x, 3, x, 4, "#a0a0a8")
    i.rect(3, 3, 4, 4, "#a0a0a8")
    i.rect(6, 3, 7, 4, "#a0a0a8")
    i.rect(9, 3, 10, 4, "#a0a0a8")
    i.rect(5, 3, 5, 4, (0, 0, 0, 0))
    i.rect(8, 3, 8, 4, (0, 0, 0, 0))
    i.rect(11, 3, 11, 4, (0, 0, 0, 0))
    i.ell(6, 10, 9, 14, INK)
    i.rect(6, 12, 9, 14, INK)
    i.pxs([(5, 7), (10, 7), (8, 6)], "#80808a")
    i.line([(13, 0), (13, 3)], WOOD)
    i.rect(10, 0, 12, 1, c)


# --- archetype relics (rare/epic build-arounds) ------------------------------

@design
def packed_ranks(i, c):
    # A shield wall: three soldiers' shields side by side, helmets behind.
    for x in (2, 7, 12):
        i.ell(x - 2, 1, x + 2, 5, "#8890a0")
        i.px(x - 1, 2, SHINE)
    for x, color in ((0, c), (5, shade(c, 0.12)), (10, c)):
        light, base, dark, darker = ramp(color)
        i.rect(x, 5, x + 4, 11, base)
        i.poly([(x, 11), (x + 4, 11), (x + 2, 14)], base)
        i.rect(x + 4, 5, x + 4, 11, dark)
        i.rect(x, 5, x + 4, 5, light)
        i.rect(x + 2, 6, x + 2, 12, (240, 236, 228, 255))
        i.rect(x + 1, 8, x + 3, 8, (240, 236, 228, 255))


@design
def concussion(i, c):
    # A dented helmet with stars spinning above it.
    i.ell(2, 6, 13, 16, "#7c8494")
    i.ell(2, 6, 12, 15, "#a8b0bc")
    i.rect(1, 12, 14, 14, "#5c6474")
    i.rect(1, 12, 14, 12, "#8890a0")
    i.pxs([(8, 8), (9, 9), (8, 10)], "#5c6474")  # dent
    i.px(5, 8, SHINE)
    for x, y in ((2, 3), (7, 1), (12, 3)):
        sparkle(i, x, y, hexc(c))
        i.px(x, y, WHITE)


@design
def festering(i, c):
    # A bubbling green ooze with popping blisters.
    light, base, dark, darker = ramp(c)
    i.ell(1, 6, 14, 14, darker)
    i.ell(1, 6, 13, 13, base)
    i.ell(4, 3, 10, 9, base)
    i.ell(3, 9, 6, 12, dark)
    i.ell(8, 8, 12, 12, dark)
    i.pxs([(4, 10), (9, 9)], light)
    i.px(6, 4, light)
    i.ell(10, 1, 13, 4, light)
    i.px(11, 2, WHITE)
    i.pxs([(2, 3), (14, 6)], light)


@design
def affliction(i, c):
    # A cursed voodoo doll stuck with pins.
    cloth, cloth_b, cloth_d, _ = ramp("#c8a070")
    i.ell(4, 1, 11, 7, cloth_b)
    i.rect(5, 7, 10, 12, cloth_b)
    i.rect(2, 8, 13, 9, cloth_b)
    i.rect(5, 13, 6, 14, cloth_b)
    i.rect(9, 13, 10, 14, cloth_b)
    i.rect(10, 7, 10, 12, cloth_d)
    i.pxs([(6, 3), (9, 3)], INK)
    i.line([(6, 5), (9, 5)], cloth_d)
    i.rect(6, 9, 9, 11, cloth_d)  # stitched patch
    for (x, y), color in (((12, 2), c), ((3, 6), "#60d0ff"), ((12, 11), "#90e050")):
        i.line([(x, y), (7 if x > 7 else 8, y + 3 if y < 8 else y - 1)], METAL)
        i.ell(x - 1, y - 1, x + 1, y + 1, color)


@design
def long_road(i, c):
    # A long winding road vanishing into the distance.
    light, base, dark, _ = ramp(c)
    i.rect(1, 1, 14, 14, "#5c8a48")
    i.rect(1, 1, 14, 3, "#88b8e0")
    i.poly([(2, 14), (8, 14), (11, 10), (5, 8), (9, 5), (8, 4), (3, 7), (8, 10)], base)
    i.line([(5, 13), (8, 10)], light)
    i.pxs([(6, 7), (7, 6)], light)
    i.rect(12, 6, 12, 12, WOOD)  # signpost
    i.rect(10, 6, 14, 7, "#c09060")


@design
def watchtower(i, c):
    # A wooden lookout tower on stilts.
    light, base, dark, darker = ramp(c)
    i.line([(4, 7), (2, 14)], dark, 2)
    i.line([(11, 7), (13, 14)], dark, 2)
    i.line([(4, 9), (12, 13)], darker)
    i.line([(11, 9), (3, 13)], darker)
    i.box(2, 4, 13, 7, c)
    i.rect(4, 5, 5, 6, INK)
    i.rect(10, 5, 11, 6, INK)
    i.poly([(1, 4), (7, 0), (8, 0), (14, 4)], "#b05040")
    i.line([(7, 0), (14, 4)], "#803028")


@design
def exposed_flank(i, c):
    # A cracked shield with a red target on the weak spot.
    light, base, dark, darker = ramp("#9098a8")
    i.poly([(2, 1), (13, 1), (13, 8), (8, 14), (7, 14), (2, 8)], base)
    i.poly([(8, 1), (13, 1), (13, 8), (8, 14)], dark)
    i.line([(2, 1), (13, 1)], light)
    i.pxs([(6, 1), (7, 2), (6, 3), (7, 4), (6, 5)], INK)  # crack
    red = hexc(c)
    i.ell(7, 5, 12, 10, red)
    i.ell(8, 6, 11, 9, WHITE)
    i.ell(9, 7, 10, 8, red)


@design
def labyrinth(i, c):
    # A hedge maze seen from above.
    light, base, dark, darker = ramp(c)
    i.rect(1, 1, 14, 14, "#d8c8a0")
    i.grid(1, 1, [
        "##############",
        "#.....#......#",
        "#.###.#.####.#",
        "#.#...#....#.#",
        "#.#.######.#.#",
        "#.#.#....#.#.#",
        "#...#.##.#...#",
        "#####.#..###.#",
        "#.....#.##...#",
        "#.#####.#..###",
        "#.......#.#..#",
        "#.#######.##.#",
        "#.........#...",
        "##############",
    ], {"#": base})
    i.pxs([(13, 13), (14, 13)], GOLD)


@design
def veterans_medal(i, c):
    # A medal hanging from a striped ribbon.
    i.poly([(3, 1), (7, 1), (9, 7), (6, 7)], "#c03838")
    i.poly([(8, 1), (12, 1), (9, 7), (8, 4)], "#3858c0")
    i.line([(5, 1), (7, 6)], WHITE)
    coin(i, 3, 6, 12, 15, c)
    sparkle(i, 7, 10, shade(c, 0.25))


@design
def elite_training(i, c):
    # A sergeant's badge: three bold chevrons on a dark shield.
    i.poly([(1, 1), (14, 1), (14, 10), (8, 15), (7, 15), (1, 10)], "#2e2a3c")
    light, base, dark, _ = ramp(c)
    for y in (2, 6, 10):
        for k in range(6):
            i.rect(2 + k, y + k // 2, 2 + k, y + k // 2 + 1, base)
            i.rect(13 - k, y + k // 2, 13 - k, y + k // 2 + 1, base)
            i.px(2 + k, y + k // 2, light)
            i.px(13 - k, y + k // 2, light)


@design
def lone_wolf(i, c):
    # A wolf howling at the moon.
    i.ell(8, 0, 14, 6, (240, 236, 210, 255))
    i.pxs([(10, 2), (12, 4)], (210, 205, 180, 255))
    fur, base, dark, darker = ramp(c)
    i.grid(1, 3, [
        "..........d...",
        ".........dbd..",
        "........dbbb..",
        ".......dbbbbbb",
        "......dbbbbkbb",
        ".....bbbbbbb..",
        "...bbbbbbbb...",
        "..bbbbbbbbb...",
        ".bbbbbbbbbb...",
        ".bbbbddbbbb...",
        "bbbb...dbbb...",
        "ddd.....ddd...",
    ], {"b": base, "d": dark, "k": INK})
    i.pxs([(9, 9), (8, 10), (7, 11)], fur)


@design
def champion(i, c):
    # A jeweled golden crown.
    light, base, dark, darker = ramp(c)
    i.poly([(1, 4), (4, 8), (7, 2), (8, 2), (11, 8), (14, 4), (13, 12), (2, 12)], base)
    i.rect(2, 10, 13, 12, dark)
    i.rect(2, 10, 13, 10, light)
    i.pxs([(1, 3), (7, 1), (8, 1), (14, 3)], light)
    i.ell(6, 6, 9, 9, "#e03050")
    i.px(7, 7, WHITE)
    i.pxs([(4, 11), (11, 11)], "#40a0ff")
    sparkle(i, 13, 14, WHITE)

