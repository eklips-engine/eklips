# Import libraries
import pyglet as pg
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Camera(CanvasItem):
    """
    A 2D Camera.
    
    XXX
    """
    _can_check_layer = True

    @export(1, "int/float", "slider")
    def zoom(self):
        return self.viewport.cam.zoom
    @zoom.setter
    def zoom(self, value):
        self.viewport.cam.zoom = value

    def _set_pos(self, x, y):
        self.viewport.cam.x = x
        self.viewport.cam.y = y