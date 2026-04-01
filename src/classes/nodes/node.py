## Import inherited
from classes.resources.object import *
import types
from typing import Any

## Classes
class Node(Object, NodeMixin):
    """
    An empty Node.

    Nodes are the building block of Eklips (well, Eklips 4+ atleast). Every Node is inherited off this node class.
    A tree of Nodes make a Scene, A scene is stored as `engine.scene`.
    
    You can make a script have an `_onready(self)` function. This will only run when a Node is fully loaded.
    You can make a script have a `_process(self, delta)` function. This will run every frame after `_onready`. The argument `delta` is the delta time variable.

    The `self` value in these functions is.. the node the script is attached to. You cannot replace Node functions with a script.

    In a Script, `engine.scene` is the main scene being run. the variable `self.scene` is the scene the Node is located in as multiple scenes can exist thanks to the PackedScene node.

    There is nothing to do with this Node. The only useful thing to do with it is run a script with it, and no more.
    
    Also, the `_onready` function in a Script is only called after the scene is fully initialized, so
    don't worry about issues.
    """
    
    ## Init
    def __init__(
            self,
            properties : dict        = {}, 
            parent     : Self | None = None
        ):
        super().__init__(properties)
        self.parent = parent
        self._scene = None

    ## Property related
    @property
    def scene(self):
        """The scene the Node is located in. Use this over `engine.scene` as that is the main scene.
        
        This variable is a thing as multiple scenes can exist thanks to the PackedScene node."""
        return self._scene
    def _setup_properties(self, scene=None):
        """Setup the Node's properties to whatever was passed in `__init__`."""
        # Setup properties
        self._scene = scene
        for key in self._properties_onready:
            if key in ["children","parent","signals","type"]:
                continue
            self.set(key, self._properties_onready[key])
        
        # The scene is expected to call _onready when the scene itself is ready.
    
    ## Memory related
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