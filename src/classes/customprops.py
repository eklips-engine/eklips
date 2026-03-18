# Import libraries & components
import json, pyglet      as pg, sys
import os
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
        hint: How to display this property in the editor (int, float, int/float, float/int, str, file_path/type, color, slider, font, bool, time, file_paths/type, vector2/ab, transform, windowid, viewportid, batchid)
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
    """Properties for the main Window."""
    maxsize      : list = [0,0]
    minsize      : list = [0,0]
    color        : list = BLACK
    resizable    : bool = False
    antialiasing : bool = False
    vsize        : list = [0,0]
    icofile      : str  = ""

class DebugConfig:
    """Debugging configuration."""
    _skipload  = True
    _freezload = False
    _enabled   = False
    _showfps   = True
    _nomercy   = False
    _showgraph = False
    _alwaysvis = False

    @property
    def sprite_always_visible(self):
        """True if sprites are always visible. Read-write."""
        return self._alwaysvis and self._enabled
    @sprite_always_visible.setter
    def sprite_always_visible(self,val): self._alwaysvis = val

    @property
    def skip_load(self):
        """True if the loading animation can be skipped. Read-write."""
        return self._skipload and self._enabled
    @skip_load.setter
    def skip_load(self,val): self._skipload = val

    @property
    def freeze_load(self):
        """True if the loading animation can be frozen. Read-write."""
        return self._freezload and self._enabled
    @freeze_load.setter
    def freeze_load(self,val): self._freezload = val

    @property
    def show_fps(self):
        """True if the engine can show the FPS. Read-write."""
        return self._showfps and self._enabled
    @show_fps.setter
    def show_fps(self,val): self._showfps = val

    @property
    def avoid_error_mercy(self):
        """True if the engine can be more error-prone. Read-write."""
        return self._nomercy and self._enabled
    @avoid_error_mercy.setter
    def avoid_error_mercy(self,val): self._nomercy = val
    
    @property
    def show_graph(self):
        """True if the engine can show a profiling graph. Read-write."""
        return self._showgraph and self._enabled
    @show_graph.setter
    def show_graph(self,val):
        self._showgraph = val

    @property
    def enabled(self):
        """True if debugging is enabled. Read-write."""
        return self._enabled
    @enabled.setter
    def enabled(self,val): self._enabled = val
    
class GameData:
    """Data about the running project."""
    
    #: The location of the game.json file being used.
    project_file = None
    #: The directory of the project that is running.
    project_dir  = None

    #: The project's version.
    version     = None
    #: The project's Eklips version.
    version_ekl = None
    
    #: The save folder.
    save_dir = None

    #: Main Window properties
    win = None

    #: List of fonts
    fonts = None

    #: The directory of all of the language files.
    langdir = None
    #: List of languages.
    langs   = None

    #: Dictionary of actions.
    actions = None

    #: The main scene.
    master_scene  = None
    #: The scene loaded at the start of the runtime. Can be used for a loading animation, etc..
    loading_scene = None

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
        self.project_file = str(self.metadata["file"]).replace("\\", "/")
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
        
        if os.path.isfile(self.project_file):
            self.project_data = json.loads(open(self.project_file).read())
        else:
            self.project_data = json.loads(open("_assets/no_game/game.json").read())
            self.project_dir  = "_assets/no_game"

        #### Project file related
        # Get basic metadata
        self.name        = self.project_data["name"]
        self.version     = self.project_data["version"]["app"]
        self.version_ekl = self.project_data["version"]["ekl"]
        
        # Make save directory
        self.save_dir    = f"{os.path.expanduser('~')}/Eklips Engine/{self.name}"
        os.makedirs(self.save_dir, exist_ok=True)

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
        self.langs   = self.project_data["language"]["langs"]
        self.langdir = self.project_data["language"]["dir"]
        self.actions = self.project_data["actions"]

        # Get scenes info
        self.master_scene  = self.project_data["scenes"]["master"]
        self.loading_scene = self.project_data["scenes"]["loading"]

class Transform:
    """A transformation object with width, height, x, y, z, scale, flip, etc..."""

    def __repr__(self):
        return f"{self.__class__.__name__}(position={self.position}, tsize={self.tsize})"
    
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
        self._visible  = True
        
        self._scale_x = 1
        self._scale_y = 1

        self._layer = 0

        self._window_size = [0,0]
    
    # Getters
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
        return [self.scale_x, self.scale_y]
    
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
        """The Transform's Rect (XYWH). Read-write"""
        return [self.x,self.y,self.w,self.h]
    @property
    def position(self):
        """The Transform's position. Read-write"""
        return [self.x,self.y]
    @property
    def tsize(self):
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

    # Setters
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
        self._set_alpha(value)
    
    @x.setter
    def x(self, value):
        self._x = value + self._offset_x
        self._set_pos(self._x,self._y)
    @y.setter
    def y(self, value):
        self._y = value + self._offset_y
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
    
    # Visual functions.
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
        self.tsize    = [value[2], value[3]]
    @position.setter
    def position(self, value : list[int,int]):
        self._x = value[0] + self._offset_x
        self.y  = value[1]
    @tsize.setter
    def tsize(self, value : list[int,int]):
        if self.tsize == value: return
        self._w = value[0]
        self.h  = value[1]

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._set_rot(value)
    
    ## Functions
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
            "tsize":    self.tsize
        }
    
    def _convert_transform_property_into_object(self, value):
        """Sets the Transform object's properties from a dictionary."""
        self.tsize     = value.get("tsize",    self.tsize)
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
    
    def into_screen_coords(self,
            viewport_size : list[int]        = [480,480],
            do_flip       : bool             = True,
            drawing       : bool             = False,
            parent_rect   : Self             = None):
        """Get the position of the Transform object in the Viewport.
        
        Args:
            viewport_size: The size of the Viewport.
            do_flip:       If True, make the `top` anchor be the top.
            drawing:       If True, account for the image's anchor being on the center.
            parent_rect:   If specified, will account the parent Transform for anchoring."""
        ## Caching stuff
        anchor          = self.anchor
        if parent_rect == None:
            parent_rect = [0,0,
                           *viewport_size]
        cid             = f"{self.rect}{viewport_size}{parent_rect}{anchor}{do_flip}{drawing}"
        if cid in _screenc_cache:
            return _screenc_cache[cid]
        
        ## Calculate pos
        x = parent_rect[0]
        y = parent_rect[1]

        if "right" in anchor:
            x += parent_rect[2] - self.w - self.x
        elif "centerx" in anchor:
            x += (parent_rect[2]/2) - (self.w/2) + self.x
        else:
            x += self.x

        if do_flip:
            if "top" in anchor:
                y += parent_rect[3] - self.h - self.y
            else:
                y += self.y
        else:
            if "top" in anchor:
                y += self.y
            else:
                y += parent_rect[3] - self.h - self.y

        if "centery" in anchor:
            y += (parent_rect[3]/2) - (self.h/2) + self.y
        
        ## Draw check
        if drawing:
            x, y = self._offset_off_anchor(x, y)
        
        ## More caching stuff
        _screenc_cache[cid] = [x,y]
        return [x,y]
    def _offset_off_anchor(self, x, y, w=None, h=None):
        if w == None: w = self._w
        if h == None: h = self._h
        return x+(w // 2) * self.scale_x, y+(h // 2) * self.scale_y
    
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

class Mouse:
    #: Mouse position anchored at bottom left
    pos          = [0,0]
    #: Relative pos from last frame
    dpos         = [0,0]
    #: If mouse is dragging
    dragging     = False
    #: 1 is up, -1 is down
    scroll       = 0
    #: Buttons just now pressed. Use `engine.is_action_pressed` instead.
    just_clicked = MOUSE_DEFAULT_STATE.copy()
    #: Use `engine.is_action_pressed` instead.
    buttons      = MOUSE_DEFAULT_STATE.copy()
    #: List of filepaths
    paths        = []

class Keyboard:
    #: Keyboard modifiers.
    modifiers = 0
    #: Dictionary of keys pressed. Use `engine.is_action_pressed` instead.
    pressed   = {}
    #: Dictionary of keys held down. Use `engine.is_action_pressed` instead.
    held      = {}
    #: Text from Window.on_text.
    text      = ""
    #: Motion from Window.on_text_motion.
    motion    = None

class Language:
    def __init__(self, file="res://data/foobar.json"):
        self.load_lang(file)
    
    @property
    def properties(self):
        """The metadata in the language file."""
        return self._file["properties"]
    @property
    def entries(self):
        """The entries in the language file."""
        return self._file["entries"]
    @property
    def name(self):
        """The name of the language."""
        return self.properties["name"]
    @property
    def base(self):
        """The language to use if an entry is not found."""
        return self.properties["base"]
    
    def load_lang(self,file):
        """Load a language file.
        
        Args:
            file: The filepath."""
        import classes.singleton as engine

        self._file = engine.loader.load(file)
        if self._file["properties"]["base"]:
            _base = Language(self._file["properties"]["base"])
            for i in _base.entries:
                if not i in self.entries:
                    self.entries[i] = _base.entries[i]
    
    def get(self, entry):
        """Get a localized entry from the language file.
        
        Args:
            entry: The name of the entry."""
        return self.entries.get(entry, entry)

class CameraTransform(Transform):
    def __init__(self):
        super().__init__()
        self._zoom = 1
    
    @property
    def zoom(self):
        """The camera's zoom. Read-write"""
        return self._zoom
    @zoom.setter
    def zoom(self, val): self._zoom = val

class Color:
    """A color container."""
    def __init__(self, r=0,g=0,b=0,a=255):
        self._r = r
        self._g = g
        self._b = b
        self._a = a
    def color_as_tuple(self):
        """Return the color as a tuple."""
        return (self.r, self.g, self.b, self.a)
    def color_as_list(self):
        """Return the color as a list."""
        return [self.r, self.g, self.b, self.a]

    @property
    def r(self):
        """Red."""
        return self._r
    @property
    def g(self):
        """Green."""
        return self._g
    @property
    def b(self):
        """Blue."""
        return self._b
    @property
    def a(self):
        """Alpha."""
        return self._a

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
        self._r, self._g, self._b = rgbv[:3]
        if len(rgbv) > 3:
            self._a = rgbv[3]
        self._update_color(*self.color_as_list())