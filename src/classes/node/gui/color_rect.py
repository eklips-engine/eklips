## Import inherited
from classes.node.gui.canvasitem import CanvasItem

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine
from classes import resources

## Node
class ColorRect(CanvasItem):
    """
    ## A Canvas Node to render a colored Rectangle.
     
    Self-explanatory.
    """
     
    node_base_data = {
        "prop":   {
            "transform": {
                "scale":  [100,100],
                "pos":    [0,0],
                "anchor": "top left",
                "layer":  0,
                "alpha":  1,
                "scroll": [0, 0],
                "rot":    0
            },
            "visible": True,
            "color":   [128, 128, 128]
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    def __init__(self, data=node_base_data, parent=None):
        super().__init__(data,parent)
        r, g, b = self.properties["color"]
        # RGB for each pixel, repeated for all pixels
        raw_data = bytes([r, g, b])
        self.image = resources.Image(
            {
                "prop":   {},
                "data":   {
                    "object": pg.image.ImageData(
                        1,
                        1,
                        'RGB',
                        raw_data
                    ),
                    "path":   f"{r}{g}{b}{self.scale}.mm"
                },
                "meta":   {
                    "kind": "Resource",
                    "name": "Image"
                },
                "script": None
            }
        )

    def update(self, delta):
        super().update(delta)
        self.draw()