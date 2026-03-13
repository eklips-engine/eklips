# Import libraries
from classes.nodes.gui.sprite import *

# Classes
class AnimatedSprite(CanvasItem):
    """
    A 2D Sprite.
    
    XXX
    """
    _isblittable     = True

    ## Exports
    @export(None, "str", "animation")
    def animation(self):
        return self._pointer[0]
    @animation.setter
    def animation(self,value):
        self._pointer[0] = value
    @export({},"list","animations/img")
    def animations(self):
        # animation: {
        #  paths: ["imgpath"]
        #  images: [Img]        # Made on Runtime
        # }
        return self._animations
    @animations.setter
    def animations(self, animations : list):
        self._animations = animations
        for name in self._animations:
            self._init_animation(name)
    def _init_animation(self, name):
        """If you want to make an animation, use `make_animation`. This function is only used internally."""
        animation           = self._animations[name]
        animation["frames"] = []
        for frame in animation["paths"]:
            animation["frames"].append(engine.loader.load(frame))
    def get_frame_from_animation(self, animation, frame):
        return self.animations[animation]["frames"][int(frame)]
    
    ## Init
    def __init__(self, properties={}, parent=None):
        self._pointer    = [None, 0]
        self._animations = {}

        super().__init__(properties, parent)
    
    def update(self):
        super().update()
        # Advance
        self._pointer[1]    += engine.delta*self.animations[self.animation]["speed"]
        if self._pointer[1]  > len(self.animations[self.animation]["frames"]):
            self._pointer[1] = 0
        
        # Set image and draw
        self.image = self.get_frame_from_animation(*self._pointer)
        self.draw()