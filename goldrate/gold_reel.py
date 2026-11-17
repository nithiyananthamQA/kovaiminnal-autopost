"""Gold + silver rate as a REEL (owner 17 Nov, ours - the reference posts the rate as a carousel only: "we need to do this also as a
reel with our best sound effect").

minnal_render.reel_page(p, r) is the design: a 1080x1920 page whose every frame is set by window.seek(t) (numbers land on the
confirmed rate - nothing estimated), window.DUR, window.CUES (sound-effect moments) and window.COVER_T (a fully built frame).
Here: frames at FPS -> H.264 with our own music (reel/assets/music, composed by tools/make_music.py - no copyright; owner 17 Nov:
the upbeat "alert" track, music only). Sound effects at the CUES are synthesized below but switched off (SFX_ON). No voice.

  make(p, r, outdir, log) -> {"mp4": Path, "cover": Path, "dur": seconds}"""
import subprocess, wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MUSIC = HERE.parent / "reel" / "assets" / "music"
SR, FPS = 44100, 30
# owner 17 Nov: "use music we have ... better music no sad music" - our own upbeat track (120 BPM), music only, no sound effects
MOOD = "alert"
SFX_ON = False          # the synthesized effects below stay in the code, switched off
MUSIC_GAIN = 1.0        # the track is mastered at -16 LUFS like our news reels; with no voice it carries the reel
SFX_GAIN = 0.9


def _t(sec):
    return np.arange(int(sec * SR)) / SR


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def _band(x, lo, hi):
    """band-pass by FFT (no filter ringing at the edges of a short effect)"""
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _norm(x, peak):
    m = np.abs(x).max()
    return x / m * peak if m > 0 else x


def sfx_hit():
    """a deep impact: falling sine thump + a short dark noise burst"""
    t = _t(0.45)
    body = np.sin(2 * np.pi * (48 * t + 70 / 28 * (1 - np.exp(-28 * t)))) * np.exp(-7 * t)
    dust = _band(_noise(len(t), 1), 40, 900) * np.exp(-22 * t)
    return _norm(body + 0.5 * _norm(dust, 1), 1.0)


def sfx_whoosh():
    """air moving past: noise whose band rises then falls, swelling in and out"""
    t = _t(0.55)
    n = _noise(len(t), 2)
    lo = _band(n, 300, 1800)
    hi = _band(n, 1800, 6000)
    env = np.sin(np.pi * t / t[-1]) ** 2
    mix = (1 - t / t[-1]) * lo + (t / t[-1]) * hi
    return _norm(mix * env, 0.7)


def sfx_tick():
    """a small bright click as a number lands"""
    t = _t(0.06)
    return _norm((np.sin(2 * np.pi * 2600 * t) + 0.4 * np.sin(2 * np.pi * 5200 * t)) * np.exp(-80 * t), 0.45)


def _bell(f0, sec, seed):
    """a struck metal bell / coin: inharmonic partials, the high ones dying first"""
    t = _t(sec)
    out = np.zeros(len(t))
    for k, (ratio, amp, dec) in enumerate(((1, 1.0, 3.2), (2.76, 0.55, 5.0), (5.40, 0.32, 8.0), (8.93, 0.18, 12.0))):
        ph = np.random.default_rng(seed + k).uniform(0, 2 * np.pi)
        out += amp * np.sin(2 * np.pi * f0 * ratio * t + ph) * np.exp(-dec * t)
    return out * np.minimum(1, t / 0.003)


def sfx_chime():
    """a price lands: two bright bell notes (gold coin shimmer)"""
    a = _bell(1318.5, 1.3, 3)
    b = _bell(1975.5, 1.2, 7)
    out = np.zeros(len(a) + int(0.09 * SR))
    out[:len(a)] += a
    out[int(0.09 * SR):int(0.09 * SR) + len(b)] += 0.8 * b
    return _norm(out, 0.6)


def sfx_riser():
    """build-up before a reveal: a rising tone + rising noise band, getting louder"""
    t = _t(0.9)
    f = 180 + 900 * (t / t[-1]) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    air = _band(_noise(len(t), 4), 2000, 7000)
    env = (t / t[-1]) ** 2
    return _norm((0.6 * tone + 0.4 * _norm(air, 1)) * env * np.minimum(1, (t[-1] - t) / 0.03), 0.55)


SFX = {"hit": sfx_hit, "whoosh": sfx_whoosh, "tick": sfx_tick, "chime": sfx_chime, "riser": sfx_riser}


def effects(cues, dur):
    """one mono track with every cue's effect at its time (unknown kinds are left out)"""
    out = np.zeros(int(dur * SR) + SR)
    made = {}
    for c in cues or []:
        k = c.get("kind")
        if k not in SFX:
            continue
        if k not in made:
            made[k] = SFX[k]()
        x = made[k]
        s = int(max(0.0, float(c.get("t", 0))) * SR)
        if k == "riser":      # a riser ends ON its cue
            s = max(0, s - len(x))
        e = min(len(out), s + len(x))
        if s < e:
            out[s:e] += x[:e - s]
    return out[:int(dur * SR)]


def music_bed(dur, mood=MOOD):
    """our music, looped to the reel's length, faded in 0.4 s and out over the last 1.5 s (None if ffmpeg / the file is missing)"""
    src = MUSIC / f"{mood}.wav"
    if not src.exists():
        src = MUSIC / "calm.wav"
    try:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-i", str(src), "-t", f"{dur:.3f}",
                              "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    except Exception:
        return None
    y = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    n = int(dur * SR)
    y = np.pad(y, (0, max(0, n - len(y))))[:n]
    fi, fo = int(0.03 * SR), int(1.2 * SR)      # starts at once (no quiet first second), fades out at the end
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo)
    return y


def soundtrack(cues, dur, path, log=print):
    """music bed + effects -> 16-bit mono wav; the effects duck the bed by a little so they cut through"""
    fx = effects(cues if SFX_ON else [], dur)
    bed = music_bed(dur)
    if bed is None:
        log("music bed not found - effects only")
        bed = np.zeros(len(fx))
    env = np.convolve(np.abs(fx), np.ones(2205) / 2205, mode="same")      # 50 ms
    duck = 1 - 0.35 * np.clip(env / (env.max() or 1) * 3, 0, 1)
    mix = MUSIC_GAIN * bed * duck + SFX_GAIN * fx
    peak = np.abs(mix).max()
    if peak > 0.95:
        mix *= 0.95 / peak
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    return path


def make(p, r, outdir, log=print):
    import minnal_render
    from playwright.sync_api import sync_playwright      # only here: the test machine has no browser
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    html = outdir / "reel.html"
    html.write_text(minnal_render.reel_page(p, r), encoding="utf-8")
    mp4, cover, wav = outdir / "reel.mp4", outdir / "reel_cover.jpg", outdir / "reel_audio.wav"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(f"file://{html.resolve()}")
        pg.evaluate("document.fonts.ready.then(() => 1)")
        pg.wait_for_timeout(400)
        dur = float(pg.evaluate("window.DUR"))
        cues = pg.evaluate("window.CUES || []")
        cover_t = float(pg.evaluate("window.COVER_T === undefined ? 0 : window.COVER_T"))
        soundtrack(cues, dur, wav, log)
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                                "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", "160k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", str(mp4)],
                               stdin=subprocess.PIPE)
        try:
            for i in range(int(round(dur * FPS))):
                pg.evaluate(f"window.seek({i / FPS:.4f})")
                enc.stdin.write(pg.screenshot(type="jpeg", quality=92))
        finally:
            enc.stdin.close()
            enc.wait()
        if enc.returncode:
            raise RuntimeError("ffmpeg could not make the reel")
        pg.evaluate(f"window.seek({cover_t:.4f})")
        pg.screenshot(path=str(cover), type="jpeg", quality=92)
        b.close()
    log(f"reel {mp4.name}: {dur:.1f} s, {len(cues)} sound cues, cover at {cover_t:.1f} s")
    return {"mp4": mp4, "cover": cover, "dur": dur}
