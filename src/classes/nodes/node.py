# Import inherited
from classes.resources.object import *
from anytree import NodeMixin
import types

# Classes
class Node(Object, NodeMixin):
    """
    ## An empty Node.

    Nodes are the building block of Eklips (well, Eklips 4+ atleast). Every Node is inherited off this node class.
    A tree of Nodes make a Scene, A scene is stored as `engine.scene`.
    
    You can make a script have an `_onready(self)` function. This will only run when a Node is fully loaded.
    You can make a script have a `_process(self, delta)` function. This will run every frame after `_onready`. The argument `delta` is the delta time variable.
    
    The `self` value in these functions is.. the node the script is attached to. You cannot replace Node functions with a script.

    There is nothing to do with this Node. The only useful thing to do with it is run a script with it, and no more.
    """
    base_properties = {
        "name":   "Node",
        "type":   "Node",
        "path":   "",
        "script": None
    }

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties)
        self.parent = parent
        self.name   = properties["name"]
        if self._can_init_script:
            self.script_path = self.properties["script"]
        
    def update(self):
        if not self._runnable:
            self._free()
            return
        self._process()
    
    def free(self):
        """Free the object from memory."""
        self._runnable = False