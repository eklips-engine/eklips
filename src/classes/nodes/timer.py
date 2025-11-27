# Import inherited
from classes.nodes.node import *

# Classes
class Timer(Node):
    def __init__(
            self,
            properties : dict                   = {}, 
            parent     : NodeMixin       | None = None,
            children   : list[NodeMixin] | None = None
        ):
        super().__init__(properties, parent, children)
        self._time = 0
