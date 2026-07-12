import io
from typing import Any, List, Tuple

from .ITpan_envelope import ITpan_envelope
from .ITvol_envelope import ITvol_envelope
from .ITpitch_envelope import ITpitch_envelope

import struct

class ITinstrument(object):
    """Represent an IT instrument definition and its associated envelopes.

    An instrument contains metadata, sample mapping information, and the
    volume, pan, and pitch envelope data that shape playback behavior.
    """

    def __init__(self):
        """Initialize an instrument with default IT-compatible values."""
        self.Filename = b''
        self.NNA = 0
        self.DCT = 0
        self.DCA = 0
        self.FadeOut = 0
        self.PPS = 0
        self.PPC = 0x3c
        self.GbV = 128
        self.DfP = 128
        self.RV = 0
        self.RP = 0
        
        self.InstName = b''
        self.IFC = 0
        self.IFR = 0
        self.MCh = 0
        self.MPr = 0
        self.MIDIBank = 0
        
        self.SampleTable = [[i, 0] for i in range(120)]
        
        self.volEnv = ITvol_envelope()
        self.panEnv = ITpan_envelope()
        self.pitchEnv = ITpitch_envelope()
    
    def write(self, outf: io.BufferedWriter):
        """Serialize the instrument to a binary writer.

        Args:
            outf: Buffered writer used to emit the instrument bytes.
        """
        
        filename = self.Filename if isinstance(self.Filename, bytes) else self.Filename.encode('ascii', errors='ignore')
        inst_name = self.InstName if isinstance(self.InstName, bytes) else self.InstName.encode('ascii', errors='ignore') # pyright: ignore[reportUnnecessaryIsInstance] # py

        outf.write(struct.pack('<4s12s', b'IMPI', filename))
        outf.write(struct.pack('<BBBB', 0, self.NNA, self.DCT, self.DCA))
        outf.write(struct.pack('<HBB', self.FadeOut, self.PPS, self.PPC))
        outf.write(struct.pack('<BBBB', self.GbV, self.DfP, self.RV, self.RP))
        outf.write(struct.pack('<HBB', 0xadde, 0xbe, 0xef))
        outf.write(struct.pack('<26s', inst_name[:25] + b'\0'))
        outf.write(struct.pack('<BBBBH', self.IFC, self.IFR, self.MCh, self.MPr, self.MIDIBank))
        
        for smp in self.SampleTable:
            outf.write(struct.pack('<BB', smp[0], smp[1]))
        
        self.volEnv.write(outf)
        self.panEnv.write(outf)
        self.pitchEnv.write(outf)
        
        outf.write(b'FOOB')
    
    def load(self, inf: io.BufferedReader) -> None:
        """Deserialize an instrument from a binary reader.

        Args:
            inf: Buffered reader containing the serialized instrument data.
        """
        
        (IMPI, self.Filename) = struct.unpack('<4s12s', inf.read(16))
        assert(IMPI == b'IMPI')
        
        (_, self.NNA, self.DCT, self.DCA, self.FadeOut, self.PPS, self.PPC, # pyright: ignore[reportConstantRedefinition]
         self.GbV, self.DfP, self.RV, self.RP, _, _, # pyright: ignore[reportConstantRedefinition]
         _) = struct.unpack('<BBBBHBBBBBBHBB', inf.read(16))
        
        self.InstName = inf.read(26).replace(b'\0', b' ')[:25]
        
        (self.IFC, self.IFR, self.MCh, self.MPr, # pyright: ignore[reportConstantRedefinition]
         self.MIDIBank) = struct.unpack('<BBBBH', inf.read(6))
        
        self.SampleTable: List[List[int|Tuple[Any, ...]]] = []
        for _ in range(120):
            self.SampleTable.append(list(struct.unpack('<BB', inf.read(2))))
        
        self.volEnv = ITvol_envelope()
        self.panEnv = ITpan_envelope()
        self.pitchEnv = ITpitch_envelope()
        
        self.volEnv.load(inf)
        self.panEnv.load(inf)
        self.pitchEnv.load(inf)
        
        inf.read(4)
        
    def __len__(self) -> int:
        """Return the serialized size of the instrument in bytes."""
        return 554
    
