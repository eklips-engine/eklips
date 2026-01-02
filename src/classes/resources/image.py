# Import singleton
from pyglet.image        import *

# Classes
class EklImage(ImageData):
    def __init__(self, width, height, fmt, data, pitch = None):
        super().__init__(width, height, fmt, data, pitch)
        self._flipimgcache = {}
    
    def get_texture(self, rectangle = False):
        texture               = super().get_texture()
        texture._flipimgcache = self._flipimgcache
        texture.flip          = self.flip
        return texture

    def flip(self, flip_w, flip_h):
        fid = f"{flip_w}{flip_h}"
        if not fid in self._flipimgcache:
            texture = super().get_texture()
            self._flipimgcache[fid] = texture.get_transform(flip_w, flip_h, 0)
        return self._flipimgcache[fid]

# Functions
def cnveklimg(pgimg : AbstractImage) -> EklImage:
    pgtxt = pgimg.get_texture()
    return EklImage(
        pgimg.width,
        pgimg.height,
        "RGBA",
        pgtxt.get_image_data().get_bytes()
    )