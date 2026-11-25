#!/usr/bin/env python3
"""THE WORLD TODAY — front page for Wednesday 25 November 2026.

Draws a one-page newspaper (1024x1024 PNG) with Pillow and DejaVu fonts.
Everything is fixed: fixed copy, fixed geometry, no randomness, no clock,
no network — so two runs write byte-identical files.

Layout, top to bottom:
  * masthead + dateline
  * lead story: photo on the left, text on the right
  * a three-story row, then a two-story row, each with a small drawn motif
  * footer line

Run:  python3 generate.py        (writes entry.png next to this file)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants

PAGE = 1024
PAPER = (245, 239, 221)      # warm newsprint
INK = (20, 18, 16)           # near-black
RED = (164, 31, 31)          # kicker red
GREY = (110, 103, 90)        # footer grey
NAVY = (13, 24, 48)          # dark strip background
STEEL = (22, 50, 79)         # sea blue
CREAM = (251, 247, 234)      # light panel
SAND = (243, 234, 210)       # motif panel

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

# ---------------------------------------------------------------- fonts


def face(name, size):
    """Load one DejaVu face; fall back to the built-in bitmap font."""
    for candidate in (FONT_DIR / name, Path("/usr/share/fonts") / name):
        try:
            return ImageFont.truetype(str(candidate), size)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default(size)


def serif_bold(size):
    return face("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return face("DejaVuSerif.ttf", size)


def sans(size):
    return face("DejaVuSans.ttf", size)


def sans_bold(size):
    return face("DejaVuSans-Bold.ttf", size)


def sans_oblique(size):
    try:
        return ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Oblique.ttf"), size)
    except (OSError, ValueError):
        return sans(size)


# ---------------------------------------------------------------- text tools


def wrap(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=font) <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fitted(draw, text, font, width, max_lines, floor=11):
    """Wrap `text`; shrink the font until it fits `max_lines` lines.

    Returns (lines, font). Deterministic: pure function of the inputs.
    """
    size = font.size
    while size > floor:
        lines = wrap(draw, text, font, width)
        if len(lines) <= max_lines:
            return lines, font
        size -= 1
        font = ImageFont.truetype(font.path, size) if hasattr(font, "path") else font
        # Rebuild from the same family: truetype keeps .path; bitmap lacks it.
        if not hasattr(font, "path"):
            break
    return wrap(draw, text, font, width), font


def draw_lines(draw, x, y, lines, font, fill, leading):
    """Draw stacked lines; returns the y just below the last line."""
    top = y
    for line in lines:
        draw.text((x, top), line, font=font, fill=fill)
        top += leading
    return top


def rule(draw, x0, x1, y, weight=1, fill=INK):
    """Horizontal rule from x0 to x1 (inclusive)."""
    draw.line([(x0, y), (x1, y)], fill=fill, width=weight)


def cover_crop(img, target_w, target_h):
    """Centre-crop `img` to the target aspect, then resize to it."""
    src_w, src_h = img.size
    want = target_w / target_h
    have = src_w / src_h
    if have > want:  # too wide: trim the sides
        cut_w = int(src_h * want)
        left = (src_w - cut_w) // 2
        box = (left, 0, left + cut_w, src_h)
    else:  # too tall: trim top and bottom
        cut_h = int(src_w / want)
        top = (src_h - cut_h) // 2
        box = (0, top, src_w, top + cut_h)
    return img.crop(box).resize((target_w, target_h), Image.LANCZOS)

# ---------------------------------------------------------------- motifs

import math

# Each painter draws one small strip inside the box (x, y, w, h).
# All shapes are plain Pillow primitives with fixed coordinates, so the
# result is identical on every run.


def paint_chart(draw, x, y, w, h):
    """Falling market line with candlesticks."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=CREAM, outline=INK, width=1)
    deep = (120, 20, 20)
    pts = [
        (x + 14, y + 12),
        (x + w // 4, y + 18),
        (x + w // 2, y + 26),
        (x + 3 * w // 4, y + 34),
        (x + w - 16, y + h - 16),
    ]
    draw.line(pts, fill=RED, width=3, joint="curve")
    for i, px in enumerate((x + w // 5, x + 2 * w // 5, x + 3 * w // 5, x + 4 * w // 5)):
        top = y + 12 + i * 6
        draw.line([(px, top - 6), (px, top + 16)], fill=deep, width=1)
        draw.rectangle([px - 4, top, px + 4, top + 10], fill=deep)
    ex, ey = x + w - 16, y + h - 16
    draw.polygon([(ex, ey), (ex - 12, ey - 6), (ex - 12, ey + 6)], fill=RED)


def paint_ship(draw, x, y, w, h):
    """Warship on a dark sea, blast star on the horizon."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=STEEL, outline=INK, width=1)
    hull = (12, 12, 16)
    base = y + h - 16
    draw.polygon(
        [
            (x + 14, base - 14),
            (x + w - 60, base - 14),
            (x + w - 34, base),
            (x + 22, base),
        ],
        fill=hull,
    )
    draw.rectangle([x + w // 3, base - 26, x + w // 3 + 34, base - 14], fill=hull)
    draw.rectangle([x + w // 3 + 8, base - 34, x + w // 3 + 18, base - 26], fill=hull)
    draw.line([(x + w // 3 + 13, base - 34), (x + w // 3 + 13, base - 44)], fill=hull, width=2)
    star_cx, star_cy = x + w - 52, y + 18
    star = []
    for k in range(8):
        ang = k * math.pi / 4
        r = 13 if k % 2 == 0 else 5
        star.append((star_cx + r * math.cos(ang), star_cy + r * math.sin(ang)))
    draw.polygon(star, fill=(255, 190, 40))
    draw.ellipse([x + w - 30, y + 10, x + w - 14, y + 26], fill=(230, 110, 40))


def paint_derrick(draw, x, y, w, h):
    """Oil derrick, smoke puffs, low sun."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=SAND, outline=INK, width=1)
    brown = (96, 62, 36)
    apex = (x + w // 4, y + 8)
    foot_l = (x + 14, y + h - 8)
    foot_r = (x + w // 2, y + h - 8)
    draw.line([apex, foot_l], fill=brown, width=3)
    draw.line([apex, foot_r], fill=brown, width=3)
    for t in (0.35, 0.65):
        ax = apex[0] + (foot_l[0] - apex[0]) * t
        ay = apex[1] + (foot_l[1] - apex[1]) * t
        bx = apex[0] + (foot_r[0] - apex[0]) * t
        by = apex[1] + (foot_r[1] - apex[1]) * t
        draw.line([(ax, ay), (bx, by)], fill=brown, width=2)
    draw.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)], fill=brown, width=2)
    for cx, cy, r in (
        (x + w // 2 + 16, y + 12, 9),
        (x + w // 2 + 32, y + 18, 11),
        (x + w // 2 + 48, y + 12, 8),
    ):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 148, 142))
    draw.ellipse([x + w - 44, y + 8, x + w - 16, y + 36], fill=(235, 140, 40))
    draw.rectangle([x + w - 66, y + h - 26, x + w - 46, y + h - 8], fill=(140, 30, 30))


def paint_shop(draw, x, y, w, h):
    """Corner shop at night under police lights."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY, outline=INK, width=1)
    # Shopfront on the left half: tall striped awning, cream wall,
    # dark door on the left, wide lit window on the right.
    shop_x0 = x + 14
    shop_w = int(w * 0.52)
    aw_top, aw_bot = y + 6, y + 22
    stripe = 14
    sx = shop_x0
    on = True
    while sx < shop_x0 + shop_w:
        fill = RED if on else CREAM
        draw.rectangle([sx, aw_top, min(sx + stripe, shop_x0 + shop_w) - 1, aw_bot], fill=fill)
        sx += stripe
        on = not on
    draw.rectangle([shop_x0, aw_top, shop_x0 + shop_w, aw_bot], outline=INK, width=1)
    draw.rectangle([shop_x0, aw_bot, shop_x0 + shop_w, y + h - 4], fill=CREAM, outline=INK, width=1)
    door_w = shop_w // 3
    draw.rectangle(
        [shop_x0 + 6, y + 30, shop_x0 + 6 + door_w, y + h - 4],
        fill=(38, 44, 66),
        outline=INK,
        width=1,
    )
    win_x0 = shop_x0 + 6 + door_w + 6
    win_x1 = shop_x0 + shop_w - 6
    draw.rectangle([win_x0, y + 30, win_x1, y + h - 12], fill=(70, 90, 130), outline=INK, width=1)
    draw.line([(win_x0, y + 38), (win_x1, y + 38)], fill=CREAM, width=2)
    # Police beacons on the right: red and blue lights with halos.
    cy = y + h // 2
    for cx, core, halo in (
        (x + w - 108, (220, 60, 60), (120, 40, 40)),
        (x + w - 68, (80, 140, 255), (40, 70, 150)),
    ):
        draw.ellipse([cx - 16, cy - 12, cx + 16, cy + 12], fill=halo)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=core)


def paint_rocket(draw, x, y, w, h):
    """Rocket climbing past Earth and stars."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY, outline=INK, width=1)
    for fx, fy, fr in (
        (0.08, 0.20, 2), (0.20, 0.70, 2), (0.32, 0.15, 1),
        (0.55, 0.80, 2), (0.68, 0.25, 1), (0.85, 0.60, 2),
        (0.92, 0.20, 1), (0.45, 0.45, 1),
    ):
        cx, cy = x + int(w * fx), y + int(h * fy)
        draw.ellipse([cx - fr, cy - fr, cx + fr, cy + fr], fill=(255, 255, 255))
    ex, ey, er = x + w - 40, y + 22, 15
    draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(52, 110, 190))
    draw.ellipse([ex - 4, ey - 8, ex + 8, ey + 2], fill=(80, 170, 90))
    rx = x + w // 2
    body_top = y + 10
    body_bot = y + h - 22
    draw.polygon([(rx - 8, body_top + 12), (rx, body_top), (rx + 8, body_top + 12)], fill=RED)
    draw.rectangle([rx - 8, body_top + 12, rx + 8, body_bot], fill=(245, 245, 245))
    draw.polygon([(rx - 8, body_bot), (rx - 16, body_bot + 8), (rx - 8, body_bot + 4)], fill=RED)
    draw.polygon([(rx + 8, body_bot), (rx + 16, body_bot + 8), (rx + 8, body_bot + 4)], fill=RED)
    draw.polygon([(rx - 5, body_bot), (rx + 5, body_bot), (rx, body_bot + 16)], fill=(235, 140, 40))
    draw.polygon([(rx - 2, body_bot), (rx + 2, body_bot), (rx, body_bot + 9)], fill=(255, 210, 80))

# ---------------------------------------------------------------- content

LEAD = {
    "kicker": "IRAN WAR",
    "headline": "MINES HIT TWO TANKERS IN HORMUZ AS WAR WIDENS",
    "summary": (
        "Two tankers hit mines in the Strait of Hormuz, Iran's Guards said, "
        "as a Saudi-led coalition struck Yemen's Hodeidah port. Trump warned "
        "Tehran of a 'very traumatic' outcome if no nuclear deal is reached."
    ),
    "caption": "Smoke over the Strait of Hormuz as tankers sail on.",
}

ROW_THREE = [
    {
        "kicker": "MARKETS",
        "headline": "NVIDIA SLIDES 7% AS AI RALLY FADES",
        "summary": (
            "Nvidia fell 7% as lawmakers questioned Trump's role in Huang's "
            "return. Nikkei -2.76%."
        ),
        "motif": paint_chart,
    },
    {
        "kicker": "UKRAINE WAR",
        "headline": "UKRAINE HITS RUSSIAN WARSHIP OFF LIBYA",
        "summary": (
            "Ukraine hit a Russian warship off Libya; leaked records put "
            "Russian war dead at 720,000."
        ),
        "motif": paint_ship,
    },
    {
        "kicker": "CLIMATE",
        "headline": "OIL STATES KILLED COP31 — NOW WHAT?",
        "summary": (
            "After COP31 collapsed, Saudi Arabia and oil states blocked any "
            "fossil-fuel phaseout mention."
        ),
        "motif": paint_derrick,
    },
]

ROW_TWO = [
    {
        "kicker": "COLOMBIA",
        "headline": "GUNMEN HOLD 20 HOSTAGE IN CARTAGENA SHOP",
        "summary": (
            "Armed men held about 20 people hostage in a Cartagena "
            "supermarket; a car bomb injured 23."
        ),
        "motif": paint_shop,
    },
    {
        "kicker": "SPACE",
        "headline": "PAKISTAN'S FIRST ASTRONAUT REACHES CHINA'S STATION",
        "summary": (
            "Zeeshan Ali became Pakistan's first astronaut aboard China's "
            "Shenzhou-24 spacecraft, reaching the Tiangong space station."
        ),
        "motif": paint_rocket,
    },
]

FOOTER = "Compiled from wire reports • 25 November 2026"


# ---------------------------------------------------------------- assembly


def centred(draw, y, text, font, fill):
    """Draw `text` centred on the page at height y."""
    width = draw.textlength(text, font=font)
    draw.text(((PAGE - width) / 2, y), text, font=font, fill=fill)


def draw_masthead(draw):
    draw.rectangle([10, 10, PAGE - 11, PAGE - 11], outline=INK, width=3)
    draw.rectangle([18, 18, PAGE - 19, PAGE - 19], outline=INK, width=1)
    centred(draw, 32, "THE WORLD TODAY", serif_bold(58), INK)
    rule(draw, 26, PAGE - 27, 102, weight=2)
    rule(draw, 26, PAGE - 27, 106, weight=1)
    centred(draw, 114, "WEDNESDAY, 25 NOVEMBER 2026", serif_bold(21), RED)
    rule(draw, 26, PAGE - 27, 146, weight=1)


def draw_lead(page, draw, photo):
    # Photo on the left, caption bar across its foot.
    art = cover_crop(photo, 526, 304)
    page.paste(art, (34, 158))
    draw.rectangle([34, 158, 559, 461], outline=INK, width=1)
    draw.rectangle([34, 432, 559, 461], fill=NAVY)
    caption = sans_oblique(13)
    cw = draw.textlength(LEAD["caption"], font=caption)
    draw.text((34 + (526 - cw) / 2, 440), LEAD["caption"], font=caption, fill=(245, 245, 245))
    # Text on the right.
    tx, tw = 584, 406
    draw.text((tx, 160), LEAD["kicker"], font=sans_bold(16), fill=RED)
    lines, font = fitted(draw, LEAD["headline"], serif_bold(36), tw, 3)
    below = draw_lines(draw, tx, 188, lines, font, INK, 44)
    slines, sfont = fitted(draw, LEAD["summary"], sans(17), tw, 5)
    draw_lines(draw, tx, below + 12, slines, sfont, INK, 24)


def draw_cell(draw, x, y, width, story, head_size, body_size, body_lines):
    """One grid story: motif strip, kicker, headline, summary."""
    story["motif"](draw, x, y, width, 58)
    draw.text((x, y + 66), story["kicker"], font=sans_bold(14), fill=RED)
    lines, font = fitted(draw, story["headline"], serif_bold(head_size), width, 2)
    draw_lines(draw, x, y + 90, lines, font, INK, head_size + 5)
    slines, sfont = fitted(draw, story["summary"], sans(body_size), width, body_lines)
    draw_lines(draw, x, y + 148, slines, sfont, INK, body_size + 5)


def build_page(photo):
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)
    draw_masthead(draw)
    draw_lead(page, draw, photo)
    rule(draw, 26, PAGE - 27, 478, weight=2)
    for i, story in enumerate(ROW_THREE):
        draw_cell(draw, 34 + i * 322, 494, 310, story, 20, 14, 3)
    for i, story in enumerate(ROW_TWO):
        draw_cell(draw, 34 + i * 484, 732, 472, story, 21, 15, 3)
    rule(draw, 26, PAGE - 27, 970, weight=1)
    centred(draw, 978, FOOTER, sans(13), GREY)
    return page


def main():
    here = Path(__file__).resolve().parent
    photo = Image.open(here / "lead-art.png").convert("RGB")
    page = build_page(photo)
    out = here / "entry.png"
    page.save(out, format="PNG")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
