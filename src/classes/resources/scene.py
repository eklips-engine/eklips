# Import classes
from classes.resources.object import *
from classes.nodes import *

# Variables
EMPTY_SCENE = {"": {"type": "Node", "children": {}}}

# Classes
class SceneError(Warning):
    pass

class CollisionManager:
    """
    Class to store and check if shapes are colliding.
    """
    shapes = {}

    @property
    def amount(self): return len(self.shapes)
    
    def add(self, shape):
        """Add `shape` to the world."""
        sid              = self.amount
        self.shapes[sid] = shape
        return sid

    def delete(self, sid):
        """Delete shape `sid` from the world."""
        self.shapes.pop(sid)
    
    def colliderect(self, shape, other):
        """Check if `shape` is colliding with `other`."""
        ax1, ay1, ax2, ay2 = shape.aabb()
        bx1, by1, bx2, by2 = other.aabb()

        return not (
            ax2 < bx1 or
            ax1 > bx2 or
            ay2 < by1 or
            ay1 > by2
        )

    def get_collisions(self, shape):
        """Get the shapes that are colliding `shape`."""
        hits = []
        for sid in self.shapes:
            other = self.shapes[sid]
            if other is shape:
                continue
            if self.colliderect(shape, other):
                hits.append(other)
        return hits

class Scene(Object):
    """
    Manages the game loop via a hierarchy of nodes from a scene file.

    As one of the most important classes, the Scene manages the hierarchy of nodes in a scene,
    as well as scenes themselves. Nodes can be added, fetched and removed. The whole scene tree
    (and thus the current scene) can be paused. Scenes can be loaded, switched and reloaded.

    The scene class also contains a CollisionManager.
    """
    print(" ~ Initialize Scene")
    paused                           = False       # If the update() function can laze around and do nothing
    nodes                            = EMPTY_SCENE # Scene tree
    _doomed                          = []          # List of nodes that are about to be deleted
    _marked_scene_chng               = ""          # Filepath of the scene that's about to be loaded
    _file_path                       = None        # Filepath of the current scene
    _inherited_scn                   = None        # Filepath of the inherited scene
    _blessed                         = []          # List of nodes that are about to be created
    _temp_node_list                  = []          # List of nodepaths in the scene tree
    _collisionman : CollisionManager = None        # Collision Manager

    @property
    def file_path(self) -> str:
        return self._file_path
    @file_path.setter
    def file_path(self, path : str):
        self.empty()
        self._collisionman = engine.resources.CollisionManager()
        self._file_path    = path
        _data              = engine.loader.load(path)
        if _data["properties"]["inherits"]:
            self._loadscenefile(_data["properties"]["inherits"])
        self._loadscenefile(path)
    
    def _loadscenefile(self, path):
        _data      = engine.loader.load(path)
        self.nodes = _data["nodes"]
        nodepaths  = self.get_node_paths("")

        for nodepath in nodepaths:
            self._initialize_node_entry(nodepath)

    def get_node_paths(self, nodepath, exclude_self=False, out=None):
        """Get a list of this Nodes children. (e.g. `["root://foo/bar", ...]`)
        
        .. nodepath:: Path of the node in the scene tree.
        .. exclude_self:: Whether to add the passed Node to the list or not.
        .. out:: The list to place the Nodes children. Defaults to None and SHOULD be None."""

        if out == None: out = []
        if not exclude_self:
            out.append(nodepath)
        
        node     = self.get_node_entry_from_path(nodepath)
        children = node.get("children",{}).keys()

        for child in children:
            self.get_node_paths(f"{nodepath}/{child}", False, out)
        return out
        
    def load(self, path):
        """Load a scene file.
        
        .. path:: Path of the scene in the filesystem (`res://`, `root://`, `user://`)"""
        self._marked_scene_chng = path
    
    def get_node_parent(self, nodepath, throw_error_if_failed=False):
        """Get a Nodes parent.
        
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed getting the parent."""
        parts    = nodepath.split("/")
        try:
            current = self.nodes[parts[0]] # Get Root node
            for name in parts[1:][:-1]:    # Go through the Node's parents
                try:
                    current = current["children"][name] # Get the previous iter.'s child
                except Exception as error:
                    raise error
            return current # Return the parent
        except Exception as error:
            if throw_error_if_failed:
                raise SceneError(f"Tried to get node entry {nodepath}'s parent but failed")
    
    def get_node_children(self, nodepath):
        """Get a Nodes children. Same as `get_nodes(nodepath, exclude_self=True)`
        
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)"""
        return self.get_nodes(nodepath, exclude_self=True)
    
    def _initialize_node_entry(self, nodepath):
        node = self.get_node_entry_from_path(nodepath)

        # Get node's parent
        parent   = self.get_node_parent(nodepath)
        children = self.get_node_children(nodepath)

        # Make Node
        classobj                = globals().get(node["type"])
        obj : engine.nodes.Node = classobj.__new__(classobj)

        # Init object and export values
        obj.__init__(node, parent)
        obj.name = nodepath.split("/")[-1]
        obj._setup_properties()

        # Set obj parameter to Node
        node["obj"] = obj

        # Recompile list of nodes
        self._temp_node_list = self.get_node_paths("")

        # Return Node if needed
        return obj
    
    def add_node(self, data, nodepath="/test", throw_error_if_failed=False):
        """Add a node with parameters after the scene has finished updating.
        
        .. data:: The node's properties.
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed making the Node."""
        self._blessed.append([data, nodepath, throw_error_if_failed])
    
    def _add_node(self, data, nodepath="", throw_error_if_failed=False) -> int:
        """Add a node with parameters. Returns the Node object.
        
        .. data:: The node's properties.
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed making the Node."""

        parts    = nodepath.split("/")
        try:
            current = self.nodes[parts[0]] # Get Root node
            for name in parts[1:][:-1]:    # Go through the Nodes in the path besides the one we're making
                try:
                    current = current["children"][name] # Get the previous iter.'s child
                except Exception as error:
                    raise error
            current["children"][parts[-1]] = data
        except Exception as error:
            if throw_error_if_failed:
                raise SceneError(f"Tried to make node entry {nodepath} but failed")
            return
        
        # Initialize Node object and recompile Node list
        return self._initialize_node_entry(nodepath)
    
    def get_nodes(self, nodepath=USE_SCENE_TREE, exclude_self=False) -> list[str]:
        """Get a list of each Node in the scene tree or a node entry. (e.g. `[Node2D(path='/'), ...]`)
        
        .. node:: The node to get a list of each child of using its node path.
        .. exclude_self:: Whether to add the passed Node to the list or not."""
        if nodepath == USE_SCENE_TREE: nodepath = ""

        nodepaths = self.get_node_paths(nodepath, exclude_self=False)
        nodes     = []

        for _nodepath in nodepaths:
            nodes.append(self.get_node_from_path(_nodepath))
        
        return nodes

    def get_node_entry_from_path(self, nodepath : str, throw_error_if_failed : bool = False) -> dict:
        """Get a Node's data using its path in the scene tree. (e.g. `{"type": "Node2D", "transform": {...}, ...}`)
        
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed getting the Node."""
        if nodepath == "": return self.nodes[""]

        parts    = nodepath.split("/")
        try:
            current = self.nodes[parts[0]] # Get Root node
            for name in parts[1:]:         # Go through the rest
                try:
                    current = current["children"][name] # Get the previous iter.'s child
                except Exception as error:
                    raise error

            # Now that we found it, return it
            return current
        except Exception as error:
            if throw_error_if_failed:
                raise SceneError(f"Tried to get node entry {nodepath} from Scene but failed")
            return {"type":"Node", "obj": None}

    def get_node_from_path(self, nodepath, throw_error_if_failed : bool = False) -> Node:
        """Get a Node using its path in the scene tree. (e.g. `/foo/bar`)
        
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed getting the Node."""
        return self.get_node_entry_from_path(nodepath, throw_error_if_failed).get("obj", None)

    def delete_node(self, nodepath, throw_error_if_failed = False):
        """Mark a Node to be deleted after the scene is updated using its path.
        
        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed deleting the Node."""
        self._doomed.append([nodepath, throw_error_if_failed])
    
    def _delete_node(self, nodepath, throw_error_if_failed = False):
        """Delete a Node using its path.

        .. nodepath:: The node's path in the scene tree. (etc, `/father/me`, `/me`)
        .. throw_error_if_failed:: Throw an Error if it failed deleting the Node."""
        
        parts    = nodepath.split("/")
        try:
            current = self.nodes[parts[0]] # Get Root node
            for name in parts[1:][:-1]:    # Go through the Nodes in the path besides the one we're making
                try:
                    current = current["children"][name] # Get the previous iter.'s child
                except Exception as error:
                    raise error
            
            # Now we can delete the Node and remove it eternally
            node : Node = current["children"][parts[-1]]
            node.free()

            current["children"].pop(parts[-1])
        except Exception as error:
            if throw_error_if_failed:
                raise SceneError(f"Tried to make node entry {nodepath} but failed")
            return
        
        # Recompile list of nodes
        self._temp_node_list = self.get_node_paths("")
    
    def empty(self):
        """Empty the scene."""
        for nodepath in self.get_node_paths(""):
            self._delete_node(nodepath)
        self.nodes = EMPTY_SCENE
    def _free(self):
        self.empty()
        super()._free()
    
    def pause(self):  self.paused = True
    def resume(self): self.paused = False
    def update(self):
        if self.paused:
            return
        try:
            for nodepath in self._temp_node_list:
                node = self.get_node_from_path(nodepath)
                if not node:
                    continue
                if not node._runnable:
                    self._delete_node(nodepath)
                    continue
                node.update()
        except Exception as error:
            raise error

        ## Things you can't do in the for loop above me without causing trouble
        if self._marked_scene_chng:
            self.file_path          = self._marked_scene_chng
            self._marked_scene_chng = None
        for i in self._doomed:
            self._delete_node(*i)
        for i in self._blessed:
            self._add_node(*i)
        self._blessed.clear()
        self._doomed.clear()