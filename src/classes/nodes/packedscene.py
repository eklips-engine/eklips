# Import inherited
from classes.nodes.node      import *
from classes.resources.scene import Scene, SceneError, CollisionManager

# Classes
class PackedScene(Node, Scene):
    def __init__(self, properties = {}, parent = None, children = None):
        super().__init__(properties, parent, children)
    
    def update(self):
        super().update()
        Scene.update(self)