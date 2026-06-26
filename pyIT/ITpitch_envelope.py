from .ITenvelope import ITenvelope

class ITpitch_envelope(ITenvelope):
    def __init__(self):
        super().__init__()
        self.IsFilter = False
    
    def extraFlags(self):
        if self.IsFilter:
            return 0x80
        else:
            return 0
    
    def setFlags(self, flags):
        super().setFlags(flags) # Atualizado para usar o super() do Python 3
        self.IsFilter = bool(flags & 0x80)