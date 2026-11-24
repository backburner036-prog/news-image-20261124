#!/usr/bin/env python3
"""Render entry.png for news-image-20261124 — 'THE WORLD TODAY'.

Clean-room build, written fresh in this session (24 Nov 2026) from the frozen
v5 template geometry (1024x1024, fixed vertical budget, Liberation fonts,
GATE-D) with fresh 24 November 2026 content (see
news-image-20261124-research.md): hero is Tuesday's Asia markets rally on
Huang's return (Nikkei +4.5%, Kospi +7.5%, Taiex +9.1%), 35 stories
(1 hero + 3 leads + 31 briefs), 7 regions, UTC timeline, no map.
Standard library + Pillow only. No network. Deterministic: no timestamps,
no randomness, fixed fonts, fixed layout.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
INK = (0x11, 0x11, 0x11)
GREY = (0x55, 0x55, 0x55)
LIGHT = (0xCC, 0xCC, 0xCC)
RED = (0xC0, 0x39, 0x2B)
PANEL = (0xF5, 0xF5, 0xF5)
WHITE = (0xFF, 0xFF, 0xFF)
GOLD = (0xFF, 0xD6, 0x17)
DARK = (0x1A, 0x1A, 0x22)
GREEN_BG_TOP = (0x0F, 0x2A, 0x1E)
GREEN_BG_MID = (0x14, 0x53, 0x2D)
GREEN_BG_BOT = (0x1F, 0x7A, 0x44)
GREEN_LINE = (0x4A, 0xDE, 0x80)
STEEL = (0x8A, 0x95, 0xA5)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(fnt, text, max_width):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        if fnt.getlength(" ".join(trial)) <= max_width or not cur:
            cur = trial
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ data
HERO = {
    "kicker": "TOP STORY  —  ASIA MARKETS",
    "headline": "Asia rallies on Huang's return",
    "sub": "Nikkei up 4.5% as Kospi jumps 7.5%",
    "source": "Reuters",
}

STRIP = [
    ("+7.5%", "KOSPI JUMPS (#1)"),
    ("+9.1%", "TAIEX SURGES (#1)"),
    ("M5.3", "NEPAL QUAKE (#5)"),
    ("$2.6B", "AAVE USDC LOANS (#26)"),
    ("91", "BANGLADESH ALL OUT (#33)"),
]

LEADS = [
    {
        "num": 2,
        "title": "Wong calls AI a foreign-policy challenge",
        "sentence": "Wong: AI reshapes policy.",
        "source": "Defence Connect",
        "art": "ai",
    },
    {
        "num": 3,
        "title": "Gaza strike kills three near Khan Younis",
        "sentence": "Airstrike kills three near Khan Younis.",
        "source": "Reuters",
        "art": "rubble",
    },
    {
        "num": 4,
        "title": "Seoul warns Ulleung after Russian jet intrusion",
        "sentence": "Seoul warns Ulleung after jet intrusion.",
        "source": "Reuters",
        "art": "radar",
    },
]

TIMELINE = [
    ("00:53 UTC", "ANDREW BRIBE CLAIM"),
    ("01:20 UTC", "WARSHIP SUNK OFF LIBYA"),
    ("01:26 UTC", "MOSCOW ACCUSES ESTONIA"),
    ("01:56 UTC", "VANCE PUSHED NVIDIA RETURN"),
    ("02:10 UTC", "AAVE LOANS HIT $2.6B"),
]

# briefs: (number, title) — titles must fit 1 line at 14px bold in 312px
BRIEFS = [
    (5, "Nepal hit by 5.3 quake"),
    (6, "Dollar nears 20-month high"),
    (7, "Canada, Qatar sign investment pact"),
    (8, "North Korea mulls closing Swiss office"),
    (9, "US eyes Iran in tanker cyberattacks"),
    (10, "Moscow accuses Estonia of arson"),
    (11, "Russia summons Estonian envoy"),
    (12, "EU faults Tajikistan for hosting Putin"),
    (13, "Armenia starts work on Trump Route"),
    (14, "Russia rejects new grain deal"),
    (15, "US sanctions Iranian exchange houses"),
    (16, "Iran protests Qatar-Germany statement"),
    (17, "Trump may back Ukraine guarantees"),
    (18, "Zelenskyy: Ukraine sank Russian warship"),
    (19, "Four nations urge Israel on Gaza aid"),
    (20, "German metal workers in 24-hour strike"),
    (21, "Central Europe questions EU budget"),
    (22, "Trump halts Iowa lead-azide blast"),
    (23, "US details $12bn Venezuela oil revenue"),
    (24, "Kate Middleton film on cancer journey"),
    (25, "Prince Andrew in $1.4m bribe claim"),
    (26, "Aave USDC loans hit $2.6bn"),
    (27, "China climate records skewed by bias"),
    (28, "Alzheimer's pill slows decline 31%"),
    (29, "Huawei unveils Mate 90 Air"),
    (30, "Brazil tourism hits target early"),
    (31, "Sega Sammy rolls out smart tables"),
    (32, "Belvedere cuts DigiPlus stake"),
    (33, "South Africa bowls out Bangladesh for 91"),
    (34, "FIFA confirms 2031, 2035 World Cups"),
    (35, "Vance also pushed Nvidia return"),
]

COLS = [
    [b for b in BRIEFS if 5 <= b[0] <= 15],
    [b for b in BRIEFS if 16 <= b[0] <= 25],
    [b for b in BRIEFS if 26 <= b[0] <= 35],
]

REGIONS_LINE = ("REGIONS: NORTH AMERICA \u00b7 LATIN AMERICA \u00b7 EUROPE "
                "\u00b7 MIDDLE EAST \u00b7 ASIA \u00b7 AFRICA \u00b7 OCEANIA")
SOURCES_LINE = ("Sources: Reuters / CBS / Japan Times / SCMP / IANS / Le Monde / "
                "CryptoSlate / EMSC / Independent / SMH / Defence Connect")


# ------------------------------------------------------------------ draw
def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    diag = []

    f_mast = font(SERIF_BOLD, 64)
    f_date = font(SANS_BOLD, 22)
    f_info = font(SANS, 13)
    f_kick = font(SANS_BOLD, 13)
    f_hero = font(SERIF_BOLD, 36)
    f_sub = font(SANS, 17)
    f_num = font(SANS_BOLD, 20)
    f_lab = font(SANS, 9)
    f_lead = font(SERIF_BOLD, 18)
    f_sent = font(SANS, 13)
    f_num2 = font(SANS_BOLD, 15)
    f_time = font(SANS_BOLD, 11)
    f_tlab = font(SANS, 10)
    f_brief = font(SANS_BOLD, 14)
    f_reg = font(SANS, 10)
    f_src = font(SANS, 10)
    f_fdate = font(SANS_BOLD, 11)

    # ---- A. Header (0..100)
    d.rectangle([0, 0, 1024, 6], fill=RED)
    d.text((28, 12), "THE WORLD TODAY", font=f_mast, fill=INK)
    d.text((28, 78), "Tuesday, 24 November 2026", font=f_date, fill=RED)
    info = "35 STORIES  \u00b7  7 REGIONS  \u00b7  UTC TIMELINE"
    d.text((996 - f_info.getlength(info), 82), info, font=f_info, fill=GREY)
    d.rectangle([28, 102, 996, 105], fill=INK)
    d.rectangle([28, 107, 996, 108], fill=INK)
    diag.append(f"header date width {f_date.getlength('Tuesday, 24 November 2026'):.0f}")

    # ---- B. Hero panel (104..248): green market gradient + rising chart
    x0, y0, x1, y1 = 28, 104, 996, 248
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / (y1 - y0)
        if t < 0.5:
            col = lerp(GREEN_BG_TOP, GREEN_BG_MID, t * 2)
        else:
            col = lerp(GREEN_BG_MID, GREEN_BG_BOT, (t - 0.5) * 2)
        d.line([(x0, yy), (x1, yy)], fill=col)
    # faint grid
    for gx in range(x0 + 60, x1, 80):
        d.line([(gx, y0), (gx, y1)], fill=(0x1E, 0x5C, 0x3A), width=1)
    for gy in (y0 + 36, y0 + 72, y0 + 108):
        d.line([(x0, gy), (x1, gy)], fill=(0x1E, 0x5C, 0x3A), width=1)
    # rising chart line: steady climb, shallow dip mid-panel, steep finish.
    # Kept above y=196 on the left so it never crosses the RALLY text.
    pts = [(60, 190), (170, 178), (290, 186), (410, 196), (520, 176),
           (640, 150), (760, 135), (870, 120), (960, 112)]
    d.line(pts, fill=GREEN_LINE, width=5, joint="curve")
    # start + end dots
    d.ellipse([54, 184, 66, 196], fill=WHITE)
    d.ellipse([954, 106, 966, 118], fill=GREEN_LINE)
    # arrow head at the peak
    d.polygon([(968, 104), (940, 108), (958, 126)], fill=GREEN_LINE)
    # panel text
    d.text((48, 196), "RALLY", font=font(SANS_BOLD, 30), fill=WHITE,
           stroke_width=1, stroke_fill=(0x07, 0x1A, 0x10))
    d.text((48, 228), "\u2014 ASIA MARKETS", font=font(SANS_BOLD, 14), fill=WHITE,
           stroke_width=1, stroke_fill=(0x07, 0x1A, 0x10))
    diag.append(f"hero headline width {f_hero.getlength(HERO['headline']):.0f}/968")

    # ---- C. Headline hero (252..340)
    d.text((28, 252), HERO["kicker"], font=f_kick, fill=RED)
    d.text((28, 270), HERO["headline"], font=f_hero, fill=INK)
    sub = HERO["sub"] + " \u2014 " + HERO["source"]
    d.text((28, 312), sub, font=f_sub, fill=INK)
    diag.append(f"hero sub width {f_sub.getlength(sub):.0f}/968")

    # ---- D. Number strip (344..392): 5 boxes 184x48, gap 12
    for i, (num, lab) in enumerate(STRIP):
        bx = 28 + i * (184 + 12)
        d.rectangle([bx, 344, bx + 184, 392], fill=PANEL)
        d.text((bx + 10, 350), num, font=f_num, fill=RED)
        lw = f_lab.getlength(lab)
        d.text((bx + 10, 376), lab, font=f_lab, fill=GREY)
        diag.append(f"strip {i+1} label {lw:.1f}/164 num {num}")

    # ---- E. Leads (396..520): 3 cols @312, gap 16
    lead_xs = [28, 356, 684]
    for lx, lead in zip(lead_xs, LEADS):
        # thumb 312x56
        ty0, ty1 = 396, 452
        if lead["art"] == "ai":
            d.rectangle([lx, ty0, lx + 312, ty1], fill=DARK)
            d.text((lx + 12, ty0 + 8), "AI", font=font(SANS_BOLD, 36), fill=WHITE)
            # circuit: gold nodes + traces on the right
            for nx, ny in [(150, 14), (190, 30), (230, 12), (268, 32)]:
                d.rectangle([lx + nx, ty0 + ny, lx + nx + 8, ty0 + ny + 8],
                            fill=GOLD)
            d.line([(lx + 158, ty0 + 18), (lx + 190, ty0 + 34)], fill=GOLD, width=2)
            d.line([(lx + 198, ty0 + 34), (lx + 230, ty0 + 16)], fill=GOLD, width=2)
            d.line([(lx + 238, ty0 + 16), (lx + 268, ty0 + 36)], fill=GOLD, width=2)
            d.text((lx + 96, ty0 + 34), "DIPLOMACY", font=font(SANS_BOLD, 10),
                   fill=(0xBB, 0xBB, 0xBB))
        elif lead["art"] == "rubble":
            d.rectangle([lx, ty0, lx + 312, ty1], fill=DARK)
            # damaged skyline: upright blocks + one leaning block (polygon)
            d.rectangle([lx + 12, ty0 + 22, lx + 40, ty1], fill=(0x3A, 0x3A, 0x44))
            d.rectangle([lx + 46, ty0 + 30, lx + 68, ty1], fill=(0x3A, 0x3A, 0x44))
            d.polygon([(lx + 74, ty0 + 44), (lx + 96, ty0 + 18), (lx + 104, ty0 + 22),
                       (lx + 86, ty0 + 52)], fill=(0x4A, 0x4A, 0x55))
            d.rectangle([lx + 110, ty0 + 34, lx + 132, ty1], fill=(0x3A, 0x3A, 0x44))
            d.text((lx + 158, ty0 + 6), "3", font=font(SANS_BOLD, 30), fill=RED)
            d.text((lx + 184, ty0 + 12), "KILLED", font=font(SANS_BOLD, 16),
                   fill=WHITE)
            d.text((lx + 184, ty0 + 34), "KHAN YOUNIS", font=font(SANS_BOLD, 10),
                   fill=(0xBB, 0xBB, 0xBB))
        else:  # radar
            d.rectangle([lx, ty0, lx + 312, ty1], fill=DARK)
            cx, cy, r = lx + 46, ty0 + 28, 21
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=2)
            d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=GREEN_LINE,
                      width=1)
            d.line([(cx, cy), (cx + 15, cy - 15)], fill=GREEN_LINE, width=2)
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
            d.text((lx + 96, ty0 + 10), "ALERT", font=font(SANS_BOLD, 20),
                   fill=WHITE)
            d.text((lx + 96, ty0 + 34), "ULLEUNG ISLAND", font=font(SANS_BOLD, 10),
                   fill=(0xBB, 0xBB, 0xBB))
        # number (red) + headline (serif bold 18, max 2 lines)
        ntxt = f"{lead['num']}."
        nw = f_num2.getlength(ntxt)
        d.text((lx, 458), ntxt, font=f_num2, fill=RED)
        lines = wrap_text(f_lead, lead["title"], 312 - nw - 6)
        y = 458
        for ln in lines[:2]:
            d.text((lx + nw + 6, y), ln, font=f_lead, fill=INK)
            y += 22
        # one sentence (13px, 1 line)
        sent = lead["sentence"] + " \u2014 " + lead["source"]
        sw = f_sent.getlength(sent)
        diag.append(f"lead {lead['num']} sentence {sw:.1f}/312 lines {len(lines)}")
        if sw > 312:
            diag.append(f"OVERFLOW lead {lead['num']} sentence")
        d.text((lx, 500), sent, font=f_sent, fill=INK)

    # ---- F. Timeline UTC (524..576)
    d.line([(28, 548), (996, 548)], fill=INK, width=2)
    centers = [124, 318, 512, 705, 899]
    for (t, lab), cx in zip(TIMELINE, centers):
        d.ellipse([cx - 5, 543, cx + 5, 553], fill=RED)
        tw = f_time.getlength(t)
        d.text((cx - tw / 2, 526), t, font=f_time, fill=RED)
        lw = f_tlab.getlength(lab)
        d.text((cx - lw / 2, 556), lab, font=f_tlab, fill=INK)
        diag.append(f"timeline {t} label {lw:.1f}px at cx {cx}")

    # ---- G. Briefs (580..960): 3 cols @312, gap 16
    col_xs = [28, 356, 684]
    ends = []
    for cx, col in zip(col_xs, COLS):
        y = 580
        for num, title in col:
            item = f"{num}. {title}"
            w = f_brief.getlength(item)
            if w > 312:
                diag.append(f"OVERFLOW brief {num}: {w:.1f}/312 :: {item}")
            d.text((cx, y), item, font=f_brief, fill=INK)
            y += 24
        ends.append(y - 7)
    diag.append(f"brief column ends {ends} (limit <=940)")

    # ---- Regions line (946..960)
    d.text((28, 946), REGIONS_LINE, font=f_reg, fill=GREY)
    diag.append(f"regions line {f_reg.getlength(REGIONS_LINE):.1f}/968")

    # ---- H. Footer (964..1000)
    d.rectangle([28, 964, 996, 966], fill=INK)
    d.text((28, 972), SOURCES_LINE, font=f_src, fill=GREY)
    fdate = "TUESDAY, 24 NOVEMBER 2026"
    d.text((996 - f_fdate.getlength(fdate), 972), fdate, font=f_fdate, fill=INK)
    diag.append(f"sources line {f_src.getlength(SOURCES_LINE):.1f} vs date at "
                f"{996 - f_fdate.getlength(fdate):.0f}")

    img.save("entry.png", optimize=True)
    print("\n".join(diag))


if __name__ == "__main__":
    main()
