from .ITenvelope import ITenvelope


class ITpitch_envelope(ITenvelope):
    """Represent the pitch envelope of an IT instrument.

    In addition to the standard envelope behavior, this class supports a
    dedicated filter flag that can alter pitch/filter semantics.
    """

    def __init__(self) -> None:
        """Initialize the pitch envelope and the optional filter flag."""
        super().__init__()
        self.IsFilter = False

    def extraFlags(self) -> int:
        """Return any extra envelope flag bits for the pitch envelope.

        Returns:
            ``0x80`` when filter mode is active, otherwise ``0``.
        """
        if self.IsFilter:
            return 0x80
        return 0

    def setFlags(self, flags: int) -> None:
        """Apply encoded envelope flags and synchronize the filter state.

        Args:
            flags: Packed flag bits read from the serialized envelope.
        """
        super().setFlags(flags)
        self.IsFilter = bool(flags & 0x80)
    
    
