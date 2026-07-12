

class ITenvelope_node(object):
    """Represents a control point in an IT envelope.

    Each node defines an output value and the number of ticks it remains
    active before the next envelope point.
    """

    def __init__(self):
        """Initialize the node with default values."""
        self.y_val = 0
        self.tick = 0
        
    def __len__(self):
        """Return the serialized size of the node in bytes."""
        return 3
    
