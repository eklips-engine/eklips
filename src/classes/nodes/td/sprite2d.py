# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.td.node2d import *

# Classes
class Sprite2D(Node2D):
    """
    ## A 2D Sprite.
    
    XXX
    """
    _can_check_layer = True
    base_properties  = {
        "name":      "Sprite2D",
        "transform": base_transform,
        "sprite":    None,
        "script":    None
    }

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        if properties["sprite"]:
            self.image = engine.loader.load(properties["sprite"])
        self._make_new_sprite()
    
    def update(self):
        super().update()
        self.draw(self.image)