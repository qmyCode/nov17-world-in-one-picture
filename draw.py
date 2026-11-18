#!/usr/bin/env python3
"""Draw the news-image-20261117 entry: a newspaper front-page poster that
sums up Tuesday 17 November 2026 in one 1024x1024 image.

Tooling only -- the shipped main.py just copies the committed entry.png.
Run:  python3 draw.py   (writes entry.png next to this file)
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
CREAM = (247, 241, 227)
PAPER = (253, 250, 240)
INK = (22, 20, 18)
RED = (178, 34, 28)
GREY = (90, 84, 74)
WATER = (86, 138, 178)
SKY = (216, 230, 240)

F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, max_w):
    """Greedy word wrap to max_w pixels; returns list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if text_w(d, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(d, s, path, max_size, min_size, max_w, max_h, lh_ratio):
    """Largest font size whose wrapped block fits max_w x max_h.
    Returns (font, lines, line_height)."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        lines = wrap(d, s, f, max_w)
        lh = int(size * lh_ratio)
        if len(lines) * lh <= max_h:
            return f, lines, lh
        size -= 1
    f = font(path, min_size)
    return f, wrap(d, s, f, max_w), int(min_size * lh_ratio)


def draw_lines(d, lines, x, y, f, lh, fill=INK):
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def centered(d, s, cx, y, f, fill=INK):
    d.text((cx - text_w(d, s, f) / 2, y), s, font=f, fill=fill)


def tracked(d, s, cx, y, f, tracking, fill=INK):
    """Draw text centered with extra letter tracking."""
    widths = [text_w(d, ch, f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + tracking


def tag_chip(d, x, y, label, color):
    f = font(F_SANS_B, 16)
    w = int(text_w(d, label, f)) + 18
    d.rectangle([x, y, x + w, y + 24], fill=color)
    d.text((x + 9, y + 3), label, font=f, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- masthead
def masthead(d):
    cx = W // 2
    tracked(d, "THE WORLD IN ONE PICTURE", cx, 26, font(F_SANS_B, 22), 6, INK)
    d.line([70, 60, W - 70, 60], fill=INK, width=2)
    centered(d, "TUESDAY", cx, 66, font(F_SERIF_B, 62))
    centered(d, "17 NOVEMBER 2026", cx, 132, font(F_SERIF_B, 40), RED)
    d.rectangle([26, 182, W - 26, 187], fill=INK)


# ---------------------------------------------------------------- world map
# Dot-matrix world map: 100 x 22 cells, equirectangular.
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

# Story pins: story number -> (col, row) on the map grid.
PINS = {
    1: (59, 6),    # Crimea / Black Sea
    2: (66, 9),    # Strait of Hormuz
    3: (84, 10),   # Manila
    4: (16, 7),    # California (Nvidia)
    5: (12, 4),    # Redmond (Microsoft), offset NW of pin 4
    6: (89, 7),    # Japan
    7: (57, 8),    # Gaza / Eastern Mediterranean
    8: (53, 6),    # Geneva
    9: (49, 4),    # Brussels / EU
}


def world_map(d, box):
    """Draw the dot-matrix map inside box, with numbered red pins."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=(238, 241, 238), outline=INK, width=2)
    grid_w = (x1 - x0) - 36
    grid_h = (y1 - y0) - 52
    px = grid_w / MAP_COLS
    py = grid_h / len(MAP_ROWS)
    ox = x0 + 18
    oy = y0 + 12
    land = (43, 52, 63)
    for r, row in enumerate(MAP_ROWS):
        row = row.ljust(MAP_COLS, ".")[:MAP_COLS]
        cy = oy + (r + 0.5) * py
        for c, ch in enumerate(row):
            if ch == "#":
                cx = ox + (c + 0.5) * px
                d.ellipse([cx - 3.1, cy - 3.1, cx + 3.1, cy + 3.1], fill=land)
    pf = font(F_SANS_B, 15)
    for num, (c, r) in PINS.items():
        cx = ox + (c + 0.5) * px
        cy = oy + (r + 0.5) * py
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED, outline=(255, 255, 255), width=2)
        s = str(num)
        d.text((cx - text_w(d, s, pf) / 2, cy - 9), s, font=pf, fill=(255, 255, 255))
    cap = "NINE STORIES \u00b7 FIVE CONTINENTS \u00b7 ONE DAY"
    centered(d, cap, (x0 + x1) // 2, y1 - 34, font(F_SANS_B, 19), INK)


# ---------------------------------------------------------------- hero art
def bridge_art(d, x, y, w, h):
    """Long bridge over water; the middle span is broken and tilted down."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    wy = y + h - 34
    d.rectangle([x, wy, x + w, y + h], fill=WATER)
    for i in range(7):  # wave ticks
        wx = x + 30 + i * (w - 60) // 6
        d.arc([wx, wy + 8, wx + 34, wy + 24], 180, 360, fill=(230, 242, 250), width=2)
    deck_y = y + 44
    col = (52, 56, 62)
    # piers
    for px in (x + 60, x + w - 110):
        d.rectangle([px, deck_y, px + 16, wy + 4], fill=col)
    # left deck + cables
    gap_l = x + int(w * 0.44)
    gap_r = x + int(w * 0.63)
    d.rectangle([x + 8, deck_y, gap_l, deck_y + 9], fill=col)
    d.rectangle([gap_r, deck_y, x + w - 8, deck_y + 9], fill=col)
    for tx in (x + 60, x + w - 110):
        d.line([tx + 8, deck_y - 30, tx + 8, deck_y], fill=col, width=4)
        d.line([tx + 8, deck_y - 30, x + 14, deck_y], fill=col, width=2)
        d.line([tx + 8, deck_y - 30, (gap_l if tx < x + w / 2 else gap_r), deck_y], fill=col, width=2)
    # broken middle span, tilted into the water
    d.polygon([(gap_l, deck_y + 2), (gap_r - 6, deck_y + 34),
               (gap_r - 6, deck_y + 43), (gap_l, deck_y + 11)], fill=col)
    # jagged crack edges
    d.line([gap_l, deck_y, gap_l + 10, deck_y + 12, gap_l + 2, deck_y + 20], fill=RED, width=3)
    d.line([gap_r, deck_y, gap_r - 12, deck_y + 10, gap_r - 4, deck_y + 18], fill=RED, width=3)
    # splash where the span hits the water
    for sx in (-14, 0, 14):
        d.line([gap_r - 26 + sx, wy + 2, gap_r - 32 + sx, wy - 12], fill=(240, 248, 252), width=3)


# ---------------------------------------------------------------- icons
def icon_tanker(d, x, y, s):
    """Tanker hull + waves + a spiked mine."""
    hull = [(x, y + s * 0.45), (x + s, y + s * 0.45), (x + s * 0.86, y + s * 0.68),
            (x + s * 0.12, y + s * 0.68)]
    d.polygon(hull, fill=(52, 56, 62))
    d.rectangle([x + s * 0.10, y + s * 0.34, x + s * 0.52, y + s * 0.45], fill=(120, 128, 138))
    d.rectangle([x + s * 0.58, y + s * 0.26, x + s * 0.70, y + s * 0.45], fill=(52, 56, 62))
    for i in range(3):
        wx = x + i * s * 0.34
        d.arc([wx, y + s * 0.74, wx + s * 0.3, y + s * 0.92], 180, 360, fill=WATER, width=3)
    mx, my, r = x + s * 0.84, y + s * 0.16, s * 0.11
    for a in range(0, 360, 45):
        import math
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([mx + dx * r * 0.6, my + dy * r * 0.6, mx + dx * r * 1.5, my + dy * r * 1.5],
               fill=INK, width=2)
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=INK)


def icon_flags(d, x, y, s):
    """Three flags on poles + a small jet overhead."""
    cols = [(38, 84, 150), (214, 178, 60), (178, 34, 28)]
    for i, c in enumerate(cols):
        px = x + s * (0.12 + i * 0.30)
        d.line([px, y + s * 0.36, px, y + s * 0.97], fill=INK, width=3)
        d.rectangle([px, y + s * 0.36, px + s * 0.24, y + s * 0.58], fill=c)
    d.polygon([(x + s * 0.18, y + s * 0.06), (x + s * 0.44, y + s * 0.13),
               (x + s * 0.82, y + s * 0.10), (x + s * 0.56, y + s * 0.18),
               (x + s * 0.62, y + s * 0.23), (x + s * 0.50, y + s * 0.21),
               (x + s * 0.24, y + s * 0.14)], fill=(52, 56, 62))


def icon_chip(d, x, y, s):
    body = s * 0.52
    bx, by = x + (s - body) / 2, y + (s - body) / 2
    for i in range(4):  # pins
        off = body * (0.18 + i * 0.21)
        d.line([bx + off, y + s * 0.06, bx + off, by], fill=INK, width=3)
        d.line([bx + off, by + body, bx + off, y + s * 0.94], fill=INK, width=3)
        d.line([x + s * 0.06, by + off, bx, by + off], fill=INK, width=3)
        d.line([bx + body, by + off, x + s * 0.94, by + off], fill=INK, width=3)
    d.rectangle([bx, by, bx + body, by + body], outline=INK, width=4)
    d.rectangle([bx + body * 0.28, by + body * 0.28, bx + body * 0.72, by + body * 0.72],
                outline=RED, width=3)


def icon_cloud(d, x, y, s):
    """Cloud with a jagged crack and a down arrow."""
    cy = y + s * 0.42
    d.ellipse([x + s * 0.06, cy - s * 0.16, x + s * 0.44, cy + s * 0.20], fill=(168, 182, 196))
    d.ellipse([x + s * 0.30, cy - s * 0.30, x + s * 0.72, cy + s * 0.20], fill=(168, 182, 196))
    d.ellipse([x + s * 0.56, cy - s * 0.14, x + s * 0.92, cy + s * 0.20], fill=(168, 182, 196))
    d.rectangle([x + s * 0.10, cy + s * 0.02, x + s * 0.88, cy + s * 0.20], fill=(168, 182, 196))
    d.line([x + s * 0.50, cy - s * 0.26, x + s * 0.42, cy - s * 0.02,
            x + s * 0.54, cy + s * 0.06, x + s * 0.46, cy + s * 0.20], fill=RED, width=3)
    ax = x + s * 0.76
    d.line([ax, y + s * 0.66, ax, y + s * 0.92], fill=RED, width=4)
    d.polygon([(ax - s * 0.08, y + s * 0.84), (ax + s * 0.08, y + s * 0.84),
               (ax, y + s * 0.97)], fill=RED)


def icon_jet(d, x, y, s):
    """Jet silhouette crossing a rising-sun disc."""
    cx, cy, r = x + s * 0.5, y + s * 0.5, s * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.polygon([(x + s * 0.06, y + s * 0.60), (x + s * 0.34, y + s * 0.50),
               (x + s * 0.78, y + s * 0.30), (x + s * 0.95, y + s * 0.28),
               (x + s * 0.82, y + s * 0.42), (x + s * 0.52, y + s * 0.52),
               (x + s * 0.58, y + s * 0.64), (x + s * 0.44, y + s * 0.60),
               (x + s * 0.16, y + s * 0.68), (x + s * 0.08, y + s * 0.76)],
              fill=(30, 30, 34))


def icon_bridge_mini(d, x, y, s):
    """Tiny bridge with a broken middle span, over water."""
    deck = y + s * 0.52
    col = (52, 56, 62)
    d.rectangle([x + s * 0.28, deck - s * 0.30, x + s * 0.34, deck], fill=col)
    d.rectangle([x + s * 0.66, deck - s * 0.30, x + s * 0.72, deck], fill=col)
    d.rectangle([x + s * 0.02, deck, x + s * 0.42, deck + s * 0.09], fill=col)
    d.rectangle([x + s * 0.60, deck, x + s * 0.98, deck + s * 0.09], fill=col)
    d.polygon([(x + s * 0.42, deck + s * 0.02), (x + s * 0.60, deck + s * 0.20),
               (x + s * 0.60, deck + s * 0.28), (x + s * 0.42, deck + s * 0.10)], fill=col)
    d.line([x + s * 0.31, deck - s * 0.30, x + s * 0.04, deck], fill=col, width=2)
    d.line([x + s * 0.69, deck - s * 0.30, x + s * 0.96, deck], fill=col, width=2)
    for i in range(3):
        wx = x + s * (0.08 + i * 0.32)
        d.arc([wx, y + s * 0.72, wx + s * 0.26, y + s * 0.92], 180, 360, fill=WATER, width=2)


def icon_crossing(d, x, y, s):
    """Aid truck with a cross, for the Gaza crossings story."""
    col = (52, 56, 62)
    d.rectangle([x + s * 0.04, y + s * 0.24, x + s * 0.62, y + s * 0.66], fill=col)
    d.polygon([(x + s * 0.62, y + s * 0.40), (x + s * 0.82, y + s * 0.40),
               (x + s * 0.94, y + s * 0.56), (x + s * 0.94, y + s * 0.66),
               (x + s * 0.62, y + s * 0.66)], fill=col)
    cx, cy = x + s * 0.33, y + s * 0.45
    d.rectangle([cx - s * 0.045, cy - s * 0.13, cx + s * 0.045, cy + s * 0.13], fill=(255, 255, 255))
    d.rectangle([cx - s * 0.13, cy - s * 0.045, cx + s * 0.13, cy + s * 0.045], fill=(255, 255, 255))
    for wx in (x + s * 0.20, x + s * 0.78):
        d.ellipse([wx - s * 0.09, y + s * 0.62, wx + s * 0.09, y + s * 0.80], fill=INK)
    d.line([x + s * 0.02, y + s * 0.84, x + s * 0.98, y + s * 0.84], fill=INK, width=2)


def icon_robot(d, x, y, s):
    """Robot head with antenna, for the autonomous-weapons talks."""
    col = (52, 56, 62)
    cx = x + s * 0.5
    d.line([cx, y + s * 0.06, cx, y + s * 0.22], fill=INK, width=3)
    d.ellipse([cx - s * 0.06, y, cx + s * 0.06, y + s * 0.12], fill=RED)
    d.rectangle([x + s * 0.16, y + s * 0.22, x + s * 0.84, y + s * 0.80], outline=col, width=4)
    for ex in (x + s * 0.36, x + s * 0.64):
        d.ellipse([ex - s * 0.07, y + s * 0.40, ex + s * 0.07, y + s * 0.54], fill=RED)
    d.rectangle([x + s * 0.34, y + s * 0.64, x + s * 0.66, y + s * 0.70], fill=col)
    d.rectangle([x + s * 0.06, y + s * 0.42, x + s * 0.16, y + s * 0.58], fill=col)
    d.rectangle([x + s * 0.84, y + s * 0.42, x + s * 0.94, y + s * 0.58], fill=col)


def icon_bag(d, x, y, s):
    """Shopping bag with a slash, for the Temu / illegal goods story."""
    col = (52, 56, 62)
    d.polygon([(x + s * 0.16, y + s * 0.30), (x + s * 0.84, y + s * 0.30),
               (x + s * 0.90, y + s * 0.92), (x + s * 0.10, y + s * 0.92)], outline=col, width=4)
    d.arc([x + s * 0.32, y + s * 0.06, x + s * 0.68, y + s * 0.44], 180, 360, fill=col, width=4)
    d.line([x + s * 0.24, y + s * 0.80, x + s * 0.76, y + s * 0.42], fill=RED, width=5)


# ---------------------------------------------------------------- panels
def num_badge(d, x, y, num):
    """Red disc with a white numeral, matching the map pins."""
    r = 13
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=RED)
    f = font(F_SANS_B, 17)
    s = str(num)
    d.text((x + r - text_w(d, s, f) / 2, y + r - 10), s, font=f, fill=(255, 255, 255))
    return 2 * r


def panel(d, box, num, tag, tag_color, headline, caption, icon=None, headline_max=26):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=PAPER, outline=INK, width=2)
    pad = 10
    bw = num_badge(d, x0 + pad, y0 + pad, num)
    tag_f = font(F_SANS_B, 14)
    label_w = int(text_w(d, tag, tag_f)) + 14
    tx0 = x0 + pad + bw + 7
    d.rectangle([tx0, y0 + pad + 1, tx0 + label_w, y0 + pad + 25], fill=tag_color)
    d.text((tx0 + 7, y0 + pad + 5), tag, font=tag_f, fill=(255, 255, 255))
    if icon:
        icon(d, x1 - pad - 42, y0 + pad - 2, 42)
    tx = x0 + pad
    tw = (x1 - x0) - 2 * pad
    hy = y0 + pad + 38
    hf, hlines, hlh = fit_block(d, headline, F_SANS_B, headline_max, 19, tw,
                                (y1 - y0) - 96, 1.12)
    hy = draw_lines(d, hlines, tx, hy, hf, hlh)
    cy = hy + 4
    cf, clines, clh = fit_block(d, caption, F_SANS, 17, 13, tw, (y1 - 7) - cy, 1.2)
    draw_lines(d, clines, tx, cy, cf, clh)


def hero_panel(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=PAPER, outline=INK, width=2)
    bridge_art(d, x0 + 10, y0 + 10, (x1 - x0) - 20, 118)
    tag_chip(d, x0 + 14, y0 + 14, "EUROPE", (31, 78, 120))
    tx = x0 + 14
    tw = (x1 - x0) - 28
    hy = y0 + 140
    hf, hlines, hlh = fit_block(
        d, "UKRAINE BLOWS A GAP IN THE CRIMEA BRIDGE", F_SANS_B, 47, 38, tw, 120, 1.1)
    hy = draw_lines(d, hlines, tx, hy, hf, hlh)
    cap = ("Strike collapses a section of the Kerch Bridge; Zelenskyy hails an "
           "'unprecedented operation' as Russian missiles hit Kyiv's bridges in reply.")
    cf, clines, clh = fit_block(d, cap, F_SANS, 22, 19, tw, (y1 - 8) - (hy + 6), 1.25)
    draw_lines(d, clines, tx, hy + 6, cf, clh)


STORIES = [
    (1, "EUROPE", (31, 78, 120),
     "UKRAINE BLOWS A GAP IN THE CRIMEA BRIDGE",
     "Strike collapses a section of the Kerch Bridge; Zelenskyy hails "
     "an 'unprecedented operation'.", icon_bridge_mini),
    (2, "MIDDLE EAST", (146, 96, 16),
     "TANKERS HIT MINES IN HORMUZ, IRAN SAYS",
     "Guards claim two tankers struck mines; a third US carrier "
     "arrives.", icon_tanker),
    (3, "ASIA", (46, 107, 52),
     "TRUMP LANDS IN MANILA FOR ASEAN SUMMIT",
     "Signs a trade statement with Thailand; tour ends in China with "
     "Xi\u2013Putin talks.", icon_flags),
    (4, "BUSINESS", (91, 58, 142),
     "NVIDIA'S FIRST EARNINGS SINCE HUANG STEPPED DOWN",
     "Founder signals he would return as the chip giant reports.",
     icon_chip),
    (5, "TECH", (140, 47, 57),
     "MICROSOFT 365 OUTAGE DISRUPTS MILLIONS",
     "Global failure hit users in 70+ countries; services restored.",
     icon_cloud),
    (6, "ASIA-PACIFIC", (23, 97, 107),
     "JAPAN SCRAMBLES JETS OVER RUSSIAN AIRCRAFT",
     "Tokyo protests after two suspected planes enter its airspace.",
     icon_jet),
    (7, "MIDDLE EAST", (146, 96, 16),
     "WEST URGES ISRAEL TO OPEN GAZA CROSSINGS",
     "UK, Australia, Canada and Italy call the aid situation "
     "catastrophic.", icon_crossing),
    (8, "WORLD", (70, 70, 70),
     "128 STATES DEBATE A BAN ON KILLER ROBOTS",
     "UN talks in Geneva weigh a treaty on lethal autonomous weapons.",
     icon_robot),
    (9, "EUROPE", (31, 78, 120),
     "EU CHARGES TEMU OVER ILLEGAL GOODS",
     "Brussels says the platform does too little to stop illegal sales.",
     icon_bag),
]


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 10, H - 10], outline=INK, width=3)
    d.rectangle([17, 17, W - 17, H - 17], outline=INK, width=1)

    masthead(d)
    world_map(d, (26, 198, W - 26, 436))

    gx0, gx1 = 26, W - 26
    colw = (gx1 - gx0 - 20) // 3
    rows_y = [(448, 612), (620, 784), (792, 956)]
    for i, (num, tag, color, head, cap, icon) in enumerate(STORIES):
        r, c = divmod(i, 3)
        x0 = gx0 + c * (colw + 10)
        box = (x0, rows_y[r][0], x0 + colw, rows_y[r][1])
        panel(d, box, num, tag, color, head, cap, icon)

    d.line([70, 966, W - 70, 966], fill=INK, width=2)
    centered(d, "17 NOV 2026 \u00b7 THE DAY'S NEWS IN ONE IMAGE", W // 2, 974,
             font(F_SANS_B, 19))
    img.save(OUT, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()

