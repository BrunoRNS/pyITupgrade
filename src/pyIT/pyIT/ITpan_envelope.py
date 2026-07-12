from typing import Any, Dict, List

from .ITenvelope import ITenvelope

class ITpan_envelope(ITenvelope):
    """Represent the pan envelope of an IT instrument.

    This class inherits the generic envelope behavior and is specialized for
    pan control data.
    """

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]):
        """Initialize the pan envelope and delegate to the base envelope.

        Args:
            *args: Positional arguments forwarded to :class:`ITenvelope`.
            **kwargs: Keyword arguments forwarded to :class:`ITenvelope`.
        """
        super().__init__(*args, **kwargs)
    
