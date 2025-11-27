# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Sprite(CanvasItem):
    """
    ## A 2D Sprite.
    
    XXX
    """
    _can_check_layer = True

    @export(None,"str","file_path/image")
    def image_path(self): return self._imagepath
    @image_path.setter
    def image_path(self, value):
        if not value: return
        self._imagepath = value
        self.image      = engine.loader.load(value)
        if self.sprite:
            self.sprite.image = self.image
    
    def __init__(self, properties={}, parent=None, children=None):
        self._imagepath = None

        super().__init__(properties, parent, children)
        self._make_new_sprite()
    
    def update(self):
        super().update()
        self.draw(self.image)