# Import singleton
import pygame
from pyglet.image import *

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

    def flip(self, flip_w, flip_h, no_cache=False) -> Texture:
        fid = f"{flip_w}{flip_h}"
        if not fid in self._flipimgcache or no_cache:
            texture = super().get_texture()
            result  = texture.get_transform(flip_w, flip_h, 0)

            self._flipimgcache[fid] = result
            return result
        return self._flipimgcache[fid]

# Functions
def cnvsrfekl(srf : pygame.Surface) -> EklImage:
    """Convert a Pygame surface to an Eklips Image."""
    gw = srf.get_width()
    gh = srf.get_height()

    return EklImage(
        gw,
        gh,
        "RGBA",
        srf.get_buffer(),
        -4 * gw
    )

def cnveklimg(pgimg : AbstractImage) -> EklImage:
    """Convert a Pyglet Image to an Eklips Image."""
    pgtxt = pgimg.get_texture()
    return EklImage(
        pgimg.width,
        pgimg.height,
        "RGBA",
        pgtxt.get_image_data().get_bytes()
    )