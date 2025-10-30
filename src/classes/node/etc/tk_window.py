## Import inherited
from classes.node.node import Node

## Import engine singleton and others
import tkinter as tk
from PIL import Image, ImageTk
import pyglet as pg, io
import classes.singleton as engine

## Node
class TkWindow(Node):
    """
    ## A Tkinter Window.

    Self-explanatory if you have used Tkinter. `TkWindow.tk_self` is the Tk() object.
    No 2D Nodes work in this.
    """
    
    node_base_data = {
        "prop":   {
            "caption":     "Node.Window.Tk",
            "icon":        None,
            "dimension":   "640x480"
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    def __init__(self, data=node_base_data, parent=None):
        super().__init__(data,parent)
        self.tk_self = tk.Tk()
        self.tk_self.geometry(self.properties["dimension"])
        self.tk_self.title(self.properties["caption"])
        icon_image  = Image.open(io.BytesIO(engine.resource_loader.load(self.properties["icon"]), force_type = "bin"))
        photo_image = ImageTk.PhotoImage(icon_image)
        self.tk_self.wm_iconphoto(True, photo_image)