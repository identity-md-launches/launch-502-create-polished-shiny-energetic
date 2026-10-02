# Pepe2Pepe V2 audio provenance

## Narration

The installed fal.ai connector successfully generated two **complete**, separate
performances using ElevenLabs **Eleven v4** (`elevenlabs/tts/eleven-v4`). No V1
Edge voice, sentence-fragment assembly, or time stretching is used.

| Candidate | Settings | Request | Result |
| --- | --- | --- | --- |
| Roger, selected | stability 0.42, similarity 0.65, seed 41; `[warm]` and short pauses | `01a0fe49-c51c-7cc1-8ea3-cb4e53efc878` | `assets/audio-take-roger.mp3`, 12.3559 s |
| Chris | stability 0.35, similarity 0.60, seed 57; `[warm] [thoughtful]` and pauses | `01a0fe4a-2879-73b2-b9e2-54ead2afdf49` | `assets/audio-take-chris.mp3`, approximately 11.16 s |

Both performances were generated in English at MP3 44.1 kHz / 192 kb/s. The
selected Roger performance was placed intact at **6.20 seconds**. Its measured
sentence pauses (approximately 0.53, 0.77, 0.69 and 0.74 seconds) leave more room
than Chris and align the product, Oracle and final invitation with the edit.
Processing is a 65 Hz high-pass, loudness normalization, equal centered placement
in the stereo score, and constant final gain. No speech timing was changed.

Spoken script:

> Your question. Someone else’s take. On Pepe to Pepe, pick a side at fixed odds,
> with funds on-chain. Powered by the I M D Oracle. Take the other side.

Source URLs (local files supplied; no network required for rendering):

- Roger: https://v3b.fal.media/files/b/0aacceb0/QLTrVI75VZXMD9HhqkkbM_output.mp3
- Chris: https://v3b.fal.media/files/b/0aacceb3/CeIVaZD7b5XLZNTUA0282_output.mp3

**Review limitation:** two expressive settings were generated and compared by
duration, measured pauses, and timing fit. They were **not auditioned by ear**.
This environment exposes no audio-perception tool or usable audio device
(`/dev/snd` is absent). A naturalness or pronunciation judgment is not claimed.
Provider character timestamps were available for Chris; Roger timing was
inspected through the waveform and silence detection. Human listening remains
advisable. This is a disclosure of the review limitation, not a claim that a
waveform establishes voice quality.

## Original instrumental

`audio.py` composes and renders the original score locally: **96 BPM**, eight
bars / 32 beats over exactly 20 seconds, warm damped-string keyboard motif,
soft detuned harmonic pad, rounded bass, restrained low pulse and noise-brush
percussion. Sparse D-major-family harmony leaves long rests. A single soft high
keyboard accent accompanies the Oracle. A generated room impulse provides
subtle stereo depth. The music resolves under the CTA and tapers naturally to
the end; there are no repetitive transition whooshes.

All notes, synthesis and room impulse were created for this deliverable. There
are no external music recordings, stock loops or sampled copyrighted songs.
No third-party attribution is required for this locally composed score.

## Delivered audio / reproducibility

- `assets/audio-mix.flac`: finished 20.000 s, stereo, 48 kHz, 24-bit FLAC.
- `assets/audio-music.flac`: original instrumental, same technical format.
- `assets/audio-stats.json`: generation statistics.
- Both narration candidates are included as editable local source media.
- Run `python production/v2/audio.py`; this score renderer needs only the Python
  standard library and FFmpeg (including its `afir` filter) on `PATH`. No NumPy,
  package installation, network access, or vendor wheel is required. To verify
  without replacing the saved mix, use
  `python production/v2/audio.py --output-dir test/scratch/audio`.
- Technical review: decoded fully, measured loudness and true peak, checked
  duration, sample format, channel count and no clipping. No listening claimed.

The final mix is approximately **−18.4 LUFS integrated**, with approximately
**−2.8 dBTP** headroom before AAC encoding. Quiet instrumental opening versus
narration creates intentional loudness contrast; no limiter is driven hard.

### Compact offline source revision

The delivered mix and original music FLAC retain their existing export bytes. To keep the editable source bundle compact, the score renderer was
reimplemented with Python standard-library arrays and math; FFmpeg `afir` now
performs the stereo room convolution with automatic impulse normalization
disabled. Every note, harmony, event time, envelope, pan, gain, the 96 BPM groove,
the room design and the complete Roger performance retain their original
settings. The deterministic noise source now uses Python's seeded random
generator instead of NumPy's: regenerated brush and room noise therefore differ
at sample level, so a fresh render is not claimed to be bit-identical to the
saved original FLAC. No narration timing or duration is changed.

The standard-library check render completed offline to `test/scratch/audio-stdlib`:
20.000 seconds, stereo, 48 kHz, 24-bit FLAC; the Roger performance remains
12.3559167 seconds long at the original 6.20-second offset. The check mix
measured −18.54 LUFS integrated and −2.63 dBTP. This check did not overwrite
the saved mix or the delivered film. No auditory review is claimed.
