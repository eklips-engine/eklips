# Import inherited
from classes.resources.object import *
from anytree import NodeMixin
import types
from typing import Any

# Classes
class Node(Object, NodeMixin):
    """
    An empty Node.

    Nodes are the building block of Eklips (well, Eklips 4+ atleast). Every Node is inherited off this node class.
    A tree of Nodes make a Scene, A scene is stored as `engine.scene`.
    
    You can make a script have an `_onready(self)` function. This will only run when a Node is fully loaded.
    You can make a script have a `_process(self, delta)` function. This will run every frame after `_onready`. The argument `delta` is the delta time variable.
    
    The `self` value in these functions is.. the node the script is attached to. You cannot replace Node functions with a script.

    There is nothing to do with this Node. The only useful thing to do with it is run a script with it, and no more.
    """

    def __init__(
            self,
            properties : dict                   = {}, 
            parent     : NodeMixin       | None = None,
            children   : list[NodeMixin] | None = None
        ):
        super().__init__(properties)

        # Set up family tree
        # self.parent = parent
        if children:
            self.children = children
    
    # Update code
    def update(self):
        # Check if i have to be freed
        if not self._runnable:
            self._free()
            return

        # Run process function
        self._process()
    
    # Memory related
    def _free(self):
        # Free children
        self._runnable = False
        for child in self.children:
            child._free()
        
        # Free self
        super()._free()
    
    def free(self):
        """Free the Node from memory.
        
        Freeing a Node does not delete it from the scene tree, but the
        Scene can automatically detect this and delete it."""
        self._runnable = False