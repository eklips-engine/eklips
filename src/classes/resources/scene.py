# Import inherited
from classes.resources.object import *
import types

# Import nodes
from classes.nodes import *

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
    nodes                   = {}
    _marked_for_disassembly = []
    _marked_scene_chng      = ""
    _file_path              = None
    _inherited_scn          = None

    @property
    def file_path(self) -> str:
        return self._file_path
    @file_path.setter
    def file_path(self, path : str):
        self.empty()
        self._file_path = path
        _data           = engine.loader.load(path)
        self.nodes      = _data["nodes"]
        if _data["properties"]["inherited"]:
            self._inherited_scn = _data["properties"]["inherits"]
            _inherited_nodes    = engine.loader.load(path)["nodes"]

            for node in _inherited_nodes:
                self.nodes[f"i@{self._inherited_scn}:{node}"] = _inherited_nodes[node]
        
        for nid in self.nodes:
            self._initialize_node_entry(nid)
        
    def load(self, path):
        """Load a scene file."""
        self._marked_scene_chng = path
    
    def _initialize_node_entry(self, nid):
        # {'type':'Node', 'path':'', 'name':'Node'...}
        node = self.nodes[nid]

        # Full path including this node
        full_path   = f"{node['path']}/{node['name']}".strip("/")

        directories  = full_path.split("/")[:-1]  # Only parents, exclude self
        parent       = None
        current_path = ""

        for directory in directories:
            if len(current_path) == 0:
                continue
            existing = self.get_node_from_path(f"{current_path.lstrip('/')/directory}")
            current_path += f"/{directory}"
            if not existing:
                raise SceneError("The parent of the node you are creating does not exist.")
            else:
                parent = existing

        # Make Node
        classobj                = globals().get(node["type"])
        obj : engine.nodes.Node = classobj.__new__(classobj)
        for i in obj.base_properties:
            if not i in node:
                node[i] = obj.base_properties[i]
        obj.__init__(node, parent)

        # Set obj parameter to Node
        node["obj"] = obj
    
    def add_node(self, data) -> int:
        """Add a node with parameters. Returns that Node's ID."""
        nid = f"@:{len(self.nodes)}"

        self.nodes[nid] = data
        self._initialize_node_entry(nid)

        return nid
    
    def get_node_from_path(self, nodepath) -> Node:
        """Get a Node using its path in the scene tree. (e.g. `foo/bar`)"""
        path = "/".join(nodepath.split("/")[:-1])
        name = nodepath.split("/")[-1]
        for i in self.nodes:
            if self.nodes[i]["path"] == path:
                if self.nodes[i]["name"] == name:
                    return self.nodes[i]["obj"]

    def delete_node(self, node_id):
        """Mark a Node to be deleted after the scene is updated using its ID."""
        if not node_id in self.nodes:
            return
        self._marked_for_disassembly.append(node_id)
    
    def _delete_node(self, node_id):
        """Delete a Node using its ID."""
        if not node_id in self.nodes:
            return
        try:
            node   = self.nodes[node_id]["obj"]
            node._free()
        except:
            pass
        self.nodes[node_id]["obj"] = None
        self.nodes.pop(node_id)
        gc.collect()
    def empty(self):
        """Empty the scene."""
        while len(self.nodes):
            try:
                for node_id in self.nodes:
                    self._delete_node(node_id)
            except:
                pass
    
    def _free(self):
        self.empty()
        super()._free()
    
    def update(self):
        try:
            for node_id in self.nodes:
                node : Node = self.nodes[node_id].get("obj", None)
                if not node:
                    continue
                if not node._runnable:
                    node._free()
                    self._delete_node(node_id)
                    continue
                node.update()
        except Exception as error:
            raise error

        ## Things you can't do in the for loop above me without causing trouble
        if self._marked_scene_chng:
            self.empty()
            self.file_path = self._marked_scene_chng
            self._marked_scene_chng = None
        for i in self._marked_for_disassembly:
            self._delete_node(i)
        
        self._marked_for_disassembly.clear()