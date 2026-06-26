from . import pyitcompress
import io
import struct
import logging
import traceback

class ITsample(object):
    def __init__(self):
        self.Filename = b''  # Python 3: bytes
        self.GvL = 64
        
        self.IsSample = False
        self.Is16bit = False
        self.IsStereo = False
        self.IsCompressed = False
        self.IsLooped = False
        self.IsSusLooped = False
        self.IsPingPongLoop = False
        self.IsPingPongSusLoop = False
        
        self.Vol = 64
        self.SampleName = b''  # Python 3: bytes
        self.Cvt = 0x01
        self.DfP = 0x00
        
        # O comprimento é determinado pelos dados do sample
        # Nota: comprimentos e índices de loop são em SAMPLES, não BYTES
        
        self.LoopBegin = 0
        self.LoopEnd = 0
        self.C5Speed = 8363
        self.SusLoopBegin = 0
        self.SusLoopEnd = 0
        self.ViS = 0
        self.ViD = 0
        self.ViT = 0
        self.ViR = 0
        
        self.SampleData = b''  # Python 3: bytes
        self.CompressedSampleData = None
        self._original_sample_data = self.SampleData
    
    def sampleDataLen(self):
        """
        Retorna o comprimento dos dados do sample em SAMPLES.
        """
        divider = 1
        if self.Is16bit:
            divider = divider * 2
        if self.IsStereo:
            divider = divider * 2
            
        return len(self.SampleData) // divider  # Python 3: força divisão inteira
    
    def rawSampleData(self):
        """
        Retorna os dados brutos do sample.
        """
        self._check_compression_status()
        
        if self.IsCompressed and self.CompressedSampleData is not None:
            return self.CompressedSampleData
        else:
            return self.SampleData
    
    def _check_compression_status(self):
        if self.IsCompressed and self.modified():
            self.IsCompressed = False
        
    def write(self, outf, sample_offset):
        log = logging.getLogger('pyIT.ITsample.save')
        
        if not self.IsSample:
            self.SampleData = b''
        
        self._check_compression_status()
        
        flags = 0
        flags = flags | ((self.IsSample) << 0)
        flags = flags | ((self.Is16bit) << 1)
        flags = flags | ((self.IsStereo) << 2)
        flags = flags | ((self.IsCompressed) << 3)
        flags = flags | ((self.IsLooped) << 4)
        flags = flags | ((self.IsSusLooped) << 5)
        flags = flags | ((self.IsPingPongLoop) << 6)
        flags = flags | ((self.IsPingPongSusLoop) << 7)

        filename = self.Filename if isinstance(self.Filename, bytes) else self.Filename.encode('ascii', errors='ignore')
        sample_name = self.SampleName if isinstance(self.SampleName, bytes) else self.SampleName.encode('ascii', errors='ignore')
        
        outf.write(struct.pack('<4s12s', b'IMPS', filename))  # Python 3: b'IMPS'
        outf.write(struct.pack('<BBBB', 0, self.GvL, flags, self.Vol))
        outf.write(struct.pack('<26s', sample_name[:25] + b'\0'))  # Python 3: b'\0'
        outf.write(struct.pack('<BB', self.Cvt, self.DfP))
        outf.write(struct.pack('<I', self.sampleDataLen()))
        outf.write(struct.pack('<III', self.LoopBegin, self.LoopEnd, self.C5Speed))
        outf.write(struct.pack('<II', self.SusLoopBegin, self.SusLoopEnd))
        outf.write(struct.pack('<I', sample_offset))
        outf.write(struct.pack('<BBBB', self.ViS, self.ViD, self.ViT, self.ViR))

    def load(self, inf):
        log = logging.getLogger('pyIT.ITsample.load')
        
        (IMPS, self.Filename) = struct.unpack('<4s12s', inf.read(16))
        assert(IMPS == b'IMPS')  # Python 3: Comparação de bytes b'IMPS'
        
        (zero, self.GvL, flags, self.Vol) = struct.unpack('<BBBB', inf.read(4))
        
        self.IsSample = bool(flags & 0x01)
        self.Is16bit = bool(flags & 0x02)
        self.IsStereo = bool(flags & 0x04)
        self.IsCompressed = bool(flags & 0x08)
        self.IsLooped = bool(flags & 0x10)
        self.IsSusLooped = bool(flags & 0x20)
        self.IsPingPongLoop = bool(flags & 0x40)
        self.IsPingPongSusLoop = bool(flags & 0x80)
        
        self.SampleName = inf.read(26).replace(b'\0', b' ')[:25]  # Python 3: replace em bytes
        
        log.debug("=> Loading sample %s" % (self.SampleName,))
        
        (self.Cvt, self.DfP) = struct.unpack('<BB', inf.read(2))
        log.debug("     Cvt (convert) = 0x%02x" % (self.Cvt,))
        self.IT215Compression = self.IsCompressed and bool(self.Cvt & 0x04)
        
        (length, self.LoopBegin, self.LoopEnd, self.C5Speed) = struct.unpack('<IIII', inf.read(16))
        (self.SusLoopBegin, self.SusLoopEnd, offs_sampledata, self.ViS,
         self.ViD, self.ViT, self.ViR) = struct.unpack('<IIIBBBB', inf.read(16))
        
        if self.IsSample and length > 0:
            mult = 1
            if self.Is16bit:
                mult = mult * 2
            if self.IsStereo:
                mult = mult * 2
            
            log.debug("     length in samples is %d" % (length,))
            if self.IsCompressed:
                log.debug("     compressed!")
                
                decompressedbuf = io.BytesIO()  # Python 3: Substituído cStringIO por io.BytesIO
                
                if self.Is16bit:
                    decompressor = pyitcompress.it_decompress16
                    log.debug("     16-bit compressed sample at %d" % (offs_sampledata,))
                else:
                    decompressor = pyitcompress.it_decompress8
                    log.debug("     8-bit compressed sample at %d" % (offs_sampledata,))
                    
                inf.seek(offs_sampledata)
                
                try:
                    if self.IT215Compression:
                        log.debug("     IT 2.15 sample compression")
                    
                    compressed_len = decompressor(decompressedbuf, length, inf, self.IT215Compression)
                    self.SampleData = decompressedbuf.getvalue()
                    log.debug("     compressed length: %d; decompressed length: %d" % (compressed_len, len(self.SampleData)))
                    
                    inf.seek(offs_sampledata)
                    self.CompressedSampleData = inf.read(compressed_len)
                    self._original_sample_data = self.SampleData
                    
                except:
                    print()  # Python 3: Print vazio com parênteses
                    traceback.print_exc()
            else:
                length = length * mult
                log.debug("     length in bytes is %s" % (length,))
                inf.seek(offs_sampledata)
                self.SampleData = inf.read(length)
                self.CompressedSampleData = None
                self._original_sample_data = self.SampleData
            
    def modified(self):
        return (self.SampleData is not self._original_sample_data)
        
    def __len__(self):
        return 80
