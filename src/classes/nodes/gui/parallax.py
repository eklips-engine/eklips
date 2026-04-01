## Import libraries
import pyglet as pg
from classes.nodes.gui.sprite import *

## Classes
## XXX implement zoom stuff
class Parallax(Sprite):
    """
    A 2D scrolling Sprite.
    """
    _isblittable = True

    def __init__(self, properties=None, parent=None):
        if properties is None:
            properties = {}
        super().__init__(properties, parent)

        self._citemtr    = None
        self._citembl    = None
        self._citembr    = None
        self._speed      = 150.0
    
    ## Exports
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

    ## CItem and Transform
    def _set_alpha(self, deg):
        for s in [self.citem, self._citemtr, self._citembl, self._citembr]:
            if s:
                s.opacity = deg
    def _set_layer(self, val):
        super()._set_layer(val)
        self._citembl.group = self._citembr.group = self._citemtr.group = self.citem.group
    def _set_visible(self, val):
        for s in [self.citem, self._citemtr, self._citembl, self._citembr]:
            if s:
                s.visible = val
    def _set_rot(self, deg):
        return
    def _make_new_item(self):
        if self.citem:
            self._remove_item()
        if not self.image:
            self._image = engine.loader.load("root://_assets/error.png")
        self.citem      = pg.sprite.Sprite(img=self.image, batch=self.batch)
        self._citemtr   = pg.sprite.Sprite(img=self.image, batch=self.batch)
        self._citembl   = pg.sprite.Sprite(img=self.image, batch=self.batch)
        self._citembr   = pg.sprite.Sprite(img=self.image, batch=self.batch)
        self._set_anchors()
        self._set_visible(False)
    def _remove_item(self):
        self._switch_window()
        for s in [self.citem, self._citemtr, self._citembl, self._citembr]:
            if s:
                s.delete()
        self.citem = self._citemtr = self._citembl = self._citembr = None
    def _set_anchors(self):
        self.image.anchor_x = self.image.width  // 2
        self.image.anchor_y = self.image.height // 2
    
    ## Draw
    def draw(self):
        if self.visible and self.citem:
            zoom  = self.viewport.cam.zoom
            speed = self.speed / 25 + engine.ZDE_FIX

            cx,cy = round(self.viewport.cam.x)+ZDE_FIX,round(self.viewport.cam.y)+ZDE_FIX
            x,  y = cx-(abs(cx/speed%self.w)), cy-(cy/speed%self.h)
            #if engine.ineditor and not self._iseditortool:
            #    x = 0
            #    y = 0
            #
            
            self.citem.x    = self._citembl.x = x + (self.citem.image.anchor_x * self.scale_x)
            self.citem.y    = self._citemtr.y = y + (self.citem.image.anchor_y * self.scale_y)
            self._citemtr.x = self._citembr.x = self.citem.x + self.w
            self._citembr.y = self._citembl.y = self.citem.y + self.h
            
            self._set_visible(True)
        else:
            self._set_visible(False)