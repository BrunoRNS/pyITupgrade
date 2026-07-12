"""
 * Schism Tracker - a cross-platform Impulse Tracker clone
 * copyright (c) 2003-2005 Storlek <storlek@rigelseven.com>
 * copyright (c) 2005-2008 Mrs. Brisby <mrs.brisby@nimh.org>
 * copyright (c) 2009 Storlek & Mrs. Brisby
 * URL: http://schismtracker.org/
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import logging
from typing import BinaryIO, Optional


class ReadBitsState:
    def __init__(self) -> None:
        self.bitbuf: int = 0
        self.bitnum: int = 0


def MIN(a: int, b: int) -> int:
    return a if a < b else b


def it_readbits(n: int, state: ReadBitsState, stream: BinaryIO) -> int:
    value = 0
    i = n
    
    while i:
        i -= 1
        if not state.bitnum:
            byte_read = stream.read(1)
            if not byte_read:
                state.bitbuf = 0
            else:
                state.bitbuf = byte_read[0]
            state.bitnum = 8
            
        value >>= 1
        value |= (state.bitbuf << 31) & 0xffffffff
        state.bitbuf >>= 1
        state.bitnum -= 1

    return (value & 0xffffffff) >> (32 - n)

def signbyte(b: int) -> int:
    return b - 256 if b > 127 else b


def unsignbyte(b: int) -> int:
    return b & 0xff


def signword(w: int) -> int:
    return w - 65536 if w > 32767 else w


def unsignword(w: int) -> int:
    return w & 0xffff


def it_decompress8(dest: BinaryIO, length: int, srcbuf: BinaryIO, it215: bool) -> Optional[int]:
    """
    dest: (file-like object) output buffer for decompressed data
    length: number of samples (renomeado de 'len' para evitar shadowing)
    srcbuf: (file-like object) input
    it215: (bool) use it215 algorithm
    
    RETURN: actual size (in bytes) of COMPRESSED data
    """
    state = ReadBitsState()
    log = logging.getLogger("pyitcompress.it_decompress8")
    startpos = srcbuf.tell()
    
    while (length):
        if not srcbuf.read(2):
            return
            
        state.bitbuf = state.bitnum = 0
        blklen = MIN(0x8000, length)
        blkpos = 0
        width = 9 
        d1 = d2 = 0 
        
        while (blkpos < blklen):
            value = it_readbits(width, state, srcbuf)
            
            if (width < 7):
                if (value == 1 << (width - 1)):
                    value = it_readbits(3, state, srcbuf) + 1 
                    width = value if (value < width) else value + 1 
                    continue 
            elif (width < 9):
                border = (0xFF >> (9 - width)) - 4 
                if (value > border and value <= (border + 8)):
                    value -= border 
                    width = value if (value < width) else value + 1 
                    continue 
            elif (width == 9):
                if (value & 0x100):
                    width = (value + 1) & 0xff 
                    continue 
            else:
                log.error("Illegal width")
                return

            if (width < 8):
                shift = 8 - width
                v = signbyte((value << shift) & 0xff)
                v >>= shift
                v = (v & 0xff)
            else:
                v = value & 0xff
            
            d1 = (d1 + v) & 0xff
            d2 = (d2 + d1) & 0xff
            
            out_byte = d2 if it215 else d1
            dest.write(bytes([out_byte]))
            blkpos += 1

        length -= blklen
    
    compressed_len = srcbuf.tell() - startpos
    return compressed_len


def it_decompress16(dest: BinaryIO, length: int, srcbuf: BinaryIO, it215: bool) -> Optional[int]:
    """
    dest: (file-like object) output buffer for decompressed data
    length: number of samples (renomeado de 'len' para evitar shadowing)
    srcbuf: (file-like object) input
    it215: (bool) use it215 algorithm
    """
    state = ReadBitsState()
    log = logging.getLogger("pyitcompress.it_decompress16")
    startpos = srcbuf.tell()

    while (length):
        if not srcbuf.read(2):
            return

        state.bitbuf = state.bitnum = 0
        blklen = MIN(0x4000, length)
        blkpos = 0
        width = 17 
        d1 = d2 = 0 

        while (blkpos < blklen):
            value = it_readbits(width, state, srcbuf)
            
            if (width < 7):
                if (value == 1 << (width - 1)):
                    value = it_readbits(4, state, srcbuf) + 1 
                    width = value if (value < width) else value + 1 
                    continue 
            elif (width < 17):
                border = (0xFFFF >> (17 - width)) - 8 
                if (value > border and value <= (border + 16)):
                    value -= border 
                    width = value if (value < width) else value + 1 
                    continue 
            elif (width == 17):
                if (value & 0x10000):
                    width = (value + 1) & 0xff 
                    continue 
            else:
                log.error("Illegal width")
                return

            if (width < 16):
                shift = 16 - width
                v = signword((value << shift) & 0xffff)
                v >>= shift
            else:
                v = (value & 0xffff)
            
            d1 = (d1 + v) & 0xffff
            d2 = (d2 + d1) & 0xffff
            
            outval = d2 if it215 else d1
            dest.write(bytes([outval & 0xff]))
            dest.write(bytes([unsignbyte(outval >> 8)]))
            blkpos += 1

        length -= blklen

    compressed_len = srcbuf.tell() - startpos
    return compressed_len

