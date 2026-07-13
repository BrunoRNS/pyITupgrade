from typing import Any, List
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyIT import PatternBuilder, ITfile, WavInstrumentBuilder, getAsset

sonic_like_pattern: List[Any] = [
    "C-5", "A-4", None,
    "C-5", "B-4", None, 
    "C-5", "B-4", None, "G-4", None, None,
    "A-4", None, "E-5", "D-5", None, 
    "C-5", "B-4", None, 
    "C-5", "B-4", None, "G-4", None, None,
    "A-4", "F-4", None,
    "A-4", "G-4", None, 
]

sonic_like_pattern_2: List[Any] = [
    "A-4", "G-4", None, "E-4", None, None,
    None,
]

def create_sample_it(it_path: Path) -> None:
    
    music = ITfile()
    music.SongName = "SONIC_LIKE"
    
    pbuilder = PatternBuilder(bpm=180, lines_per_note=2)
    
    pattern1 = pbuilder.build_pattern(sonic_like_pattern, instrument_id=1)
    pattern2 = pbuilder.build_pattern(sonic_like_pattern_2, instrument_id=1)
    
    instrument, sample = WavInstrumentBuilder.create_from_wav(
        str(getAsset(id=2).resolve()), instrument_name="Square"
    )
    
    for note in range(120):
        instrument.SampleTable[note] = [note, 1]
    
    music.Samples.append(sample)
    music.Instruments.append(instrument)
    
    music.Patterns.append(pattern1)
    music.Patterns.append(pattern2)
    
    music.Orders.extend([0, 255])
    
    music.write(str(it_path.resolve()))
    

if __name__ == "__main__":
    
    os.makedirs(Path(__file__).parent / "temp", exist_ok=True)
    create_sample_it(Path(__file__).parent / "temp" / "local_test.it")
