## Import inherited
from classes.node.gui.canvasitem import CanvasItem

## Import engine singleton singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class Treeview(CanvasItem):
    # XXX   Out of date and not very good
    node_base_data = {
        "prop":   {
            "transform": {
                "pos":    [0,0],
                "anchor": "top left",
                "layer":  0
            },
            "visible":  True,
            "children": {}
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    def __init__(self, data=node_base_data, parent=None):
        super().__init__(data,parent)
        self.treechildren = {}
        self.revealed     = []
    
    def _rlayer(self, data, pos=[0,0], layer = 0):
        id        = 0
        _pos      = pos.copy()
        for i in data:
            _have_kid = "v " if len(data[i]) else ""
            self.screen.render(
                text    = f"{'| '*layer}{_have_kid}{i}",
                pos     = _pos,
                anchor  = "",
                layer   = 10+id,
                blit_in = self.window_id
            )
            id      += 1
            _pos[1] += 25
            if i in self.revealed:
                _pos     = self._rlayer(data[i], _pos, layer+1)
        return _pos

    def update(self, delta):
        super().update(delta)
        # TBA
        self.treechildren = self.properties["children"]
        self.revealed     = []
        
        if self.visible:
            self._rlayer(self.treechildren, self.runtime_data["rendererpos"].copy())