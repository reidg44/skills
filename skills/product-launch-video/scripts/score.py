"""Synthesize the film's score + sound design, locked to the film's timeline.

No samples, no licences: everything is numpy synthesis (FM plucks/bells,
band-limited saws, filtered noise, convolution reverb). Edit the CUE SHEET to
mirror config.js — every visual event that matters should have a sound.

    uv run --with numpy --with scipy python score.py [--out score.wav]

Structure it builds (the arc that works for 30 s):
  intro pulse (one pluck + heartbeat per hook word, riser, reverse suck)
  → DROP (sub boom + crash, 4-on-the-floor, sidechain pump, pads, offbeat bass)
  → layers added every few bars (claps, 16th hats, plucked lead arp)
  → BREATH (drums out, filter closed, foley e.g. typing) → riser + snare roll
  → DROP 2 → bigger hit + flicker blips + word hits
  → CUT to silence + slash "shing" → rising tone → logo sting (major-key bells) → tail.
Then normalize to -14 LUFS / -1 dBTP at mux time (ffmpeg loudnorm).
"""

import argparse

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt, sosfilt_zi

# ════════════════════════ CUE SHEET — mirror config.js ════════════════════════
BPM = 120
DUR = 30.0
DROP, CUT, LOGO, WORD, TAG = 4.0, 24.0, 25.6, 26.1, 27.4
HOOK_WORDS = [0, .5, 1, 1.5, 2, 2.5, 3]               # one pluck + heartbeat each
HOOK_CARDS = [-.6, .5, 1, 1.25, 1.5, 2, 2.5, 3]        # digit-scramble chatter
GROOVE = [(DROP, 18.0), (20.0, CUT)]                   # (start, end) of drum sections
CLAPS_FROM, HATS16_FROM, LEAD_FROM = 8.0, 12.0, 12.0   # layer entrances (build the arc!)
BREATH = (18.0, 20.0)                                  # drums out, filter closes
SECOND_DROPS = [(20.0, 0.6)]                           # (t, strength) smaller impacts
BIG_HIT = 22.0                                         # wall / climax impact
WHOOSHES = [(8, 1), (10, -1), (12, 1), (14, -1), (16, 1), (18, -1), (7.72, 0)]  # (t of cut, pan dir)
ROLLS = [(4.0, 5.1), (6.25, 7.3), (12.05, 13.0), (14.0, 15.0), (16.0, 16.8)]    # number rolls (odometer ticks)
POPS = [(10.06 + i * .045) for i in range(18)]          # tiny pops (tiles, chips…)
GLISS = [(8.08 + i * .05) for i in range(8)]            # rising plucks under growing bars
TYPING = (18.3, 19.45, "Why did churn spike in March?")  # (start, end, text) — a click per non-space char
QUAD_POPS = [20.0, 20.25, 20.5, 20.75]
FLICKERS = [22 + i * .047 for i in range(15)]
WORD_HITS = [22.5, 23.0, 23.5]
WORDMARK_LETTERS = 6                                   # len(brand.name)
# harmony: one chord per bar from DROP — (bass MIDI, [voicing]) — i–VI–III–VII in A minor
CHORDS = [(45, [60, 64, 67, 71]), (41, [57, 60, 64, 67]), (48, [64, 67, 71, 74]), (43, [59, 62, 64, 69])]
HOOK_ARP = [69, 72, 76, 79, 83, 84, 88]                 # rising, one per hook word
STING = [57, 61, 64, 68, 71, 76]                        # A major add9: the Picardy lift out of minor
# ══════════════════════════════════════════════════════════════════════════════

SR = 48000
N = int(DUR * SR)
BEAT = 60 / BPM
rng = np.random.default_rng(7)
dry, verb, duck = (np.zeros((N, 2)) for _ in range(3))
DUCK = np.ones(N)


def midi(n: float) -> float:
    """MIDI note number → frequency in Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(n: int) -> np.ndarray:
    """Time axis in seconds for n samples."""
    return np.arange(n) / SR


def add(bus: np.ndarray, sig: np.ndarray, t0: float, gain: float = 1.0, pan: float = 0.0) -> None:
    """Mix mono/stereo `sig` into `bus` at t0 s, equal-power pan −1..1."""
    i = int(round(t0 * SR))
    if i >= N:
        return
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
    j, s0 = min(N, i + len(sig)), max(0, -i)
    bus[max(0, i):j] += sig[s0:j - i] * gain


def filt(x: np.ndarray, kind: str, f: float | list[float], order: int = 2) -> np.ndarray:
    """Apply a static Butterworth filter (lowpass/highpass/bandpass)."""
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def sweep(x: np.ndarray, kind: str, f0: float, f1: float, curve: float = 2.0, block: int = 256) -> np.ndarray:
    """Time-varying filter, cutoff gliding f0→f1."""
    out, zi, nb = np.zeros_like(x), None, (len(x) + block - 1) // block
    for b in range(nb):
        fc = f0 * (f1 / f0) ** ((b / max(1, nb - 1)) ** curve)
        sos = butter(2, [fc / 1.6, min(fc * 1.6, SR / 2 - 100)] if kind == "bandpass" else min(fc, SR / 2 - 100), kind, fs=SR, output="sos")
        if zi is None:
            zi = sosfilt_zi(sos) * 0
        out[b * block:(b + 1) * block], zi = sosfilt(sos, x[b * block:(b + 1) * block], zi=zi)
    return out


def env(n: int, a: float, d: float) -> np.ndarray:
    """Linear attack over a s, exponential decay with time constant d s."""
    t = tt(n)
    return np.exp(-t / d) * (np.clip(t / a, 0, 1) if a > 0 else 1)


def saw(f: float, n: int, detune: float = 0.0, phase: float = 0.0) -> np.ndarray:
    """Band-limited sawtooth (additive, harmonics below 9 kHz)."""
    t, f, y, k = tt(n), f * (1 + detune), np.zeros(n), 1
    while k * f < 9000:
        y += np.sin(2 * np.pi * k * f * t + phase * k) / k
        k += 1
    return y * 0.6


def noise(n: int) -> np.ndarray:
    """White noise from the seeded generator (deterministic renders)."""
    return rng.standard_normal(n)


# ── instruments ──
def kick(g: float = 1.0) -> np.ndarray:
    """Pitch-swept sine kick with a noise click."""
    n = int(.5 * SR)
    t = tt(n)
    body = np.sin(2 * np.pi * np.cumsum(46 + 120 * np.exp(-t / .035)) / SR) * np.exp(-t / .26)
    return np.tanh((body + filt(noise(n), "highpass", 2500) * np.exp(-t / .004) * .35) * 1.6) * g


def clap() -> np.ndarray:
    """Three-burst band-passed noise clap with a short tail."""
    n = int(.45 * SR)
    t = tt(n)
    e = np.zeros(n)
    for o in (0, .011, .022):
        e += (t >= o) * np.exp(-np.clip(t - o, 0, None) / .008)
    e += (t >= .03) * np.exp(-np.clip(t - .03, 0, None) / .12) * .7
    return filt(noise(n), "bandpass", [900, 3200]) * e


def hat(open_: bool = False) -> np.ndarray:
    """High-passed noise hi-hat, closed or open."""
    n = int((.25 if open_ else .06) * SR)
    return filt(noise(n), "highpass", 7500, 4) * env(n, 0, .09 if open_ else .014)


def pluck(note: float, dur: float = .6, bright: float = 2.2) -> np.ndarray:
    """FM pluck; `bright` is the decaying modulation index."""
    n = int(dur * SR)
    t = tt(n)
    f = midi(note)
    tone = np.sin(2 * np.pi * f * t + bright * np.exp(-t / .08) * np.sin(4 * np.pi * f * t))
    return tone * np.exp(-t / (dur / 3.2)) * np.clip(t / .002, 0, 1)


def bell(note: float, dur: float = 4.0) -> np.ndarray:
    """Inharmonic FM bell for the logo sting."""
    n = int(dur * SR)
    t = tt(n)
    f = midi(note)
    y = np.sin(2 * np.pi * f * t + 3 * np.exp(-t / .6) * np.sin(2 * np.pi * 3.5 * f * t)) * np.exp(-t / 1.4)
    return (y + .35 * np.sin(4 * np.pi * f * t) * np.exp(-t / .5)) * np.clip(t / .003, 0, 1)


def boom(g: float = 1.0, length: float = 2.4, f0: float = 58) -> np.ndarray:
    """Sub-bass impact with a noise transient."""
    n = int(length * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * np.cumsum(f0 * (.62 + .38 * np.exp(-t / .5))) / SR) * np.exp(-t / .7)
    return np.tanh(y * 1.4 + filt(noise(n), "lowpass", 5000) * np.exp(-t / .03) * .6) * g


def crash(length: float = 2.2) -> np.ndarray:
    """High-passed noise cymbal crash."""
    n = int(length * SR)
    return filt(noise(n), "highpass", 4500) * env(n, .002, .55)


def riser(length: float, f0: float = 300, f1: float = 9000) -> np.ndarray:
    """Noise sweep plus rising tone that builds into a hit."""
    n = int(length * SR)
    t = tt(n)
    tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2.5 * t / length)) / SR) * .12
    return (sweep(noise(n), "bandpass", f0, f1, 1.6) * .9 + tone) * (t / length) ** 2.2


def whoosh(length: float = .42) -> np.ndarray:
    """Band-swept noise swell for camera moves."""
    n = int(length * SR)
    t = tt(n)
    return sweep(noise(n), "bandpass", 500, 5000, 1.0) * np.sin(np.pi * np.clip(t / length, 0, 1)) ** 2.5


def tick(f: float = 3000, length: float = .012) -> np.ndarray:
    """Tiny sine tick (odometer digits, flickers, wordmark letters)."""
    n = int(length * SR)
    t = tt(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / (length / 4))


def key_click() -> np.ndarray:
    """Keyboard click foley for typing shots."""
    n = int(.05 * SR)
    t = tt(n)
    return filt(noise(n), "bandpass", [1800, 5200]) * np.exp(-t / .006) + np.sin(2 * np.pi * 180 * t) * np.exp(-t / .01) * .4


def pad(notes: list[int], length: float, c0: float, c1: float) -> np.ndarray:
    """Detuned-saw chord pad with its lowpass gliding c0→c1 Hz."""
    n = int(length * SR)
    y = np.zeros(n)
    for nt in notes:
        for d in (-.006, 0, .007):
            y += saw(midi(nt), n, d, rng.uniform(0, 6.28))
    t = tt(n)
    return sweep(y / (len(notes) * 3), "lowpass", c0, c1, 1.0) * np.clip(t / .08, 0, 1) * np.clip((length - t) / .12, 0, 1)


def chord_at(t: float) -> tuple[int, list[int]]:
    """Return the (bass, voicing) chord for the bar containing t."""
    return CHORDS[int((t - DROP) // (4 * BEAT)) % len(CHORDS)]


def duck_env(t0: float, depth: float = .8) -> None:
    """Carve a sidechain dip into DUCK at t0 (the kick 'pump')."""
    i, n = int(t0 * SR), int(.45 * SR)
    g = 1 - depth * np.exp(-tt(n) / .11)
    j = min(N, i + n)
    DUCK[i:j] = np.minimum(DUCK[i:j], g[:j - i])


def roll_ticks(t0: float, t1: float, gain: float = .08, f: float = 3400) -> None:
    """Odometer clicks whose spacing follows the outExpo number roll."""
    span, last = t1 - t0, -1
    for i in range(int(span * SR / 64)):
        x = i * 64 / SR / span
        d = int((1 - 2 ** (-10 * x)) * 40)
        if d != last:
            add(dry, tick(f * rng.uniform(.92, 1.08), .008), t0 + x * span, gain * (1 - .6 * x), rng.uniform(-.3, .3))
            last = d


def build(out: str) -> None:
    """Arrange, mix and write the score."""
    # intro pulse
    add(duck, pad([57, 60, 64, 67, 71], DROP, 220, 1400), 0, .32)
    add(dry, np.sin(2 * np.pi * 55 * tt(int(DROP * SR))) * np.clip(tt(int(DROP * SR)) / .4, 0, 1), 0, .08)
    for i, t0 in enumerate(HOOK_WORDS):
        p = pluck(HOOK_ARP[i % len(HOOK_ARP)], .9, 2.6)
        add(dry, p, t0, .32, -.3 + .1 * i)
        add(verb, p, t0, .22)
        add(dry, filt(kick(.55), "lowpass", 400), t0, .5)
    for t0 in HOOK_CARDS:
        for k in range(9):
            add(dry, tick(rng.uniform(2600, 4200), .008), max(0, t0) + .035 * k, .06 * (1 - k / 10), rng.uniform(-.6, .6))
    add(dry, riser(DROP / 2), DROP / 2, .22)
    add(verb, riser(DROP / 2), DROP / 2, .12)
    rv = boom(1, .55)[::-1] * np.linspace(0, 1, int(.55 * SR)) ** 2
    add(dry, filt(rv, "highpass", 120), DROP - .55, .5)

    # grooves
    for g0, g1 in GROOVE:
        for bar in np.arange(g0, g1 - 1e-6, 4 * BEAT):
            _, notes = chord_at(bar)
            add(duck, filt(pad(notes, 4 * BEAT, 900, 2600), "highpass", 180), bar, .36)
        b = g0
        while b < g1 - 1e-6:
            beat = int(round((b - g0) / BEAT))
            root, notes = chord_at(b)
            add(dry, kick(), b, .72)
            duck_env(b)
            if beat % 2 == 1 and b >= CLAPS_FROM:
                add(dry, clap(), b, .36)
                add(verb, clap(), b, .2)
            add(dry, hat(True), b + BEAT / 2, .12, .25)
            if b >= HATS16_FROM:
                for o in (BEAT / 4, 3 * BEAT / 4):
                    add(dry, hat(), b + o, .08, -.3)
            bs = filt(saw(midi(root), int(.22 * SR)), "lowpass", 600) * env(int(.22 * SR), .005, .12)
            add(duck, bs, b + BEAT / 2, .36)
            add(duck, np.sin(2 * np.pi * midi(root) * tt(len(bs))) * env(len(bs), .005, .14), b + BEAT / 2, .3)
            if b >= LEAD_FROM:
                seq = notes + [notes[1] + 12]
                for s in range(2):
                    p = pluck(seq[(beat * 2 + s) % len(seq)] + 12, .35, 1.6)
                    add(dry, p, b + s * BEAT / 2, .1, .4 if s else -.4)
                    add(verb, p, b + s * BEAT / 2, .12)
            b += BEAT

    # impacts
    add(dry, boom(), DROP, .95)
    add(verb, boom(), DROP, .25)
    add(dry, crash(), DROP, .28)
    add(verb, crash(), DROP, .2)
    for t0, s in SECOND_DROPS:
        add(dry, boom(s, 1.6, 64), t0, .8 * s)
        add(dry, crash(1.6), t0, .3 * s)
    add(dry, boom(1, 2.2, 52), BIG_HIT, .95)
    add(dry, crash(2), BIG_HIT, .3)
    add(verb, crash(2), BIG_HIT, .25)
    for _, notes in [chord_at(BIG_HIT)]:
        add(duck, pad(notes, 4 * BEAT, 1400, 4200), BIG_HIT, .42)

    # foley that mirrors the picture
    for tw, d in WHOOSHES:
        w = whoosh(.45)
        seg = np.stack([w * np.linspace(1, .2, len(w)), w * np.linspace(.2, 1, len(w))], 1)
        if d < 0:
            seg = seg[:, ::-1]
        add(dry, seg if d else w, tw - .3, .28)
        add(verb, seg if d else w, tw - .3, .12)
    for r0, r1 in ROLLS:
        roll_ticks(r0, r1)
    for tp in POPS:
        add(dry, pluck(96 + rng.integers(-5, 5), .06, .5), tp, .05, rng.uniform(-.7, .7))
    for i, tg in enumerate(GLISS):
        add(dry, pluck(76 + [0, 3, 7, 10, 12, 15, 19, 22][i % 8], .25, 1.2), tg, .06, .4)

    # breath
    b0, b1 = BREATH
    _, notes = chord_at(b0)
    add(duck, pad(notes, b1 - b0, 2400, 300), b0, .45)
    ty0, ty1, text = TYPING
    for k, ch in enumerate(text, 1):
        if ch != " ":
            add(dry, key_click(), ty0 + k / len(text) * (ty1 - ty0) + rng.uniform(-.008, .008), .16, rng.uniform(-.2, .2))
    add(dry, riser(1.0, 400, 10000), b1 - 1, .28)
    for k in range(16):
        add(dry, clap(), b1 - 1 + (1 - (1 - k / 16) ** 1.6), .05 + .18 * (k / 16) ** 2)

    for i, tq in enumerate(QUAD_POPS):
        p = pluck([81, 84, 88, 91][i % 4], .5, 2)
        add(dry, p, tq, .22, [-.5, .5][i % 2])
        add(verb, p, tq, .18)
    for tf in FLICKERS:
        add(dry, tick(rng.uniform(1800, 5200), .02), tf, .09, rng.uniform(-.8, .8))
    for tw in WORD_HITS:
        add(dry, boom(.8, .7, 70), tw, .45)
        add(dry, clap(), tw, .3)
        add(verb, clap(), tw, .25)
    add(dry, riser(.5, 1200, 12000), CUT - .5, .3)

    # the cut, the slash, the sting
    pre = np.ones(N)
    ci = int(CUT * SR)
    f = int(.06 * SR)
    pre[ci:] = 0
    pre[ci - f:ci] = np.linspace(1, 0, f)
    post = np.zeros((N, 2))
    sn = int(1.6 * SR)
    st = tt(sn)
    shing = filt(noise(sn), "bandpass", [5000, 14000]) * np.exp(-st / .09)
    for fq in (2637, 3951, 5274):
        shing += np.sin(2 * np.pi * fq * st) * np.exp(-st / .5) * .12
    sw = np.r_[whoosh(.3), np.zeros(sn - int(.3 * SR))]
    add(post, np.stack([sw * np.linspace(1, .1, sn) + shing * .5, sw * np.linspace(.1, 1, sn) + shing * .5], 1), CUT - .04, .42)
    add(verb, np.stack([shing, shing], 1), CUT - .04, .3)
    add(post, boom(.6, 1.4, 45), CUT, .5)
    sl = LOGO - (CUT + .35)
    n = int(sl * SR)
    t = tt(n)
    fq = midi(57) * 2 ** (t / sl)
    snake = (np.sin(2 * np.pi * np.cumsum(fq) / SR) + .3 * np.sin(2 * np.pi * np.cumsum(fq * 2.005) / SR)) * (t / sl) ** 1.5
    add(post, snake, CUT + .35, .09)
    add(verb, snake, CUT + .35, .12)
    add(post, riser(sl, 2000, 12000), CUT + .35, .08)
    for nt, g in zip(STING, (.5, .34, .34, .28, .26, .22)):
        b = bell(nt + 12, 4.4)
        add(post, b, LOGO, g * .32, rng.uniform(-.35, .35))
        add(verb, b, LOGO, g * .4)
    add(post, boom(.9, 3, 55), LOGO, .7)
    pe = pad(STING, 4.4, 3500, 600) * np.clip((4.4 - tt(int(4.4 * SR))) / 3, 0, 1)
    add(post, pe, LOGO, .28)
    add(verb, pe, LOGO, .2)
    for i in range(WORDMARK_LETTERS):
        add(post, tick(5000 - i * 250, .01), WORD + i * .045, .05, -.2 + i * .08)
    add(post, bell(88, 2.5), TAG, .06)
    add(verb, bell(88, 2.5), TAG, .1)

    # mix
    mix = dry * pre[:, None] + duck * (DUCK * pre)[:, None] + post
    irn = int(2.6 * SR)
    it = tt(irn)
    ir = np.stack([filt(noise(irn), "lowpass", 7000) * np.exp(-it / .55) for _ in range(2)], 1)
    ir[:int(.012 * SR)] = 0
    wet = np.stack([fftconvolve(verb[:, c], ir[:, c])[:N] for c in range(2)], 1)
    mix += wet / (np.max(np.abs(wet)) + 1e-9) * .22
    mix = filt(mix.T, "highpass", 28).T
    mix /= np.max(np.abs(mix))
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)           # gentle glue — loudness is set later by loudnorm
    mix /= np.max(np.abs(mix)) / .89
    mix[-int(.03 * SR):] *= np.linspace(1, 0, int(.03 * SR))[:, None]
    wavfile.write(out, SR, (mix * 32767).astype(np.int16))
    print(out, "written")


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="score.wav")
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
