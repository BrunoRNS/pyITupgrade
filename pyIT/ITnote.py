class ITnote(object):
    def __init__(self):
        self.Note = None
        self.Instrument = None
        self.Volume = None
        self.Effect = None
        self.EffectArg = None
    
    def __eq__(self, other):
        return (self.Note == other.Note and
                self.Instrument == other.Instrument and
                self.Volume == other.Volume and
                self.Effect == other.Effect and
                self.EffectArg == other.EffectArg)
        
    def __ne__(self, other):
        return not (self == other)
    
    def note_num_as_str(self, note_num):
        # C C# D D# E F F# G G# A A# B
        if self.Note is None:
            return '...'
        if self.Note == 254:
            return '^^^'
        if self.Note == 255:
            return '==='
        
        note_list = [
            'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        pitch = note_list[note_num % 12]
        octave = note_num // 12  # Python 3: alterado '/' para '//' para garantir que o resultado seja int
        
        return ('%-2s%d' % (pitch, octave)).replace(' ', '-')
    
    def __str__(self):
        if self.Instrument is None:
            instrument = ".."
        else:
            instrument = "%02d" % self.Instrument
        if self.Volume is None:
            volume = ".."
        else:
            volume = "%02d" % self.Volume
            
        if self.Effect is None:
            effect = ".."
        else:
            effect = "%02d" % self.Effect
            
        if self.EffectArg is None:
            effectarg = ".."
        else:
            effectarg = "%02x" % self.EffectArg
            
        return "%s %s %s %s%s" % (self.note_num_as_str(self.Note),
                                 instrument,
                                 volume,
                                 effect,
                                 effectarg
                                )