# Import libraries
import pyglet as pg
from classes import ui

# Import inherited
from classes.nodes.gui.sprite import *

# Classes
class Parallax(Sprite):
    """
    A 2D scrolling Sprite.
    
    XXX
    """

    def __init__(self, properties=..., parent=None, children=None):
        super().__init__(properties, parent, children)

        self._speed      = 150.0
        self._imgoffsetx = 0 # How many pixels to offset the image, it's named this for
                             # lack of a better name

    @export(150.0,"float","slider")
    def speed(self):
        """How fast the Parallax should be.

        The reason why the default value is so high
        because on 1x speed, it takes 1 second to
        move 1 pixel.

        You can make this value negative to go backwards.
        """
        return self._speed
    @speed.setter
    def speed(self, value): self._speed = value

    def update(self):
        self._imgoffsetx += engine.delta * self.speed
        super().update()
    
    def _draw(self):
        # Draw the Sprite
        self.sprite.image = self.image

        return engine.display.blit(
            transform   = self,
            window_id   = self._drawing_wid,
            viewport_id = self._drawing_vid,
            sprite      = self.sprite,
            region      = [
                self._imgoffsetx % self.image.width, # X
                0,                                               # Y
                self.image.width,                                # W
                self.image.height                                # H
            ]
        )