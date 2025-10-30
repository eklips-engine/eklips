## Import inherited
from classes.node.twod.sprite2d import Sprite2D

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class AnimatedSprite2D(Sprite2D):
    """
    ## A 2D Node to display an animmated image.
     
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
            "sprite":   ["res://media/bg.png"]
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
        self.images      = []
        self.sprite_used = 0          
        for i in self.properties["sprite"]: 
            asset = self.resourceman.load(i)
            self.images.append(asset)       
    
    def draw(self):
        if self.sprite_used in self.images and self.visible:
            img=self.images[self.sprite_used]
            self.w,self.h=img.w,img.h
            return self._draw_onto_screen(img)