## Import inherited
from classes.nodes.node      import *
from classes.resources.scene import Scene

## Classes
class PackedScene(Node, Scene):
    def __init__(self, properties = {}, parent = None):
        ## Initialize scene
        Scene.__init__(self)

        ## Initialize Node
        Node.__init__(self, properties, parent)
    
    def update(self):
        ## Update the Node
        Node.update(self)

        ## Update the Scene
        Scene.update(self)
    
    def _free(self):
        ## Empty the Scene
        self.empty()

        ## Free the Node
        Node._free(self)