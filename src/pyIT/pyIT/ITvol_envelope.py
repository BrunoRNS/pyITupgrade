from .ITenvelope import ITenvelope


class ITvol_envelope(ITenvelope):
    """Represent the volume envelope of an IT instrument.

    This class specializes the generic envelope structure for volume-related
    control points and loop/sustain settings.
    """

    def __init__(self) -> None:
        """Initialize a volume envelope with the default base-envelope state."""
        super().__init__()

