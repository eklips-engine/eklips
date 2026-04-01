## Import libraries
import pyglet                     as pg
from classes.resources.tileset    import *
from classes.nodes.gui.canvasitem import *

## XXX implement rendering and collision logic
class Tilemap(CanvasItem):
    _isblittable                                = True
    citem : pg.graphics.vertexdomain.VertexList = None

    ## Exported
    @export({}, "dict", "rsc/Tileset")
    def tileset(self) -> Tileset:
        return self._tileset

    @tileset.setter
    def tileset(self, value):
        self._tileset = engine.loader.load(value)
        self._rebuild()

    @export({}, "dict", "tiles")
    def tiles(self):
        return self._tiles

    @tiles.setter
    def tiles(self, value: dict):
        self._tiles = value
        self._rebuild()

    ## Init
    def __init__(self, properties={}, parent=None):
        self._tiles             = {}
        self._tileset : Tileset = None
        self._latestid          = 0

        self._vertices = []
        self._count    = 0

        super().__init__(properties, parent)
        self._make_new_item()
    
    ## VertexList Management
    def _make_new_item(self):
        if self.citem:
            self.citem.delete()
        if not self.tileset or not self.tiles:
            self.citem = None
            return

        self._drawing_bid = self.viewport.add_batch()
    
    def _rebuild(self):
        if self._tileset == None or not self._tiles:
            self._count = 0
            if self.citem:
                self.citem.resize(0)
            return
        
        gw, gh = self._tileset.grid_size

    def _handle_collisions(self):
        return
    def draw(self):
        return

    def update(self):
        super().update()
        self._handle_collisions()
        self.draw()