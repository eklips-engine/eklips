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
    ## A Canvas Node.
    
    This is a Node that has properties for transformation,
    and is meant for rendering items in the window.

    (NOTE: The reason why `tsize` is called that because
    anytree's NodeMixin uses a size property..)
    """
    _can_check_layer                            = True
    _drawing_bid : int                          = 0
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

    def __init__(self, properties={}, parent=None, children=None):
        engine.Transform.__init__(self)
        super().__init__(properties, parent, children)
        if self.parent:
            self._drawing_wid = self.parent._drawing_wid
        else:
            self._drawing_wid = MAIN_WINDOW
        self._imgflip         = [False, False]
        self._drawing_bid     = MAIN_BATCH

        self.batch = engine.display.get_batch_from_window(self._drawing_wid, self._drawing_bid)

    def _setup_properties(self):
        super()._setup_properties()
        self._convert_transform_property_into_object(self._properties_onready.get("transform", base_transform))
    
    def _convert_transform_property_into_object(self, value):
        self.position = value["position"]
        self.scale    = value["scale"]
        self.alpha    = value["alpha"]
        self.skew     = value["skew"]
        self.rotation = value["rotation"]
        self.anchor   = value["anchor"]
        self.scroll   = value["scroll"]
        self.visible  = value["visible"]
        self.tsize    = value["tsize"]
    
    def draw(self, image):
        """Draw the Node's image. This is usually called automatically."""
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
        if deg:
            self.sprite.image.anchor_x = self.w/4
            self.sprite.image.anchor_y = self.h/4 
    def _set_alpha(self, deg):
        if not self.sprite:
            return
        self.sprite.opacity = round(deg)
        
    def _draw(self):
        """Draw the Sprite"""
        return engine.display.blit(
            transform = self,
            window_id = self._drawing_wid,
            sprite    = self.sprite
        )

    def _get_viewport(self) -> ui.Viewport:
        """Get the Viewport that the CanvasItem will be drawn to."""
        viewport : ui.Viewport = engine.display.get_viewport_from_window(
            self._drawing_wid,
            MAIN_VIEWPORT
        )
        return viewport
    def _remove_sprite(self):
        if not self.sprite and not engine.debug.sprite_always_visible:
            return
        viewport = self._get_viewport()
        viewport._deallocate_sprite(self._sprite_id)
        self.sprite = None
    def _make_new_sprite(self):
        """Request a new Sprite from the Viewport to use."""
        if self.sprite:
            self._remove_sprite()
        viewport                     = self._get_viewport()
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
        x,y    = self.into_screen_coords(viewport.size)
        is_it  = (
            mpos[0] >= x          and
            mpos[0] <= x + self.w and
            mpos[1] >= y          and
            mpos[1] <= y + self.h
        )
        
        return is_it