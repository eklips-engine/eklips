## Import libraries
import pyglet as pg
from classes.nodes.gui.canvasitem import *

class Progressbar(CanvasItem):
    """
    A themed progressbar element.
    """
    _isblittable = True
    
    @export(0, "int", "int")
    def value(self):
        return self._value
    @export(0, "int", "int")
    def minimum(self):
        return self._minimum
    @export(150, "int", "int")
    def maximum(self):
        return self._maximum
    @export(True, "bool", "bool")
    def show_percentage(self):
        return self._showpercent
    
    @value.setter
    def value(self, val):
        if val  < self.minimum:
            val = self.minimum
        if val  > self.maximum:
            val = self.maximum
        self._value   = val
        self._set_fill_size()
    @minimum.setter
    def minimum(self, val):
        self._minimum = val
    @maximum.setter
    def maximum(self, val):
        self._maximum = val
        self._set_fill_size()
    @show_percentage.setter
    def show_percentage(self, val):
        self._showpercent = val
    
    def _set_bar_size(self):
        self.bar.scale_x = self.w / self.bar.image.width
        self.bar.scale_y = self.h / self.bar.image.height
    def _set_fill_size(self):
        self.citem.scale_x = ((self._value+ZDE_FIX)/self._maximum*self.w) / self.citem.image.width
        self.citem.scale_y = self.h / self.citem.image.height
    def _set_size(self, w, h):
        self._set_bar_size()
        self._set_fill_size()
    def _set_flip(self, w, h):
        return
    def _set_scale(self, x, y):
        self._set_size()
    def _set_alpha(self, deg):
        self.citem.alpha = deg
        self.bar.alpha = deg
        self.label.alpha = deg
    def _set_rot(self, deg):
        self.citem.rotation = deg
    def _set_visible(self, val):
        self.citem.visible = val
        self.bar.visible = val
        self.label.visible = val
    
    def __init__(self, properties={}, parent=None):
        # Setup CanvasItem
        super().__init__(properties, parent)
        
        # Set properties
        self.bar   = None
        self.label = None

        self._showpercent = True
        self._minimum     = 0
        self._maximum     = 150
        self._value       = 0

        # Make new item
        self._make_new_item()
    
    def _fix_broken_item(self):
        self._remove_item(False)
        self._make_new_item()
        self._convert_transform_property_into_object(self.transform)
    def _make_new_item(self):
        if self.bar:
            self._remove_item(False)
        else:
            self._drawing_bid = self.viewport.add_batch()
        
        self.bar   = pg.sprite.Sprite(
            img    = engine.theme.get_static_widget("bg"),
            batch  = self.batch)
        self.citem = pg.sprite.Sprite(
            img    = engine.theme.get_static_widget("pb_fill"),
            batch  = self.batch)
        self.label = pg.text.Label(
            text   = f"0%",
            batch  = self.batch)
        self._set_size(*self.size)
        self._set_anchors()
    def _set_anchors(self):
        self.bar.image.anchor_x   = self.bar.image.width    // 2
        self.bar.image.anchor_y   = self.bar.image.height   // 2
        self.citem.image.anchor_x = self.citem.image.width  // 2
        self.citem.image.anchor_y = self.citem.image.height // 2
        self.citem._update_position()
        self.bar._update_position()
    def _remove_item(self, remove_batches=True):
        if not self.bar or not self.bar._vertex_list:
            return
        self._switch_window()
        self.bar.delete()
        self.citem.delete()
        self.label.delete()
        if self.viewport and remove_batches:
            self.viewport.batches.pop(self.batch_id)
    
    def update(self):
        super().update()
        self.draw()
    
    def draw(self):
        ## Check if visible
        if not (self.visible and self.viewport.is_onscreen(self)):
            return
        
        ## Fun little feature
        self.citem.rotation = self.value/self.maximum*360

        ## Set label text
        self.label.text = f"{int(self.value/self.maximum*100)}%" if self.show_percentage else f"{int(self.value)}"
        
        ## Get position of full progressbar object
        bgx, bgy = self.into_screen_coords(drawing=True)
        x,     y = self.into_screen_coords(drawing=False)

        ## Move bg
        self.bar.x = bgx
        self.bar.y = bgy

        ## Move label
        self.label.x = x + self.w / 2 - self.label.content_width  / 2
        self.label.y = y + self.h / 2 - self.label.content_height / 2 + 2
        
        ## Move fill
        self.citem.x, self.citem.y = self._offset_off_anchor(x=x,y=y, w=self.citem.width,h=self.citem.height)