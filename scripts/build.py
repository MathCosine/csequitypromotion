#!/usr/bin/env python3
"""Generate every CS Equity AI promo graphic.

All copy is taken from csequityai.org. Change it here, then:

    pip install segno numpy scipy
    python3 scripts/build.py
    node scripts/render.mjs      # PNG exports + video/demo.mp4

Posters are in posters.py; social graphics and the video use the
paper-theater toolkit (paper.py); the video's timeline is in video.py and its
soundtrack is synthesised by music.py.
"""
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from paper import *  # noqa: E402,F401,F403


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


def brand():
    def logo(w, h, body, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                f'aria-label="{title}"><title>{title}</title>{defs()}{body}</svg>\n')
    write("brand/logo-mark.svg", logo(160, 160, mark(20, 16, 120), "CS Equity AI mark"))
    write("brand/logo-horizontal.svg", logo(620, 160, mark(20, 16, 120)
          + t(170, 88, "CS Equity AI", 58, INK, SERIF, 900, ls=-1)
          + t(172, 124, "csequityai.org", 24, TEAL_D, TYPE, 400, ls=1), "CS Equity AI"))


if __name__ == "__main__":
    import posters
    import video as demo
    brand()
    write("posters/poster-build-with-ai.svg", posters.poster_main(LEVELS))
    write("posters/poster-vibe-coding-happy-hour.svg", posters.poster_vibe())
    write("posters/poster-built-by-students.svg", posters.poster_students(PROJECTS))
    social()
    import music
    svg, plan, total = demo.video()
    write("video/demo.svg", svg)
    music.render([start for start, *_ in plan], total, ROOT / "video" / "soundtrack.wav", ROOT / "video" / "soundtrack.m4a")
    print("wrote video/soundtrack.m4a", f"({total:.1f}s)")
