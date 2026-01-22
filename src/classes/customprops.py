# Import libraries & components
import json, pyglet    as pg, sys
from classes.locals    import *
from typing_extensions import *
from typing            import *

# Variables
_screenc_cache = {}

# Classes
@disjoint_base
class _export:
    def __init__(self, type_=None, default=None, hint=None, fget=None, fset=None):
        self.type    = type_
        self.default = default
        self.hint    = hint
        self.fget    = fget
        self.fset    = fset

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.fget:
            return self.fget(instance)
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        if self.fset:
            return self.fset(instance, value)
        instance.__dict__[self.name] = value

    def getter(self, fget):
        self.fget = fget
        return self

    def setter(self, fset):
        self.fset = fset
        return self

def export(default=None, type_=None, hint=None):
    """
    Use this class to expose a value as a property in the editor.
    This class is similar to the `property` class in Python.
    
    "Wait a sec, this isn't a class!" You might be saying, well,
    this is a decorator to make the `_export` class, and do you
    really wanna type in `export.set_metadata(..)` every time you
    wanna make an export property instead of just `@export(..)`?
    
    Args:
        default: The default value to use.
        type: The name of the type that the value should be (int, str, list, bool...)
        hint: How to display this property in the editor (int, float, int/float, float/int, str, file_path/xxx, color, slider, font, bool)
    """
    def wrapper(func):
        return _export(
            fget    = func,
            default = default,
            type_   = type_,
            hint    = hint,
        )
    return wrapper

class _exportmeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Start with parent's properties
        props = {}
        for base in reversed(bases):
            if hasattr(base, "_properties"):
                props.update(base._properties)

        # Add properties in this class
        for key, value in namespace.items():
            if isinstance(value, _export):
                props[key] = {
                    "default": value.default,
                    "type": value.type,
                    "hint": value.hint,
                    "getter": value.fget,
                    "setter": value.fset
                }

        cls._properties = props
        return cls

class WindowProperties:
    maxsize      : list = [0,0]
    minsize      : list = [0,0]
    color        : list = [0,0,0]
    resizable    : bool = False
    antialiasing : bool = False
    vsize        : list = [0,0]
    icofile      : str  = ""

class GameData:
    def __init__(self, settings="settings.json", is_file = True):
        #### Settings file related
        ### Load settings
        if is_file:
            self.file_data = json.loads(open(settings).read())
        else:
            self.file_data = settings

        ### Get data about what project to use
        self.metadata     = self.file_data["project"]

        ## Get project itself
        self.project_file = self.metadata["file"].replace("\\", "/")
        self.project_dir  = self.metadata["dir"].replace("\\", "/")
        
        # Check if arguments decide otherwise ("-file ...", "-dir ...")
        words = sys.argv
        wrid  = 0
        for current in words:
            try:
                after  = words[wrid+1]
                before = words[wrid-1]
            except:
                after  = None
                before = None
            
            if current.startswith("-"):
                if after == None:
                    wrid += 1
                elif current == "-dir":
                    self.project_dir  = after.replace("\\", "/")
                elif current == "-file":
                    self.project_file = after.replace("\\", "/")
            
            wrid += 1

        if self.project_dir == USE_GAME_PARENT:
            self.project_dir = "/".join(self.project_file.split("/")[:-1])
        self.project_data = json.loads(open(self.project_file).read())

        #### Project file related
        # Get basic metadata
        self.name        = self.project_data["name"]
        self.version     = self.project_data["version"]["app"]
        self.version_ekl = self.project_data["version"]["ekl"]

        # Initialize window properties
        self.win              = WindowProperties()
        self.win.vsize        = self.project_data["viewport"]["size"]
        self.win.color        = self.project_data["viewport"]["color"]
        self.win.resizable    = self.project_data["viewport"]["resizable"]
        self.win.minsize      = self.project_data["viewport"]["minsize"]
        self.win.maxsize      = self.project_data["viewport"]["maxsize"]
        self.win.icofile      = self.project_data["viewport"]["icon_file"]
        self.win.antialiasing = self.project_data["behavior"]["antialiasing"]

        # Text-related
        self.fonts   = self.project_data["behavior"]["fonts"]
        self.langdir = self.project_data["language"]["dir"]

        # Get scenes info
        self.master_scene  = self.project_data["scenes"]["master"]
        self.loading_scene = self.project_data["scenes"]["loading"]

class Transform:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._w = 10
        self._h = 10

        self._flip_w = 0
        self._flip_h = 0
        
        self._offset_x = 0
        self._offset_y = 0

        self._rotation = 0
        self.skew      = 0
        self._alpha    = 255
        self._anchor   = "top left"
        self.scroll    = [0,0]
        self.visible   = True
        
        self._scale_x = 1
        self._scale_y = 1

        self._window_size = [0,0]
    
    # Getters
    @property
    def anchor(self): return self._anchor

    @property
    def x(self): return self._x - self._offset_x
    @property
    def y(self): return self._y - self._offset_y

    @property
    def scale_x(self): return self._scale_x
    @property
    def scale_y(self): return self._scale_y
    @property
    def scale(self):   return [self.scale_x, self.scale_y]
    
    @property
    def w(self): return self._w * self._scale_x
    @property
    def h(self): return self._h * self._scale_y
    
    @property
    def rect(self): return [self.x,self.y,self.w,self.h]
    @property
    def position(self):  return [self.x,self.y]
    @property
    def tsize(self):  return [self.w,self.h]

    @property
    def rotation(self): return self._rotation
    
    @property
    def alpha(self): return round(self._alpha)

    @property
    def flip_w(self): return self._flip_w
    @property
    def flip_h(self): return self._flip_h

    # Setters
    @flip_w.setter
    def flip_w(self, val): self._flip_w = val
    @flip_h.setter
    def flip_h(self, val): self._flip_h = val
    
    @alpha.setter
    def alpha(self, value):
        self._alpha = value
        self._set_alpha(value)
    
    @x.setter
    def x(self, value):
        self._x = value + self._offset_x
        self._set_pos(self._x,self._y)
    @y.setter
    def y(self, value):
        self._y = value + self._offset_y
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
    
    @scale_x.setter
    def scale_x(self, value):
        if self._scale_x == value: return
        self._scale_x = value
        self._set_scale(self.scale_x, self.scale_y)
        self._set_size(self.w, self.h)
    @scale_y.setter
    def scale_y(self, value):
        if self._scale_y == value: return
        self._scale_y = value
        self._set_scale(self.scale_x, self.scale_y)
        self._set_size(self.w, self.h)
    @scale.setter
    def scale(self, value):
        self.scale_x, self.scale_y = value
    
    # Visual functions.
    def _set_pos(self,   x,y):
        pass
    def _set_scale(self, x,y):
        pass
    def _set_rot(self,   deg):
        pass
    def _set_alpha(self, deg):
        pass
    def _set_size(self,  w,h):
        # This is affected by scaling
        pass
    
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
        self.x,self.y,self.w,self.h = value
    @position.setter
    def position(self, value : list[int,int]): self.x,self.y = value
    @tsize.setter
    def tsize(self, value : list[int,int]): self.w,self.h = value

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._set_rot(value)
    
    ## Functions
    def _turn_object_into_transform_property(self):
        transprop = {
            "position": self.position,
            "scale":    self.scale,
            "alpha":    self.alpha,
            "skew":     self.skew,
            "rotation": self.rotation,
            "anchor":   self.anchor,
            "scroll":   self.scroll,
            "visible":  self.visible,
            "tsize":    self.tsize
        }
        return transprop
    
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
    
    def into_screen_coords(self, window_size : list[int,int] = [480,480]):
        anchor = self.anchor
        cid    = f"{self.position}{window_size}{self.tsize}{anchor}"
        if cid in _screenc_cache:
            return _screenc_cache[cid]
        x        = 0
        y        = 0
        if "right"      in anchor:
            x = window_size[0] - self.w - self.x
        else:
            x = self.x
        if "top" in anchor:
            y = window_size[1] - self.h - self.y
        else:
            y = self.y
        if "centerx"    in anchor:
            x = (window_size[0]/2) - (self.w/2) + self.x
        if "centery"    in anchor:
            y = (window_size[1]/2) - (self.h/2) + self.y
        _screenc_cache[cid] = [x,y]
        return [x,y]
    
    def get_half_size(self):
        return [self.w/2,self.h/2]
    def get_quarter_size(self):
        return [self.w/4,self.h/4]
    
    def new(pos : position, surface = None, scale = [1,1], opacity = 255, layer = 0, rotation = 0, anchor = "", scroll = [0,0], visible = True, skew = 0):
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

class Mouse:
    pos      = [0,0]
    dpos     = [0,0]
    scroll   = 0           # 1 is up, -1 is down
    buttons  = [0,0,0,0,0] # Index 0 is ignored
    paths    = []          # List of filepaths

class Keyboard:
    modifiers = 0
    pressed   = {}
    held      = {}

class Language:
    def __init__(self, file="res://data/foobar.json"):
        self.load_lang(file)
    
    @property
    def properties(self):  return self._file["properties"]
    @property
    def entries(self):     return self._file["entries"]
    @property
    def name(self):        return self.properties["name"]
    @property
    def description(self): return self.properties["description"]
    @property
    def base(self):        return self.properties["base"]
    
    def load_lang(self,file):
        import classes.singleton as engine
        self._file = engine.loader.load(file)
        if self._file["properties"]["base"]:
            _base = Language(self._file["properties"]["base"])
            for i in _base.entries:
                if not i in self.entries:
                    self.entries[i] = _base.entries[i]
    
    def get(self, entry):
        return self.entries.get(entry, entry)

class Color:
    def __init__(self, r=0,g=0,b=0,a=255):
        self._r = r
        self._g = g
        self._b = b
        self._a = a
    def color_as_tuple(self): return (self.r, self.g, self.b, self.a)
    def color_as_list(self):  return [self.r, self.g, self.b, self.a]

    @property
    def r(self): return self._r
    @property
    def g(self): return self._g
    @property
    def b(self): return self._b
    @property
    def a(self): return self._a

    @r.setter
    def r(self, value):
        self._r = int(value)
        self._update_color(*self.color_as_list())
    @g.setter
    def g(self, value):
        self._g = int(value)
        self._update_color(*self.color_as_list())
    @b.setter
    def b(self, value):
        self._b = int(value)
        self._update_color(*self.color_as_list())
    @a.setter
    def a(self, value):
        self._a = int(value)
        self._update_color(*self.color_as_list())
    
    def _update_color(self, r,g,b,a):
        return

    @property
    def rgb(self):
        """RGBA color value as a list. Read-write.
        
        Due to Python limitations, this can only be modified by doing `self.rgb = ...` and not `self.rgb[X] = ...`."""
        return self.color_as_list()
    @rgb.setter
    def rgb(self, rgbv):
        self._r, self._g, self._b = rgbv
        if len(rgbv) > 3:
            self._a = rgbv[3]
        self._update_color(*self.color_as_list())