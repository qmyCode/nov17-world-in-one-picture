#!/usr/bin/env python3
"""Draw the v4 entry poster: 'Tuesday 17 November 2026 - The Day in World News'.

Top-10 format: 39 verified stories (12 illustrated mains + 27 one-liners),
a dominant hero panel for the Kerch Bridge lead, a Day-in-Numbers strip,
a Stories-by-Region tally, a numbered dot-matrix world map, and a
per-region colour system shared by kicker chips, map pins and ALSO numbers.
Deterministic: pure Pillow drawing, no randomness, no clock.

Tooling only -- the shipped main.py just copies the committed entry.png.
Run:  python3 draw.py   (writes entry.png next to this file)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (250, 248, 243)
INK = (18, 18, 20)
GREY = (96, 96, 100)
ACCENT = (146, 30, 30)
RULE = (210, 205, 195)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF = FD + "DejaVuSerif.ttf"
SERIFB = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANSB = FD + "DejaVuSans-Bold.ttf"

REGIONS = {
    "EUROPE": (31, 78, 120),
    "MIDEAST": (146, 96, 16),
    "ASIA": (46, 107, 52),
    "AFRICA": (176, 84, 18),
    "AMERICAS": (110, 52, 148),
    "OCEANIA": (0, 121, 107),
    "GLOBAL": (84, 84, 84),
}
REGION_LABEL = {"MIDEAST": "MIDDLE EAST"}


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, xy, lines, font, fill, lh):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def centered(draw, y, text, font, fill):
    draw.text(((W - draw.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def tracked(draw, y, text, font, fill, spacing=6, cx=W / 2):
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += w + spacing
    return total


def fit_font(draw, text, path, size, max_w, min_size=8):
    while size > min_size and draw.textlength(text, font=F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def badge(draw, cx, cy, num, colour, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    t = str(num)
    f = F(SANSB, 10 if num < 10 else 9)
    draw.text((cx - draw.textlength(t, font=f) / 2, cy - 6), t, font=f, fill=(255, 255, 255))


def chip(draw, x, y, region, topic, h=18):
    label = REGION_LABEL.get(region, region) + " · " + topic
    f = F(SANSB, 10)
    w = draw.textlength(label, font=f) + 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=REGIONS[region])
    draw.text((x + 7, y + h // 2 - 6), label, font=f, fill=(255, 255, 255))
    return x + w


# ---------------------------------------------------------------- icons
def icon_ship(d, x, y, s):
    d.polygon([(x + 6, y + s - 14), (x + s - 4, y + s - 14), (x + s - 12, y + s - 5),
               (x + 12, y + s - 5)], fill=(70, 90, 110))
    d.rectangle([x + 14, y + s - 24, x + 30, y + s - 14], fill=(178, 60, 40))
    d.rectangle([x + 32, y + s - 24, x + 48, y + s - 14], fill=(52, 110, 70))
    d.rectangle([x + s - 22, y + 12, x + s - 12, y + s - 24], fill=(90, 90, 90))
    d.arc([x + 4, y + s - 6, x + s - 4, y + s + 4], 0, 180, fill=(70, 130, 180), width=2)


def icon_plane(d, x, y, s):
    d.ellipse([x + 6, y + 6, x + 26, y + 26], outline=(200, 40, 40), width=3)
    d.ellipse([x + s - 26, y + 6, x + s - 6, y + 26], outline=(40, 90, 180), width=3)
    d.polygon([(x + 8, y + s - 12), (x + s - 10, y + s - 22), (x + s - 4, y + s - 10),
               (x + 16, y + s - 4)], fill=(60, 60, 66))
    d.polygon([(x + s // 2 - 4, y + s - 20), (x + s // 2 + 8, y + s - 34),
               (x + s // 2 + 14, y + s - 18)], fill=(90, 90, 96))


def icon_chip(d, x, y, s):
    d.rounded_rectangle([x + 12, y + 12, x + s - 12, y + s - 12], radius=4,
                        outline=(30, 110, 60), width=3)
    for i in range(4):
        px = x + 16 + i * (s - 36) / 3
        d.line([px, y + 4, px, y + 12], fill=(30, 110, 60), width=2)
        d.line([px, y + s - 12, px, y + s - 4], fill=(30, 110, 60), width=2)
    d.rectangle([x + s // 2 - 7, y + s // 2 - 7, x + s // 2 + 7, y + s // 2 + 7],
                fill=(30, 110, 60))
    d.text((x + s // 2 - 8, y + s // 2 - 19), "AI", font=F(SANSB, 11), fill=(30, 110, 60))


def icon_cloud(d, x, y, s):
    d.ellipse([x + 8, y + 16, x + 34, y + 38], fill=(120, 130, 145))
    d.ellipse([x + 24, y + 8, x + 54, y + 38], fill=(120, 130, 145))
    d.rectangle([x + 14, y + 28, x + 50, y + 40], fill=(120, 130, 145))
    d.line([x + s - 14, y + 6, x + s - 22, y + 22], fill=(200, 40, 40), width=4)
    d.line([x + s - 22, y + 6, x + s - 14, y + 22], fill=(200, 40, 40), width=4)


def icon_jet(d, x, y, s):
    d.polygon([(x + 4, y + s - 16), (x + s - 14, y + 10), (x + s - 6, y + 12),
               (x + s - 12, y + s - 8), (x + 22, y + s - 6)], fill=(80, 88, 100))
    d.polygon([(x + 16, y + s - 14), (x + 30, y + s - 28), (x + 36, y + s - 12)],
              fill=(60, 66, 78))
    d.ellipse([x + s - 20, y + 12, x + s - 12, y + 20], fill=(240, 244, 248))
    d.line([x + 8, y + 20, x + 20, y + 30], fill=(190, 60, 50), width=2)
    d.line([x + 6, y + 28, x + 16, y + 38], fill=(190, 60, 50), width=2)


def icon_truck(d, x, y, s):
    d.rectangle([x + 6, y + 16, x + s - 20, y + s - 16], outline=(120, 84, 30), width=3)
    d.polygon([(x + s - 20, y + 24), (x + s - 8, y + 34), (x + s - 8, y + s - 16),
               (x + s - 20, y + s - 16)], outline=(120, 84, 30), width=3)
    d.rectangle([x + 13, y + 9, x + 25, y + 16], fill=(178, 60, 40))
    for cx in (x + 18, x + s - 16):
        d.ellipse([cx - 6, y + s - 16, cx + 6, y + s - 4], fill=(40, 40, 44))
    d.line([x + 12, y + 26, x + s - 26, y + 26], fill=(178, 60, 40), width=2)
    d.line([x + 12, y + 32, x + s - 26, y + 32], fill=(178, 60, 40), width=2)


def icon_robot(d, x, y, s):
    d.rounded_rectangle([x + 14, y + 14, x + s - 14, y + s - 14], radius=6,
                        outline=(90, 60, 130), width=3)
    d.ellipse([x + 22, y + 24, x + 30, y + 32], fill=(200, 40, 40))
    d.ellipse([x + s - 30, y + 24, x + s - 22, y + 32], fill=(200, 40, 40))
    d.line([x + 24, y + s - 22, x + s - 24, y + s - 22], fill=(90, 60, 130), width=3)
    d.line([x + s // 2, y + 14, x + s // 2, y + 6], fill=(90, 60, 130), width=3)
    d.ellipse([x + s // 2 - 3, y + 3, x + s // 2 + 3, y + 9], fill=(200, 40, 40))


def icon_parcel(d, x, y, s):
    d.rectangle([x + 10, y + 14, x + s - 10, y + s - 8], outline=(160, 90, 30), width=3)
    d.line([x + 10, y + 26, x + s - 10, y + 26], fill=(160, 90, 30), width=2)
    d.line([x + s // 2, y + 14, x + s // 2, y + 26], fill=(160, 90, 30), width=2)
    d.line([x + s - 24, y + 4, x + s - 10, y + 18], fill=(200, 40, 40), width=4)
    d.line([x + s - 10, y + 4, x + s - 24, y + 18], fill=(200, 40, 40), width=4)


def icon_leaf(d, x, y, s):
    d.polygon([(x + 12, y + s - 10), (x + 16, y + 18), (x + 30, y + 8),
               (x + s - 10, y + 10), (x + s - 14, y + 30), (x + 30, y + s - 14)],
              fill=(52, 130, 66))
    d.line([x + 14, y + s - 8, x + s - 14, y + 14], fill=(30, 90, 44), width=2)


def icon_virus(d, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, 13
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x2, y2 = cx + 19 * math.cos(rad), cy + 19 * math.sin(rad)
        d.line([cx, cy, x2, y2], fill=(178, 52, 40), width=3)
        d.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=(178, 52, 40))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 84, 60))
    d.ellipse([cx - 5, cy - 4, cx - 1, cy], fill=(240, 190, 170))
    d.ellipse([cx + 3, cy + 4, cx + 7, cy + 8], fill=(240, 190, 170))


def icon_trophy(d, x, y, s):
    d.polygon([(x + 16, y + 8), (x + s - 16, y + 8), (x + s - 20, y + 30),
               (x + s // 2 + 5, y + 36), (x + s // 2 - 5, y + 36), (x + 20, y + 30)],
              fill=(198, 152, 40))
    d.arc([x + 4, y + 10, x + 20, y + 28], 90, 270, fill=(198, 152, 40), width=3)
    d.arc([x + s - 20, y + 10, x + s - 4, y + 28], 270, 90, fill=(198, 152, 40), width=3)
    d.rectangle([x + s // 2 - 3, y + 36, x + s // 2 + 3, y + 44], fill=(150, 112, 30))
    d.rectangle([x + s // 2 - 11, y + 44, x + s // 2 + 11, y + 50], fill=(150, 112, 30))
    d.ellipse([x + s // 2 - 5, y + 15, x + s // 2 + 5, y + 25], fill=(250, 250, 250))


ICONS = {2: icon_ship, 3: icon_plane, 4: icon_chip, 5: icon_cloud, 6: icon_jet,
         7: icon_truck, 8: icon_robot, 9: icon_parcel, 10: icon_leaf,
         11: icon_virus, 12: icon_trophy}


def bridge_art(d, x0, y0, x1, y1):
    """Kerch Bridge scene for the hero panel: strait, towers, collapsed span."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y0 + h * 0.52], fill=(206, 224, 236))
    d.rectangle([x0, y0 + h * 0.52, x1, y1], fill=(88, 138, 178))
    for i in range(6):
        yy = y0 + h * (0.60 + i * 0.07)
        d.line([x0 + (i % 3) * 46, yy, x0 + (i % 3) * 46 + 74, yy],
               fill=(140, 180, 205), width=2)
    deck = y0 + h * 0.50
    for fx in (0.16, 0.84):
        tx = x0 + w * fx
        d.rectangle([tx - 5, y0 + h * 0.10, tx + 5, deck], fill=(70, 74, 82))
        d.polygon([(tx - 34, deck), (tx, y0 + h * 0.10), (tx + 34, deck)],
                  outline=(70, 74, 82), width=2)
    d.rectangle([x0, deck - 4, x0 + w * 0.40, deck + 3], fill=(52, 56, 64))
    d.rectangle([x0 + w * 0.60, deck - 4, x1, deck + 3], fill=(52, 56, 64))
    d.polygon([(x0 + w * 0.40, deck - 3), (x0 + w * 0.52, deck + h * 0.20),
               (x0 + w * 0.60, deck - 3)], fill=(40, 44, 50))
    for fx, col in ((0.10, (200, 60, 40)), (0.24, (240, 244, 248)), (0.72, (60, 110, 200))):
        cx = x0 + w * fx
        d.rectangle([cx - 11, deck - 13, cx + 11, deck - 4], fill=col)
        d.rectangle([cx - 6, deck - 19, cx + 3, deck - 13], fill=(230, 232, 236))
    gx, gy = x0 + w * 0.50, y0 + h * 0.16
    for r, col in ((17, (120, 120, 124)), (12, (168, 96, 40)), (7, (226, 178, 60))):
        d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=col)
    for dx, dy, r in ((-24, 8, 8), (22, 12, 9), (-6, -16, 7), (14, -12, 6)):
        d.ellipse([gx + dx - r, gy + dy - r, gx + dx + r, gy + dy + r], fill=(110, 110, 114))


# ---------------------------------------------------------------- page
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# Masthead
d.rectangle([26, 18, 998, 21], fill=INK)
d.line([26, 26, 998, 26], fill=INK, width=1)
tracked(d, 32, "THE DAY IN WORLD NEWS", F(SERIFB, 27), INK, spacing=7)
tracked(d, 68, "39 STORIES · 6 CONTINENTS · ONE DAY", F(SANSB, 14), ACCENT, spacing=4)
centered(d, 90, "Tuesday 17 November 2026", F(SERIFB, 56), INK)
d.line([26, 156, 998, 156], fill=INK, width=2)

# Hero panel: story 1, Kerch Bridge (EUROPE)
d.rectangle([26, 164, 628, 386], outline=INK, width=2)
badge(d, 48, 182, 1, REGIONS["EUROPE"], r=10)
chip(d, 68, 172, "EUROPE", "WAR")
_ls = "LEAD STORY"
d.text((614 - d.textlength(_ls, font=F(SANSB, 10)), 176), _ls, font=F(SANSB, 10), fill=GREY)
bridge_art(d, 40, 200, 614, 294)
_hl = wrap(d, "Ukraine strike collapses part of the Kerch Bridge", F(SERIFB, 28), 574)
draw_lines(d, (40, 300), _hl, F(SERIFB, 28), INK, 33)
d.text((40, 366), "Road-and-rail link to Crimea severed; Moscow blames Kyiv, Kyiv silent.",
       font=F(SANS, 12), fill=(52, 52, 56))

# Stacked mains 2 and 3
STACK = [
    (2, "MIDEAST", "ENERGY", "IRGC says mines hit two tankers in Hormuz",
     "A third US carrier arrives in the region as shipping stays paralysed."),
    (3, "ASIA", "SUMMIT", "Trump lands in Manila for ASEAN summit",
     "Signs a Thailand trade statement at the summit."),
]
for i, (num, region, topic, head, deck) in enumerate(STACK):
    px, py = 638, 164 + i * 114
    d.rectangle([px, py, 998, py + 106], outline=INK, width=1)
    badge(d, px + 20, py + 19, num, REGIONS[region])
    chip(d, px + 36, py + 10, region, topic)
    ICONS[num](d, px + 10, py + 38, 60)
    hf = F(SERIFB, 15)
    draw_lines(d, (px + 80, py + 36), wrap(d, head, hf, 268), hf, INK, 18)
    df = F(SANS, 11)
    draw_lines(d, (px + 80, py + 74), wrap(d, deck, df, 268), df, (52, 52, 56), 13)

# Grid mains 4-12
GRID = [
    (4, "AMERICAS", "BUSINESS", "Nvidia's first earnings since Huang stepped down",
     "Chip giant reports amid AI-spending scrutiny.", icon_chip),
    (5, "GLOBAL", "TECH", "Microsoft 365 outage hits 70+ countries",
     "Worldwide failure restored the same day.", icon_cloud),
    (6, "ASIA", "DEFENCE", "Japan scrambles jets over suspected Russian aircraft",
     "Interception near Japan's northern airspace.", icon_jet),
    (7, "MIDEAST", "AID", "Four nations urge Israel to open Gaza crossings",
     "Aid situation called 'catastrophic'.", icon_truck),
    (8, "EUROPE", "DIPLOMACY", "128 states debate killer robots in Geneva",
     "Talks weigh a binding treaty on AI weapons.", icon_robot),
    (9, "EUROPE", "TRADE", "EU charges Temu over illegal goods",
     "Brussels: platform failed on unsafe products.", icon_parcel),
    (10, "GLOBAL", "CLIMATE", "COP31 draft calls time on fossil fuels",
     "$120bn a year in adaptation aid by 2035.", icon_leaf),
    (11, "AFRICA", "HEALTH", "Ebola in DR Congo 'still not under control'",
     "Africa CDC: 11,200 cases, 5,500 deaths.", icon_virus),
    (12, "ASIA", "SPORT", "India win U19 Asia Cup in last-ball thriller",
     "Ulva's 49* seals a one-wicket win.", icon_trophy),
]
for i, (num, region, topic, head, deck, icon) in enumerate(GRID):
    gx, gy = 26 + (i % 3) * 328, 394 + (i // 3) * 86
    d.rectangle([gx, gy, gx + 316, gy + 80], outline=RULE, width=1)
    badge(d, gx + 19, gy + 16, num, REGIONS[region])
    chip(d, gx + 34, gy + 7, region, topic, h=17)
    icon(d, gx + 8, gy + 30, 46)
    hf = F(SERIFB, 14)
    draw_lines(d, (gx + 62, gy + 28), wrap(d, head, hf, 246), hf, INK, 16)
    d.text((gx + 62, gy + 62), deck, font=fit_font(d, deck, SANS, 10, 246), fill=(52, 52, 56))


# ------------------------------------------------------- Day in Numbers
d.line([26, 654, 998, 654], fill=INK, width=2)
d.text((26, 660), "THE DAY IN NUMBERS", font=F(SANSB, 13), fill=INK)
_dn_note = "Five figures that frame the day"
d.text((998 - d.textlength(_dn_note, font=F(SANS, 10)), 662), _dn_note,
       font=F(SANS, 10), fill=GREY)
d.line([26, 680, 998, 680], fill=RULE, width=1)
NUMBERS = [
    ("11,200", "Ebola cases counted in DR Congo — Africa CDC"),
    ("5,700+", "measles infections in the US this year — Nature"),
    ("146,000", "people marched in France's pay strike — Interior Ministry"),
    ("66–52", "Knesset vote electing speaker Matan Kahana"),
    ("1", "light-day from Earth: Voyager 1's distance — NASA"),
]
for i, (big, label) in enumerate(NUMBERS):
    nx = 26 + i * 194
    d.text((nx, 686), big, font=F(SERIFB, 30), fill=ACCENT)
    draw_lines(d, (nx, 720), wrap(d, label, F(SANS, 10), 186), F(SANS, 10), (52, 52, 56), 12)

# ------------------------------------------------------------- world map
# Dot-matrix world map: 100 x 22 cells, equirectangular (reused from v3).
# '#' = land, '.' = ocean. Rows run lat ~+77 (top) to ~-54 (bottom),
# columns run lon -180 (left) to +180 (right).
MAP_COLS = 100
MAP_ROWS = [
    "......####" "#####....." ".........." ".........." ".........." ".........." "##########" "##########" "##########" "######....",
    "....######" "###.######" "#########." "........##" "####......" "..########" "##########" "##########" "##########" "########..",
    "...#######" "###.######" "##########" "####......" "####......" "..########" "##########" "##########" "##########" "######....",
    ".........." "##########" "##########" "##..######" "#......###" "##########" "##########" "##########" "##########" "######....",
    ".........#" "##########" "##########" "#........." ".......###" "##########" "##########" "##########" "##########" "#####.....",
    ".........." ".#########" "##########" "##........" ".......###" "##########" "##########" "##########" "#####....#" "#.........",
    ".........." "##########" "##########" "###......." "......####" "##########" "##########" "##########" "#######.##" "..........",
    ".........." ".#########" "##########" "#........." "....######" "##########" "##########" "##########" "########.#" "..........",
    ".........." "...#######" "##########" ".........." "....######" "##########" "#######..#" "##########" "######...." "..........",
    ".........." "....######" "#######..." ".........." "....######" "##########" "#######..#" "####..####" "#...##...." "..........",
    ".........." ".........." ".......###" "##........" "....######" "##########" "#........#" "###...####" "#.#####..." "..........",
    ".........." ".........." ".......###" "##########" "......####" "#########." ".........." "...##..##." ".##..##..." "..........",
    ".........." ".........." "........##" "##########" "#.....####" "########.." ".........." "....##..##" "...##..##." "..........",
    ".........." ".........." ".........#" "##########" "......####" "#######..." ".........." ".........." "##########" "#.........",
    ".........." ".........." ".........#" "########.." ".......###" "######...." ".........." ".........." "##########" "##........",
    ".........." ".........." "........##" "#######..." "......####" "#####....." ".........." ".........." "##########" "##........",
    ".........." ".........." ".........#" "#######..." "......####" "####......" ".........." ".........." "##########" "#.........",
    ".........." ".........." ".........." "#######..." "......####" "###......." ".........." ".........." ".#########" "..........",
    ".........." ".........." ".........." "######...." ".........." ".........." ".........." ".........." ".#########" ".....##...",
    ".........." ".........." ".........." "####......" ".........." ".........." ".........." ".........." ".........." "....##....",
    ".........." ".........." ".........." "##........" ".........." ".........." ".........." ".........." ".........." "..........",
    ".........." ".........." ".........." "#........." ".........." ".........." ".........." ".........." ".........." "..........",
]

# Pins: story number -> (col, row, region). Stories 5 and 39 have no
# location (global outage / deep space) and appear as chips below the map.
PINS = {
    1: (63, 5, "EUROPE"), 2: (65, 9, "MIDEAST"), 3: (84, 10, "ASIA"),
    4: (16, 7, "AMERICAS"), 6: (88, 7, "ASIA"), 7: (59, 8, "MIDEAST"),
    8: (52, 6, "EUROPE"), 9: (51, 3, "EUROPE"), 10: (58, 7, "GLOBAL"),
    11: (56, 13, "AFRICA"), 12: (70, 10, "ASIA"), 13: (59, 3, "EUROPE"),
    14: (58, 5, "EUROPE"), 15: (55, 5, "EUROPE"), 16: (53, 4, "EUROPE"),
    17: (49, 3, "EUROPE"), 18: (50, 5, "EUROPE"), 19: (61, 7, "MIDEAST"),
    20: (62, 11, "MIDEAST"), 21: (60, 9, "MIDEAST"), 22: (67, 10, "MIDEAST"),
    23: (80, 5, "ASIA"), 24: (75, 9, "ASIA"), 25: (79, 13, "ASIA"),
    26: (71, 8, "ASIA"), 27: (70, 7, "ASIA"), 28: (86, 11, "ASIA"),
    29: (46, 11, "AFRICA"), 30: (61, 12, "AFRICA"), 31: (52, 11, "AFRICA"),
    32: (28, 7, "AMERICAS"), 33: (31, 5, "AMERICAS"), 34: (30, 10, "AMERICAS"),
    35: (29, 14, "AMERICAS"), 36: (36, 15, "AMERICAS"), 37: (34, 17, "AMERICAS"),
    38: (90, 19, "OCEANIA"),
}

d.rectangle([26, 750, 498, 968], outline=INK, width=1)
d.text((38, 758), "WHERE IT HAPPENED", font=F(SANSB, 12), fill=INK)
d.rectangle([34, 772, 490, 876], fill=(238, 241, 238))
OX, OY, CELL = 36, 774, 4.5
LAND = (43, 52, 63)
for r, row in enumerate(MAP_ROWS):
    row = row.ljust(MAP_COLS, ".")[:MAP_COLS]
    for c, ch in enumerate(row):
        if ch == "#":
            cx, cy = OX + (c + 0.5) * CELL, OY + (r + 0.5) * CELL
            d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=LAND)
for num in sorted(PINS):
    c, r, region = PINS[num]
    cx, cy = OX + (c + 0.5) * CELL, OY + (r + 0.5) * CELL
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=REGIONS[region],
              outline=(255, 255, 255), width=2)
    t = str(num)
    pf = F(SANSB, 8)
    d.text((cx - d.textlength(t, font=pf) / 2, cy - 5), t, font=pf, fill=(255, 255, 255))

# Global stories as chips under the map
gy = 890
d.text((38, gy - 5), "WORLDWIDE / IN SPACE:", font=F(SANSB, 9), fill=GREY)
gx = 38 + d.textlength("WORLDWIDE / IN SPACE:", font=F(SANSB, 9)) + 10
for num, label in ((5, "Microsoft 365 outage"), (39, "Voyager 1")):
    badge(d, gx + 8, gy + 3, num, REGIONS["GLOBAL"], r=8)
    d.text((gx + 20, gy - 5), label, font=F(SANS, 9), fill=(52, 52, 56))
    gx += 20 + d.textlength(label, font=F(SANS, 9)) + 18

# Legend: the per-region colour system
lx = 38
for region in ("EUROPE", "MIDEAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "GLOBAL"):
    label = REGION_LABEL.get(region, region)
    d.ellipse([lx, 906, lx + 8, 914], fill=REGIONS[region])
    d.text((lx + 12, 905), label, font=F(SANSB, 8), fill=(52, 52, 56))
    lx += 12 + d.textlength(label, font=F(SANSB, 8)) + 10

# Stories-by-region tally (auditable breadth)
d.text((38, 924), "STORIES BY REGION", font=F(SANSB, 10), fill=INK)
TALLY = [("EUROPE", 9), ("ASIA", 9), ("AMERICAS", 7), ("MIDDLE EAST", 6),
         ("AFRICA", 4), ("GLOBAL", 3), ("OCEANIA", 1)]
TALLY_KEY = {"EUROPE": "EUROPE", "ASIA": "ASIA", "AMERICAS": "AMERICAS",
             "MIDDLE EAST": "MIDEAST", "AFRICA": "AFRICA", "GLOBAL": "GLOBAL",
             "OCEANIA": "OCEANIA"}
for i, (label, count) in enumerate(TALLY):
    tx = 38 + (i % 4) * 116
    ty = 940 + (i // 4) * 14
    d.text((tx, ty), label, font=F(SANS, 8), fill=(52, 52, 56))
    bw = count * 4.5
    d.rectangle([tx + 58, ty + 1, tx + 58 + bw, ty + 8], fill=REGIONS[TALLY_KEY[label]])
    d.text((tx + 62 + bw, ty), str(count), font=F(SANSB, 8), fill=INK)


# ------------------------------------------------------- ALSO ON TUESDAY
ALSO = [
    (13, "EUROPE", "Kyiv: Russian strikes hit two bridges"),
    (14, "EUROPE", "Moldova shuts airspace over drone"),
    (15, "EUROPE", "Prague: two trains collide, 46 hurt"),
    (16, "EUROPE", "Deutsche Bank hit by leak reports"),
    (17, "EUROPE", "UK sanctions 8 settler firms, Tzav 9"),
    (18, "EUROPE", "France: 146,000 march in pay strike"),
    (19, "MIDEAST", "Knesset elects Kahana speaker 66–52"),
    (20, "MIDEAST", "Yemen: Houthis advance towards Aden"),
    (21, "MIDEAST", "Gaza rains flood shelters, UN warns"),
    (22, "MIDEAST", "Oman hosts Iran shipping talks"),
    (23, "ASIA", "Mongolia: president to quit in graft row"),
    (24, "ASIA", "Bangladesh garment protest tear-gassed"),
    (25, "ASIA", "Singapore seeks trusted AI chip access"),
    (26, "ASIA", "Imran Khan fears he won't survive jail"),
    (27, "ASIA", "Sri Lanka all out for 98 in Rawalpindi"),
    (28, "ASIA", "Australia, Philippines sign defence pact"),
    (29, "AFRICA", "Guinea jails 224 in gold-mining purge"),
    (30, "AFRICA", "Kenya: WFP aids 30,000 fleeing Moyale"),
    (31, "AFRICA", "Nigeria inflation eases to 14.06%"),
    (32, "AMERICAS", "US, Mexico, Bolivia lose measles status"),
    (33, "AMERICAS", "JPMorgan blames bug for banking outage"),
    (34, "AMERICAS", "Haiti: 33 register for presidential race"),
    (35, "AMERICAS", "Peru: Pope Leo ends South America tour"),
    (36, "AMERICAS", "Brazil 7–0 Singapore: Vinícius hat-trick"),
    (37, "AMERICAS", "Paraguay ex-president sent to army jail"),
    (38, "OCEANIA", "Curlew chicks hatch, first in 50 years"),
    (39, "GLOBAL", "Voyager 1 reaches one light-day out"),
]
d.rectangle([510, 750, 998, 968], outline=INK, width=1)
d.text((522, 758), "ALSO ON TUESDAY", font=F(SERIFB, 15), fill=INK)
_also_note = "27 more verified stories"
d.text((986 - d.textlength(_also_note, font=F(SANS, 9)), 762), _also_note,
       font=F(SANS, 9), fill=GREY)
d.line([522, 782, 986, 782], fill=RULE, width=1)
for i, (num, region, text) in enumerate(ALSO):
    ax = 522 if i < 14 else 766
    ay = 790 + (i % 14) * 12.5
    nf = F(SANSB, 11)
    d.text((ax, ay), str(num), font=nf, fill=REGIONS[region])
    tf = fit_font(d, text, SANS, 11, 212)
    d.text((ax + 20, ay), text, font=tf, fill=INK)

# ---------------------------------------------------------------- footer
d.line([26, 974, 998, 974], fill=INK, width=1)
centered(d, 980,
         "QUOTE OF THE DAY — “I have never stolen from my people or my state.” "
         "— Mongolia's President Khurelsukh, announcing he will resign (AP)",
         F(SERIF, 11), (52, 52, 56))
centered(d, 996,
         "Sources: Reuters · AP · AFP · BBC · Al Jazeera · The Guardian · UN News · "
         "NASA · PAHO · Nature · Africa CDC · ESPNcricinfo · Defense News",
         F(SANS, 9), GREY)
centered(d, 1007,
         "Disputed claims are attributed to their source. "
         "All illustrations are original drawings, made for this front page.",
         F(SANS, 9), GREY)

img.save(OUT)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
