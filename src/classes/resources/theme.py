# Import singleton
import pyglet as pg
from classes.resources.resource import *
from classes.customprops        import *

# Classes
class Theme(Resource):
    """
    A Theme class
    
    XXX
    """
    print(" ~ Initialize themer")

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, img : pg.image.ImageData):
        self._image = img
        self.refresh()
    
    @export(None,"str","file_path/img")
    def image_path(self):
        """Filepath of the attached Image. Setting this value loads and sets the imagepath as the Tileset's image."""
        return self._imagepath
    @image_path.setter
    def image_path(self, value):
        if not value: return
        self._imagepath = value
        self.image      = engine.loader.load(value)
        self.refresh()
    
    @export({},"dict","widgets")
    def widgets(self):
        return self._widgets
    @widgets.setter
    def widgets(self, value : dict):
        self._widgets = value
        self.refresh()
    
    def refresh(self):
        for widget in self._widgets:
            self._widgets[widget]["obj"] = Widget(self._widgets[widget], self)

    def get_static_widget(self, name):
        return self._widgets[name]["obj"]._image

    def __init__(self, properties={}):
        self._image     : pg.image.AbstractImage = None
        self._imagepath : str                    = None
        self._widgets   : dict                   = properties["widgets"]
        super().__init__(properties)

class _BaseWidget:
    def __init__(self, data, theme: Theme):
        self._data  = data
        self._theme = theme
        self._image = None
        
    def get_from_size(self, size):
        return
    
class _StaticWidget(_BaseWidget):
    def __init__(self, data, theme: Theme):
        super().__init__(data, theme)
        
        self._image = self._theme.image.get_region(
            *data["pos"],
            *data["size"]
        )
    
    def get_image(self):
        return self._image

class _SplicedWidget(_BaseWidget):
    def __init__(self, data, theme: Theme):
        super().__init__(data, theme)
        
        self._image = self._theme.image.get_region(
            *data["pos"],
            *data["size"]
        )
    
    def get_from_size(self, size):
        return self._image

class Widget(_StaticWidget, _SplicedWidget):
    def __init__(self, data, theme: Theme):
        if not "corner_size" in data or "side_size" in data:
            _StaticWidget.__init__(self, data, theme)
        else:
            _SplicedWidget.__init__(self, data, theme)

class WidgetManager:
    def __init__(self):
        self.moving_widget   = -1
        self.hovering_widget = -1
        self.focused_widget  = -1
        
        self.widgets  = {}
        self._lastgid = 0
    
    def add_widget(self, widget):
        gid               = self._lastgid
        self.widgets[gid] = widget
        
        self._lastgid += 1
        return gid