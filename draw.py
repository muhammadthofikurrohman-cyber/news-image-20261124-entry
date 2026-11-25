#!/usr/bin/env python3
"""Render 'THE WORLD IN ONE DAY — Tuesday 24 November 2026'.

Draws the 1024x1024 broadsheet with PIL (DejaVu fonts) and writes entry.png
next to this file. Fully deterministic: no randomness, no clock, no network.
The 11 banner illustrations are composited from assets/panel01.jpg ..
assets/panel11.jpg (cinematic editorial art generated in this session).
Run:  python3 draw.py
The graded entrypoint main.py only copies the rendered entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (the grader image has no PIL).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- palette ------------------------------------------------------------
PAPER   = (247, 244, 236)   # warm newsprint
INK     = (20, 33, 61)      # deep navy ink  #14213D
NAVY    = (15, 27, 51)      # #0F1B33 banner / map
NAVY2   = (51, 78, 123)     # #334E7B continent silhouettes
GOLD    = (244, 201, 93)    # #F4C95D KPI numbers
WHITE   = (255, 255, 255)
CARD    = (255, 253, 248)
RULE    = (216, 210, 192)
RED     = (198, 40, 40)
MUTE    = (90, 88, 78)
CHARCOAL = (30, 36, 48)   # #1E2430 body text

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF   = lambda s: font("DejaVuSerif.ttf", s)
SANS_B  = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS    = lambda s: font("DejaVuSans.ttf", s)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, s, f, max_w, max_lines, sizes):
    """Pick the largest size in `sizes` (first entry is f's size) that fits
    the text in max_lines; returns (font, lines)."""
    base = sizes[0]
    for sz in sizes:
        ff = font(f.path.rsplit("/", 1)[-1], sz) if hasattr(f, "path") else f
        lines = wrap(draw, s, ff, max_w)
        if len(lines) <= max_lines:
            return ff, lines
    ff = font(f.path.rsplit("/", 1)[-1], sizes[-1]) if hasattr(f, "path") else f
    return ff, wrap(draw, s, ff, max_w)[:max_lines]


def vgrad(img, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    d = ImageDraw.Draw(img)
    for i in range(h):
        t = i / h
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def sun(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def star(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


# ---- story data ---------------------------------------------------------
# (tag, headline, summary, pill, scene)
HEROES = [
    ("ASIA · MARKETS",
     "ASIAN STOCKS SOAR IN TUESDAY TECH RALLY",
     "Taiwan leapt 9.1% and Seoul jumped 7.5% in Tuesday's broad Asian tech rally.",
     "panel01"),
    ("EUROPE · UKRAINE",
     "RUSSIAN STRIKE HITS ZAPORIZHZHIA",
     "Two are killed and 22 wounded, two of them children, in an early Tuesday Russian attack.",
     "panel02"),
    ("OCEANIA · PACIFIC",
     "SOLOMONS TO DROP CHINA SECURITY PACT",
     "Honiara will end its 2022 China security pact and sign a new treaty with Australia.",
     "panel03"),
]

CARDS = [
    ("MIDDLE EAST · IRAQ",
     "IRAQ SEIZES KURDISH BORDER CROSSINGS",
     "Baghdad seizes all Kurdistan border crossings and oilfields in four provinces after a probe.",
     "4 PROVINCES UNDER BAGHDAD", "panel04"),
    ("MIDDLE EAST · UAE",
     "BUS CRASH KILLS 11 IN THE UAE",
     "Eleven people die when a passenger bus and a truck collide in Ras Al Khaimah, officials say.",
     "11 KILLED", "panel05"),
    ("ASIA · VIETNAM",
     "BLAST KILLS SIX IN CENTRAL HANOI",
     "Six die and ten are hurt in a morning blast at a food shop in a crowded Hanoi street.",
     "6 KILLED · 10 HURT", "panel06"),
    ("AFRICA · ETHIOPIA",
     "TIGRAY SHELLING 'MAY BE WAR CRIMES'",
     "Amnesty urges war-crimes probe after Ethiopian shelling kills 14 civilians in Tigray.",
     "14 CIVILIANS DEAD", "panel07"),
    ("ASIA · BANGLADESH",
     "HASINA TO FLY HOME ON 16 DECEMBER",
     "The ousted premier plans to end two years of exile in India, flying home on Liberation Day.",
     "16 DECEMBER · DHAKA", "panel08"),
    ("ASIA · JAPAN",
     "JAPAN PAYS ICC BILL EARLY",
     "Tokyo will pay its full 2027 court contribution by year-end as US sanctions threaten the ICC.",
     "15% OF ICC BUDGET", "panel09"),
    ("MIDDLE EAST · SAUDI ARABIA",
     "HOUTHI STRIKE HITS RIYADH TOWER",
     "Eleven are wounded as a Houthi strike hits a tower in Riyadh's financial district.",
     "11 WOUNDED", "panel10"),
    ("SPORT · AFRICA",
     "SENEGAL WIN BACK AFRICA CUP TITLE",
     "CAS gives Senegal its Africa Cup title back, overturning the ruling for Morocco.",
     "TITLE RESTORED", "panel11"),
]

KPI = [
    ("+9.1%", "TAIWAN LEADS ASIAN RALLY"),
    ("22", "WOUNDED IN ZAPORIZHZHIA"),
    ("11", "KILLED IN UAE BUS CRASH"),
    ("6", "KILLED IN HANOI BLAST"),
    ("14", "CIVILIANS KILLED IN TIGRAY"),
    ("6", "CONTINENTS"),
]

DIGEST = [
    "Canada and Qatar sign an investment pact.",
    "Malaysia keeps working with Myanmar on refugee returns.",
    "Infantino's private-jet flights under scrutiny.",
    "Nigeria's central bank holds its rate at 23%.",
    "Sanofi buys US biotech Insmed in a $41bn deal.",
    "UK heat deaths hit a record 5,258 in 2026.",
    "Smoke silences Borneo's gibbons as fires rage.",
    "Commanders stun Bengals on a last-second field goal.",
]

# Map pins: (number, label, x, y) in the map panel's pixel space.
PINS = [
    (1, "TAIPEI", 408, 899),
    (2, "ZAPORIZHZHIA", 293, 886),
    (3, "HONIARA", 458, 919),
    (4, "ERBIL", 311, 890),
    (5, "RAS AL KHAIMAH", 328, 897),
    (6, "HANOI", 388, 901),
    (7, "ALAMATA", 298, 909),
    (8, "DHAKA", 368, 899),
    (9, "TOKYO", 432, 893),
    (10, "RIYADH", 316, 912),
    (11, "LAUSANNE", 260, 886),
]

# Rough continent outlines in lon/lat, projected into the map panel.
MAP_X0, MAP_Y0 = 32, 868
MAP_PX_DEG, MAP_PY_DEG = 1.29, 0.58


def project(lon, lat):
    return (MAP_X0 + (lon + 170) * MAP_PX_DEG,
            MAP_Y0 + (78 - lat) * MAP_PY_DEG)


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-55, 47), (-60, 45), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-95, 19),
     (-97, 26), (-105, 20), (-110, 23), (-115, 30), (-120, 34),
     (-125, 40), (-124, 48), (-130, 55), (-145, 60), (-155, 58),
     (-165, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 64), (-30, 68), (-22, 70), (-25, 76),
     (-40, 80), (-55, 76), (-58, 70)],
    # South America
    [(-80, 9), (-75, 11), (-70, 12), (-62, 10), (-55, 6), (-52, 4),
     (-50, 0), (-44, -3), (-35, -8), (-40, -15), (-48, -25), (-55, -35),
     (-65, -40), (-70, -50), (-73, -53), (-70, -40), (-73, -30),
     (-80, -20), (-81, -12), (-80, -5), (-80, 9)],
    # Africa
    [(-17, 15), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (38, 22), (43, 12), (48, 11), (51, 10), (44, 0),
     (40, -10), (35, -18), (32, -28), (28, -33), (20, -35), (15, -27),
     (12, -18), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65),
     (20, 70), (15, 70), (10, 64), (5, 60), (-5, 58), (-10, 54),
     (-10, 48), (-10, 43), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-5, 50)],
    # Asia
    [(30, 62), (40, 68), (60, 69), (75, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 67), (178, 65), (170, 60), (162, 56),
     (158, 52), (142, 50), (140, 45), (135, 43), (130, 38), (127, 35),
     (122, 30), (120, 25), (110, 20), (105, 10), (100, 8), (98, 15),
     (95, 16), (92, 21), (88, 22), (85, 19), (80, 13), (77, 8),
     (75, 15), (72, 20), (68, 23), (62, 25), (58, 26), (55, 26),
     (52, 28), (50, 30), (48, 30), (44, 29), (42, 27), (40, 25),
     (38, 22), (35, 28), (34, 31), (33, 36), (30, 36), (28, 40),
     (26, 42), (28, 45), (30, 50), (30, 60), (30, 62)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20), (113, -22)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (174, -41), (168, -46)],
    # SE Asia islands
    [(95, 5), (98, 2), (101, -2), (98, -5), (95, 0)],
    [(110, -2), (115, -4), (118, -8), (113, -9), (109, -6)],
    [(128, -2), (132, -4), (135, -6), (131, -8), (127, -5)],
]

# ---- illustration art ---------------------------------------------------
# The 11 banner illustrations are cinematic editorial images generated in
# this session (media pipeline, no text/logos inside the art) and stored
# under assets/ as panel01.jpg .. panel11.jpg (JPEG q88, max 1200px wide).
# draw.py composites them deterministically: a fixed centre crop to the
# banner's aspect ratio, then a LANCZOS resize. No randomness, no clock,
# no network, so the same assets always give the same entry.png.
ASSETS_DIR = os.path.join(HERE, "assets")
_ASSET_CACHE = {}


def load_asset(name):
    if name not in _ASSET_CACHE:
        _ASSET_CACHE[name] = Image.open(
            os.path.join(ASSETS_DIR, name + ".jpg")).convert("RGB")
    return _ASSET_CACHE[name]


def render_scene(name, w, h, native_h=None):
    """Crop the panel art to the banner's aspect ratio and resize to it."""
    src = load_asset(name)
    sw, sh = src.size
    target = w / h
    if sw / sh > target:  # too wide: trim the sides, keep the centre
        cw = int(sh * target)
        x0 = (sw - cw) // 2
        box = (x0, 0, x0 + cw, sh)
    else:  # too tall: trim top/bottom, keep the centre band
        ch = int(sw / target)
        y0 = (sh - ch) // 2
        box = (0, y0, sw, y0 + ch)
    return src.crop(box).resize((w, h), Image.LANCZOS)


# ---- layout -------------------------------------------------------------
MARGIN = 22
CW = W - 2 * MARGIN  # 980


def draw_masthead(img, d):
    # kicker row
    f = SANS_B(11)
    d.text((MARGIN, 13), "GLOBAL EDITION", font=f, fill=INK)
    mid = "THE WORLD IN ONE DAY"
    d.text(((W - text_w(d, mid, f)) / 2, 13), mid, font=f, fill=INK)
    right = "24 NOV 2026 · TUESDAY"
    d.text((W - MARGIN - text_w(d, right, f), 13), right, font=f, fill=INK)
    # masthead
    mf = SERIF_B(40)
    title = "Tuesday 24 November 2026"
    d.text(((W - text_w(d, title, mf)) / 2, 36), title, font=mf, fill=INK)
    d.line([(MARGIN, 88), (W - MARGIN, 88)], fill=INK, width=2)
    d.line([(MARGIN, 92), (W - MARGIN, 92)], fill=INK, width=1)


def draw_kpi(img, d):
    y0, y1 = 98, 150
    d.rounded_rectangle([MARGIN, y0, W - MARGIN, y1], 6, fill=NAVY)
    cell = CW / 6
    nf, lf = SANS_B(24), SANS_B(9)
    for i, (num, label) in enumerate(KPI):
        cx = MARGIN + cell * (i + 0.5)
        d.text((cx - text_w(d, num, nf) / 2, y0 + 5), num, font=nf, fill=GOLD)
        llines = wrap(d, label, lf, cell - 10)
        ly = y0 + 34 if len(llines) == 1 else y0 + 30
        for ln in llines[:2]:
            d.text((cx - text_w(d, ln, lf) / 2, ly), ln, font=lf, fill=WHITE)
            ly += 11
        if i:
            x = MARGIN + cell * i
            d.line([(x, y0 + 8), (x, y1 - 8)], fill=NAVY2, width=1)


def draw_tag(d, x, y, tag, color=RED):
    f = SANS_B(10)
    d.text((x, y), tag, font=f, fill=color)


def draw_hero(img, d, x, y, w, h, tag, headline, summary, scene):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    img.paste(render_scene(scene, w - 2, 87, native_h=91), (x + 1, y + 1))
    d.line([(x, y + 88), (x + w, y + 88)], fill=RULE, width=1)
    tx = x + 10
    draw_tag(d, tx, y + 96, tag)
    hf = SERIF_B(21)
    lines = wrap(d, headline, hf, w - 20)
    ly = y + 114
    for ln in lines[:2]:
        d.text((tx, ly), ln, font=hf, fill=INK)
        ly += 25
    sf0 = SANS(13)
    sf, slines = fit_lines(d, summary, sf0, w - 20, 2, [13, 12])
    ly += 2
    for ln in slines:
        d.text((tx, ly), ln, font=sf, fill=CHARCOAL)
        ly += 17


def draw_card(img, d, x, y, w, h, tag, headline, summary, pill, scene):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    img.paste(render_scene(scene, w - 2, 51), (x + 1, y + 1))
    d.line([(x, y + 51), (x + w, y + 51)], fill=RULE, width=1)
    tx = x + 10
    draw_tag(d, tx, y + 57, tag)
    hf = SERIF_B(17)
    lines = wrap(d, headline, hf, w - 20)
    ly = y + 71
    for ln in lines[:2]:
        d.text((tx, ly), ln, font=hf, fill=INK)
        ly += 20
    # summary: fit in 2 lines, shrinking 12 -> 11 if needed
    sf0 = SANS(12)
    sf, slines = fit_lines(d, summary, sf0, w - 20, 2, [12, 11])
    ly += 2
    for ln in slines:
        d.text((tx, ly), ln, font=sf, fill=CHARCOAL)
        ly += 14
    # key-fact pill
    pf = SANS_B(11)
    pw = text_w(d, pill, pf) + 18
    py = y + h - 24
    d.rounded_rectangle([tx, py, tx + pw, py + 20], 10, fill=INK)
    d.text((tx + 9, py + 4), pill, font=pf, fill=WHITE)


def draw_wide(img, d, x, y, w, h, tag, headline, summary, pill, scene):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    iw = 150
    img.paste(render_scene(scene, iw - 1, h - 2), (x + 1, y + 1))
    d.line([(x + iw, y), (x + iw, y + h)], fill=RULE, width=1)
    tx = x + iw + 12
    tw = w - iw - 24
    draw_tag(d, tx, y + 8, tag)
    hf = SERIF_B(17)
    lines = wrap(d, headline, hf, tw)
    ly = y + 21
    for ln in lines[:2]:
        d.text((tx, ly), ln, font=hf, fill=INK)
        ly += 19
    sf0 = SANS(12)
    sf, slines = fit_lines(d, summary, sf0, tw, 2, [12, 11])
    ly += 2
    for ln in slines:
        d.text((tx, ly), ln, font=sf, fill=CHARCOAL)
        ly += 13
    pf = SANS_B(11)
    pw = text_w(d, pill, pf) + 18
    py = y + h - 24
    d.rounded_rectangle([tx, py, tx + pw, py + 20], 10, fill=INK)
    d.text((tx + 9, py + 4), pill, font=pf, fill=WHITE)


def draw_map_panel(img, d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    hf = SANS_B(12)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=hf, fill=WHITE)
    # continents
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=NAVY2)
    # pins
    pf = SANS_B(9)
    for num, label, px, py in PINS:
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=(10, 10, 16), width=2)
        s = str(num)
        d.text((px - text_w(d, s, pf) / 2, py - 6), s, font=pf, fill=WHITE)
    # legend (2 lines)
    lf = SANS_B(11)
    legend = "  ·  ".join("%d %s" % (n, lab) for n, lab, _, _ in PINS)
    lines = wrap(d, legend, lf, w - 20)
    ly = y + h - 8 - 14 * len(lines)
    for ln in lines:
        d.text((x + 10, ly), ln, font=lf, fill=WHITE)
        ly += 14


def draw_digest_panel(img, d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    hf = SANS_B(12)
    d.text((x + 10, y + 8), "ALSO ON TUESDAY 24 NOVEMBER", font=hf, fill=INK)
    d.line([(x + 10, y + 28), (x + w - 10, y + 28)], fill=RULE, width=1)
    col_w = (w - 30) // 2
    # Stack each column's 4 items with a 3px gap between items, all at
    # 12.5px bold charcoal. Wording is shortened so every item fits 2
    # lines; the stack totals 109px of the 111px available, leaving clean
    # breathing room above the footer.
    top = y + 33
    avail = y + h - 6 - top
    for size in (12.5,):
        df = SANS_B(size)
        lh = size  # line height equals the font size (tight, clean stack)
        cols = []
        ok = True
        for col in range(2):
            items = []
            total = 0
            for i in range(4):
                item = DIGEST[col * 4 + i]
                lines = wrap(d, item, df, col_w - 16)
                items.append(lines)
                total += len(lines) * lh + 3
            if total - 3 > avail:
                ok = False
            cols.append(items)
        if ok:
            break
    bullet_w = text_w(d, "▪ ", df)
    for col in range(2):
        ix = x + 10 + col * (col_w + 10)
        iy = top
        for lines in cols[col]:
            d.text((ix, iy), "▪", font=df, fill=RED)
            ly = iy
            for ln in lines:
                d.text((ix + bullet_w, ly), ln, font=df, fill=CHARCOAL)
                ly += lh
            iy = ly + 3


def draw_footer(img, d):
    y0, y1 = 992, 1014
    d.rectangle([MARGIN, y0, W - MARGIN, y1], fill=NAVY)
    f = SANS_B(11)
    s = ("✓ DATE CHECK — EVERY STORY ON THIS PAGE OCCURRED OR WAS FIRST "
         "REPORTED ON TUESDAY 24 NOVEMBER 2026 (UTC)")
    d.text(((W - text_w(d, s, f)) / 2, y0 + 6), s, font=f, fill=WHITE)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(img, d)
    draw_kpi(img, d)
    # heroes
    hw, gap = 320, 10
    for i, (tag, head, summ, scene) in enumerate(HEROES):
        draw_hero(img, d, MARGIN + i * (hw + gap), 158, hw, 204,
                  tag, head, summ, scene)
    # rows of 3
    for r, trio in enumerate([CARDS[0:3], CARDS[3:6]]):
        yy = 370 + r * 176
        for i, (tag, head, summ, pill, scene) in enumerate(trio):
            draw_card(img, d, MARGIN + i * (hw + gap), yy, hw, 168,
                      tag, head, summ, pill, scene)
    # bottom row: 2 wide cards (cards 7 and 8)
    ww = (CW - gap) // 2
    for i, (tag, head, summ, pill, scene) in enumerate(CARDS[6:8]):
        draw_wide(img, d, MARGIN + i * (ww + gap), 720, ww, 116,
                  tag, head, summ, pill, scene)
    # bottom split
    draw_map_panel(img, d, MARGIN, 838, ww, 150)
    draw_digest_panel(img, d, MARGIN + ww + gap, 838, ww, 150)
    draw_footer(img, d)
    return img


def main():
    img = render()
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", compress_level=6)
    os.chmod(out, 0o644)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
