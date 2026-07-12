from typing import Any, Optional


class ITnote(object):
    """Represent a single note event in an IT pattern.

    An IT note stores the note number, instrument index, volume, effect code,
    and effect argument for a given pattern position. The values are initially
    unset and may be populated later during parsing or editing.
    """

    def __init__(self):
        """Initialize the note with unset values.

        The note fields remain ``None`` until explicitly assigned by the caller
        or by the loader that parses an IT pattern.
        """
        self.Note: Optional[int] = None
        self.Instrument: Optional[Any] = None
        self.Volume: Optional[Any] = None
        self.Effect: Optional[Any] = None
        self.EffectArg: Optional[Any] = None
    
    def __eq__(self, other: object) -> bool:
        """Compare this note with another object for equality.

        Args:
            other: The object to compare against.

        Returns:
            ``True`` when both notes contain the same note, instrument,
            volume, effect, and effect argument values.
        """
        if not isinstance(other, ITnote):
            return False
        return (self.Note == other.Note and
                self.Instrument == other.Instrument and
                self.Volume == other.Volume and
                self.Effect == other.Effect and
                self.EffectArg == other.EffectArg)
        
    def __ne__(self, other: object) -> bool:
        """Return the inverse of :meth:`__eq__`."""
        return not self.__eq__(other)
    
    def note_num_as_str(self, note_num: int) -> str:
        """Convert an IT note number into a human-readable note name.

        Args:
            note_num: The numeric note value used by the IT format.

        Returns:
            A string such as ``C-4`` or ``A#5``. Special values ``254`` and
            ``255`` are rendered as ``^^^`` and ``===`` respectively.
        """
        if self.Note is None:
            return '...'
        if self.Note == 254:
            return '^^^'
        if self.Note == 255:
            return '==='
        
        note_list = [
            'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        pitch = note_list[note_num % 12]
        octave = note_num // 12
        
        return ('%-2s%d' % (pitch, octave)).replace(' ', '-')
    
    def __str__(self) -> str:
        """Render the note as a compact display string.

        Returns:
            A formatted string containing the note name, instrument number,
            volume, effect, and effect argument.

        Raises:
            ValueError: If the note number has not been set.
        """
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
            
        if self.Note == None:
            raise ValueError("Note CANNOT be NONE")
            
        return "%s %s %s %s%s" % (self.note_num_as_str(self.Note),
                                 instrument,
                                 volume,
                                 effect,
                                 effectarg
                                )
        
    
