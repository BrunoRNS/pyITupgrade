# pyIT (upgraded version) – Impulse Tracker Module Library

**pyIT** is a Python library for reading, writing, and manipulating **Impulse Tracker (IT)** module files.  
It provides a complete toolkit to programmatically create, edit, and convert `.it` files, with support for patterns, instruments, samples, envelopes, and rendering to audio or SNES soundbanks.

## Features

- **Full IT file format support** – read/write `.it` files with all header, pattern, instrument, sample, and envelope data.
- **Pattern construction** – build patterns from simple note sequences or guitar-style tablature.
- **Instrument & sample creation** – load WAV files, generate basic waveforms (sine, square, saw, etc.), and map samples to notes.
- **Envelope editing** – volume, pan, and pitch envelopes with loop and sustain points.
- **Audio rendering** – convert modules to OGG Vorbis using Schism Tracker (or a custom renderer).
- **SNES integration** – prepare IT files for `smconv` (PVSNESlib) to create soundbanks for Super Nintendo homebrew.
- **Pure Python** – no external runtime dependencies beyond Python and standard scientific libraries.

## Installation

### From PyPI

```bash
pip install pyITupgrade
```

### From Source

Clone the repository and install in editable mode:

```bash
git clone https://github.com/BrunoRNS/homebrew-renpylib.git
cd homebrew-renpylib
pip install -e .
```

For development, install the test dependencies:

```bash
pip install -r test-requirements.txt
```

Detailed build instructions are available in [BUILDING_FROM_SOURCE.md](BUILDING_FROM_SOURCE.md).

## Quick Start

### Load and inspect an IT file

```python
from pyIT import ITfile

module = ITfile()
module.open("song.it")
print(f"Song: {module.SongName.decode()}, Patterns: {len(module.Patterns)}")
```

### Create a simple pattern with `PatternBuilder`

```python
from pyIT import PatternBuilder

builder = PatternBuilder(bpm=180, lines_per_note=2)
pattern = builder.build_pattern(["C-5", "A-4", None, "G-4"], instrument_id=1)
```

### Add a WAV sample as an instrument

```python
from pyIT import WavInstrumentBuilder

instrument, sample = WavInstrumentBuilder.create_from_wav("piano.wav")
for note in range(120):
    instrument.SampleTable[note] = [note, 1]   # map all notes to this sample
module.Instruments.append(instrument)
module.Samples.append(sample)
```

### Render to OGG

```python
from pyIT import IT2ogg

converter = IT2ogg("song.it", "song.ogg", sample_rate=44100)
converter.convert()
```

For more detailed usage, see the [full documentation](DOCS.md).

## Dependencies

- Python 3.10+
- `numpy`, `scipy` – for waveform synthesis
- `pydub` – for OGG encoding (requires `ffmpeg` installed separately)
- `flit` – for building the package (development only)

Optional test dependencies: `pytest`, `mutagen`.

## Building from Source

See [BUILDING_FROM_SOURCE.md](BUILDING_FROM_SOURCE.md) for instructions on building the package and creating a distributable wheel.

## Testing

The test suite covers unit tests and integration tests (requires Schism Tracker, PVSNESlib, and a SNES emulator).  
Run all tests with:

```bash
make test
```

Detailed testing instructions are in [TESTING.md](TESTING.md).

## Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting issues, submitting pull requests, and coding standards.

## Special Thanks

- **Original PyIT** – the initial implementation by mike burke, published as a [GitHub Gist](https://gist.github.com/mikeburke), which served as the foundation for this project.
- **Schism Tracker Community** – for creating and maintaining the excellent Schism Tracker, which powers the audio rendering capabilities of this library.
- **PVSNESlib Developers** – for the tools that enable IT modules to run on SNES hardware.

## License

This project is licensed under the **GNU General Public License v3.0 or later** (GPL-3.0-or-later).  
See the [LICENSE](LICENSE) file for details.

## Links

- [Documentation](docs/DOCS.md)
- [Building from Source](docs/BUILDING_FROM_SOURCE.md)
- [Testing Guide](docs/TESTING.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Schism Tracker](https://github.com/schismtracker/schismtracker)
- [PVSNESlib](https://github.com/alekmaul/pvsneslib)
