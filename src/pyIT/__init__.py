"""PyIT: a Python library for reading, writing, and manipulating Impulse Tracker (IT) module files."""
from .pyIT import (
    ITenvelope_node,
    ITenvelope,
    ITvol_envelope,
    ITpan_envelope,
    ITpitch_envelope,
    ITinstrument,
    ITsample,
    ITnote,
    ITpattern,
    ITfile,
    PatternBuilder,
    WavInstrumentBuilder,
    TablatureBuilder
)

from .convert import IT2ogg, SchismRenderer, OggVorbisEncoder, AudioEncoder, ModuleRenderer
from .instrument import synthesizer, getAsset

__all__ = [
    'ITenvelope_node',
    'ITenvelope',
    'ITvol_envelope',
    'ITpan_envelope',
    'ITpitch_envelope',
    'ITinstrument',
    'ITsample',
    'ITnote',
    'ITpattern',
    'ITfile',
    'PatternBuilder',
    'WavInstrumentBuilder',
    'TablatureBuilder',
    'IT2ogg',
    'SchismRenderer',
    'synthesizer',
    'getAsset',
    'OggVorbisEncoder',
    'AudioEncoder',
    'ModuleRenderer',
]

__version__ = '1.0.0'