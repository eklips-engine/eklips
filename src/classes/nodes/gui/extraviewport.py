# Import inherited
from classes.nodes.gui.canvasitem import *
from classes.ui                   import *

# Variables
viewport_transform = {
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
class ExtraViewport(CanvasItem, Color, Viewport): # Group project looking ass node 😭
    """
    A Viewport Node.
    
    This Node will create a new Viewport. You can get this Viewport
    by using `engine.display.get_viewport(node.viewport_id, wid)`
    or by using `node` itself.
    """
    _isdisplayobject = True

    ## CanvasItem stuff
    def _get_viewport(self):
        return self
    
    ## Exports
    @export([255,255,255],"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the Viewport. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : list[int]):
        self.rgb = rgb
    
    ## Transform related
    def _set_alpha(self, deg):
        # Viewport objects don't have an alpha property yet
        return
    def _set_rot(self, deg):
        # Viewport objects cannot rotate yet
        return
    def _set_scale(self, x, y):
        # No effect
        return
    def _update_color(self, r, g, b, a):
        self.set_background(r,g,b,a)
    
    ## Init
    def __init__(self, properties={}, parent=None):
        ## Setup CanvasItem
        super().__init__(properties, parent)

        ## Setup BG color
        Color.__init__(self)

        ## Setup Viewport
        # Get window and VID
        window            = engine.display.get_window(self.window_id)
        self._drawing_vid = len(window.viewports)

        # Init Viewport
        Viewport.__init__(self, self.viewport_id, window, [])

        # Add a batch and add viewport to window
        self.add_batch()
        window.viewports[self.viewport_id] = self
    
    ## Rewrites
    def _update_relativity(self):
        if self.parent and self.parent.get("_iscitem", False):
            self._offset_x, self._offset_y = self.parent.into_screen_coords(self.window.size, False)
    
    def draw(self):
        """Draw the Viewport. This should be called automatically by the `EklWindow`."""
        Viewport.draw(self)
    
    def get_if_mouse_hovering(self):
        mpos   = engine.mouse.pos
        x,y    = self.into_screen_coords()
        is_it  = (
            mpos[0] >= x          and
            mpos[0] <= x + self.w and
            mpos[1] >= y          and
            mpos[1] <= y + self.h
        )
        
        return is_it
    def _remove_item(self):
        self.close()