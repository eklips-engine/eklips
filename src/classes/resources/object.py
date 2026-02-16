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
    _can_init_script = True
    obj_id           = None
    _function_queue  = []
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
            self._script_path = None
            return
        
        exec(src, self.__dict__, self.__dict__)

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
        if not function in self.__dict__:
            return
        mobj = types.MethodType(self.__dict__[function], self)
        try:
            if len(args) == 0:
                return mobj() 
            else:
                return mobj(*args)
        except:
            if engine.debug.avoid_error_mercy:
                raise ScriptError(f"The Script {self.script_path} tried to call '{function}{tuple(args)}' but it failed horribly")
    
    def call_signal(self, signal_name, *args):
        """Call an attached signal from the attached Script, if it exists."""
        if not self.signals.get(signal_name, None) in self.__dict__:
            return
        mobj = types.MethodType(self.__dict__[self.signals[signal_name]], self)
        try:
            if len(args) == 0:
                return mobj() 
            else:
                return mobj(*args)
        except:
            if engine.debug.avoid_error_mercy:
                raise ScriptError(f"The Script {self.script_path} tried to call '{signal_name}{tuple(args)}' but it failed horribly")
    
    def call_deferred(self, function, *args, is_signal = False) -> None:
        """Call a function/signal from the attached Script after the Script has finished its process tick."""
        self._function_queue.append([function, args, is_signal])

    def update(self):
        """Run the `_process()` function on the Script and call queued functions. This is called every frame of the Object/Node's existence."""
        # Check if i have to be freed
        if not self._runnable:
            self._free()
            return
        
        try:
            self._process(self, engine.delta)
        except Exception as err:
            pass

        for info in self._function_queue:
            if info[2]:
                self.call_signal(info[0], info[1])
            else:
                self.call(info[0], info[1])
        self._function_queue.clear()
    
    def _setup_properties(self):
        # Setup properties
        for key in self._properties_onready:
            if key in ["children","parent","signals","type"]:
                continue
            self.set(key, self._properties_onready[key])
        
        # Call _onready
        try:
            self._onready(self)
        except:
            pass