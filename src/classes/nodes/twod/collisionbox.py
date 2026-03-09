# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.colorrect import *

# Classes
class CollisionBox(CanvasItem):
    """
    A rectangle with Collision abilities.

    This Node uses the `CollisionManager` class, and
    as soon as it is initialized, it adds itself to the
    list.

    This Node uses basic AABB collision cause i'm too
    bad at programming to even bother making collision
    for any other shape than rectangles
    """
    _supports_tsize = True

    def __init__(self, properties={}, parent=None):
        super().__init__(properties, parent)
        self.world  = engine.scene._collisionman
        self._shape = pygame.Rect((0,0,0,0))
        self.rid    = self.world.add(self._shape)
    
    def _free(self):
        self.world.delete(self.rid)
        super()._free()
    
    def colliderect(self, shape):
        return self._shape.colliderect(shape)
    
    def _set_pos(self, x, y):
        self._shape.x = x
        self._shape.y = y
    def _set_size(self, w, h):
        self._shape.w = w
        self._shape.h = h
    def _set_rot(self, deg):
        # pygame.Rect does not support rotation
        return