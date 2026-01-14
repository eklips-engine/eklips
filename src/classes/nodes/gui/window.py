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
class Window(CanvasItem):
    """
    A Window Node.
    
    This Node will create a new Window with its own viewport. You can
    get this window by using `engine.display.get_window(wid)` or by 
    using `window._window`.

    XXX not implemented
    """