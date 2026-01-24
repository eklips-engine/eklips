# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.node  import *
from classes.customprops import *

# Variables
base_transform = {
    "position": [0,0],
    "tsize":    [0,0],
    "scale":    [1,1],
    "scroll":   [0,0],

    "rotation": 0,
    "alpha":    255,
    "anchor":   "top left",
    "visible":  True,
    "skew":     0
}

# Classes
class CanvasItem(Node, Transform):
    """
    A Canvas Node.
    
    This is a Node that has properties for transformation,
    and is meant for rendering items in the window.

    (NOTE: The reason why `tsize` is called that because
    anytree's NodeMixin uses a size property..)
    """
    _can_check_layer                            = True
    _isdisplayobject                            = False
    _drawing_bid : int                          = 0
    _drawing_vid : int                          = 0
    _drawing_wid : int                          = 0
    _sprite_id   : int                          = 0
    sprite       : pg.sprite.Sprite             = None
    _imagesid    : int                          = 0
    _images      : dict[pg.image.AbstractImage] = {}
    _image       : pg.image.AbstractImage       = None
    _ignore_size_if_drawing                     = False

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        self._image = value
        if self.sprite:
            self.sprite.image = value
    
    @export([False, False], "list", "vector2/wh")
    def flip(self):
        return [self.flip_w, self.flip_h]
    @flip.setter
    def flip(self, value : list):
        self.flip_w, self.flip_h = value

    def __init__(self, properties={}, parent = None, children=None):
        engine.Transform.__init__(self)
        super().__init__(properties, parent, children)

        if self.parent:
            self._drawing_wid = self.parent.get("_drawing_wid", MAIN_WINDOW)
            self._drawing_vid = self.parent.get("_drawing_vid", MAIN_WINDOW)
            self._drawing_bid = self.parent.get("_drawing_bid", MAIN_WINDOW)
        else:
            self._drawing_wid = MAIN_WINDOW
            self._drawing_vid = MAIN_VIEWPORT
            self._drawing_bid = MAIN_BATCH
        
        self._imgflip = [False, False]
        self.batch    = engine.display.get_batch_from_window(self._drawing_wid, self._drawing_vid, self._drawing_bid)

    @export(base_transform, "dict", "transform")
    def transform(self):
        return self._turn_object_into_transform_property()
    @transform.setter
    def transform(self, value):
        self._convert_transform_property_into_object(value)

    @export(MAIN_WINDOW,   "int", "windowid")
    def window_id(self):
        """ID of the Window `window_id` to draw to."""
        return self._drawing_wid
    @window_id.setter
    def window_id(self, value):
        if self._isdisplayobject:
            return
        if self.sprite:
            self._remove_sprite()
        self._drawing_wid = value
        self._refresh_sprite()
    @export(MAIN_VIEWPORT, "int", "viewportid")
    def viewport_id(self):
        """ID of the viewport in Window `window_id` to draw to."""
        return self._drawing_vid
    @viewport_id.setter
    def viewport_id(self, value):
        if self._isdisplayobject:
            return
        if self.sprite:
            self._remove_sprite()
        self._drawing_vid = value
        self._refresh_sprite()
    
    @export(MAIN_BATCH,    "int", "batchid")
    def batch_id(self):
        """ID of the batch in Viewport `viewport_id` to use."""
        return self._drawing_vid
    @batch_id.setter
    def batch_id(self, value):
        if self._isdisplayobject:
            return
        if self.sprite:
            self._remove_sprite()
        self._drawing_bid = value
        self._refresh_sprite()

    def _refresh_sprite(self):
        if self.sprite:
            self._remove_sprite()
        self._make_new_sprite()
        self.batch = engine.display.get_batch_from_window(self.window_id, self.viewport_id, self.batch_id)
    
    def draw(self, image):
        """Draw the CanvasItem. This is usually called automatically."""
        if image:
            if image != self.sprite.image:
                self.sprite.image = image
            self.w, self.h = image.width, image.height
            self._draw()

    def _set_pos(self, x, y):
        if not self.sprite:
            return
        self.sprite.x = x
        self.sprite.y = y
    def _set_scale(self, x, y):
        if not self.sprite:
            return
        self.sprite.scale_x = x
        self.sprite.scale_y = y  
    def _set_rot(self, deg):
        if not self.sprite:
            return
        self.sprite.rotation = deg
    def _set_alpha(self, deg):
        if not self.sprite:
            return
        self.sprite.opacity = round(deg)
        
    def _draw(self):
        """Draw the Sprite"""
        return engine.display.blit(
            transform   = self,
            window_id   = self.window_id,
            viewport_id = self.viewport_id,
            sprite      = self.sprite
        )

    def _get_viewport(self) -> ui.Viewport:
        """Get the Viewport that the CanvasItem will be drawn to."""
        viewport : ui.Viewport = engine.display.get_viewport_from_window(
            self.window_id,
            self.viewport_id
        )
        return viewport
    def _remove_sprite(self):
        if not self.sprite and not engine.debug.sprite_always_visible:
            return
        viewport = self._get_viewport()
        viewport._deallocate_sprite(self._sprite_id)
        self.sprite = None
    def _make_new_sprite(self):
        """Request a new Item from the Viewport to use."""
        if self.sprite:
            self._remove_sprite()
        viewport = self._get_viewport()
        self.sprite, self._sprite_id = viewport._allocate_sprite(self._drawing_bid)
    
    def _free(self):
        self._remove_sprite()
        super()._free()
    
    def update(self):
        super().update()
        if self.get_if_mouse_hovering():
            self.call_signal("_hover")
            if engine.mouse.buttons[engine.MOUSE_LEFT]:
                self.call_signal("_clicked")
    
    def get_if_mouse_hovering(self) -> bool:
        """Returns true if the mouse is hovering over self."""
        mpos     = engine.mouse.pos
        viewport = self._get_viewport()
        if not viewport:
            return
        x,  y    = self.into_screen_coords(viewport.tsize)
        vx, vy   = viewport.into_screen_coords()
        is_it  = (
            mpos[0] >= ((x + vx - viewport.cam.x) * viewport.cam.zoom)                                and
            mpos[0] <= ((x + vx - viewport.cam.x) * viewport.cam.zoom) + (self.w * viewport.cam.zoom) and
            mpos[1] >= ((y + vy - viewport.cam.y) * viewport.cam.zoom)                                and
            mpos[1] <= ((y + vy - viewport.cam.y) * viewport.cam.zoom) + (self.h * viewport.cam.zoom)
        )
            
        return is_it