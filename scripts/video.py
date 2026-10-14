"""The paper-theater demo video, timed to its own text and cut on the music's bars.

Each beat lists the text it shows. Its length is the time a viewer needs to read that
text (READ_CPS characters per second, plus LEAD seconds to spot it; small labels marked
"~" count half because they are scanned, not read), rounded up to whole
half-bars at BPM so every scene change lands on the beat of the soundtrack.
"""
import math

from paper import *  # noqa: F401,F403
from build import hung_card, stage, PROJECTS

BPM = 128
BAR = 240 / BPM            # 1.875 s
HALF = BAR / 2
READ_CPS = 15              # subtitle reading speed, chars/sec (guides: ~13 for kids, ~17 for adults)
LEAD = 1.4                 # seconds to land, settle and find the text
INTRO_BARS, OUTRO_BARS = 2, 2

SX, SY, SW, SH = 130, 66, 1660, 800
D = 60.0                   # replaced by the schedule in video()


class Anim:
    def __init__(self):
        self.css, self.n = [], 0

    def kf(self, frames, dur=None, extra="", timing="cubic-bezier(.3,.6,.35,1)", delay=0.0):
        dur = dur or D
        self.n += 1
        name = f"a{self.n}"
        body = " ".join(f"{max(0, min(100, 100 * tt / dur)):.3f}% {{{p}}}" for tt, p in frames)
        self.css.append(f"@keyframes {name} {{{body}}}\n.{name} {{animation:{name} {dur}s {timing} {-delay}s infinite both;{extra}}}")
        return name

    # Every entrance lands exactly at t0; every exit is finished by t1 - .3.
    def drop(self, t0, t1, dist=1100):
        s, e = t0 - .32, t1 - .3
        up, z = f"transform:translateY({-dist}px)", "transform:translateY(0)"
        return self.kf([(0, up), (s, up), (t0, "transform:translateY(22px)"), (t0 + .14, "transform:translateY(-8px)"),
                        (t0 + .26, z), (e - .35, z), (e, up), (D, up)])

    def whip(self, t0, t1, dx):
        s, e = t0 - .28, t1 - .3
        off, z, up = f"transform:translate({dx}px,0)", "transform:translate(0,0)", "transform:translate(0,-1100px)"
        ov = f"transform:translate({-26 if dx > 0 else 26}px,0)"
        return self.kf([(0, off), (s, off), (t0, ov), (t0 + .14, z), (e - .35, z), (e, up), (D, up)])

    def slam(self, t0, t1):
        s, e = t0 - .16, t1 - .3
        a, b = "opacity:0;transform:scale(2.4) rotate(-8deg)", "opacity:1;transform:scale(1) rotate(0deg)"
        c = "opacity:0;transform:scale(.4) rotate(0deg)"
        return self.kf([(0, a), (s, a), (t0, "opacity:1;transform:scale(.9) rotate(2deg)"), (t0 + .14, b),
                        (e - .25, b), (e, c), (D, c)], extra="transform-box:fill-box;transform-origin:center;")

    def pop(self, t0):
        return self.kf([(0, "transform:scale(0)"), (t0, "transform:scale(0)"), (t0 + .2, "transform:scale(1.18)"),
                        (t0 + .32, "transform:scale(1)"), (D, "transform:scale(1)")],
                       extra="transform-box:fill-box;transform-origin:center;")

    def show(self, t0, t1):
        return self.kf([(0, "opacity:0"), (t0, "opacity:0"), (t0 + .15, "opacity:1"), (t1 - .15, "opacity:1"),
                        (t1, "opacity:0"), (D, "opacity:0")])

    def sway(self, period, deg, ox, oy, phase=0.0):
        return self.kf([(0, f"transform:rotate({-deg}deg)"), (period / 2, f"transform:rotate({deg}deg)"),
                        (period, f"transform:rotate({-deg}deg)")], dur=period, delay=phase, timing="ease-in-out",
                       extra=f"transform-origin:{ox}px {oy}px;")

    def spin(self, period, cx, cy):
        return self.kf([(0, "transform:rotate(0deg)"), (period, "transform:rotate(360deg)")],
                       dur=period, timing="linear", extra=f"transform-origin:{cx}px {cy}px;")

    def loop(self, frames, period, timing="linear"):
        return self.kf(frames, dur=period, timing=timing)

    def grow(self, t0, t1):
        return self.kf([(0, "transform:scaleX(0)"), (t0, "transform:scaleX(0)"), (t1, "transform:scaleX(1)"),
                        (D, "transform:scaleX(1)")], extra="transform-box:fill-box;transform-origin:left center;")

    def draw(self, t0, t1, length):
        return self.kf([(0, f"stroke-dashoffset:{length}"), (t0, f"stroke-dashoffset:{length}"),
                        (t1, "stroke-dashoffset:0"), (D, "stroke-dashoffset:0")])

    def curtain(self, t_open, t_close, dx):
        c, o = "transform:translateX(0)", f"transform:translateX({dx}px)"
        return self.kf([(0, c), (t_open, c), (t_open + .75, o), (t_close, o), (t_close + .75, c), (D, c)],
                       timing="cubic-bezier(.6,0,.3,1)")


def G(cls, inner):
    return f'<g class="{cls}">{inner}</g>'


def hang(A, t0, t1, inner, ox, period=3.75, deg=.7, phase=0.0, enter=None):
    """A flat that drops (or whips) in on strings, sways while it hangs, and is yanked back up."""
    move = A.whip(t0, t1, enter) if enter else A.drop(t0, t1)
    return G(move, G(A.sway(period, deg, ox, -500, phase), inner))


def info(A, t0, t1, kicker, title, body):
    x, y, w, h = 180, 150, 820, 440
    inner = "\n".join([hung_card(x, y, w, h),
                       t(x + 50, y + 85, kicker, 24, TEAL_D, TYPE, 400, ls=2),
                       tl(x + 48, y + 170, title, 70, 80, fill=INK, font=SERIF, weight=900, ls=-1.5),
                       tl(x + 50, y + 185 + 80 * len(title), body, 31, 44, fill=INK, font=TYPE, weight=400)])
    return hang(A, t0, t1, inner, x + w / 2)


def small_tag(x, y, w, label):
    h = 70
    return "\n".join([hung_card(x, y, w, h, border=False),
                      piece(P(poly([(x + w / 2 - 18, y + h - 4), (x + w / 2 + 18, y + h - 4), (x + w / 2, y + h + 30)])),
                            PAPER, hatch=None, edge=None, ink=False, filt="cut"),
                      t(x + w / 2, y + 47, label, 32, INK, SERIF, 900, "middle", 1)])


def curtains(A, t_open, t_close):
    half = SW / 2 + 30
    out = []
    for side, x0 in (("l", SX - 10), ("r", SX + SW / 2 - 20)):
        g = [piece(R(x0, SY - 20, half, SH + 40), TERRA, hatch="hv", edge=None, ink=False, filt="cut2")]
        g += [f'<rect x="{x0 + i * half / 10:.1f}" y="{SY - 20}" width="{half / 10:.1f}" height="{SH + 40}" '
              f'fill="#7A3E2C" fill-opacity=".28"/>' for i in range(1, 10, 2)]
        g.append(f'<rect x="{x0}" y="{SY + SH - 40}" width="{half}" height="22" fill="{OCHRE}"/>')
        g.append("".join(f'<circle cx="{x0 + 20 + k * 40}" cy="{SY + SH - 10}" r="9" fill="{OCHRE}" '
                         f'stroke="{BRASS_D}" stroke-width="2"/>' for k in range(int(half // 40))))
        out.append(G(A.curtain(t_open, t_close, -(half + 60) if side == "l" else half + 60), "".join(g)))
    return "\n".join(out)


def valance():
    n, top, depth = 14, SY - 10, 64
    sw = (SW + 40) / n
    d = f"M{SX - 20} {top} H{SX + SW + 20} V{top + depth} "
    for i in range(n):
        d += f"A{sw / 2:.1f} {sw / 2.6:.1f} 0 0 1 {SX + SW + 20 - (i + 1) * sw:.1f} {top + depth} "
    return (piece(P(d + "Z"), "#A85A44", hatch="hv", edge=None, filt="cut2")
            + f'<line x1="{SX}" y1="{top + 18}" x2="{SX + SW}" y2="{top + 18}" stroke="{OCHRE}" stroke-width="6"/>')


# ---------------------------------------------------------------- beats
# Each beat: (ticker label, texts shown, builder(A, t0, t1) -> svg)

def b_title(A, t0, t1):
    out = []
    for i, (w_, col) in enumerate((("LEARN.", INK), ("BUILD.", TERRA), ("SHIP.", TEAL_D))):
        x = 240 + i * 490
        out.append(G(A.slam(t0 + i * BEAT, t1), card(x, 220, 450, 250) + t(x + 225, 385, w_, 118, col, SERIF, 900, "middle", -3)))
    out.append(hang(A, t0 + 3 * BEAT, t1, hung_card(560, 540, 800, 90, border=False)
                    + t(960, 598, "Free CS & AI courses since 2021", 32, INK, TYPE, 400, "middle"), 960))
    return "\n".join(out)


def b_mission(A, t0, t1):
    return (hang(A, t0, t1, "\n".join([
        hung_card(260, 150, 1240, 470),
        t(320, 270, "We teach students to", 66, INK, SERIF, 900, ls=-1),
        t(320, 390, "build with AI,", 112, INK, SERIF, 900, ls=-3),
        t(320, 510, "not just use it.", 112, TERRA, SERIF, 900, ls=-3)]), 880)
        + hang(A, t0 + 2 * BEAT, t1, f'<g transform="rotate(-10 1550 590)">{strings([(1420, 590)])}{tag(1380, 520, 380, 150)}'
               + t(1590, 620, "FREE.", 84, EDGE, SERIF, 900, "middle") + "</g>", 1420, 1.875, 3, enter=900))


def b_where(A, t0, t1):
    out = [hang(A, t0 + i * BEAT, t1, small_tag(x, 260 + (i % 2) * 40, w_, lab), x + w_ / 2, 1.875, 2.5, i * .4)
           for i, (x, w_, lab) in enumerate(((410, 170, "USA"), (1080, 260, "HONG KONG"), (1440, 210, "TAIWAN")))]
    out.append(hang(A, t0 + 3 * BEAT, t1, hung_card(330, 600, 1260, 190)
                    + t(960, 680, "Live online courses, taught by engineers", 50, INK, SERIF, 900, "middle", -1)
                    + t(960, 745, "from Google and academia.", 50, TERRA, SERIF, 900, "middle", -1), 960))
    return "\n".join(out)


def b_lab(A, t0, t1):
    bx, by = 1080, 160
    lab = [hung_card(bx, by, 660, 450, border=False),
           f'<rect x="{bx + 20}" y="{by + 20}" width="620" height="54" rx="10" fill="#E2D7BD"/>',
           "".join(f'<circle cx="{bx + 50 + k * 26}" cy="{by + 47}" r="8" fill="{c}"/>' for k, c in enumerate((TERRA, OCHRE, TEAL))),
           f'<rect x="{bx + 140}" y="{by + 30}" width="420" height="34" rx="17" fill="{EDGE}"/>',
           t(bx + 350, by + 55, "OpenImpact Lab", 22, INK, TYPE, 400, "middle")]
    for k, lesson in enumerate(["AI & CS fundamentals", "Hands-on labs", "Foundation course"]):
        yy = by + 110 + k * 82
        lab.append(f'<rect x="{bx + 40}" y="{yy}" width="580" height="64" rx="10" fill="{EDGE}" stroke="{INK}" stroke-opacity=".25"/>'
                   f'<rect x="{bx + 60}" y="{yy + 15}" width="34" height="34" rx="6" fill="none" stroke="{INK}" stroke-width="3"/>'
                   + G(A.pop(t0 + (2 + 2 * k) * BEAT), f'<path d="M{bx + 66} {yy + 33} l8 9 l16 -20" fill="none" stroke="{TERRA}" '
                       f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
                   + t(bx + 116, yy + 42, lesson, 28, INK, TYPE, 400))
    lab.append(f'<rect x="{bx + 40}" y="{by + 370}" width="580" height="22" rx="11" fill="#E2D7BD"/>'
               f'<rect class="{A.grow(t0 + BEAT, t0 + 7 * BEAT)}" x="{bx + 40}" y="{by + 370}" width="580" height="22" rx="11" fill="{TEAL_D}"/>')
    return (info(A, t0, t1, "LEVEL 1 · CAPABILITY", ["Start on the", "OpenImpact Lab."],
                 ["Free and self-paced, right in", "the browser."])
            + hang(A, t0 + BEAT, t1, "\n".join(lab), bx + 330, 3.75, .8, 2)
            + G(A.slam(t0 + 8 * BEAT, t1), rosette(1650, 630, 100)))


def b_projects(A, t0, t1):
    out = [hang(A, t0, t1, hung_card(500, 175, 920, 120)
                + t(960, 239, "Built by students.", 62, INK, SERIF, 900, "middle", -1)
                + t(960, 277, "LEVEL 2 · CREATION · six AI systems from our last course", 22, TEAL_D, TYPE, 400, "middle", 1), 960)]
    for i, (name, _, _) in enumerate(PROJECTS):
        col, row = i % 2, i // 2
        x, y = (200, 1020)[col], 340 + row * 140
        body = (hung_card(x, y, 700, 104, border=False)
                + t(x + 36, y + 66, f"{i + 1:02d}", 28, TERRA, TYPE, 400, ls=2)
                + t(x + 100, y + 68, name, 42 if len(name) < 20 else 38, INK, CJK, 900))
        out.append(hang(A, t0 + (2 + i) * BEAT, t1, body, x + 350, 2.5, 1, i * .3, enter=-1500 if col == 0 else 1500))
    return "\n".join(out)


def b_mle(A, t0, t1):
    cx, cy = 1390, 450
    ring = [f'<g class="{A.spin(7.5, cx, cy)}"><circle cx="{cx}" cy="{cy}" r="210" fill="none" stroke="{EDGE}" stroke-width="12" '
            f'stroke-dasharray="26 18"/><circle cx="{cx}" cy="{cy}" r="210" fill="none" stroke="{INK}" stroke-width="4" '
            f'stroke-dasharray="26 18"/></g>',
            G(A.spin(1.875, cx, cy), piece(C(cx, cy - 210, 26), OCHRE, hatch="hx", filt="cut2")),
            card(cx - 130, cy - 70, 260, 140, border=False),
            t(cx, cy + 6, "8 WEEKS", 54, TERRA, SERIF, 900, "middle", -1),
            t(cx, cy + 46, "of open materials", 20, INK, TYPE, 400, "middle")]
    for k, (lab_, dx, dy) in enumerate((("read the problem", -190, -165), ("write code", 210, -165), ("test it", 210, 165),
                                        ("refine on failure", -190, 165))):
        w_ = len(lab_) * 16 + 60
        nx, ny = cx + dx - w_ / 2, cy + dy - 38
        ring.append(G(A.pop(t0 + (2 + 2 * k) * BEAT), card(nx, ny, w_, 76, border=False)
                      + t(nx + w_ / 2, ny + 50, lab_, 28, INK, TYPE, 400, "middle")))
    return (info(A, t0, t1, "NOW RUNNING · MLE-STAR BOOTCAMP", ["Eight weeks of", "autonomous LLMs."],
                 ["Slides and problem sets are open."])
            + G(A.drop(t0 + BEAT, t1), "\n".join(ring)))


def b_vibe(A, t0, t1):
    lap, (ix, iy, iw, ih) = laptop(1120, 160, 600)
    gy = iy + ih - 50
    period = BAR * 2 / 3          # three jumps every two bars
    run = A.loop([(0, "transform:translateX(0)"), (period, f"transform:translateX({-iw - 120}px)")], period)
    jump = A.loop([(0, "transform:translateY(0)"), (period * .33, "transform:translateY(0)"),
                   (period * .58, "transform:translateY(-130px)"), (period * .83, "transform:translateY(0)"),
                   (period, "transform:translateY(0)")], period, "ease-in-out")
    game = [lap, f'<clipPath id="scr"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="6"/></clipPath>',
            f'<g clip-path="url(#scr)"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="{SKY}"/>'
            f'<rect x="{ix}" y="{gy}" width="{iw}" height="60" fill="#E2C68E"/>'
            f'<line x1="{ix}" y1="{gy}" x2="{ix + iw}" y2="{gy}" stroke="{INK}" stroke-width="3"/>'
            + G(run, cactus(ix + iw + 40, gy + 2, .62)) + G(jump, pixel_cat(ix + 120, gy - 98, 14))
            + t(ix + iw - 16, iy + 34, "SCORE 0042", 22, INK, TYPE, 400, "end", 2) + "</g>"]
    return (info(A, t0, t1, "VIBE CODING HAPPY HOUR · AGES 8–14", ["Their first game,", "in two hours."],
                 ["Kids build it with an AI coding", "agent. Free for schools."])
            + hang(A, t0 + BEAT, t1, strings([(1180, 164), (1660, 164)]) + "\n".join(game), 1420, 3.75, .6, 1)
            + G(A.slam(t0 + 5 * BEAT, t1), bubble(1110, 620, 430, 78, fill=TERRA) + t(1140, 670, "make it jump higher lol", 26, EDGE, TYPE, 400))
            + G(A.slam(t0 + 8 * BEAT, t1), bubble(1290, 730, 450, 78, tail="right") + t(1316, 780, "Jump height doubled. Try it.", 26, INK, TYPE, 400)))


def b_pitch(A, t0, t1):
    board = [hung_card(1150, 160, 560, 330),
             t(1190, 235, "Investor pitch", 40, INK, SERIF, 900),
             t(1190, 272, "a student team · AI travel agent", 20, INK, TYPE, 400),
             f'<line x1="1190" y1="450" x2="1670" y2="450" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>',
             f'<polyline class="{A.draw(t0 + 2 * BEAT, t0 + 6 * BEAT, 700)}" points="1200,435 1300,410 1390,375 1480,365 1570,320 1660,285" '
             f'fill="none" stroke="{TERRA}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="700"/>']
    out = [info(A, t0, t1, "LEVEL 3 · CAPITAL", ["Then pitch it."],
                ["A founding team of three to five", "takes what they built to angel", "investors."]),
           hang(A, t0 + BEAT, t1, "\n".join(board), 1430)]
    for i, col in enumerate((TERRA, TEAL, OCHRE, SLATE)):
        px = 1230 + i * 130
        bob = A.loop([(0, "transform:translateY(0)"), (BEAT / 2, "transform:translateY(-20px)"), (BEAT, "transform:translateY(0)")],
                     BEAT, "ease-in-out")
        out.append(G(A.drop(t0 + (2 + i * .5) * BEAT, t1), f'<g class="{bob}">{strings([(px, 700)])}{person(px, 850, col, 1.0)}</g>'))
    return "\n".join(out)


RUNS = [("2021", ["Android on", "the Cloud"]), ("2023", ["A Beginner’s", "Guide to AI"]), ("2024", ["Gen AI", "Bootcamp"]),
        ("2024–25", ["AI Tutor", "for [X]"]), ("2026", ["Vibe Coding", "Happy Hour"]), ("now", ["MLE-STAR", "Bootcamp"]),
        ("fall 2026", ["The next", "course"])]


def b_programs(A, t0, t1):
    out = [hang(A, t0, t1, hung_card(460, 172, 1000, 100) + t(960, 242, "Free programs since 2021", 60, INK, SERIF, 900, "middle", -1), 960)]
    for i, (yr, name) in enumerate(RUNS):
        row, k = (0, i) if i < 4 else (1, i - 4)
        x, y = ((210 + k * 385), 310) if row == 0 else ((405 + k * 385), 500)
        body = (card(x, y, 350, 165, fill=OCHRE if yr == "fall 2026" else PAPER, border=False)
                + t(x + 26, y + 46, yr.upper(), 24, TERRA, TYPE, 400, ls=2) + tl(x + 26, y + 96, name, 36, 40, fill=INK, font=SERIF, weight=900))
        out.append(G(A.slam(t0 + (2 + i) * BEAT, t1), body))
    return "\n".join(out)


def b_zero(A, t0, t1):
    return (G(A.slam(t0, t1), G(A.sway(1.875, 3, 640, 360), strings([(640, 360)]) + tag(600, 230, 760, 260)
              + t(1010, 385, "$0", 160, EDGE, SERIF, 900, "middle", -4)
              + t(1300, 410, "tuition.", 40, EDGE, TYPE, 400, "end") + t(1300, 452, "ever.", 40, EDGE, TYPE, 400, "end")))
            + hang(A, t0 + 2 * BEAT, t1, hung_card(410, 590, 1100, 100, border=False)
                   + t(960, 652, "No tuition, no gatekeeping. Just a browser and curiosity.", 29, INK, TYPE, 400, "middle"), 960))


def b_cta(A, t0, t1):
    return (hang(A, t0, t1, strings([(960, 110)]) + mark(885, 120, 150), 960, 1.875, 1.5)
            + hang(A, t0 + BEAT, t1, "\n".join([hung_card(330, 310, 1260, 400),
                                               t(960, 415, "Start with the free Foundation course.", 60, INK, SERIF, 900, "middle", -1),
                                               t(960, 550, "csequityai.org", 112, TERRA, SERIF, 900, "middle", -2),
                                               t(960, 630, "The Fall 2026 roster is drawn from students who finish it.", 28, INK, TYPE, 400, "middle")]), 960))


BEAT = 60 / BPM
BEATS = [
    ("", ["LEARN.", "BUILD.", "SHIP.", "Free CS & AI courses since 2021"], b_title),
    ("", ["We teach students to", "build with AI,", "not just use it.", "FREE."], b_mission),
    ("where we teach", ["~USA", "~HONG KONG", "~TAIWAN", "Live online courses, taught by engineers", "from Google and academia."], b_where),
    ("level 1 · capability", ["~LEVEL 1 · CAPABILITY", "Start on the OpenImpact Lab.", "Free and self-paced, right in the browser.",
                              "~AI & CS fundamentals", "~Hands-on labs", "~Foundation course",
                              "~FOUNDATION CERTIFICATE"], b_lab),
    ("level 2 · creation", ["Built by students.", "~LEVEL 2 · CREATION · six AI systems from our last course"] + [p[0] for p in PROJECTS], b_projects),
    ("running now", ["~NOW RUNNING · MLE-STAR BOOTCAMP", "Eight weeks of autonomous LLMs.",
                     "Slides and problem sets are open.",
                     "~read the problem", "~write code", "~test it", "~refine on failure", "~8 WEEKS"], b_mle),
    ("workshops", ["~VIBE CODING HAPPY HOUR · AGES 8–14", "Their first game, in two hours.",
                   "Kids build it with an AI coding agent. Free for schools.",
                   "make it jump higher lol", "Jump height doubled. Try it."], b_vibe),
    ("level 3 · capital", ["~LEVEL 3 · CAPITAL", "Then pitch it.", "A founding team of three to five takes what they built to angel investors.",
                           "~Investor pitch"], b_pitch),
    ("since 2021", ["Free programs since 2021"] + [" ".join(n) for _, n in RUNS] + [f"~{y}" for y, _ in RUNS], b_programs),
    ("free, always", ["$0 tuition. ever.", "No tuition, no gatekeeping. Just a browser and curiosity."], b_zero),
    ("csequityai.org", ["Start with the free Foundation course.", "csequityai.org",
                        "The Fall 2026 roster is drawn from students who finish it."], b_cta),
]


def schedule():
    """Start time of each beat, plus the total length. Everything lands on a half-bar."""
    t0, out = INTRO_BARS * BAR, []
    for label, texts, fn in BEATS:
        # Labels marked "~" are glanced at rather than read, so they count half.
        chars = sum(len(s) / 2 if s.startswith("~") else len(s) for s in texts)
        need = LEAD + chars / READ_CPS
        dur = math.ceil(need / HALF) * HALF
        out.append((t0, t0 + dur, label, fn, chars, need))
        t0 += dur
    total = math.ceil((t0 + OUTRO_BARS * BAR) / BAR) * BAR
    return out, total


def video():
    global D
    plan, D = schedule()
    A = Anim()
    clouds = tuple(A.loop([(0, "transform:translateX(0)"), (p / 2, f"transform:translateX({dx}px)"), (p, "transform:translateX(0)")],
                          p, "ease-in-out") for dx, p in ((90, 15), (-70, 7.5), (60, 3.75)))
    S = [scenery(SX, SY, SW, SH, horizon=.6, cloud_cls=clouds)]
    for i, (a, z, _, fn, _, _) in enumerate(plan):
        last = i == len(plan) - 1
        S.append(fn(A, a, D + .3 if last else z))
    S.append(valance())
    t_open, t_close = BAR * .6, D - BAR * .9
    S.append(curtains(A, t_open, t_close))
    title = A.kf([(0, "opacity:1;transform:translateY(0)"), (t_open - .1, "opacity:1;transform:translateY(0)"),
                  (t_open + .25, "opacity:0;transform:translateY(-500px)"), (D - .45, "opacity:0;transform:translateY(-500px)"),
                  (D - .05, "opacity:1;transform:translateY(0)"), (D, "opacity:1;transform:translateY(0)")])
    S.append(G(title, strings([(760, 330), (1160, 330)]) + card(660, 330, 600, 230)
               + mark(700, 375, 140) + t(870, 450, "CS Equity AI", 52, INK, SERIF, 900)
               + t(872, 495, "presents", 26, TERRA, TYPE, 400, ls=2)))
    out = [stage(SX, SY, SW, SH, "\n".join(S), "vs"), ledge(60, 930, 1800, 40),
           card(130, 996, 520, 66, border=False), mark(146, 1004, 50),
           t(212, 1040, "CS Equity AI · csequityai.org", 26, INK, TYPE, 400)]
    for a, z, label, _, _, _ in plan:
        if label:
            out.append(G(A.show(a - .2, z - .2), t(1790, 1040, label.upper(), 27, OCHRE, TYPE, 400, "end", 3)))
    svg = doc(1920, 1080, "\n".join(out), "CS Equity AI: demo of what we do", "\n".join(A.css))
    return svg.replace("<svg ", f'<svg data-duration="{D}" ', 1), plan, D


if __name__ == "__main__":
    plan, total = schedule()
    for a, z, label, fn, chars, need in plan:
        print(f"{fn.__name__:12s} {a:6.2f}–{z:6.2f}  {z - a:5.2f}s  ({chars} chars, needs {need:.1f}s)")
    print(f"total {total:.2f}s")
