# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class ColorRect(CanvasItem):
    """
    ## A single-color rectangle on the screen.
    
    XXX
    """
    _can_check_layer = True
    _color           = [0,0,0]

    def __init__(self, properties={}, parent=None, children=None):
        super().__init__(properties, parent, children)
        self._make_new_sprite()
    
    @export([0,0,0],"list","color")
    def color(self) -> list[int]:
        """RGB color of the ColorRect."""
        return self._color
    @color.setter
    def color(self, rgb : list[int]):
        self._color = rgb
        self._refresh_image()
    
    def _refresh_image(self):
        self._set_size(self.w,self.h)
    def _set_size(self,w,h):
        # Make the size be valid
        rw, rh         = round(w),round(h)
        if rw == 0: rw = 1
        if rh == 0: rh = 1

        # Make the image
        self.image = pg.image.ImageData(rw,rh,'RGB',bytes(self.color*rw*rh))
        
        # Set the Sprite's image
        self.sprite.image = self.image
    
    def update(self):
        super().update()
        self.draw(self.image)