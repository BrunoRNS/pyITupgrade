from typing import List, Optional

from .ITnote import ITnote

import io
import struct
import logging

class ITpattern(object):
    """Represent a pattern of note events in an IT module.

    A pattern contains 64 channels and 64 rows by default, and each cell may
    hold a note event with instrument, volume, and effect data.
    """

    Rows: List[List[ITnote]]

    def __init__(self) -> None:
        """Initialize a pattern with an empty 64x64 grid of note cells."""
        self.Rows = [[ITnote() for _ in range(64)] for _ in range(64)]

    def __len__(self) -> int:
        """Return the serialized size of the pattern in bytes."""
        return len(self.pack()) + 8

    def __eq__(self, other: object) -> bool:
        
        if isinstance(other, ITpattern):
            return self.Rows == other.Rows
        
        else: return False
    
    def __ne__(self, other: object) -> bool:
        """Return the inverse of :meth:`__eq__`."""
        return not (self == other)

    def isEmpty(self) -> bool:
        """Return whether the pattern is empty.

        Returns:
            ``True`` when the pattern contains no populated note events.
        """
        return self == ITpattern()

    def write(self, outf: io.BufferedWriter) -> None:
        ptndata = self.pack()
        outf.write(struct.pack('<HH4s', len(ptndata), len(self.Rows), b'\0'*4))
        outf.write(ptndata)
        
    @staticmethod
    def copy_channel(src: 'ITpattern', src_chn: int, dest: 'ITpattern', dest_chn: int) -> None:
        """Copy all notes from one channel of a source pattern to a destination pattern.

        The source and destination patterns can have different row counts; only the
        rows that exist in both patterns will be copied. Each note is deep-copied
        so that subsequent modifications do not affect the other pattern.

        Args:
            src: source pattern from which to read channel data.
            src_chn: index of the channel in *src* to copy from (0‑63).
            dest: destination pattern where channel data is written.
            dest_chn: index of the channel in *dest* to copy to (0‑63).
        """
        
        rows_to_copy = min(len(src.Rows), len(dest.Rows))
        for row in range(rows_to_copy):
            src_note = src.Rows[row][src_chn]
            
            new_note = ITnote()
            new_note.Note = src_note.Note
            new_note.Instrument = src_note.Instrument
            new_note.Volume = src_note.Volume
            new_note.Effect = src_note.Effect
            new_note.EffectArg = src_note.EffectArg
            dest.Rows[row][dest_chn] = new_note
    
    def unpack(self, rows: int, ptndata: bytes) -> None:
        """Deserialize pattern data into the current row grid.

        Args:
            rows: Number of rows to allocate for the pattern.
            ptndata: Serialized pattern payload bytes.
        """
        
        log = logging.getLogger("pyIT.ITpattern.unpack")
        log.info("load pattern: rows = %d, len = %d" % (rows, len(ptndata),))
        
        ptn_reader = io.BytesIO(ptndata)
        masks: List[int] = [0] * 64
        
        last_note = [ITnote() for _ in range(64)]

        self.Rows = [[ITnote() for _ in range(64)] for _ in range(rows)]
        
        row_num = 0
        
        while True:
            chan_data = ptn_reader.read(1)
            
            if chan_data == b'':
                break
            
            chan_data = struct.unpack('<B', chan_data)[0]
            
            if chan_data == 0:
                row_num = row_num + 1
                continue
            
            chan_num: int = (chan_data - 1) & 63
            
            if chan_data & 128:
                masks[chan_num] = struct.unpack('<B', ptn_reader.read(1))[0]
            
            mask: int = masks[chan_num]
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
                
    def pack(self) -> bytes:
        """Serialize the pattern into the IT packed pattern format.

        Returns:
            The packed pattern bytes.
        """

        ptn_writer = io.BytesIO()
        masks = [0] * 64 
        last_note = [ITnote() for _ in range(64)]
        empty_note = ITnote()
        
        for row_data in self.Rows:
            for chan_num in range(64):
                note = row_data[chan_num]
                if note == empty_note:
                    continue
                
                mask = 0
                packed_note = io.BytesIO()
                
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

                if mask == masks[chan_num]:
                    ptn_writer.write(struct.pack('<B', (chan_num + 1)))
                else:
                    ptn_writer.write(struct.pack('<BB',
                                        (chan_num + 1) | 128,
                                        mask))
                    masks[chan_num] = mask
                ptn_writer.write(packed_note.getvalue())
                
            ptn_writer.write(b"\x00")
        
        return ptn_writer.getvalue()
        
    def load(self, inf: io.BufferedReader) -> None:
        """Load a pattern from a binary reader.

        Args:
            inf: Buffered reader containing the serialized pattern data.
        """
        
        (ptnlen, rows, _) = struct.unpack('<HH4s', inf.read(8))
        ptndata = inf.read(ptnlen)
        
        self.unpack(rows, ptndata)

    def add_note_to_final(self, 
                          channel: int, 
                          note: Optional[int] = None, 
                          instrument: Optional[int] = None, 
                          volume: Optional[int] = None, 
                          effect: Optional[int] = None, 
                          effect_arg: Optional[int] = None) -> bool:
        """
        Add a note to the final row of the pattern.
        If the pattern is full, return False.
        """
        
        empty_note = ITnote()
        last_used_row = -1
        
        for row_idx in range(len(self.Rows)):
            if any(cell != empty_note for cell in self.Rows[row_idx]):
                last_used_row = row_idx
                
        target_row = last_used_row + 1
        
        if target_row < 0:
            target_row = 0
            
        if target_row >= len(self.Rows):
            return False
            
        target_cell = self.Rows[target_row][channel]
        target_cell.Note = note
        target_cell.Instrument = instrument
        target_cell.Volume = volume
        target_cell.Effect = effect
        target_cell.EffectArg = effect_arg
        
        return True
    
