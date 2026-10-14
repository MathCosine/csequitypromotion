"""The 36-second paper-theater demo: fast cuts, everything on strings."""
from paper import *  # noqa: F401,F403
from build import hung_card, stage, PROJECTS

D = 36.0
SX, SY, SW, SH = 130, 66, 1660, 800


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

    def drop(self, t0, t1, dist=1100):
        up, z = f"transform:translateY({-dist}px)", "transform:translateY(0)"
        return self.kf([(0, up), (t0, up), (t0 + .32, "transform:translateY(22px)"), (t0 + .46, "transform:translateY(-8px)"),
                        (t0 + .58, z), (t1 - .35, z), (t1, up), (D, up)])

    def whip(self, t0, t1, dx):
        off, z, up = f"transform:translate({dx}px,0)", "transform:translate(0,0)", "transform:translate(0,-1100px)"
        ov = f"transform:translate({-26 if dx > 0 else 26}px,0)"
        return self.kf([(0, off), (t0, off), (t0 + .28, ov), (t0 + .42, z), (t1 - .35, z), (t1, up), (D, up)])

    def slam(self, t0, t1):
        a = "opacity:0;transform:scale(2.4) rotate(-8deg)"
        b = "opacity:1;transform:scale(1) rotate(0deg)"
        c = "opacity:0;transform:scale(.4) rotate(0deg)"
        return self.kf([(0, a), (t0, a), (t0 + .16, "opacity:1;transform:scale(.9) rotate(2deg)"), (t0 + .3, b),
                        (t1 - .25, b), (t1, c), (D, c)], extra="transform-box:fill-box;transform-origin:center;")

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

    def spin(self, period, cx, cy, rev=False):
        return self.kf([(0, "transform:rotate(0deg)"), (period, f"transform:rotate({-360 if rev else 360}deg)")],
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
        return self.kf([(0, c), (t_open, c), (t_open + .75, o), (t_close, o), (t_close + .7, c), (D, c)],
                       timing="cubic-bezier(.6,0,.3,1)")


def G(cls, inner):
    return f'<g class="{cls}">{inner}</g>'


def hang(A, t0, t1, inner, ox, period=3.0, deg=.8, phase=0.0, enter=None):
    """Drop (or whip) a flat in on strings; it sways while it hangs and is yanked back up."""
    move = A.whip(t0, t1, enter) if enter else A.drop(t0, t1)
    return G(move, G(A.sway(period, deg, ox, -500, phase), inner))


def info(A, t0, t1, kicker, title, body):
    x, y, w, h = 180, 120, 820, 440
    inner = "\n".join([hung_card(x, y, w, h),
                       t(x + 50, y + 85, kicker, 24, TEAL_D, TYPE, 400, ls=2),
                       tl(x + 48, y + 170, title, 70, 80, fill=INK, font=SERIF, weight=900, ls=-1.5),
                       tl(x + 50, y + 180 + 80 * len(title), body, 29, 42, fill=INK, font=TYPE, weight=400)])
    return hang(A, t0, t1, inner, x + w / 2, 3, .7)


def small_tag(x, y, w, label, pointer=True):
    h = 70
    out = [hung_card(x, y, w, h, border=False), t(x + w / 2, y + 47, label, 32, INK, SERIF, 900, "middle", 1)]
    if pointer:
        out.insert(1, piece(P(poly([(x + w / 2 - 18, y + h - 4), (x + w / 2 + 18, y + h - 4), (x + w / 2, y + h + 30)])),
                            PAPER, hatch=None, edge=None, ink=False, filt="cut"))
    return "\n".join(out)


def curtains(A):
    half = SW / 2 + 30
    out = []
    for side, x0 in (("l", SX - 10), ("r", SX + SW / 2 - 20)):
        g = [piece(R(x0, SY - 20, half, SH + 40), TERRA, hatch="hv", edge=None, ink=False, filt="cut2")]
        for i in range(10):
            if i % 2:
                g.append(f'<rect x="{x0 + i * half / 10:.1f}" y="{SY - 20}" width="{half / 10:.1f}" height="{SH + 40}" '
                         f'fill="#7A3E2C" fill-opacity=".28"/>')
        g.append(f'<rect x="{x0}" y="{SY + SH - 40}" width="{half}" height="22" fill="{OCHRE}"/>')
        g.append("".join(f'<circle cx="{x0 + 20 + k * 40}" cy="{SY + SH - 10}" r="9" fill="{OCHRE}" stroke="{BRASS_D}" stroke-width="2"/>'
                         for k in range(int(half // 40))))
        dx = -(half + 60) if side == "l" else half + 60
        out.append(G(A.curtain(.15, 35.2, dx), "".join(g)))
    return "\n".join(out)


def valance():
    n, top, depth = 14, SY - 10, 64
    sw = (SW + 40) / n
    d = f"M{SX - 20} {top} H{SX + SW + 20} V{top + depth} "
    for i in range(n):
        d += f"A{sw / 2:.1f} {sw / 2.6:.1f} 0 0 1 {SX + SW + 20 - (i + 1) * sw:.1f} {top + depth} "
    d += "Z"
    return (piece(P(d), "#A85A44", hatch="hv", edge=None, filt="cut2")
            + f'<line x1="{SX}" y1="{top + 18}" x2="{SX + SW}" y2="{top + 18}" stroke="{OCHRE}" stroke-width="6"/>')


def video():
    A = Anim()
    clouds = (A.loop([(0, "transform:translateX(0)"), (6, "transform:translateX(90px)"), (12, "transform:translateX(0)")], 12, "ease-in-out"),
              A.loop([(0, "transform:translateX(0)"), (4.5, "transform:translateX(-70px)"), (9, "transform:translateX(0)")], 9, "ease-in-out"),
              A.loop([(0, "transform:translateX(0)"), (3, "transform:translateX(60px)"), (6, "transform:translateX(0)")], 6, "ease-in-out"))
    S = [scenery(SX, SY, SW, SH, horizon=.6, cloud_cls=clouds)]

    # B0 0–2.6  LEARN. BUILD. SHIP.
    for i, (w_, col) in enumerate((("LEARN.", INK), ("BUILD.", TERRA), ("SHIP.", TEAL_D))):
        x = 240 + i * 490
        body = card(x, 200, 450, 250) + t(x + 225, 365, w_, 118, col, SERIF, 900, "middle", -3)
        S.append(G(A.slam(.55 + i * .3, 2.6), body))
    S.append(hang(A, 1.35, 2.6, hung_card(560, 520, 800, 90, border=False)
                  + t(960, 578, "CS Equity AI · free CS & AI courses since 2021", 28, INK, TYPE, 400, "middle"), 960))

    # B1 2.6–5.2  the mission
    S.append(hang(A, 2.65, 5.2, "\n".join([
        hung_card(260, 120, 1240, 470),
        t(320, 240, "We teach students to", 66, INK, SERIF, 900, ls=-1),
        t(320, 360, "build with AI,", 112, INK, SERIF, 900, ls=-3),
        t(320, 480, "not just use it.", 112, TERRA, SERIF, 900, ls=-3),
        t(322, 545, "Live online courses. No tuition, no gatekeeping.", 28, INK, TYPE, 400)]), 880))
    S.append(hang(A, 3.3, 5.2, f'<g transform="rotate(-10 1550 560)">{strings([(1420, 560)])}{tag(1380, 490, 380, 150)}'
                  + t(1590, 590, "FREE.", 84, EDGE, SERIF, 900, "middle") + "</g>", 1420, 1.5, 3, enter=900))

    # B2 5.2–8.0  where
    for i, (x, w_, lab) in enumerate(((410, 170, "USA"), (1080, 260, "HONG KONG"), (1440, 210, "TAIWAN"))):
        S.append(hang(A, 5.45 + i * .25, 8.0, small_tag(x, 260 + (i % 2) * 40, w_, lab), x + w_ / 2, 2, 2.5, i * .4))
    S.append(hang(A, 5.3, 8.0, hung_card(330, 600, 1260, 190)
                  + t(960, 680, "Live online courses, taught by engineers", 50, INK, SERIF, 900, "middle", -1)
                  + t(960, 745, "from Google and academia.", 50, TERRA, SERIF, 900, "middle", -1), 960))

    # B3 8.0–10.8  live class
    S.append(info(A, 8.05, 10.8, "LIVE CLASSES", ["Class is live."],
                  ["Weekly sessions with working", "engineers. Students join from", "three places, one call."]))
    lap, (ix, iy, iw, ih) = laptop(1100, 150, 640)
    tiles = [lap]
    tw, th = (iw - 24) / 3, (ih - 12) / 2
    cols = [SLATE, ROSE, SAGE, OCHRE, TEAL, "#C9A6C2"]
    for k in range(6):
        tx, ty = ix + (k % 3) * (tw + 12), iy + (k // 3) * (th + 12)
        hx, hy = tx + tw / 2, ty + th * .45
        tiles.append(G(A.pop(8.45 + k * .14),
                       f'<rect x="{tx:.0f}" y="{ty:.0f}" width="{tw:.0f}" height="{th:.0f}" rx="8" fill="{cols[k]}"/>'
                       f'<path d="M{hx - 46:.0f} {ty + th:.0f} Q{hx:.0f} {hy + 20:.0f} {hx + 46:.0f} {ty + th:.0f} Z" fill="{NAVY}" fill-opacity=".75"/>'
                       f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="26" fill="#E3C3A2" stroke="{INK}" stroke-width="2"/>'))
    blink = A.loop([(0, "opacity:1"), (.5, "opacity:1"), (.6, "opacity:.15"), (1.1, "opacity:.15"), (1.2, "opacity:1")], 1.2)
    tiles.append(f'<rect x="{ix + 14}" y="{iy + 14}" width="104" height="38" rx="19" fill="{TERRA}"/>'
                 + G(blink, f'<circle cx="{ix + 36}" cy="{iy + 33}" r="8" fill="{EDGE}"/>')
                 + t(ix + 52, iy + 42, "LIVE", 24, EDGE, TYPE, 400, ls=2))
    S.append(hang(A, 8.2, 10.8, strings([(1160, 154), (1680, 154)]) + "\n".join(tiles), 1420, 3, .9, 1))

    # B4 10.8–13.6  OpenImpact Lab → certificate
    S.append(info(A, 10.85, 13.6, "LEVEL 1 · CAPABILITY", ["Start on the", "OpenImpact Lab."],
                  ["Free, self-paced, in the browser.", "No setup, no installs."]))
    bx, by = 1080, 140
    lab = [hung_card(bx, by, 660, 450, border=False),
           f'<rect x="{bx + 20}" y="{by + 20}" width="620" height="54" rx="10" fill="#E2D7BD"/>',
           "".join(f'<circle cx="{bx + 50 + k * 26}" cy="{by + 47}" r="8" fill="{c}"/>' for k, c in enumerate((TERRA, OCHRE, TEAL))),
           f'<rect x="{bx + 140}" y="{by + 30}" width="420" height="34" rx="17" fill="{EDGE}"/>',
           t(bx + 350, by + 55, "OpenImpact Lab", 22, INK, TYPE, 400, "middle")]
    for k, lesson in enumerate(["AI & CS fundamentals", "Hands-on labs, modern AI tools", "Foundation course"]):
        yy = by + 110 + k * 82
        lab.append(f'<rect x="{bx + 40}" y="{yy}" width="580" height="64" rx="10" fill="{EDGE}" stroke="{INK}" stroke-opacity=".25"/>'
                   f'<rect x="{bx + 60}" y="{yy + 15}" width="34" height="34" rx="6" fill="none" stroke="{INK}" stroke-width="3"/>'
                   + G(A.pop(11.5 + k * .3), f'<path d="M{bx + 66} {yy + 33} l8 9 l16 -20" fill="none" stroke="{TERRA}" '
                       f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
                   + t(bx + 116, yy + 42, lesson, 27, INK, TYPE, 400))
    lab.append(f'<rect x="{bx + 40}" y="{by + 370}" width="580" height="22" rx="11" fill="#E2D7BD"/>'
               f'<rect class="{A.grow(11.3, 12.5)}" x="{bx + 40}" y="{by + 370}" width="580" height="22" rx="11" fill="{TEAL_D}"/>')
    S.append(hang(A, 11.0, 13.6, "\n".join(lab), bx + 330, 3, .8, 2))
    S.append(G(A.slam(12.6, 13.6), rosette(1650, 600, 100)))

    # B5 13.6–17.6  built by students
    S.append(hang(A, 13.65, 17.6, hung_card(560, 175, 800, 120)
                  + t(960, 239, "Built by students.", 62, INK, SERIF, 900, "middle", -1)
                  + t(960, 277, "LEVEL 2 · CREATION · six AI systems from our last course", 20, TEAL_D, TYPE, 400, "middle", 1), 960))
    for i, (name, desc, _) in enumerate(PROJECTS):
        col, row = i % 2, i // 2
        x, y = (200, 1020)[col], 330 + row * 150
        body = (hung_card(x, y, 700, 130, border=False)
                + t(x + 34, y + 58, f"{i + 1:02d}", 26, TERRA, TYPE, 400, ls=2)
                + t(x + 92, y + 60, name, 40 if len(name) < 20 else 36, INK, CJK, 900)
                + t(x + 92, y + 100, " ".join(desc), 19, INK, TYPE, 400))
        S.append(hang(A, 14.1 + i * .3, 17.6, body, x + 350, 2.4, 1, i * .3, enter=-1500 if col == 0 else 1500))

    # B6 17.6–20.6  MLE-STAR loop
    S.append(info(A, 17.65, 20.6, "NOW RUNNING · MLE-STAR BOOTCAMP", ["Eight weeks of", "autonomous LLMs."],
                  ["Pipelines that read a problem, write", "code, test it, and refine on failure.", "Slides and problem sets are open."]))
    cx, cy = 1390, 450
    ring = [f'<g class="{A.spin(9, cx, cy)}"><circle cx="{cx}" cy="{cy}" r="210" fill="none" stroke="{EDGE}" stroke-width="12" '
            f'stroke-dasharray="26 18"/><circle cx="{cx}" cy="{cy}" r="210" fill="none" stroke="{INK}" stroke-width="4" '
            f'stroke-dasharray="26 18"/></g>',
            G(A.spin(2.25, cx, cy), piece(C(cx, cy - 210, 26), OCHRE, hatch="hx", filt="cut2")),
            card(cx - 130, cy - 70, 260, 140, border=False),
            t(cx, cy + 6, "8 WEEKS", 54, TERRA, SERIF, 900, "middle", -1),
            t(cx, cy + 46, "of open materials", 20, INK, TYPE, 400, "middle")]
    for k, (lab_, dx, dy) in enumerate((("read the problem", -190, -165), ("write code", 210, -165), ("test it", 210, 165),
                                        ("refine on failure", -190, 165))):
        w_ = len(lab_) * 15 + 60
        nx, ny = cx + dx - w_ / 2, cy + dy - 38
        ring.append(G(A.pop(18.1 + k * .22), card(nx, ny, w_, 76, border=False)
                      + t(nx + w_ / 2, ny + 48, lab_, 26, INK, TYPE, 400, "middle")))
    S.append(G(A.drop(17.8, 20.6), "\n".join(ring)))

    # B7 20.6–23.6  Vibe Coding Happy Hour, as a little runner game
    S.append(info(A, 20.65, 23.6, "VIBE CODING HAPPY HOUR · AGES 8–14", ["Their first game,", "in two hours."],
                  ["Kids build it with an AI coding", "agent. Free, and schools can", "request a session."]))
    lap, (ix, iy, iw, ih) = laptop(1120, 140, 600)
    gy = iy + ih - 50
    period = 1.2
    cactus_run = A.loop([(0, "transform:translateX(0)"), (period, f"transform:translateX({-iw - 120}px)")], period)
    jump = A.loop([(0, "transform:translateY(0)"), (.4, "transform:translateY(0)"), (.7, "transform:translateY(-130px)"),
                   (1.0, "transform:translateY(0)"), (period, "transform:translateY(0)")], period, "ease-in-out")
    game = [lap, f'<clipPath id="scr"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="6"/></clipPath>',
            f'<g clip-path="url(#scr)"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="{SKY}"/>'
            f'<rect x="{ix}" y="{gy}" width="{iw}" height="60" fill="#E2C68E"/>'
            f'<line x1="{ix}" y1="{gy}" x2="{ix + iw}" y2="{gy}" stroke="{INK}" stroke-width="3"/>'
            + G(cactus_run, cactus(ix + iw + 40, gy + 2, .62))
            + G(jump, pixel_cat(ix + 120, gy - 98, 14))
            + t(ix + iw - 16, iy + 34, "SCORE 0042", 22, INK, TYPE, 400, "end", 2) + "</g>"]
    S.append(hang(A, 20.8, 23.6, strings([(1180, 144), (1660, 144)]) + "\n".join(game), 1420, 3, .6, 1))
    S.append(G(A.slam(21.5, 23.6), bubble(1110, 600, 430, 78, fill=TERRA)
               + t(1140, 650, "make it jump higher lol", 25, EDGE, TYPE, 400)))
    S.append(G(A.slam(22.2, 23.6), bubble(1290, 712, 450, 78, tail="right")
               + t(1320, 762, "Jump height doubled. Try it.", 25, INK, TYPE, 400)))

    # B8 23.6–26.2  pitch
    S.append(info(A, 23.65, 26.2, "LEVEL 3 · CAPITAL", ["Then pitch it."],
                  ["A founding team of three to five", "takes what they built to angel", "investors."]))
    board = [hung_card(1150, 130, 560, 330),
             t(1190, 205, "Investor pitch", 40, INK, SERIF, 900),
             t(1190, 242, "a student team · AI travel agent", 20, INK, TYPE, 400),
             f'<line x1="1190" y1="420" x2="1670" y2="420" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>',
             f'<polyline class="{A.draw(24.2, 25.2, 700)}" points="1200,405 1300,380 1390,345 1480,335 1570,290 1660,255" '
             f'fill="none" stroke="{TERRA}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="700"/>']
    S.append(hang(A, 23.8, 26.2, "\n".join(board), 1430, 3, .8))
    for i, col in enumerate((TERRA, TEAL, OCHRE, SLATE)):
        px = 1230 + i * 130
        bob = A.loop([(0, "transform:translateY(0)"), (.3, "transform:translateY(-22px)"), (.6, "transform:translateY(0)")], .6, "ease-in-out")
        S.append(G(A.drop(24.0 + i * .12, 26.2),
                   f'<g class="{bob}" style="animation-delay:{-i * .15}s">{strings([(px, 700)])}{person(px, 850, col, 1.0)}</g>'))

    # B9 26.2–29.6  everything we've run
    S.append(hang(A, 26.25, 29.6, hung_card(460, 172, 1000, 100)
                  + t(960, 242, "Free programs since 2021", 60, INK, SERIF, 900, "middle", -1), 960))
    runs = [("2021", ["Android on", "the Cloud"]), ("2023", ["A Beginner’s", "Guide to AI"]), ("2024", ["Gen AI", "Bootcamp"]),
            ("2024–25", ["AI Tutor", "for [X]"]), ("2026", ["Vibe Coding", "Happy Hour"]), ("now", ["MLE-STAR", "Bootcamp"]),
            ("fall 2026", ["The next", "course"])]
    for i, (yr, name) in enumerate(runs):
        row = 0 if i < 4 else 1
        k = i if i < 4 else i - 4
        x = (210 + k * 385) if row == 0 else (405 + k * 385)
        y = 300 if row == 0 else 480
        fill = OCHRE if yr == "fall 2026" else PAPER
        body = (card(x, y, 350, 165, fill=fill, border=False) + t(x + 26, y + 46, yr.upper(), 24, TERRA, TYPE, 400, ls=2)
                + tl(x + 26, y + 96, name, 36, 40, fill=INK, font=SERIF, weight=900))
        S.append(G(A.slam(26.45 + i * .17, 29.6), body))
    S.append(hang(A, 27.6, 29.6, hung_card(300, 680, 1320, 120, border=False)
                  + t(960, 732, "With Taiwan NEXT Foundation · The Hong Kong Polytechnic University ·", 23, INK, TYPE, 400, "middle")
                  + t(960, 768, "National Yang Ming Chiao Tung University · VC.in.Taiwan · CSEB", 23, INK, TYPE, 400, "middle"), 960))

    # B10 29.6–31.8  $0
    S.append(G(A.slam(29.65, 31.8), G(A.sway(1.5, 3, 640, 340), strings([(640, 340)]) + tag(600, 210, 760, 260)
               + t(1010, 365, "$0", 160, EDGE, SERIF, 900, "middle", -4)
               + t(1300, 390, "tuition.", 40, EDGE, TYPE, 400, "end") + t(1300, 432, "ever.", 40, EDGE, TYPE, 400, "end"))))
    S.append(hang(A, 30.0, 31.8, hung_card(410, 560, 1100, 100, border=False)
                  + t(960, 622, "No tuition, no gatekeeping. Just a browser and curiosity.", 28, INK, TYPE, 400, "middle"), 960))

    # B11 31.8–36  end card, curtains close
    S.append(hang(A, 31.85, D, strings([(960, 110)]) + mark(885, 100, 150), 960, 2, 1.5))
    S.append(hang(A, 32.05, D, "\n".join([hung_card(330, 290, 1260, 400),
                                         t(960, 395, "Start with the free Foundation course.", 60, INK, SERIF, 900, "middle", -1),
                                         t(960, 530, "csequityai.org", 112, TERRA, SERIF, 900, "middle", -2),
                                         t(960, 610, "The Fall 2026 roster is drawn from students who finish it.", 27, INK, TYPE, 400, "middle")]), 960))

    S.append(valance())
    S.append(curtains(A))
    title = A.kf([(0, "opacity:1;transform:translateY(0)"), (.35, "opacity:1;transform:translateY(0)"),
                  (.6, "opacity:0;transform:translateY(-500px)"), (35.6, "opacity:0;transform:translateY(-500px)"),
                  (35.95, "opacity:1;transform:translateY(0)"), (D, "opacity:1;transform:translateY(0)")])
    S.append(G(title, strings([(760, 330), (1160, 330)]) + card(660, 330, 600, 230)
               + mark(700, 375, 140) + t(870, 450, "CS Equity AI", 52, INK, SERIF, 900)
               + t(872, 495, "presents", 26, TERRA, TYPE, 400, ls=2)))
    out = [stage(SX, SY, SW, SH, "\n".join(S), "vs"),
           ledge(60, 930, 1800, 40),
           card(130, 996, 520, 66, border=False), mark(146, 1004, 50),
           t(212, 1040, "CS Equity AI · csequityai.org", 26, INK, TYPE, 400)]
    beats = [(5.2, 8.0, "where we teach"), (8.0, 10.8, "live classes"), (10.8, 13.6, "level 1 · capability"),
             (13.6, 17.6, "level 2 · creation"), (17.6, 20.6, "running now"), (20.6, 23.6, "workshops"),
             (23.6, 26.2, "level 3 · capital"), (26.2, 29.6, "since 2021"), (29.6, 31.8, "free, always")]
    for a, z, lab_ in beats:
        out.append(f'<g class="{A.show(a, z)}">' + t(1790, 1040, lab_.upper(), 27, OCHRE, TYPE, 400, "end", 3) + "</g>")
    return doc(1920, 1080, "\n".join(out), "CS Equity AI: 36-second demo of what we do", "\n".join(A.css))
