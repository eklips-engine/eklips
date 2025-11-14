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
    base_properties  = {
        "name":      "ColorRect",
        "transform": base_transform,
        "color":     [0,0,0],
        "script":    None
    }

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        self.color = self.get("color", [0,0,0])
        self._make_new_sprite()
    
    @property
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
        rw, rh = round(w),round(h)
        self.image = pg.image.ImageData(rw,rh,'RGB',bytes(self.color*rw*rh))
    
    def update(self):
        super().update()
        self.draw(self.image)