import io
import struct
from typing import List
from .ITenvelope_node import ITenvelope_node

class ITenvelope(object):
    """Represents the structure of an IT instrument envelope.

    The envelope stores activation flags, control points, and the loop and
    sustain boundaries used to describe how volume, pitch, or another
    parameter evolves over time.
    """

    def __init__(self):
        """Initialize the envelope with default IT state values."""
        self.IsOn = False
        self.LoopOn = False
        self.SusloopOn = False
        
        self.LpB = 0
        self.LpE = 0
        self.SLB = 0
        self.SLE = 0
        
        self.numNodePoints = 0
        self.Nodes: List[ITenvelope_node] = [ITenvelope_node() for _ in range(25)]

    def extraFlags(self) -> int:
        """Return any additional envelope flags.

        Returns:
            An integer containing extra flag bits for derived classes.
        """
        return 0
                
    def write(self, outf: io.BufferedWriter):
        """Serialize the envelope to a binary writer.

        Args:
            outf: Buffered writer used to emit the envelope bytes.
        """
        flags = 0
        flags = flags | ((self.IsOn) << 0)
        flags = flags | ((self.LoopOn) << 1)
        flags = flags | ((self.SusloopOn) << 2)
        flags = flags | self.extraFlags()
    
        outf.write(struct.pack('<BBBB', flags, self.numNodePoints, self.LpB, self.LpE))
        outf.write(struct.pack('<BB', self.SLB, self.SLE))
        
        for node in self.Nodes:
            outf.write(struct.pack('<bH', node.y_val, node.tick))
        
        outf.write(b'\0')
    
    def load(self, inf: io.BufferedReader):
        """Load the envelope data from a binary reader.

        Args:
            inf: Buffered reader containing the serialized envelope data.
        """
        (flags, self.numNodePoints, self.LpB, self.LpE, self.SLB, # pyright: ignore[reportConstantRedefinition]
         self.SLE) = struct.unpack('<BBBBBB', inf.read(6)) # pyright: ignore[reportConstantRedefinition]
        
        self.setFlags(flags)
        
        self.Nodes: List[ITenvelope_node] = []
        
        for _ in range(25):
            node = ITenvelope_node()
            self.Nodes.append(node)
            (node.y_val, node.tick) = struct.unpack('<bH', inf.read(3))
        inf.read(1)
        
    def setFlags(self, flags: int):
        """Apply the packed flag bits to the envelope state.

        Args:
            flags: Integer containing the encoded envelope flags.
        """
        self.IsOn = bool(flags & 0x01)
        self.LoopOn = bool(flags & 0x02)
        self.SusloopOn = bool(flags & 0x04)
        
    def __len__(self):
        """Return the serialized size of the envelope in bytes."""
        return 82
    
