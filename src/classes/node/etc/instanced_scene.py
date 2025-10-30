## Import all the libraries necessary and engine singleton
import pyglet as pg
from tkinter.messagebox import *
from classes.object import Object
from anytree import NodeMixin
import classes.singleton as engine

## Import inherited
from classes.node.node import Node
from classes.scene     import Scene

## Node
class InstancedScene(Node):
    """
    ### A Node acting as a Scene.

    A Scene is a collection of Nodes in a tree hierarchy.
    This Node takes the path of a scene file (e.g. `root://internal/scn/loading.scn`..) and puts all of its Nodes in the current Scene.
    """

    node_base_data = {
        "prop":   {
            "path": "root://internal/scn/loading.scn"
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "InstancedScene"
        },
        "script": None
    }

    node_signals = [
        "_scene_instanced",
        "_scene_uninstanced",
        "_scene_crashed"
    ]

    def __init__(self, data=node_base_data, parent=None):
        super().__init__(data, parent)
        Scene.__init__(self, self.properties["path"])
        self.file_path  = self.properties["path"]