#!/usr/bin/env python3
"""THE WORLD -- front page summing up Monday 23 November 2026.

Deterministic, stdlib-only Python 3.13. Draws a 1024x1024 newspaper front
page and writes entry.png (PNG encoded by hand with zlib + struct; the
letterforms come from a small 5x7 bitmap font defined below, so no font
files, no network and no external assets are needed). Running the program
twice writes byte-identical output.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024
PAPER = (247, 242, 231)
INK = (22, 22, 22)
RED = (176, 32, 32)
GREY = (96, 90, 78)
LIGHT = (214, 205, 188)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, uppercase only. Every glyph is 7 rows of 5 bits.
# Text is normalised to uppercase before drawing.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

# Middle dot used as the bullet in the ALSO TODAY strip.
FONT["\u00b7"] = ("00000", "00000", "00000", "01100", "01100", "00000", "00000")

_NORMALISE = {
    "\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"', "\u00f6": "O", "\u00d6": "O",
    "\u2022": "\u00b7", "\u00e9": "E", "\u00e8": "E",
}


def normalise(text):
    out = []
    for ch in text.upper():
        out.append(_NORMALISE.get(ch, ch))
    return "".join(out)


def text_width(text, scale):
    """Width in pixels of text drawn at the given scale."""
    return len(normalise(text)) * 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    text = normalise(text)
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word is hard-split by characters.
            while text_width(word, scale) > max_width:
                cut = max_width // (6 * scale)
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        for i in range(w * h):
            self.pix[3 * i] = bg[0]
            self.pix[3 * i + 1] = bg[1]
            self.pix[3 * i + 2] = bg[2]

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i] = color[0]
            self.pix[i + 1] = color[1]
            self.pix[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pix[i] = color[0]
                self.pix[i + 1] = color[1]
                self.pix[i + 2] = color[2]

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, color, thick=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], color, thick)

    def circle(self, cx, cy, r, color, thick=1):
        steps = max(48, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = int(round(cx + r * math.cos(a)))
            y = int(round(cy + r * math.sin(a)))
            self.fill_rect(x, y, thick, thick, color)

    def ellipse(self, cx, cy, rx, ry, color, thick=1):
        steps = max(48, int(2 * math.pi * max(rx, ry)))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            self.fill_rect(x, y, thick, thick, color)

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.fill_rect(cx - half, yy, 2 * half + 1, 1, color)

    def fill_poly(self, pts, color):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, color)

    # -- text -------------------------------------------------------------
    def draw_glyph(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            return
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    self.fill_rect(
                        x + col_i * scale, y + row_i * scale, scale, scale, color
                    )

    def draw_text(self, x, y, text, scale, color):
        text = normalise(text)
        cx = x
        for ch in text:
            self.draw_glyph(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx - x

    def draw_text_centred(self, cx, y, text, scale, color):
        w = text_width(text, scale)
        return self.draw_text(cx - w // 2, y, text, scale, color)

    def draw_block(self, x, y, text, scale, max_width, color):
        """Draw wrapped text; returns the y just below the last line."""
        lh = 8 * scale
        for line in wrap_text(text, scale, max_width):
            self.draw_text(x, y, line, scale, color)
            y += lh
        return y


# -------------------------------------------------------- illustrations ---
def draw_globe(cv, cx, cy, r, color, crack=False):
    """Small line globe: outline, meridians, equator, land blobs."""
    cv.circle(cx, cy, r, color, 2)
    cv.ellipse(cx, cy, int(r * 0.45), r, color, 1)
    cv.ellipse(cx, cy, r, int(r * 0.45), color, 1)
    cv.hline(cx - r, cy, 2 * r, color, 1)
    # Land blobs, kept well inside the circle.
    blobs = [
        (cx - int(r * 0.45), cy - int(r * 0.35), int(r * 0.28)),
        (cx + int(r * 0.35), cy - int(r * 0.15), int(r * 0.24)),
        (cx - int(r * 0.10), cy + int(r * 0.42), int(r * 0.22)),
        (cx + int(r * 0.55), cy + int(r * 0.45), int(r * 0.16)),
    ]
    for bx, by, br in blobs:
        cv.fill_circle(bx, by, br, color)
    if crack:
        pts = [
            (cx - int(r * 0.2), cy - r),
            (cx + int(r * 0.15), cy - int(r * 0.55)),
            (cx - int(r * 0.25), cy - int(r * 0.1)),
            (cx + int(r * 0.2), cy + int(r * 0.35)),
            (cx - int(r * 0.05), cy + int(r * 0.8)),
            (cx + int(r * 0.3), cy + r),
        ]
        cv.polyline(pts, RED, 3)
        # Fallen fragments.
        cv.fill_poly(
            [(cx + r + 6, cy - 8), (cx + r + 20, cy - 2), (cx + r + 8, cy + 10)],
            RED,
        )
        cv.fill_poly(
            [(cx - r - 22, cy + 14), (cx - r - 8, cy + 10), (cx - r - 12, cy + 26)],
            RED,
        )


def draw_summit(cv, x, y, w, h):
    """Three flags over a summit table."""
    # Table.
    cv.ellipse(x + w // 2, y + h - 12, w // 2 - 4, 10, INK, 2)
    cv.hline(x + 8, y + h - 12, w - 16, INK, 2)
    # Three seated figures: heads above the table.
    heads = [x + w // 4, x + w // 2, x + 3 * w // 4]
    for hx in heads:
        cv.fill_circle(hx, y + h - 34, 9, INK)
        cv.fill_rect(hx - 12, y + h - 24, 24, 12, INK)
    # Three flag poles with small flags behind the figures.
    for i, fx in enumerate([x + 14, x + w // 2 - 4, x + w - 22]):
        cv.vline(fx, y + 2, h - 40, INK, 2)
        flag = RED if i == 1 else INK
        cv.fill_rect(fx + 2, y + 2, 18, 12, flag)
        cv.fill_rect(fx + 2, y + 2, 18, 3, PAPER)


def draw_ship(cv, x, y, w, h):
    """A warship going down: tilted hull, waves, a drone above."""
    # Drone.
    dx, dy = x + w - 34, y + 8
    cv.fill_circle(dx, dy, 4, INK)
    cv.hline(dx - 10, dy - 7, 20, INK, 2)
    cv.hline(dx - 10, dy + 7, 20, INK, 2)
    cv.line(dx - 4, dy + 4, x + w // 2 + 20, y + 26, GREY, 1)
    # Hull, tilted as it sinks bow-first.
    hull = [
        (x + 10, y + 18),
        (x + w - 34, y + 12),
        (x + w - 16, y + 22),
        (x + w - 30, y + 34),
        (x + 26, y + 38),
    ]
    cv.fill_poly(hull, INK)
    # Funnel leaning with the hull.
    cv.line(x + w // 2, y + 14, x + w // 2 + 6, y + 2, INK, 3)
    # Waves.
    for wy in (y + h - 14, y + h - 5):
        pts = []
        for i in range(0, w + 1, 8):
            pts.append((x + i, wy + (5 if (i // 8) % 2 else -3)))
        cv.polyline(pts, INK, 2)


def draw_tanker(cv, x, y, w, h):
    """Oil tanker under a red warning triangle."""
    # Tanker silhouette.
    cv.fill_rect(x + 8, y + h - 34, w - 60, 18, INK)
    cv.fill_rect(x + w - 62, y + h - 56, 16, 24, INK)
    cv.fill_rect(x + 16, y + h - 46, w - 90, 10, PAPER)
    # Waves.
    for wy in (y + h - 10, y + h - 3):
        pts = []
        for i in range(0, w - 40, 8):
            pts.append((x + i, wy + (4 if (i // 8) % 2 else -3)))
        cv.polyline(pts, INK, 2)
    # Warning triangle, red, with an exclamation mark.
    tx, ty = x + w - 44, y + 2
    cv.fill_poly(
        [(tx, ty + 34), (tx + 18, ty), (tx + 36, ty + 34)], RED
    )
    cv.fill_poly(
        [(tx + 6, ty + 28), (tx + 18, ty + 8), (tx + 30, ty + 28)], PAPER
    )
    cv.draw_text(tx + 13, ty + 10, "!", 1, RED)


def draw_chart(cv, x, y, w, h):
    """Market line: a plunge, then a recovery."""
    # Axes.
    cv.vline(x + 6, y + 2, h - 8, INK, 2)
    cv.hline(x + 6, y + h - 6, w - 10, INK, 2)
    pts = [
        (x + 10, y + 10),
        (x + w // 4, y + 14),
        (x + w // 3, y + h - 8),
        (x + w // 2, y + h - 12),
        (x + 2 * w // 3, y + h - 20),
        (x + 3 * w // 4, y + 12),
        (x + w - 8, y + 8),
    ]
    cv.polyline(pts, RED, 3)


def draw_spiral(cv, x, y, w, h):
    """Prime-number spiral: dots winding out, primes in red."""
    cx, cy = x + w // 2, y + h // 2
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}
    for n in range(1, 130, 2):
        a = 0.30 * n
        r = 0.62 * math.sqrt(n) * (min(w, h) / 16.0)
        px = int(cx + r * math.cos(a))
        py = int(cy + r * math.sin(a))
        col = RED if n in primes else INK
        cv.fill_rect(px, py, 2, 2, col)


# -------------------------------------------------------------- the page ---
M = 36  # page margin
CW = W - 2 * M  # content width


def rule(cv, y, color=INK, thick=1):
    cv.hline(M, y, CW, color, thick)


def divider(cv, y):
    cv.hline(M, y, CW, INK, 1)


def story_column(cv, x, y, w, kicker, headline, deck, illo, illo_h=58):
    """One column story: kicker, headline, deck, illustration. Returns
    the y just below the illustration."""
    cv.draw_text(x, y, kicker, 2, RED)
    y += 22
    y = cv.draw_block(x, y, headline, 4, w, INK)
    y += 6
    y = cv.draw_block(x, y, deck, 2, w, INK)
    y += 8
    illo(cv, x, y, w, illo_h)
    return y + illo_h


def build_png():
    cv = Canvas(W, H, PAPER)

    # ---- top line ------------------------------------------------------
    cv.draw_text(M, 24, "EST. MMXXVI", 2, GREY)
    right = "MONDAY EDITION"
    cv.draw_text(W - M - text_width(right, 2), 24, right, 2, GREY)
    rule(cv, 44)

    # ---- masthead ------------------------------------------------------
    cv.draw_text_centred(W // 2 - 30, 54, "THE WORLD", 14, INK)
    draw_globe(cv, 950, 102, 32, INK)
    cv.draw_text_centred(W // 2, 160, "MONDAY, 23 NOVEMBER 2026", 3, INK)
    cv.hline(M, 190, CW, RED, 4)
    cv.hline(M, 198, CW, INK, 2)

    # ---- lead story: COP31 collapses ----------------------------------
    cv.draw_text(M, 206, "CLIMATE - COP31 - ANTALYA", 2, RED)
    y = 226
    y = cv.draw_block(M, y, "COP31 COLLAPSES", 6, 700, INK)
    y = cv.draw_block(M, y, "NO DEAL ON CLIMATE", 6, 700, INK)
    lead_deck = (
        "AFTER A RECORD TWO WEEKS IN ANTALYA, THE UN CLIMATE TALKS END "
        "WITH NO AGREEMENT - THE FIRST COLLAPSE SINCE COPENHAGEN 2009. "
        "THE EU REJECTED THE 'ANTALYA PACT'; 194 NATIONS LEAVE WITH "
        "NOTHING."
    )
    cv.draw_block(M, 328, lead_deck, 2, 620, INK)
    # Cracked-earth globe beside the lead story.
    draw_globe(cv, 830, 300, 88, INK, crack=True)

    divider(cv, 402)

    # ---- second row: three columns ------------------------------------
    col_w = (CW - 2 * 16) // 3
    x2 = M + col_w + 16
    x3 = x2 + col_w + 16
    y = 414
    story_column(
        cv, M, y, col_w,
        "DIPLOMACY - SHENZHEN",
        "A THREE-WAY SUMMIT IN SHENZHEN",
        "TRUMP, XI AND PUTIN ISSUE A 'DECLARATION TOWARD PEACE'. PUTIN "
        "IS SEEN AS THE BIGGEST WINNER.",
        draw_summit,
    )
    story_column(
        cv, x2, y, col_w,
        "WAR AT SEA - LIBYA",
        "SEA DRONES SINK RUSSIAN WARSHIP",
        "THE FRIGATE MERKURY GOES DOWN IN BENGHAZI AFTER A SUSPECTED "
        "UKRAINIAN NAVAL DRONE STRIKE.",
        draw_ship,
    )
    story_column(
        cv, x3, y, col_w,
        "THE GULF - ON THE BRINK",
        "TRUMP THREATENS TO SINK IRANIAN VESSELS",
        "US STRIKES AN OIL TANKER; TRUMP WARNS IRAN; HOUTHIS HIT A "
        "SAUDI REFINERY.",
        draw_tanker,
    )
    # Column rules.
    cv.vline(M + col_w + 8, 414, 270, LIGHT, 1)
    cv.vline(x2 + col_w + 8, 414, 270, LIGHT, 1)

    divider(cv, 694)

    # ---- third row: two columns ---------------------------------------
    col2_w = (CW - 24) // 2
    x5 = M + col2_w + 24
    story_column(
        cv, M, 706, col2_w,
        "MARKETS - AI SELLOFF",
        "AI SELLOFF SHAKES ASIAN MARKETS",
        "KOSPI PLUNGES 5%, TAIWAN SWINGS 1,578 POINTS IN A DAY, THEN "
        "NASDAQ FUTURES REBOUND NEARLY 3% - AS NVIDIA'S BOARD REJECTS "
        "JENSEN HUANG'S RETURN.",
        draw_chart,
        36,
    )
    story_column(
        cv, x5, 706, col2_w,
        "SCIENCE - PRIMES",
        "AI CLAIMS PROOF OF RIEMANN HYPOTHESIS",
        "ANTHROPIC MATHEMATICIAN LEVENT ALPOGE AND CLAUDE SAY THEY HAVE "
        "PROVED THE 167-YEAR-OLD PRIME-NUMBER PROBLEM IN 17 MILLION "
        "LINES OF LEAN CODE.",
        draw_spiral,
        36,
    )
    cv.vline(M + col2_w + 12, 706, 198, LIGHT, 1)

    divider(cv, 914)

    # ---- also today ----------------------------------------------------
    y = 924
    cv.draw_text(M, y, "ALSO TODAY", 2, RED)
    y += 18
    items = [
        "SOUTH KOREA'S EXPORTS TOP $1 TRILLION FOR THE FIRST TIME",
        "DEMOCRATS CLINCH A HISTORIC HOUSE MAJORITY - 258 SEATS",
        "ICE DETAINS FATHER AND DAUGHTER AT SEATTLE AIRPORT",
        "METS SIGN TARIK SKUBAL FOR A RECORD $450 MILLION",
        "LIVERPOOL ROUT UNITED IN POCHETTINO'S DEBUT",
    ]
    for item in items:
        cv.draw_text(M, y, "\u00b7 " + item, 2, INK)
        y += 15

    return encode_png(cv)


def encode_png(cv):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += cv.pix[yy * W * 3:(yy + 1) * W * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )


def main():
    data = build_png()
    here = os.path.dirname(os.path.abspath(__file__))
    env_out = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if env_out and os.path.isdir(env_out):
        out_dir = env_out
    elif os.path.isdir("/output"):
        out_dir = "/output"
    else:
        out_dir = here
    primary = os.path.join(out_dir, "entry.png")
    with open(primary, "wb") as fh:
        fh.write(data)
    written = [primary]
    local = os.path.join(here, "entry.png")
    if local != primary:
        try:
            with open(local, "wb") as fh:
                fh.write(data)
            written.append(local)
        except OSError:
            pass  # the grader mounts the repo read-only; /output holds the graded copy
    print("wrote %d bytes to %s" % (len(data), ", ".join(written)))


if __name__ == "__main__":
    sys.exit(main())
