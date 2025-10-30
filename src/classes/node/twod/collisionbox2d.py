## Import inherited
from classes.node.twod.area2d import Area2D

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class CollisionBox2D(Area2D):
    """
    ## A rectangular hitbox node.

    This node has a rectangular hitbox, which will stop if collided with any bodies. Useful for things like.. boxes.
    """
    
    def _handle_motion_end(self, bounce_mode):
        if bounce_mode:
            self.motion[1] = -self.motion[1]
        else:
            self.motion = [0,0]
    
    def _handle_bump_x(self, bounce_mode):
        if bounce_mode:
            self.motion[0] = -self.motion[0] + engine.ZDE_FIX / self.weight + engine.ZDE_FIX
        else:
            self.motion[0] = 0
    
    def _handle_bump_y(self, bounce_mode):
        if bounce_mode:
            self.motion[1] = -self.motion[1] + engine.ZDE_FIX / self.weight + engine.ZDE_FIX
        else:
            self.motion[1] = 0