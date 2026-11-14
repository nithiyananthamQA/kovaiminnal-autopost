#!/usr/bin/env python3
"""Synthesize copyright-free background beds for the Minnal news reels.

Every sound in the output is generated here from oscillators: band-limited
additive waveforms, envelopes, FFT-domain filters and an FFT-convolution
reverb whose impulse response is decaying synthetic noise. No samples, loops,
stock tracks or ML models are used, so the audio is wholly our own.
The output is deterministic (fixed seeds).

Each loop is rendered into a buffer of exactly N whole bars. Note tails,
delays and reverb wrap around modulo that length (circular FFT convolution),
and every oscillator that runs across the loop point completes a whole number
of cycles, so the end flows into the start with no crossfade.

    python make_music.py --out DIR [--voice VOICE.mp3] [--moods serious,alert,calm]

Writes <mood>.wav (stereo loop, -16 LUFS, true peak <= -1.5 dBTP) and, with
--voice, <mood>_with_voice.mp3: 1 s of music, then the voice with the music
14 dB under it while it speaks and back at normal level in its pauses, then
the music fades out 1.5 s after the last word. Needs numpy and ffmpeg.
"""
import argparse
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
TAU = 2 * np.pi
TARGET_LUFS = -16.0
TARGET_TP = -1.5          # dBTP ceiling given to loudnorm
PEAK_MARGIN_DB = 0.5      # loops land at <= -2 dBTP, leaving room for MP3 overshoot
DUCK_DB = -14.0           # music level while the voice speaks, relative to the voice
GAP_S = 0.5               # pauses longer than this bring the music back to normal
DOWN_S, UP_S = 0.12, 0.30 # duck and recover ramp times
LEAD_S = 1.0              # music before the voice starts
TAIL_S = 1.5              # music fade-out after the voice ends
SEEDS = {"serious": 101, "alert": 202, "calm": 303}


# ---------------------------------------------------------------- pitch / time

_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    """'Bb2' -> 46, 'C#3' -> 49 (C4 = 60)."""
    pc, i = _PC[name[0]], 1
    while name[i] in "#b":
        pc += 1 if name[i] == "#" else -1
        i += 1
    return pc + 12 * (int(name[i:]) + 1)


def hz(note):
    m = midi(note) if isinstance(note, str) else note
    return 440.0 * 2 ** ((m - 69) / 12)


class Loop:
    """A loop of whole 4/4 bars; all buses are exactly `n` samples long."""

    def __init__(self, bpm, bars):
        self.bpm, self.bars = bpm, bars
        self.beat = 60.0 / bpm
        self.bar = 4 * self.beat
        self.n = int(round(bars * self.bar * SR))
        self.T = self.n / SR

    def t(self, bar, beat=0.0):
        return bar * self.bar + beat * self.beat

    def bus(self):
        return np.zeros((2, self.n))

    def snap(self, f):
        """Nearest frequency that completes a whole number of cycles per loop."""
        return max(1, round(f * self.T)) / self.T


def pan_gains(p):
    a = (p + 1) * np.pi / 4          # constant power, p in [-1, 1]
    return np.cos(a), np.sin(a)


def place(bus, sig, t0, gain=1.0, pan=0.0):
    """Add a mono or stereo signal at time t0, wrapping past the loop end."""
    sig = np.asarray(sig, dtype=float)
    if sig.ndim == 1:
        gl, gr = pan_gains(pan)
        sig = np.vstack([sig * gl, sig * gr])
    n, m = bus.shape[1], sig.shape[1]
    pos, i = int(round(t0 * SR)) % n, 0
    while i < m:
        k = min(m - i, n - pos)
        bus[:, pos:pos + k] += gain * sig[:, i:i + k]
        i, pos = i + k, 0


# ------------------------------------------------------------------ envelopes

def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def adsr(gate, attack, decay, sustain, release):
    """Raised-cosine attack, exponential decay to sustain, -60 dB release."""
    ng, nr = int(gate * SR), int(release * SR)
    t = np.arange(ng) / SR
    body = sustain + (1 - sustain) * np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-4))
    body = np.where(t < attack, 0.5 - 0.5 * np.cos(np.pi * t / attack), body)
    rel = body[-1] * 10 ** (-3 * np.arange(nr) / SR / release)
    env = np.concatenate([body, rel])
    env[-int(0.005 * SR):] *= np.linspace(1, 0, int(0.005 * SR))
    return env


# ---------------------------------------------------------------- oscillators

def osc(f, n, wave="saw", cutoff=None, order=2, rng=None, vib=None, fmax=6000.0):
    """Band-limited additive oscillator.

    `cutoff` (Hz, scalar or per-sample array) applies a Butterworth-magnitude
    low-pass to each partial, so the filter can move over time. `vib` is a
    per-sample relative frequency deviation (0.01 = +1 %).
    """
    inst = np.full(n, float(f)) if vib is None else f * (1 + vib)
    ph = TAU * np.cumsum(inst) / SR
    out = np.zeros(n)
    for k in range(1, int(min(fmax, 0.45 * SR) / f) + 1):
        if wave == "sine" and k > 1:
            break
        if wave in ("square", "tri") and k % 2 == 0:
            continue
        a = 1.0 / k**2 if wave == "tri" else 1.0 / k
        if cutoff is not None:
            h = 1 / np.sqrt(1 + (k * f / cutoff) ** (2 * order))
            if np.max(h) * a < 1e-3:
                break
            a = a * h
        p0 = rng.uniform(0, TAU) if rng is not None else 0.0
        out += a * np.sin(k * ph + p0)
    return out


def pad_note(f, gate, attack, release, rng, cutoff_fn, t0, wave="saw",
             detune=(-6.0, 0.0, 6.0), pans=(-0.55, 0.0, 0.55), order=3, mix_tri=0.0):
    """Chorused pad note: detuned voices with slow pitch drift, spread in stereo."""
    env = adsr(gate, attack, 0.5, 1.0, release)
    n = len(env)
    t = np.arange(n) / SR
    cutoff = cutoff_fn(t0 + t)
    out = np.zeros((2, n))
    for cents, p in zip(detune, pans):
        drift = 0.0012 * np.sin(TAU * rng.uniform(0.08, 0.2) * t + rng.uniform(0, TAU))
        vib = 2 ** (cents / 1200) * (1 + drift) - 1
        v = osc(f, n, wave, cutoff, order, rng, vib)
        if mix_tri:
            v = (1 - mix_tri) * v + mix_tri * osc(f, n, "tri", cutoff, order, rng, vib)
        gl, gr = pan_gains(p)
        out[0] += v * gl
        out[1] += v * gr
    return out * env / len(detune)


def thump(f_start, f_end, pitch_tau, amp_tau, dur, drive=1.5):
    """Pitch-dropping sine (kick / heartbeat); tanh adds harmonics phones can play."""
    t = np.arange(int(dur * SR)) / SR
    f = f_end + (f_start - f_end) * np.exp(-t / pitch_tau)
    s = np.sin(TAU * np.cumsum(f) / SR)
    s *= (1 - np.exp(-t / 0.002)) * np.exp(-t / amp_tau)
    s = np.tanh(drive * s) / np.tanh(drive)
    s[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return s


def tick(freqs, taus, rng, dur=0.04):
    """Clock tick: a few damped high resonances (all above the voice band)."""
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(TAU * f * t + rng.uniform(0, TAU)) * np.exp(-t / tau)
            for f, tau in zip(freqs, taus))
    return s * (1 - np.exp(-t / 0.0003))


def pluck(f, dur, rng, wave="saw", cut_lo=200.0, cut_hi=1200.0, cut_tau=0.05,
          amp_tau=0.09, order=2):
    """Staccato synth pluck with a decaying filter envelope."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = osc(f, n, wave, cut_lo + cut_hi * np.exp(-t / cut_tau), order, rng)
    s *= (1 - np.exp(-t / 0.002)) * np.exp(-t / amp_tau)
    s[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return s


def epiano(f, vel, rng, dur=1.3):
    """Electric-piano-like tone: sine plus 2nd/3rd harmonics that decay faster."""
    t = np.arange(int(dur * SR)) / SR
    ph = TAU * f * t
    s = (np.sin(ph + rng.uniform(0, TAU)) * np.exp(-t / 0.6)
         + 0.35 * np.sin(TAU * f * 1.0009 * t + rng.uniform(0, TAU)) * np.exp(-t / 0.5)
         + 0.22 * vel * np.sin(2 * ph + rng.uniform(0, TAU)) * np.exp(-t / 0.22)
         + 0.05 * vel * np.sin(3 * ph + rng.uniform(0, TAU)) * np.exp(-t / 0.08))
    s *= (1 - np.exp(-t / 0.003)) * vel
    s[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    return s


def saturate(x, drive):
    """Memoryless tanh drive on a whole stem (loop-safe): tames the crest
    factor and adds harmonics that small phone speakers can reproduce."""
    return np.tanh(drive * x / np.max(np.abs(x))) / np.tanh(drive)


def soft_limit(x, reduce_db, knee_db=3.0):
    """Memoryless soft-knee peak limiter (loop-safe): the highest peak comes
    down by about `reduce_db`; samples more than `knee_db` below that new
    ceiling pass untouched."""
    c = np.max(np.abs(x)) * 10 ** (-reduce_db / 20)
    k = c * 10 ** (-knee_db / 20)
    a = np.abs(x)
    over = k + (c - k) * np.tanh((a - k) / (c - k))
    return np.sign(x) * np.where(a > k, over, a)


def noise_burst(rng, dur, attack, decay):
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(t / attack, 1.0) * np.exp(-np.maximum(t - attack, 0) / decay)
    return rng.standard_normal(len(t)) * env


# -------------------------------------------------------------------- filters

def lowpass(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def highpass(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-6)) ** (2 * order))


def bell(fc, gain_db, width_oct):
    sigma = width_oct / 2.355                     # width given as FWHM in octaves
    return lambda f: 10 ** (gain_db / 20 * np.exp(
        -0.5 * (np.log2(np.maximum(f, 1.0) / fc) / sigma) ** 2))


def fft_filter(x, *responses):
    """Zero-phase, circular filtering: loop-safe because the FFT wraps around."""
    n = x.shape[-1]
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    for r in responses:
        g = g * r(f)
    return np.fft.irfft(np.fft.rfft(x, axis=-1) * g, n, axis=-1)


def sweep_bandpass(x, f0, f1, width_oct=1.2, nfft=2048, hop=512):
    """Band-pass whose centre glides exponentially f0 -> f1 (STFT overlap-add)."""
    n = len(x)
    xp = np.pad(x, (nfft, 2 * nfft))
    win = np.hanning(nfft + 1)[:-1]
    starts = np.arange(0, len(xp) - nfft, hop)
    frames = xp[starts[:, None] + np.arange(nfft)] * win
    centre = np.clip((starts + nfft / 2 - nfft) / n, 0, 1)
    fc = f0 * (f1 / f0) ** centre
    f = np.fft.rfftfreq(nfft, 1 / SR)
    g = np.exp(-0.5 * (np.log2(np.maximum(f, 1.0) / fc[:, None]) / (width_oct / 2.355)) ** 2)
    y_frames = np.fft.irfft(np.fft.rfft(frames, axis=1) * g, nfft, axis=1) * win
    y = np.zeros(len(xp))
    for s, fr in zip(starts, y_frames):
        y[s:s + nfft] += fr
    return y[nfft:nfft + n] / 1.5                 # Hann^2 at 75 % overlap sums to 1.5


# --------------------------------------------------------------------- reverb

def make_ir(rng, rt60, length, predelay=0.02, damp=0.55, bands=7):
    """Stereo noise impulse response; high bands decay faster (air absorption)."""
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal((2, n))
    f = np.fft.rfftfreq(n, 1 / SR)
    centres = np.linspace(np.log2(120), np.log2(8000), bands)
    logf = np.log2(np.clip(f, 20, 20000))
    spec = np.fft.rfft(noise, axis=1)
    ir = np.zeros((2, n))
    for b in range(bands):
        weight = np.interp(logf, centres, np.eye(bands)[b])   # partition of unity
        rt = rt60 * (1 - damp * b / (bands - 1))
        ir += np.fft.irfft(spec * weight, n, axis=1) * 10 ** (-3 * t / rt)
    ir *= 1 - np.exp(-t / 0.006)
    ir = np.concatenate([np.zeros((2, int(predelay * SR))), ir], axis=1)
    return ir / np.sqrt(np.mean(np.sum(ir**2, axis=1)))


def circ_conv(x, ir):
    """Per-channel circular convolution over the loop length (tails wrap)."""
    n = x.shape[1]
    return np.fft.irfft(np.fft.rfft(x, axis=1) * np.fft.rfft(ir, n, axis=1), n, axis=1)


def pingpong(x, delay_s, feedback, repeats, lp_hz=2500):
    """Circular ping-pong delay (wet only); repeats darken each time."""
    d = int(round(delay_s * SR))
    wet = np.zeros_like(x)
    tap = x
    for _ in range(repeats):
        tap = fft_filter(np.roll(tap, d, axis=1)[::-1], lowpass(lp_hz, 1)) * feedback
        wet += tap
    return wet


def mixdown(loop, stems, rng, rt60, wet_db, predelay=0.02, damp=0.55):
    """stems: name -> (bus, level_db, reverb_send). Each stem is first set to
    -20 dBFS RMS so `level_db` is its level relative to the others."""
    dry, send = loop.bus(), loop.bus()
    for bus, level_db, send_amt in stems.values():
        s = bus * (0.1 / np.sqrt(np.mean(bus**2))) * 10 ** (level_db / 20)
        dry += s
        send += s * send_amt
    ir = make_ir(rng, rt60, min(1.3 * rt60, 0.8 * loop.T), predelay, damp)
    wet = fft_filter(circ_conv(send, ir), highpass(160, 2), lowpass(5000, 2))
    out = dry + wet * 10 ** (wet_db / 20)
    # Rumble cut, and a broad dip where the voice lives (about 1-4.5 kHz).
    out = fft_filter(out, highpass(28, 2), bell(2300, -4.0, 2.0))
    return out * (0.5 / np.max(np.abs(out)))


# ---------------------------------------------------------------------- moods

def serious(rng):
    """Crime / accidents: 80 BPM, D minor, Dm-Bb-Gm-A (2 bars each)."""
    L = Loop(80, 8)
    t_all = np.arange(L.n) / SR

    # Dark pad, cutoff breathing twice per loop (750-1100 Hz). Inner voice
    # D4 -> C#4 and top line F4 F4 G4 E4; the soft chord root leaves the low
    # end to the drone, and the mid register keeps it audible on phones.
    pad = L.bus()
    cutoff = lambda ta: 750 + 350 * (0.5 - 0.5 * np.cos(TAU * 2 * ta / L.T))
    chords = [(0, ["D3", "A3", "D4", "F4"]), (2, ["Bb2", "F3", "D4", "F4"]),
              (4, ["G2", "Bb3", "D4", "G4"]), (6, ["A2", "A3", "C#4", "E4"])]
    for bar, notes in chords:
        t0 = L.t(bar) - 0.5
        for i, nm in enumerate(notes):
            place(pad, pad_note(hz(nm), 2 * L.bar, 1.6, 2.8, rng, cutoff, t0, mix_tri=0.35), t0,
                  gain=0.55 if i == 0 else 1.0)

    # D pedal drone: whole cycles per loop; a partner 6 cycles off gives slow beating.
    f, f_low = L.snap(hz("D2")), L.snap(hz("D1"))
    sub = (np.sin(TAU * f * t_all) + 0.55 * np.sin(TAU * (f + 6 / L.T) * t_all + 1.0)
           + 0.25 * np.sin(TAU * f_low * t_all)
           + 0.32 * np.sin(TAU * 2 * f * t_all + 0.5) + 0.10 * np.sin(TAU * 3 * f * t_all + 2.0))
    sub *= 0.82 + 0.18 * np.sin(TAU * 4 / L.T * t_all - np.pi / 2)
    drone = np.vstack([sub, sub])

    # Heartbeat on every beat (80 BPM is a resting heart rate): lub ... dub.
    hb = L.bus()
    lub = thump(92, 48, 0.035, 0.09, 0.45, drive=3.0)
    dub = thump(80, 45, 0.03, 0.075, 0.4, drive=3.0)
    for b in range(L.bars * 4):
        v = (1.0 if b % 4 == 0 else 0.82) * rng.uniform(0.95, 1.05)
        place(hb, lub * v, b * L.beat)
        place(hb, dub * 0.62 * v, b * L.beat + 0.2)
    hb = fft_filter(hb, lowpass(600, 2))

    # Very quiet clock: tick-tock on eighth notes, all energy above 4.5 kHz.
    ticks = L.bus()
    tick_hi = tick((6100, 8300, 10400), (0.0025, 0.0018, 0.0012), rng)
    tick_lo = tick((5200, 7100, 9300), (0.0028, 0.002, 0.0012), rng)
    for e in range(L.bars * 8):
        place(ticks, (tick_hi if e % 2 == 0 else tick_lo) * rng.uniform(0.85, 1.0),
              e * L.beat / 2, pan=0.25 if e % 2 == 0 else -0.25)
    ticks = fft_filter(ticks, highpass(4500, 4))

    stems = {"pad": (pad, 0.0, 0.55), "drone": (drone, -9.0, 0.0),
             "heartbeat": (hb, -12.0, 0.12), "ticks": (ticks, -27.0, 0.5)}
    return L, mixdown(L, stems, rng, rt60=3.2, wet_db=-6.0, predelay=0.03, damp=0.6)


def alert(rng):
    """Power cuts / urgent: 120 BPM, E minor, Em-C-Am-B-C-B (2 bars each)."""
    L = Loop(120, 12)
    t_all = np.arange(L.n) / SR
    prog = [  # bar, pad voicing, bass root, arpeggio tones
        (0, ["B3", "E4", "G4"], "E2", ["B3", "E4", "G4", "B4"]),
        (2, ["C4", "E4", "G4"], "C2", ["C4", "E4", "G4", "C5"]),
        (4, ["C4", "E4", "A4"], "A1", ["A3", "C4", "E4", "A4"]),
        (6, ["B3", "D#4", "F#4"], "B1", ["B3", "D#4", "F#4", "B4"]),
        (8, ["C4", "E4", "G4"], "C2", ["C4", "E4", "G4", "C5"]),
        (10, ["B3", "D#4", "F#4"], "B1", ["B3", "D#4", "F#4", "B4"]),
    ]

    pad, bass, arp = L.bus(), L.bus(), L.bus()
    cutoff = lambda ta: 950 + 200 * np.sin(TAU * 3 * ta / L.T)
    arp_order = [0, 1, 2, 3, 2, 1, 0, 1]
    for bar, voicing, root, tones in prog:
        t0 = L.t(bar)
        for nm in voicing:
            place(pad, pad_note(hz(nm), 2 * L.bar, 0.25, 0.8, rng, cutoff, t0,
                                detune=(-8.0, 8.0), pans=(-0.6, 0.6)), t0)
        for e in range(16):                    # tight eighth-note octave pulse
            f = hz(midi(root) + 12 * (e % 2))
            v = 1.0 if e % 2 == 0 else 0.72
            place(bass, pluck(f, 0.2, rng, cut_lo=320, cut_hi=1400, amp_tau=0.07) * v,
                  t0 + e * L.beat / 2)
        for s in range(32):                    # soft sixteenth arpeggio
            nm = tones[arp_order[s % 8]]
            v = (0.9 if s % 4 == 0 else 0.6) * rng.uniform(0.9, 1.0)
            place(arp, pluck(hz(nm), 0.16, rng, wave="tri", cut_lo=500, cut_hi=900,
                             cut_tau=0.03, amp_tau=0.05) * v,
                  t0 + s * L.beat / 4, pan=0.3 * np.sin(TAU * s / 16))
    arp = fft_filter(arp, lowpass(1800, 2))
    bass = saturate(bass, 2.5)

    # Pad ducks a little on every beat (sidechain pump) for forward motion.
    since = np.mod(t_all, L.beat)
    pad *= 1 - 0.35 * np.exp(-since / 0.14) * (1 - np.exp(-since / 0.004))

    # Soft kick on every beat.
    kick = L.bus()
    k = thump(110, 48, 0.028, 0.15, 0.4, drive=1.6)
    for b in range(L.bars * 4):
        place(kick, k * (1.0 if b % 4 == 0 else 0.85), b * L.beat)
    kick = fft_filter(kick, lowpass(500, 2))

    # Clock-tick hi-hat on eighths: downbeat "tick", accented off-beat "tock".
    hat = L.bus()
    t_on = tick((7200, 9100, 11500), (0.0016, 0.0012, 0.0009), rng)
    t_off = tick((6300, 8600, 10800), (0.002, 0.0014, 0.001), rng)
    for e in range(L.bars * 8):
        place(hat, t_on * 0.6 if e % 2 == 0 else t_off, e * L.beat / 2,
              pan=-0.2 if e % 2 == 0 else 0.2)
    hat = fft_filter(hat, highpass(5500, 4))

    # Small riser in the last bar of every 4-bar phrase, plus a soft low hit
    # on the downbeat it lands on.
    riser, hit = L.bus(), L.bus()
    boom = thump(62, 34, 0.08, 0.5, 1.4, drive=1.3)
    for phrase in range(L.bars // 4):
        t0 = L.t(4 * phrase + 3)
        n = int(L.bar * SR)
        swell = np.linspace(0, 1, n) ** 2.5
        swell[-int(0.015 * SR):] *= np.linspace(1, 0, int(0.015 * SR))
        x = np.vstack([sweep_bandpass(rng.standard_normal(n), 220, 1600, 1.2) for _ in "LR"])
        place(riser, x * swell, t0)
        place(hit, boom, L.t(4 * phrase + 4))
    riser = fft_filter(riser, lowpass(2200, 2))

    stems = {"bass": (bass, 0.0, 0.1), "pad": (pad, -3.0, 0.35), "arp": (arp, -4.0, 0.4),
             "kick": (kick, -9.0, 0.05), "hat": (hat, -22.0, 0.25),
             "riser": (riser, -13.0, 0.6), "hit": (hit, -18.0, 0.25)}
    return L, mixdown(L, stems, rng, rt60=1.7, wet_db=-8.0, predelay=0.015, damp=0.5)


def calm(rng):
    """City / civic / general: 90 BPM, C major, Cmaj7-Am7-Fmaj7-G6-Cmaj7-Em7-Fmaj7-Gsus4."""
    L = Loop(90, 8)
    prog = [  # pad voicing, bass root, arpeggio tones (low -> high)
        ([48, 55, 59, 64], "C2", [60, 64, 67, 71, 72]),     # Cmaj7
        ([45, 52, 55, 60], "A1", [57, 60, 64, 67, 69]),     # Am7
        ([48, 52, 57, 60], "F2", [57, 60, 64, 65, 69]),     # Fmaj7
        ([50, 55, 59, 64], "G2", [55, 59, 62, 64, 67]),     # G6
        ([48, 55, 59, 64], "C2", [60, 64, 67, 71, 72]),     # Cmaj7
        ([47, 52, 55, 62], "E2", [59, 62, 64, 67, 71]),     # Em7
        ([48, 52, 57, 60], "F2", [57, 60, 64, 65, 69]),     # Fmaj7
        ([50, 55, 60, 62], "G2", [55, 60, 62, 67, 72]),     # Gsus4
    ]
    pad, bass, ep, shaker = L.bus(), L.bus(), L.bus(), L.bus()
    cutoff = lambda ta: 1250 + 250 * np.sin(TAU * 2 * ta / L.T)
    pattern = [0, 2, 3, 4, 1, 3, 2, 4]          # eighth-note e-piano figure
    for bar, (voicing, root, tones) in enumerate(prog):
        t0 = L.t(bar)
        for m in voicing:
            place(pad, pad_note(hz(m), L.bar + 0.3, 0.9, 1.8, rng, cutoff, t0 - 0.3,
                                wave="saw", mix_tri=0.6), t0 - 0.3)
        r = hz(root)
        for beat, length, mult in ((0, 1.8, 1.0), (2, 1.0, 1.0), (3, 0.9, 1.5)):
            env = adsr(length * L.beat - 0.12, 0.012, 0.4, 0.6, 0.12)
            t = np.arange(len(env)) / SR
            f = r * mult
            s = (np.sin(TAU * f * t) + 0.3 * np.sin(TAU * 2 * f * t) + 0.08 * np.sin(TAU * 3 * f * t))
            s *= env
            place(bass, s * (1.0 if beat == 0 else 0.75), t0 + beat * L.beat)
        for e, idx in enumerate(pattern):
            v = (0.85 if e % 2 == 0 else 0.62) * rng.uniform(0.9, 1.05)
            place(ep, epiano(hz(tones[idx]), v, rng), t0 + e * L.beat / 2,
                  pan=0.35 * np.sin(TAU * (bar * 8 + e) / 16))
    ep = ep + 0.45 * pingpong(ep, 0.75 * L.beat, 0.55, 3)

    # Light shaker on sixteenths, accent on the off-beat eighth.
    accents = [0.45, 0.25, 0.85, 0.3]
    for s in range(L.bars * 16):
        burst = noise_burst(rng, 0.09, 0.006, 0.03) * accents[s % 4] * rng.uniform(0.85, 1.05)
        place(shaker, burst, s * L.beat / 4, pan=0.15)
    shaker = fft_filter(shaker, highpass(5500, 4), lowpass(11000, 2))

    stems = {"pad": (pad, 0.0, 0.4), "bass": (bass, -8.0, 0.05),
             "epiano": (ep, 1.0, 0.45), "shaker": (shaker, -23.0, 0.2)}
    return L, mixdown(L, stems, rng, rt60=2.2, wet_db=-7.0, predelay=0.025, damp=0.55)


MOODS = {
    "serious": (serious, "80 BPM, D minor (Dm-Bb-Gm-A)"),
    "alert": (alert, "120 BPM, E minor (Em-C-Am-B-C-B)"),
    "calm": (calm, "90 BPM, C major (Cmaj7-Am7-Fmaj7-G6-Cmaj7-Em7-Fmaj7-Gsus4)"),
}


# --------------------------------------------------------------------- ffmpeg

def _ffmpeg(args, data=None):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], input=data,
                       capture_output=True, check=True)
    return p.stdout, p.stderr.decode(errors="replace")


def _raw_input(x):
    x = np.atleast_2d(x)
    return (["-f", "f32le", "-ar", str(SR), "-ac", str(x.shape[0]), "-i", "pipe:0"],
            np.ascontiguousarray(x.T, dtype="<f4").tobytes())


def _source(src):
    return (["-i", str(src)], None) if isinstance(src, (str, Path)) else _raw_input(src)


def loudnorm_json(src, extra=""):
    args, data = _source(src)
    af = f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=11:print_format=json{extra}"
    _, err = _ffmpeg([*args, "-af", af, "-f", "null", "-"], data)
    return json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err)[-1])


PHONE_BAND = "highpass=f=250:poles=2,highpass=f=250:poles=2,highpass=f=250:poles=2,"


def ebur128(src, frames=False, pre=""):
    """Integrated loudness, true peak and sample peak (+ momentary values).
    `pre` is an optional filter chain applied before metering."""
    args, data = _source(src)
    af = pre + "ebur128=peak=true+sample" + (":framelog=info" if frames else "")
    _, err = _ffmpeg([*args, "-af", af, "-f", "null", "-"], data)
    summary = err[err.rfind("Summary:"):]
    num = lambda pat: float(re.search(pat, summary, re.S).group(1))
    out = {"I": num(r"I:\s+(-?[\d.]+|-inf) LUFS"),
           "TP": num(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf)"),
           "SP": num(r"Sample peak:\s+Peak:\s+(-?[\d.]+|-inf)")}
    if frames:
        out["M"] = [float(v) for v in re.findall(r"M:\s*(-?[\d.]+|-inf)\s+S:", err[:err.rfind("Summary:")])]
    return out


def decode(path, channels):
    raw, _ = _ffmpeg(["-i", str(path), "-f", "f32le", "-ac", str(channels), "-ar", str(SR), "pipe:1"])
    return np.frombuffer(raw, dtype="<f4").reshape(-1, channels).T.astype(float)


def write_wav(path, x, rng):
    """16-bit PCM with TPDF dither."""
    pcm = x.T * 32767 + rng.random(x.T.shape) - rng.random(x.T.shape)
    pcm = np.clip(np.round(pcm), -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[0])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return pcm.T


def encode_mp3(path, x):
    args, data = _raw_input(x)
    _ffmpeg(["-y", *args, "-c:a", "libmp3lame", "-b:a", "192k", str(path)], data)


# --------------------------------------------------------------- build steps

def normalize(x):
    """Two-pass loudnorm: measure, confirm the linear (pure gain) mode applies,
    then apply that same gain here so no resampling touches the loop seam.
    If the gain would push the true peak past the ceiling, the mix's few
    highest peaks are soft-limited first (memoryless, so the loop stays exact)."""
    limited = 0.0
    for _ in range(4):
        m = loudnorm_json(x)
        excess = float(m["input_tp"]) + TARGET_LUFS - float(m["input_i"]) - (TARGET_TP - PEAK_MARGIN_DB)
        if excess <= 0:
            break
        x = soft_limit(x, excess + 0.2)
        limited += excess + 0.2
    else:
        m = loudnorm_json(x)
    p2 = loudnorm_json(x, f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
                          f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
                          f":offset={m['target_offset']}:linear=true")
    if p2["normalization_type"] != "linear":
        raise SystemExit(f"loudnorm would go dynamic (input TP {m['input_tp']}, I {m['input_i']}); "
                         "reduce transient levels in the mix")
    gain_db = TARGET_LUFS - float(m["input_i"])
    return x * 10 ** (gain_db / 20), limited


def analyse(x):
    """Share of energy in the 1-4 kHz voice band, spectral centroid, onset rate."""
    mono = x.mean(axis=0)
    f = np.fft.rfftfreq(len(mono), 1 / SR)
    p = np.abs(np.fft.rfft(mono)) ** 2
    audible = f >= 20
    share = p[(f >= 1000) & (f < 4000)].sum() / p[audible].sum()
    centroid = (f[audible] * p[audible]).sum() / p[audible].sum()
    nfft, hop = 1024, 512
    frames = mono[np.arange(0, len(mono) - nfft, hop)[:, None] + np.arange(nfft)] * np.hanning(nfft)
    mag = np.log1p(100 * np.abs(np.fft.rfft(frames, axis=1)))
    flux = np.maximum(np.diff(mag, axis=0), 0).sum(axis=1)
    thr = np.median(flux) + 1.5 * flux.std()
    peaks = (flux[1:-1] > thr) & (flux[1:-1] >= flux[:-2]) & (flux[1:-1] >= flux[2:])
    return share, centroid, peaks.sum() / (len(mono) / SR)


def seam_check(pcm):
    """Step across the loop point vs the 99.9th-percentile step inside the loop."""
    pcm = pcm.astype(float)
    junction = np.abs(pcm[:, 0] - pcm[:, -1]).max()
    return junction, np.percentile(np.abs(np.diff(pcm, axis=1)), 99.9)


def prepare_voice(path):
    """Voice to -16 LUFS (two-pass loudnorm; its peak limiting acts on the voice
    stem only), mono 44.1 kHz, plus the speech onset/offset times."""
    m = loudnorm_json(path)
    af = (f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=11:measured_I={m['input_i']}"
          f":measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    raw, _ = _ffmpeg(["-i", str(path), "-af", af, "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"])
    v = np.frombuffer(raw, dtype="<f4").astype(float)
    hop = int(0.01 * SR)
    rms = np.sqrt(np.mean(v[:len(v) // hop * hop].reshape(-1, hop) ** 2, axis=1))
    active = np.flatnonzero(20 * np.log10(rms + 1e-12) > -45)
    return v, active[0] * hop / SR, (active[-1] + 1) * hop / SR


def with_voice(music, loop_n, voice, onset, offset):
    """Music under the voice, ducked from the voice's own activity: normal level
    for the 1 s intro, in every pause longer than GAP_S and after the last word;
    DUCK_DB (re the voice) while it speaks; silent TAIL_S after the voice ends.
    Returns the mix, both stems and a mask of the samples where speech is ducked."""
    speech = offset - onset
    n = int(round((LEAD_S + speech + TAIL_S) * SR))
    t = np.arange(n) / SR
    bed = np.tile(music, int(np.ceil(n / loop_n)))[:, :n]

    v = np.zeros(n)
    start = int(round((LEAD_S - onset) * SR))
    seg = voice[max(0, -start):][:n - max(0, start)]
    v[max(0, start):max(0, start) + len(seg)] = seg
    vox = np.vstack([v, v]) * np.sqrt(0.5)    # mono -16 LUFS -> stereo -16 LUFS

    # Voice activity per 10 ms frame; short gaps between words stay ducked.
    hop_s, hop = 0.01, int(0.01 * SR)
    nfr = -(-n // hop)
    vp = np.pad(v, (0, nfr * hop - n))
    act = 20 * np.log10(np.sqrt(np.mean(vp.reshape(nfr, hop) ** 2, axis=1)) + 1e-12) > -45
    idx = np.flatnonzero(act)
    for a, gap in zip(idx[:-1], np.diff(idx) - 1):
        if 0 < gap * hop_s <= GAP_S:
            act[a + 1:a + 1 + gap] = True
    # Start ducking DOWN_S before each phrase (so it is fully down when the
    # word starts) and hold 0.1 s after it.
    lead, hold = round(DOWN_S / hop_s), round(0.1 / hop_s)
    near = np.convolve(act.astype(float), np.ones(lead + hold + 1))[lead:lead + nfr] > 0.5
    target = np.where(near, DUCK_DB, 0.0)
    g_db, cur = np.empty(nfr), 0.0
    for i, tg in enumerate(target):           # ramps linear in dB
        cur = max(tg, cur + DUCK_DB * hop_s / DOWN_S) if tg < cur else min(tg, cur - DUCK_DB * hop_s / UP_S)
        g_db[i] = cur
    g_db = np.interp(t, (np.arange(nfr) + 0.5) * hop_s, g_db)

    off = LEAD_S + speech
    fade = np.where(t < off + 0.3, 1.0,
                    np.cos(0.5 * np.pi * smoothstep((t - off - 0.3) / (TAIL_S - 0.3))) ** 2)
    bed_ducked = bed * 10 ** (g_db / 20) * fade * smoothstep(t / 0.12)
    speaking = np.repeat(act, hop)[:n]
    return vox + bed_ducked, vox, bed_ducked, speaking


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--voice", type=Path, help="voice file for the *_with_voice.mp3 demos")
    ap.add_argument("--moods", default=",".join(MOODS))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    voice = prepare_voice(args.voice) if args.voice else None
    if voice:
        vm = ebur128(voice[0])
        print(f"voice: {vm['I']:.1f} LUFS, TP {vm['TP']:.1f} dBTP, "
              f"speech {voice[1]:.2f}-{voice[2]:.2f} s")

    for name in args.moods.split(","):
        build, desc = MOODS[name]
        rng = np.random.default_rng(SEEDS[name])
        loop, mix = build(rng)
        mix, limited_db = normalize(mix)
        wav = args.out / f"{name}.wav"
        pcm = write_wav(wav, mix, rng)

        m = ebur128(wav)
        phone = ebur128(wav, pre=PHONE_BAND)["I"]
        clipped = int(np.sum(np.abs(pcm) >= 32767))
        junction, typical = seam_check(pcm)
        share, centroid, onsets = analyse(mix)
        print(f"\n{name}: {desc}, {loop.bars} bars = {loop.T:.2f} s")
        print(f"  {wav}: {m['I']:.1f} LUFS, TP {m['TP']:.1f} dBTP, sample peak {m['SP']:.1f} dBFS, "
              f"clipped samples {clipped}, peak limiting {limited_db:.1f} dB, "
              f"above 250 Hz {phone:.1f} LUFS")
        print(f"  loop seam step {junction:.0f} vs p99.9 step {typical:.0f} (LSB); "
              f"1-4 kHz energy {100 * share:.1f} %, centroid {centroid:.0f} Hz, "
              f"onsets {onsets:.1f}/s")

        if voice:
            mixed, vox, bed, speaking = with_voice(pcm / 32767.0, loop.n, *voice)
            mp3 = args.out / f"{name}_with_voice.mp3"
            encode_mp3(mp3, mixed)
            win = speaking
            mv, mb = ebur128(vox[:, win]), ebur128(bed[:, win], frames=True)
            final = ebur128(mp3)
            dec = decode(mp3, 2)
            print(f"  {mp3}: {final['I']:.1f} LUFS, TP {final['TP']:.1f} dBTP, "
                  f"decoded peak {20 * np.log10(np.abs(dec).max()):.1f} dBFS, {dec.shape[1] / SR:.1f} s")
            print(f"  while speaking: voice {mv['I']:.1f} LUFS, music {mb['I']:.1f} LUFS "
                  f"-> {mv['I'] - mb['I']:.1f} dB below (loudest 400 ms of music "
                  f"{mv['I'] - max(mb['M']):.1f} dB below)")


if __name__ == "__main__":
    main()
