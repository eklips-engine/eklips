# Import singleton
import pyglet as pg
from classes.resources.object import *
from classes.customprops      import *

# Classes
class Resource(Object):
    """
    An Object that can be saved or loaded.
    
    For making Resources, you can modify `save()` and `load()` with your own code, for example:
    
```python
class MyResource(Resource):
    @classmethod
    def load(cls, path) -> Self:
        data = json.loads(engine.loader.load(path))
        return cls(data)
    
    @classmethod
    def new(cls) -> Self:
        return cls({"value": "default"})
    
    def save(self, path) -> None:
        with open(engine.loader._get_true_path(path), "w") as f:
            ...
```
    """
    @classmethod
    def load(cls, path) -> Self:
        """Load a resource from a file.
        
        Args:
            path: Filepath. (eg: `res://media/load.mp3`, `root://_assets/icon.png`)"""
        data = json.loads(engine.loader.load(path))
        return cls(data)

    @classmethod
    def new(cls) -> Self:
        """Get a new Resource with all its default values."""
        return cls({})

    def save(self, path) -> None:
        """Save a resource to a file.
        
        Args:
            path: Filepath. (eg: `res://media/load.mp3`, `root://_assets/icon.png`)"""
        ...