# Import components
import classes.singleton as engine
import gc, types
from classes.locals       import *
from classes.customprops  import export, _exportmeta
from classes.log          import *

# Classes
class ScriptError(Exception):
    pass

class Object(metaclass=_exportmeta):
    """
    Base class for almost all other classes in the engine.

    This class is the ancestor for classes that can be programmable and interacts with the Engine's libraries, components, etc..
    Each class may define new properties, methods or signals, which are available to all inheriting classes. For example, a Sprite instance is able to call Object.call_deferred() because it inherits from Object.

    You can create new instances, using `Object(properties)`.
    To delete an Object instance, call `free()`. This is necessary for most classes inheriting Object, because they do not manage memory on their own, and will otherwise cause memory leaks when no longer used.
    Objects can have a `Script` resource attached to them. Once the Script is instantiated, it effectively acts as an extension to the base class, allowing it to define and inherit new properties, methods and signals.
    
    If you are setting up an Object, don't forget to call `_setup_properties()` after initializing the Object.
    """
    _runnable        = True
    _script_path     = None
    _script          = None
    _can_init_script = True
    obj_id           = None
    _properties      = {}   # NOT actual property values, but instead info of this classes properties
    
    # Property related functions
    def get(self, name, fallback=None):
        """Get the Object property `name`, if non-existent, return `fallback`."""
        return getattr(self, name, fallback)
    
    def set(self, name, value):
        """Set the Object property `name` into `value`."""
        setattr(self, name, value)
    
    def get_property_list(self):
        return self._properties.keys()
    
    # Properties
    @export(None,"str","str")
    def name(self) -> str: return self._name
    
    @property
    def script(self):
        return self._script
    @export(None,"str","file_path/ekl")
    def script_path(self) -> str: return self._script_path

    @name.setter
    def name(self, value):   self._name = value
    @script.setter
    def script(self, value): raise ScriptError("Object property 'script' does not have a setter. Instead, set the 'script_path' property to the path of the script needed.")
    @script_path.setter
    def script_path(self, path : str):
        if not path: return

        self._script_path = path
        try:
            src  = engine.loader.load(path, force_new_resource=True)
        except:
            src  = ""
            path = None

        if not path or not src:
            if self._script:
                self._script.free()
            self._script       = None
            return
        
        self._script : engine.resources.Script = engine.resources.Script()

        self._script.file_path   = path
        self._script.source_code = src.replace("fun ", "def ").replace("fn ", "def ")
        
        exec(self._script.source_code, self._script._namespace, self._script._namespace)

    # Init
    def __init__(self, properties={}):
        self._name               = self.get_class_name()
        self._properties_onready = properties

        # Set Unique ID
        self.uid    = engine.uid
        engine.uid += 1

        # Add signals
        self.signals = properties.get("signals", {})

    # Get class name
    def get_class_name(self) -> str: 
        """Return the name of the Object. (e.g. Object, Node...)"""
        return self.__class__.__name__
    
    # Memory related
    def _free(self):
        self._runnable = False
        engine.uid -= 1
        del self
        gc.collect()
    
    def free(self):
        """Free the object from memory."""
        self._runnable = False
        self._free()

    # Script related
    def call(self, function, *args):
        """Call a function from the attached Script, if it exists."""
        if not self._script:
            return
        if not self._script._namespace:
            return
        if not function in self._script._namespace:
            return
            raise ScriptError(f"The Script {self._script.file_path} tried to call '{function}{tuple(args)}' but failed as the function doesn't exist in the Script.")
        mobj = types.MethodType(self._script._namespace[function], self)
        try:
            if len(args) == 0:
                return mobj() 
            else:
                return mobj(*args)
        except:
            if engine.debug.avoid_error_mercy:
                raise ScriptError(f"The Script {self._script.file_path} tried to call '{function}{tuple(args)}' but it failed horribly")
    
    def call_signal(self, signal_name, *args):
        """Call an attached signal from the attached Script, if it exists."""
        if not self._script:
            return
        if not self._script._namespace:
            return
        if not self.signals.get(signal_name, None) in self._script._namespace:
            return
        mobj = types.MethodType(self._script._namespace[self.signals[signal_name]], self)
        try:
            if len(args) == 0:
                return mobj() 
            else:
                return mobj(*args)
        except:
            if engine.debug.avoid_error_mercy:
                raise ScriptError(f"The Script {self._script.file_path} tried to call '{signal_name}{tuple(args)}' but it failed horribly")
    
    def call_deferred(self, function, *args, is_signal = False) -> None:
        """Call a function/signal from the attached Script after the Script has finished its process tick."""
        self._function_queue.append([function, args, is_signal])

    def getvar(self, name, default = None):
        """Get a variable from the attached Script."""
        return self._script._namespace.get(name, default)

    def setvar(self, name, value):
        """Set a variable from the attached Script."""
        self._script._namespace[name] = value

    def _process(self):
        """Run the `_process()` function on the Script and call queued functions. This is called every frame of the Object/Node's existence."""
        if not self._script:
            return
        
        try:
            self.call("_process", engine.delta)
        except Exception as err:
            pass

        for info in self._script._function_queue:
            if info[2]:
                self.call_signal(info[0], info[1])
            else:
                self.call(info[0], info[1])
        self._script._function_queue.clear()
    
    def _onready(self):
        """Run the `_onready()` function on the Script. This should only be called after the Object/Node is ready."""
        try:
            self.call("_onready")
        except Exception as err:
            pass
    
    def _setup_properties(self):
        # Setup properties
        for key in self._properties_onready:
            if key in ["children","parent","signals","type"]:
                continue
            self.set(key, self._properties_onready[key])
        self._onready()