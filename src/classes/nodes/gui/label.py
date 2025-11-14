# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.td.node2d import *

# Classes
class Label(CanvasItem):
    """
    ## A 2D Sprite.
    
    XXX
    """
    _can_check_layer       = True
    sprite : pg.text.Label = None
    base_properties        = {
        "name":      "Label",
        "transform": base_transform,
        "sprite":    None,
        "script":    None
    }

    @property
    def text(self) -> str: return self.sprite.text
    @text.setter
    def text(self, value): self.sprite.text = value

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        self._make_new_sprite()
    
    def update(self):
        super().update()
        self.draw()
    
    def draw(self):
        """Draw the label. This is usually called automatically."""
        if len(self.text.split()):
            self.w, self.h = self._draw()
    
    def _draw(self):
        return engine.display.blit_label(
            transform = self,
            window_id = self.window_id,
            label     = self.sprite,
            group     = self._canvas_layer
        )
    
    def _remove_sprite(self):
        if not self.sprite:
            return
        self.sprite.visible = False
    def _make_new_sprite(self):
        if self.sprite:
            self._remove_sprite()
        viewport = self._get_viewport()
        self.sprite, self._sprite_id = viewport._allocate_label(self.batch_id)