# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.colorrect import *

# Classes
class CollisionBox(ColorRect):
    """
    ## A rectangle with Collision abilities.

    This Node uses the `CollisionManager` class, and
    as soon as it is initialized, it adds itself to the
    list.

    This Node uses basic AABB collision cause i'm too
    bad at programming to even bother making collision
    for any other shape than rectangles
    
    The sole reason it inherits ColorRect is to draw a
    debug hitbox if `engine.debug.shapes_visible` is on.
    """

    def __init__(self, properties={}, parent=None, children=None):
        super().__init__(properties, parent, children)
        self.world = engine.scene._collisionman
        self.rid   = self.world.add(self)
    
    def _free(self):
        self.world.delete(self.rid)
        super()._free()
    
    def draw(self, image):
        if engine.debug.shapes_visible:
            super().draw(image)
    
    def aabb(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)
    
    def _set_pos(self):
        return
    