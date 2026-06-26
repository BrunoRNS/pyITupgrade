
from .ITpattern import ITpattern
from .ITinstrument import ITinstrument
from .ITsample import ITsample

import struct
import logging

class ITfile(object):
    Orderlist_offs = 192 # Comprimento do cabeçalho IT antes dos dados dinâmicos
    pyIT_Cwt_v = 0x4101  # Valor escrito em Cwt_v ("Criado com a versão do tracker")

    def __init__(self):
        self.SongName = b'' # Python 3: Inicializado como bytes
        self.PHilight_minor = 4
        self.PHilight_major = 16
        
        # OrdNum, InsNum, SmpNum, PatNum são usados apenas ao carregar arquivos;
        # os números reais serão baseados em len(lists)
        
        self.Cwt_v = ITfile.pyIT_Cwt_v
        self.Cmwt = 0x0214
        self.Flags = 0x000d
        self.Special = 0x0006
        self.GV = 128     # Volume global
        self.MV = 48      # Volume de mixagem
        self.IS = 6       # Velocidade inicial
        self.IT = 125     # Tempo inicial
        self.Sep = 128    # Separação estéreo
        self.PWD = 0x00
        
        self.Message = b'' # Python 3: Inicializado como bytes
        
        self.ChannelPans = 64 * [32]
        self.ChannelVols = 64 * [64]
        
        self.Orders = []
        self.Instruments = []
        self.Samples = []
        self.Patterns = []

    def open(self, infilename):
        log = logging.getLogger("pyIT.ITfile.open")
        inf = open(infilename, "rb") # Python 3: Substituído file() por open()
        
        buf = inf.read(30)
        (IMPM, self.SongName) = struct.unpack('<4s26s', buf)
        
        assert(IMPM == b'IMPM') # Python 3: Comparação com bytes b'IMPM'
        
        self.SongName = self.SongName.split(b'\0')[0] # Python 3: Split em bytes
        
        buf = inf.read(34)
        (self.PHilight_minor, self.PHilight_major, n_ords, n_insts, n_samps,
         n_ptns, self.Cwt_v, self.Cmwt, self.Flags, self.Special, self.GV, self.MV,
         self.IS, self.IT, self.Sep, self.PWD, msglen, offs_msg, reserved) = struct.unpack(
         '<BBHHHHHHHHBBBBBBHII', buf)
        
        offs_ords = ITfile.Orderlist_offs
        offs_instoffs = offs_ords + n_ords
        offs_sampoffs = offs_instoffs + n_insts * 4
        offs_ptnoffs = offs_sampoffs + n_samps * 4
        
        assert(inf.tell() == 0x40)
        
        self.ChannelPans = []
        for i in range(64): # Python 3: range()
            self.ChannelPans.append(struct.unpack('<B', inf.read(1))[0])
        
        self.ChannelVols = []
        for i in range(64): # Python 3: range()
            self.ChannelVols.append(struct.unpack('<B', inf.read(1))[0])
        
        assert(inf.tell() == offs_ords)
        
        self.Orders = []
        for i in range(n_ords): # Python 3: range()
            self.Orders.append(struct.unpack('<B', inf.read(1))[0])
        
        assert(inf.tell() == offs_instoffs)
        
        offs_insts = []
        for i in range(n_insts): # Python 3: range()
            offs_insts.append(struct.unpack('<I', inf.read(4))[0])
        
        assert(inf.tell() == offs_sampoffs)
        
        offs_samps = []
        for i in range(n_samps): # Python 3: range()
            offs_samps.append(struct.unpack('<I', inf.read(4))[0])
        
        assert(inf.tell() == offs_ptnoffs)
        
        offs_ptns = []
        for i in range(n_ptns): # Python 3: range()
            offs_ptns.append(struct.unpack('<I', inf.read(4))[0])
        
        # Carrega a mensagem da música
        if (self.Special & 0x0001) and (msglen > 0):
            inf.seek(offs_msg)
            self.Message = inf.read(msglen).replace(b'\0', b' ').replace(b'\r', b'\n')[:-1]
        else:
            self.Message = b'' # Python 3: bytes
        
        # Carrega os padrões
        self.Patterns = []
        for offs_ptn in offs_ptns:
            ptn = ITpattern()
            if offs_ptn != 0:
                inf.seek(offs_ptn)
                ptn.load(inf)
            self.Patterns.append(ptn)
        
        # Carrega os instrumentos
        self.Instruments = []
        for offs_inst in offs_insts:
            inf.seek(offs_inst)
            inst = ITinstrument()
            try:
                inst.load(inf)
            except:
                pass
            self.Instruments.append(inst)
        
        # Carrega os samples
        self.Samples = []
        for offs_samp in offs_samps:
            inf.seek(offs_samp)
            samp = ITsample()
            try:
                samp.load(inf)
            except:
                pass
            self.Samples.append(samp)
        
        inf.close()
        
    def write(self, outfilename):
        log = logging.getLogger("pyIT.ITfile.write")
        outf = open(outfilename, "wb") # Python 3: Substituído file() por open()
        
        if (len(self.Message) > 0):
            self.Special = self.Special | 0x0001
            msg_bytes = self.Message if isinstance(self.Message, bytes) else self.Message.encode('ascii', errors='ignore')
            message = msg_bytes.replace(b'\n', b'\r') + b'\0'
        else:
            self.Special = self.Special & (~0x0001)
            message = b'' # Python 3: bytes vazio

        self.Cwt_v = ITfile.pyIT_Cwt_v
        
        self.Cmwt = 0x0214
        for sample in self.Samples:
            sample._check_compression_status()
            if sample.IsCompressed and sample.IT215Compression:
                log.debug("Song contains at least one IT 2.15 sample; setting cmwt == 0x0215")
                self.Cmwt = 0x0215
                break
        
        instoffs_offs = ITfile.Orderlist_offs + len(self.Orders)
        sampoffs_offs = instoffs_offs + len(self.Instruments) * 4
        ptnoffs_offs = sampoffs_offs + len(self.Samples) * 4
        msg_offs = ptnoffs_offs + len(self.Patterns) * 4
        ptn_offs = msg_offs + len(message)
        
        (pattern_list, unique_ITpatterns) = self.pack_ptns()
        ptn_offsets = {} 
        offs = ptn_offs
        for x in pattern_list:
            if x is not False and x not in ptn_offsets:
                ptn_offsets[x] = offs
                offs = offs + len(unique_ITpatterns[x])
        
        samp_offs = offs
        inst_offs = samp_offs + sum([len(x) for x in self.Samples])
        sampledata_offs = inst_offs + sum([len(x) for x in self.Instruments])
        
        # Escreve o cabeçalho
        songname = self.SongName if isinstance(self.SongName, bytes) else self.SongName.encode('ascii', errors='ignore')
        songname = songname[:25].ljust(26, b'\x00') # Python 3: b'\x00'
        
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
        
        # Salva padrões (empacotados)
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
        
    def pack_ptns(self):
        """Retorna uma tupla (pattern_list, unique_ITpatterns)""" 
        ptnlist = []
        ptns = []
        
        for ptn in self.Patterns:
            if ptn.isEmpty():
                ptnlist.append(False)
            elif ptn in ptns:
                ptnlist.append(ptns.index(ptn))
            else:
                ptns.append(ptn)
                ptnlist.append(ptns.index(ptn))
        
        return (ptnlist, ptns)