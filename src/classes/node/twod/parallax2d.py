## Import inherited
from classes.node.twod.sprite2d import Sprite2D

## Import engine singleton singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class Parallax2D(Sprite2D):
    """
    ## A 2D Sprite Node.. to scroll the image at a provided speed..
     
    There is seriously no way you need help with this
    """

    node_base_data = {
        "prop":   {
            "transform": {
                "scale":  [1,1],
                "pos":    [0,0],
                "anchor": "top left",
                "layer":  0,
                "alpha":  1,
                "scroll": [0, 0],
                "rot":    0
            },
            "visible":      True,
            "sprite":       "res://media/bg.png",
            "scroll_speed": 5,
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }
    
    node_signals = [
        "_hover",
        "_pressed_down",
        "_clicked",
        "_reached_end"
    ]
    
    def __init__(self, data=node_base_data, parent=None):
        super().__init__(data,parent)
    
    def update(self, delta):
        super().update(delta)

        self.scroll[0]    -= self.properties["scroll_speed"]
        if self.scroll[0]  < (-self.image.get().width) + self.properties["scroll_speed"]:
            self.scroll[0] = -(self.properties["scroll_speed"])
            self.call_signal("_reached_end")