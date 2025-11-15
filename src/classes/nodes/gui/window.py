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
        self._window = None
        super().__init__(properties, parent)
        
    def popup(self):
        """
        Create the window.
        """
        
        self.wid           = engine.display.add_window(
            name           = self.title,
            size           = self.tsize,
            minimum_size   = self.tsize,
            maximum_size   = None,
            viewport_color = self.color,
            resizable      = self.get("resizable"),
            icon           = engine.icon
        )

        self._window          = engine.display.get_window(self.wid)
        self._window.on_draw  = self.update
        self._window.on_close = self._free
        self._drawing_wid     = self.wid
    
    @property
    def title(self): return self.get("title", DEFAULT_NAME)
    @property
    def color(self): return self.get("color", [0,0,0])
    
    @title.setter
    def title(self, name):
        self.set("title", name)
        if self._window:
            self._window.set_caption(name)
    
    @color.setter
    def color(self, rgb):
        self.set("color", rgb)
        if self._window:
            self._window.set_caption(rgb)

    def _free(self):
        if self._window:
            self._window.eklips_viewport.close()
            engine.display.close_window(self.wid)
            self._window.closed = True
        super()._free()
    
    def _set_size(self,w,h):
        rw, rh = round(w),round(h)
        if self._window:
            self._window.width  = rw
            self._window.height = rh
    
    def update(self):
        super().update()

        if self._window:
            engine.display.clear_window(self.wid)
            engine.display.flip_window(self.wid)