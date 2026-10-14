"""Risograph-style posters: three spot inks that overprint, halftone dots, misregistration.

Each ink is its own layer, multiplied onto the paper and nudged a few pixels off
register, with a mottled-ink texture, so it reads like a real riso print.
"""
import base64
import math
import re
from functools import lru_cache
from xml.sax.saxutils import escape

import segno
from fontTools.ttLib import TTFont

from paper import FONTS, ROOT

PAPER = "#F4EFE4"
INKS = {"yellow": "#FFE800", "pink": "#FF48B0", "blue": "#0078BF"}
ANGLE = {"yellow": 0, "pink": 75, "blue": 15}
OFFSET = {"yellow": (0, 0), "pink": (5, -3), "blue": (-3, 4)}

DISPLAY = "Anton, Impact, 'Arial Narrow Bold', sans-serif"
MONO = "'Space Mono', 'Courier New', monospace"
CJK = "Anton, 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', 'WenQuanYi Zen Hei', sans-serif"
CAP = 1760 / 2048  # Anton cap height, in em


@lru_cache(None)
def _font(name):
    f = TTFont(FONTS / name)
    return f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm


def width(s, size, name="anton-latin-400-normal.woff2"):
    cmap, hmtx, upm = _font(name)
    return sum(hmtx[cmap.get(ord(c), cmap[32])][0] for c in s) * size / upm


def fit(s, w):
    """Anton size at which `s` is exactly `w` wide."""
    return w / width(s, 1)


def font_css():
    out = []
    for fam, f, wt in [("Anton", "anton-latin-400-normal.woff2", 400),
                       ("Space Mono", "space-mono-latin-400-normal.woff2", 400),
                       ("Space Mono", "space-mono-latin-700-normal.woff2", 700)]:
        b64 = base64.b64encode((FONTS / f).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "\n".join(out)


def halftones():
    out = []
    for ink, col in INKS.items():
        for pct in (15, 30, 50, 70):
            cell = 12
            r = cell * math.sqrt(pct / 100 / math.pi)
            out.append(f'<pattern id="ht-{ink}-{pct}" width="{cell}" height="{cell}" patternUnits="userSpaceOnUse" '
                       f'patternTransform="rotate({ANGLE[ink]})"><circle cx="{cell / 2}" cy="{cell / 2}" r="{r:.2f}" fill="{col}"/></pattern>')
    return "\n".join(out)


class Print:
    """Collects artwork per ink, then composites the inks like a riso pass."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.layers = {k: [] for k in INKS}
        self.n = 0

    def __call__(self, ink, *parts):
        self.layers[ink].extend(parts)

    def uid(self, p="m"):
        self.n += 1
        return f"{p}{self.n}"

    def svg(self, title):
        w, h = self.w, self.h
        defs = f'''<defs><style>{font_css()}</style>{halftones()}
<filter id="ink" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="11" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 2.2" result="m"/>
  <feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="2" seed="3" result="w"/>
  <feDisplacementMap in="SourceGraphic" in2="w" scale="3" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feComposite in="d" in2="m" operator="in"/>
</filter>
<filter id="paperg" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="5" stitchTiles="stitch"/>
  <feColorMatrix type="matrix" values="0 0 0 0 .35  0 0 0 0 .3  0 0 0 0 .22  0 0 0 -1.5 .82"/>
</filter></defs>'''
        body = [f'<rect width="{w}" height="{h}" fill="{PAPER}"/>']
        for ink in ("yellow", "pink", "blue"):
            dx, dy = OFFSET[ink]
            body.append(f'<g style="mix-blend-mode:multiply;color:{INKS[ink]}" fill="{INKS[ink]}" filter="url(#ink)" '
                        f'transform="translate({dx} {dy})">{"".join(self.layers[ink])}</g>')
        body.append(f'<rect width="{w}" height="{h}" filter="url(#paperg)" style="mix-blend-mode:multiply" opacity=".55"/>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                f'aria-label="{escape(title)}"><title>{escape(title)}</title>{defs}{"".join(body)}</svg>\n')


# ---------------------------------------------------------------- drawing helpers (inside a layer)

def T(x, y, s, size, font=DISPLAY, anchor="start", ls=0, fill="currentColor", weight=400, fitw=None, extra=""):
    fl = f' textLength="{fitw:.1f}" lengthAdjust="spacingAndGlyphs"' if fitw else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size:.1f}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}"{fl} {extra}>{escape(s)}</text>')


def fitline(x, y, s, w, fill="currentColor"):
    """Anton line set to exactly width w; returns (svg, cap height)."""
    size = fit(s, w)
    return T(x, y, s, size, fill=fill, fitw=w), size * CAP


def M(x, y, rows, size, lh, bold=False, fill="currentColor", anchor="start"):
    return "".join(T(x, y + i * lh, r, size, MONO, anchor, 0, fill, 700 if bold else 400) for i, r in enumerate(rows))


def burst(cx, cy, r1, r2, n=18, rot=0, fill="currentColor"):
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n + math.radians(rot)
        r = r1 if i % 2 == 0 else r2
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def pixels(x, y, p, rows, ch="X", fill="currentColor"):
    d = "".join(f"M{x + c * p} {y + r * p}h{p}v{p}h-{p}Z" for r, row in enumerate(rows) for c, k in enumerate(row) if k == ch)
    return f'<path d="{d}" fill="{fill}"/>'


def qr(url, x, y, size):
    q = segno.make(url, error="m")
    n = q.symbol_size(scale=1, border=0)[0]
    d = re.search(r' d="([^"]+)"', q.svg_inline(scale=1, border=0)).group(1)
    return f'<path transform="translate({x} {y}) scale({size / n:.4f})" stroke="currentColor" fill="none" d="{d}"/>'


def rule(x1, y, x2, w=4, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="currentColor" stroke-width="{w}"{da}/>'


def strip(pr, y=100):
    """Masthead line across the top."""
    pr("blue", T(90, y, "CS EQUITY AI", 28, MONO, weight=700),
       T(900, y, "501(c)(3) PUBLIC CHARITY · EST. 2021", 24, MONO, "middle"),
       T(1710, y, "CSEQUITYAI.ORG", 28, MONO, "end", weight=700),
       rule(90, y + 22, 1710, 5))


def cta_band(pr, y, text, url, qr_label):
    """Solid blue band with knocked-out type, QR code beside it."""
    pr("blue", f'<rect x="90" y="{y}" width="1330" height="150"/>')
    size = fit(text, 1250)
    pr("blue", T(130, y + 75 + size * CAP / 2, text, size, fill="#FFFFFF", fitw=1250))
    pr("pink", f'<rect x="1452" y="{y - 118}" width="256" height="266" fill="none" stroke="currentColor" stroke-width="10"/>')
    pr("blue", qr(url, 1470, y - 105, 220), T(1580, y + 140, qr_label, 20, MONO, "middle", weight=700))


def footer(pr):
    pr("blue", T(900, 2365, "CS Equity AI is a 501(c)(3) public charity · EIN 99-3463829 · info@csequityai.org",
                 21, MONO, "middle"))


# ---------------------------------------------------------------- posters

SITE = "https://csequityai.org"
VIBE = "https://csequityai.org/events/vibe-coding-happy-hour.html"


def poster_main():
    pr = Print(1800, 2400)
    strip(pr)
    # sun + halftone glow behind the headline
    pr("yellow", '<circle cx="1330" cy="640" r="470"/>')
    pr("pink", '<circle cx="1420" cy="760" r="400" fill="url(#ht-pink-30)"/>')
    y = 180
    for s, ink, shadow in (("WE TEACH STUDENTS TO", "blue", False), ("BUILD WITH AI,", "pink", True),
                           ("NOT JUST USE IT.", "blue", False)):
        _, cap = fitline(90, 0, s, 1620)
        y += cap
        if shadow:
            pr("yellow", fitline(102, y + 12, s, 1620)[0])
        pr(ink, fitline(90, y, s, 1620)[0])
        y += 34
    # FREE sticker
    pr("pink", burst(1510, 1045, 165, 140, 22, 7))
    pr("blue", f'<g transform="rotate(-10 1510 1045)">{T(1510, 1062, "FREE", 112, anchor="middle")}'
               f'{T(1510, 1104, "$0 TUITION, EVER", 21, MONO, "middle", weight=700)}</g>')
    pr("blue", M(90, 985, ["Live online courses taught by engineers",
                           "from Google and academia, for students in",
                           "the US, Taiwan and Hong Kong.",
                           "No tuition, no gatekeeping. Just a browser",
                           "and curiosity."], 31, 42))
    # the path
    pr("blue", rule(90, 1205, 1710, 5), T(90, 1250, "THE PATH  ·  EACH LEVEL ENDS WITH SOMETHING REAL", 24, MONO, weight=700))
    cols = [("1", "LEVEL 1 · CAPABILITY", "FOUNDATION COURSE", ["Self-paced, in the", "browser."], "→ CERTIFICATE"),
            ("2", "LEVEL 2 · CREATION", "BOOTCAMP", ["Weekly live sessions,", "small teams."], "→ A WORKING AI SYSTEM"),
            ("3", "LEVEL 3 · CAPITAL", "STARTUP", ["Founding team of", "three to five."], "→ PITCH TO ANGEL INVESTORS")]
    for i, (num, lab, title, desc, out) in enumerate(cols):
        x = 90 + i * 555
        pr("yellow", T(x, 1550, num, 290))
        pr("pink", T(x + 12, 1562, num, 290, fill="url(#ht-pink-50)"))
        tx = x + 185
        pr("blue", T(tx, 1340, lab, 20, MONO, weight=700),
           T(tx, 1410, title, min(60, fit(title, 345))),
           M(tx, 1455, desc, 23, 31))
        pr("pink", T(tx, 1548, out, 19, MONO, weight=700))
    # what we've run, gig-poster lineup
    pr("blue", rule(90, 1630, 1710, 5), T(90, 1675, "WHAT WE’VE RUN, ALL FREE", 24, MONO, weight=700),
       T(1000, 1675, "PAST COLLABORATORS", 24, MONO, weight=700))
    lineup = [("2021", "ANDROID ON THE CLOUD"), ("2023", "A BEGINNER’S GUIDE TO AI"), ("2024", "GEN AI BOOTCAMP"),
              ("2024–25", "AI TUTOR FOR [X]"), ("2026", "VIBE CODING HAPPY HOUR"), ("NOW", "MLE-STAR BOOTCAMP"),
              ("FALL 2026", "THE NEXT COURSE")]
    for i, (yr, name) in enumerate(lineup):
        yy = 1740 + i * 56
        pr("pink", T(90, yy, yr, 24, MONO, weight=700))
        pr("blue", T(250, yy + 2, name, 46))
    pr("blue", M(1000, 1740, ["Taiwan NEXT Foundation", "The Hong Kong Polytechnic", "  University",
                              "National Yang Ming Chiao", "  Tung University", "VC.in.Taiwan", "CSEB"], 23, 38))
    cta_band(pr, 2160, "START THE FREE FOUNDATION COURSE → CSEQUITYAI.ORG", SITE, "SCAN TO START")
    footer(pr)
    return pr.svg("CS Equity AI poster: we teach students to build with AI, not just use it. Free.")


CAT = ["X...X...", "XXXXX...", "XOXOX...", "XXXXX...", ".XXXXXXX", ".XXXXXX.", ".X.X.X.X"]
CACTUS = ["..X..", "..X.X", "X.X.X", "X.XXX", "XXX..", "..X..", "..X..", "..X.."]


def poster_vibe():
    pr = Print(1800, 2400)
    strip(pr)
    y = 180
    for s, ink in (("VIBE CODING", "blue"), ("HAPPY HOUR", "pink")):
        _, cap = fitline(90, 0, s, 1620)
        y += cap
        if ink == "pink":
            pr("yellow", fitline(104, y + 14, s, 1620)[0])
        pr(ink, fitline(90, y, s, 1620)[0])
        y += 36
    pr("blue", M(90, y + 60, ["A two-hour workshop that gets 8–14 year olds building",
                              "their first game with an AI coding agent."], 34, 48))
    # game scene
    top, ground = 1060, 1700
    pr("yellow", '<rect x="90" y="1000" width="1620" height="760" fill="url(#ht-yellow-30)"/>')
    pr("blue", f'<rect x="90" y="1000" width="1620" height="760" fill="none" stroke="currentColor" stroke-width="5"/>',
       rule(90, ground, 1710, 6), T(1670, 1060, "SCORE 0042", 34, MONO, "end", weight=700))
    p = 34
    cx, cy = 1050, 1180
    pr("yellow", pixels(cx, cy, p, CAT))
    pr("pink", pixels(cx, cy + 4 * p, p, CAT[4:], fill="url(#ht-pink-50)"))
    pr("blue", pixels(cx, cy, p, CAT, "O"))
    pr("pink", f'<path d="M820 {ground - 8} Q1180 820 1560 {ground - 8}" fill="none" stroke="currentColor" '
               f'stroke-width="9" stroke-dasharray="2 24" stroke-linecap="round"/>')
    for x0, pp in ((1280, 30), (1540, 24)):
        rows = len(CACTUS)
        pr("yellow", pixels(x0, ground - rows * pp, pp, CACTUS))
        pr("blue", pixels(x0, ground - rows * pp, pp, CACTUS, fill="url(#ht-blue-70)"))
    chat = [(">", "make a cat that jumps over cactuses"), ("ai", "Done. Press space to jump."),
            (">", "make it jump higher lol"), ("ai", "Jump height doubled. Try it.")]
    for i, (who, s) in enumerate(chat):
        yy = 1080 + i * 108
        if who == ">":
            pr("pink", f'<rect x="130" y="{yy}" width="{len(s) * 15.3 + 70:.0f}" height="78" rx="39"/>')
            pr("blue", T(160, yy + 50, "> " + s, 25, MONO, weight=700))
        else:
            pr("blue", f'<rect x="130" y="{yy}" width="{len(s) * 15.3 + 50:.0f}" height="78" rx="39" fill="none" '
                       f'stroke="currentColor" stroke-width="4"/>', T(160, yy + 50, s, 25, MONO))
    pr("pink", burst(420, 1620, 130, 110, 16, 4))
    pr("blue", f'<g transform="rotate(-8 420 1620)">{T(420, 1602, "AGES", 42, anchor="middle")}'
               f'{T(420, 1668, "8–14", 70, anchor="middle")}</g>')
    facts = [("2 HRS", "one workshop"), ("FREE", "like everything we run"), ("OPEN", "source curriculum"),
             ("GOOGLE", "office pilot, May 2026")]
    for i, (big, small) in enumerate(facts):
        x = 90 + i * 412
        pr("blue", f'<rect x="{x}" y="1810" width="384" height="190" fill="none" stroke="currentColor" stroke-width="4"/>',
           T(x + 28, 1930, big, 96 if len(big) < 6 else 78))
        pr("pink", T(x + 30, 1975, small, 21, MONO, weight=700))
    cta_band(pr, 2160, "SCHOOLS: REQUEST A FREE SESSION → CSEQUITYAI.ORG", VIBE, "SCAN FOR DETAILS")
    footer(pr)
    return pr.svg("Vibe Coding Happy Hour poster: 8 to 14 year olds build their first game with an AI coding agent")


def poster_students(projects):
    pr = Print(1800, 2400)
    strip(pr)
    y = 180
    for s, ink in (("BUILT BY", "blue"), ("STUDENTS.", "pink")):
        _, cap = fitline(90, 0, s, 1000)
        y += cap
        if ink == "pink":
            pr("yellow", fitline(102, y + 12, s, 1000)[0])
        pr(ink, fitline(90, y, s, 1000)[0])
        y += 26
    pr("yellow", '<circle cx="1440" cy="400" r="240"/>')
    pr("pink", burst(1440, 400, 222, 190, 24, 0, fill="url(#ht-pink-50)"))
    pr("blue", f'<g transform="rotate(8 1440 400)">{T(1440, 420, "6", 230, anchor="middle")}'
               f'{T(1440, 478, "AI SYSTEMS", 46, anchor="middle")}{T(1440, 528, "SHIPPED", 46, anchor="middle")}</g>')
    pr("blue", M(90, y + 50, ["From our last course, “The Course of Making AI Tutor for [X].”",
                              "Real repos, real demos."], 32, 46))
    top = y + 120
    rh = 178
    for i, (name, desc, stack) in enumerate(projects):
        yy = top + i * rh
        pr("blue", rule(90, yy, 1710, 3, "8 8"))
        pr("yellow", T(90, yy + 150, f"{i + 1:02d}", 140))
        pr("pink", T(100, yy + 160, f"{i + 1:02d}", 140, fill="url(#ht-pink-50)"))
        pr("blue", T(300, yy + 78, name.upper() if name.isascii() else name, 56, CJK),
           M(300, yy + 122, [" ".join(desc)], 24, 34))
        if stack:
            pr("pink", T(300, yy + 156, stack.upper(), 20, MONO, weight=700))
    pr("blue", rule(90, top + 6 * rh, 1710, 3, "8 8"))
    pr("blue", T(90, 2080, "NEXT COURSE: FALL 2026. THE ROSTER IS DRAWN FROM STUDENTS WHO", 24, MONO, weight=700),
       T(90, 2115, "FINISH THE FREE FOUNDATION COURSE. START IT NOW.", 24, MONO, weight=700))
    cta_band(pr, 2190, "YOUR TEAM COULD SHIP ONE TOO → CSEQUITYAI.ORG", SITE, "SCAN TO START")
    footer(pr)
    return pr.svg("CS Equity AI poster: six AI systems built by students")
