# Import libraries
import pygame, pyglet as pg, json, gc
from classes import ui

# Import inherited
from classes.nodes.node  import *
from classes.customprops import *

# Variables
base_transform = {
    "position": [0,0],
    "size":     [0,0],
    "scale":    [1,1],
    "scroll":   [0,0],

    "rotation": 0,
    "alpha":    255,
    "anchor":   "top left",
    "visible":  True,
    "skew":     0,
}

# Classes
class CanvasItem(Node, Transform):
    """
    ## A Canvas Node.
    
    This is a Node that has properties for transformation, and is meant for rendering items in the window.
    For Nodes in a 2D world, use Node2D.

    This has relativity only on the position.
    """
    _can_check_layer = True
    base_properties  = {
        "name":      "CanvasItem",
        "transform": base_transform,
        "script":    None
    }
    _sprite_id : int                          = 0
    sprite     : pg.sprite.Sprite             = None
    images     : list[pg.image.AbstractImage] = []
    image      : pg.image.AbstractImage       = None
    _canvas_layer                             = None
    _ignore_size_if_drawing                   = False
    is_layer                                  = False

    def _find_layer(self):
        while self.parent and not getattr(self.parent, "_is_layer", False):
            self.parent = getattr(self.parent, "parent", None)
        return self.parent

    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        self._find_layer()

        self.batch_id  = MAIN_BATCH
        self.window_id = MAIN_WINDOW

        self.batch = engine.display.get_batch_from_window(self.window_id, self.batch_id)

        engine.Transform.__init__(self)
        self._convert_transform_property_into_object(properties)
    
    def _convert_transform_property_into_object(self, properties):
        transform_property = properties.get("transform", base_transform)
        self.pos           = transform_property["position"]
        self.scale         = transform_property["scale"]
        self.alpha         = transform_property["alpha"]
        self.skew          = transform_property["skew"]
        self.rotation      = transform_property["rotation"]
        self.anchor        = transform_property["anchor"]
        self.scroll        = transform_property["scroll"]
        self.visible       = transform_property["visible"]
    
    def draw(self, image):
        if image:
            self.w, self.h = image.width, image.height
            self._draw(image)

    def _draw(self, image):
        return engine.display.blit(
            surface   = image,
            transform = self,
            window_id = self.window_id,
            sprite    = self.sprite,
            group     = self._canvas_layer
        )

    def _get_viewport(self) -> ui.Viewport:
        viewport : ui.Viewport = engine.display.get_viewport_from_window(
            self.window_id,
            MAIN_VIEWPORT
        )
        return viewport
    def _remove_sprite(self):
        if not self.sprite:
            return
        self._get_viewport().delete_sprite(self._sprite_id)
    def _make_new_sprite(self):
        if self.sprite:
            self._remove_sprite()
        viewport = self._get_viewport()
        self.sprite, self._sprite_id = viewport._allocate_sprite(self.batch_id)
    
    def _free(self):
        self._remove_sprite()
        super()._free()
    
    def update(self):
        super().update()
        if self.get_if_mouse_hovering():
            self.call_signal("_hover")
            if engine.mouse.clk[0]:
                self.call_signal("_clicked")
    
    def get_if_mouse_hovering(self) -> bool:
        mpos   = engine.mouse.pos
        window = engine.display.windows[self.window_id]["window"]
        if not window:
            return
        x,y    = self.into_screen_coords(window.size)
        is_it  = (
            mpos[0] < x  + self.w and
            mpos[0] + 20 > x      and
            mpos[1] < y  + self.h and
            mpos[1] + 20 > y
        )
        return is_it