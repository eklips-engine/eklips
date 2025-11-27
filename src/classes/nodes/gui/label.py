# Import libraries
import pygame, pyglet as pg, json, gc

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Label(CanvasItem):
    """
    ## A Label.
    
    XXX
    """
    _can_check_layer       = True
    sprite : pg.text.Label = None

    @export("Label","str","str")
    def text(self) -> str: return self.sprite.text
    @text.setter
    def text(self, value): self.sprite.text = value

    @export(DEFAULT_FONT_NAME,"str","font")
    def font(self) -> str: return self.sprite.font_name
    @font.setter
    def font(self, value): self.sprite.font_name = value

    @export(DEFAULT_FONT_SIZE,"float/int","float/int")
    def font_size(self) -> float | int: return self.sprite.font_size
    @font_size.setter
    def font_size(self, value):         self.sprite.font_size = value

    def __init__(self, properties={}, parent=None, children=None):
        super().__init__(properties, parent, children)
        self._make_new_sprite()
    
    def update(self):
        super().update()
        self.draw()
    
    def draw(self):
        """Draw the label. This is usually called automatically."""
        self.w, self.h = self._draw()
    
    def _draw(self):
        return engine.display.blit_label(
            text      = self.text,
            transform = self,
            window_id = self._drawing_wid,
            label     = self.sprite,
            font_name = self.font,
            font_size = self.font_size  
        )
    
    def _remove_sprite(self):
        if not self.sprite:
            return
        self.sprite.visible = False
    def _make_new_sprite(self):
        if self.sprite:
            self._remove_sprite()
        viewport = self._get_viewport()
        self.sprite, self._sprite_id = viewport._allocate_label(self._drawing_bid)