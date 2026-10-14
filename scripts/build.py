#!/usr/bin/env python3
"""Generate every CS Equity AI promo SVG from one place.

All copy here is taken from csequityai.org. If the site changes, change it here
and re-run:

    pip install segno
    python3 scripts/build.py
    node scripts/render.mjs      # optional: PNG previews + demo.mp4
"""
from pathlib import Path
from xml.sax.saxutils import escape
import re

import segno

ROOT = Path(__file__).resolve().parent.parent

INDIGO, CORAL, TEAL, SUN, CREAM, LAV, INK2 = (
    "#1E1B4B", "#FF6B5B", "#14B8A6", "#FBBF24", "#FFF8EE", "#A5B4FC", "#3B3870")
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
CJK = "Inter, 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', 'WenQuanYi Zen Hei', sans-serif"

SITE = "https://csequityai.org"
VIBE = "https://csequityai.org/events/vibe-coding-happy-hour.html"


# ---------------------------------------------------------------- helpers

def svg(w, h, body, title, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="{escape(title)}">\n'
            f'<title>{escape(title)}</title>\n{extra_defs}{body}\n</svg>\n')


def text(x, y, s, size, fill=INDIGO, weight=400, anchor="start", ls=0, font=FONT, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}" {extra}>{escape(s) if "<tspan" not in s else s}</text>')


def lines(x, y, rows, size, lh, **kw):
    return "\n".join(text(x, y + i * lh, r, size, **kw) for i, r in enumerate(rows))


def mark(x, y, size):
    """The logo mark: code brackets around an equals sign, with two gold nodes."""
    s = size / 120
    return f'''<g transform="translate({x} {y}) scale({s})">
  <rect width="120" height="120" rx="28" fill="{INDIGO}"/>
  <path d="M38 36 L20 60 L38 84" fill="none" stroke="{CORAL}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M82 36 L100 60 L82 84" fill="none" stroke="{TEAL}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="44" y1="50" x2="76" y2="50" stroke="{CREAM}" stroke-width="8" stroke-linecap="round"/>
  <line x1="44" y1="70" x2="76" y2="70" stroke="{CREAM}" stroke-width="8" stroke-linecap="round"/>
  <circle cx="60" cy="30" r="7" fill="{SUN}"/><circle cx="60" cy="90" r="7" fill="{SUN}"/>
</g>'''


def qr(url, x, y, size, pad=22, bg="#FFFFFF", fg=INDIGO):
    q = segno.make(url, error="m")
    n = q.symbol_size(scale=1, border=0)[0]
    path = re.search(r' d="([^"]+)"', q.svg_inline(scale=1, border=0)).group(1)
    s = (size - 2 * pad) / n
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="20" fill="{bg}"/>'
            f'<path transform="translate({x + pad} {y + pad}) scale({s})" stroke="{fg}" '
            f'fill="none" d="{path}"/>')


def network(x, y, w, h, r=14, cols=(3, 4, 2), stroke="#1E1B4B22"):
    """Little input / hidden / output net, like the hero on the site."""
    pts = []
    for ci, n in enumerate(cols):
        cx = x + ci * w / (len(cols) - 1)
        pts.append([(cx, y + (i + 0.5) * h / n) for i in range(n)])
    out = []
    for a, b in zip(pts, pts[1:]):
        for p in a:
            for q in b:
                out.append(f'<line x1="{p[0]:.0f}" y1="{p[1]:.0f}" x2="{q[0]:.0f}" y2="{q[1]:.0f}" '
                           f'stroke="{stroke}" stroke-width="3"/>')
    colors = [CORAL, SUN, TEAL]
    for ci, col in enumerate(pts):
        for p in col:
            out.append(f'<circle cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="{r}" fill="{colors[ci]}"/>')
    return "\n".join(out)


def pill(x, y, label, size, bg, fg, padx=22, h=None, weight=700, ls=2):
    h = h or size * 1.9
    w = len(label) * (size * 0.68 + ls) + padx * 2
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h:.0f}" rx="{h / 2:.0f}" fill="{bg}"/>'
            + text(x + padx, y + h / 2 + size * 0.36, label, size, fg, weight, ls=ls))


def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


# ---------------------------------------------------------------- posters

LEVELS = [
    ("i.", "LEVEL 1 · CAPABILITY", "Foundation course", ["Self-paced, in the browser"], "Foundation Certificate"),
    ("ii.", "LEVEL 2 · CREATION", "Bootcamp", ["Weekly live sessions,", "small teams"], "A working AI system"),
    ("iii.", "LEVEL 3 · CAPITAL", "Startup", ["Founding team of", "three to five"], "Pitch to angel investors"),
]


def poster_main():
    W, H = 1800, 2400
    b = [f'<rect width="{W}" height="{H}" fill="{CREAM}"/>',
         network(1300, 110, 360, 280, r=16),
         mark(120, 100, 110),
         text(255, 160, "CS Equity AI", 50, INDIGO, 800, ls=-1),
         text(257, 200, "501(c)(3) public charity · since 2021", 26, INK2, 500),
         lines(120, 560, ["We teach students", "to build with AI,"], 128, 140, fill=INDIGO, weight=800, ls=-3),
         text(120, 840, "not just use it.", 128, CORAL, 800, ls=-3),
         text(120, 1090, "Free.", 230, TEAL, 800, ls=-6),
         lines(124, 1200, ["Live online courses taught by engineers from Google and",
                           "academia, for students in the US, Taiwan and Hong Kong.",
                           "No tuition. You need a browser and some curiosity."],
               40, 60, fill=INK2, weight=500),
         f'<rect y="1420" width="{W}" height="600" fill="{INDIGO}"/>',
         text(120, 1515, "How it works", 52, CREAM, 800, ls=-1),
         text(470, 1515, "Each level ends with something real.", 32, LAV, 500)]
    for i, (num, lab, title, desc, outcome) in enumerate(LEVELS):
        x = 120 + i * 540
        b += [text(x, 1650, num, 84, CORAL, 800),
              text(x, 1712, lab, 22, TEAL, 700, ls=3),
              text(x, 1770, title, 46, CREAM, 800, ls=-1),
              lines(x, 1822, desc, 30, 40, fill=LAV, weight=500),
              text(x, 1905, "→ " + outcome, 28, SUN, 700)]
    b += [text(120, 1990, "Finishing one level is how you get into the next.", 26, LAV, 400,
               extra='font-style="italic"'),
          text(120, 2150, "Start with the free Foundation course.", 58, INDIGO, 800, ls=-1),
          lines(122, 2210, ["It’s open now, and it’s how students get onto the", "roster for the Fall 2026 course."],
                32, 44, fill=INK2, weight=500),
          text(120, 2340, "csequityai.org", 72, CORAL, 800, ls=-1),
          qr(SITE, 1430, 2080, 250, bg="#FFFFFF"),
          text(1555, 2368, "scan to start", 24, INK2, 600, anchor="middle", ls=2)]
    write("posters/poster-build-with-ai.svg",
          svg(W, H, "\n".join(b), "CS Equity AI poster: We teach students to build with AI, not just use it. Free."))


def game_window(x, y, w, h):
    """Chat with a coding agent on the left, the kid's game on the right."""
    split = x + w * 0.44
    g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28" fill="{CREAM}"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="64" rx="28" fill="#E9E3F7"/>',
         f'<rect x="{x}" y="{y + 36}" width="{w}" height="28" fill="#E9E3F7"/>']
    for i, c in enumerate([CORAL, SUN, TEAL]):
        g.append(f'<circle cx="{x + 40 + i * 32}" cy="{y + 32}" r="10" fill="{c}"/>')
    g.append(text(x + w / 2, y + 42, "my-first-game", 24, INK2, 600, anchor="middle"))
    g.append(f'<line x1="{split}" y1="{y + 64}" x2="{split}" y2="{y + h}" stroke="#E2DCF0" stroke-width="3"/>')

    # chat bubbles
    bx, bw = x + 34, split - x - 68
    chat = [("kid", ["make a cat that jumps", "over cactuses"]),
            ("agent", ["Done. Press space to jump."]),
            ("kid", ["make it jump higher lol"]),
            ("agent", ["Jump height doubled. Try it."])]
    cy = y + 110
    for who, rows in chat:
        hh = 30 + len(rows) * 38
        kid = who == "kid"
        ww = bw * (0.86 if kid else 0.9)
        xx = bx + (bw - ww if kid else 0)
        g.append(f'<rect x="{xx:.0f}" y="{cy}" width="{ww:.0f}" height="{hh}" rx="22" '
                 f'fill="{CORAL if kid else "#FFFFFF"}" stroke="{"none" if kid else "#E2DCF0"}" stroke-width="2"/>')
        g.append(lines(xx + 26, cy + 46, rows, 28, 38, fill="#FFFFFF" if kid else INDIGO, weight=600))
        cy += hh + 26

    g.append(f'<rect x="{bx}" y="{y + h - 100}" width="{bw}" height="64" rx="32" fill="#FFFFFF" stroke="#E2DCF0" stroke-width="2"/>')
    g.append(text(bx + 30, y + h - 58, "now add a high score…", 26, "#9A96B8", 500))
    g.append(f'<circle cx="{bx + bw - 32}" cy="{y + h - 68}" r="20" fill="{CORAL}"/>')
    g.append(f'<path d="M{bx + bw - 40} {y + h - 68} h16 m-7 -7 l7 7 l-7 7" fill="none" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')

    # game scene
    gx, gw = split + 30, x + w - split - 60
    ground = y + h - 120
    g.append(text(gx + gw - 10, y + 120, "SCORE 0042", 28, INDIGO, 800, anchor="end", ls=3,
                  font="'DejaVu Sans Mono', ui-monospace, monospace"))
    for cxx, cyy in [(gx + 80, y + 170), (gx + 330, y + 220)]:
        g.append(f'<g fill="#FFFFFF"><circle cx="{cxx}" cy="{cyy}" r="30"/><circle cx="{cxx + 36}" cy="{cyy - 10}" r="38"/>'
                 f'<circle cx="{cxx + 76}" cy="{cyy}" r="28"/></g>')
    g.append(f'<rect x="{gx}" y="{ground}" width="{gw}" height="10" rx="5" fill="{INDIGO}"/>')
    # dotted jump arc
    g.append(f'<path d="M{gx + 60} {ground - 40} Q {gx + 250} {ground - 420} {gx + 440} {ground - 40}" '
             f'fill="none" stroke="{TEAL}" stroke-width="5" stroke-dasharray="4 16" stroke-linecap="round"/>')
    # pixel cat mid-jump
    px, py, p = gx + 200, ground - 330, 16
    cat = ["X...X", "XXXXX", "XOXOX", "XXXXX", ".XXXXXXX", ".XXXXXX.", ".X.X.X.X"]
    for r, row in enumerate(cat):
        for c, ch in enumerate(row):
            if ch == "X":
                g.append(f'<rect x="{px + c * p}" y="{py + r * p}" width="{p}" height="{p}" fill="{SUN}"/>')
            elif ch == "O":
                g.append(f'<rect x="{px + c * p}" y="{py + r * p}" width="{p}" height="{p}" fill="{INDIGO}"/>')
    # cactuses
    for cx0 in (gx + 250, gx + 560):
        g.append(f'<g fill="{TEAL}"><rect x="{cx0}" y="{ground - 130}" width="34" height="130" rx="12"/>'
                 f'<rect x="{cx0 - 30}" y="{ground - 90}" width="22" height="50" rx="10"/>'
                 f'<rect x="{cx0 - 30}" y="{ground - 52}" width="44" height="18" rx="9"/>'
                 f'<rect x="{cx0 + 42}" y="{ground - 110}" width="22" height="46" rx="10"/>'
                 f'<rect x="{cx0 + 22}" y="{ground - 76}" width="42" height="18" rx="9"/></g>')
    return "\n".join(g)


def poster_vibe():
    W, H = 1800, 2400
    b = [f'<rect width="{W}" height="{H}" fill="{INDIGO}"/>',
         pill(120, 110, "OPEN TO HOSTS · FREE", 28, SUN, INDIGO, ls=3),
         text(120, 390, "Vibe Coding", 180, CREAM, 800, ls=-5),
         text(120, 570, "Happy Hour", 180, CORAL, 800, ls=-5),
         lines(124, 700, ["Kids aged 8 to 14 build their first game", "with an AI coding agent. In two hours."],
               56, 74, fill=CREAM, weight=500),
         game_window(120, 880, 1560, 780)]
    facts = [("2 hrs", "one workshop"), ("8–14", "years old"), ("Free", "like everything we run"),
             ("Open", "source curriculum")]
    for i, (big, small) in enumerate(facts):
        x = 120 + i * 400
        b += [text(x, 1810, big, 84, TEAL if i % 2 else SUN, 800, ls=-2),
              text(x + 2, 1860, small, 28, LAV, 500)]
    b += [text(120, 1960, "Piloted at a Google office in May 2026.", 32, LAV, 500, extra='font-style="italic"'),
          f'<line x1="120" y1="2020" x2="1680" y2="2020" stroke="#FFFFFF22" stroke-width="2"/>',
          text(120, 2140, "Schools: request a free session.", 62, CREAM, 800, ls=-1),
          text(120, 2230, "csequityai.org", 60, TEAL, 800, ls=-1),
          mark(120, 2272, 64),
          text(200, 2316, "CS Equity AI · 501(c)(3) public charity", 26, LAV, 500),
          qr(VIBE, 1420, 2070, 260, bg=CREAM),
          text(1550, 2370, "scan for details", 22, LAV, 600, anchor="middle", ls=2)]
    write("posters/poster-vibe-coding-happy-hour.svg",
          svg(W, H, "\n".join(b), "Vibe Coding Happy Hour poster: kids 8 to 14 build their first game with an AI coding agent"))


PROJECTS = [
    ("AI 菜單推薦系統", ["Upload a photo of a menu, get", "waiter-style suggestions."], ["RAG", "OCR", "ChromaDB"]),
    ("Travel AI", ["Travel recommendations from a RAG", "pipeline plus the Gemini API."], ["RAG", "Gemini API"]),
    ("Cooking Assistant Agent", ["Walks you through any recipe step by", "step, with help when you’re stuck."], ["Agent"]),
    ("Compai", ["A companion chatbot on Telegram."], ["RAG", "Gemini", "ChromaDB", "Embeddings"]),
    ("Smart Travel Agent", ["Collects preferences, curates attractions", "with live data, writes the itinerary."], ["Live demo"]),
    ("Gacha Game Pull Advisor", ["What to pull, how to build your", "character. Confusion ends here."], []),
]


def poster_students():
    W, H = 1800, 2400
    b = [f'<rect width="{W}" height="{H}" fill="{CREAM}"/>',
         mark(120, 100, 90),
         text(230, 162, "CS Equity AI", 44, INDIGO, 800, ls=-1),
         text(120, 400, "Built by students.", 140, INDIGO, 800, ls=-4),
         lines(124, 500, ["Six of the AI systems shipped by teams in our last course,",
                          "“The Course of Making AI Tutor for [X].” Real repos, real demos."],
               38, 54, fill=INK2, weight=500)]
    accents = [CORAL, TEAL, SUN]
    for i, (name, desc, tags) in enumerate(PROJECTS):
        x, y = 120 + (i % 2) * 810, 640 + (i // 2) * 420
        a = accents[i % 3]
        b += [f'<rect x="{x}" y="{y}" width="750" height="380" rx="28" fill="#FFFFFF" stroke="#E9E3F7" stroke-width="3"/>',
              f'<rect x="{x}" y="{y + 40}" width="10" height="300" rx="5" fill="{a}"/>',
              text(x + 50, y + 80, f"{i + 1:02d}", 30, a if a != SUN else "#D69E0B", 800, ls=2),
              text(x + 50, y + 145, name, 48 if len(name) > 18 else 54, INDIGO, 800, ls=-1, font=CJK),
              lines(x + 50, y + 200, desc, 30, 42, fill=INK2, weight=500)]
        tx = x + 50
        for t in tags:
            w = len(t) * 15 + 36
            b += [f'<rect x="{tx}" y="{y + 300}" width="{w}" height="44" rx="22" fill="#F1EDFB"/>',
                  text(tx + w / 2, y + 330, t, 22, INK2, 700, anchor="middle")]
            tx += w + 12
    b += [text(120, 2010 + 70, "The next course starts Fall 2026.", 64, INDIGO, 800, ls=-1),
          lines(122, 2150, ["Students who finish the free Foundation course", "are first in line for the roster."],
                34, 48, fill=INK2, weight=500),
          text(120, 2320, "csequityai.org", 72, CORAL, 800, ls=-1),
          qr(SITE, 1430, 2040, 250),
          text(1555, 2330, "scan to start", 24, INK2, 600, anchor="middle", ls=2)]
    write("posters/poster-built-by-students.svg",
          svg(W, H, "\n".join(b), "CS Equity AI poster: six AI systems built by students"))


# ---------------------------------------------------------------- social

def social():
    S = 1080
    # 1. headline
    b = [f'<rect width="{S}" height="{S}" fill="{INDIGO}"/>',
         network(720, 90, 260, 200, r=12, stroke="#FFFFFF22"),
         lines(80, 430, ["We teach students", "to build with AI,"], 92, 104, fill=CREAM, weight=800, ls=-2),
         text(80, 638, "not just use it.", 92, CORAL, 800, ls=-2),
         text(80, 840, "Free.", 170, TEAL, 800, ls=-4),
         mark(80, 930, 70),
         text(170, 978, "csequityai.org", 40, CREAM, 700)]
    write("social/square-01-build-with-ai.svg", svg(S, S, "\n".join(b), "We teach students to build with AI, not just use it. Free."))

    # 2. the path
    b = [f'<rect width="{S}" height="{S}" fill="{CREAM}"/>',
         text(80, 170, "From first lesson", 78, INDIGO, 800, ls=-2),
         text(80, 260, "to founding team.", 78, CORAL, 800, ls=-2)]
    for i, (num, lab, title, desc, outcome) in enumerate(LEVELS):
        y = 350 + i * 190
        b += [f'<rect x="80" y="{y}" width="920" height="160" rx="26" fill="#FFFFFF" stroke="#E9E3F7" stroke-width="3"/>',
              text(120, y + 100, num, 64, CORAL, 800),
              text(270, y + 58, lab, 20, TEAL, 700, ls=3),
              text(270, y + 104, title, 40, INDIGO, 800, ls=-1),
              text(270, y + 140, "→ " + outcome, 26, INK2, 600)]
    b += [text(80, 980, "Free, all of it.", 40, INDIGO, 800),
          text(1000, 980, "csequityai.org", 40, CORAL, 800, anchor="end")]
    write("social/square-02-the-path.svg", svg(S, S, "\n".join(b), "From first lesson to founding team: the CS Equity AI path"))

    # 3. Happy Hour
    b = [f'<rect width="{S}" height="{S}" fill="{SUN}"/>',
         pill(80, 80, "OPEN TO HOSTS", 24, INDIGO, SUN, ls=3),
         text(80, 290, "Vibe Coding", 120, INDIGO, 800, ls=-4),
         text(80, 410, "Happy Hour", 120, CORAL, 800, ls=-4),
         lines(84, 510, ["Kids aged 8 to 14 build their", "first game with an AI coding", "agent. Two hours. Free."],
               48, 62, fill=INDIGO, weight=600),
         text(84, 780, "Your school can host one.", 48, INDIGO, 800, ls=-1),
         mark(80, 900, 80),
         text(180, 955, "csequityai.org", 44, INDIGO, 800)]
    # pixel cat corner
    px, py, p = 780, 800, 22
    for r, row in enumerate(["X...X", "XXXXX", "XOXOX", "XXXXX", ".XXXXXXX", ".XXXXXX.", ".X.X.X.X"]):
        for c, ch in enumerate(row):
            if ch != ".":
                b.append(f'<rect x="{px + c * p}" y="{py + r * p}" width="{p}" height="{p}" '
                         f'fill="{INDIGO if ch == "X" else SUN}"/>')
    write("social/square-03-vibe-coding.svg", svg(S, S, "\n".join(b), "Vibe Coding Happy Hour: your school can host one"))

    # 4. Facebook cover 1640x624 (keep text in the middle so mobile crops are safe)
    W, H = 1640, 624
    b = [f'<rect width="{W}" height="{H}" fill="{INDIGO}"/>',
         network(1250, 150, 260, 320, r=16, stroke="#FFFFFF22"),
         text(300, 250, "Build with AI,", 96, CREAM, 800, ls=-3),
         text(300, 360, "not just use it.", 96, CORAL, 800, ls=-3),
         text(304, 440, "Free CS & AI courses taught by working engineers.", 32, LAV, 500),
         text(304, 490, "Since 2021 · US · Taiwan · Hong Kong · csequityai.org", 32, TEAL, 700)]
    write("social/facebook-cover.svg", svg(W, H, "\n".join(b), "CS Equity AI: build with AI, not just use it"))


# ---------------------------------------------------------------- video

D = 30.0  # seconds per loop


class Anim:
    def __init__(self):
        self.css, self.n = [], 0

    def _kf(self, pts, extra=""):
        self.n += 1
        name = f"a{self.n}"
        frames = " ".join(f"{100 * t / D:.3f}% {{{p}}}" for t, p in pts)
        self.css.append(f"@keyframes {name} {{{frames}}}\n.{name} {{animation: {name} {D}s linear infinite both;{extra}}}")
        return name

    def show(self, t0, t1, dy=30, fade=0.45):
        hid = f"opacity:0;transform:translateY({dy}px)"
        on = "opacity:1;transform:translateY(0)"
        off = "opacity:0;transform:translateY(0)"
        pts = [(0, hid if t0 > 0 else on), (t0, hid), (t0 + fade, on), (t1 - fade, on), (t1, off), (D, off)]
        if t0 == 0:
            pts = [(0, hid), (fade, on), (t1 - fade, on), (t1, off), (D, off)]
        return self._kf(pts)

    def grow(self, t0, t1):
        return self._kf([(0, "transform:scaleX(0)"), (t0, "transform:scaleX(0)"),
                         (t1, "transform:scaleX(1)"), (D, "transform:scaleX(1)")],
                        "transform-box:fill-box;transform-origin:left center;")

    def pop(self, t0):
        return self._kf([(0, "transform:scale(0)"), (t0, "transform:scale(0)"),
                         (t0 + 0.25, "transform:scale(1.15)"), (t0 + 0.4, "transform:scale(1)"),
                         (D, "transform:scale(1)")],
                        "transform-box:fill-box;transform-origin:center;")

    def tint(self, t0, t1, off_color, on_color):
        return self._kf([(0, f"fill:{off_color}"), (t0, f"fill:{off_color}"), (t0 + 0.3, f"fill:{on_color}"),
                         (t1 - 0.3, f"fill:{on_color}"), (t1, f"fill:{off_color}"), (D, f"fill:{off_color}")])


def g(cls, inner):
    return f'<g class="{cls}">{inner}</g>'


def window(x, y, w, h, title):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{CREAM}"/>',
           f'<path d="M{x} {y + 22} a22 22 0 0 1 22 -22 h{w - 44} a22 22 0 0 1 22 22 v34 h-{w} z" fill="#E9E3F7"/>']
    for i, c in enumerate([CORAL, SUN, TEAL]):
        out.append(f'<circle cx="{x + 32 + i * 26}" cy="{y + 28}" r="8" fill="{c}"/>')
    out.append(text(x + w / 2, y + 36, title, 22, INK2, 600, anchor="middle"))
    return "\n".join(out)


def scene_text(A, t0, t1, label, title, body):
    return "\n".join([
        g(A.show(t0 + 0.1, t1), text(160, 380, label, 30, TEAL, 700, ls=4)),
        g(A.show(t0 + 0.3, t1), text(156, 480, title, 80, CREAM, 800, ls=-3)),
        g(A.show(t0 + 0.6, t1), lines(160, 570, body, 38, 54, fill=LAV, weight=500)),
    ])


def video():
    W, H = 1920, 1080
    A = Anim()
    out = [f'<rect width="{W}" height="{H}" fill="{INDIGO}"/>']

    # persistent corner brand
    out.append(mark(80, 960, 64) + text(160, 1003, "CS Equity AI", 30, CREAM, 700))

    # step tracker, visible during the three levels
    steps = [("i. Capability", 5, 11), ("ii. Creation", 11, 18), ("iii. Capital", 18, 23)]
    tracker = []
    for i, (lab, s0, s1) in enumerate(steps):
        x = 160 + i * 300
        tracker.append(f'<circle class="{A.tint(s0, s1, "#FFFFFF33", CORAL)}" cx="{x}" cy="120" r="12"/>')
        tracker.append(text(x + 26, 130, lab, 26, LAV, 600))
        if i < 2:
            tracker.append(f'<line x1="{x + 210}" y1="120" x2="{x + 270}" y2="120" stroke="#FFFFFF33" stroke-width="3"/>')
    out.append(g(A.show(5, 23, dy=0), "\n".join(tracker)))

    # S1 0–5: hook
    out.append(g(A.show(0.2, 5), text(W / 2, 470, "Plenty of students use AI.", 96, CREAM, 800, anchor="middle", ls=-2)))
    out.append(g(A.show(1.6, 5), text(W / 2, 640, "Ours build it.", 150, CORAL, 800, anchor="middle", ls=-4)))
    out.append(g(A.show(2.6, 5), text(W / 2, 740, "Free CS & AI courses since 2021", 36, LAV, 500, anchor="middle")))

    # S2 5–11: Capability
    out.append(scene_text(A, 5, 11, "LEVEL 1 · CAPABILITY", "Learn the essentials",
                          ["The free Foundation course on the", "OpenImpact Lab. Self-paced and it", "runs in your browser. Nothing to install."]))
    wx, wy = 1080, 250
    lab = [window(wx, wy, 680, 520, "OpenImpact Lab")]
    lessons = ["CS fundamentals", "AI fundamentals", "Hands-on lab: modern AI tooling"]
    for i, l in enumerate(lessons):
        y = wy + 110 + i * 90
        lab.append(f'<rect x="{wx + 40}" y="{y}" width="600" height="68" rx="14" fill="#FFFFFF"/>')
        lab.append(text(wx + 120, y + 44, l, 28, INDIGO, 600))
        lab.append(f'<circle cx="{wx + 80}" cy="{y + 34}" r="18" fill="#E9E3F7"/>')
        lab.append(g(A.pop(6.4 + i * 0.9),
                     f'<circle cx="{wx + 80}" cy="{y + 34}" r="18" fill="{TEAL}"/>'
                     f'<path d="M{wx + 71} {y + 34} l6 7 l12 -14" fill="none" stroke="#FFFFFF" stroke-width="4" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>'))
    lab.append(f'<rect x="{wx + 40}" y="{wy + 410}" width="600" height="18" rx="9" fill="#E9E3F7"/>')
    lab.append(f'<rect class="{A.grow(6.2, 9.2)}" x="{wx + 40}" y="{wy + 410}" width="600" height="18" rx="9" fill="{TEAL}"/>')
    lab.append(text(wx + 40, wy + 470, "Foundation course", 24, INK2, 600))
    # certificate badge
    lab.append(g(A.pop(9.4),
                 f'<circle cx="{wx + 610}" cy="{wy + 470}" r="92" fill="{SUN}"/>'
                 f'<circle cx="{wx + 610}" cy="{wy + 470}" r="74" fill="none" stroke="{INDIGO}" stroke-width="3" stroke-dasharray="6 8"/>'
                 + text(wx + 610, wy + 462, "FOUNDATION", 15, INDIGO, 800, anchor="middle", ls=2)
                 + text(wx + 610, wy + 492, "CERTIFICATE", 15, INDIGO, 800, anchor="middle", ls=2)))
    out.append(g(A.show(5.2, 11), "\n".join(lab)))

    # S3 11–18: Creation
    out.append(scene_text(A, 11, 18, "LEVEL 2 · CREATION", "Build a real AI system",
                          ["Weekly live sessions in small teams,", "taught by engineers from Google", "and academia."]))
    ex, ey = 1100, 180
    ed = [window(ex, ey, 680, 340, "team-3 / app.py")]
    code = [("def recommend(menu_photo):", CORAL), ("    text = ocr(menu_photo)", CREAM),
            ("    dishes = retrieve(text, k=5)", CREAM), ("    return llm.suggest(dishes)", CREAM)]
    ed.append(f'<rect x="{ex}" y="{ey + 56}" width="680" height="284" fill="#2A2660"/>')
    ed.append(f'<path d="M{ex} {ey + 318} v0 a22 22 0 0 0 22 22 h636 a22 22 0 0 0 22 -22" fill="#2A2660"/>')
    for i, (c, col) in enumerate(code):
        y = ey + 120 + i * 50
        ed.append(f'<g class="{A.grow(11.8 + i * 0.7, 12.4 + i * 0.7)}">'
                  + text(ex + 40, y, c, 28, col, 500, font="'DejaVu Sans Mono', ui-monospace, monospace",
                         extra='xml:space="preserve"') + "</g>")
    ed.append(g(A.show(14.6, 18, dy=10),
                text(ex + 40, ey + 320, "✓ tests passed", 26, TEAL, 700, font="'DejaVu Sans Mono', ui-monospace, monospace")))
    shipped = [("AI 菜單推薦系統", "Menu photo in, waiter-style picks out"),
               ("Smart Travel Agent", "Curates attractions, writes the itinerary"),
               ("Cooking Assistant Agent", "Walks you through any recipe")]
    for i, (n, d) in enumerate(shipped):
        y = ey + 370 + i * 112
        ed.append(g(A.show(15.0 + i * 0.6, 18),
                    f'<rect x="{ex}" y="{y}" width="680" height="96" rx="18" fill="#FFFFFF"/>'
                    f'<rect x="{ex}" y="{y}" width="10" height="96" rx="5" fill="{[CORAL, TEAL, SUN][i]}"/>'
                    + text(ex + 36, y + 42, n, 30, INDIGO, 800, font=CJK)
                    + text(ex + 36, y + 78, d, 22, INK2, 500)))
    ed.append(g(A.show(15.0, 18), text(ex + 680, ey + 370 - 18, "shipped by students", 22, LAV, 600, anchor="end", ls=2)))
    out.append(g(A.show(11.2, 18), "\n".join(ed)))

    # S4 18–23: Capital
    out.append(scene_text(A, 18, 23, "LEVEL 3 · CAPITAL", "Pitch it",
                          ["A founding team of three to five", "takes what they built in front", "of angel investors."]))
    sx, sy = 1060, 220
    st = [f'<rect x="{sx}" y="{sy}" width="700" height="400" rx="20" fill="{CREAM}"/>',
          text(sx + 50, sy + 90, "Investor pitch", 46, INDIGO, 800, ls=-1),
          text(sx + 50, sy + 136, "Team 2 · AI travel agent", 26, INK2, 600),
          f'<polyline class="{A.grow(19.0, 20.6)}" points="{sx + 60},{sy + 340} {sx + 220},{sy + 300} {sx + 360},{sy + 250} '
          f'{sx + 500},{sy + 230} {sx + 640},{sy + 170}" fill="none" stroke="{CORAL}" stroke-width="10" '
          f'stroke-linecap="round" stroke-linejoin="round"/>',
          f'<rect x="{sx + 340}" y="{sy + 400}" width="20" height="90" fill="#FFFFFF33"/>']
    team_cols = [CORAL, TEAL, SUN, LAV]
    for i, c in enumerate(team_cols):
        x = sx + 180 + i * 110
        st.append(g(A.show(19.4 + i * 0.2, 23, dy=20),
                    f'<circle cx="{x}" cy="{sy + 560}" r="30" fill="{c}"/>'
                    f'<path d="M{x - 46} {sy + 660} a46 50 0 0 1 92 0 z" fill="{c}"/>'))
    for i in range(7):
        x = sx + 20 + i * 110
        st.append(f'<circle cx="{x}" cy="{sy + 740}" r="26" fill="#FFFFFF22"/>')
    out.append(g(A.show(18.2, 23), "\n".join(st)))

    # S5 23–26.5: free
    out.append(g(A.show(23.1, 26.5), text(W / 2, 560, "$0", 320, SUN, 800, anchor="middle", ls=-10)))
    out.append(g(A.show(23.5, 26.5), text(W / 2, 680, "tuition. Ever.", 76, CREAM, 800, anchor="middle", ls=-2)))
    out.append(g(A.show(24.2, 26.5), text(W / 2, 770, "Students in the US, Taiwan and Hong Kong, since 2021.",
                                          38, LAV, 500, anchor="middle")))

    # S6 26.5–30: call to action
    out.append(g(A.show(26.6, 29.8), mark(W / 2 - 90, 230, 180)))
    out.append(g(A.show(26.9, 29.8), text(W / 2, 560, "Start with the free Foundation course.", 64, CREAM, 800, anchor="middle", ls=-2)))
    out.append(g(A.show(27.3, 29.8), text(W / 2, 700, "csequityai.org", 110, CORAL, 800, anchor="middle", ls=-3)))
    out.append(g(A.show(27.7, 29.8), text(W / 2, 790, "The Fall 2026 roster is drawn from students who finish it.",
                                          34, LAV, 500, anchor="middle")))

    defs = "<style>\n" + "\n".join(A.css) + "\n</style>\n"
    write("video/demo.svg", svg(W, H, "\n".join(out), "CS Equity AI: 30-second demo of what we do", defs))


if __name__ == "__main__":
    poster_main()
    poster_vibe()
    poster_students()
    social()
    video()
