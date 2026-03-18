# Import singleton
import pyglet as pg
from classes.resources.resource import *
from classes.customprops        import *

## Image Grid
class ImageGrid(Resource):
    """
    A Resource wrapper around pg.image.ImageGrid.
    """

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        self._image = value
        self._make_grid()

    @property
    def columns(self):
        return self._col
    @columns.setter
    def columns(self, value):
        self._col = value
        self._make_grid()
    @property
    def rows(self):
        return self._row
    @rows.setter
    def rows(self, value):
        self._row = value
        self._make_grid()
    @property
    def column_padding(self):
        return self._colpd
    @column_padding.setter
    def column_padding(self, value):
        self._colpd = value
        self._make_grid()
    @property
    def row_padding(self):
        return self._rowpd
    @row_padding.setter
    def row_padding(self, value):
        self._rowpd = value
        self._make_grid()
    def _make_grid(self):
        self._grid = pg.image.ImageGrid(
            self.image,
            self.rows, self.columns,
        
            row_padding=self.row_padding,
            column_padding=self.column_padding)
        
    def __init__(self, properties={}):
        self._col   = 0
        self._row   = 0
        self._colpd = 0
        self._rowpd = 0
        self._image = None

        self._make_grid()
        super().__init__(properties)

## Animation
class _ModifiedAnimation(pg.image.animation.Animation):
    @property
    def width(self):  return self.get_max_width()
    @property
    def height(self): return self.get_max_height()
    @property
    def size(self):   return [self.width, self.height]
class Animation(Resource):
    """
    An Animation resource used by AnimatedSprite.
    """
    
    def save(self, path):
        pass
    @export(None, "str", "animation")
    def animation(self):
        return self._pointer
    @animation.setter
    def animation(self,value):
        if self._pointer == value: return
        self._pointer = value
        self._set_animation_as_image()
    @export({},"list","animations/img")
    def animations(self):
        # animation: {
        #  paths: ["imgpath"]               # If animation is a sequence
        #  path:  res://media/animation.gif # If paths property is None
        #  obj:   [Img]                     # Made on Runtime
        # }
        return self._animations
    @animations.setter
    def animations(self, animations : list):
        self._animations = animations
        for name in self._animations:
            self._init_animation(name)
    def _init_animation(self, name):
        """If you want to make an animation, use `make_animation`. This function is only used internally."""
        animation_data = self._animations[name]
        animation      = None
        speed          = animation_data["speed"]
        if animation_data["paths"]:
            frames    = []
            for frame in animation_data["paths"]:
                frames.append(pg.image.animation.AnimationFrame(engine.loader.load(frame), speed))

            animation = _ModifiedAnimation(frames)
        else:
            animation = engine.loader.load(animation_data["path"])
        
        self._animations[name]["obj"] = animation
    def get_animation_image(self, animation):
        return self.animations[animation]["obj"]
    def _set_animation_as_image(self):
        return
    
    def __init__(self, properties={}):
        self._pointer    = [None]
        self._animations = {}
        super().__init__(properties)