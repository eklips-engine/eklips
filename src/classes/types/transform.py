## Import libraries & components
from typing            import *
from classes.locals    import *
from typing_extensions import *

## Classes
class Transform:
    """A transformation object with width, height, x, y, z, scale, flip, etc..."""

    def __repr__(self):
        return f"{self.__class__.__name__}(position={self.position}, size={self.size})"
    
    def __init__(self):
        ## Coords and size
        self._x = 0
        self._y = 0
        self._z = 0
        self._w = 10
        self._h = 10

        ## Flip
        self._flip_w = 0
        self._flip_h = 0
        
        ## Offset
        self._offset_x = 0
        self._offset_y = 0

        ## Other properties
        self._rotation = 0
        self.skew      = 0
        self._alpha    = 255
        self._anchor   = "top left"
        self.scroll    = [0,0]
        self._visible  = True
        
        ## Scale
        self._scale_x = 1
        self._scale_y = 1

        ## Layer
        self._layer = 0

    ## Collision
    def _get_screen_aabb(self, viewport, parent_rect=None, ignore_camera=False):
        x, y = self.into_window_coords(viewport, parent_rect)
        cam  = viewport.cam
        if cam and not ignore_camera:
            x = (x - cam.x) * cam.zoom
            y = (y + cam.y) * cam.zoom
            return (
                x, x + self.w*cam.zoom,
                y, y + self.h*cam.zoom)
        return (
            x, x + self.w,
            y, y + self.h)
    def _get_aabb(self):
        return (
            self.x, self.x+self.w,
            self.y, self.y+self.h)
    def _aabbcheck(self, _aabb1, _aabb2):
        return (
            _aabb1[0] < _aabb2[1] and
            _aabb1[1] > _aabb2[0] and
            _aabb1[2] < _aabb2[3] and
            _aabb1[3] > _aabb2[2])
    def collides_ui_aabb(self, other : Self,
                         ctx_a=None, ctx_b=None):
        """
        Check if a Transform is colliding with another Transform in screen space using AABB.
        
        Args:
            other: The other Transform to check for collisions.
            ctx_a: The context for this Transform, which is a tuple like so: (viewport, parent_rect, ignore_camera).
            ctx_b: The same thing as `ctx_a` but for the `other` Transform.
            ignore_camera: Whether if to ignore the context's cameras."""
        _aabb1 = self._get_screen_aabb(*ctx_a)
        _aabb2 = other._get_screen_aabb(*ctx_b)

        return self._aabbcheck(_aabb1, _aabb2)
    def collides_aabb(self, other : Self):
        """
        Check if a Transform is colliding with another Transform in world space using AABB.
        
        Args:
            other: The other Transform to check for collisions."""
        _aabb1 = self._get_aabb()
        _aabb2 = other._get_aabb()

        return self._aabbcheck(_aabb1, _aabb2)
    
    ## Getters
    @property
    def visible(self):
        """If the Transform is visible. Read-write"""
        return self._visible
    @property
    def anchor(self):
        """The Transform's anchor (top, left, right, bottom). You can put multiple, too. Read-write"""
        return self._anchor
    @property
    def x(self):
        """The Transform's X. Read-write"""
        return self._x + self._offset_x
    @property
    def y(self):
        """The Transform's Y. Read-write"""
        return self._y + self._offset_y
    @property
    def z(self):
        """The Transform's Z. Read-write"""
        return self._z
    @property
    def layer(self):
        """The Transform's layer. Read-write"""
        return self._layer
    @property
    def scale_x(self):
        """The Transform's X scale. Read-write"""
        return self._scale_x
    @property
    def scale_y(self):
        """The Transform's Y scale. Read-write"""
        return self._scale_y
    @property
    def scale(self):
        """The Transform's scaling. Read-write"""
        return [self._scale_x, self._scale_y]
    @property
    def w(self):
        """The Transform's width. Read-write"""
        return round(self._w * self._scale_x)
    @property
    def h(self):
        """The Transform's height. Read-write"""
        return round(self._h * self._scale_y)
    @property
    def rect(self):
        """The Transform's AABB Rect (XYWH). Read-write"""
        return [self.x,self.y,self.w,self.h]
    @property
    def position(self):
        """The Transform's position. Read-write"""
        return [self.x,self.y]
    @property
    def size(self):
        """The Transform's size. Read-write"""
        return [self.w,self.h]
    @property
    def rotation(self):
        """The Transform's rotation. Read-write"""
        return self._rotation
    @property
    def alpha(self):
        """The Transform's opacity. Read-write"""
        return round(self._alpha)
    @property
    def flip_w(self):
        """If the Transform's flipped horizontaly. Read-write"""
        return self._flip_w
    @property
    def flip_h(self):
        """If the Transform's flipped vertically. Read-write"""
        return self._flip_h
    @property
    def flip(self):
        """The Transform's flip. Read-write"""
        return [self.flip_w,self.flip_h]

    ## Setters
    @layer.setter
    def layer(self, val):
        self._layer = val
        self._set_layer(val)
    @visible.setter
    def visible(self, val):
        self._visible = val
        self._set_visible(val)
    @flip_w.setter
    def flip_w(self, val):
        self._flip_w = val
        self._set_flip(*self.flip)
    @flip_h.setter
    def flip_h(self, val):
        self._flip_h = val
        self._set_flip(*self.flip)
    @flip.setter
    def flip(self, val):
        self._flip_w = val[0]
        self.flip_h  = val[1]
    @alpha.setter
    def alpha(self, value):
        self._alpha = value
        if value < 0: value = 0
        self._set_alpha(value)
    @x.setter
    def x(self, value):
        self._x = value
        self._set_pos(self._x,self._y)
    @y.setter
    def y(self, value):
        self._y = value
        self._set_pos(self._x,self._y)
    @z.setter
    def z(self, value):
        self._z = value
        self._set_pos(self._x,self._y)
    @anchor.setter
    def anchor(self, value):
        split_value  = value.split()
        new_value    = []
        for value in split_value:
            if value == "center":
                new_value.append("centerx")
                new_value.append("centery")
            else:
                new_value.append(value)
        
        self._anchor = " ".join(new_value).lower()
        self._set_pos(self._x, self._y)
    @scale_x.setter
    def scale_x(self, value):
        if self._scale_x == value: return
        self._scale_x = value
        self._set_scale(self.scale_x, self.scale_y)
    @scale_y.setter
    def scale_y(self, value):
        if self._scale_y == value: return
        self._scale_y = value
        self._set_scale(self.scale_x, self.scale_y)
    @scale.setter
    def scale(self, value):
        self._scale_x = value[0]
        self.scale_y  = value[1]
    @w.setter
    def w(self, value):
        if self._w == value: return
        self._w = value
        self._set_size(self.w,self.h)
    @h.setter
    def h(self, value):
        if self._h == value: return
        self._h = value
        self._set_size(self.w,self.h)
    @rect.setter
    def rect(self, value : list[int,int,int,int]):
        self.position = [value[0], value[1]]
        self.size     = [value[2], value[3]]
    @position.setter
    def position(self, value : list[int,int]):
        self._x = value[0] + self._offset_x
        self.y  = value[1]
    @size.setter
    def size(self, value : list[int,int]):
        if self.size == value: return
        self._w = value[0]
        self.h  = value[1]
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._set_rot(value)
    
    ## Visual functions.
    def _set_visible(self, val):
        pass
    def _set_pos(self,     x,y):
        pass
    def _set_scale(self,   x,y):
        pass
    def _set_rot(self,     deg):
        pass
    def _set_alpha(self,   deg):
        pass
    def _set_size(self,    w,h):
        # This is affected by scaling
        pass
    def _set_flip(self,    w,h):
        pass
    def _set_layer(self,   val):
        pass
    
    ## Helper functions for CanvasItems etc
    def _turn_object_into_transform_property(self):
        """Returns a dictionary of the Transform object's properties."""
        return {
            "position": self.position,
            "scale":    self.scale,
            "alpha":    self.alpha,
            "skew":     self.skew,
            "layer":    self.layer,
            "rotation": self.rotation,
            "anchor":   self.anchor,
            "scroll":   self.scroll,
            "visible":  self.visible,
            "size":     self.size
        }
    def _convert_transform_property_into_object(self, value):
        """Sets the Transform object's properties from a dictionary."""
        self.size      = value.get("size",    self.size)
        self.flip      = value.get("flip",     self.flip)
        self.position  = value.get("position", self.position)
        self.scale     = value.get("scale",    self.scale)
        self.alpha     = value.get("alpha",    self.alpha)
        self.skew      = value.get("skew",     self.skew)
        self.rotation  = value.get("rotation", self.rotation)
        self.anchor    = value.get("anchor",   self.anchor)
        self.scroll    = value.get("scroll",   self.scroll)
        self.layer     = value.get("layer",    self.layer)
        self.visible   = value.get("visible",  self.visible)
    
    def _calculate_anchors(self, parent_rect):
        anchor = self.anchor
        x      = parent_rect[0]
        y      = parent_rect[1]

        if "right" in anchor:
            x += parent_rect[2] - self.w - self.x
        elif "centerx" in anchor:
            x += (parent_rect[2]/2) - (self.w/2) + self.x
        else:
            x += self.x

        if "centery" in anchor:
            y += (parent_rect[3]/2) - (self.h/2) + self.y
        elif "top" in anchor:
            y += parent_rect[3] - self.h - self.y
        else:
            y += self.y

        return x, y
    def into_window_coords(self,
        viewport    : Self = None,
        drawing     : bool = False,
        parent_rect : list = None):
        """Get the position of the Transform object in the Window using the Transform's viewport.
        
        Args:
            viewport:    The Viewport itself.
            drawing:     If True, account for the image's anchor being on the center.
            parent_rect: If specified, will account the parent Transform for anchoring."""

        ## Fixup
        if parent_rect is None:
            parent_rect = (*viewport.position, *viewport.size)

        return self.into_viewport_coords(viewport, drawing, parent_rect)
    def into_viewport_coords(self,
        viewport    : Self = None,
        drawing     : bool = False,
        parent_rect : list = None):
        """Get the position of the Transform object in the Viewport.
        
        Args:
            viewport:    The Viewport itself.
            drawing:     If True, account for the image's anchor being on the center.
            parent_rect: If specified, will account the parent Transform for anchoring."""

        ## Fixup
        anchor          = self.anchor
        if parent_rect is None:
            parent_rect = (0,0, *viewport.size)
        
        ## Calculate pos
        x, y = self._calculate_anchors(parent_rect)
        
        ## Offset the position if `drawing` is True, implying the sprite
        ## has the anchor w/2,h/2 since.. All of them do, and you're not
        ## really supposed to make your own pyglet Sprite manually, just
        ## use the Sprite node.
        if drawing:
            x, y = self._offset_off_anchor(x, y)
        
        ## Return result
        return [x,y]
    def _offset_off_anchor(self, x, y, w=None, h=None):
        if w == None: w = self.w
        if h == None: h = self.h
        return x+(w // 2), y+(h // 2)
    
    ## New
    @classmethod
    def new(cls, pos : list, surface = None, scale = [1,1], opacity = 255, layer = 0, rotation = 0, anchor = "", scroll = [0,0], visible = True, skew = 0):
        transform_obj          = Transform()
        transform_obj.pos      = pos
        if surface:
            transform_obj.w    = surface.width
            transform_obj.h    = surface.height
        transform_obj.scale    = scale
        transform_obj.alpha    = opacity
        transform_obj.layer    = layer
        transform_obj.rotation = rotation
        transform_obj.anchor   = anchor
        transform_obj.scroll   = scroll
        transform_obj.skew     = skew
        transform_obj.visible  = visible
        return transform_obj
class RadianTransform(Transform):
    @property
    def rotation(self):
        """The Transform's rotation in regular degrees. Read-write"""
        return self._rotation
    @rotation.setter
    def rotation(self, val):
        self._rotation = val
        self._set_rot(val)
    @property
    def altrotation(self):
        """The Transform's rotation in Radians. Read-only"""
        return self._rotation*(math.pi/180)
class CameraTransform(RadianTransform):
    def __init__(self):
        super().__init__()
        self._zoom = 1
    
    @property
    def zoom(self):
        """The camera's zoom. Read-write"""
        return self._zoom
    @zoom.setter
    def zoom(self, val): self._zoom = val