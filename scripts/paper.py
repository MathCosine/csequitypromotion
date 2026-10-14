"""Paper-theater toolkit: cut-paper pieces, hatching, brass stage frame, strings, scenery.

Every piece is drawn in four passes so it reads as a printed illustration cut out of
card stock: a cream paper margin, the colour, an engraving-style hatch, and a thin ink
outline. The `cut` filters roughen the edges a little and drop a soft shadow behind.
"""
import base64
import math
import re
from pathlib import Path
from xml.sax.saxutils import escape

import segno

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "brand" / "fonts"

# ---------------------------------------------------------------- palette
KRAFT, KRAFT_D = "#5E4634", "#3B2B1F"
PAPER, EDGE, SKY = "#F1E8D4", "#FBF6EA", "#EAE0C8"
INK = "#2E2620"
TERRA, ROSE = "#C47A5E", "#D9A28C"
TEAL, TEAL_D = "#8DB9B3", "#4F8580"
SLATE, SLATE_D = "#94A9BC", "#5F7A91"
OCHRE, BRASS, BRASS_D = "#D8B25C", "#B48A3C", "#7A5A22"
SAGE, NAVY, WOOD = "#8FAF8A", "#2F3A56", "#8A5E3B"

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
TYPE = "'Special Elite', 'Courier New', Courier, monospace"
CJK = "Fraunces, 'Noto Serif TC', 'PingFang TC', 'Microsoft JhengHei', 'WenQuanYi Zen Hei', serif"


# ---------------------------------------------------------------- document

def font_css():
    out = []
    for fam, f, w in [("Fraunces", "fraunces-latin-500-normal.woff2", 500),
                      ("Fraunces", "fraunces-latin-700-normal.woff2", 700),
                      ("Fraunces", "fraunces-latin-900-normal.woff2", 900),
                      ("Special Elite", "special-elite-latin-400-normal.woff2", 400)]:
        b64 = base64.b64encode((FONTS / f).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "\n".join(out)


def defs(extra_css=""):
    return f'''<defs>
<style>{font_css()}
{extra_css}</style>
<pattern id="hl" width="10" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="3" x2="10" y2="3" stroke="{INK}" stroke-opacity=".13" stroke-width="1.3"/></pattern>
<pattern id="hlw" width="10" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="3" x2="10" y2="3" stroke="#FFFFFF" stroke-opacity=".16" stroke-width="1.3"/></pattern>
<pattern id="hv" width="6" height="10" patternUnits="userSpaceOnUse"><line x1="3" y1="0" x2="3" y2="10" stroke="{INK}" stroke-opacity=".14" stroke-width="1.3"/></pattern>
<pattern id="hx" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><line x1="0" y1="0" x2="0" y2="7" stroke="{INK}" stroke-opacity=".2" stroke-width="1.4"/></pattern>
<pattern id="none" width="1" height="1" patternUnits="userSpaceOnUse"></pattern>
<filter id="cut" x="-15%" y="-15%" width="135%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="4" result="w"/>
  <feDisplacementMap in="SourceGraphic" in2="w" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feDropShadow in="d" dx="3" dy="5" stdDeviation="3.5" flood-color="#1E140C" flood-opacity=".42"/>
</filter>
<filter id="cut2" x="-15%" y="-15%" width="135%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="2" seed="9" result="w"/>
  <feDisplacementMap in="SourceGraphic" in2="w" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feDropShadow in="d" dx="6" dy="11" stdDeviation="7" flood-color="#1E140C" flood-opacity=".5"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" seed="2" stitchTiles="stitch" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 .2  0 0 0 0 .14  0 0 0 0 .08  0 0 0 -1.6 .95"/>
</filter>
<filter id="fiber" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".004 .09" numOctaves="2" seed="5" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 .25  0 0 0 0 .18  0 0 0 0 .1  0 0 0 -1.2 .62"/>
</filter>
<radialGradient id="vignette" cx="50%" cy="48%" r="72%">
  <stop offset="55%" stop-color="#1A1008" stop-opacity="0"/><stop offset="100%" stop-color="#1A1008" stop-opacity=".55"/>
</radialGradient>
</defs>'''


def doc(w, h, body, title, extra_css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n{defs(extra_css)}\n'
            f'<rect width="{w}" height="{h}" fill="{KRAFT}"/>\n'
            f'<rect width="{w}" height="{h}" filter="url(#fiber)"/>\n'
            f'{body}\n'
            f'<rect width="{w}" height="{h}" filter="url(#grain)" style="mix-blend-mode:multiply" opacity=".85"/>\n'
            f'<rect width="{w}" height="{h}" fill="url(#vignette)"/>\n</svg>\n')


# ---------------------------------------------------------------- shapes

def R(x, y, w, h, rx=0):
    return lambda a: f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" {a}/>'


def P(d):
    return lambda a: f'<path d="{d}" {a}/>'


def C(cx, cy, r):
    return lambda a: f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" {a}/>'


def poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def rr(x, y, w, h, r):
    return (f"M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} "
            f"A{r} {r} 0 0 1 {x + w - r} {y + h} H{x + r} A{r} {r} 0 0 1 {x} {y + h - r} "
            f"V{y + r} A{r} {r} 0 0 1 {x + r} {y} Z")


def piece(shape, fill, hatch="hl", edge=EDGE, edgew=10, ink=True, filt="cut", extra=""):
    """A cut-out: paper margin, colour, hatch, ink line, with a shadow."""
    out = []
    if edge:
        out.append(shape(f'fill="{edge}" stroke="{edge}" stroke-width="{edgew}" stroke-linejoin="round"'))
    out.append(shape(f'fill="{fill}"'))
    if hatch:
        out.append(shape(f'fill="url(#{hatch})"'))
    if ink:
        out.append(shape(f'fill="none" stroke="{INK}" stroke-opacity=".75" stroke-width="2" stroke-linejoin="round"'))
    f = f' filter="url(#{filt})"' if filt else ""
    return f'<g{f}{extra}>{"".join(out)}</g>'


def t(x, y, s, size, fill=INK, font=SERIF, weight=700, anchor="start", ls=0, extra=""):
    body = s if s.startswith("<tspan") else escape(s)
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{body}</text>')


def tl(x, y, rows, size, lh, **kw):
    return "\n".join(t(x, y + i * lh, r, size, **kw) for i, r in enumerate(rows))


def strings(points, top=-2000, width=1.6):
    return "".join(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{y:.1f}" stroke="{INK}" '
                   f'stroke-opacity=".7" stroke-width="{width}"/>' for x, y in points)


def card(x, y, w, h, fill=PAPER, border=True, filt="cut2", hatch=None, border_col=INK):
    """A printed paper card / ticket with a double ink rule."""
    out = [piece(R(x, y, w, h, 6), fill, hatch=hatch, edge=None, ink=False, filt=filt)]
    if border:
        out.append(f'<rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{h - 28}" rx="4" fill="none" '
                   f'stroke="{border_col}" stroke-opacity=".55" stroke-width="2"/>')
        out.append(f'<rect x="{x + 21}" y="{y + 21}" width="{w - 42}" height="{h - 42}" rx="3" fill="none" '
                   f'stroke="{border_col}" stroke-opacity=".35" stroke-width="1"/>')
    return "\n".join(out)


def tape(x, y, w=110, h=34, rot=-8):
    return (f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" fill="#EFE3B8" fill-opacity=".78" '
            f'transform="rotate({rot} {x} {y})" stroke="#C9B985" stroke-opacity=".5"/>')


def tag(x, y, w, h, fill=TERRA, filt="cut2"):
    """Price tag pointing left, eyelet at (x+38, y+h/2)."""
    d = poly([(x + 70, y), (x + w, y), (x + w, y + h), (x + 70, y + h), (x, y + h / 2)])
    hx, hy = x + 40, y + h / 2
    return (piece(P(d), fill, hatch="hl", filt=filt)
            + f'<circle cx="{hx}" cy="{hy}" r="13" fill="{KRAFT_D}" fill-opacity=".55" stroke="{OCHRE}" stroke-width="6"/>')


def qr(url, x, y, size, fg=INK):
    q = segno.make(url, error="m")
    n = q.symbol_size(scale=1, border=0)[0]
    d = re.search(r' d="([^"]+)"', q.svg_inline(scale=1, border=0)).group(1)
    return (f'<path transform="translate({x} {y}) scale({size / n:.4f})" stroke="{fg}" fill="none" d="{d}"/>')


# ---------------------------------------------------------------- props

def frame(x, y, w, h, r=110, thick=46, step=78):
    """Brass porthole frame with rivets around the stage opening (x, y, w, h)."""
    outer = rr(x - thick, y - thick, w + 2 * thick, h + 2 * thick, r + thick)
    inner = rr(x, y, w, h, r)
    out = [piece(lambda a: f'<path d="{outer} {inner}" fill-rule="evenodd" {a}/>', BRASS, hatch="hx", edge=None, filt="cut2"),
           f'<path d="{rr(x - 8, y - 8, w + 16, h + 16, r + 8)}" fill="none" stroke="{BRASS_D}" stroke-width="10"/>',
           f'<path d="{rr(x - thick + 6, y - thick + 6, w + 2 * thick - 12, h + 2 * thick - 12, r + thick - 6)}" '
           f'fill="none" stroke="#E6C887" stroke-opacity=".6" stroke-width="3"/>']
    m = thick / 2 + 4
    pts = []
    n = int((w - 2 * r) // step)
    for i in range(n + 1):
        xx = x + r + i * (w - 2 * r) / n
        pts += [(xx, y - m), (xx, y + h + m)]
    n = max(1, int((h - 2 * r) // step))
    for i in range(n + 1):
        yy = y + r + i * (h - 2 * r) / n
        pts += [(x - m, yy), (x + w + m, yy)]
    for px, py in pts:
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="#E2C27A" stroke="{BRASS_D}" stroke-width="2.5"/>'
                   f'<circle cx="{px - 2.5:.1f}" cy="{py - 2.5:.1f}" r="2.5" fill="#FFF4D6" fill-opacity=".8"/>')
    return "\n".join(out)


def ledge(x, y, w, h=44):
    return (piece(R(x, y, w, h, 8), WOOD, hatch="hl", edge=None, filt="cut2")
            + f'<rect x="{x}" y="{y + h - 10}" width="{w}" height="10" rx="4" fill="{KRAFT_D}" fill-opacity=".45"/>'
            + "".join(f'<line x1="{x + 30}" y1="{y + yy}" x2="{x + w - 30}" y2="{y + yy}" stroke="{KRAFT_D}" '
                      f'stroke-opacity=".35" stroke-width="1.5"/>' for yy in (12, 22)))


def cloud(x, y, s=1.0, fill=EDGE):
    d = ("M0 60 C -6 36 18 20 40 28 C 46 4 86 -2 100 20 C 116 4 152 10 150 38 C 176 34 188 62 170 72 "
         "L 12 72 C -6 72 -6 62 0 60 Z")
    return f'<g transform="translate({x} {y}) scale({s})">{piece(P(d), fill, hatch="hl", filt="cut")}</g>'


def building(x, base, w, h, fill, cols=3, chimneys=1):
    out = [piece(R(x, base - h, w, h), fill, hatch="hv")]
    cw, ch = w / (cols * 2 + 1), 18
    rows = int((h - 30) // 38)
    for r in range(rows):
        for c in range(cols):
            out.append(f'<rect x="{x + cw * (1 + 2 * c):.1f}" y="{base - h + 22 + r * 38}" width="{cw:.1f}" '
                       f'height="{ch}" fill="{INK}" fill-opacity=".55"/>')
    for i in range(chimneys):
        cx = x + w * (0.25 + 0.5 * i)
        out.insert(0, piece(R(cx - 8, base - h - 26, 16, 30), fill, hatch="hv", filt="cut"))
    return "\n".join(out)


def taipei101(cx, base, s=1.0):
    out, y = [], base
    pod = 50 * s
    pts = [(cx - 48 * s, y), (cx + 48 * s, y), (cx + 44 * s, y - pod), (cx - 44 * s, y - pod)]
    out.append(piece(P(poly(pts)), "#9CC0B5", hatch="hv"))
    y -= pod
    for i in range(8):
        m = 36 * s
        pts = [(cx - 30 * s, y), (cx + 30 * s, y), (cx + 40 * s, y - m), (cx - 40 * s, y - m)]
        out.append(piece(P(poly(pts)), "#9CC0B5", hatch="hv", filt="cut"))
        y -= m
    for ww, hh in ((26, 26), (16, 22)):
        out.append(piece(R(cx - ww * s / 2, y - hh * s, ww * s, hh * s), "#9CC0B5", hatch="hv", filt="cut"))
        y -= hh * s
    out.insert(0, f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{y - 70 * s}" stroke="{EDGE}" stroke-width="8"/>'
                  f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{y - 70 * s}" stroke="{INK}" stroke-width="3"/>')
    return "\n".join(out)


def boc_tower(cx, base, s=1.0):
    w, h = 76 * s, 330 * s
    pts = [(cx - w / 2, base), (cx + w / 2, base), (cx + w / 2, base - h * .62), (cx, base - h * .82),
           (cx, base - h), (cx - w / 2, base - h * .78)]
    out = [piece(P(poly(pts)), SLATE, hatch="hx")]
    for k in range(4):
        y0 = base - k * h * .17
        y1 = y0 - h * .17
        out.append(f'<path d="M{cx - w / 2} {y0} L{cx + w / 2} {y1} M{cx + w / 2} {y0} L{cx - w / 2} {y1}" '
                   f'stroke="{INK}" stroke-opacity=".5" stroke-width="2.5"/>')
    for dx in (-8, 8):
        out.insert(0, f'<line x1="{cx + dx * s}" y1="{base - h}" x2="{cx + dx * s}" y2="{base - h - 60 * s}" stroke="{INK}" stroke-width="3"/>')
    return "\n".join(out)


def golden_gate(x0, x1, deck, top, tower_w=34):
    """Suspension bridge (the US nod): two terracotta towers, draped cables, deck."""
    span = x1 - x0
    ta, tb = x0 + span * .22, x0 + span * .78
    out = []
    # cables: ink over a paper under-stroke
    cab = (f"M{x0 - 40} {deck - 10} Q{(x0 + ta) / 2} {deck - 30} {ta} {top + 20} "
           f"Q{(ta + tb) / 2} {deck + 60} {tb} {top + 20} Q{(tb + x1) / 2} {deck - 30} {x1 + 40} {deck - 10}")
    out.append(f'<path d="{cab}" fill="none" stroke="{EDGE}" stroke-width="10"/><path d="{cab}" fill="none" stroke="{INK}" stroke-width="3.5"/>')
    for i in range(1, 16):
        xx = ta + (tb - ta) * i / 16
        u = i / 16
        yc = (1 - u) ** 2 * (top + 20) + 2 * (1 - u) * u * (deck + 60) + u * u * (top + 20)
        out.append(f'<line x1="{xx:.1f}" y1="{yc:.1f}" x2="{xx:.1f}" y2="{deck}" stroke="{INK}" stroke-opacity=".6" stroke-width="1.6"/>')
    for tx in (ta, tb):
        d = (f"M{tx - tower_w / 2} {deck + 70} V{top} H{tx + tower_w / 2} V{deck + 70} Z")
        out.append(piece(P(d), TERRA, hatch="hv", filt="cut"))
        for yy in (top + 30, top + (deck - top) * .5):
            out.append(f'<rect x="{tx - tower_w / 2 + 7}" y="{yy}" width="{tower_w - 14}" height="34" fill="{INK}" fill-opacity=".5"/>')
    out.append(piece(R(x0 - 60, deck, span + 120, 16), TERRA, hatch="hl", filt="cut"))
    return "\n".join(out)


def water(x, y, w, h, ripples=True):
    out = [piece(R(x, y, w, h), TEAL, hatch="hl", edge=None, ink=False, filt=None),
           f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>']
    if ripples:
        import random
        rnd = random.Random(3)
        for _ in range(int(w * h / 9000)):
            rx, ry = x + rnd.random() * w, y + 20 + rnd.random() * (h - 30)
            ln = 30 + rnd.random() * 70
            out.append(f'<line x1="{rx:.0f}" y1="{ry:.0f}" x2="{rx + ln:.0f}" y2="{ry:.0f}" stroke="{EDGE}" '
                       f'stroke-opacity=".7" stroke-width="3" stroke-linecap="round"/>')
    return "\n".join(out)


def scenery(sx, sy, sw, sh, horizon=.66, cloud_cls=("", "", "")):
    """US bridge on the left, Hong Kong + Taipei skyline on the right, water in front."""
    hz = sy + sh * horizon
    out = [f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{SKY}"/>',
           f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#hl)"/>']
    for (fx, fy, fs), cls in zip(((.1, .08, 1.2), (.46, .03, .9), (.74, .12, 1.4)), cloud_cls):
        out.append(f'<g class="{cls}">{cloud(sx + sw * fx, sy + sh * fy, fs)}</g>')
    sky_h = hz - sy
    out.append(golden_gate(sx + sw * .02, sx + sw * .42, hz - 70, hz - sky_h * .78))
    bx = sx + sw * .47
    blocks = [(.0, .07, .26, ROSE, 2), (.065, .06, .36, SLATE, 2), (.21, .07, .3, OCHRE, 2),
              (.28, .06, .22, TERRA, 2), (.39, .07, .33, ROSE, 2), (.46, .06, .24, SLATE, 1)]
    out.append(boc_tower(bx + sw * .165, hz, s=sky_h / 430))
    out.append(taipei101(bx + sw * .37, hz, s=sky_h / 500))
    for fx, fw, fh, col, cols in blocks:
        out.append(building(bx + sw * fx, hz, sw * fw, sky_h * fh * 1.25, col, cols=cols))
    out.append(water(sx, hz, sw, sy + sh - hz))
    return "\n".join(out)


def laptop(x, y, w, screen_fill=NAVY):
    h = w * .62
    out = [piece(R(x, y, w, h, 14), screen_fill, hatch="hlw"),
           piece(P(poly([(x - w * .08, y + h + 4), (x + w * 1.08, y + h + 4), (x + w * 1.0, y + h + 36),
                         (x, y + h + 36)])), SLATE, hatch="hl")]
    return "\n".join(out), (x + 26, y + 26, w - 52, h - 52)


def rosette(cx, cy, r, label1="FOUNDATION", label2="CERTIFICATE"):
    pts = []
    for i in range(48):
        a = math.pi * 2 * i / 48
        rr_ = r if i % 2 == 0 else r * .9
        pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    rib = lambda dx: poly([(cx + dx - 22, cy + r * .5), (cx + dx + 22, cy + r * .5), (cx + dx + 30, cy + r * 1.7),
                           (cx + dx + 4, cy + r * 1.5), (cx + dx - 14, cy + r * 1.75)])
    return "\n".join([piece(P(rib(-30)), TERRA, hatch="hl"), piece(P(rib(30)), TERRA, hatch="hl"),
                      piece(P(poly(pts)), OCHRE, hatch="hx", filt="cut2"),
                      f'<circle cx="{cx}" cy="{cy}" r="{r * .7}" fill="none" stroke="{INK}" stroke-opacity=".6" stroke-width="2" stroke-dasharray="5 6"/>',
                      t(cx, cy - 4, label1, r * .17, INK, TYPE, 400, "middle", 1),
                      t(cx, cy + r * .24, label2, r * .17, INK, TYPE, 400, "middle", 1)])


def gear(cx, cy, r, teeth=10, fill=SLATE):
    pts = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        w = 2 * math.pi / teeth
        for da, rad in ((-.5, .8), (-.28, 1), (.28, 1), (.5, .8)):
            pts.append((cx + r * rad * math.cos(a + da * w), cy + r * rad * math.sin(a + da * w)))
    hole = r * .25
    d = poly(pts) + f" M{cx + hole} {cy} A{hole} {hole} 0 1 0 {cx - hole} {cy} A{hole} {hole} 0 1 0 {cx + hole} {cy} Z"
    return piece(lambda a: f'<path d="{d}" fill-rule="evenodd" {a}/>', fill, hatch="hx")


def person(x, feet, body, s=1.0):
    head = C(x, feet - 150 * s, 24 * s)
    d = (f"M{x - 38 * s} {feet - 30 * s} L{x - 32 * s} {feet - 108 * s} Q{x} {feet - 124 * s} {x + 32 * s} {feet - 108 * s} "
         f"L{x + 38 * s} {feet - 30 * s} Z")
    legs = P(f"M{x - 22 * s} {feet - 34 * s} h16 v34 h-16 Z M{x + 6 * s} {feet - 34 * s} h16 v34 h-16 Z")
    return "\n".join([piece(legs, INK, hatch=None, filt="cut"), piece(P(d), body, hatch="hl"),
                      piece(head, "#E3C3A2", hatch="hl")])


def pixel_cat(x, y, p, color=OCHRE, eye=INK):
    rows = ["X...X", "XXXXX", "XOXOX", "XXXXX", ".XXXXXXX", ".XXXXXX.", ".X.X.X.X"]
    body = "".join(f"M{x + c * p} {y + r * p} h{p} v{p} h-{p} Z" for r, row in enumerate(rows)
                   for c, ch in enumerate(row) if ch == "X")
    eyes = "".join(f"M{x + c * p} {y + r * p} h{p} v{p} h-{p} Z" for r, row in enumerate(rows)
                   for c, ch in enumerate(row) if ch == "O")
    return piece(P(body), color, hatch="hl", filt="cut2") + f'<path d="{eyes}" fill="{eye}"/>'


def cactus(x, base, s=1.0):
    d = (f"M{x} {base} V{base - 130 * s} a17 17 0 0 1 34 0 V{base} Z "
         f"M{x - 34 * s} {base - 60 * s} V{base - 92 * s} a11 11 0 0 1 22 0 V{base - 70 * s} H{x + 4} V{base - 48 * s} H{x - 22 * s} a12 12 0 0 1 -12 -12 Z "
         f"M{x + 64 * s} {base - 84 * s} V{base - 112 * s} a11 11 0 0 1 22 0 V{base - 72 * s} a12 12 0 0 1 -12 12 H{x + 30} V{base - 84 * s} Z")
    return piece(P(d), SAGE, hatch="hv")


def mark(x, y, size):
    """Logo mark as cut paper: brackets around an equals sign, two gold nodes."""
    s = size / 120
    g = [piece(R(0, 0, 120, 120, 26), NAVY, hatch="hlw", edgew=12, filt="cut2")]
    for d, col in (("M38 36 L20 60 L38 84", TERRA), ("M82 36 L100 60 L82 84", TEAL)):
        g.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>')
    for yy in (50, 70):
        g.append(f'<line x1="44" y1="{yy}" x2="76" y2="{yy}" stroke="{EDGE}" stroke-width="9" stroke-linecap="round"/>')
    g.append(f'<circle cx="60" cy="30" r="7.5" fill="{OCHRE}"/><circle cx="60" cy="90" r="7.5" fill="{OCHRE}"/>')
    return f'<g transform="translate({x} {y}) scale({s:.4f})">{"".join(g)}</g>'


def bubble(x, y, w, h, fill=EDGE, tail="left"):
    tx = x + 40 if tail == "left" else x + w - 70
    d = rr(x, y, w, h, 26)[:-1] + f" M{tx} {y + h - 2} L{tx + 10} {y + h + 30} L{tx + 36} {y + h - 2} Z"
    return piece(P(d), fill, hatch="hl" if fill != EDGE else None, filt="cut2")
