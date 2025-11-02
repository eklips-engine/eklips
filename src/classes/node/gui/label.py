## Import inherited
from classes.node.gui.canvasitem import CanvasItem

## Import engine singleton singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class Label(CanvasItem):
    """
    ## A Canvas Node to render text.
     
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
            "text":    "",
            "color":   [255,255,255]
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    def draw(self):
        if self.visible:
            img           = self._draw_onto_screen(self.properties["text"])
            self.w,self.h = img.w, img.h
        
    def _draw_onto_screen(self, text):
        return self.screen.render(
            text      = text,
            pos       = self.runtime_data["rendererpos"],
 
            anchor    = self.anchor,
            layer     = self.layer,
            screen_id = self.window_id,
            size      = self.properties["font_size"],
            rotation  = self.rotation,
            alpha     = self.alpha,
            color     = self.properties["color"]
        )
    
    def update(self, delta):
        super().update(delta)
        self.draw()