# pyIT – Comprehensive Documentation

`pyIT` is a Python library for reading, writing, and manipulating **Impulse Tracker (IT)** module files.  
It provides a full-featured API to programmatically create, edit, and convert `.it` files, as well as render them to audio or prepare them for SNES soundbanks via `smconv`.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
  - [IT File Structure](#it-file-structure)
  - [Patterns & Notes](#patterns--notes)
  - [Instruments & Samples](#instruments--samples)
  - [Envelopes](#envelopes)
- [Working with IT Files](#working-with-it-files)
  - [Loading an Existing IT File](#loading-an-existing-it-file)
  - [Creating a New IT File](#creating-a-new-it-file)
  - [Saving Changes](#saving-changes)
- [Pattern Building](#pattern-building)
  - [Using `PatternBuilder`](#using-patternbuilder)
  - [Using `TablatureBuilder` (Guitar‑Style)](#using-tablaturebuilder-guitarstyle)
- [Instruments & Samples](#instruments--samples)
  - [Creating from WAV Files](#creating-from-wav-files)
  - [Generating Waveforms with `MathSynthesizer`](#generating-waveforms-with-mathsynthesizer)
  - [Asset Management with `getAsset`](#asset-management-with-getasset)
- [Rendering to Audio](#rendering-to-audio)
  - [`IT2ogg` Converter](#it2ogg-converter)
  - [Custom Renderers & Encoders](#custom-renderers--encoders)
- [Testing & Development](#testing--development)
  - [Running Tests](#running-tests)
  - [SNES Integration (smconv)](#snes-integration-smconv)
- [Tips & Best Practices](#tips--best-practices)
- [API Reference](#api-reference)

## Overview

`pyIT` is a pure‑Python library that fully implements the **Impulse Tracker** file format specification. It allows you to:

- Read and write `.it` files.
- Create and edit patterns, notes, instruments, samples, and envelopes.
- Build patterns from note sequences or guitar tablature.
- Convert WAV files into IT instruments/samples.
- Synthesize simple waveforms (sine, square, saw, etc.) for quick prototyping.
- Render `.it` modules to **OGG Vorbis** via Schism Tracker (or a custom renderer).
- Prepare modules for the SNES using `smconv` (part of PVSNESlib).

The library is designed with **clean separation of concerns**, **dependency inversion**, and **type hints** for modern Python development.

## Installation

```bash
pip install pyit
```

(If not yet published on PyPI, you can install from source or add the `src/` directory to your `PYTHONPATH`.)

### Requirements

- Python 3.10+
- `numpy`, `scipy` (for synthesizer)
- `pydub` (for OGG encoding, requires ffmpeg)
- `mutagen` (for testing OGG validation)
- `pytest` (for running tests)

## Core Concepts

### IT File Structure

An IT file is composed of:

- **Header** – global song parameters (song name, tempo, flags, etc.)
- **Order list** – sequence of pattern indices that define the song flow.
- **Patterns** – 64 rows × 64 channels of note events.
- **Instruments** – metadata, sample mapping, and envelopes (volume, pan, pitch).
- **Samples** – audio data (8‑bit/16‑bit, mono/stereo, optionally compressed).

`pyIT` mirrors this structure with classes:

- `ITfile` – the top‑level container.
- `ITpattern` – a 2D grid of `ITnote` cells.
- `ITinstrument` – includes envelope objects.
- `ITsample` – holds raw PCM and loop parameters.

### Patterns & Notes

- `ITpattern` contains `Rows` (list of 64 lists of 64 `ITnote` objects).
- `ITnote` stores `Note`, `Instrument`, `Volume`, `Effect`, and `EffectArg`.
- Effects follow the IT effect command set (e.g., 0x0A = volume slide).

### Instruments & Samples

- An `ITinstrument` has a **sample table** (120 entries mapping note ranges to sample indices).
- It includes **volume**, **pan**, and **pitch envelopes** (`ITvol_envelope`, `ITpan_envelope`, `ITpitch_envelope`).
- `ITsample` holds the actual waveform data, loop points, C‑5 frequency, and compression flags.

### Envelopes

Envelopes are defined by up to 25 control points (`ITenvelope_node`), each with a value (y) and a tick position. They support loop and sustain loops.

## Working with IT Files

### Loading an Existing IT File

```python
from pyIT import ITfile

my_it = ITfile()
my_it.open("song.it")
print(f"Song name: {my_it.SongName.decode()}")
print(f"Patterns: {len(my_it.Patterns)}")
```

### Creating a New IT File

```python
from pyIT import ITfile, ITpattern, ITnote

music = ITfile()
music.SongName = b"My Song"
# Build a pattern manually...
pattern = ITpattern()
note = pattern.Rows[0][0]
note.Note = 60   # C-5
note.Instrument = 1
note.Volume = 64
music.Patterns.append(pattern)
music.Orders = [0, 255]   # play pattern 0, then stop
```

### Saving Changes

```python
music.write("my_song.it")
```

## Pattern Building

### Using `PatternBuilder`

`PatternBuilder` helps you generate patterns from a sequence of note names.

```python
from pyIT import PatternBuilder

builder = PatternBuilder(bpm=180, lines_per_note=2)
notes = ["C-5", "A-4", None, "G-4", "F-4"]
pattern = builder.build_pattern(notes, instrument_id=1)
```

- `bpm` – influences timing (stored in the builder for reference).
- `lines_per_note` – rows occupied by each note (e.g., 2 = 1/8th note spacing at standard tempo).
- Notes can be `None` (rest) or strings like `"C#4"`, `"A-5"`, or Portuguese aliases (`"DO"` = C-5).
- `stop_line` can be set to insert a **Pattern Break** effect (0x02) early.

To build a long sequence that exceeds 64 rows, use `build_long_pattern`, which splits into multiple patterns and adds a break at the end.

```python
patterns = builder.build_long_pattern(long_sequence, instrument_id=1)
music.Patterns.extend(patterns)
music.Orders = list(range(len(patterns))) + [255]
```

### Using `TablatureBuilder` (Guitar‑Style)

`TablatureBuilder` converts guitar tablature (strings/frets) into IT patterns. It supports multiple strings, chords, bends, slides, and hammer‑ons.

```python
from pyIT import TablatureBuilder

tab = TablatureBuilder(lines_per_note=3)

# Define a tab: each row is a tuple of (fret, effect) for each string
# Strings are tuned to ["E4", "A4", "D4", "G3"] (example)
rows = [
    (None, 0, 3, None),
    ({"chord": [(0, 2), (1, 3)]}, None, 5, 2),
    ("1b2", None, None, None),   # bend notation
]

tab.add_tablature(
    tablature=rows,
    tuning=["E4", "A4", "D4", "G3"],
    fret_count=12,
    instrument_id=1,
    pre_note_effects={"set_volume": 64},
    post_note_effects={"portamento_up": 3},
)

pattern = tab.build()
```

**Features:**

- Each row can contain per‑string values: `None` (rest), integer (fret), dict with `fret`, `bend`, `slide`, `hammer_on`, `hammer_off`, or compact tokens like `"1b2"` (fret 1, bend 2).
- `"chord"` key spreads multiple notes across consecutive rows (arpeggiated).
- Effects are automatically mapped to IT effect codes.
- `pre_note_effects` and `post_note_effects` apply to the row before/after the note.
- BPM can be overridden per tablature block.

## Instruments & Samples

### Creating from WAV Files

`WavInstrumentBuilder` loads a WAV file, normalizes it, and returns an `ITinstrument` and `ITsample` ready for use.

```python
from pyIT import WavInstrumentBuilder

instrument, sample = WavInstrumentBuilder.create_from_wav(
    "my_sample.wav", instrument_name="Piano"
)
# Map all notes to this sample
for note in range(120):
    instrument.SampleTable[note] = [note, 1]   # sample index 1 (the first sample)

music.Samples.append(sample)
music.Instruments.append(instrument)
```

Supported WAV formats: 8‑bit/16‑bit PCM, 24‑bit/32‑bit PCM, and 32‑bit/64‑bit IEEE float (all converted to 16‑bit).

### Generating Waveforms with `MathSynthesizer`

`MathSynthesizer` generates simple waveforms for quick prototyping. It outputs 8‑bit WAV files.

```python
from pyIT.instrument.MathSynthesizer import MathSynthesizer

synth = MathSynthesizer(sample_rate=8000)
synth.sine_wave("C", octave=5, duration=2.0, output_file="sine.wav")
synth.square_wave("C", octave=5, duration=2.0, output_file="square.wav")
# Available: sine, square, sawtooth, triangle, pwm_pulse
```

You can also run the module to generate the default asset waveforms:

```bash
python -m pyIT.instrument.MathSynthesizer
```

### Asset Management with `getAsset`

The library ships with 5 built‑in waveforms (1‑sine, 2‑square, 3‑sawtooth, 4‑triangle, 5‑pwm_pulse). Use `getAsset` to obtain their paths:

```python
from pyIT import getAsset

sine_path = getAsset(id=1)
square_path = getAsset(name="2_square.wav")
```

This is useful for creating sample instruments quickly.

## Rendering to Audio

### `IT2ogg` Converter

`IT2ogg` renders an IT module to an OGG Vorbis file. It uses **Schism Tracker** as the default renderer.

```python
from pyIT import IT2ogg

converter = IT2ogg("song.it", "song.ogg", sample_rate=44100, channels=2)
converter.convert()
```

**Parameters:**

- `sample_rate` – output sample rate (default 44100).
- `channels` – 1 (mono) or 2 (stereo).
- `quality` – bitrate string (e.g., "128k") or Vorbis quality float (0.0‑1.0).
- `renderer` – custom renderer (must implement `ModuleRenderer`).
- `encoder` – custom encoder (must implement `AudioEncoder`).

### Custom Renderers & Encoders

You can replace the renderer (e.g., to use `libxmp`) or the encoder (e.g., to use `lame` for MP3) by implementing the abstract base classes:

```python
from pyIT import ModuleRenderer, AudioEncoder

class MyRenderer(ModuleRenderer):
    def render(self, input_path, sample_rate, channels) -> bytes:
        # return PCM bytes
        ...

class MyEncoder(AudioEncoder):
    def encode(self, pcm_data, sample_rate, channels, output_path, quality):
        # write output file
        ...
```

Then pass them to `IT2ogg`.

**Note:** The built‑in `SchismRenderer` assumes `schism` is in your PATH (or a `.app` on macOS). On Windows, provide the full path to `schismtracker.exe`.

## Testing & Development

### Running Tests

The `test/` directory contains comprehensive unit and integration tests.  
To run them, install `pytest` and execute from the project root:

```bash
pytest test/
```

The tests cover:

- Pattern building (note conversion, row placement, truncation).
- Tablature parsing and effect application.
- Asset loading.
- OGG conversion (validates output with `mutagen`).
- SNES `smconv` integration (requires `PVSNESLIB_HOME` and `SNES_EMU` environment variables).

### SNES Integration (smconv)

The library can be used to create IT files that are compatible with **PVSNESlib**’s `smconv` tool, which converts IT modules into SNES soundbank formats. The test suite includes:

- `test_smconv` – converts a sample IT to a soundbank and checks file sizes.
- `test_snes_rom` – builds a full SNES ROM, runs it in an emulator, and cleans up.

To run these tests, you need:

- `PVSNESLIB_HOME` – path to PVSNESlib installation.
- `SNES_EMU` – path to your SNES emulator (e.g., `snes9x` or `bsnes`).
- `make` and a working SNES development environment.

These tests ensure that the generated IT files are fully compatible with SNES sound hardware.

## Tips & Best Practices

1. **Use `PatternBuilder` for simple melodic sequences** – it handles spacing and note name parsing automatically.

2. **For complex guitar‑like arrangements, `TablatureBuilder` is ideal** – it supports bends, slides, and chords in a compact syntax.

3. **Reuse instruments** – if you have multiple patterns using the same instrument, define it once and reuse the same object.

4. **Leverage the built‑in assets** – use `getAsset` to quickly add waveforms to your projects.

5. **When converting to audio, be patient** – Schism Tracker renders in real time; for batch processing, consider using a headless renderer or increasing the sample rate only when needed.

6. **Test with `smconv` early** – if you are targeting the SNES, validate your IT files with `smconv` frequently to catch format incompatibilities.

7. **Check compression** – the library automatically handles IT 2.15 sample compression when reading. When writing, it preserves compression if the sample data hasn’t been modified.

8. **Envelopes** – remember that volume, pan, and pitch envelopes are part of the instrument, not the sample. You can manipulate them directly:

   ```python
   instrument.volEnv.IsOn = True
   instrument.volEnv.Nodes[0].y_val = 64
   instrument.volEnv.Nodes[0].tick = 0
   ```

## API Reference

For full API details, refer to the docstrings in each module. Key classes:

| Class | Purpose |
|-------|---------|
| `ITfile` | Top‑level container; load/save `.it` files. |
| `ITpattern` | 64×64 grid of `ITnote`. Methods: `load`, `write`, `pack`, `unpack`, `isEmpty`, `add_note_to_final`. |
| `ITnote` | Single cell: `Note`, `Instrument`, `Volume`, `Effect`, `EffectArg`. |
| `ITinstrument` | Instrument metadata, sample table, envelopes. |
| `ITsample` | Sample data, loop points, compression. |
| `ITenvelope` (and subclasses) | Envelope control points and flags. |
| `PatternBuilder` | Build patterns from note name sequences. |
| `TablatureBuilder` | Build patterns from guitar tablature. |
| `WavInstrumentBuilder` | Create instruments/samples from WAV files. |
| `MathSynthesizer` | Generate simple WAV waveforms. |
| `getAsset` | Retrieve built‑in waveform paths. |
| `IT2ogg` | Convert IT to OGG using a renderer/encoder. |
| `SchismRenderer` | Render via Schism Tracker CLI. |
| `OggVorbisEncoder` | Encode PCM to OGG using `pydub`/ffmpeg. |

## License

`pyIT` is distributed under the terms of the GNU General Public License v3 (or later).  
This is inherited from the Schism Tracker decompression code (`pyitcompress.py`) (which is GNU GPL v2 or later).  
All other parts are released under the same license for consistency.

Happy tracking!  
If you encounter any issues or have feature requests, please open an issue in the project repository.
