# Import libraries
import pygame, pyglet as pg, json, gc

# Import components
from classes.locals      import *
import classes.singleton as engine

# Import resources
print(" ~ Importing all resources")
from classes.resources.object import *
from classes.resources.script import *
from classes.resources.scene  import *

# Classes
class Loader:
    print(" ~ Initialize Resource Loader")
    resource_tree = {}
    use_binary    = False
    extensions    = {
        "img": ["png","jpg","jpeg","bmp","gif","dds","tif","tiff"],
        "sfx": ["mp3","ogg","wav"],
        "txt": ["py","txt","ekl"],
        "jsn": ["json","scn","res"],
        "vid": ["mp4","webm","gif"]
    }

    def _get_true_path(self, path : str):
        if path.startswith("res://"):  return f"{engine.game.project_dir}/{path.removeprefix('res://')}"
        if path.startswith("root://"): return f"{path.removeprefix('root://')}"
        if path.startswith("user://"): return f"{path.removeprefix('user://')}"

        return path

    def _load(self, path, ext):
        actual_path = self._get_true_path(path)
        
        try:
            if ext in self.extensions["img"]:
                return pg.image.load(actual_path)
            if ext in self.extensions["sfx"]:
                return pygame.Sound(actual_path)
            if ext in self.extensions["txt"]:
                return open(actual_path).read()
            if ext in self.extensions["jsn"]:
                return json.loads(open(actual_path).read())
            if ext in self.extensions["vid"]:
                return engine.pvd.VideoPyglet(actual_path)
        except:
            pass
        
        return None
    
    def load(self, path, force_type = None, return_identifier = False, force_new_resource = False):
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
