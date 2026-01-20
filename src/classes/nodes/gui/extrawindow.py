# Import inherited
from classes.nodes.gui.canvasitem import *

# Variables
window_transform = {
    "position": [0,0],
    "tsize":    [320,320],
    "scale":    [1,1],
    "scroll":   [0,0],

    "rotation": 0,
    "alpha":    255,
    "anchor":   "top left",
    "visible":  True,
    "skew":     0
}

# Classes
class ExtraWindow(CanvasItem):
    """
    A Window Node.
    
    This Node will create a new Window with its own viewport. You can
    get this window by using `engine.display.get_window(node.window_id)`
    or by using `node` itself.

    XXX not implemented
    """
    _iswindoworviewportlikeobject = True

    def __init__(self, properties={}, parent=None, children=None):
        super().__init__(properties, parent, children)

        self.window_id = engine.display._create_window_entry()