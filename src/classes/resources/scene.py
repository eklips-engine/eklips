## Import classes
import pymunk
from classes.resources.resource import *
from classes.resources.theme    import *
from classes.nodes              import *

## Classes
class SceneLike:
    def __init__(self):
        self.paused                           = False       # If the update() function can laze around and do nothing
        self._nodes                           = EMPTY_SCENE # Scene tree
        self._doomed                          = []          # List of nodes that are about to be deleted
        self._marked_scene_chng               = None        # Filepath of the scene that's about to be loaded
        self._file_path                       = None        # Filepath of the current scene
        self._inherited_scn                   = None        # Filepath of the inherited scene
        self._blessed                         = []          # List of nodes that are about to be created
        self._temp_node_list                  = []          # List of nodepaths in the scene tree
        self._widgetman    : WidgetManager    = None        # Widget Manager

class Scene(Resource, SceneLike):
    """
    Manages the game loop via a hierarchy of nodes from a scene file.

    As one of the most important classes, the Scene manages the hierarchy of nodes in a scene,
    as well as scenes themselves. Nodes can be added, fetched and removed. The whole scene tree
    (and thus the current scene) can be paused. Scenes can be loaded, switched and reloaded.
    There can be multiple Scenes running in the game loop thanks to the `PackedScene` node,
    but ultimately is in this class (exposed as `self.scene`) 

    The scene class also contains a CollisionManager.
    """
    print(" ~ Initialize Scene")
    
    ## Init
    def __init__(self, properties={}):
        super().__init__(properties)
        SceneLike.__init__(self)

    ## Resource related
    # Filepath property
    @export(None, "str", "file_path/scn")
    def file_path(self) -> str:
        return self._file_path
    @file_path.setter
    def file_path(self, path : str):
        print(f" ~ Load scene {path}")

        # Set filepath and load
        self._file_path = path
        self.nodes      = engine.loader.load(path, force_new_resource=True)["nodes"]
    
    # Nodes property
    @export({}, "dict", "HIDDEN")
    def nodes(self) -> dict:
        return self._nodes
    @nodes.setter
    def nodes(self, nodes : dict):
        if self._file_path != None: # Scene is probs empty if this is True so dont bother if it is
            self.empty()
        
        ## Init managers
        self._reload_managers()

        ## Set nodes
        self._nodes = nodes
        self._reload_nodes()
    
    # Reload
    def _reload_managers(self):
        self._widgetman = engine.resources.WidgetManager()
    def _reload_nodes(self):
        nodepaths = self.get_node_paths("")
        _nodes    = []

        # Make nodes
        for nodepath in nodepaths:
            node = self._initialize_node_entry(nodepath)
            _nodes.append(node)
        
        # Make nodes ready up
        for node in _nodes:
            self._ready_node(node)
    
    # Replace resource classes
    def load(self, path):
        """
        Load a scene file.

        .. note:: This does not return a Scene class, as this is different from `Resource.load()` and is not a classmethod. Instead, use it like this: `myscene.load(path)`

        Args:
            path: Path of the scene in the filesystem (`res://`, `root://`, `user://`)
        """
        self._marked_scene_chng = path
    @classmethod
    def new(cls):
        return Scene({"nodes":EMPTY_SCENE})
    def save(self, path):
        with open(engine.loader._get_true_path(path), "w") as f:
            f.write(json.dumps({
                "nodes": self.nodes, 
                "properties": {
                    "inherits": self._inherited_scn
                }}))
    
    ## Add node
    def _initialize_node_entry(self, nodepath):
        node = self.get_node_entry_from_path(nodepath)

        # Get node's parent
        parent = self.get_node_parent(nodepath)

        # Make Node
        classobj                = globals().get(node["type"])
        obj : engine.nodes.Node = classobj.__new__(classobj)
        
        # Set obj parameter to Node
        node["obj"] = obj

        # Init object and export values
        obj.__init__(node, parent)
        obj.name = nodepath.split("/")[-1]
        obj._setup_properties(scene=self)

        # Recompile list of nodes
        self._temp_node_list.append([obj, nodepath])

        # Return Node if needed
        return obj
    def add_node(self, data, nodepath="/test", throw_error_if_failed=False) -> None:
        """Add a node with parameters after the scene has finished updating.
        
        Args:
            data: The node's properties.
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed making the Node."""
        self._blessed.append([data, nodepath, throw_error_if_failed])
    def _add_node(self, data, nodepath="/test", throw_error_if_failed=False) -> int:
        """Add a node with parameters. Returns the Node object.
        
        Args:
            data: The node's properties.
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed making the Node."""
        parts = [""] + nodepath.strip("/").split("/") if nodepath else [""]
        try:
            current = self.nodes[parts[0]]          # Get root node
            for name in parts[1:][:-1]:             # Go through the Nodes in the path besides the one we're making
                current = current["children"][name] # Get the previous iter.'s child
            current["children"][parts[-1]] = data
        except Exception as error:
            if throw_error_if_failed or engine.debug.avoid_error_mercy:
                raise SceneError(f"Tried to make node entry {nodepath} but failed")
            return

        # Initialize Node object and recompile Node list
        return self._ready_node(self._initialize_node_entry(nodepath))
    
    ## Ready node
    def _ready_node(self, node : Node) -> Node:
        if not node.processable:
            return
        try:
            node._onready(node)
        except AttributeError:
            pass # Script probably doesn't have an onready func
        return node
    
    ## Get nodes
    def get_node_paths(self, nodepath, exclude_self=False, out=None) -> list[str]:
        """Get a list of this Nodes children. (e.g. `["root://foo/bar", ...]`)
        
        Args:
            nodepath: Path of the node in the scene tree.
            exclude_self: Whether to add the passed Node to the list or not.
            out: The list to place the Nodes children. Defaults to None and SHOULD be None."""
        out = out or []
        if not exclude_self: out.append(nodepath)
        for child in self.get_node_entry_from_path(nodepath).get("children", {}):
            self.get_node_paths(f"{nodepath}/{child}", False, out)
        return out
    def get_nodes(self, nodepath=USE_SCENE_TREE, exclude_self=False) -> list[Node]:
        """Get a list of each Node alongside its path in the scene tree or a node entry. (e.g. `[(Node2D(), "/"), ...]`)
     
        Args:   
            node: The node to get a list of each child of using its node path.
            exclude_self: Whether to add the passed Node to the list or not."""
        nodepath = "" if nodepath == USE_SCENE_TREE else nodepath
        return [[self.get_node_from_path(p), p] for p in self.get_node_paths(nodepath, exclude_self)]
    def get_node_entry_from_path(self, nodepath : str, throw_error_if_failed : bool = False) -> dict:
        """Get a Node's data using its path in the scene tree. (e.g. `{"type": "Node2D", "transform": {...}, ...}`)
       
        Args: 
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed getting the Node."""
        if nodepath == "": return self.nodes[""]
        if len(nodepath.split("/")) == 1:
            nodepath = "/" + nodepath
        
        parts = nodepath.split("/")
        try:
            current = self.nodes[parts[0]]          # Get root node
            for name in parts[1:]:                  # Go through the Nodes in the path
                current = current["children"][name] # Get the previous iter.'s child
            return current                          # Now that we found it, return it.
        except Exception as error:
            if throw_error_if_failed or engine.debug.avoid_error_mercy:
                raise SceneError(f"Tried to get node entry {nodepath} but failed")
            raise error
    def get_node_from_path(self, nodepath, throw_error_if_failed : bool = False) -> Node:
        """Get a Node using its path in the scene tree. (e.g. `/foo/bar`)
        
        Args:
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed getting the Node."""
        return self.get_node_entry_from_path(nodepath, throw_error_if_failed).get("obj", None)
    def get_node_parent(self, nodepath, throw_error_if_failed=False) -> Node:
        """Get a Nodes parent.

        Args:
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed getting the parent."""
        parts = [""] + nodepath.strip("/").split("/") if nodepath else [""]
        try:
            current = self.nodes[parts[0]]          # Get root node
            for name in parts[1:][:-1]:             # Go through the Nodes parents
                current = current["children"][name] # Get the previous iter.'s child
            return current.get("obj", None)         # Return the parent
        except Exception as error:
            if throw_error_if_failed or engine.debug.avoid_error_mercy:
                raise SceneError(f"Tried to get node entry {nodepath}'s parent but failed")
            return
    def get_node_children(self, nodepath, throw_error_if_failed=False) -> list[Node]:
        """Get a Nodes children.

        Args:     
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed getting the children."""
        parts = [""] + nodepath.strip("/").split("/") if nodepath else [""]
        try:
            current = self.nodes[parts[0]]          # Get root node
            for name in parts[1:]:                  # Go through the Nodes in the path
                current = current["children"][name] # Get the previous iter.'s child
            children = current.get("children", {})
            return [c.get("obj") for c in children.values()] # Return the children
        except Exception as error:
            if throw_error_if_failed or engine.debug.avoid_error_mercy:
                raise SceneError(f"Tried to get node entry {nodepath}'s children but failed")
            return
    
    ## Delete related
    def delete_node(self, nodepath, throw_error_if_failed = False):
        """Mark a Node to be deleted after the scene is updated using its path.
        
        Args:
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed deleting the Node."""
        self._doomed.append([nodepath, throw_error_if_failed])
    def _delete_node(self, nodepath, throw_error_if_failed = False):
        """Delete a Node using its path.

        Args:
            nodepath: The node's path in the scene tree. (etc, `/father/me`, `/me`)
            throw_error_if_failed: Throw an Error if it failed deleting the Node."""
        parts = [""] + nodepath.strip("/").split("/") if nodepath else [""]
        try:
            current = self.nodes[parts[0]]                   # Get root node
            for name in parts[1:][:-1]:                      # Go through the Nodes in the path
                current = current["children"][name]          # Get the previous iter.'s child
            if parts[-1] not in current["children"]:
                return
            node = current["children"][parts[-1]].get("obj") # Get the Node

            # Now we can delete the Node and remove it eternally
            current["children"].pop(parts[-1])
        except Exception as error:
            if throw_error_if_failed or engine.debug.avoid_error_mercy:
                raise SceneError(f"Tried to delete node entry {nodepath} but failed")
            return
        
        # Recompile list of nodes
        self._temp_node_list.remove([node, nodepath])

    def empty(self):
        """Empty the scene."""
        root = self.nodes[""].get("obj")
        if root: root._free()
        
        self._nodes          = EMPTY_SCENE
        self._temp_node_list = []
    def _free(self):
        self.empty()
        super()._free()
    
    ## Update
    def pause(self):  self.paused = True
    def resume(self): self.paused = False
    def update(self):
        if self.paused:
            return

        # Update all nodes
        for node, path in self._temp_node_list:
            if not self._runnable:
                return
            if not node or not node._runnable:
                self.delete_node(path)
                continue
            node.update()

        # Change scenes
        if self._marked_scene_chng:
            self.file_path          = self._marked_scene_chng
            self._marked_scene_chng = None

        # Delete nodes
        for path, throw in self._doomed:
            self._delete_node(path, throw)

        # Add nodes
        for data, path, throw in self._blessed:
            self._add_node(data, path, throw)
        
        # Clear queues
        self._blessed.clear()
        self._doomed.clear()

## Import PackedScene here to not have any trouble
from classes.nodes.packedscene import *