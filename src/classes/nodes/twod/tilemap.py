# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Tilemap(CanvasItem):
    """
    A grid of tiles placed together to make a map.

    XXX
    """

    @export({}, "dict", "tiles")
    def tiles(self):
        return self._tiles
    @tiles.setter
    def tiles(self, value):
        self._tiles = {}
        for i in value: # TileID, GridX, GridY
            self.place_tile(*i)
    
    def __init__(self, properties={}, parent=None, children=None):
        self._tiles = {}
        super().__init__(properties, parent, children)

        self.batch_id = self._get_viewport().add_batch()
        self.batch    = self._get_viewport().batches[self.batch_id]