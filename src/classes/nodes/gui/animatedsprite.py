# Import libraries
import pyglet as pg
from classes import ui

# Import inherited
from classes.nodes.gui.sprite import *

# Classes
class AnimatedSprite(CanvasItem):
    """
    A 2D Sprite.
    
    XXX
    """
    _can_check_layer = True
    _isblittable     = True

    @export(["root://_assets/error.png"],"list","file_paths/img")
    def image_paths(self):
        """List of filepaths of the attached Images.
        
        Add a sprite by using `add_sprite_from_animation()`,
        and remove one using `remove_sprite_from_animation()`.

        .. note:: `remove_sprite_from_animation()` and `_remove_item` are not the same."""
        return self._images.values()
    @image_paths.setter
    def image_paths(self, paths : list):
        self._images = {}
        for path in paths:
            self.add_sprite_from_animation(path)
    
    def add_sprite_from_animation(self, image_path):
        """Add a Sprite from AnimatedSprite. Returns ID in `self._images`"""
        img_id               = len(self._images)
        self._images[img_id] = engine.loader.load(image_path)
        return img_id
    
    def remove_sprite_from_animation(self, img_id):
        self._images.pop(img_id)
    
    def __init__(self, properties={}, parent=None):
        self._imagesid  = 0
        self._images    = {}

        super().__init__(properties, parent)
    
    def step(self):
        self._imagesid    += 1
        if self._imagesid  < 0:
            self._imagesid = len(self._images) - 1
        if self._imagesid  > len(self._images) - 1:
            self._imagesid = 0

    def update(self):
        super().update()
        if self._imagesid in self._images:
            self.image = self._images[self._imagesid]
            self.draw()