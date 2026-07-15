from typing import Tuple

from ..create_sample_it import create_sample_it

from pathlib import Path
import subprocess
import logging
import shutil
import stat
import sys
import os

def _verify_file_size(file_path: Path) -> Tuple[bool, int]:
    """Validates the file size, it can't pass the LoROM bank size"""
    
    logger = logging.getLogger()
    LIMIT_BYTES = 32 * 1000
    
    try:
        size_bytes = os.path.getsize(file_path)
        
        it_fits = size_bytes <= LIMIT_BYTES
        size_kb = size_bytes // 1000
        
        return it_fits, size_kb
        
    except FileNotFoundError:
        logger.error("File not found to calculate the specified size")
        return False, 0

def test_smconv():
    """Tests if smconv can convert your IT file, and generates a normalized soundbank.

    Raises:
        e: If fails to generate the IT file.
    """
    
    BASE_DIR = Path(__file__).parent / "temp"
    BASE_DIR.mkdir(parents=True, exist_ok=True) 
    sample_it = BASE_DIR / "music.it"
        
    try:
        create_sample_it(sample_it)
    except Exception as e:
        e.add_note("Failed to create IT file in test_smconv")
        raise e
        
    assert sample_it.exists()
    assert sample_it.is_file()
    assert str(os.environ["PVSNESLIB_HOME"]).strip() != ""
    
    smconv: Path = Path(os.environ["PVSNESLIB_HOME"]) / "devkitsnes" / "tools" / (
        "smconv" if os.name != "nt" else "smconv.exe"
    )
    soundbank_path: Path = BASE_DIR / 'res' / 'soundbank'
    
    os.makedirs(BASE_DIR / 'res', exist_ok=True)
    subprocess.run([smconv, '-s', '-o', soundbank_path, sample_it], cwd=BASE_DIR, check=True)
    
    soundbank_path = soundbank_path.parent
    
    assert soundbank_path.exists()
    assert (soundbank_path / "soundbank.asm").exists()
    assert (soundbank_path / "soundbank.asm").is_file()
    assert (soundbank_path / "soundbank.bnk").exists()
    assert (soundbank_path / "soundbank.bnk").is_file()
    assert (soundbank_path / "soundbank.h").exists()
    assert (soundbank_path / "soundbank.h").is_file()

    assert _verify_file_size(soundbank_path / "soundbank.bnk")[0]

def test_snes_rom():
    """Tests if the IT file converted to a soundbank can run in a SNES ROM.

    Raises:
        e: If fails to generate the IT file.
    """
    
    assert Path(os.environ["PVSNESLIB_HOME"]).exists()
    assert Path(os.environ["PVSNESLIB_HOME"]).is_dir()
    assert Path(os.environ["SNES_EMU"]).exists()
    assert Path(os.environ["SNES_EMU"]).is_file() if sys.platform.lower() != 'darwin' else (
        Path(os.environ["SNES_EMU"]).is_dir()
    )
    assert True if os.name == "nt" else (
        Path(str(os.environ["SNES_EMU"]))
    ).stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    BASE_DIR = Path(__file__).parent / "snes_proj"
    os.makedirs(BASE_DIR / "res", exist_ok=True)
    sample_it = BASE_DIR / "music.it"
        
    try:
        create_sample_it(sample_it)
    except Exception as e:
        e.add_note("Failed to create IT file in test_snes_rom")
        raise e
    
    assert sample_it.exists()
    assert sample_it.is_file()
    
    assert shutil.which("make")
    
    subprocess.run(["make"], cwd=BASE_DIR, check=True)
    
    rom: Path = BASE_DIR / "music.sfc"
    
    assert rom.exists()
    assert rom.is_file()
    
    try:
        subprocess.run([
            Path(os.environ["SNES_EMU"]) if sys.platform.lower() != 'darwin' else 
            "open -a " + str(os.environ["SNES_EMU"]), rom
        ], cwd=BASE_DIR, check=True, timeout=10)
    except subprocess.TimeoutExpired:
        pass
    subprocess.run(["make", "clean"], cwd=BASE_DIR, check=True)
    