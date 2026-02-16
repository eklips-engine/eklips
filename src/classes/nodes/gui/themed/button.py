# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Button(CanvasItem):
    """
    A Button.
    
    XXX
    """
    
    def __init__(self, properties={}, parent=None):
        self._tiles = {}
        super().__init__(properties, parent)

        self.batch_id = self.viewport.add_batch()