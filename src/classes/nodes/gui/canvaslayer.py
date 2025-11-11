# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class CanvasLayer(CanvasItem):
    """
    ## A Canvas Layer.

    This Node's sole purpose is to provide a layer for child CanvasItem Nodes to draw in.
    A Camera only has effect on one CanvasLayer, so to make an UI element not follow the camera, make a seperate CanvasLayer node and make that its parent.
    """
    _can_check_layer = False
    base_properties  = {
        "name":      "CanvasLayer",
        "layer":     0,
        "transform": base_transform,
        "script":    None
    }
    _camera_layer    = None
    _is_layer        = True

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        self.layer = pg.graphics.Group(order=properties["layer"])
    
    def _free(self):
        del self.layer
        super()._free()