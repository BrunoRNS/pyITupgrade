from pathlib import Path
from typing import List

possibilities: List[str] = [
    "1_sine.wav",
    "2_square.wav",
    "3_sawtooth.wav",
    "4_triangle.wav",
    "5_pwm_pulse.wav"
]

def getAsset(name: str|None = None, id: int|None = None) -> Path:
    """Get an asset from the WHL package (../../assets), it can be one of the options:
    
    "1_sine.wav",
    "2_square.wav",
    "3_sawtooth.wav",
    "4_triangle.wav",
    "5_pwm_pulse.wav"
    
    Or you can send just the id of it, like: getAsset(id=1), etc.
    
    """
    
    if isinstance(id, int):
        if id >= 1 and id <= 5:
            idx: int = id-1
            rel_path: str = possibilities[idx]
            
            return (Path(__file__).parent.parent.parent / "assets" / rel_path).resolve()
            
        else:
            raise ValueError("Can't get Asset of ID smaller than 1 or greater than 5")
    
    elif isinstance(name, str):
        
        if name not in possibilities:
            raise ValueError(
                f"Can't get asset {name}, it does not exist in options: "
                f"{str(possibilities)}\n")
            
        rel_path: str = name
            
        return (Path(__file__).parent.parent.parent / "assets" / rel_path).resolve()

    else:
        raise ValueError(
            "No ID or Name provided, can't give any asset"
        )
    
