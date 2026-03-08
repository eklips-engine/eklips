# XXX
# Import libraries
import pyglet as pg
from classes import ui

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class Slider(CanvasItem):
    """
    A slider element.
    
    XXX
    """
    _supports_tsize = True
    
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
    @minimum.setter
    def minimum(self, val):
        self._minimum = val
    @maximum.setter
    def maximum(self, val):
        self._maximum = val
    @show_percentage.setter
    def show_percentage(self, val):
        self._showpercent = val
    
    def _set_size(self, w, h):
        self.slider_bg.scale_x = w / self.slider_bg.image.width
        self.slider_bg.scale_y = (h-20) / self.slider_bg.image.height
    def _set_scale(self, x, y):
        return
    def _set_alpha(self, deg):
        self.knob.alpha = deg
        self.slider_bg.alpha = deg
        self.label.alpha = deg
    def _set_rot(self, deg):
        self.knob.rotation = deg
    def _set_visible(self, val):
        self.knob.visible = val
        self.slider_bg.visible = val
        self.label.visible = val
    
    def __init__(self, properties={}, parent=None):
        # Setup CanvasItem
        super().__init__(properties, parent)
        
        # Alias
        self.widgetman = engine.scene._widgetman
        
        # Set properties
        self._showpercent = True
        self._minimum     = 0
        self._maximum     = 150
        self._value       = 0
        self.gid          = self.widgetman.add_widget(self)
        
        # Make item
        self._make_new_item()
    
    def _make_new_item(self):
        self._drawing_bid = self.viewport.add_batch()
        self.slider_bg    = pg.sprite.Sprite(
            img           = engine.theme.get_static_widget("bg"),
            batch         = self.viewport.batches[self.batch_id])
        self.knob         = pg.sprite.Sprite(
            img           = engine.theme.get_static_widget("knob"),
            batch         = self.viewport.batches[self.batch_id])
        self.label        = pg.text.Label(
            text          = f"0%",
            batch         = self.viewport.batches[self.batch_id])
        self._set_anchors()

    def _set_anchors(self):
        self.knob.image.anchor_x = self.knob.image.width  // 2
        self.knob.image.anchor_y = self.knob.image.height // 2
        self.knob._update_position()
    
    def _remove_item(self):
        self.slider_bg.delete()
        self.knob.delete()
        if self.viewport:
            self.viewport.batches.pop(self.batch_id)
    
    def get_if_mouse_hovering_knob(self) -> bool:
        """Returns true if the mouse is hovering over the knob."""
        if not self.viewport:
            return
        ## Get things
        mpos   = engine.mouse.pos
        x, y   = self.knob.x-self.knob.width/2, self.knob.y-self.knob.height/2
        vx, vy = self.viewport.into_screen_coords()

        ## Apply viewport position into x and y
        x += vx - self.viewport.cam.x
        y += vy - self.viewport.cam.y

        ## Apply viewport zooming
        x *= self.viewport.cam.zoom
        y *= self.viewport.cam.zoom
        w  = self.knob.width  * self.viewport.cam.zoom
        h  = self.knob.height * self.viewport.cam.zoom

        ## Result
        return (
            mpos[0] >= x     and
            mpos[0] <= x + w and
            mpos[1] >= y     and
            mpos[1] <= y + h
        )
    
    def update(self):
        super().update()
        
        ## Handle knob
        if self.get_if_mouse_hovering_knob():
            self.widgetman.hovering_widget = self.gid
        else:
            if self.widgetman.hovering_widget == self.gid:
                self.widgetman.hovering_widget = -1

        if engine.mouse.buttons[MOUSE_LEFT]:
            if self.get_if_mouse_hovering_knob():
                if self.widgetman.moving_widget == -1:
                    self.widgetman.focused_widget = self.gid
                if engine.mouse.dragging and self.widgetman.focused_widget == self.gid:
                    self.widgetman.moving_widget  = self.gid
            if self.widgetman.moving_widget  == self.gid:
                engine.set_mouse(MOUSE_DRAG)
                self.value += (engine.mouse.dpos[0])/self.w*self.maximum
        else:
            if self.widgetman.hovering_widget == -1:
                engine.set_mouse(MOUSE_NORMAL)
            if self.get_if_mouse_hovering_knob() or self.widgetman.moving_widget == self.gid:
                engine.set_mouse(MOUSE_DRAGGABLE)
                self.widgetman.moving_widget = -1
        
        ## Draw it
        self.draw()
        
    def _free(self):
        self.widgetman.widgets.pop(self.gid)
        super()._free()
    
    def draw(self):
        ## Check if visible
        if not (self.visible and self.viewport.is_onscreen(self)):
            return
        
        ## Fun little feature
        self.knob.rotation = self.value/self.maximum*360

        ## Set label text
        self.label.text = f"{int(self.value/self.maximum*100)}%" if self.show_percentage else f"{int(self.value)}"
        
        ## Get position of full slider object
        x, y = self.into_screen_coords(self.viewport.tsize)

        ## Move bg
        self.slider_bg.x = x + 5
        self.slider_bg.y = y + 5

        ## Move label
        self.label.x = x + self.w / 2 - self.label.content_width  / 2
        self.label.y = y + self.h / 2 - self.label.content_height / 2

        ## Move knob
        self.knob.y = y + self.knob.height / 2
        if self._value   == 0:
            self.knob.x = x
        else:
            self.knob.x = x + (self._value/self._maximum)*self.w 
        self.knob.x += self.knob.image.anchor_x - self.knob.width / 2