## Import inherited
from classes.node.gui.canvasitem import CanvasItem

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class Node2D(CanvasItem):
    """
    ## A 2D Node.
    
    This is basically the same as a CanvasItem, but meant for gameplay purposes, because it follows the camera.
    All nodes that are meant in a 2D space (Camera2D, Sprite2D..) are inherited from this Node.
    """
    
    def update(self, delta):
        global camera_pos
        rel_pos, parent_pos              = self.get_relative_pos()

        # World-space relative position
        self.runtime_data["relativepos"] = rel_pos
        self.runtime_data["rendererpos"] = [
            rel_pos[0] + engine.cam_pos[0],
            rel_pos[1] + engine.cam_pos[1]
        ]
        super().update(delta)