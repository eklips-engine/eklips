## Import all the libraries necessary and engine singleton
import pyglet as pg
from tkinter.messagebox import *
from classes.Object import Object
from anytree import NodeMixin
import classes.Singleton as engine

## Node
class Node(Object, NodeMixin):
    """
    ## An empty Node.

    Nodes are the building block of Eklips (well, Eklips 4+ atleast). Every Node is inherited off this node class.
    A tree of Nodes make a Scene, A scene is stored as `engine.scene`.
    
    You can make a script have an `_onready(self)` function. This will only run when a Node is fully loaded.
    You can make a script have an `_process(self, delta)` function. This will run every frame after `on_ready()`. The argument `delta` is the delta time variable.
    
    The `self` value in these functions is.. the node the script is attached to. You cannot replace Node functions with a script.

    There is nothing to do with this Node. The only useful thing to do with it is run a script with it, and no more.
    """
    
    node_base_data = {
        "prop":   {},
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    def __init__(self, data=node_base_data, parent=None):
        self.parent      = parent
        self.screen      = engine.interface
        self.resourceman = engine.resource_loader
        self.window_id   = engine.interface.main_surf_id
        super().__init__(data)
    
    def free(self):
        """Free object from memory"""
        self.stop_running = True

    def update(self, delta):
        if self.stop_running:
            return
        self._process(delta)