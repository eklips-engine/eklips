## Import inherited
from classes.node.twod.node2d import Node2D

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class Sprite2D(Node2D):
    """
    ## A 2D Node to display an image.
     
    Self-explanatory.
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
            "visible":  True,
            "sprite":   "res://media/bg.png"
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
        asset      = self.resourceman.load(self.properties["sprite"])
        self.image = asset
    
    def update(self, delta):
        super().update(delta)
        self.draw()