"""Generates placeholder chiptune sound effects and music loops.

Run from the project folder:  python3 tools/make_audio.py
Writes assets/sfx/*.wav and assets/music/*.wav. Replace any file with your
own sound of the same name and the game will use it. Pass --only-missing to
keep files you've already replaced.
"""
import math
import random
import struct
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets"
ONLY_MISSING = "--only-missing" in sys.argv
SFX_RATE = 22050
MUSIC_RATE = 22050


# --- Tiny synthesizer --------------------------------------------------------

def note(name):
    """'A4' -> frequency in Hz. Also accepts sharps like 'C#5'."""
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3,
             "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    octave = int(name[-1])
    semis = names[name[:-1]] + (octave - 4) * 12
    return 440.0 * 2 ** (semis / 12)


def square(phase, duty=0.5):
    return 1.0 if (phase % 1.0) < duty else -1.0


def triangle(phase):
    p = phase % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


def tone(freq, seconds, rate, volume=0.3, duty=0.5, slide=0.0, wave_fn="square",
         attack=0.005, release=0.05, vibrato=0.0):
    """A single note. `slide` changes the pitch (Hz per second)."""
    out = []
    phase = 0.0
    n = int(seconds * rate)
    for i in range(n):
        t = i / rate
        f = max(20.0, freq + slide * t) * (1 + vibrato * math.sin(t * 30))
        phase += f / rate
        sample = square(phase, duty) if wave_fn == "square" else triangle(phase)
        env = min(1.0, t / attack) if attack > 0 else 1.0
        env *= min(1.0, (seconds - t) / release) if release > 0 else 1.0
        out.append(sample * volume * max(0.0, env))
    return out


def noise(seconds, rate, volume=0.3, decay=8.0, seed=1, low=0):
    """White noise with an exponential fade (drums, explosions)."""
    rng = random.Random(seed)
    out, held, value = [], 0, 0.0
    for i in range(int(seconds * rate)):
        if held <= 0:
            value = rng.uniform(-1, 1)
            held = low  # hold samples longer for a lower, crunchier sound
        held -= 1
        out.append(value * volume * math.exp(-decay * i / rate))
    return out


def silence(seconds, rate):
    return [0.0] * int(seconds * rate)


def mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for track in tracks:
        for i, s in enumerate(track):
            out[i] += s
    return out


def join(*parts):
    out = []
    for part in parts:
        out.extend(part)
    return out


def write(path, samples, rate):
    if ONLY_MISSING and path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(0.001, max(abs(s) for s in samples))
    scale = min(1.0, 0.95 / peak)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s * scale)) * 32767)) for s in samples))


# --- Sound effects -------------------------------------------------------------

def sfx():
    r = SFX_RATE
    return {
        "shoot": tone(1400, 0.05, r, 0.18, duty=0.25, slide=-9000, release=0.03),
        "kill": join(tone(700, 0.04, r, 0.25, slide=-4000), noise(0.08, r, 0.18, decay=30, low=2)),
        "place": join(tone(330, 0.04, r, 0.3, duty=0.25), tone(495, 0.06, r, 0.3, duty=0.25)),
        "sell": join(tone(495, 0.05, r, 0.3, duty=0.25), tone(330, 0.08, r, 0.3, duty=0.25)),
        "evolve": join(*[tone(note(n), 0.06, r, 0.28, duty=0.25) for n in ("C5", "E5", "G5", "C6")],
                       tone(note("E6"), 0.18, r, 0.25, duty=0.125, vibrato=0.02)),
        "atp": join(tone(note("E6"), 0.04, r, 0.2, duty=0.25), tone(note("B6"), 0.08, r, 0.2, duty=0.25)),
        "wave_start": join(tone(note("G4"), 0.12, r, 0.3), silence(0.03, r), tone(note("C5"), 0.25, r, 0.3)),
        "wave_clear": join(*[tone(note(n), 0.09, r, 0.28, duty=0.25) for n in ("C5", "E5", "G5")],
                           tone(note("C6"), 0.25, r, 0.28, duty=0.25)),
        "base_hit": mix(tone(110, 0.25, r, 0.4, slide=-200, wave_fn="triangle"), noise(0.2, r, 0.3, decay=15, low=6)),
        "bomb": mix(noise(0.6, r, 0.45, decay=5, low=10), tone(90, 0.5, r, 0.35, slide=-120, wave_fn="triangle")),
        "blink": tone(300, 0.12, r, 0.2, duty=0.125, slide=5000),
        # A wet squelch when a spiller gums up a unit.
        "spill": join(noise(0.07, r, 0.22, decay=25, low=8), tone(180, 0.1, r, 0.2, slide=-500, wave_fn="triangle")),
        "deny": join(tone(140, 0.08, r, 0.3), silence(0.03, r), tone(140, 0.1, r, 0.3)),
        "button": tone(880, 0.03, r, 0.15, duty=0.25, release=0.02),
        "win": join(*[tone(note(n), d, r, 0.3, duty=0.25) for n, d in
                      (("C5", 0.12), ("E5", 0.12), ("G5", 0.12), ("C6", 0.3), ("G5", 0.12), ("C6", 0.5))]),
        "lose": join(*[tone(note(n), d, r, 0.3, duty=0.5) for n, d in
                       (("G4", 0.2), ("F#4", 0.2), ("F4", 0.2), ("E4", 0.6))]),
        "victory": join(*[tone(note(n), d, r, 0.3, duty=0.25, vibrato=0.01) for n, d in
                          (("C5", 0.15), ("C5", 0.15), ("C5", 0.15), ("C5", 0.4), ("G#4", 0.4), ("A#4", 0.4),
                           ("C5", 0.2), ("A#4", 0.1), ("C5", 0.8))]),
    }


# --- Music loops ---------------------------------------------------------------

def song(chords, melody_scale, bpm, seed, lead_duty=0.25, drums=True, bars_per_chord=1):
    """A loop: bass on the chord root, an arpeggio, a simple melody and drums.
    `chords` is a list of (root, third, fifth) note names, one per bar."""
    r = MUSIC_RATE
    beat = 60.0 / bpm
    rng = random.Random(seed)
    bass, arp, lead, kit = [], [], [], []
    for chord in chords:
        for _ in range(bars_per_chord):
            root, third, fifth = chord
            for b in range(4):
                bass += tone(note(root[:-1] + str(int(root[-1]) - 1)), beat, r, 0.32, wave_fn="triangle", release=0.08)
                for n in (root, third, fifth, third):
                    arp += tone(note(n), beat / 4, r, 0.07, duty=0.125, release=0.02)
                if drums:
                    hit = noise(beat / 2, r, 0.18 if b % 2 == 0 else 0.1, decay=40 if b % 2 == 0 else 60, seed=b, low=4 if b % 2 == 0 else 0)
                    kit += hit + noise(beat / 2, r, 0.05, decay=80, seed=b + 9)
            # Melody: a few notes from the scale that fit over the chord.
            t = 0.0
            while t < 4 - 1e-6:
                length = rng.choice([0.5, 0.5, 1.0, 1.0, 1.5])
                length = min(length, 4 - t)
                if rng.random() < 0.18:
                    lead += silence(beat * length, r)
                else:
                    pick = rng.choice([root, third, fifth] + melody_scale)
                    lead += tone(note(pick), beat * length, r, 0.12, duty=lead_duty, release=0.06, vibrato=0.006)
                t += length
    return mix(bass, arp, lead, kit if drums else [0.0])


def music():
    return {
        # Calm, a little mysterious.
        "menu": song([("A4", "C5", "E5"), ("F4", "A4", "C5"), ("C4", "E4", "G4"), ("G4", "B4", "D5")] * 2,
                     ["E5", "G5", "A5", "C6"], 96, seed=1, drums=False),
        # Microscopic: minor and floaty.
        "immune_system": song([("D4", "F4", "A4"), ("A#3", "D4", "F4"), ("C4", "E4", "G4"), ("A3", "C#4", "E4")] * 2,
                              ["D5", "F5", "A5", "E5"], 110, seed=2),
        # Backyard: bouncy major.
        "backyard_bugs": song([("G4", "B4", "D5"), ("C4", "E4", "G4"), ("D4", "F#4", "A4"), ("G4", "B4", "D5")] * 2,
                              ["G5", "A5", "B5", "D6"], 128, seed=3, lead_duty=0.125),
        # Farm: folky.
        "wild_kingdom": song([("F4", "A4", "C5"), ("A#3", "D4", "F4"), ("C4", "E4", "G4"), ("F4", "A4", "C5")] * 2,
                             ["F5", "G5", "A5", "C6"], 118, seed=4),
        # Toy war: a little march.
        "total_war": song([("C4", "E4", "G4"), ("G3", "B3", "D4"), ("A3", "C4", "E4"), ("F3", "A3", "C4")] * 2,
                          ["C5", "D5", "E5", "G5"], 132, seed=5, lead_duty=0.5),
        # Space: minor arpeggios.
        # Kitchen: a jaunty, busy little tune.
        "kitchen_defense": song([("D4", "F#4", "A4"), ("G3", "B3", "D4"), ("E4", "G4", "B4"), ("A3", "C#4", "E4")] * 2,
                                ["D5", "E5", "F#5", "A5"], 138, seed=7, lead_duty=0.25),
        "galactic_siege": song([("E4", "G4", "B4"), ("C4", "E4", "G4"), ("A3", "C4", "E4"), ("B3", "D#4", "F#4")] * 2,
                               ["E5", "F#5", "G5", "B5"], 124, seed=6, lead_duty=0.125),
    }


if __name__ == "__main__":
    for name, samples in sfx().items():
        write(ROOT / "sfx" / f"{name}.wav", samples, SFX_RATE)
    for name, samples in music().items():
        write(ROOT / "music" / f"{name}.wav", samples, MUSIC_RATE)
    print("Audio written to", ROOT)
