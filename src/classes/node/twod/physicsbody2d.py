## Import inherited
from classes.node.twod.node2d import Node2D

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class PhysicsBody2D(Node2D):
    node_base_data = {
        "prop":   {
            "transform": {
                "size":   [100,100],
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

    def _phys_init(self):
        self.should_stop = True
        self._onf        = False
        self._onw        = False
        self.weight      = 1
        self.motion      = [0, 0]

    def if_on_floor(self): return self._onf 
    def if_on_wall(self):  return self._onw
    def _physics_update(self, nearby, collided, bounce_mode = False):
        # Most basic of basic physics.
        self._onf = False
        self._onw = False

        for node in collided:
            if self.colliderect(node) and node.get_class() == "Area2D":
                # You little shit
                if self.y + self.h <= node.y:
                    self._onf = True
                    # Ow
                    self._handle_bump_y(bounce_mode)
                elif (self.x + self.w > node.x and
                      self.x < node.x + node.w):
                    self._onw = True
                    # Ow
                    self._handle_bump_x(bounce_mode)
        
        self._handle_motion(bounce_mode)
    
    def _handle_motion(self, bounce_mode=False):
        self.x += self.motion[0]
        self.y += self.motion[1]
        
        self._handle_motion_end(bounce_mode)
    
    def _handle_motion_end(self, bounce_mode): # visual
        pass
    
    def _handle_bump_x(self, bounce_mode): # visual
        pass
    
    def _handle_bump_y(self, bounce_mode): # visual
        pass