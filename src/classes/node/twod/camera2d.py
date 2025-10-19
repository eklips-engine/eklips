## Import inherited
from classes.node.twod.node2d import Node2D

## Import engine singleton and others
import pyglet as pg
from pyglet.math import Mat4, Vec2, Vec3, Vec4
import classes.Singleton as engine

## Node
class Camera2D(Node2D):
    """
    ## A 2D Node to control the Camera in the 2D world.
     
    Self-explanatory. The position of this Node is the position of the camera
    """
    
    def __init__(self, data=Node2D.node_base_data, parent=None):
        super().__init__(data,parent)
        self.target      = None
        self.cam_pos     = [0, 0, 0]
        self.zoom        = 1
        self.rot         = 0
        self.rot_vec     = [0, 1,0] 
        self.old_cam_pos = [-1,1,1]
        self.old_zoom    = -2
    
    def change_view(self):
        engine.cam_pos  = self.cam_pos
        engine.cam_zoom = self.zoom
    
    def follow(self, target_node):
        self.target = target_node
    
    def update(self, delta):
        super().update(delta)
        if not self.target:
            self.cam_pos = [
                self.x,
                self.y,
                self.cam_pos[2]
            ]
        else:
            # FIXME Target doesn't work apparently
            w,h=self.target.w,self.target.h
            self.cam_pos = [
                self.target.x - self.screen.screen.width  // 2 - w // 2,
                self.target.y - self.screen.screen.height // 2 - h // 2,
                self.cam_pos[2]
            ]
        if self.cam_pos != self.old_cam_pos or self.zoom != self.old_zoom:
            self.change_view()
            self.old_cam_pos = self.cam_pos
            self.old_zoom    = self.zoom