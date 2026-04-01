## Import libraries
import pyglet as pg
from classes.nodes.gui.colorrect import *

## Classes
class Inputbox(ColorRect, Color):
    """
    A themed inputbox element.
    """
    _isblittable = True
    _blinktimer  = 0.5
    
    ## Exports
    @export("", "str", "str")
    def value(self):
        return "".join(self._value)
    @value.setter
    def value(self, val):
        self._value   = list(val)
        self._pointer = len(self._value)
    
    ## Transform related
    def _set_alpha(self, deg):
        self.citem.alpha = deg
        self.label.alpha = deg
    def _set_visible(self, val):
        self.citem.visible = val
        self.label.visible = val
    
    ## Init
    def __init__(self, properties={}, parent=None):
        # Setup CanvasItem
        Color.__init__(self, *WHITE)
        super().__init__(properties, parent)
        
        # Alias
        self.widgetman = engine.scene._widgetman
        
        # Set properties
        self._value   = []
        self._pointer = 0
        self._elapsed = 0
        self.gid      = self.widgetman.add_widget(self)

        # Make new item
        self._make_new_item()
    
    ## CItem management
    def _fix_broken_item(self):
        self._remove_item(False)
        self._make_new_item()
        self._convert_transform_property_into_object(self.transform)
    def _make_new_item(self):
        if self.citem:
            self._remove_item(False)
        else:
            self._drawing_bid = self.viewport.add_batch()

        self.citem = pg.shapes.Rectangle(0,0,self.w,self.h, color=self.color, batch=self.batch)
        self.label = pg.text.Label(
            text   = self.value,
            batch  = self.batch)
        self._set_anchors()
    def _remove_item(self, remove_batches=True):
        self._switch_window()
        self.citem.delete()
        self.label.delete()
        if self.viewport and remove_batches:
            self.viewport.batches.pop(self.batch_id)
    
    def update(self):
        super().update()
        
        ## Focusing
        if self.get_if_mouse_hovering():
            self.widgetman.hovering_widget = self.gid
        else:
            if self.widgetman.hovering_widget == self.gid:
                self.widgetman.hovering_widget = -1

        if engine.mouse.buttons[MOUSE_LEFT]:
            if self.widgetman.hovering_widget == self.gid:
                self.widgetman.focused_widget  = self.gid

        ## Mouse
        if self.widgetman.hovering_widget == -1:
            engine.set_mouse(MOUSE_NORMAL, self.window_id)
        if self.get_if_mouse_hovering():
            engine.set_mouse(MOUSE_IBEAM, self.window_id)
            self.widgetman.moving_widget = -1

        ## Typing
        if self.widgetman.focused_widget == self.gid:
            char   = engine.keyboard.text
            motion = engine.keyboard.motion
            
            if char != "":
                self._value.insert(self._pointer, char)
                self._pointer += len(char)
            elif motion == key.MOTION_DELETE:
                if len(self._value) and self._pointer < len(self._value):
                    self._value.pop(self._pointer)
            elif motion == key.MOTION_LEFT:
                if self._pointer-1 > -1:
                    self._pointer -= 1
            elif motion == key.MOTION_RIGHT:
                if self._pointer+1 <= len(self._value):
                    self._pointer += 1
            elif motion == key.MOTION_BEGINNING_OF_FILE:
                self._pointer = 0
            elif motion == key.MOTION_END_OF_FILE:
                self._pointer = len(self._value)
            elif motion == key.MOTION_BACKSPACE:
                if len(self._value) and self._pointer-1 > -1:
                    self._value.pop(self._pointer-1)
                    self._pointer -= 1
        
        ## Draw it
        self._elapsed += engine.delta
        if self._elapsed  > self._blinktimer*2:
            self._elapsed = 0
        self.draw()
        
    def _free(self):
        self.widgetman.widgets.pop(self.gid)
        super()._free()
    
    def draw(self):
        ## Check if visible
        if not (self.visible and self.viewport.is_onscreen(self)):
            return
        
        ## Get position of full object
        x,   y = self.into_screen_coords()
        tx, ty = self.into_screen_coords(drawing=True)

        ## Move bg
        self.citem.x = tx
        self.citem.y = ty

        ## Move label
        self.label.x = x + 5
        self.label.y = y + self.h / 2 - self.label.content_height / 2 + 5

        display_value = self._value[:]
        if self.widgetman.focused_widget == self.gid:
            display_value.insert(self._pointer, "_" if self._elapsed > self._blinktimer else "")
        self._switch_window()
        self.label.text = f"{''.join(display_value)}"