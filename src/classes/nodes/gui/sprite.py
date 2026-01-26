# Import libraries
import pyglet as pg
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Sprite(CanvasItem):
    """
    A 2D Sprite.
    
    XXX
    """
    _can_check_layer = True
    _isblittable     = True

    @export("root://_assets/error.png","str","file_path/img")
    def image_path(self):
        """Filepath of the attached Image. Setting this value loads and sets the imagepath as the Sprite's image."""
        return self._imagepath
    @image_path.setter
    def image_path(self, value):
        if not value: return
        self._imagepath = value
        self.image      = engine.loader.load(value)
    
    def __init__(self, properties={}, parent=None):
        self._imagepath = "root://_assets/error.png"
        super().__init__(properties, parent)
    
    def update(self):
        super().update()
        self.draw(self.image)