from ..create_sample_it import create_sample_it

from pathlib import Path
import tempfile
import stat
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyIT import IT2ogg, SchismRenderer
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError

schism = SchismRenderer(
    schism_executable=str(
        Path(os.environ["SCHISM_HOME"]) / 
        ("Schism Tracker.app" if sys.platform.lower() == "darwin" else "run.sh" if os.name == "posix" else "schismtracker.exe")
    )
)

def _is_ogg_vorbis(file: Path) -> bool:
    """Validate OGG vorbis header using mutagen"""
    
    try:
        OggVorbis(file)
        return True
    
    except OggVorbisHeaderError:
        return False
    
    except Exception:
        return False


def test_create_sample_it():
    """Test creating a sample IT file in a temporary directory.
    
    raises:
        Exception: if fails to create IT file.
    """
    
    with tempfile.TemporaryDirectory() as tempdir:
        
        sample_it: Path = Path(tempdir) / "sample.it"
        try:
            create_sample_it(sample_it)
        except Exception as e:
            e.add_note("Failed to create IT file in test_create_sample_it")
            raise e
        
        assert sample_it.exists()
        assert sample_it.is_file()
        
    
def test_convert_it_ogg():
    """Test converting the sample IT to an OGG Vorbis file (and validate it).
    
    raises:
        Exception: if fails to create IT file.
    """
    
    assert str(os.environ["SCHISM_HOME"]).strip() != ""
    assert (Path(str(os.environ["SCHISM_HOME"])) / "Schism Tracker.app").is_dir() if sys.platform.lower() == "darwin" else (
        Path(str(os.environ["SCHISM_HOME"])) / ("run.sh" if os.name == "posix" else "schismtracker.exe")
    ).is_file()
    assert True if os.name == "nt" else (
        Path(str(os.environ["SCHISM_HOME"])) / (
            "Schism Tracker.app" if sys.platform.lower() == "darwin" else "run.sh"
        )
    ).stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) 
    
    with tempfile.TemporaryDirectory() as tempdir:
        
        sample_it: Path = Path(tempdir) / "sample.it"
        output_ogg: Path = sample_it.parent / "output.ogg"
        try:
            create_sample_it(sample_it)
        except Exception as e:
            e.add_note("Failed to create IT file in test_create_sample_it")
            raise e
        
        converter = IT2ogg(
            sample_it, output_ogg,
            renderer=schism
        )
        
        converter.convert()
        
        assert output_ogg.exists()
        assert output_ogg.is_file()
        assert _is_ogg_vorbis(output_ogg)
    
