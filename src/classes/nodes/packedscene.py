# Import inherited
from classes.nodes.node      import *
from classes.resources.scene import Scene, SceneError, CollisionManager, SceneLike

# Classes
class PackedScene(Node, Scene):
    def __init__(self, properties = {}, parent = None):
        Scene.__init__(self)
        Node.__init__(self, properties, parent)
    
    def update(self):
        Node.update(self)
        Scene.update(self)
    
    def _free(self):
        self.empty()
        Node._free(self)