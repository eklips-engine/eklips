# Import libraries
import pyglet as pg
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

    (NOTE: This node does not draw on its own. Use Sprite for that instead.)
    """
    _relativity_pos                             = True
    _iscitem                                    = True 
    _isdisplayobject                            = False
    _isblittable                                = False # If class is meant to blit CItem
    _drawing_bid : int                          = 0    
    _drawing_vid : int                          = 0    
    _drawing_wid : int                          = 0    
    citem        : pg.sprite.Sprite             = None 
    _imagesid    : int                          = 0    
    _images      : list[pg.image.AbstractImage] = {}   
    _image       : pg.image.AbstractImage       = None 
    _ignore_size_if_drawing                     = False

    ## Properties
    @property
    def viewport(self):
        if not hasattr(self, "_cached_viewport"):
            self._cached_viewport = engine.display.get_viewport_from_window(self.window_id, self.viewport_id)
        return self._cached_viewport
    @property
    def batch(self):
        if not hasattr(self, "_cached_batch"):
            self._cached_batch = engine.display.get_batch_from_window(self.window_id, self.viewport_id, self.batch_id)
        return self._cached_batch
    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        self._image    = value
        self.w, self.h = value.width, value.height
        if self.citem:
            self.citem.image = value
            self._set_anchors()
            self._set_flip(*self.flip)

    ## Init
    def __init__(self, properties={}, parent = None):
        engine.Transform.__init__(self)
        super().__init__(properties, parent)

        self._image = None

        if self.parent:
            self._drawing_wid = self.parent.get("_drawing_wid", MAIN_WINDOW)
            self._drawing_vid = self.parent.get("_drawing_vid", MAIN_VIEWPORT)
            self._drawing_bid = self.parent.get("_drawing_bid", MAIN_BATCH)
        else:
            self._drawing_wid = MAIN_WINDOW
            self._drawing_vid = MAIN_VIEWPORT
            self._drawing_bid = MAIN_BATCH
        
        self._imgflip = [False, False]
    
    ## Exported properties
    @export([False, False], "list", "vector2/wh")
    def flip(self):
        return [self.flip_w, self.flip_h]
    @flip.setter
    def flip(self, value : list):
        self._flip_w = value[0]
        self.flip_h  = value[1]
    @export(base_transform, "dict", "transform")
    def transform(self):
        return self._turn_object_into_transform_property()
    @transform.setter
    def transform(self, value):
        if self._isblittable:
            self._make_new_item()
        self._convert_transform_property_into_object(value)
    
    def _update_drawing_ids(self, attr, value):
        if self._isdisplayobject:
            return
        if self.citem:
            self._remove_item()
        setattr(self, attr, value)
        self._make_new_item()
    @export(MAIN_WINDOW, "int", "windowid")
    def window_id(self): return self._drawing_wid
    @window_id.setter
    def window_id(self, value): self._update_drawing_ids("_drawing_wid", value)
    @export(MAIN_VIEWPORT, "int", "viewportid")
    def viewport_id(self): return self._drawing_vid
    @viewport_id.setter
    def viewport_id(self, value): self._update_drawing_ids("_drawing_vid", value)
    @export(MAIN_BATCH, "int", "batchid")
    def batch_id(self): return self._drawing_bid
    @batch_id.setter
    def batch_id(self, value): self._update_drawing_ids("_drawing_bid", value)

    ## Drawing related
    def draw(self):
        """Draw the CanvasItem. This is usually called automatically."""
        if self.visible and self.viewport.is_onscreen(self) and self.citem:
            x, y         = self.into_screen_coords(self.viewport.tsize)
            self.citem.x = x + (self.citem.image.anchor_x * self.scale_x)
            self.citem.y = y + (self.citem.image.anchor_y * self.scale_y)
            
            self.citem.visible = self.visible
        else:
            self.citem.visible = False

    ## Transform related
    def _set_layer(self, val):
        if self.citem:
            self.citem.group = engine.ui.request_group(val)
    def _set_flip(self, w, h):
        if self.citem:
            if w: self.citem.scale_x = -self.scale_x
            else: self.citem.scale_x = self.scale_x

            if h: self.citem.scale_y = -self.scale_y
            else: self.citem.scale_y = self.scale_y
    def _set_anchors(self):
        self.citem.image.anchor_x = self._w // 2
        self.citem.image.anchor_y = self._h // 2
        self.citem._update_position()
    def _set_size(self, w, h):
        if self.image:
            self._w, self._h = self.image.width, self.image.height
    def _set_scale(self, x, y):
        if self.citem:
            self._set_flip(self.flip_w, self.flip_h)
    def _set_rot(self, deg):
        if self.citem:
            self.citem.rotation = deg
    def _set_visible(self, val):
        if self.citem:
            self.citem.visible = val
    def _set_alpha(self, deg):
        if self.citem:
            self.citem.opacity = round(deg)

    def _get_viewport(self) -> ui.Viewport:
        """Get the Viewport that the CanvasItem will be drawn to."""
        viewport : ui.Viewport = engine.display.get_viewport_from_window(
            self.window_id,
            self.viewport_id
        )
        return viewport
    def _get_window(self) -> ui.EklWindow:
        """Get the Window that the CanvasItem will be drawn to."""
        window : ui.EklWindow = engine.display.get_window(
            self.window_id
        )
        return window
    
    ## CItem managing
    def _remove_item(self):
        if self.citem:
            self.citem.delete()
            self.citem = None
    def _make_new_item(self):
        if self.citem:
            self._remove_item()
        if not self.image:
            self._image    = engine.loader.load("root://_assets/error.png")
        self.citem         = pg.sprite.Sprite(img=self.image, batch=self.batch)
        self.citem.visible = False
    def _refresh_item(self):
        if self.citem:
            self._remove_item()
        self._make_new_item()
    def _free(self):
        self._remove_item()
        super()._free()
    
    ## Update
    def _update_relativity(self):
        if self.parent and self.parent.get("_iscitem", False) and self._relativity_pos:
            if self.parent.get("_isdisplayobject", False):
                self._offset_x, self._offset_y = self.parent.into_screen_coords(False)
            else:
                self._offset_x, self._offset_y = self.parent.into_screen_coords(self.viewport.tsize, False)
        else:
            self._offset_x = self._offset_y = 0
    
    def update(self):
        super().update()

        ## Update relativity
        self._update_relativity()
        
        ## Reset CITEM if it's fucked.
        if getattr(self.batch, "invalid", False) and self.citem and not self.viewport._refreshing:
            self._remove_item()
            del self._cached_batch
            self._make_new_item()
            self._convert_transform_property_into_object(self.transform)
        
        ## Check for hovering
        if self.get_if_mouse_hovering():
            self.call_signal("_hover")
            if engine.mouse.buttons[engine.MOUSE_LEFT]:
                self.call_signal("_held")
            if engine.mouse.just_clicked[engine.MOUSE_LEFT]:
                self.call_signal("_clicked")
    
    ## Convenience functions for user
    def get_if_mouse_hovering(self) -> bool:
        """Returns true if the mouse is hovering over self."""
        if not self.viewport:
            return
        if not self.viewport.is_onscreen(self):
            return
        
        ## Get things
        mpos   = engine.mouse.pos
        x,  y  = self.into_screen_coords(self.viewport.tsize)
        vx, vy = self.viewport.into_screen_coords()

        ## Apply viewport position into x and y
        x += vx - self.viewport.cam.x
        y += vy - self.viewport.cam.y

        ## Apply viewport zooming
        x *= self.viewport.cam.zoom
        y *= self.viewport.cam.zoom
        w  = self.w * self.viewport.cam.zoom
        h  = self.h * self.viewport.cam.zoom

        ## Result
        return (
            mpos[0] >= x     and
            mpos[0] <= x + w and
            mpos[1] >= y     and
            mpos[1] <= y + h
        )