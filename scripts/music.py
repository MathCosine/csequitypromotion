"""An original, royalty-free 128 BPM soundtrack for the demo video, synthesised from scratch.

Four-on-the-floor drums, off-beat bass, syncopated chord stabs and a chiptune arpeggio over
Am - F - C - G. A whoosh rises into every scene change and a crash marks it, so the music
follows the cut list from video.py exactly.
"""
import subprocess
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 128
BEAT = 60 / BPM
BAR = 4 * BEAT
STEP = BEAT / 4
rng = np.random.default_rng(7)

A3, C4, E4, F3, G3, B3, D4 = 220.0, 261.63, 329.63, 174.61, 196.0, 246.94, 293.66
CHORDS = [  # (bass root, chord tones)
    (110.0, [A3, C4, E4, 2 * A3]),
    (87.31, [F3, A3, C4, 2 * F3]),
    (130.81, [G3, C4, E4, 2 * G3]),
    (98.0, [G3, B3, D4, 2 * G3]),
]


def lp(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=SR, output="sos"), x)


def hp(x, hz, order=2):
    return sosfilt(butter(order, hz, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def saw(f, dur):
    t = tt(dur)
    return 2 * ((f * t) % 1) - 1


def square(f, dur, duty=.5):
    t = tt(dur)
    return np.where((f * t) % 1 < duty, 1.0, -1.0)


def kick():
    t = tt(.42)
    f = 46 + 120 * np.exp(-t * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 400) * .25
    return body + click


def clap():
    t = tt(.3)
    n = bp(rng.standard_normal(len(t)), 900, 3200)
    env = np.exp(-t * 22)
    for k in (0.0, .011, .022):
        env += .6 * np.exp(-np.clip(t - k, 0, None) * 160) * (t >= k)
    return n * env * .55


def hat(open_=False):
    t = tt(.28 if open_ else .06)
    return hp(rng.standard_normal(len(t)), 7500) * np.exp(-t * (11 if open_ else 70)) * .3


def crash():
    t = tt(2.2)
    return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 2.2) * .28


def whoosh(dur=1.0):
    n = rng.standard_normal(int(dur * SR))
    out = np.zeros_like(n)
    chunks = 24
    size = len(n) // chunks
    for i in range(chunks):
        seg = slice(i * size, (i + 1) * size if i < chunks - 1 else len(n))
        out[seg] = lp(n, 300 + 9000 * (i / chunks) ** 2)[seg]
    return out * np.linspace(0, 1, len(n)) ** 2 * .22


def supersaw(freqs, dur, detune=(-.12, 0, .11)):
    x = sum(saw(f * 2 ** (d / 12), dur) for f in freqs for d in detune)
    return x / (len(freqs) * len(detune))


def adsr(n, a=.005, d=.15, s=.0, r=.05):
    t = np.arange(n) / SR
    env = np.minimum(1, t / a) * (s + (1 - s) * np.exp(-np.clip(t - a, 0, None) / d))
    tail = int(r * SR)
    if tail and n > tail:
        env[-tail:] *= np.linspace(1, 0, tail)
    return env


def place(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


def render(cuts, total, path_wav, path_m4a, intro_bars=2, outro_bars=2):
    """cuts: times (s) where a new scene lands; total: length in seconds (whole bars)."""
    n = int(total * SR) + SR * 3
    drums, bass, chords, arp, fx, pad = (np.zeros(n) for _ in range(6))
    bars = int(round(total / BAR))
    K, CL, HC, HO = kick(), clap(), hat(), hat(True)
    for b in range(bars):
        t0 = b * BAR
        root, tones = CHORDS[b % 4]
        intro, outro = b < intro_bars, b >= bars - outro_bars
        section = (b - intro_bars) // 8
        busy = section % 2 == 1                      # every other 8 bars adds 16th hats + arp
        fill = (b - intro_bars) % 8 == 7

        # pad under everything
        p = supersaw(tones[:3], BAR, (-.08, .07)) * adsr(int(BAR * SR), a=.3, d=9, s=.8, r=.3)
        place(pad, lp(p, 900 if intro else 1400), t0, .5)
        if intro:
            # filtered arp + snare build into the first scene
            for s in range(16):
                f = tones[s % 4] * 2
                place(arp, lp(square(f, STEP * .9, .25), 600 + 300 * b + 40 * s) * adsr(int(STEP * .9 * SR), d=.06), t0 + s * STEP, .35)
            if b == intro_bars - 1:
                for s in range(8, 16):
                    place(drums, CL, t0 + s * STEP, .25 + .05 * (s - 8))
            continue
        if outro:
            if b == bars - outro_bars:
                place(chords, lp(supersaw(tones, 2.5), 2400) * adsr(int(2.5 * SR), d=.9), t0, .9)
                place(drums, K, t0)
                place(fx, crash(), t0, 1.2)
            continue

        for s in range(16):
            at = t0 + s * STEP
            if s % 4 == 0:
                place(drums, K, at)
            if s in (4, 12) or (fill and s in (13, 14, 15)):
                place(drums, CL, at, .9 if s in (4, 12) else .55)
            if s % 4 == 2:
                place(drums, HO if s == 14 else HC, at, .9)
            elif busy and s % 2 == 1:
                place(drums, HC, at, .45)
            # off-beat bass, plus a pickup on the last 16th
            if s % 4 == 2 or s == 15:
                note = saw(root, STEP * 1.6) * .6 + square(root / 2, STEP * 1.6) * .4
                place(bass, lp(note, 700) * adsr(len(note), d=.12, s=.3, r=.02), at, .9)
            # syncopated chord stabs
            if s in (0, 3, 6, 10, 13):
                st = supersaw(tones, STEP * 1.5)
                place(chords, lp(st, 3200) * adsr(len(st), d=.09), at, .55)
            if busy:
                order = [0, 1, 2, 3, 2, 1, 0, 1]
                f = tones[order[s % 8]] * 2
                note = lp(square(f, STEP * .85, .25), 4200) * adsr(int(STEP * .85 * SR), d=.07)
                place(arp, note, at, .3)
                place(arp, note, at + 3 * STEP, .12)        # dotted-8th echo

    # scene changes: rising whoosh into the cut, crash on it
    for c in cuts:
        place(fx, whoosh(1.0), c - 1.0)
        place(fx, crash(), c, .7)

    # side-chain the melodic parts against the kick
    duck = np.ones(n)
    for b in range(intro_bars, bars - outro_bars):
        for q in range(4):
            i = int((b * BAR + q * BEAT) * SR)
            k = np.arange(min(int(.25 * SR), n - i)) / SR
            duck[i:i + len(k)] = np.minimum(duck[i:i + len(k)], 1 - .6 * np.exp(-k / .09))
    mel = (bass * .8 + chords * .7 + pad * .45) * duck

    left = drums + mel + arp * 1.0 + fx
    right = drums + mel + np.roll(arp, int(STEP * SR)) * .8 + fx
    left, right = hp(left, 32), hp(right, 32)       # clear sub-rumble the speakers can't play anyway
    mix = np.stack([left, right], 1)[: int(total * SR)]
    fade = int(.4 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mix = np.tanh(1.3 * mix / np.max(np.abs(mix))) / np.tanh(1.3) * .89
    pcm = (mix * 32767).astype("<i2")
    with wave.open(str(path_wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(path_wav), "-c:a", "aac", "-b:a", "192k", str(path_m4a)],
                   check=True)
