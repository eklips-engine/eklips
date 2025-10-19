## Import inherited
from classes.node.gui.canvasitem import CanvasItem

## Import engine singleton and others
import pyglet as pg
import classes.Singleton as engine
from classes import Resources

class Progressbar(CanvasItem):
    """
    ## A Canvas Node to render a Progressbar.
     
    Self-explanatory.
    """
     
    node_base_data = {
        "prop":   {
            "transform": {
                "scale":  [100,25],
                "pos":    [0,0],
                "anchor": "top left",
                "layer":  0,
                "alpha":  1,
                "scroll": [0, 0],
                "rot":    0
            },

            "visible": True,

            "minimum": 0,
            "maximum": 100,
            "value":   50
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
        self.barbatch  = pg.graphics.Batch()
        self.barfbatch = pg.graphics.Batch()
        
    def draw(self):
        if self.visible:
            size          = self._draw_onto_screen(self.scale_x * (self.properties["value"] / abs(self.properties["maximum"] - self.properties["minimum"])))
            self.w,self.h = size
    
    def _draw_onto_screen(self, width):
        img_size = engine.thm.draw_marginable_thing("progressbar", self.runtime_data["rendererpos"], self.scale, self.window_id, self.anchor, self.layer, batch=self.barbatch)
        pb       = engine.thm.draw_marginable_thing("progrfill", self.runtime_data["rendererpos"], [width, self.scale_y], self.window_id, self.anchor, self.layer, batch=self.barfbatch)

        lw, lh, l = self.screen.render(
            f"{round(self.properties['value']/self.properties['maximum']*100)}%",
            [
                self.runtime_data["rendererpos"][0],
                self.runtime_data["rendererpos"][1]
            ],                     
            anchor     = self.anchor,              
            layer      = self.layer,       
            color      = self.properties.get("txcolor", [255,255,255]),
            return_obj = True,
            batchxt    = self.barfbatch
        )
        l.x = self.runtime_data["rendererpos"][0] + (self.scale_x/2 - lw/2)

        return img_size

    def update(self, delta):
        super().update(delta)
        if self.properties["value"] > self.properties["maximum"]:
            self.properties["value"] = self.properties["maximum"]
        self.draw()    
    
    def _free(self):
        return super()._free()