## Import inherited
from classes.nodes.gui.canvasitem import *
from classes.ui                   import *

## Classes
class ExtraViewport(CanvasItem, Viewport):
    """
    A Viewport Node.
    
    This Node will create a new Viewport. You can get this Viewport
    by using `engine.display.get_viewport(node.viewport_id, wid)`
    or by using `node` itself.
    """

    ## CanvasItem stuff
    def _get_viewport(self):
        return self
    
    ## Exports
    @export(WHITE,"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the Viewport. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : list[int]):
        self.set_background(*rgb)
    
    ## Init
    def __init__(self, properties={}, parent=None):
        ## Setup CanvasItem
        super().__init__(properties, parent)

        ## Setup Viewport
        # Get window and VID
        window            = engine.display.get_window(self.window_id)
        self._drawing_vid = len(window.viewports)

        ## Init Viewport
        if self.parent:
            vppr = window.viewports[self.parent.get("_drawing_vid", MAIN_VIEWPORT)]
        else:
            vppr = window.viewports[MAIN_VIEWPORT]
        Viewport.__init__(self, self.viewport_id, window, [], vppr)

        # Add a batch and add viewport to window
        self.add_batch()
        window.viewports[self.viewport_id] = self
    
    ## Transform related
    def _set_anchors(self):
        Viewport._set_anchors(self)
    def _set_size(self, w, h):
        Viewport._set_size(self, w,h)
    def _set_scale(self, x, y):
        Viewport._set_scale(self, x, y)
    def _set_rot(self, deg):
        Viewport._set_rot(self, deg)
    def _set_visible(self, val):
        Viewport._set_visible(self, val)
    def _set_alpha(self, deg):
        Viewport._set_alpha(self, deg)
    
    ## Item managing
    def _make_new_item(self):
        self._make_framebuffer()
    def _remove_item(self):
        self.close()
    
    ## Draw
    def draw(self):
        """Draw the Viewport. This should be called automatically by the `EklWindow`."""
        Viewport.draw(self)
    
    ## Convenience functions for user
    def get_if_mouse_hovering(self) -> bool:
        """Returns true if the mouse is hovering over self."""
        return engine.mouse.collides_ui_aabb(self, ctx_a=(
            self, self._isc_get_parent_property(), 1
        ), ctx_b=(self._get_window(), None, 1))
        return engine.mouse.collides_ui_aabb(self, ctx_a=(self, None), ctx_b=(self._get_window(), None))