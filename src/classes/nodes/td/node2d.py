# Import libraries
import pygame, pyglet as pg, json, gc

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Node2D(CanvasItem):
    """
    ## A 2D Node.
    
    XXX
    """

    _can_check_layer = True
    base_properties  = {
        "name":      "Node2D",
        "transform": base_transform,
        "script":    None
    }

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
    
    def update(self):
        super().update()