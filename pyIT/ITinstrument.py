from .ITpan_envelope import ITpan_envelope
from .ITvol_envelope import ITvol_envelope
from .ITpitch_envelope import ITpitch_envelope

import struct

class ITinstrument(object):
    def __init__(self):
        self.Filename = b''  # Python 3: Inicializado como bytes
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
        # TrkVers e NoS são ignorados (usados apenas em arquivos de instrumento)
        self.InstName = b''  # Python 3: Inicializado como bytes
        self.IFC = 0
        self.IFR = 0
        self.MCh = 0
        self.MPr = 0
        self.MIDIBank = 0
        
        self.SampleTable = [[i, 0] for i in range(120)]
        
        self.volEnv = ITvol_envelope()
        self.panEnv = ITpan_envelope()
        self.pitchEnv = ITpitch_envelope()
    
    def write(self, outf):
        # Garante que as strings sejam tratadas como bytes antes de empacotar
        filename = self.Filename if isinstance(self.Filename, bytes) else self.Filename.encode('ascii', errors='ignore')
        inst_name = self.InstName if isinstance(self.InstName, bytes) else self.InstName.encode('ascii', errors='ignore')

        outf.write(struct.pack('<4s12s', b'IMPI', filename)) # Python 3: b'IMPI'
        outf.write(struct.pack('<BBBB', 0, self.NNA, self.DCT, self.DCA))
        outf.write(struct.pack('<HBB', self.FadeOut, self.PPS, self.PPC))
        outf.write(struct.pack('<BBBB', self.GbV, self.DfP, self.RV, self.RP))
        outf.write(struct.pack('<HBB', 0xadde, 0xbe, 0xef)) # dados não utilizados
        outf.write(struct.pack('<26s', inst_name[:25] + b'\0')) # Python 3: b'\0'
        outf.write(struct.pack('<BBBBH', self.IFC, self.IFR, self.MCh, self.MPr, self.MIDIBank))
        for smp in self.SampleTable:
            outf.write(struct.pack('<BB', smp[0], smp[1]))
        
        self.volEnv.write(outf)
        self.panEnv.write(outf)
        self.pitchEnv.write(outf)
        
        outf.write(b'FOOB') # Python 3: b'FOOB'
    
    def load(self, inf):
        """inf deve estar posicionado na posição do instrumento a ser lido"""
        (IMPI, self.Filename) = struct.unpack('<4s12s', inf.read(16))
        assert(IMPI == b'IMPI') # Python 3: Comparação com bytes b'IMPI'
        
        (zero, self.NNA, self.DCT, self.DCA, self.FadeOut, self.PPS, self.PPC, 
         self.GbV, self.DfP, self.RV, self.RP, discard, discard,
         discard) = struct.unpack('<BBBBHBBBBBBHBB', inf.read(16))
        
        # Correção da substituição de caracteres nulos em modo binário
        self.InstName = inf.read(26).replace(b'\0', b' ')[:25]
        
        (self.IFC, self.IFR, self.MCh, self.MPr,
         self.MIDIBank) = struct.unpack('<BBBBH', inf.read(6))
        
        self.SampleTable = []
        for i in range(120): # Python 3: range() no lugar de xrange()
            self.SampleTable.append(list(struct.unpack('<BB', inf.read(2))))
        
        self.volEnv = ITvol_envelope()
        self.panEnv = ITpan_envelope()
        self.pitchEnv = ITpitch_envelope()
        
        self.volEnv.load(inf)
        self.panEnv.load(inf)
        self.pitchEnv.load(inf)
        
        inf.read(4) # leitura dummy
        
    def __len__(self):
        return 554