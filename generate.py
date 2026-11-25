#!/usr/bin/env python3
"""Deterministic generator for the news-image-20261125 entry.

Draws a one-page newspaper front page, "THE WORLD TODAY", summing up
Wednesday 25 November 2026 from six verified wire stories. The page is
composed with Pillow: flat shapes and DejaVu fonts for every panel, plus
one generated illustration (lead-art.png, made for this entry) cropped
into the lead panel. No network, no randomness. Running it twice writes
byte-identical PNGs.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
LEAD_ART = os.path.join(HERE, "lead-art.png")

PAPER = (248, 243, 230)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (90, 88, 80)
RULE = (40, 40, 40)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(text, fnt, max_width):
    """Greedy word wrap using the font's real metrics."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if fnt.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(text, fnt, max_width, max_lines):
    """Wrap text and fail loudly if it would overflow its box."""
    lines = wrap_text(text, fnt, max_width)
    if len(lines) > max_lines:
        raise ValueError(f"text overflows ({len(lines)} > {max_lines}): {text!r}")
    return lines


def rule(draw, x0, y, x1, width=2):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def kicker_headline(draw, x, y, width, kicker, headline, head_font,
                    head_leading, kicker_font):
    draw.text((x, y), kicker, font=kicker_font, fill=RED)
    y += 24
    lines = fit_lines(headline, head_font, width, 3)
    y = draw_lines(draw, x, y, lines, head_font, INK, head_leading)
    return y


def paste_lead_art(draw, img, x, y, w, h):
    """Centre-crop the generated lead illustration into its panel."""
    art = Image.open(LEAD_ART).convert("RGB")
    aw, ah = art.size
    target = w / h
    if aw / ah > target:
        nw = int(ah * target)
        off = (aw - nw) // 2
        art = art.crop((off, 0, off + nw, ah))
    else:
        nh = int(aw / target)
        off = (ah - nh) // 2
        art = art.crop((0, off, aw, off + nh))
    art = art.resize((w, h), Image.LANCZOS)
    img.paste(art, (x, y))
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)


# ---------------------------------------------------------------------------
# Flat illustrations: one small scene per story, drawn from rectangles,
# ellipses and polygons only. Each is drawn fresh for this entry.
# All coordinates are relative to the panel origin (x, y).
# ---------------------------------------------------------------------------

def art_chart(draw, x, y, w, h):
    """A falling market chart: red line diving down over candlesticks."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 234, 224))
    # faint horizontal gridlines
    for gy in (y + 14, y + 28, y + 42):
        draw.line([(x + 8, gy), (x + w - 8, gy)], fill=(210, 204, 190), width=1)
    # candlesticks, alternating down
    for i, (cx, top, bot) in enumerate([(40, 10, 26), (110, 16, 34),
                                        (180, 22, 40), (250, 30, 46),
                                        (320, 36, 50), (390, 42, 54)]):
        col = RED if i % 2 == 0 else (120, 40, 40)
        draw.line([(x + cx + 6, y + top - 4), (x + cx + 6, y + bot + 4)],
                  fill=col, width=2)
        draw.rectangle([x + cx, y + top, x + cx + 12, y + bot], fill=col)
    # red line diving from top-left to bottom-right
    pts = [(x + 12, y + 6), (x + 90, y + 12), (x + 170, y + 24),
           (x + 250, y + 30), (x + 330, y + 44), (x + w - 16, y + 50)]
    draw.line(pts, fill=RED, width=4, joint="curve")
    ax, ay = pts[-1]
    draw.polygon([(ax - 12, ay - 8), (ax + 4, ay), (ax - 12, ay + 8)],
                 fill=RED)


def art_warship(draw, x, y, w, h):
    """A warship at sea with an orange blast flash on the horizon."""
    draw.rectangle([x, y, x + w, y + h], fill=(36, 84, 120))
    # sun low on the horizon
    draw.ellipse([x + w - 60, y + 6, x + w - 28, y + 38],
                 fill=(226, 120, 60))
    # blast flash, right of centre
    bx, by = x + w - 130, y + 12
    draw.polygon([(bx, by - 8), (bx + 8, by + 2), (bx + 20, by - 4),
                  (bx + 12, by + 8), (bx + 22, by + 14), (bx + 4, by + 14),
                  (bx - 2, by + 24), (bx - 8, by + 10), (bx - 20, by + 12),
                  (bx - 10, by + 2)], fill=(240, 190, 60))
    # smoke above the blast
    for cx, cy, r in [(bx - 6, by - 12, 7), (bx + 6, by - 16, 6)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 112, 104))
    # warship hull, lower left
    draw.polygon([(x + 20, y + h - 14), (x + 210, y + h - 14),
                  (x + 196, y + h - 2), (x + 34, y + h - 2)],
                 fill=(24, 34, 44))
    draw.rectangle([x + 60, y + h - 28, x + 96, y + h - 14],
                   fill=(24, 34, 44))
    draw.rectangle([x + 120, y + h - 24, x + 132, y + h - 14],
                   fill=(24, 34, 44))
    # wake lines
    draw.line([(x + 20, y + h - 4), (x + 220, y + h - 4)],
              fill=(150, 200, 225), width=2)


def art_oil(draw, x, y, w, h):
    """A desert oil derrick under a hazy sun, grey cloud overhead."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 226, 200))
    # hazy sun
    draw.ellipse([x + w - 56, y + 6, x + w - 24, y + 38],
                 fill=(240, 190, 60))
    # grey cloud, mid-panel
    for cx, cy, r in [(200, 12, 12), (220, 8, 10), (240, 12, 11)]:
        draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                     fill=(150, 144, 134))
    # ground line
    draw.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(120, 100, 70),
              width=2)
    # oil derrick (A-frame), left-centre
    ax = x + 90
    draw.line([(ax - 34, y + h - 12), (ax, y + 6)], fill=(70, 66, 60), width=3)
    draw.line([(ax + 34, y + h - 12), (ax, y + 6)], fill=(70, 66, 60), width=3)
    draw.line([(ax - 22, y + h - 26), (ax + 22, y + h - 26)],
              fill=(70, 66, 60), width=2)
    draw.line([(ax - 12, y + h - 38), (ax + 12, y + h - 38)],
              fill=(70, 66, 60), width=2)
    # oil barrel, right
    draw.rectangle([x + w - 120, y + h - 34, x + w - 84, y + h - 12],
                   fill=(122, 44, 34))
    draw.line([(x + w - 120, y + h - 27), (x + w - 84, y + h - 27)],
              fill=(90, 30, 24), width=2)
    draw.line([(x + w - 120, y + h - 19), (x + w - 84, y + h - 19)],
              fill=(90, 30, 24), width=2)


def art_shop(draw, x, y, w, h):
    """A shopfront at night under flashing red and blue police lights."""
    draw.rectangle([x, y, x + w, y + h], fill=(22, 26, 40))
    # police light bars with glow, top corners
    draw.rectangle([x + 14, y + 6, x + 58, y + 16], fill=(220, 40, 40))
    draw.ellipse([x + 20, y + 18, x + 52, y + 26], fill=(240, 120, 120))
    draw.rectangle([x + w - 58, y + 6, x + w - 14, y + 16],
                   fill=(50, 90, 220))
    draw.ellipse([x + w - 52, y + 18, x + w - 20, y + 26],
                 fill=(120, 150, 240))
    # shopfront: awning + glass door + window
    draw.polygon([(x + 120, y + 18), (x + w - 120, y + 18),
                  (x + w - 100, y + 32), (x + 100, y + 32)],
                 fill=(178, 34, 34))
    draw.rectangle([x + 120, y + 32, x + w - 120, y + h - 4],
                   fill=(240, 226, 200))
    draw.rectangle([x + 140, y + 40, x + w - 220, y + h - 12],
                   fill=(70, 90, 110))
    draw.rectangle([x + w - 200, y + 40, x + w - 140, y + h - 12],
                   fill=(40, 52, 66))
    # lit shelves inside the window
    for sy in (y + 48, y + 60):
        draw.line([(x + 148, sy), (x + w - 228, sy)], fill=(240, 200, 90),
                  width=2)
    # pavement
    draw.rectangle([x, y + h - 4, x + w, y + h], fill=(60, 60, 66))


def art_space(draw, x, y, w, h):
    """A rocket climbing past stars toward a small space station."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    # stars
    for sx, sy in [(18, 12), (60, 26), (110, 10), (160, 22), (30, 60),
                   (90, 80), (150, 66), (180, 100), (44, 104), (120, 110)]:
        draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                     fill=(220, 220, 200))
    # planet, top right
    draw.ellipse([x + w - 46, y + 10, x + w - 14, y + 42],
                 fill=(52, 110, 168))
    draw.ellipse([x + w - 40, y + 18, x + w - 28, y + 26],
                 fill=(86, 150, 84))
    # space station, top left
    draw.rectangle([x + 16, y + 30, x + 64, y + 40], fill=(200, 200, 210))
    draw.rectangle([x + 8, y + 32, x + 16, y + 38], fill=(140, 160, 200))
    draw.rectangle([x + 64, y + 32, x + 72, y + 38], fill=(140, 160, 200))
    # rocket, centre, nose up
    rx = x + w // 2
    draw.polygon([(rx - 10, y + h - 34), (rx + 10, y + h - 34),
                  (rx + 10, y + h - 66), (rx, y + h - 84),
                  (rx - 10, y + h - 66)], fill=(240, 238, 230))
    draw.polygon([(rx - 18, y + h - 34), (rx - 10, y + h - 34),
                  (rx - 10, y + h - 52)], fill=RED)
    draw.polygon([(rx + 18, y + h - 34), (rx + 10, y + h - 34),
                  (rx + 10, y + h - 52)], fill=RED)
    # flame
    draw.polygon([(rx - 7, y + h - 34), (rx + 7, y + h - 34),
                  (rx, y + h - 12)], fill=(240, 140, 40))
    draw.polygon([(rx - 4, y + h - 34), (rx + 4, y + h - 34),
                  (rx, y + h - 20)], fill=(240, 200, 90))


# ---------------------------------------------------------------------------
# Stories: headlines and summaries, every fact verified from live wire
# reports on 25 November 2026.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "IRAN WAR",
    "headline": "MINES HIT TWO TANKERS IN HORMUZ AS WAR WIDENS",
    "summary": ("Iran's Guards said two tankers hit mines in the Strait "
                "of Hormuz as a Saudi-led coalition struck Yemen's "
                "Hodeidah port. Trump warned Tehran of a 'very traumatic' "
                "outcome if no nuclear deal is reached."),
}

GRID = [
    {
        "kicker": "MARKETS",
        "headline": "NVIDIA SLIDES 7% AS AI RALLY FADES",
        "summary": ("Nvidia fell 7% as lawmakers questioned Trump's "
                    "role in Huang's return. Nikkei -2.76%."),
        "art": art_chart,
    },
    {
        "kicker": "UKRAINE WAR",
        "headline": "UKRAINE HITS RUSSIAN WARSHIP OFF LIBYA",
        "summary": ("Ukraine hit a Russian warship off Libya; leaked "
                    "records put Russian war dead at 720,000."),
        "art": art_warship,
    },
    {
        "kicker": "CLIMATE",
        "headline": "OIL STATES KILLED COP31 — NOW WHAT?",
        "summary": ("After COP31 collapsed, Saudi Arabia and oil states "
                    "blocked any fossil-fuel phaseout mention."),
        "art": art_oil,
    },
    {
        "kicker": "COLOMBIA",
        "headline": "GUNMEN HOLD 20 HOSTAGE IN CARTAGENA SHOP",
        "summary": ("Armed men held about 20 people hostage in a "
                    "Cartagena supermarket; a car bomb injured 23."),
        "art": art_shop,
    },
]

BOTTOM = {
    "kicker": "SPACE",
    "headline": "PAKISTAN'S FIRST ASTRONAUT REACHES CHINA'S STATION",
    "summary": ("Zeeshan Ali became Pakistan's first astronaut aboard "
                "China's Shenzhou-24 spacecraft, reaching the Tiangong "
                "space station."),
}


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)

    # Masthead and dateline.
    mast = font(SERIF_B, 62)
    title = "THE WORLD TODAY"
    draw.text(((W - mast.getlength(title)) / 2, 24), title, font=mast, fill=INK)
    rule(draw, 28, 104, W - 28)
    date_font = font(SERIF_B, 26)
    dateline = "WEDNESDAY, 25 NOVEMBER 2026"
    draw.text(((W - date_font.getlength(dateline)) / 2, 114), dateline,
              font=date_font, fill=RED)
    rule(draw, 28, 150, W - 28)

    # Lead story: text left, illustration right.
    lead_y = 162
    paste_lead_art(draw, img, 620, lead_y, 376, 232)
    y = kicker_headline(draw, 28, lead_y, 572, LEAD["kicker"],
                        LEAD["headline"], font(SERIF_B, 33), 40,
                        font(SANS_B, 16))
    y += 6
    lines = fit_lines(LEAD["summary"], font(SANS, 18), 572, 4)
    draw_lines(draw, 28, y, lines, font(SANS, 18), INK, 25)

    # Two-by-two grid.
    rule(draw, 28, 406, W - 28)
    grid_y = 418
    cell_w, cell_h = 470, 178
    for i, story in enumerate(GRID):
        cx = 28 + (i % 2) * (cell_w + 28)
        cy = grid_y + (i // 2) * (cell_h + 12)
        story["art"](draw, cx, cy, cell_w, 56)
        draw.rectangle([cx, cy, cx + cell_w - 1, cy + 55], outline=INK, width=1)
        draw.text((cx, cy + 62), story["kicker"], font=font(SANS_B, 15), fill=RED)
        head_lines = fit_lines(story["headline"], font(SERIF_B, 21), cell_w, 2)
        draw_lines(draw, cx, cy + 84, head_lines, font(SERIF_B, 21), INK, 25)
        sum_lines = fit_lines(story["summary"], font(SANS, 16), cell_w, 2)
        draw_lines(draw, cx, cy + 136, sum_lines, font(SANS, 16), INK, 21)

    # Bottom strip: story six.
    rule(draw, 28, 812, W - 28)
    art_space(draw, 28, 826, 200, 130)
    draw.rectangle([28, 826, 227, 955], outline=INK, width=2)
    y = kicker_headline(draw, 248, 826, 748, BOTTOM["kicker"],
                        BOTTOM["headline"], font(SERIF_B, 24), 29,
                        font(SANS_B, 15))
    y += 4
    lines = fit_lines(BOTTOM["summary"], font(SANS, 17), 748, 2)
    draw_lines(draw, 248, y, lines, font(SANS, 17), INK, 23)

    # Footer.
    foot = font(SANS, 15)
    footer = "Compiled from wire reports  \u2022  25 November 2026"
    draw.text(((W - foot.getlength(footer)) / 2, 978), footer, font=foot, fill=GREY)
    return img


def main():
    img = build()
    img.save(OUT, format="PNG", optimize=True)
    size = os.path.getsize(OUT)
    digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"wrote {OUT} ({size} bytes, sha256 {digest})")
    if size > 1048576:
        raise SystemExit("entry.png is over the 1 MiB limit")


if __name__ == "__main__":
    main()
