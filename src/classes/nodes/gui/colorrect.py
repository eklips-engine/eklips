# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class ColorRect(CanvasItem, Color):
    """
    A single-color rectangle on the screen.
    
    XXX
    """
    _can_check_layer = True

    def __init__(self, properties={}, parent=None, children=None):
        Color.__init__(self, 255,255,255)

        super().__init__(properties, parent, children)
        self._make_new_sprite()
    
    @export([255,255,255],"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the Label. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : list[int]):
        self.rgb = rgb
    def _update_color(self, r, g, b, a):
        self._refresh_image()
    
    def _refresh_image(self):
        self._set_size(self.w,self.h)
    def _set_size(self,w,h):
        # Make the size be valid
        rw, rh         = round(w),round(h)
        if rw == 0: rw = 1
        if rh == 0: rh = 1

        # Make the image
        self.image = pg.image.ImageData(rw,rh,'RGB',bytes(self.rgb[:3]*rw*rh))
    
    def update(self):
        super().update()
        self.draw(self.image)