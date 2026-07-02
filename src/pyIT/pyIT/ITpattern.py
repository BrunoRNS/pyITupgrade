from .ITnote import ITnote

import io
import struct
import logging

class ITpattern(object):
    def __init__(self):
        # Preenche o padrão com instâncias vazias de ITnote.
        # self.Rows[4][2] retornará a nota no terceiro canal da quinta linha.
        self.Rows = [[ITnote() for i in range(64)] for j in range(64)] # Python 3: range()

    def __len__(self):
        return len(self.pack()) + 8
    
    def __eq__(self, other):
        return self.Rows == other.Rows
    
    def __ne__(self, other):
        return not (self == other)
    
    def isEmpty(self):
        """ 'empty' aqui usa a definição do IT de um padrão de 64 linhas sem dados de notas. """
        return self == ITpattern()
        
    def write(self, outf):
        ptndata = self.pack()
        outf.write(struct.pack('<HH4s', len(ptndata), len(self.Rows), b'\0'*4)) # Python 3: b'\0'*4
        outf.write(ptndata)
    
    def unpack(self, rows, ptndata):
        """
        Desempacota os dados brutos do padrão armazenados em ptndata.
        """
        log = logging.getLogger("pyIT.ITpattern.unpack")
        log.info("load pattern: rows = %d, len = %d" % (rows, len(ptndata),))
        
        ptn_reader = io.BytesIO(ptndata) # Python 3: Alterado StringIO -> io.BytesIO
        masks = [0] * 64 # Prepara variáveis de máscara
        last_note = [ITnote() for i in range(64)] # Python 3: range()
        
        # Reseta os dados das linhas
        self.Rows = [[ITnote() for i in range(64)] for j in range(rows)] # Python 3: range()
        
        row_num = 0
        
        while True:
            chan_data = ptn_reader.read(1)
            
            if chan_data == b'': # Python 3: Fim dos dados em bytes
                break
            
            chan_data = struct.unpack('<B', chan_data)[0]
            
            if chan_data == 0: # Fim da linha
                row_num = row_num + 1
                continue
            
            chan_num = (chan_data - 1) & 63 # Obtém o número do canal para estes dados
            
            if chan_data & 128: # Novo valor para a variável de máscara deste canal
                masks[chan_num] = struct.unpack('<B', ptn_reader.read(1))[0]
            
            mask = masks[chan_num]
            if mask & 1:
                self.Rows[row_num][chan_num].Note = struct.unpack('<B', ptn_reader.read(1))[0]
                last_note[chan_num].Note = self.Rows[row_num][chan_num].Note
            if mask & 2:
                self.Rows[row_num][chan_num].Instrument = struct.unpack('<B', ptn_reader.read(1))[0]
                last_note[chan_num].Instrument = self.Rows[row_num][chan_num].Instrument
            if mask & 4:
                self.Rows[row_num][chan_num].Volume = struct.unpack('<B', ptn_reader.read(1))[0]
                last_note[chan_num].Volume = self.Rows[row_num][chan_num].Volume
            if mask & 8:
                (self.Rows[row_num][chan_num].Effect,
                 self.Rows[row_num][chan_num].EffectArg) = struct.unpack('<BB', ptn_reader.read(2))
                last_note[chan_num].Effect = self.Rows[row_num][chan_num].Effect
                last_note[chan_num].EffectArg = self.Rows[row_num][chan_num].EffectArg
            if mask & 16:
                self.Rows[row_num][chan_num].Note = last_note[chan_num].Note
            if mask & 32:
                self.Rows[row_num][chan_num].Instrument = last_note[chan_num].Instrument
            if mask & 64:
                self.Rows[row_num][chan_num].Volume = last_note[chan_num].Volume
            if mask & 128:
                self.Rows[row_num][chan_num].Effect = last_note[chan_num].Effect
                self.Rows[row_num][chan_num].EffectArg = last_note[chan_num].EffectArg
                
    def pack(self):
        """
        Empacota os dados do padrão de volta e os retorna como uma string de bytes brutos.
        """
        log = logging.getLogger("pyIT.ITpattern.unpack")

        ptn_writer = io.BytesIO() # Python 3: Alterado StringIO -> io.BytesIO
        masks = [0] * 64 
        last_note = [ITnote() for i in range(64)] # Python 3: range()
        empty_note = ITnote()
        
        for row_data in self.Rows:
            for chan_num in range(64): # Python 3: range()
                note = row_data[chan_num]
                if note == empty_note:
                    continue
                
                mask = 0
                packed_note = io.BytesIO() # Python 3: Alterado StringIO -> io.BytesIO
                
                if note.Note is not None:
                    if note.Note == last_note[chan_num].Note:
                        mask |= 16
                    else:
                        packed_note.write(struct.pack('<B', note.Note))
                        last_note[chan_num].Note = note.Note
                        mask |= 1
                if note.Instrument is not None:
                    if note.Instrument == last_note[chan_num].Instrument:
                        mask |= 32
                    else:
                        packed_note.write(struct.pack('<B', note.Instrument))
                        last_note[chan_num].Instrument = note.Instrument
                        mask |= 2
                if note.Volume is not None:
                    if note.Volume == last_note[chan_num].Volume:
                        mask |= 64
                    else:
                        packed_note.write(struct.pack('<B', note.Volume))
                        last_note[chan_num].Volume = note.Volume
                        mask |= 4
                if note.Effect is not None or note.EffectArg is not None:
                    if (note.Effect == last_note[chan_num].Effect and 
                        note.EffectArg == last_note[chan_num].EffectArg):
                        mask |= 128
                    else:
                        mask |= 8
                        write_effect = note.Effect
                        write_effectarg = note.EffectArg
                        if write_effect is None:
                            write_effect = 0
                        if write_effectarg is None:
                            write_effectarg = 0
                            
                        last_note[chan_num].Effect = write_effect
                        last_note[chan_num].EffectArg = write_effectarg
                        
                        packed_note.write(struct.pack('<BB',
                                                      write_effect,
                                                      write_effectarg))
                
                # Verifica se reutilizaremos a última máscara
                if mask == masks[chan_num]:
                    ptn_writer.write(struct.pack('<B', (chan_num + 1)))
                else:
                    ptn_writer.write(struct.pack('<BB',
                                        (chan_num + 1) | 128,
                                        mask))
                    masks[chan_num] = mask
                ptn_writer.write(packed_note.getvalue())
                
            # Escreve o marcador de fim de linha
            ptn_writer.write(b"\x00") # Python 3: Literal de bytes b"\x00"
        
        return ptn_writer.getvalue()
        
    def load(self, inf):
        """Carrega os dados do padrão IT a partir de inf. inf já deve estar posicionado."""
        (ptnlen, rows, discard) = struct.unpack('<HH4s', inf.read(8))
        ptndata = inf.read(ptnlen)
        
        self.unpack(rows, ptndata)
