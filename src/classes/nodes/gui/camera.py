# Import libraries=
from classes.nodes.gui.canvasitem import *

# Classes
class Camera(CanvasItem):
    """
    A 2D Camera.
    """
    
    ## Init
    def __init__(self, properties={}, parent=None):
        super().__init__(properties, parent)
        self._follow_parent = True
    
    ## Exports
    @export(True, "bool", "bool")
    def follow_parent(self):
        return self._follow_parent
    @follow_parent.setter
    def follow_parent(self, value):
        self._follow_parent = value
    @export(1, "int/float", "slider")
    def zoom(self):
        return self.viewport.cam.zoom
    @zoom.setter
    def zoom(self, value):
        self.viewport.cam.zoom = value

    ## Transform related
    def _set_rot(self, deg):
        self.viewport.cam.rotation = deg
    def _set_pos(self, x, y):
        if not self._follow_parent:
            self.viewport.cam.x = x
            self.viewport.cam.y = y
    
    ## Update
    def update(self):
        if (self._follow_parent and self.parent and self.parent.get("_iscitem", False)
           and not self.parent.get("_isdisplayobject", False)):
            self.parent : CanvasItem
            x, y = self.parent.into_screen_coords()

            target_x = x - (self.viewport.w / 2 - self.parent.w / 2)
            target_y = y - (self.viewport.h / 2 - self.parent.h / 2)

            if self.parent.flip_w:
                target_x -= self.parent.w*5
            else:
                target_x += self.parent.w*5
            
            self.viewport.cam.x += (target_x - self.viewport.cam.x) / (engine.fps * 0.35)
            self.viewport.cam.y += (target_y - self.viewport.cam.y) / (engine.fps * 0.35)
            self.position        = self.viewport.cam.position
        
        super().update()