# Import singleton
import pyglet as pg
from classes.resources.resource import *
from classes.customprops        import *

# Classes
class Tileset(Resource):
    """
    Tileset
    
    XXX
    """
    _can_init_script = False

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, img : pg.image.ImageData):
        self._image   = img
        self.refresh_tiles()
    
    @export(None,"str","file_path/image")
    def image_path(self):
        """Filepath of the attached Image. Setting this value loads and sets the imagepath as the Tileset's image."""
        return self._imagepath
    @image_path.setter
    def image_path(self, value):
        if not value: return
        self._imagepath = value
        self.image      = engine.loader.load(value)
    
    @export({},"dict","sprites")
    def tiles(self) -> dict:
        return self._sprites
    @tiles.setter
    def tiles(self, value : dict):
        self._sprites = {}
        for i in value:
            self.add_tile(*value[i], dont_refresh=True)
        self.refresh_tiles()
    
    def add_tile(self, sx, sy, sw, sh, hx, hy, hw, hh, dont_refresh=False):
        self._sprites[len(self._sprites)] = [sx, sy, sw, sh, hx, hy, hw, hh, None]
        if not dont_refresh:
            self.refresh_tiles()
    
    def refresh_tiles(self):
        ogsprites     = self._sprites.copy()
        for i in ogsprites: #[SX, SY, SW, SH, HX, HY, HW, HH, img if loaded]
            self._sprites[i][8] = self.image.get_region(*self._sprites[i][:4])

    def __init__(self, properties={}):
        self._image     = None
        self._imagepath = None
        self._sprites   = {}
        super().__init__(properties)