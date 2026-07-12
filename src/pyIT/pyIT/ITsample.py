from . import pyitcompress
import io
import struct
import logging
import traceback

class ITsample(object):
    """Represent a sample entry in an IT module.

    An IT sample contains playback metadata, loop information, and the raw
    sample payload used by the module. It can also track compressed sample
    data and serialization state.
    """

    def __init__(self) -> None:
        """Initialize the sample with default IT-compatible values."""
        self.Filename = b''
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
        self.SampleName = b''
        self.Cvt = 0x01
        self.DfP = 0x00
        

        self.LoopBegin = 0
        self.LoopEnd = 0
        self.C5Speed = 8363
        self.SusLoopBegin = 0
        self.SusLoopEnd = 0
        self.ViS = 0
        self.ViD = 0
        self.ViT = 0
        self.ViR = 0
        
        self.SampleData = b''
        self.CompressedSampleData = None
        self._original_sample_data = self.SampleData
    
    def sampleDataLen(self) -> int:
        """Return the logical sample length in samples.

        Returns:
            The number of audio samples represented by the stored payload.
        """
        divider = 1
        if self.Is16bit:
            divider = divider * 2
        if self.IsStereo:
            divider = divider * 2
            
        return len(self.SampleData) // divider
    
    
    def rawSampleData(self) -> bytes:
        """Return the active payload bytes for serialization.

        Returns:
            The compressed payload when compression is active, otherwise the
            stored uncompressed sample data.
        """
        self._check_compression_status()
        
        if self.IsCompressed and self.CompressedSampleData is not None:
            return self.CompressedSampleData
        else:
            return self.SampleData
    
    def _check_compression_status(self) -> None:
        """Invalidate compression state if the sample data has changed."""
        if self.IsCompressed and self.modified():
            self.IsCompressed = False
        
    def write(self, outf: io.BufferedWriter, sample_offset: int) -> None:
        """Serialize the sample metadata and payload to a binary writer.

        Args:
            outf: Buffered writer used to emit the sample bytes.
            sample_offset: Offset of the sample data in the output file.
        """
        
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
        sample_name = self.SampleName if isinstance(self.SampleName, bytes) else self.SampleName.encode('ascii', errors='ignore') # pyright: ignore[reportUnnecessaryIsInstance]
        
        outf.write(struct.pack('<4s12s', b'IMPS', filename))
        outf.write(struct.pack('<BBBB', 0, self.GvL, flags, self.Vol))
        outf.write(struct.pack('<26s', sample_name[:25] + b'\0'))
        outf.write(struct.pack('<BB', self.Cvt, self.DfP))
        outf.write(struct.pack('<I', self.sampleDataLen()))
        outf.write(struct.pack('<III', self.LoopBegin, self.LoopEnd, self.C5Speed))
        outf.write(struct.pack('<II', self.SusLoopBegin, self.SusLoopEnd))
        outf.write(struct.pack('<I', sample_offset))
        outf.write(struct.pack('<BBBB', self.ViS, self.ViD, self.ViT, self.ViR))

    def load(self, inf: io.BufferedReader) -> None:
        """Deserialize a sample from a binary reader.

        Args:
            inf: Buffered reader containing the serialized sample data.
        """
        log = logging.getLogger('pyIT.ITsample.load')
        
        (IMPS, self.Filename) = struct.unpack('<4s12s', inf.read(16))
        assert(IMPS == b'IMPS')
        
        (_, self.GvL, flags, self.Vol) = struct.unpack('<BBBB', inf.read(4))
        
        self.IsSample = bool(flags & 0x01)
        self.Is16bit = bool(flags & 0x02)
        self.IsStereo = bool(flags & 0x04)
        self.IsCompressed = bool(flags & 0x08)
        self.IsLooped = bool(flags & 0x10)
        self.IsSusLooped = bool(flags & 0x20)
        self.IsPingPongLoop = bool(flags & 0x40)
        self.IsPingPongSusLoop = bool(flags & 0x80)
        
        self.SampleName = inf.read(26).replace(b'\0', b' ')[:25]
        
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
                
                decompressedbuf = io.BytesIO()
                
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
                    print()
                    traceback.print_exc()
            else:
                length = length * mult
                log.debug("     length in bytes is %s" % (length,))
                inf.seek(offs_sampledata)
                self.SampleData = inf.read(length)
                self.CompressedSampleData = None
                self._original_sample_data = self.SampleData
            
    def modified(self) -> bool:
        """Return whether the sample data differs from the original payload."""
        return (self.SampleData is not self._original_sample_data)

    def __len__(self) -> int:
        """Return the serialized size of the sample header in bytes."""
        return 80
