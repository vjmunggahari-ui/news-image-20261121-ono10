#!/usr/bin/env python3
"""Render the news-image-20261121 front page (1024x1024 PNG).

Draws a dense newspaper front page for Saturday 21 November 2026 from a
fixed, dated story table. No network, no randomness, no timestamps: the
same input always produces the same bytes. Run: python3 tools/render.py
writes entry.png next to this file's parent (the repo root).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 26                      # outer margin
CW = W - 2 * M              # content width = 972
PAPER = (247, 242, 230)
INK = (20, 20, 20)
RED = (176, 30, 30)
GRAY = (85, 85, 85)
LINE = (20, 20, 20)
REGION = {
    "Europe": (29, 78, 158),
    "Asia": (176, 30, 30),
    "Middle East": (138, 109, 0),
    "Americas": (107, 63, 160),
    "Oceania": (14, 124, 123),
    "Global": (68, 68, 68),
}

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    for base in (FDIR, "/usr/share/fonts/truetype/noto"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise OSError("font not found: %s" % name)


SERIF = "DejaVuSerif-Bold.ttf"
SERIF_R = "DejaVuSerif.ttf"
SERIF_I = "NotoSerif-Italic.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, f, fill, max_w, leading, max_lines=None):
    """Draw wrapped text; returns y just below the last line."""
    lines = wrap(d, text, f, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def center(d, y, text, f, fill, cx=W // 2):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)
    return y + f.size + 4


# ---------------------------------------------------------------- stories
# Every story happened, or was first reported, on Saturday 21 Nov 2026.
# Sources are the outlets that reported it that day (named on the page).
LEADS = [
    {
        "n": 1, "region": "Europe", "tag": "POLAND · CONFLICT",
        "head": "Russian missiles fall in Poland",
        "body": ("Two Russian missiles and a suspected drone came down in "
                 "Poland. Warsaw calls it a deliberate provocation; NATO "
                 "calls it a grave violation of its airspace."),
        "src": "One Turn News", "art": "poland",
    },
    {
        "n": 2, "region": "Americas", "tag": "WALL STREET · MARKETS",
        "head": "Wall Street enters correction",
        "body": ("US stocks fell about 3.7% as a sell-off in AI and chip "
                 "shares pushed the S&P 500 and the Dow into correction "
                 "territory."),
        "src": "One Turn News", "art": "markets",
    },
    {
        "n": 3, "region": "Asia", "tag": "ODISHA, INDIA · CYCLONE",
        "head": "Cyclone Akvan weakens after landfall",
        "body": ("Akvan crossed the Odisha and Andhra Pradesh coasts near "
                 "Gopalpur, bringing strong winds and heavy rain, then "
                 "weakened as it moved inland."),
        "src": "Jagran Josh", "art": "cyclone",
    },
]

GRID = [
    {"n": 4, "region": "Europe", "tag": "BRUSSELS · DIPLOMACY",
     "head": "UK and EU seal a \u201creset\u201d deal",
     "body": "Food trade, youth visas, carbon link agreed in Brussels.",
     "src": "One Turn News", "art": "flags"},
    {"n": 5, "region": "Global", "tag": "SHENZHEN · SUMMIT",
     "head": "Trump–Xi–Putin summit ends thin",
     "body": "First trilateral meeting closes with few concrete results.",
     "src": "One Turn News", "art": "summit"},
    {"n": 6, "region": "Global", "tag": "ANTALYA · CLIMATE",
     "head": "COP31 reaches its last day with no deal",
     "body": "Draft text leaves out fossil fuels as talks stall in Turkey.",
     "src": "Jagran Josh", "art": "globe"},
    {"n": 7, "region": "Americas", "tag": "NEW YORK · TECH",
     "head": "Anthropic falls 9% after record IPO",
     "body": "Shares slide a day after the record listing.",
     "src": "NDTV", "art": "down"},
    {"n": 8, "region": "Americas", "tag": "LOS ANGELES · GAMES",
     "head": "GTA VI banks $3.79bn on day one",
     "body": "Record first-day retail sales, reports say.",
     "src": "NDTV", "art": "sunset"},
    {"n": 9, "region": "Americas", "tag": "NEW YORK · CYBER",
     "head": "Banks hit by vendor cyberattack",
     "body": "JPMorgan, Visa, Mastercard report third-party incidents.",
     "src": "Jagran Josh", "art": "shield"},
    {"n": 10, "region": "Middle East", "tag": "CENTRAL IRAQ · SECURITY",
     "head": "Iraqi army deploys into militia stronghold",
     "body": "Troops move into an Iran-backed stronghold at Jurf al-Sakhr.",
     "src": "m.lamediterranee.eu", "art": "convoy"},
    {"n": 11, "region": "Middle East", "tag": "RIYADH · CONFLICT",
     "head": "Houthi missiles intercepted over Riyadh",
     "body": "Saudi coalition says three ballistic missiles destroyed.",
     "src": "One Turn News", "art": "missile"},
    {"n": 12, "region": "Europe", "tag": "BRUSSELS · AID",
     "head": "EU pledges \u20ac90bn to Ukraine",
     "body": "\u20ac90bn by end of 2027, plus \u20ac70bn in military aid from allies.",
     "src": "R\u00e9seau ADSI", "art": "euro"},
    {"n": 13, "region": "Oceania", "tag": "WELLINGTON · CRICKET",
     "head": "India fight back in Wellington Test",
     "body": "India 159/1 at stumps on day two, trailing by 209 runs.",
     "src": "Jagran Josh", "art": "cricket"},
]

ALSO = [
    {"n": 14, "region": "Asia",
     "head": "Sensex rallies 898 points", "src": "Jagran Josh"},
    {"n": 15, "region": "Asia",
     "head": "NSE now the world\u2019s 5th-largest listed exchange",
     "src": "Daily Jagran"},
    {"n": 16, "region": "Asia",
     "head": "Indonesia fire losses could reach $30bn", "src": "Daily Jagran"},
    {"n": 17, "region": "Asia",
     "head": "Pakistan suicide bombing kills 5, injures 13",
     "src": "Times of India"},
    {"n": 18, "region": "Americas",
     "head": "Trump \u201cclose to deal\u201d with Mexico; more work with Canada",
     "src": "Forex Factory"},
    {"n": 19, "region": "Americas",
     "head": "Trump threatens ban on US firms building AI data centres abroad",
     "src": "BBC"},
    {"n": 20, "region": "Americas",
     "head": "Indian man jailed 19+ years in Sikh-leader murder plot",
     "src": "BBC"},
    {"n": 21, "region": "Americas",
     "head": "Bolsonaro taken to hospital with severe abdominal pain",
     "src": "Times of India"},
    {"n": 22, "region": "Europe",
     "head": "Berlin does not rule out talks with the Kremlin",
     "src": "m.lamediterranee.eu"},
    {"n": 23, "region": "Europe",
     "head": "US floats NATO membership for Ukraine in exchange for land",
     "src": "m.lamediterranee.eu"},
    {"n": 24, "region": "Europe",
     "head": "Kryvyi Rih strike: 2 dead, 42 injured", "src": "AppiSToS"},
    {"n": 25, "region": "Asia",
     "head": "South Korea reports first cholera case in a decade",
     "src": "R\u00e9seau ADSI"},
    {"n": 26, "region": "Asia",
     "head": "Nepal PM Balendra Shah to visit India, 22\u201323 Nov",
     "src": "Daily Jagran"},
    {"n": 27, "region": "Global",
     "head": "Carlsen forfeits rapid games at chess tournament",
     "src": "Education Times"},
    {"n": 28, "region": "Europe",
     "head": "UEFA backs Diallo to stand against Infantino in FIFA vote",
     "src": "Daily Jagran"},
    {"n": 29, "region": "Global",
     "head": "UN warns hunger will grow as food-aid funding runs short",
     "src": "Education Times"},
    {"n": 30, "region": "Global",
     "head": "UN gives $52m for schooling children in crisis countries",
     "src": "Education Times"},
    {"n": 31, "region": "Asia",
     "head": "Malaysia to resettle 10,000 Rohingya in Turkiye after ICJ ruling",
     "src": "Daily Jagran"},
    {"n": 32, "region": "Middle East",
     "head": "Iran war nears ninth month; Trump says he is not rushing",
     "src": "One Turn News"},
]

NUMBERS = [
    ("2", "missiles down in Poland"),
    ("\u22123.7%", "S&P 500, Friday"),
    ("$3.79bn", "GTA VI day-one sales"),
    ("898", "Sensex points gained"),
    ("\u20ac90bn", "EU aid to Ukraine"),
    ("$30bn", "Indonesia fire losses"),
]

DATE_CHECK = ("DATE CHECK \u2014 Left out because it happened on another day: the "
              "World Court\u2019s Myanmar genocide ruling (Thu 19 Nov \u2014 only the "
              "reactions are today\u2019s news); Cyclone Akvan\u2019s landfall, the "
              "OFAC sanctions on four Iranians, the UK drone pledge and the ECB "
              "board race (all Fri 20 Nov); COP31\u2019s final text (not agreed by "
              "press time).")

# ---------------------------------------------------------------- drawing

def starburst(d, cx, cy, r, color):
    pts = []
    for i in range(16):
        ang = 3.14159265 * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * __import__("math").cos(ang),
                    cy + rr * __import__("math").sin(ang)))
    d.polygon(pts, fill=color)


def art_poland(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 30, 51))
    for sx, sy in [(20, 12), (60, 26), (110, 8), (150, 30), (200, 14),
                   (250, 34), (290, 10), (90, 44), (170, 52), (230, 48)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 255, 255))
    # ground + bridge silhouette
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(8, 14, 26))
    d.arc([x + 30, y + h - 52, x + w - 30, y + h + 6], 180, 360,
          fill=(40, 60, 96), width=4)
    for bx in (70, 130, 190, 250):
        d.line([x + bx, y + h - 34, x + bx, y + h - 20], fill=(40, 60, 96),
               width=3)
    # two dashed missile trails
    for (x0, y0, x1, y1) in [(40, 8, 150, 62), (270, 6, 190, 58)]:
        steps = 9
        for i in range(steps):
            if i % 2 == 0:
                continue
            ax = x + x0 + (x1 - x0) * i / steps
            ay = y + y0 + (y1 - y0) * i / steps
            bx = x + x0 + (x1 - x0) * (i + 0.7) / steps
            by = y + y0 + (y1 - y0) * (i + 0.7) / steps
            d.line([ax, ay, bx, by], fill=(255, 255, 255), width=2)
    starburst(d, x + 150, y + 62, 12, (255, 176, 32))
    starburst(d, x + 190, y + 58, 9, (255, 120, 40))
    d.ellipse([x + 146, y + 58, x + 154, y + 66], fill=(255, 240, 180))


def art_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 24, 34))
    for gy in (y + 22, y + 48, y + 74):
        d.line([x + 8, gy, x + w - 8, gy], fill=(58, 58, 74), width=1)
    pts = [(x + 14, y + 18), (x + 60, y + 26), (x + 100, y + 24),
           (x + 140, y + 44), (x + 180, y + 52), (x + 220, y + 66),
           (x + 260, y + 78), (x + 296, y + 92)]
    d.line(pts, fill=(224, 49, 49), width=4, joint="curve")
    d.polygon([(x + 296, y + 92), (x + 288, y + 84), (x + 288, y + 96)],
              fill=(224, 49, 49))
    for i, bh in enumerate([14, 20, 16, 30, 38, 46, 54]):
        bx = x + 30 + i * 38
        d.rectangle([bx, y + h - 8 - bh, bx + 18, y + h - 8],
                    fill=(120, 120, 140))


def art_cyclone(d, x, y, w, h):
    for i in range(6):
        d.rectangle([x, y + i * h // 6, x + w, y + (i + 1) * h // 6],
                    fill=(38 + i * 8, 96 + i * 6, 150 + i * 4))
    cx, cy = x + w // 2 - 8, y + h // 2 + 14
    for r in (42, 33, 24, 16, 9):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(255, 255, 255),
              width=3)
    d.polygon([(x + w - 90, y + h), (x + w, y + 30), (x + w, y + h)],
              fill=(216, 196, 150))
    d.ellipse([x + w - 108, y + h - 30, x + w - 96, y + h - 18],
              fill=(224, 49, 49))
    d.ellipse([x + w - 112, y + h - 34, x + w - 92, y + h - 14],
              outline=(255, 255, 255), width=2)
    d.text((x + 10, y + 8), "BAY OF BENGAL", font=font(SANS_B, 11),
           fill=(255, 255, 255))


def chip(d, x, y, w, h, kind):
    if kind == "flags":
        d.rectangle([x, y, x + w // 2, y + h], fill=(18, 52, 120))
        d.rectangle([x, y + h // 2 - 3, x + w // 2, y + h // 2 + 3],
                    fill=(255, 255, 255))
        d.rectangle([x + w // 4 - 3, y, x + w // 4 + 3, y + h],
                    fill=(255, 255, 255))
        d.rectangle([x, y + h // 2 - 1, x + w // 2, y + h // 2 + 1],
                    fill=(200, 30, 30))
        d.rectangle([x + w // 4 - 1, y, x + w // 4 + 1, y + h],
                    fill=(200, 30, 30))
        d.rectangle([x + w // 2, y, x + w, y + h], fill=(0, 40, 110))
        for k in range(8):
            import math
            a = math.pi * k / 4
            d.ellipse([x + w * 0.75 + 11 * math.cos(a) - 2,
                       y + h / 2 + 9 * math.sin(a) - 2,
                       x + w * 0.75 + 11 * math.cos(a) + 2,
                       y + h / 2 + 9 * math.sin(a) + 2], fill=(255, 215, 0))
    elif kind == "summit":
        d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
        for i, col in enumerate([(200, 30, 30), (30, 90, 160), (240, 240, 240)]):
            px = x + 40 + i * 55
            d.rectangle([px, y + 4, px + 34, y + 16], fill=col)
            d.line([px + 2, y + 4, px + 2, y + h - 4], fill=(60, 60, 60),
                   width=2)
    elif kind == "globe":
        d.rectangle([x, y, x + w, y + h], fill=(38, 96, 150))
        d.ellipse([x + 14, y + 4, x + 46, y + 32], fill=(46, 160, 90))
        d.ellipse([x + 22, y + 10, x + 30, y + 16], fill=(38, 96, 150))
        d.rectangle([x + 66, y + 6, x + 72, y + 26], fill=(224, 49, 49))
        d.ellipse([x + 62, y + 24, x + 76, y + 34], fill=(224, 49, 49))
        d.text((x + 86, y + 10), "1.5\u00b0C", font=font(SANS_B, 13),
               fill=(255, 255, 255))
    elif kind == "down":
        d.rectangle([x, y, x + w, y + h], fill=(24, 24, 34))
        for i, bh in enumerate([26, 22, 18, 12, 8]):
            bx = x + 16 + i * 26
            d.rectangle([bx, y + h - 4 - bh, bx + 14, y + h - 4],
                        fill=(224, 49, 49))
        d.polygon([(x + w - 34, y + 6), (x + w - 16, y + 6), (x + w - 25, y + 26)],
                  fill=(224, 49, 49))
    elif kind == "sunset":
        for i, col in enumerate([(90, 40, 120), (200, 60, 90), (240, 140, 60),
                                 (250, 200, 90)]):
            d.rectangle([x, y + i * h // 4, x + w, y + (i + 1) * h // 4],
                        fill=col)
        d.ellipse([x + w - 52, y + 6, x + w - 28, y + 30], fill=(255, 240, 180))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(30, 20, 40))
    elif kind == "shield":
        d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
        d.polygon([(x + 20, y + 4), (x + 48, y + 4), (x + 48, y + 20),
                   (x + 34, y + 32), (x + 20, y + 20)], fill=(29, 78, 158))
        d.text((x + 29, y + 8), "!", font=font(SANS_B, 16), fill=(255, 215, 0))
        d.line([x + 62, y + 8, x + 150, y + 8], fill=(120, 120, 120), width=2)
        d.line([x + 62, y + 16, x + 150, y + 16], fill=(120, 120, 120), width=2)
        d.line([x + 62, y + 24, x + 120, y + 24], fill=(120, 120, 120), width=2)
    elif kind == "convoy":
        d.rectangle([x, y, x + w, y + h], fill=(216, 196, 150))
        d.rectangle([x, y + h - 12, x + w, y + h - 8], fill=(90, 80, 60))
        for i in range(3):
            vx = x + 20 + i * 56
            d.rectangle([vx, y + 8, vx + 40, y + 20], fill=(60, 80, 50))
            d.ellipse([vx + 6, y + 20, vx + 12, y + 26], fill=(20, 20, 20))
            d.ellipse([vx + 28, y + 20, vx + 34, y + 26], fill=(20, 20, 20))
    elif kind == "missile":
        d.rectangle([x, y, x + w, y + h], fill=(180, 210, 230))
        d.polygon([(x + 30, y + 14), (x + 120, y + 14), (x + 138, y + 18),
                   (x + 120, y + 22), (x + 30, y + 22)], fill=(90, 90, 100))
        d.polygon([(x + 30, y + 10), (x + 44, y + 18), (x + 30, y + 26)],
                  fill=(224, 49, 49))
        for i in range(5):
            d.ellipse([x + 150 + i * 7, y + 16, x + 154 + i * 7, y + 20],
                      fill=(255, 255, 255))
    elif kind == "euro":
        d.rectangle([x, y, x + w, y + h], fill=(0, 40, 110))
        d.text((x + 16, y + 2), "\u20ac", font=font(SANS_B, 26),
               fill=(255, 255, 255))
        for k in range(6):
            import math
            a = math.pi * k / 3
            d.ellipse([x + 130 + 12 * math.cos(a) - 2,
                       y + h / 2 + 10 * math.sin(a) - 2,
                       x + 130 + 12 * math.cos(a) + 2,
                       y + h / 2 + 10 * math.sin(a) + 2], fill=(255, 215, 0))
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(46, 140, 70))
        d.rectangle([x, y + h - 10, x + w, y + h], fill=(120, 90, 50))
        d.rectangle([x + 30, y + 6, x + 34, y + 24], fill=(240, 220, 160))
        d.rectangle([x + 38, y + 6, x + 42, y + 24], fill=(240, 220, 160))
        d.rectangle([x + 46, y + 6, x + 50, y + 24], fill=(240, 220, 160))
        d.ellipse([x + 120, y + 10, x + 132, y + 22], fill=(255, 255, 255))
        d.rectangle([x + 80, y + 22, x + 112, y + 28], fill=(150, 110, 60))


LEAD_ART = {"poland": art_poland, "markets": art_markets,
            "cyclone": art_cyclone}


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(LEADS) + len(GRID) + len(ALSO)
    counts = {}
    for s in LEADS + GRID + ALSO:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    order = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    y = 14
    # masthead
    d.text((M, y), "THE WORLD TODAY", font=font(SANS_B, 20), fill=RED)
    right = "%d STORIES \u00b7 %d REGIONS \u00b7 EVERY ONE DATED" % (
        total, len(counts))
    d.text((W - M - d.textlength(right, font=font(SANS_B, 14)), y + 3),
           right, font=font(SANS_B, 14), fill=INK)
    y += 30
    d.rectangle([M, y, W - M, y + 3], fill=LINE)
    y += 12
    # giant date headline
    y = center(d, y, "Saturday 21 November 2026", font(SERIF, 56), INK) - 4
    # sub-headline: the four biggest stories, one line
    sub = ("Russian missiles fall in Poland  \u00b7  Wall Street enters "
           "correction  \u00b7  Cyclone Akvan weakens  \u00b7  UK and EU seal a deal")
    y = center(d, y + 2, sub, font(SERIF_I, 16), INK)
    y += 6
    d.rectangle([M, y, W - M, y + 1], fill=LINE)
    y += 8
    # numbers strip: six figures that carry the day
    cell = CW // 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cell
        if i:
            d.line([cx, y, cx, y + 46], fill=(180, 175, 160), width=1)
        d.text((cx + 10, y), num, font=font(SERIF, 23), fill=INK)
        d.text((cx + 10, y + 28), cap, font=font(SANS, 10), fill=GRAY)
    y += 54
    d.rectangle([M, y, W - M, y + 1], fill=LINE)
    y += 8
    # region tabs
    tx = M
    for name, n in order:
        label = "%s %d" % (name.upper(), n)
        f = font(SANS_B, 13)
        tw = d.textlength(label, font=f) + 20
        d.rounded_rectangle([tx, y, tx + tw, y + 24], radius=4,
                            fill=REGION[name])
        d.text((tx + 10, y + 4), label, font=f, fill=(255, 255, 255))
        tx += tw + 8
    d.text((W - M - d.textlength("ALL DATED 21 NOV 2026",
                                 font=font(SANS_B, 11)), y + 5),
           "ALL DATED 21 NOV 2026", font=font(SANS_B, 11), fill=GRAY)
    y += 34
    # three lead stories, each with a drawn illustration
    pw, gap = 312, 18
    for i, s in enumerate(LEADS):
        px = M + i * (pw + gap)
        LEAD_ART[s["art"]](d, px, y, pw, 100)
        yy = y + 108
        d.text((px, yy), "%d \u00b7 %s" % (s["n"], s["tag"]),
               font=font(SANS_B, 11), fill=RED)
        yy += 16
        yy = text_block(d, px, yy, s["head"], font(SERIF, 19), INK, pw, 22,
                        max_lines=2)
        yy += 2
        yy = text_block(d, px, yy, s["body"], font(SANS, 12), INK, pw, 15,
                        max_lines=4)
        d.text((px, y + 228), "(%s)" % s["src"], font=font(SERIF_I, 10),
               fill=GRAY)
    y += 244
    # ten-story grid, two rows of five
    cw, cgap = 186, 10
    for row in range(2):
        for col in range(5):
            s = GRID[row * 5 + col]
            gx = M + col * (cw + cgap)
            gy = y + row * 140
            chip(d, gx, gy, cw, 36, s["art"])
            yy = gy + 42
            d.text((gx, yy), "%d \u00b7 %s" % (s["n"], s["tag"]),
                   font=font(SANS_B, 10), fill=RED)
            yy += 14
            yy = text_block(d, gx, yy, s["head"], font(SERIF, 13), INK, cw,
                            16, max_lines=2)
            yy += 1
            yy = text_block(d, gx, yy, s["body"], font(SANS, 10), INK, cw,
                            13, max_lines=2)
            d.text((gx, gy + 124), "(%s)" % s["src"], font=font(SERIF_I, 9),
                   fill=GRAY)
    y += 292
    # also list: the rest of the day, numbered, two columns
    d.text((M, y), "ALSO ON SATURDAY 21 NOVEMBER \u2014 %d MORE STORIES"
           % len(ALSO), font=font(SANS_B, 13), fill=INK)
    y += 20
    d.rectangle([M, y, W - M, y + 1], fill=LINE)
    y += 8
    col_w = (CW - 24) // 2
    half = (len(ALSO) + 1) // 2
    for idx, s in enumerate(ALSO):
        col = 0 if idx < half else 1
        row = idx if idx < half else idx - half
        ix = M + col * (col_w + 24)
        iy = y + row * 14
        d.text((ix, iy), "%d  %s  (%s)" % (s["n"], s["head"], s["src"]),
               font=font(SANS, 11), fill=INK)
    y += half * 14 + 8
    # date-check box: what was deliberately left out
    box_top = y
    lines = wrap(d, DATE_CHECK, font(SANS, 11), CW - 20)
    box_h = len(lines) * 14 + 12
    d.rectangle([M, box_top, W - M, box_top + box_h], outline=RED, width=2)
    yy = box_top + 6
    for line in lines:
        d.text((M + 10, yy), line, font=font(SANS, 11), fill=INK)
        yy += 14
    y = box_top + box_h + 8
    # footer
    center(d, y, ("Every story here happened, or was first reported, on "
                  "Saturday 21 November 2026. Sources are named beside each "
                  "story. Original drawings."),
           font(SANS, 9), GRAY)
    y += 14
    assert y <= 1020, "layout overflow: y=%d" % y
    print("layout ok, final y=%d, stories=%d, regions=%s"
          % (y, total, dict(order)))
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "entry.png")
    img = build()
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
