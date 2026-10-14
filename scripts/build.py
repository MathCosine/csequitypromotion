#!/usr/bin/env python3
"""Generate every CS Equity AI promo graphic in the paper-theater style.

All copy is taken from csequityai.org. Change it here, then:

    pip install segno
    python3 scripts/build.py
    node scripts/render.mjs      # PNG exports + video/demo.mp4
"""
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from paper import *  # noqa: E402,F401,F403

SITE = "https://csequityai.org"
VIBE = "https://csequityai.org/events/vibe-coding-happy-hour.html"

LEVELS = [
    ("i.", "LEVEL 1 · CAPABILITY", "Foundation course", ["Self-paced, in the", "browser"], "Foundation Certificate"),
    ("ii.", "LEVEL 2 · CREATION", "Bootcamp", ["Weekly live sessions,", "small teams"], "A working AI system"),
    ("iii.", "LEVEL 3 · CAPITAL", "Startup", ["Founding team of", "three to five"], "Pitch to angel investors"),
]

PROJECTS = [
    ("AI 菜單推薦系統", ["Upload a photo of a menu, get", "waiter-style suggestions."], "RAG · OCR · ChromaDB"),
    ("Travel AI", ["Travel recommendations from a", "RAG pipeline plus the Gemini API."], "RAG · Gemini API"),
    ("Cooking Assistant Agent", ["Walks you through any recipe step", "by step, with help when stuck."], "Agent"),
    ("Compai", ["A companion chatbot on Telegram."], "RAG · Gemini · ChromaDB · embeddings"),
    ("Smart Travel Agent", ["Collects preferences, curates", "attractions, writes the itinerary."], "Live demo on Hugging Face"),
    ("Gacha Game Pull Advisor", ["What to pull, how to build your", "character. Confusion ends here."], ""),
]


def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


def stage(x, y, w, h, inner, cid, r=110, thick=46):
    """Clip `inner` to a porthole opening and put the brass frame over it."""
    return (f'<clipPath id="{cid}"><path d="{rr(x, y, w, h, r)}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{inner}</g>' + frame(x, y, w, h, r, thick))


def hung_card(x, y, w, h, **kw):
    pins = [(x + 60, y + 8), (x + w - 60, y + 8)]
    return (strings(pins) + card(x, y, w, h, **kw)
            + "".join(f'<circle cx="{px}" cy="{py}" r="5" fill="{INK}"/>' for px, py in pins))


def level_sign(x, y, w, h, lvl):
    num, lab, title, desc, outcome = lvl
    return "\n".join([
        hung_card(x, y, w, h),
        t(x + 42, y + 100, num, 60, TERRA, SERIF, 900),
        t(x + 42, y + 140, lab, 21, TEAL_D, TYPE, 400, ls=1.5),
        t(x + 42, y + 188, title, 38, INK, SERIF, 900, ls=-.5),
        tl(x + 42, y + 230, desc, 25, 33, fill=INK, font=TYPE, weight=400),
        f'<line x1="{x + 42}" y1="{y + h - 74}" x2="{x + w - 42}" y2="{y + h - 74}" stroke="{INK}" stroke-opacity=".35" stroke-dasharray="4 5"/>',
        t(x + 42, y + h - 40, "→ " + outcome, 25, TERRA, SERIF, 700)])


def qr_card(x, y, url, label, size=230, rot=4):
    w = size + 70
    cx = x + w / 2
    return (f'<g transform="rotate({rot} {cx} {y + 160})">{card(x, y, w, size + 100)}'
            + qr(url, x + 35, y + 35, size) + t(cx, y + size + 72, label, 24, INK, TYPE, 400, "middle") + "</g>"
            + tape(cx, y + 4, rot=-rot))


# ---------------------------------------------------------------- posters

def poster_main():
    W, H = 1800, 2400
    sx, sy, sw, sh = 140, 930, 1520, 960
    b = [strings([(240, 140), (1560, 140)]),
         card(110, 120, 1580, 690),
         mark(170, 180, 92),
         t(290, 226, "CS Equity AI", 40, INK, SERIF, 900),
         t(292, 262, "501(c)(3) public charity · est. 2021", 22, INK, TYPE, 400),
         t(170, 420, "We teach students", 116, INK, SERIF, 900, ls=-2),
         t(170, 545, "to build with AI,", 116, INK, SERIF, 900, ls=-2),
         t(170, 670, "not just use it.", 116, TERRA, SERIF, 900, ls=-2),
         tl(172, 740, ["Live online courses taught by engineers from Google and academia,",
                       "for students in the US, Taiwan and Hong Kong. Just a browser."], 27, 36,
            fill=INK, font=TYPE, weight=400),
         f'<path d="M1628 236 C 1610 300 1570 330 1508 354" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity=".75"/>',
         f'<circle cx="1628" cy="232" r="10" fill="{BRASS}" stroke="{BRASS_D}" stroke-width="2"/>',
         f'<g transform="rotate(-9 1460 420)">{tag(1270, 330, 400, 170)}'
         + t(1505, 448, "FREE.", 92, EDGE, SERIF, 900, "middle", -1) + "</g>"]
    inner = [scenery(sx, sy, sw, sh, horizon=.47)]
    for i, lvl in enumerate(LEVELS):
        inner.append(level_sign(sx + 40 + i * 490, sy + 500, 460, 400, lvl))
    b.append(stage(sx, sy, sw, sh, "\n".join(inner), "s1"))
    b.append(ledge(70, sy + sh + 60, 1660))
    b.append(t(W / 2, sy + sh + 160, "Each level ends with something real. Finishing one is how you get into the next.",
               27, PAPER, TYPE, 400, "middle"))
    b += [card(110, 2140, 1180, 200),
          tape(200, 2142), tape(1200, 2142, rot=7),
          t(160, 2218, "Start with the free Foundation course.", 50, INK, SERIF, 900, ls=-.5),
          t(160, 2296, "csequityai.org", 58, TERRA, SERIF, 900),
          t(640, 2290, "← open now, and it’s how you get", 23, INK, TYPE, 400),
          t(668, 2318, "onto the Fall 2026 roster", 23, INK, TYPE, 400),
          qr_card(1360, 2070, SITE, "scan to start")]
    write("posters/poster-build-with-ai.svg", doc(W, H, "\n".join(b),
          "CS Equity AI poster: we teach students to build with AI, not just use it. Free."))


def desert(sx, sy, sw, sh, horizon=.74):
    hz = sy + sh * horizon
    out = [f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{SKY}"/>',
           f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#hl)"/>',
           cloud(sx + sw * .05, sy + sh * .06, 1.1), cloud(sx + sw * .55, sy + sh * .1, .9)]
    # far mesas
    out.append(piece(P(poly([(sx, hz), (sx + sw * .08, hz - 70), (sx + sw * .22, hz - 70), (sx + sw * .28, hz),
                             (sx + sw * .6, hz), (sx + sw * .66, hz - 50), (sx + sw * .8, hz - 50), (sx + sw * .86, hz)])),
                     ROSE, hatch="hv", filt="cut"))
    out.append(piece(R(sx - 10, hz, sw + 20, sy + sh - hz + 10), "#E2C68E", hatch="hl", edge=None, ink=False, filt=None))
    out.append(f'<line x1="{sx}" y1="{hz}" x2="{sx + sw}" y2="{hz}" stroke="{INK}" stroke-opacity=".55" stroke-width="2.5"/>')
    return "\n".join(out), hz


def chat_laptop(x, y, w):
    lap, (ix, iy, iw, ih) = laptop(x, y, w)
    out = [lap]
    rows = [("kid", "make a cat that jumps over cactuses"), ("ai", "Done. Press space to jump."),
            ("kid", "make it jump higher lol"), ("ai", "Jump height doubled. Try it.")]
    bh = (ih - 3 * 14) / 4
    for i, (who, s) in enumerate(rows):
        by = iy + i * (bh + 14)
        bw = iw * (.92 if who == "kid" else .8)
        bx = ix + (iw - bw if who == "kid" else 0)
        fill = TERRA if who == "kid" else EDGE
        out.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{bh / 2:.1f}" fill="{fill}"/>')
        out.append(t(bx + 20, by + bh / 2 + 8, s, min(24, w / 24), EDGE if who == "kid" else INK, TYPE, 400))
    return "\n".join(out)


def poster_vibe():
    W, H = 1800, 2400
    sx, sy, sw, sh = 140, 850, 1520, 800
    b = [strings([(240, 140), (1560, 140)]),
         card(110, 120, 1580, 620),
         f'<g transform="rotate(-2 330 205)">{piece(R(170, 172, 420, 62), OCHRE, hatch="hl", filt="cut")}'
         + t(380, 214, "OPEN TO HOSTS · FREE", 26, INK, TYPE, 400, "middle", 2) + "</g>",
         t(166, 410, "Vibe Coding", 176, INK, SERIF, 900, ls=-4),
         t(166, 575, "Happy Hour", 176, TERRA, SERIF, 900, ls=-4),
         tl(172, 650, ["Kids aged 8 to 14 build their first game with an AI coding agent.",
                       "In two hours. The curriculum is open source."], 30, 40, fill=INK, font=TYPE, weight=400)]
    scene, hz = desert(sx, sy, sw, sh, horizon=.8)
    inner = [scene]
    inner.append(strings([(sx + 120, sy + 140), (sx + 600, sy + 140)]) + chat_laptop(sx + 80, sy + 140, 600))
    # score card
    inner.append(hung_card(sx + 1170, sy + 70, 300, 90, border=False)
                 + t(sx + 1320, sy + 128, "SCORE 0042", 32, INK, TYPE, 400, "middle", 3))
    # jump arc, cactuses, cat on strings
    ax0, ax1, peak = sx + 820, sx + 1420, sy + 250
    inner.append(f'<path d="M{ax0} {hz - 10} Q{(ax0 + ax1) / 2} {peak - 120} {ax1} {hz - 10}" fill="none" stroke="{TEAL_D}" '
                 f'stroke-width="6" stroke-dasharray="3 18" stroke-linecap="round"/>')
    inner.append(cactus(sx + 1090, hz + 6, 1.2) + cactus(sx + 1360, hz + 6, .95))
    cx, cy, p = sx + 1030, sy + 230, 26
    inner.append(strings([(cx + p * .5, cy + 4), (cx + p * 4.5, cy + 4), (cx + p * 7.5, cy + p * 4 + 4)]))
    inner.append(pixel_cat(cx, cy, p))
    b.append(stage(sx, sy, sw, sh, "\n".join(inner), "s2"))
    b.append(ledge(70, sy + sh + 60, 1660))
    facts = [("2 hrs", "one workshop"), ("8–14", "years old"), ("Free", "like everything we run"), ("Open", "source curriculum")]
    for i, (big, small) in enumerate(facts):
        x, rot = 110 + i * 400, (-2, 1.5, -1, 2)[i]
        b.append(f'<g transform="rotate({rot} {x + 180} 1860)">{card(x, 1780, 360, 160, border=False)}'
                 + t(x + 30, 1860, big, 64, TERRA if i % 2 == 0 else TEAL_D, SERIF, 900)
                 + t(x + 32, 1910, small, 23, INK, TYPE, 400) + "</g>" + tape(x + 180, 1782, 90, 28, rot=rot * 2))
    b += [t(110, 2010, "Piloted at a Google office in May 2026.", 27, PAPER, TYPE, 400),
          card(110, 2070, 1180, 220),
          tape(220, 2072), tape(1180, 2072, rot=6),
          t(160, 2160, "Schools: request a free session.", 58, INK, SERIF, 900, ls=-.5),
          t(160, 2250, "csequityai.org", 60, TERRA, SERIF, 900),
          qr_card(1370, 2030, VIBE, "scan for details")]
    write("posters/poster-vibe-coding-happy-hour.svg", doc(W, H, "\n".join(b),
          "Vibe Coding Happy Hour poster: kids 8 to 14 build their first game with an AI coding agent"))


def rope_y(x, y0, x0=40, x1=1760, sag=46):
    u = (x - x0) / (x1 - x0)
    return y0 + sag * 4 * u * (1 - u)


def pin(x, y):
    return piece(R(x - 9, y - 26, 18, 54, 4), WOOD, hatch="hv", edge=None, filt="cut") + \
        f'<line x1="{x - 9}" y1="{y + 4}" x2="{x + 9}" y2="{y + 4}" stroke="{KRAFT_D}" stroke-width="2"/>'


def project_card(x, y, w, h, i, proj, rot):
    name, desc, stack = proj
    cx = x + w / 2
    out = [f'<g transform="rotate({rot} {cx} {y})">', card(x, y, w, h),
           t(x + 44, y + 76, f"No. {i + 1:02d}", 25, TERRA, TYPE, 400, ls=2),
           t(x + 44, y + 140, name, 50 if len(name) < 20 else 46, INK, CJK, 900, ls=-.5),
           tl(x + 44, y + 192, desc, 27, 38, fill=INK, font=TYPE, weight=400)]
    if stack:
        out += [f'<line x1="{x + 44}" y1="{y + h - 80}" x2="{x + w - 44}" y2="{y + h - 80}" stroke="{INK}" stroke-opacity=".35" stroke-dasharray="4 5"/>',
                t(x + 44, y + h - 44, stack, 22, TEAL_D, TYPE, 400)]
    out.append("</g>")
    out += [pin(x + 90, y + 2), pin(x + w - 90, y + 2)]
    return "\n".join(out)


def poster_students():
    W, H = 1800, 2400
    b = [strings([(240, 140), (1560, 140)]),
         card(110, 120, 1580, 420),
         mark(170, 175, 76),
         t(268, 228, "CS Equity AI", 36, INK, SERIF, 900),
         t(166, 390, "Built by students.", 150, INK, SERIF, 900, ls=-4),
         tl(172, 460, ["Six of the AI systems shipped by teams in our last course,",
                       "“The Course of Making AI Tutor for [X].” Real repos, real demos."], 30, 40,
            fill=INK, font=TYPE, weight=400)]
    for row in range(3):
        y0 = 640 + row * 460
        d = f"M40 {y0} Q900 {y0 + 92} 1760 {y0}"
        b.append(f'<path d="{d}" fill="none" stroke="{EDGE}" stroke-opacity=".5" stroke-width="5"/>'
                 f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
        for col in range(2):
            i = row * 2 + col
            x = 110 + col * 810
            y = rope_y(x + 380, y0)
            b.append(project_card(x, y + 6, 760, 380, i, PROJECTS[i], (-1.2, 1.0, .8, -1.4, -.6, 1.3)[i]))
    b += [card(110, 2090, 1180, 270),
          t(160, 2172, "The next course starts Fall 2026.", 58, INK, SERIF, 900, ls=-.5),
          tl(162, 2222, ["The roster is drawn from students who finish", "the free Foundation course. Start it now."],
             26, 34, fill=INK, font=TYPE, weight=400),
          t(160, 2330, "csequityai.org", 56, TERRA, SERIF, 900),
          qr_card(1370, 2060, SITE, "scan to start")]
    write("posters/poster-built-by-students.svg", doc(W, H, "\n".join(b),
          "CS Equity AI poster: six AI systems built by students"))


# ---------------------------------------------------------------- social

def social():
    S = 1080
    # 1. headline over the city stage
    inner = [scenery(100, 90, 880, 520, horizon=.7),
             f'<g transform="rotate(-8 640 300)">{strings([(560, 235)])}{tag(520, 230, 360, 150)}'
             + t(732, 333, "FREE.", 84, EDGE, SERIF, 900, "middle") + "</g>"]
    b = [stage(100, 90, 880, 520, "\n".join(inner), "q1", r=80, thick=36),
         card(60, 680, 960, 360),
         t(110, 770, "We teach students to", 66, INK, SERIF, 900, ls=-1),
         t(110, 846, "build with AI,", 66, INK, SERIF, 900, ls=-1),
         t(110, 922, "not just use it.", 66, TERRA, SERIF, 900, ls=-1),
         t(112, 990, "free courses since 2021 · csequityai.org", 27, INK, TYPE, 400)]
    write("social/square-01-build-with-ai.svg", doc(S, S, "\n".join(b), "We teach students to build with AI, not just use it. Free."))

    # 2. the three levels
    b = [strings([(160, 70), (920, 70)]), card(60, 50, 960, 230),
         t(110, 145, "From first lesson", 66, INK, SERIF, 900, ls=-1),
         t(110, 222, "to founding team.", 66, TERRA, SERIF, 900, ls=-1)]
    for i, (num, lab, title, desc, outcome) in enumerate(LEVELS):
        y = 330 + i * 205
        rot = (-1, 1.2, -.8)[i]
        b.append(f'<g transform="rotate({rot} 540 {y + 80})">{card(90, y, 900, 170)}'
                 + t(140, y + 112, num, 72, TERRA, SERIF, 900)
                 + t(300, y + 64, lab, 19, TEAL_D, TYPE, 400, ls=1.5)
                 + t(300, y + 108, title, 40, INK, SERIF, 900)
                 + t(300, y + 142, "→ " + outcome, 23, INK, TYPE, 400) + "</g>"
                 + tape(540, y + 2, rot=rot * 3))
    b.append(t(540, 1000, "Free, all of it. csequityai.org", 32, PAPER, TYPE, 400, "middle"))
    write("social/square-02-the-path.svg", doc(S, S, "\n".join(b), "From first lesson to founding team: the CS Equity AI path"))

    # 3. Vibe Coding Happy Hour
    scene, hz = desert(100, 90, 880, 520, horizon=.78)
    inner = [scene, cactus(640, hz + 4, .9), cactus(860, hz + 4, .7),
             f'<path d="M520 {hz - 6} Q700 120 900 {hz - 6}" fill="none" stroke="{TEAL_D}" stroke-width="5" stroke-dasharray="3 15" stroke-linecap="round"/>',
             strings([(640, 216), (734, 216)]), pixel_cat(628, 212, 20),
             strings([(180, 160), (440, 160)]), bubble(150, 160, 330, 84, fill=TERRA),
             t(176, 212, "make it jump higher lol", 21, EDGE, TYPE, 400)]
    b = [stage(100, 90, 880, 520, "\n".join(inner), "q3", r=80, thick=36),
         card(60, 680, 960, 360),
         t(110, 772, "Vibe Coding", 78, INK, SERIF, 900, ls=-2),
         t(110, 852, "Happy Hour", 78, TERRA, SERIF, 900, ls=-2),
         tl(112, 912, ["Ages 8–14 build a game with an AI coding agent.", "Two hours, free. Your school can host one."],
            25, 34, fill=INK, font=TYPE, weight=400),
         t(112, 1000, "csequityai.org", 34, TERRA, SERIF, 900)]
    write("social/square-03-vibe-coding.svg", doc(S, S, "\n".join(b), "Vibe Coding Happy Hour: your school can host one"))

    # 4. Facebook cover
    W, H = 1640, 624
    inner = [scenery(70, 62, 1500, 500, horizon=.66),
             hung_card(420, 150, 800, 300),
             t(820, 250, "Build with AI,", 72, INK, SERIF, 900, "middle", -1),
             t(820, 330, "not just use it.", 72, TERRA, SERIF, 900, "middle", -1),
             t(820, 385, "Free CS & AI courses taught by working engineers", 22, INK, TYPE, 400, "middle"),
             t(820, 418, "US · Taiwan · Hong Kong · csequityai.org", 22, TEAL_D, TYPE, 400, "middle")]
    write("social/facebook-cover.svg", doc(W, H, stage(70, 62, 1500, 500, "\n".join(inner), "fc", r=80, thick=40),
                                           "CS Equity AI: build with AI, not just use it"))


# ---------------------------------------------------------------- video

D = 30.0


class Anim:
    def __init__(self):
        self.css, self.n = [], 0

    def _kf(self, frames, dur=D, extra="", timing="ease-in-out", delay=0):
        self.n += 1
        name = f"a{self.n}"
        body = " ".join(f"{100 * tt / dur:.3f}% {{{p}}}" for tt, p in frames)
        self.css.append(f"@keyframes {name} {{{body}}}\n.{name} {{animation: {name} {dur}s {timing} {-delay}s infinite both;{extra}}}")
        return name

    def drop(self, t0, t1, dist=1000):
        up, z = f"transform:translateY({-dist}px)", "transform:translateY(0)"
        return self._kf([(0, up), (t0, up), (t0 + .75, "transform:translateY(16px)"), (t0 + 1.0, "transform:translateY(-6px)"),
                         (t0 + 1.2, z), (t1 - .8, z), (t1, up), (D, up)])

    def rise(self, t0, t1, dist=500):
        dn, z = f"transform:translateY({dist}px)", "transform:translateY(0)"
        return self._kf([(0, dn), (t0, dn), (t0 + .8, z), (t1 - .8, z), (t1, dn), (D, dn)])

    def sway(self, period, deg, ox, oy, phase=0.0):
        return self._kf([(0, f"transform:rotate({-deg}deg)"), (period / 2, f"transform:rotate({deg}deg)"),
                         (period, f"transform:rotate({-deg}deg)")], dur=period, delay=phase,
                        extra=f"transform-origin:{ox}px {oy}px;")

    def spin(self, period, cx, cy, rev=False):
        return self._kf([(0, "transform:rotate(0deg)"), (period, f"transform:rotate({-360 if rev else 360}deg)")],
                        dur=period, timing="linear", extra=f"transform-origin:{cx}px {cy}px;")

    def drift(self, dx, period):
        return self._kf([(0, "transform:translateX(0)"), (period / 2, f"transform:translateX({dx}px)"),
                         (period, "transform:translateX(0)")], dur=period)

    def pop(self, t0, t1=D):
        return self._kf([(0, "transform:scale(0)"), (t0, "transform:scale(0)"), (t0 + .25, "transform:scale(1.2)"),
                         (t0 + .4, "transform:scale(1)"), (t1, "transform:scale(1)"), (D, "transform:scale(1)")],
                        extra="transform-box:fill-box;transform-origin:center;")

    def stamp(self, t0):
        return self._kf([(0, "opacity:0;transform:scale(1.5)"), (t0, "opacity:0;transform:scale(1.5)"),
                         (t0 + .3, "opacity:1;transform:scale(1)"), (D, "opacity:1;transform:scale(1)")],
                        extra="transform-box:fill-box;transform-origin:center;")

    def grow(self, t0, t1):
        return self._kf([(0, "transform:scaleX(0)"), (t0, "transform:scaleX(0)"), (t1, "transform:scaleX(1)"),
                         (D, "transform:scaleX(1)")], extra="transform-box:fill-box;transform-origin:left center;")

    def draw(self, t0, t1, length):
        return self._kf([(0, f"stroke-dashoffset:{length}"), (t0, f"stroke-dashoffset:{length}"),
                         (t1, "stroke-dashoffset:0"), (D, "stroke-dashoffset:0")])

    def tint(self, t0, t1, a, b):
        return self._kf([(0, f"fill:{a}"), (t0, f"fill:{a}"), (t0 + .3, f"fill:{b}"), (t1 - .3, f"fill:{b}"),
                         (t1, f"fill:{a}"), (D, f"fill:{a}")])


def G(cls, inner):
    return f'<g class="{cls}">{inner}</g>'


def puppet(A, t0, t1, inner, ox, oy, period=6, deg=1.2, phase=0.0):
    """A flat that drops in on strings, sways while it hangs, and is pulled back up."""
    return G(A.drop(t0, t1), G(A.sway(period, deg, ox, oy, phase), inner))


def text_flat(A, t0, t1, num, lab, title, body, size=62):
    x, y, w, h = 190, 130, 840, 470
    inner = "\n".join([hung_card(x, y, w, h),
                       t(x + 50, y + 110, num, 74, TERRA, SERIF, 900),
                       t(x + 50, y + 160, lab, 25, TEAL_D, TYPE, 400, ls=2),
                       t(x + 48, y + 235, title, size, INK, SERIF, 900, ls=-1),
                       tl(x + 50, y + 300, body, 29, 42, fill=INK, font=TYPE, weight=400)])
    return puppet(A, t0, t1, inner, x + w / 2, -400, 6, .8)


def video():
    W, H = 1920, 1080
    sx, sy, sw, sh = 130, 66, 1660, 800
    A = Anim()
    clouds = (A.drift(60, 15), A.drift(-40, 10), A.drift(50, 7.5))
    inner = [scenery(sx, sy, sw, sh, horizon=.6, cloud_cls=clouds)]

    # S1 0–5: the hook
    s1 = "\n".join([hung_card(330, 150, 1260, 420),
                    t(960, 290, "Plenty of students use AI.", 78, INK, SERIF, 900, "middle", -1),
                    G(A.stamp(1.7), t(960, 450, "Ours build it.", 132, TERRA, SERIF, 900, "middle", -2)),
                    t(960, 520, "CS Equity AI · free CS & AI courses since 2021", 26, INK, TYPE, 400, "middle")])
    inner.append(puppet(A, .2, 5.1, s1, 960, -400, 6, .7))

    # S2 5–11: Capability
    inner.append(text_flat(A, 5.3, 11.1, "i.", "LEVEL 1 · CAPABILITY", "Learn the essentials",
                           ["Free, self-paced Foundation course", "on the OpenImpact Lab. Runs in the",
                            "browser. No setup, no installs."]))
    lap, (ix, iy, iw, ih) = laptop(1180, 200, 520)
    rows = []
    for i, label in enumerate(["CS fundamentals", "AI fundamentals", "Hands-on labs"]):
        yy = iy + 20 + i * 70
        rows.append(f'<rect x="{ix + 6}" y="{yy}" width="34" height="34" rx="6" fill="none" stroke="{EDGE}" stroke-width="3"/>'
                    + G(A.pop(6.9 + i * .8), f'<path d="M{ix + 13} {yy + 18} l8 8 l14 -18" fill="none" stroke="{OCHRE}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
                    + t(ix + 60, yy + 27, label, 28, EDGE, TYPE, 400))
    rows.append(f'<rect x="{ix + 6}" y="{iy + ih - 34}" width="{iw - 12}" height="16" rx="8" fill="{EDGE}" fill-opacity=".25"/>'
                f'<rect class="{A.grow(6.7, 9.2)}" x="{ix + 6}" y="{iy + ih - 34}" width="{iw - 12}" height="16" rx="8" fill="{OCHRE}"/>')
    inner.append(puppet(A, 5.7, 11.1, strings([(1230, 204), (1650, 204)]) + lap + "\n".join(rows), 1440, -400, 5, 1.2, 1))
    inner.append(puppet(A, 9.3, 11.1, strings([(1640, 520)]) + rosette(1640, 600, 82), 1640, -300, 3, 1.2))

    # S3 11–18: Creation
    inner.append(text_flat(A, 11.3, 18.1, "ii.", "LEVEL 2 · CREATION", "Build a real AI system",
                           ["Weekly live sessions in small teams,", "taught by engineers from Google",
                            "and academia."], size=58))
    gears = (f'<g class="{A.spin(6, 1690, 760)}">{gear(1690, 760, 95, 12, OCHRE)}</g>'
             f'<g class="{A.spin(4.5, 1543, 800, rev=True)}">{gear(1543, 800, 62, 8, SLATE)}</g>')
    inner.append(G(A.rise(11.6, 18.1), gears))
    tags = [("AI 菜單推薦系統", "Menu photo in, waiter-style picks out"),
            ("Smart Travel Agent", "Curates attractions, writes the itinerary"),
            ("Cooking Assistant Agent", "Walks you through any recipe")]
    for i in reversed(range(3)):
        x, y = 1150 + (i % 2) * 40, 150 + i * 150
        n, d = tags[i]
        body = (hung_card(x, y, 520, 118, border=False)
                + t(x + 30, y + 52, n, 34, INK, CJK, 900) + t(x + 30, y + 90, d, 21, INK, TYPE, 400))
        inner.append(puppet(A, 13.0 + i * .7, 18.1, body, x + 260, -400, 5, 1.4, i))

    # S4 18–23: Capital
    inner.append(text_flat(A, 18.3, 23.1, "iii.", "LEVEL 3 · CAPITAL", "Pitch it",
                           ["A founding team of three to five", "takes what they built in front of",
                            "angel investors."]))
    board = [hung_card(1180, 140, 500, 320),
             t(1220, 210, "Investor pitch", 36, INK, SERIF, 900),
             t(1220, 245, "a student team · AI travel agent", 20, INK, TYPE, 400),
             f'<line x1="1220" y1="420" x2="1640" y2="420" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>',
             f'<polyline class="{A.draw(19.4, 21.0, 600)}" points="1230,405 1320,380 1400,350 1480,340 1560,300 1630,270" '
             f'fill="none" stroke="{TERRA}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="600"/>']
    inner.append(puppet(A, 18.6, 23.1, "\n".join(board), 1430, -400, 6, .9, 2))
    for i, col in enumerate([TERRA, TEAL, OCHRE, SLATE]):
        px = 1250 + i * 120
        body = strings([(px, 700)]) + person(px, 860, col, 1.0)
        inner.append(puppet(A, 19.0 + i * .2, 23.1, body, px, -300, 2.5, 1.0, i * .6))

    # S5 23–26.6: free
    big = (strings([(640, 350)]) + tag(600, 220, 760, 260)
           + t(1020, 375, "$0", 150, EDGE, SERIF, 900, "middle", -4)
           + t(1250, 400, "tuition.", 38, EDGE, TYPE, 400, "end") + t(1250, 440, "ever.", 38, EDGE, TYPE, 400, "end"))
    inner.append(puppet(A, 23.3, 26.7, big, 640, -300, 3, 2.5))
    cap = hung_card(470, 560, 980, 100, border=False) + t(960, 622, "Students in the US, Taiwan and Hong Kong, since 2021.",
                                                           29, INK, TYPE, 400, "middle")
    inner.append(puppet(A, 23.9, 26.7, cap, 960, -400, 5, .5))

    # S6 26.6–30: call to action
    end = "\n".join([hung_card(360, 300, 1200, 380),
                     t(960, 410, "Start with the free Foundation course.", 58, INK, SERIF, 900, "middle", -1),
                     t(960, 540, "csequityai.org", 104, TERRA, SERIF, 900, "middle", -2),
                     t(960, 610, "The Fall 2026 roster is drawn from students who finish it.", 26, INK, TYPE, 400, "middle")])
    inner.append(puppet(A, 26.8, 29.9, end, 960, -400, 6, .6))
    inner.append(puppet(A, 26.6, 29.9, strings([(960, 120)]) + mark(885, 110, 150), 960, -300, 4, .8))

    out = [stage(sx, sy, sw, sh, "\n".join(inner), "vs"),
           ledge(60, 930, 1800, 40),
           card(130, 996, 520, 66, border=False), mark(146, 1004, 50),
           t(212, 1040, "CS Equity AI · csequityai.org", 26, INK, TYPE, 400)]
    steps = [("i. Capability", 5.3, 11.1), ("ii. Creation", 11.3, 18.1), ("iii. Capital", 18.3, 23.1)]
    for i, (lab, a, z) in enumerate(steps):
        out.append(f'<text class="{A.tint(a, z, PAPER, OCHRE)}" x="{1090 + i * 250}" y="1040" font-family="{TYPE}" '
                   f'font-size="27" fill="{PAPER}">{lab}</text>')
    css = "\n".join(A.css)
    write("video/demo.svg", doc(W, H, "\n".join(out), "CS Equity AI: 30-second demo of what we do", css))


def brand():
    def logo(w, h, body, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                f'aria-label="{title}"><title>{title}</title>{defs()}{body}</svg>\n')
    write("brand/logo-mark.svg", logo(160, 160, mark(20, 16, 120), "CS Equity AI mark"))
    write("brand/logo-horizontal.svg", logo(620, 160, mark(20, 16, 120)
          + t(170, 88, "CS Equity AI", 58, INK, SERIF, 900, ls=-1)
          + t(172, 124, "csequityai.org", 24, TEAL_D, TYPE, 400, ls=1), "CS Equity AI"))


if __name__ == "__main__":
    brand()
    poster_main()
    poster_vibe()
    poster_students()
    social()
    video()
