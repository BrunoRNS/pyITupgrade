from typing import Any, List, Tuple
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyIT import (
    TablatureBuilder,
    WavInstrumentBuilder,
    ITfile,
    getAsset,
)

tablature: List[Tuple[Any, ...]] = [
    (None, 9, 9, 9, 9, 7, 7, 7, 7, 5, 5, 5, 5, 7, 7, 7, 9),
    (None, 7, 7, 7, 7, 5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 7),
]

def create_sample_tablature_it(it_path: Path) -> None:
    
    music = ITfile()
    music.IT = 225
    music.SongName = "TROPPER_LIKE"
    
    tab = TablatureBuilder(lines_per_note=3)
    tab.add_tablature(
        tablature=list(zip(tablature[0], tablature[1])),
        tuning=["D4", "A3"],
        fret_count=12,
        instrument_id=1,
        bpm=162
    )

    pattern = tab.build()
    pattern.add_note_to_final(
        0,
        effect=0x02,
        effect_arg=0x00
    )
    
    instrument, sample = WavInstrumentBuilder.create_from_wav(
        str(getAsset(id=5).resolve()), instrument_name="Pulse"
    )
    
    for note in range(120):
        instrument.SampleTable[note] = [note, 1]
    
    music.Samples.append(sample)
    music.Instruments.append(instrument)
    
    music.Patterns.append(pattern)
    
    music.Orders.extend([0, 255])
    
    music.write(str(it_path.resolve()))

if __name__ == "__main__":
    
    os.makedirs(Path(__file__).parent / "temp", exist_ok=True)
    create_sample_tablature_it(Path(__file__).parent / "temp" / "tab.it")
