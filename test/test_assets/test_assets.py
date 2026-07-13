from pathlib import Path
import sys
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyIT import getAsset


def test_assets_exists():
    """Test if the assets are accessible via ID

    Raises:
        AssertionError: if the getAsset() raises a ValueError
    """
    for i in range(1, 6):
        asset: Path
        
        try:
            asset = getAsset(id=i)
        except ValueError as e:
            raise AssertionError(f"Failed to load asset {i} due to: {e}")
        
        assert asset.exists()
        assert asset.is_file()
        
def test_assets_access_by_name():
    """Tests if the assets are accessible by name

    Raises:
        AssertionError: if getAsset returns a ValueError
    """
    assets: List[str] = [
        "1_sine.wav",
        "2_square.wav",
        "3_sawtooth.wav",
        "4_triangle.wav",
        "5_pwm_pulse.wav"
    ]
    
    for name in assets:
        
        asset: Path
        
        try:
            asset = getAsset(name=name)
        except ValueError as e:
            raise AssertionError(f"Failed to load asset {name} due to: {e}")
        
        assert asset.exists()
        assert asset.is_file()

def test_id_name_mirror():
    """Tests if the assets by ID and by NAME are the exactly same

    Raises:
        AssertionError: if getAsset returns a ValueError
    """
    
    assets: Dict[int, str] = {
        1: "1_sine.wav",
        2: "2_square.wav",
        3: "3_sawtooth.wav",
        4: "4_triangle.wav",
        5: "5_pwm_pulse.wav"
    }
    
    for id in assets.keys():
        
        asset_by_id: Path
        asset_by_name: Path
        
        try:
            asset_by_id = getAsset(id=id)
            asset_by_name = getAsset(name=assets[id])
        except ValueError as e:
            raise AssertionError(f"Failed to load asset {id} due to: {e}")
        
        assert asset_by_id == asset_by_name
        assert asset_by_id.exists() and asset_by_name.exists()
        assert asset_by_id.is_file() and asset_by_name.is_file()
        assert asset_by_id.name == assets[id]
        
