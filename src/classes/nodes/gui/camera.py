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
        return self._get_viewport().cam.zoom
    @zoom.setter
    def zoom(self, value):
        viewport         = self._get_viewport()
        viewport.cam.zoom = value

    def _set_pos(self, x, y):
        viewport      = self._get_viewport()
        viewport.cam.x = x
        viewport.cam.y = y