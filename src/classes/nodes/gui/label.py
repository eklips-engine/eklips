# Import libraries
import pyglet as pg
from classes.nodes.gui.canvasitem import *

# Classes
class Label(CanvasItem, Color):
    """
    A Label.
    
    XXX
    """
    _can_check_layer       = True
    citem  : pg.text.Label = None
    _isblittable           = True

    @export("dolorem ipsum","str","str")
    def text(self) -> str: return self._text
    @text.setter
    def text(self, value):
        self._text = value
        if self.citem:
            self.citem.text = value

    @export(DEFAULT_FONT_NAME,"str","font")
    def font(self) -> str: return self._fname
    @font.setter
    def font(self, value):
        self._fname = value
        if self.citem:
            self.citem.font_name = value

    @export(DEFAULT_FONT_SIZE,"float/int","float/int")
    def font_size(self) -> float | int: return self._fsize
    @font_size.setter
    def font_size(self, value):
        self._fsize = value
        if self.citem:
            self.citem.font_size = value

    @export([255,255,255],"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the Label. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : tuple[int, int, int] | list[int]):
        self.rgb = rgb
    def _update_color(self, r, g, b, a):
        if not self.citem:
            return
        self.citem.color = (r,g,b,a)
    
    def __init__(self, properties={}, parent=None):
        Color.__init__(self, 255,255,255)
        self._text  = "dolorem ipsum"
        self._fsize = DEFAULT_FONT_SIZE
        self._fname = DEFAULT_FONT_NAME

        super().__init__(properties, parent)
    
    def update(self):
        super().update()
        self.draw()
    
    def draw(self):
        """Draw the label. This is usually called automatically."""
        if not len(self.text.split()):
            return
        self._draw()
    def _draw(self):
        return engine.display.blit_label(
            text        = self.text,
            transform   = self,
            window_id   = self._drawing_wid,
            viewport_id = self._drawing_vid,
            label       = self.citem,
            font_name   = self.font,
            font_size   = self.font_size  
        )

    ## CItem managing
    def _remove_item(self):
        if not self.citem:
            return
        self.citem.delete()
        self.citem = None
    def _make_new_item(self):
        if self.citem:
            self._remove_item()
        self.batch = engine.display.get_batch_from_window(self.window_id, self.viewport_id, self.batch_id)
        self.citem = pg.text.Label(batch=self.batch)
        
        self.citem.color     = self.color
        self.citem.text      = self.text
        self.citem.font_name = self.font
        self.citem.font_size = self.font_size
        self.citem.visible   = False
    def _setup_properties(self, scene=None):
        super()._setup_properties(scene)
        self._make_new_item()