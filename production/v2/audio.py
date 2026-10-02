"""Offline 96 BPM score and one uncut ElevenLabs performance for Pepe2Pepe V2.

Uses only Python's standard library and an installed FFmpeg with the afir filter.
Run from repository root: python production/v2/audio.py
For a non-destructive check: python production/v2/audio.py --output-dir test/scratch/audio
No network, external samples, TTS calls, or speech time stretching are required.
"""
from array import array
import argparse
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

SR = 48000
DURATION = 20
N = SR * DURATION
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
FF = shutil.which('ffmpeg') or 'ffmpeg'
PI = math.pi
TAU = 2 * PI


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def zeros(n):
    return array('d', [0.]) * n


def place(target, sound, start, gain=1., pan=0.):
    """Equal-power stereo placement; the score and mix are interleaved doubles."""
    first = round(start * SR)
    if first >= N:
        return
    angle = (pan + 1) * PI / 4
    left = gain * math.cos(angle)
    right = gain * math.sin(angle)
    for j in range(min(len(sound), N - first)):
        index = 2 * (first + j)
        target[index] += sound[j] * left
        target[index + 1] += sound[j] * right


def piano(midi, velocity, length=4.2):
    """Damped inharmonic string modes; restrained highs, soft felt attack."""
    n = round(SR * length)
    sound = zeros(n)
    f = hz(midi)
    for partial, weight in enumerate([1., .31, .12, .065, .025, .011], 1):
        freq = f * partial * math.sqrt(1 + .00006 * partial * partial)
        decay = 1.8 / (1 + .30 * partial) * (440 / f) ** .14
        step = TAU * freq / SR
        damping = math.exp(-1 / (SR * decay))
        amplitude = weight
        for i in range(n):
            sound[i] += math.sin(step * i) * amplitude
            amplitude *= damping
    for i in range(n):
        sound[i] *= (1 - math.exp(-i / (SR * .009))) * velocity
    return sound


def pad(midi, length=6.8):
    f = hz(midi)
    sound = zeros(round(SR * length))
    for i in range(len(sound)):
        t = i / SR
        phase = TAU * f * t
        value = (math.sin(phase + .007 * math.sin(TAU * .21 * t))
                 + .40 * math.sin(phase * 1.0017 + .5)
                 + .34 * math.sin(phase * .9982 + 1.2)
                 + .10 * math.sin(2 * phase + .3)) / 1.84
        envelope = math.sin(min(t / .9, 1) * PI / 2) ** 2
        envelope *= min(1, max(0, (length - t) / 2.5)) ** 1.4
        sound[i] = value * envelope
    return sound


def smooth(sound, width):
    """Centered box FIR with zero padding, equivalent to a same-size convolution."""
    half = width // 2
    result = zeros(len(sound))
    running = sum(sound[:half + 1])
    for i in range(len(sound)):
        result[i] = running / width
        before = i - half
        after = i + half + 1
        if before >= 0:
            running -= sound[before]
        if after < len(sound):
            running += sound[after]
    return result


def little_bytes(values):
    if sys.byteorder == 'little':
        return values.tobytes()
    result = array(values.typecode, values)
    result.byteswap()
    return result.tobytes()


def doubles(raw):
    result = array('d')
    result.frombytes(raw)
    if sys.byteorder != 'little':
        result.byteswap()
    return result


def room(score, rng, temporary):
    """Original filtered-noise room impulse, convolved efficiently by FFmpeg.

    A unit impulse at sample zero retains the direct sound. Disabling afir's IR
    normalization preserves the explicit reflection gains and room level.
    """
    length = round(1.8 * SR)
    impulse = zeros(length * 2)
    for channel in range(2):
        noise = array('d', (rng.gauss(0, 1) * math.exp(-i / (SR * .28))
                            for i in range(length)))
        filtered = smooth(noise, 29)
        for i in range(round(.035 * SR), length):
            impulse[2 * i + channel] = filtered[i] * .003
        for seconds, amplitude in [(.047, .07), (.071, .05), (.101, .03)]:
            impulse[2 * round((seconds + channel * .009) * SR) + channel] += amplitude
        impulse[channel] = 1.
    dry_path, ir_path = temporary / 'dry.f64le', temporary / 'room.f64le'
    dry_path.write_bytes(little_bytes(score))
    ir_path.write_bytes(little_bytes(impulse))
    raw = subprocess.check_output([
        FF, '-v', 'error', '-f', 'f64le', '-ar', str(SR), '-ac', '2',
        '-i', str(dry_path), '-f', 'f64le', '-ar', str(SR), '-ac', '2',
        '-i', str(ir_path), '-filter_complex',
        '[0:a][1:a]afir=irnorm=-1:irgain=1:dry=1:wet=1:precision=double',
        '-t', str(DURATION), '-f', 'f64le', '-'])
    result = doubles(raw)
    if len(result) != 2 * N:
        raise RuntimeError(f'Room convolution returned {len(result)} samples, expected {2 * N}')
    return result


def compose(temporary):
    rng = random.Random(57321)
    score = zeros(N * 2)
    # Spacious eight-bar harmony, voiced in an intimate middle register.
    chords = [(0., [50, 57, 61, 66]), (5., [47, 54, 57, 62]),
              (10., [43, 55, 59, 62]), (15., [45, 55, 59, 64]),
              (17.5, [50, 57, 61, 66])]
    for start, notes in chords:
        gain = .013 if start == 15 else .020
        length = 4.9 if start == 15 else 6.9
        for i, note in enumerate(notes):
            place(score, pad(note, length), start, gain, -.6 + i * .4)

    # Humanized felt-key motif; wide rests give the voice space.
    melody = [(0.10,69,.070,-.18),(.79,73,.037,.22),(2.52,66,.050,-.22),
              (3.78,69,.034,.12),(5.07,71,.045,.12),(6.38,69,.030,-.1),
              (7.59,66,.034,-.2),(8.83,64,.028,.15),(10.05,67,.047,-.2),
              (11.33,69,.034,.15),(12.59,74,.025,.25),(13.23,71,.025,.1),
              (15.04,76,.023,.1),(16.30,74,.022,-.18),
              (17.54,69,.050,.16),(18.15,66,.034,-.16),(18.80,62,.033,0)]
    for at, note, velocity, pan in melody:
        place(score, piano(note, velocity), at, 1, pan)

    # Soft bass entries keep the low end grounded without a club side-chain.
    for at, note in [(0,38),(5,35),(10,31),(15,33),(17.5,38)]:
        length = min(4.6, 20 - at)
        sound = zeros(round(length * SR))
        for i in range(len(sound)):
            t = i / SR
            envelope = (1 - math.exp(-t / .12)) * min(1, max(0, (length - t) / .9))
            envelope *= math.exp(-t / 5.)
            sound[i] = (math.sin(TAU * hz(note) * t) + .13 * math.sin(2 * TAU * hz(note) * t)) * envelope
        place(score, sound, at, .024, 0)

    # Restrained heartbeat/paper-brush groove enters after the poster establishes.
    beat = 60 / 96
    for k in range(8, 28):
        at = k * beat
        if k % 2 == 0 and not 22 <= k <= 25:
            sound = zeros(round(.32 * SR))
            for i in range(len(sound)):
                t = i / SR
                phase = TAU * (48 * t + 17 * .045 * (1 - math.exp(-t / .045)))
                envelope = (1 - math.exp(-t / .004)) * math.exp(-t / .070)
                sound[i] = math.sin(phase) * envelope
            place(score, sound, at, .041, 0)
        if k % 4 == 2 and k < 22:
            noise = array('d', (rng.gauss(0, 1) for _ in range(round(.15 * SR))))
            low = smooth(noise, 27)
            high = array('d', (x - y for x, y in zip(noise, low)))
            brush = smooth(high, 5)
            for i in range(len(brush)):
                t = i / SR
                brush[i] *= (1 - math.exp(-t / .004)) * math.exp(-t / .022)
            place(score, brush, at + .013, .025, .20)

    # One soft porcelain-like IMD accent, not a transition whoosh.
    place(score, piano(81, .012, 2.7), 14.12, 1, .38)
    score = room(score, rng, temporary)
    for i in range(N):
        t = i / SR
        envelope = 1.10 * math.sin(min(1, t / .26) * PI / 2) ** 2
        envelope *= math.sin(min(1, max(0, (20 - t) / 1.15)) * PI / 2) ** 2
        score[2 * i] *= envelope
        score[2 * i + 1] *= envelope
    return score


def write_flac(path, audio):
    # Explicit 24-bit signed PCM before lossless encoding preserves export format.
    pcm = bytearray(3 * len(audio))
    for i, value in enumerate(audio):
        sample = round(min(1, max(-1, value)) * 8388607) & 0xffffff
        pcm[3*i] = sample & 255
        pcm[3*i+1] = (sample >> 8) & 255
        pcm[3*i+2] = (sample >> 16) & 255
    subprocess.run([FF, '-y', '-v', 'error', '-f', 's24le', '-ar', str(SR),
                    '-ac', '2', '-i', '-', '-c:a', 'flac', str(path)],
                   input=pcm, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ASSETS,
                        help='Export directory; use test/scratch/audio for a non-destructive check.')
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.audio-', dir=output) as temp:
        score = compose(Path(temp))
    # Roger remains one coherent performance. Position only; never fragment,
    # shorten, stretch, or alter speaking speed.
    raw = subprocess.check_output([
        FF, '-v', 'error', '-i', str(ASSETS / 'audio-take-roger.mp3'),
        '-af', 'highpass=f=65,loudnorm=I=-19:TP=-3:LRA=8',
        '-ar', str(SR), '-ac', '1', '-f', 'f64le', '-'])
    voice = doubles(raw)
    mix = array('d', score)
    place(mix, voice, 6.20)
    gain = 10 ** (2.5 / 20)  # Constant final gain; generous true-peak headroom.
    for i in range(len(mix)):
        mix[i] *= gain
    write_flac(output / 'audio-music.flac', score)
    write_flac(output / 'audio-mix.flac', mix)
    stats = {'duration_seconds': DURATION, 'sample_rate': SR, 'channels': 2,
             'tempo_bpm': 96, 'voice_offset_seconds': 6.2,
             'voice_duration_seconds': len(voice) / SR,
             'mix_sample_peak_dbfs': 20 * math.log10(max(map(abs, mix))),
             'mix_rms_dbfs': 20 * math.log10(math.sqrt(sum(x*x for x in mix) / len(mix))),
             'music_sample_peak_dbfs': 20 * math.log10(max(map(abs, score))),
             'renderer': 'Python standard library + FFmpeg afir; seeded stdlib noise'}
    (output / 'audio-stats.json').write_text(json.dumps(stats, indent=2) + '\n')
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
