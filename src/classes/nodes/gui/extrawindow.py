# Import inherited
from classes.nodes.gui.canvasitem import *
from classes.ui                   import *

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
class ExtraWindow(CanvasItem, Color):
    """
    A Window Node.
    
    This Node will create a new Window with its own viewport. You can
    get this window by using `engine.display.get_window(node.window_id)`
    or by using `node._window`.
    
    Definitely wouldn't recommend giving it any CanvasItem-related children
    if the Window is initialized as invisible, as the engine crashes since
    the `ExtraWindow` object has its own WindowID but no Window to go along
    with it to save resources.. and stuff.. 
    """
    _isdisplayobject = True
    _isblittable     = True

    def __init__(self, properties={}, parent=None):
        ## Setup CanvasItem
        self._icon     = engine.icon
        self._iconpath = engine.game.win.icofile
        self._title    = DEFAULT_NAME
        super().__init__(properties, parent)

        ## Setup BG color
        Color.__init__(self)

        ## Claim an empty slot for use
        self._drawing_wid        = engine.display._add_window_entry()
        self._window : EklWindow = None
    
    @export([255,255,255],"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the Window's main viewport. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : list[int]):
        self.rgb = rgb
    
    @export(None,"str","file_path/img")
    def icon_path(self):
        """Filepath of the attached Icon. Setting this value loads and sets the iconpath as the Window's icon."""
        return self._iconpath
    @icon_path.setter
    def icon_path(self, value):
        if not value: return
        self._iconpath = value
        self.icon      = engine.loader.load(value)
    
    @property
    def icon(self): return self._icon
    @icon.setter
    def icon(self, value):
        self._icon = value
        if self._window:
            self._window.set_icon(value)
    
    @export(DEFAULT_NAME,"list","color")
    def title(self) -> str: return self._title
    @title.setter
    def title(self, val):
        self._title = val
        if self._window:
            self._window.set_caption(val)
    
    def _set_alpha(self, deg):
        # Any desktop environment does not have support for opacity, unless i manage the window frame and shit
        # myself. Which i am NOT doing.
        return
    def _set_rot(self, deg):
        # Unless you're FlyTech, Microsoft Windows does not have support for rotating windows
        return
    def _set_scale(self, x, y):
        # Unless there's some way to magically set the user's DPI scale on one window in particular,
        # this shit is not happening, unless i manage the window frame and shit myself. Which i am NOT doing.
        return
    def _update_color(self, r, g, b, a):
        if not self._window:
            return
        self._window.viewports[MAIN_VIEWPORT].set_background(r,g,b,a)
    
    def _make_new_item(self):
        if self._window:
            return
        if not self.visible:
            return
        
        ## Make Window
        engine.display.add_window(
            name = self.title,
            size = self.tsize,

            viewport_flags = [VIEWPORT_EQUAL_WINDOW],
            viewport_size  = self.tsize,
            viewport_color = self.color,
            
            icon = self.icon,

            resizable    = True,
            minimum_size = None,
            maximum_size = None,

            visible    = self.visible,
            fpsvisible = False,

            wid = self.window_id
        )

        ## Get Window
        self._window          = engine.display.get_window(self.window_id)
        self._window.on_close = self._hookonclose
    
    def _hookonclose(self):
        if self._window.closed:
            return
        self._window.close()
        self._window                           = None
        engine.display.windows[self.window_id] = None
    
    def _remove_item(self):
        if not self._window:
            return
        self._hookonclose()
    
    def _set_visible(self, val):
        if val:
            self._make_new_item()
        else:
            self._remove_item()