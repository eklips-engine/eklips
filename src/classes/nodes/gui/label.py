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
    sprite : pg.text.Label = None

    @export("dolorem ipsum","str","str")
    def text(self) -> str: return self._text
    @text.setter
    def text(self, value):
        self._text = value
        if self.sprite:
            self.sprite.text = value

    @export(DEFAULT_FONT_NAME,"str","font")
    def font(self) -> str: return self._fname
    @font.setter
    def font(self, value):
        self._fname = value
        if self.sprite:
            self.sprite.font_name = value

    @export(DEFAULT_FONT_SIZE,"float/int","float/int")
    def font_size(self) -> float | int: return self._fsize
    @font_size.setter
    def font_size(self, value):
        self._fsize = value
        if self.sprite:
            self.sprite.font_size = value

    @export([255,255,255],"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the Label. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : tuple[int, int, int] | list[int]):
        self.rgb = rgb
    def _update_color(self, r, g, b, a):
        self.sprite.color = (r,g,b,a)
    
    def __init__(self, properties={}, parent=None, children=None):
        Color.__init__(self, 255,255,255)
        self._text  = "dolorem ipsum"
        self._fsize = DEFAULT_FONT_SIZE
        self._fname = DEFAULT_FONT_NAME

        super().__init__(properties, parent, children)
        self._make_new_sprite()
    
    def update(self):
        super().update()
        self.draw()
    
    def draw(self):
        """Draw the label. This is usually called automatically."""
        self._draw()
    
    def _draw(self):
        return engine.display.blit_label(
            text      = self.text,
            transform = self,
            window_id = self._drawing_wid,
            label     = self.sprite,
            font_name = self.font,
            font_size = self.font_size  
        )
    
    def _remove_sprite(self):
        if not self.sprite and not engine.debug.sprite_always_visible:
            return
        viewport = self._get_viewport()
        viewport._deallocate_label(self._sprite_id)
        self.sprite = None
    def _make_new_sprite(self):
        if self.sprite:
            self._remove_sprite()
        viewport = self._get_viewport()
        self.sprite, self._sprite_id = viewport._allocate_label(self._drawing_bid)