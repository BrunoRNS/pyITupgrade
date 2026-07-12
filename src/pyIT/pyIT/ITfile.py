from typing import List

from .ITpattern import ITpattern
from .ITinstrument import ITinstrument
from .ITsample import ITsample

import struct
import logging

class ITfile(object):
    """Represent an Impulse Tracker song file and its internal structures.

    This class manages the song header, order list, instruments, samples,
    patterns, and message data for an IT module.
    """

    Orderlist_offs = 192
    pyIT_Cwt_v = 0x4101

    def __init__(self):
        self.SongName = b''
        self.PHilight_minor = 4
        self.PHilight_major = 16
        
        self.Cwt_v = ITfile.pyIT_Cwt_v
        self.Cmwt = 0x0214
        self.Flags = 0x000d
        self.Special = 0x0006
        self.GV = 128
        self.MV = 48
        self.IS = 6
        self.IT = 125
        self.Sep = 128
        self.PWD = 0x00
        
        self.Message = b''
        
        self.ChannelPans: List[int] = 64 * [32]
        self.ChannelVols: List[int] = 64 * [64]
        
        self.Orders: List[int] = []
        self.Instruments: List[ITinstrument] = []
        self.Samples: List[ITsample] = []
        self.Patterns: List[ITpattern] = []

    def open(self, infilename: str):
        """Load an IT module from a file on disk.

        Args:
            infilename: Path to the input IT file.
        """
        inf = open(infilename, "rb")
        
        buf = inf.read(30)
        (IMPM, self.SongName) = struct.unpack('<4s26s', buf)
        
        assert(IMPM == b'IMPM')
        
        self.SongName = self.SongName.split(b'\0')[0]
        
        buf = inf.read(34)
        (self.PHilight_minor, self.PHilight_major, n_ords, n_insts, n_samps,
         n_ptns, self.Cwt_v, self.Cmwt, self.Flags, self.Special, self.GV, self.MV, # pyright: ignore[reportConstantRedefinition]
         self.IS, self.IT, self.Sep, self.PWD, msglen, offs_msg, _) = struct.unpack( # pyright: ignore[reportConstantRedefinition]
         '<BBHHHHHHHHBBBBBBHII', buf)
        
        offs_ords = ITfile.Orderlist_offs
        offs_instoffs = offs_ords + n_ords
        offs_sampoffs = offs_instoffs + n_insts * 4
        offs_ptnoffs = offs_sampoffs + n_samps * 4
        
        assert(inf.tell() == 0x40)
        
        self.ChannelPans = []
        for _ in range(64):
            self.ChannelPans.append(struct.unpack('<B', inf.read(1))[0])
        
        self.ChannelVols = []
        for _ in range(64):
            self.ChannelVols.append(struct.unpack('<B', inf.read(1))[0])
        
        assert(inf.tell() == offs_ords)
        
        self.Orders = []
        for _ in range(n_ords):
            self.Orders.append(struct.unpack('<B', inf.read(1))[0])
        
        assert(inf.tell() == offs_instoffs)
        
        offs_insts: List[int] = []
        for _ in range(n_insts):
            offs_insts.append(struct.unpack('<I', inf.read(4))[0])
        
        assert(inf.tell() == offs_sampoffs)
        
        offs_samps: List[int] = []
        for _ in range(n_samps):
            offs_samps.append(struct.unpack('<I', inf.read(4))[0])
        
        assert(inf.tell() == offs_ptnoffs)
        
        offs_ptns: List[int] = []
        for _ in range(n_ptns):
            offs_ptns.append(struct.unpack('<I', inf.read(4))[0])
        
        if (self.Special & 0x0001) and (msglen > 0):
            inf.seek(offs_msg)
            self.Message = inf.read(msglen).replace(b'\0', b' ').replace(b'\r', b'\n')[:-1]
        else:
            self.Message = b''
        
        self.Patterns: List[ITpattern] = []
        for offs_ptn in offs_ptns:
            ptn = ITpattern()
            if offs_ptn != 0:
                inf.seek(offs_ptn)
                ptn.load(inf)
            self.Patterns.append(ptn)
        
        self.Instruments: List[ITinstrument] = []
        for offs_inst in offs_insts:
            inf.seek(offs_inst)
            inst = ITinstrument()
            try:
                inst.load(inf)
            except:
                pass
            self.Instruments.append(inst)
        
        self.Samples: List[ITsample] = []
        for offs_samp in offs_samps:
            inf.seek(offs_samp)
            samp = ITsample()
            try:
                samp.load(inf)
            except:
                pass
            self.Samples.append(samp)
        
        inf.close()
        
    def write(self, outfilename: str):
        """Write the current module state to an IT file.

        Args:
            outfilename: Path where the output IT file will be written.
        """
        log = logging.getLogger("pyIT.ITfile.write")
        outf = open(outfilename, "wb")
        
        if (len(self.Message) > 0):
            self.Special = self.Special | 0x0001
            msg_bytes = self.Message if isinstance(self.Message, bytes) else self.Message.encode('ascii', errors='ignore') # pyright: ignore[reportUnnecessaryIsInstance]
            message = msg_bytes.replace(b'\n', b'\r') + b'\0'
        else:
            self.Special = self.Special & (~0x0001)
            message = b''

        self.Cwt_v = ITfile.pyIT_Cwt_v
        
        self.Cmwt = 0x0214
        for sample in self.Samples:
            sample._check_compression_status() # pyright: ignore[reportPrivateUsage]
            if sample.IsCompressed and sample.IT215Compression:
                log.debug("Song contains at least one IT 2.15 sample; setting cmwt == 0x0215")
                self.Cmwt = 0x0215
                break
        
        instoffs_offs = ITfile.Orderlist_offs + len(self.Orders)
        sampoffs_offs = instoffs_offs + len(self.Instruments) * 4
        ptnoffs_offs: int = sampoffs_offs + len(self.Samples) * 4
        msg_offs = ptnoffs_offs + len(self.Patterns) * 4
        ptn_offs = msg_offs + len(message)
        
        unique_ITpatterns: List[ITpattern] = []
        pattern_list: List[int|bool] = []
        
        (pattern_list, unique_ITpatterns) = self.pack_ptns()
        ptn_offsets: dict[int, int] = {}
        offs = ptn_offs
        for x in pattern_list:
            if x is not False and x not in ptn_offsets:
                ptn_offsets[x] = offs
                offs = offs + len(unique_ITpatterns[x])
        
        samp_offs = offs
        inst_offs = samp_offs + sum([len(x) for x in self.Samples])
        sampledata_offs = inst_offs + sum([len(x) for x in self.Instruments])
        
        songname = self.SongName if isinstance(self.SongName, bytes) else self.SongName.encode('ascii', errors='ignore')
        songname = songname[:25].ljust(26, b'\x00')
        
        outf.write(struct.pack('<4s26sBB', b'IMPM', songname, self.PHilight_minor, self.PHilight_major)) # Python 3: b'IMPM'
        outf.write(struct.pack('<HHHHHHHH', len(self.Orders), len(self.Instruments),
                                            len(self.Samples), len(self.Patterns),
                                            self.Cwt_v, self.Cmwt, self.Flags, self.Special))
        outf.write(struct.pack('<BBBBBBHII', self.GV, self.MV, self.IS, self.IT,
                                             self.Sep, self.PWD, len(message), msg_offs, 0))
        for x in self.ChannelPans:
            if (x > 64 and x < 128):
                x = 100 
            elif x < 0:
                x = 0
            outf.write(struct.pack('<B', x))
        
        for x in self.ChannelVols:
            if (x > 64):
                x = 64
            elif x < 0:
                x = 0
            outf.write(struct.pack('<B', x))
        
        assert(outf.tell() == ITfile.Orderlist_offs)
        
        for x in self.Orders:
            if (x > 199):
                if (x < 254):
                    x = 199
                elif (x > 255):
                    x = 255
            elif x < 0:
                x = 0
            outf.write(struct.pack('<B', x))
        
        assert(outf.tell() == instoffs_offs)
        
        offs = inst_offs
        for x in self.Instruments:
            outf.write(struct.pack('<I', offs))
            offs = offs + len(x)
            
        assert(outf.tell() == sampoffs_offs)
        
        offs = samp_offs
        for x in self.Samples:
            outf.write(struct.pack('<I', offs))
            offs = offs + len(x)
        
        assert(outf.tell() == ptnoffs_offs)

        for x in pattern_list:
            if x is False:
                log.debug("write empty pattern offs")
                ptnoffs = 0
            else:
                log.debug("write real pattern offs")
                ptnoffs = ptn_offsets[x]
                
            outf.write(struct.pack('<I', ptnoffs))
        
        assert(outf.tell() == msg_offs)
        if message:
            outf.write(message)
        assert(outf.tell() == ptn_offs)
        
        for ptn in unique_ITpatterns:
            log.debug("write pattern")
            ptn.write(outf)
        assert(outf.tell() == samp_offs)
        
        next_smpoffs = sampledata_offs
        for samp in self.Samples:
            samp.write(outf, next_smpoffs)
            next_smpoffs = next_smpoffs + len(samp.rawSampleData())
        eof = next_smpoffs
        
        assert(outf.tell() == inst_offs)
        
        for inst in self.Instruments:
            inst.write(outf)
        assert(outf.tell() == sampledata_offs)
        
        for samp in self.Samples:
            outf.write(samp.rawSampleData())
        
        assert(outf.tell() == eof)
        outf.close()
        
    def pack_ptns(self) -> tuple[list[int|bool], list[ITpattern]]:
        """Pack patterns into a deduplicated list for serialization.

        Returns:
            A tuple containing the packed pattern references and the unique
            pattern list that should be written.
        """
        ptnlist: List[int|bool] = []
        ptns: List[ITpattern] = []
        
        for ptn in self.Patterns:
            if ptn.isEmpty():
                ptnlist.append(False)
            elif ptn in ptns:
                ptnlist.append(ptns.index(ptn))
            else:
                ptns.append(ptn)
                ptnlist.append(ptns.index(ptn))
        
        return (ptnlist, ptns)

