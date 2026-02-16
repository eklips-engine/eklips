## Import libraries
import pyglet as pg
from classes import ui
from functools import reduce
import operator

## Import inherited
from classes.nodes.gui.canvasitem import *

class Treeview(CanvasItem):
    ## Init
    def __init__(self, properties={}, parent=None):
        self._items = {}
        super().__init__(properties, parent)
    
    ## Export
    @export({}, "dict", "treeview/children")
    def items(self) -> dict:
        return self._items
    @items.setter
    def items(self, val):
        self._items = val # Surely the editor will know what to do
    
    ## Update
    def update(self):
        # Draw Treeview
        for item in self.items:
            ...

        # Update CanvasItem
        super().update()

    ## Item management
    def add_item(self, path, name):
        try:
            keys = path.split('/')
            d = self._items
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = [name, False]

            return 0
        except:
            return 1
    def open(self, path):
        try:
            keys = path.split('/')
            d    = self._items
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]][1] = True

            return 0
        except:
            return 1
    def close(self, path):
        try:
            keys = path.split('/')
            d    = self._items
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]][1] = False

            return 0
        except:
            return 1