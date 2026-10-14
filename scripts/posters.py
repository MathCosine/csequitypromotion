"""Clean, conventional event posters: one sans-serif, flat colour, a clear reading order."""
import base64
import re
from xml.sax.saxutils import escape

import segno

from paper import FONTS

BG, CARD = "#FBF7EF", "#FFFFFF"
INK, MUTED = "#1C2B4A", "#56617A"
BLUE, PINK, YELLOW = "#2457C5", "#E5487F", "#FFCF3D"
TINT_B, TINT_Y, TINT_P = "#E7EEFB", "#FFF3C9", "#FCE3EC"
SANS = "'DM Sans', 'Helvetica Neue', Arial, sans-serif"
CJK = "'DM Sans', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', 'WenQuanYi Zen Hei', sans-serif"

SITE = "https://csequityai.org"
VIBE = "https://csequityai.org/events/vibe-coding-happy-hour.html"
W, H, M = 1800, 2400, 120


def font_css():
    out = []
    for wt in (400, 500, 700, 800):
        b64 = base64.b64encode((FONTS / f"dm-sans-latin-{wt}-normal.woff2").read_bytes()).decode()
        out.append(f"@font-face{{font-family:'DM Sans';font-weight:{wt};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "\n".join(out)


def doc(body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title)}</title><defs><style>{font_css()}</style>'
            f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
            f'baseFrequency=".9" numOctaves="2" seed="4" stitchTiles="stitch"/><feColorMatrix type="matrix" '
            f'values="0 0 0 0 .3  0 0 0 0 .25  0 0 0 0 .2  0 0 0 -1.4 .7"/></filter></defs>'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>{body}'
            f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".35" style="mix-blend-mode:multiply"/></svg>\n')


def T(x, y, s, size, fill=INK, weight=400, anchor="start", ls=0, font=SANS):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{escape(s)}</text>')


def TL(x, y, rows, size, lh, **kw):
    return "".join(T(x, y + i * lh, r, size, **kw) for i, r in enumerate(rows))


def box(x, y, w, h, fill, r=28, stroke=None):
    st = f' stroke="{stroke}" stroke-width="3"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{st}/>'


def pill(x, y, label, size, fill, color, pad=26):
    w = len(label) * size * .62 + pad * 2
    h = size * 2
    return box(x, y, w, h, fill, h / 2) + T(x + pad, y + h / 2 + size * .36, label, size, color, 700, ls=1)


def mark(x, y, s):
    k = s / 120
    return (f'<g transform="translate({x} {y}) scale({k:.4f})"><rect width="120" height="120" rx="28" fill="{BLUE}"/>'
            f'<path d="M38 36 L20 60 L38 84" fill="none" stroke="{PINK}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M82 36 L100 60 L82 84" fill="none" stroke="{YELLOW}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<line x1="44" y1="50" x2="76" y2="50" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
            f'<line x1="44" y1="70" x2="76" y2="70" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="60" cy="30" r="7" fill="{YELLOW}"/><circle cx="60" cy="90" r="7" fill="{YELLOW}"/></g>')


def qr(url, x, y, size):
    q = segno.make(url, error="m")
    n = q.symbol_size(scale=1, border=0)[0]
    d = re.search(r' d="([^"]+)"', q.svg_inline(scale=1, border=0)).group(1)
    return f'<path transform="translate({x} {y}) scale({size / n:.4f})" stroke="{INK}" fill="none" d="{d}"/>'


def header():
    return (mark(M, 90, 84) + T(M + 108, 145, "CS Equity AI", 40, INK, 800)
            + T(W - M, 145, "csequityai.org", 34, BLUE, 700, "end"))


def cta(y, line1, line2, url, label):
    """Blue panel with the call to action and a QR code on a white tile."""
    h = 300
    return (box(M, y, W - 2 * M, h, BLUE, 36)
            + T(M + 70, y + 120, line1, 62, "#FFFFFF", 800, ls=-1)
            + T(M + 70, y + 205, line2, 64, YELLOW, 800)
            + T(M + 72, y + 255, f"{label}. Free, from a 501(c)(3) public charity.", 26, "#C9D7F5", 500)
            + box(W - M - 290, y + 25, 250, 250, "#FFFFFF", 22)
            + qr(url, W - M - 268, y + 47, 206))


def footer():
    return T(W / 2, H - 40, "CS Equity AI · 501(c)(3) public charity · EIN 99-3463829 · info@csequityai.org",
             22, MUTED, 400, "middle")


# ---------------------------------------------------------------- posters

def poster_main(levels):
    b = [header(),
         T(M, 400, "We teach students", 150, INK, 800, ls=-4),
         T(M, 560, "to build with AI,", 150, INK, 800, ls=-4),
         T(M, 720, "not just use it.", 150, PINK, 800, ls=-4),
         pill(M, 790, "FREE · NO TUITION, EVER", 30, YELLOW, INK),
         TL(M, 945, ["Live online courses taught by engineers from Google and academia,",
                     "for students in the US, Taiwan and Hong Kong. All you need is a browser."], 38, 54, fill=MUTED, weight=500),
         T(M, 1150, "How it works", 56, INK, 800, ls=-1),
         T(M + 380, 1150, "Each level ends with something real.", 32, MUTED, 500)]
    cw = (W - 2 * M - 2 * 36) / 3
    tints = (TINT_B, TINT_Y, TINT_P)
    for i, (_, lab, title, desc, out) in enumerate(levels):
        x = M + i * (cw + 36)
        b += [box(x, 1200, cw, 420, tints[i], 30),
              f'<circle cx="{x + 75}" cy="{1280}" r="42" fill="{(BLUE, YELLOW, PINK)[i]}"/>',
              T(x + 75, 1297, str(i + 1), 46, INK if i == 1 else "#FFFFFF", 800, "middle"),
              T(x + 40, 1380, lab.title(), 24, MUTED, 700, ls=1),
              T(x + 40, 1440, title, 46, INK, 800, ls=-1),
              TL(x + 40, 1495, [" ".join(desc)], 28, 40, fill=INK, weight=500),
              T(x + 40, 1575, "→ " + out, 28, BLUE, 700)]
    b += [T(M, 1730, "Free programs we’ve run", 56, INK, 800, ls=-1)]
    runs = [("2021", "Android on the Cloud"), ("2023", "A Beginner’s Guide to AI"), ("2024", "Gen AI Bootcamp"),
            ("2024–25", "AI Tutor for [X]"), ("2026", "Vibe Coding Happy Hour"), ("Now", "MLE-STAR Bootcamp"),
            ("Fall 2026", "Next course (finish the Foundation course first)")]
    for i, (yr, name) in enumerate(runs):
        col, row = (0, i) if i < 4 else (1, i - 4)
        x, y = M + col * 800, 1810 + row * 58
        b += [T(x, y, yr, 30, PINK, 700), T(x + 170, y, name, 30, INK, 500)]
    b += [cta(2010, "Start with the free Foundation course.", "csequityai.org", SITE, "Scan the code to start"), footer()]
    return doc("".join(b), "CS Equity AI poster: we teach students to build with AI, not just use it. Free.")


CAT = ["X...X", "XXXXX", "XOXOX", "XXXXX", ".XXXXXXX", ".XXXXXX.", ".X.X.X.X"]


def pixels(x, y, p, rows, ch, fill):
    d = "".join(f"M{x + c * p} {y + r * p}h{p}v{p}h-{p}Z" for r, row in enumerate(rows) for c, k in enumerate(row) if k == ch)
    return f'<path d="{d}" fill="{fill}"/>'


def cactus(x, base, s, fill):
    return (f'<g fill="{fill}"><rect x="{x}" y="{base - 150 * s}" width="{40 * s}" height="{150 * s}" rx="{20 * s}"/>'
            f'<rect x="{x - 34 * s}" y="{base - 105 * s}" width="{24 * s}" height="{58 * s}" rx="{12 * s}"/>'
            f'<rect x="{x - 34 * s}" y="{base - 66 * s}" width="{50 * s}" height="{20 * s}" rx="{10 * s}"/>'
            f'<rect x="{x + 50 * s}" y="{base - 125 * s}" width="{24 * s}" height="{52 * s}" rx="{12 * s}"/>'
            f'<rect x="{x + 24 * s}" y="{base - 92 * s}" width="{50 * s}" height="{20 * s}" rx="{10 * s}"/></g>')


def poster_vibe():
    b = [header(),
         pill(M, 240, "FREE WORKSHOP · OPEN TO HOSTS", 28, TINT_P, PINK),
         T(M, 470, "Vibe Coding", 176, INK, 800, ls=-5),
         T(M, 640, "Happy Hour", 176, PINK, 800, ls=-5),
         TL(M, 750, ["A two-hour workshop that gets 8–14 year olds building their", "first game with an AI coding agent."],
            40, 56, fill=MUTED, weight=500)]
    # illustration panel: chat on the left, the game on the right
    py, ph = 880, 700
    b += [box(M, py, W - 2 * M, ph, TINT_Y, 36)]
    chat = [("me", "make a cat that jumps over cactuses"), ("ai", "Done. Press space to jump."),
            ("me", "make it jump higher lol"), ("ai", "Jump height doubled. Try it.")]
    for i, (who, s) in enumerate(chat):
        y = py + 60 + i * 110
        w = len(s) * 15.5 + 70
        if who == "me":
            b += [box(M + 50, y, w, 80, PINK, 40), T(M + 85, y + 51, s, 28, "#FFFFFF", 500)]
        else:
            b += [box(M + 50, y, w, 80, CARD, 40, stroke="#E9DFC0"), T(M + 85, y + 51, s, 28, INK, 500)]
    gy = py + ph - 110
    b += [f'<line x1="{M + 760}" y1="{gy}" x2="{W - M - 50}" y2="{gy}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
          f'<path d="M{M + 800} {gy - 10} Q{M + 1080} {py - 40} {M + 1400} {gy - 10}" fill="none" stroke="{BLUE}" '
          f'stroke-width="7" stroke-dasharray="2 20" stroke-linecap="round"/>',
          pixels(M + 960, py + 170, 26, CAT, "X", "#F2A93B"), pixels(M + 960, py + 170, 26, CAT, "O", INK),
          cactus(M + 1150, gy, 1.0, "#3E9E6E"), cactus(M + 1400, gy, .8, "#3E9E6E"),
          T(W - M - 50, py + 70, "SCORE 0042", 30, INK, 700, "end", 3)]
    facts = [("2 hours", "one workshop"), ("Ages 8–14", "their first game"), ("Free", "like everything we run"),
             ("Open source", "curriculum on GitHub")]
    cw = (W - 2 * M - 3 * 30) / 4
    for i, (big, small) in enumerate(facts):
        x = M + i * (cw + 30)
        b += [box(x, 1640, cw, 190, CARD, 28, stroke="#ECE4D2"),
              T(x + 34, 1730, big, 52, (BLUE, PINK, BLUE, PINK)[i], 800, ls=-1),
              T(x + 34, 1785, small, 25, MUTED, 500)]
    b += [T(M, 1910, "Piloted at a Google office in May 2026. Schools can still request a session.", 30, MUTED, 500),
          cta(2010, "Schools: request a free session.", "csequityai.org", VIBE, "Scan the code for details"), footer()]
    return doc("".join(b), "Vibe Coding Happy Hour poster: 8 to 14 year olds build their first game with an AI coding agent")


def poster_students(projects):
    b = [header(),
         T(M, 420, "Built by students.", 170, INK, 800, ls=-5),
         TL(M, 520, ["Six AI systems shipped by teams in our last course,",
                     "“The Course of Making AI Tutor for [X].” Real repos, real demos."], 38, 54, fill=MUTED, weight=500)]
    cw, ch = (W - 2 * M - 40) / 2, 360
    tints = (TINT_B, TINT_Y, TINT_P)
    for i, (name, desc, stack) in enumerate(projects):
        x, y = M + (i % 2) * (cw + 40), 680 + (i // 2) * (ch + 36)
        b += [box(x, y, cw, ch, CARD, 30, stroke="#ECE4D2"),
              box(x + 40, y + 40, 84, 84, tints[i % 3], 20),
              T(x + 82, y + 97, f"{i + 1:02d}", 36, (BLUE, "#B58400", PINK)[i % 3], 800, "middle"),
              T(x + 40, y + 190, name, 52 if len(name) < 20 else 48, INK, 800, ls=-1, font=CJK),
              TL(x + 40, y + 243, desc, 30, 42, fill=MUTED, weight=500)]
        if stack:
            b.append(T(x + 40, y + ch - 36, stack, 26, BLUE, 700))
    b += [cta(2010, "The next course starts Fall 2026.", "csequityai.org", SITE, "Scan the code to start"),
          T(M, 1940, "The roster is drawn from students who finish the free Foundation course, so start it now.",
            30, MUTED, 500), footer()]
    return doc("".join(b), "CS Equity AI poster: six AI systems built by students")
