## Import inherited
from classes.node.node import Node

## Import engine singleton and others
import pyglet as pg
from tkinter.messagebox import *
import classes.singleton as engine

## Node
class OptionDialog(Node):
    """
    ## A Window node to ask for a question.
     
    The `OptionDialog.popup` function returns True if the user chose an affirmative value on the dialog.

    The questions that can be asked are:
    # 1: Yes/No
    # 2: Ok/Cancel
    # 3: Retry/Cancel
    # 4: Yes/No/Cancel
    """

    node_base_data = {
        "prop":   {
            "caption":     "Node.Window.Tk.Dialog",
            "message":     "Node.Window.Tk.Dialog.Message",
            "optionindex": 4
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    node_signals = [
        "_popup_answer"
    ]

    def __init__(self, data=node_base_data, parent=None):
        super().__init__(data,parent)
        self.result = None
    
    def popup(self):
        if self.properties["optionindex"] == 1:
            func=askyesno(self.properties["caption"], self.properties["message"])
        if self.properties["optionindex"] == 2:
            func=askokcancel(self.properties["caption"], self.properties["message"])
        if self.properties["optionindex"] == 3:
            func=askretrycancel(self.properties["caption"], self.properties["message"])
        if self.properties["optionindex"] == 4:
            func=askyesnocancel(self.properties["caption"], self.properties["message"])
        self.call_signal("_popup_answer", func)
        self.result = func
        return func
