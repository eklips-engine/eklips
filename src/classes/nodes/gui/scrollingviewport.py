# Import inherited
from classes.nodes.gui.extraviewport import *
from classes.ui                      import *

# Variables
viewport_transform = {
    "position": [0,0],
    "tsize":    [320,320],
    "scale":    [1,1],
    "scroll":   [0,0],

    "rotation": 0,
    "alpha":    255,
    "anchor":   "top left",
    "visible":  True,
    "skew":     0
}

# Classes
class ScrollingViewport(ExtraViewport):
    """
    A Viewport Node.
    
    This Node will create a new Viewport. You can get this Viewport
    by using `engine.display.get_viewport(node.viewport_id, wid)`
    or by using `node` itself.
    """
    _iswindoworviewportlikeobject = True

    @export(1200.0,"float","slider")
    def speed(self):
        """How fast the scrolling should be.

        The reason why the default value is so high
        because on 1x speed, it takes 1 second to
        move 1 pixel and scrolling isn't exactly
        smooth as of right now.

        You can make this value negative to go backwards.
        """
        return self._speed
    @speed.setter
    def speed(self, value): self._speed = value

    @export(False, "bool", "bool")
    def left_to_right(self):
        return self._left_to_right
    @left_to_right.setter
    def left_to_right(self, value):
        self._left_to_right = value
    
    def __init__(self, properties={}, parent=None, children=None):
        self._speed         = 1200.0
        self._left_to_right = False
        super().__init__(properties, parent, children)
    
    def update(self):
        super().update()
        if self._left_to_right:
            self.cam.x -= engine.mouse.scroll * (engine.delta * self.speed)
            if self.cam.x  < 0:
                self.cam.x = 0
        else:
            self.cam.y += engine.mouse.scroll * (engine.delta * self.speed)
            if self.cam.y  > 0:
                self.cam.y = 0