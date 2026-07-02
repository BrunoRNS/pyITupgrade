# -*- coding: utf-8 -*-
"""
pyIT - Biblioteca para manipulação de arquivos Impulse Tracker (.it)
"""

# Importações relativas das classes de cada arquivo convertido
from .ITenvelope_node import ITenvelope_node
from .ITenvelope import ITenvelope
from .ITvol_envelope import ITvol_envelope
from .ITpan_envelope import ITpan_envelope
from .ITpitch_envelope import ITpitch_envelope
from .ITinstrument import ITinstrument
from .ITsample import ITsample
from .ITnote import ITnote
from .ITpattern import ITpattern
from .ITfile import ITfile
from .PatternBuilder import PatternBuilder
from .WavInstrumentBuilder import WavInstrumentBuilder

# pyitcompress geralmente contém apenas funções utilitárias (it_decompress8, etc)
# Se quiser exportá-las também, pode descomentar a linha abaixo:
# from .pyitcompress import it_decompress8, it_decompress16

# Define o que será exportado quando alguém der "from pyIT import *"
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
    'WavInstrumentBuilder'
]