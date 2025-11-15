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
    ## A Window Node.
    
    This Node will create a new Window with its own viewport. You can
    get this window by using `engine.display.get_window(wid)` or by 
    using `window._window`.
    
    As soon as the Window is made, the other windows are frozen and
    cannot be used untill this Window is closed.
    """
    _can_check_layer = False
    base_properties  = {
        "name":      "Window",
        "transform": window_transform,
        "color":     [35,35,50],
        "resizable": True,
        "script":    None
    }
    wid : int        = -1

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        
        # Create the window.
        self.wid           = engine.display.add_window(
            name           = self.get("name"),
            size           = self.tsize,
            minimum_size   = self.tsize,
            maximum_size   = None,
            viewport_color = self.get("color"),
            resizable      = self.get("resizable"),
            icon           = engine.icon
        )

        self._window          = engine.display.get_window(self.wid)
        self._window.on_draw  = self.update
        self._window.on_close = self._free
    
    def _free(self):
        self._window.eklips_viewport.close()
        engine.display.close_window(self.wid)
        self._window.closed = True
        super()._free()
    
    def update(self):
        super().update()
        engine.display.clear_window(self.wid)

        engine.display.flip_window(self.wid)