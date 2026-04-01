## Import libraries
import pyglet as pg, json, xmltodict

## Import components
from classes.locals      import *
import classes.singleton as engine

## Import resources
print(" ~ Importing all resources")
from classes.resources.image   import Animation, _ModifiedAnimation
from classes.resources.object  import *
from classes.resources.scene   import *
from classes.resources.tileset import *
from classes.resources.theme   import *

## Classes
class Loader:
    """
    A class to load resources for use.
    """
    print(" ~ Initialize Resource Loader")
    resource_tree = {}
    use_binary    = False
    extensions    = {
        "img": ["png","jpg","jpeg","bmp","dds","tif","tiff"], # Image
        "cur": ["cur"],                                       # Windows Mouse Cursor
        "sfx": ["mp3","ogg","wav"],                           # Sound
        "txt": ["py","txt","ekl"],                            # TXT file
        "jsn": ["json"],                                      # JSON
        "vid": ["mp4","webm","mkv","flv"],                    # Video
        "ani": ["gif"],                                       # pyglet.image.Animation
        "fnt": ["ttf","otf"],                                 # Fonts
        "scn": ["scn","tscn"],                                # Scene
        "res": ["res","rc"],                                  # Eklips Resource
        "xml": ["xml", "svg", "html"]                         # Xml
    }

    def _get_true_path(self, path : str):
        path     = path.replace("\\", "/")
        rel_path = os.path.relpath(path).replace("\\", "/") # Don't use if `path` is custom FS
        proj_dir = os.path.relpath(engine.game.project_dir).replace("\\", "/")
        save_dir = engine.game.save_dir

        if path.startswith("res://"):    return f"{proj_dir}/{path.removeprefix('res://')}".replace("\\", "/")
        elif path.startswith("root://"): return f"{path.removeprefix('root://')}".replace("\\", "/")
        elif path.startswith("user://"): return f"{save_dir}{path.removeprefix('user://')}".replace("\\", "/")
        else:
            parent = "/".join(rel_path.split("/")[:-1])
            if not parent in pg.resource.path:
                pg.resource.path.append(parent)
            return rel_path

    def _load(self, path, ext):
        actual_path = self._get_true_path(path)
        
        if ext in self.extensions["img"]:
            image          = pg.resource.image(actual_path)
            image.anchor_x = image.width  // 2
            image.anchor_y = image.height // 2
            
            return image
        if ext in self.extensions["sfx"]:
            return pg.resource.media(actual_path)
        if ext in self.extensions["txt"]:
            with pg.resource.file(actual_path, "r") as f:
                return f.read()
        if ext in [*self.extensions["scn"],
                    *self.extensions["jsn"]]:
            with pg.resource.file(actual_path, "r") as f:
                return json.loads(f.read())
            return json.loads(open(actual_path).read())
        if ext in self.extensions["xml"]:
            with pg.resource.file(actual_path, "r") as f:
                return xmltodict.parse(f.read())
        if ext in self.extensions["cur"]:
            image = pg.resource.image(actual_path)
            return pg.window.ImageMouseCursor(image, hot_x=0, hot_y=image.height, acceleration=True)
        if ext in self.extensions["res"]:
            with pg.resource.file(actual_path, "r") as f:
                data = json.loads(f.read())
            
            ## Make Resource
            classobj = globals().get(data["type"])
            obj      = classobj.__new__(classobj)
            obj.__init__(data)
            
            ## Setup properties
            obj._setup_properties()
            return obj
        if ext in self.extensions["vid"]:
            return engine.pvd.VideoPyglet(pg.resource.file(actual_path).read())
        if ext in self.extensions["fnt"]:
            pg.resource.add_font(actual_path)
        if ext in self.extensions["ani"]:
            image= _ModifiedAnimation(pg.resource.animation(actual_path).frames)

            for frame in image.frames:
                frame.anchor_x = frame.width  // 2
                frame.anchor_y = frame.height // 2
            return
        
        return None
    
    def load(self, path, force_type = None, return_identifier = False, force_new_resource = False) -> Any | (tuple[Any | str]):
        """Load a resource from a file.
        
        Args:
            path: Filepath. (eg: `res://media/load.mp3`, `root://_assets/icon.png`)
            force_type: If not None, what extension should `path` be treated as.
            return_identifier: If True, return resource and its ID.
            force_new_resource: If True, don't cache resource and always load new ones. Might be useful for things like Scenes or Scripts."""
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
