# Import libraries
import pygame, pyglet as pg, json, xmltodict

# Import components
from classes.locals      import *
import classes.singleton as engine

# Import resources
print(" ~ Importing all resources")
from classes.resources.object  import *
from classes.resources.scene   import *
from classes.resources.tileset import *
from classes.resources.theme   import *

# Classes
class Loader:
    """
    A class to load resources for use.
    """
    print(" ~ Initialize Resource Loader")
    resource_tree = {}
    use_binary    = False
    extensions    = {
        "img": ["png","jpg","jpeg","bmp","gif","dds","tif","tiff"], # Image
        "cur": ["cur"],                                             # Windows Mouse Cursor
        "sfx": ["mp3","ogg","wav"],                                 # Sound
        "txt": ["py","txt","ekl"],                                  # TXT file
        "jsn": ["json"],                                            # JSON
        "vid": ["mp4","webm"],                                      # Video
        "ani": ["gif"],                                             # pyglet.image.Animation
        "fnt": ["ttf","otf"],                                       # Fonts
        "scn": ["scn","tscn"],                                      # Scene
        "res": ["res","rc"],                                        # Ekl Resource
        "xml": ["xml", "svg", "html"]                               # Xml
    }

    def _get_true_path(self, path : str):
        path = path.replace("\\", "/")
        
        if path.startswith("res://"):  return f"{engine.game.project_dir}/{path.removeprefix('res://')}"
        if path.startswith("root://"): return f"{path.removeprefix('root://')}"
        if path.startswith("user://"): return f"{engine.game.save_dir}{path.removeprefix('user://')}"

        return path

    def _load(self, path, ext):
        actual_path = self._get_true_path(path)
        
        try:
            if ext in self.extensions["img"]:
                image          = pg.image.load(actual_path)
                image.anchor_x = image.width  // 2
                image.anchor_y = image.height // 2
                return image
            if ext in self.extensions["sfx"]:
                return pygame.Sound(actual_path)
            if ext in self.extensions["txt"]:
                return open(actual_path).read()
            if ext in self.extensions["jsn"]:
                return json.loads(open(actual_path).read())
            if ext in self.extensions["scn"]:
                return json.loads(open(actual_path).read())
            if ext in self.extensions["xml"]:
                return xmltodict.parse(open(actual_path).read())
            if ext in self.extensions["cur"]:
                image = pg.image.load(actual_path)
                return pg.window.ImageMouseCursor(image, hot_x=0, hot_y=image.height)
            if ext in self.extensions["res"]:
                data     = json.loads(open(actual_path).read())
                
                ## Make Resource
                classobj = globals().get(data["type"])
                obj      = classobj.__new__(classobj)
                obj.__init__(data)
                
                ## Setup properties
                obj._setup_properties()
                return obj
            if ext in self.extensions["vid"]:
                return engine.pvd.VideoPyglet(actual_path)
            if ext in self.extensions["fnt"]:
                pg.font.add_file(actual_path)
                return
        except Exception as error:
            engine.error_handler.show_error(error)
        
        return None
    
    def load(self, path, force_type = None, return_identifier = False, force_new_resource = False):
        """Load a resource from a file.
        
        Args:
            path: Filepath. (eg: `res://media/load.mp3`, `root://_assets/icon.png`)
            force_type: If not None, what extension should `path` be treated as.
            return_identifier: If True, return resource and its ID.
            force_new_resource: If True, don't cache resource and always load new ones. Might be useful for things like Scripts."""
        rid = path.replace(":",".").replace("/",",")
        obj = None
        ext = path.split(".")[-1]
        if force_type: ext = force_type

        if rid in self.resource_tree and not force_new_resource:
            obj = self.resource_tree[rid]
        else:
            obj = self._load(path, ext)
            self.resource_tree[rid] = obj
        
        if return_identifier:
            return obj, rid
        else:
            return obj
