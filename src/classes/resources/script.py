# Import singleton
import classes.singleton as engine

# Classes
class Script:
    """
    This class handles Python Script files.
    
    A script extends the functionality of all objects that instantiate it.
    Please do not try initializing a Script by this Object directly. It will not do anything.

    Instead, set your Object's `script_path` property to the path of the Script.

    Also, you can type `fun` or `fn` instead of `def`, `null` instead of None,
    `true` instead of True, and `false` instead of False. Why? cuz why not.
    """
    file_path        = None
    source_code      = "# Empty.. Please initialize the Script in your Object."
    _can_init_script = False
    _namespace       = {}
    _function_queue  = []

    def __init__(self):
        self._namespace      = {"engine": engine, "null": None, "true": True, "false": False}
        self.source_code     = "# Empty.. Please initialize the Script in your Object."
        self._function_queue = []
        self.file_path       = None