import struct
from .ITenvelope_node import ITenvelope_node

class ITenvelope(object):
    def __init__(self):
        self.IsOn = False
        self.LoopOn = False
        self.SusloopOn = False
        
        self.LpB = 0
        self.LpE = 0
        self.SLB = 0
        self.SLE = 0
        
        # O self.Nodes list conterá o número de node points fixos em 25
        self.numNodePoints = 0
        self.Nodes = [ITenvelope_node() for i in range(25)] # Python 3: range() no lugar de xrange()

    def extraFlags(self):
        return 0
                
    def write(self, outf):
        flags = 0
        flags = flags | ((self.IsOn) << 0)
        flags = flags | ((self.LoopOn) << 1)
        flags = flags | ((self.SusloopOn) << 2)
        flags = flags | self.extraFlags()
    
        outf.write(struct.pack('<BBBB', flags, self.numNodePoints, self.LpB, self.LpE))
        outf.write(struct.pack('<BB', self.SLB, self.SLE))
        
        for node in self.Nodes:
            outf.write(struct.pack('<bH', node.y_val, node.tick))
        
        outf.write(b'\0') # Python 3: b'\0' indica string de bytes pura
    
    def load(self, inf):
        (flags, self.numNodePoints, self.LpB, self.LpE, self.SLB,
         self.SLE) = struct.unpack('<BBBBBB', inf.read(6))
        
        self.setFlags(flags)
        
        self.Nodes = []
        
        for i in range(25): # Python 3: range() no lugar de xrange()
            node = ITenvelope_node()
            self.Nodes.append(node)
            (node.y_val, node.tick) = struct.unpack('<bH', inf.read(3))
        inf.read(1)
        
    def setFlags(self, flags):
        self.IsOn = bool(flags & 0x01)
        self.LoopOn = bool(flags & 0x02)
        self.SusloopOn = bool(flags & 0x04)
        
    def __len__(self):
        return 82