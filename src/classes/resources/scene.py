# Import inherited
from classes.resources.object import *

# Import nodes
from classes.nodes import *

# Variables
EMPTY_SCENE = {"": {"type": "Node", "children": {}}}

# Classes
class SceneError(Warning):
    pass

class Scene(Object):
    """
    Manages the game loop via a hierarchy of nodes from a scene file.

    As one of the most important classes, the Scene manages the hierarchy of nodes in a scene,
    as well as scenes themselves. Nodes can be added, fetched and removed. The whole scene tree
    (and thus the current scene) can be paused. Scenes can be loaded, switched and reloaded.
    """
    print(" ~ Initialize Scene")
    paused                  = False       # If the update() function can laze around and do nothing
    nodes                   = EMPTY_SCENE # Scene tree
    _doomed                 = []          # List of nodes that are about to be deleted
    _marked_scene_chng      = ""          # Filepath of the scene that's about to be loaded
    _file_path              = None        # Filepath of the current scene
    _inherited_scn          = None        # Filepath of the inherited scene
    _blessed                = []          # List of nodes that are about to be created
    _temp_node_list         = []          # List of nodepaths in the scene tree

    @property
    def file_path(self) -> str:
        return self._file_path
    @file_path.setter
    def file_path(self, path : str):
        self.empty()
        self._file_path = path
        _data           = engine.loader.load(path)
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
    
    def get_node_parent(self, nodepath):
        """Get a Nodes parent.
        
        .. nodepath:: Path of the node in the scene tree."""
        ppath = "/".join(nodepath.split("/")[:-1])
        return self.get_node_from_path(ppath)
    
    def get_node_children(self, nodepath):
        """Get a Nodes children. Same as `get_nodes(nodepath, exclude_self=True)`
        
        .. nodepath:: Path of the node in the scene tree."""
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
    
    def add_node(self, data):
        """Add a node with parameters after the scene has finished updating.
        
        .. data:: The node's properties."""
        self._blessed.append(data)
    
    def _add_node(self, data) -> int:
        """Add a node with parameters. Returns that Nodes ID.
        
        .. data:: The node's properties."""
        nid = f"@:{len(self.nodes)}"

        self.nodes[nid] = data
        self._initialize_node_entry(nid)

        return nid
    
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
        
        .. nodepath:: Path of the node in the scene tree.
        .. throw_error_if_failed:: Throw an Error if it failed getting the Node."""
        if nodepath == "": return self.nodes[""]

        parts    = nodepath.split("/")
        try:
            current = self.nodes[parts[0]]
            for name in parts[1:]:
                try:
                    current = current["children"][name]
                except Exception as error:
                    raise error

            return current
        except Exception as error:
            if throw_error_if_failed:
                raise SceneError(f"Tried to get node entry {nodepath} from Scene but failed")
            else:
                raise error
                return {"obj": None}

    def get_node_from_path(self, nodepath, throw_error_if_failed : bool = False) -> Node:
        """Get a Node using its path in the scene tree. (e.g. `root://foo/bar`)
        
        .. nodepath:: Path of the node in the scene tree.
        .. throw_error_if_failed:: Throw an Error if it failed getting the Node."""
        return self.get_node_entry_from_path(nodepath, throw_error_if_failed).get("obj", None)

    def delete_node(self, nodepath):
        """Mark a Node to be deleted after the scene is updated using its path.
        
        .. nodepath:: Path of the node in the scene tree."""
        if not self.get_node_from_path(nodepath, throw_error_if_failed=False):
            return
        self._doomed.append(nodepath)
    
    def _delete_node(self, nodepath):
        """Delete a Node using its path."""
        if not self.get_node_from_path(nodepath, throw_error_if_failed=False):
            return
        try:
            node   = self.get_node_from_path(nodepath)
            node._free()
        except:
            pass
        self.get_node_entry_from_path(nodepath)["obj"] = None
        # XXX Delete that entry? ^ (it's self.nodes[""]["children"]["something"])
        gc.collect()
    
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
            self._delete_node(i)
        for i in self._blessed:
            self._add_node(i)
        self._blessed.clear()
        self._doomed.clear()