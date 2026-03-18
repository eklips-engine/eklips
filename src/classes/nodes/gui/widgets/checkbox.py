# Import libraries
from classes.nodes.gui.canvasitem import *

# Classes
class Checkbox(CanvasItem):
    """
    A themed Checkbox element that has two states; on or off.
    """
    _isblittable = True
    
    @export(False, "bool", "bool")
    def value(self) -> bool:
        return self._value
    @value.setter
    def value(self, val):
        self._value = val
    
    def __init__(self, properties={}, parent=None):
        # Setup CanvasItem
        super().__init__(properties, parent)
        
        # Alias
        self.widgetman = engine.scene._widgetman
        
        # Set properties
        self._value = False
        self.gid    = self.widgetman.add_widget(self)
        
        # Make item
        self._make_new_item()
        self._checkbox_image    = engine.theme.get_static_widget("boxbtn")
        self._checkbox_selected = engine.theme.get_static_widget("boxedbtn")
    
    def update(self):
        super().update()
        
        ## Handle widget
        if engine.mouse.just_clicked[MOUSE_LEFT]:
            if self.get_if_mouse_hovering():
                self.value = not self.value
        
        ## Handle cursor
        if self.get_if_mouse_hovering():
            self.widgetman.hovering_widget = self.gid
        else:
            if self.widgetman.hovering_widget == self.gid:
                self.widgetman.hovering_widget = -1
        
        if engine.mouse.buttons[MOUSE_LEFT]:
            if self.get_if_mouse_hovering():
                if self.widgetman.moving_widget == -1:
                    self.widgetman.focused_widget = self.gid
                if engine.mouse.dragging and self.widgetman.focused_widget == self.gid:
                    self.widgetman.moving_widget  = self.gid
        else:
            if self.widgetman.hovering_widget == -1:
                engine.set_mouse(MOUSE_NORMAL, self.window_id)
            if self.get_if_mouse_hovering() or self.widgetman.moving_widget == self.gid:
                engine.set_mouse(MOUSE_POINT, self.window_id)
                self.widgetman.moving_widget = -1
        
        ## Select the image based on the value
        if self.value:
            self.citem.image = self._checkbox_selected
        else:
            self.citem.image = self._checkbox_image
        self.draw()
        
    def _free(self):
        self.widgetman.widgets.pop(self.gid)
        super()._free()