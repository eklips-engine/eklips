## Import all the libraries
import pyglet as pg
import json, time, types, tkinter as tk
from tkinter.messagebox import *
from classes import event, ui, resources
from classes.object import Object
from pyglet import gl
from anytree import NodeMixin
from PIL import Image, ImageTk
import classes.singleton as engine

# I don't even know
tot = 1
def _node_tree(kind, gen, fg, nme, l, sp=False):
    global tot
    if sp: print("|"*l+" "+nme.__name__)
    for n in kind:
        n : Node
        ls = n.__subclasses__()
        ds = {}
        for i in ls:
            ds[i] = {}
        gen[n] = ds
        tot   += 1
        gen[n] =_node_tree(ds, gen[n], gen, n, l+1, sp)
    return gen

# Get a dictionary of a tree of all the Nodes in Eklips
def node_tree(can_print = False):
    global tot
    gens   = {Node: {}}
    genone = Node.__subclasses__()

    gens   = _node_tree(genone, gens[Node], gens, Node, 0, can_print)

    if can_print:
        print(f"There are a total of {tot} Node{'s' if tot != 1 else ''}")
    
    return gens

## Scene class
class Scene(Object):
    def __init__(self, file_path):
        self.file_path        = file_path
        self.nodes            = {}
        self.cam_pos          = [0, 0]
        self.nodes_collision  = {}
        self.properties       = {}
        self.screen           = engine.interface
        self.resourceman      = engine.resource_loader

    def _free(self):
        self.empty()
        super()._free()
        
    def empty(self):
        self.nodes_collision = {}
        self.cam_pos         = [0, 0]
        for i in self.nodes:
            self.nodes[i]["object"]._free()
        self.nodes           = {}
    
    def add_node(self, node_data={}):
        id = len(self.nodes)

        # Full path including this node
        full_path   = f"{node_data['path']}/{node_data['name']}".strip("/")

        directories  = full_path.split("/")[:-1]  # Only parents, exclude self
        parent       = None
        current_path = ""

        for directory in directories:
            if len(current_path) == 0:
                continue
            existing = self.get_node_from_path(current_path.lstrip("/"), directory)
            current_path += f"/{directory}"
            if not existing:
                raise Exception("The parent of the node you are creating does not exist.")
            else:
                parent = existing

        # Construct node data
        node_obj_data = {
            "prop":     node_data["properties"],
            "data":     {},
            "meta":     {
                "kind": "Node",
                "name": node_data["name"]
            },
            "script":   node_data["script"],
            "signal":   node_data["signals"]
        }

        # Create the actual node
        classobj           = globals().get(node_data["type"])
        object             = classobj.__new__(classobj)
        object.__init__(node_obj_data, parent)

        # Store in dictionary
        self.nodes[id] = {
            "class":     node_data["type"],
            "path":      node_data["path"],
            "object":    object,
            "name":      node_data["name"],
            "base_data": node_data
        }

        return self.nodes[id]["object"]

    def load(self):
        self.empty()
        scene_obj  = json.loads(self.resourceman.load(self.file_path).get())
        self.properties = scene_obj["Properties"]
        for node in scene_obj["Nodes"]:
            node_data = scene_obj["Nodes"][node]
            self.add_node(node_data)

    def update(self, delta):
        try:
            nkill = []
            for nodeID in self.nodes:
                try:
                    node = self.nodes[nodeID]["object"]
                except:
                    print("Node may have been removed without notice.. Skipping")
                    continue
                if node.stop_running:
                    node._free()
                    continue
                node.update(delta)
            for nodeID in nkill:
                self.nodes.pop(nodeID)
        except Exception as error:
            print(f" Scene({self.file_path}) had an error updating; {error}")
            raise error
    
    ## Get nodes
    def get_node_from_path(self, path, name):
        for i in self.nodes:
            if self.nodes[i]["path"] == path:
                if self.nodes[i]["name"] == name:
                    return self.nodes[i]["object"]

## Import nodes
from classes.node.node                   import Node

from classes.node.gui.button             import *
from classes.node.gui.canvasitem         import *
from classes.node.gui.color_rect         import *
from classes.node.gui.label              import *
from classes.node.gui.progressbar        import *
from classes.node.gui.slider             import *
from classes.node.gui.treeview           import *

from classes.node.gui.media.audio_player import *
from classes.node.gui.media.video_player import *

from classes.node.etc.option_dialog      import *
from classes.node.etc.tk_window          import *
from classes.node.etc.timer              import *
from classes.node.etc.instanced_scene    import *

from classes.node.twod.node2d            import *
from classes.node.twod.sprite2d          import *
from classes.node.twod.animatedsprite2d  import *
from classes.node.twod.area2d            import *
from classes.node.twod.camera2d          import *
from classes.node.twod.physicsbody2d     import *
from classes.node.twod.collisionbox2d    import *
from classes.node.twod.parallax2d        import *
from classes.node.twod.tilemap           import *