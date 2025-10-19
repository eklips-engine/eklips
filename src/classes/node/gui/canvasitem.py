## Import inherited
from classes.node.node import Node

## Import engine singleton and others
import pyglet as pg
import classes.Singleton as engine
from classes.Constants   import *
from classes.Convenience import *

## Node
class CanvasItem(Node, Transform):
    """
    ## A Canvas Node.
    
    This is a Node that has properties for transformation, and is meant for rendering items in the window.
    This has no effect by Cameras, which makes it good for rendering UI elements. Which is its purpose.
    For Nodes in a 2D world, use Node2D.

    This has relativity only on the position.
    """
    node_base_data = {
        "prop":   {
            "transform": {
                "scale":  [1,1], #
                "pos":    [0,0], #
                "anchor": "top left",
                "layer":  0, #
                "alpha":  1, #
                "scroll": [0, 0], #
                "rot":    0 #
            },
            "visible": True, #
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
        
        Transform.__init__(self)
        self._change_transform()

        self.clicked                     = False
        self.holding                     = False
        self.sprite                      = pg.sprite.Sprite(engine.interface.boilerimg)

        self.runtime_data["rendererpos"] = self.properties["transform"]["pos"][:]
        self.runtime_data["relativepos"] = self.properties["transform"]["pos"][:]

    def _change_transform(self):
        self.anchor                = self.properties["transform"]["anchor"]
        self.x,       self.y       = self.properties["transform"]["pos"]
        self.scale_x, self.scale_y = self.properties["transform"]["scale"]
        self.visible               = self.properties["visible"]
        self.layer                 = self.properties["transform"]["layer"]
        self.scroll                = self.properties["transform"]["scroll"]
        self.rotation              = self.properties["transform"]["rot"]
        self.alpha                 = self.properties["transform"]["alpha"]
        self.anchor                = self.properties["transform"]["anchor"]

    def get_relative_pos(self):
        my_pos     = self.pos
        parent_pos = [0, 0]
        if self.parent and hasattr(self.parent, "get_relative_pos"):
            parent_pos = self.parent.get_relative_pos()[0]
            return [my_pos[0] + parent_pos[0], my_pos[1] + parent_pos[1]], parent_pos
        return my_pos[:], parent_pos
    
    def get_relative_anchor(self):
        if self.parent and hasattr(self.parent, "anchor"):
            return self.parent.anchor
        return self.anchor
    
    def draw(self):
        if self.image and self.properties["visible"]:
            self.w,self.h         = self.image.width,self.image.height
            self._draw_onto_screen(self.image)
    
    def get_if_mouse_hovering(self) -> bool:
        mpos = engine.mpos
        x,y  = self.screen.get_anchor(
            [self.x, self.y],
            self.window_id,
            self.anchor,
            self.w,
            self.h,
            True,
            self.rotation,
            True
        )
        is_it = (
            mpos[0] < x  + self.w and
            mpos[0] + 20 > x      and
            mpos[1] < y  + self.h and
            mpos[1] + 20 > y
        )
        return is_it
    
    def _draw_onto_screen(self, img):
        return self.screen.blit(
            img,                                   
            self.runtime_data["rendererpos"],             
            anchor  = self.anchor,
            scale   = self.scale,
            layer   = self.layer,
            rot     = self.rotation,
            opacity = self.alpha,
            scroll  = self.scroll,
            sprite  = self.sprite
        )
        
    def update(self, delta):
        self.anchor                      = self.anchor
        rel_pos, parent_pos              = self.get_relative_pos()
        self.clicked                     = False
        self.holding                     = False

        if self.get_if_mouse_hovering():
            self.call("_hover")
            if engine.mpressed[0]:
                self.holding = True
                self.call("_pressed_down")
            if MOUSEUP in engine.events:
                self.clicked = True
                self.call("_clicked")

        # World-space relative position
        self.runtime_data["relativepos"] = rel_pos
        self.runtime_data["rendererpos"] = rel_pos
        
        super().update(delta)