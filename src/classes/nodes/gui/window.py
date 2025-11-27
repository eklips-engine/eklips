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
    """
    _can_check_layer = False

    def __init__(self, properties={}, parent=None, children=None):
        self._window      = None
        self._color       = [0,0,0]
        self._autopopup   = False
        self._drawing_wid = None
        self._title       = None
        self._resizable   = False
        super().__init__(properties, parent, children)
        
    def _setup_properties(self):
        super()._setup_properties()
        
        if self.auto_popup:
            self.popup()
    
    def _make_window(self):
        self.wid              = engine.display.add_window(
            name              = " ",
            size              = [5,5],
            minimum_size      = [5,5],
            maximum_size      = None,
            viewport_color    = self.color,
            resizable         = self.resizable,
            icon              = engine.icon,
            wid               = AUTOMATICALLY_CREATE,
            visible           = False
        )
        self._window          = engine.display.get_window(self.wid)
        self._drawing_wid     = self.wid
        
    def popup(self):
        """
        Make the window.
        """
        if not self._window or self._window.closed:
            self._make_window()
        self._window.set_size(self.w, self.h)
        self._window.set_caption(self.title)
        self._window.set_visible()
    
    @export(False,"bool","bool")
    def auto_popup(self): return self._autopopup
    @export(True,"bool","bool")
    def resizable(self): return self._resizable
    @export(DEFAULT_NAME,"str","str")
    def title(self): return self._title
    @export([0,0,0],"list","color")
    def color(self): return self._color
    
    @auto_popup.setter
    def auto_popup(self, value): self._autopopup = value
    @title.setter
    def title(self, name):
        self._title = name
        if self._window:
            self._window.set_caption(name)
    
    @color.setter
    def color(self, rgb):
        self._color = rgb
        if self._window:
            self._window.eklips_viewport.set_background(*rgb)
    
    def _set_size(self,w,h):
        rw, rh = round(w),round(h)
        if self._window:
            self._window.width  = rw
            self._window.height = rh
    
    def _get_viewport(self):
        if not self._window:
            return
        return self._window.eklips_viewport
    
    def get_if_mouse_hovering(self):
        """Returns true if the mouse is hovering over self."""
        mpos     = engine.mouse.pos
        viewport = self._get_viewport()
        return False