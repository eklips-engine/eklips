# Import inherited
from classes.resources.object import *
import types

# Classes
class Script(Object):
    """
    This class handles Python Script files.
    
    A script extends the functionality of all objects that instantiate it.
    Please do not try initializing a Script by this Object directly. It will throw an error.

    Instead, set your Object's `script_path` property to the path of the Script.
    If the property `source_code` is a string, it will override the code that `path` has.
    """
    base_properties = {
        "name":        "Script",
        "path":        None,
        "source_code": None
    }
    file_path        = None
    source_code      = "# Empty.. Please initialize the Script in your Object."
    _can_init_script = False
    _namespace       = {"engine": engine}
    _function_queue  = []