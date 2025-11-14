# Import components
import classes.singleton as engine
import gc, types
from classes.fakes.script import _ScriptDoc

# Classes
class ScriptError(Exception):
    pass

class Object:
    """
    Base class for almost all other classes in the engine.

    This class is the ancestor for classes that can be programmable and interacts with the Engine's libraries, components, etc..
    Each class may define new properties, methods or signals, which are available to all inheriting classes. For example, a Sprite2D instance is able to call Node.add_child() because it inherits from Node.

    You can create new instances, using `Object()`.
    To delete an Object instance, call `free()`. This is necessary for most classes inheriting Object, because they do not manage memory on their own, and will otherwise cause memory leaks when no longer used.
    Objects can have a `Script` resource attached to them. Once the Script is instantiated, it effectively acts as an extension to the base class, allowing it to define and inherit new properties, methods and signals.
    """
    base_properties = {
        "name":   "Object",
        "script": None
    }
    _runnable        = True
    _script_path     = None
    _script          = None
    _can_init_script = True
    obj_id           = None
    @property
    def script(self) -> _ScriptDoc:
        return self._script
    @property
    def script_path(self) -> str:
        return self._script_path
    
    @script.setter
    def script(self):
        raise ScriptError("Object property 'script' does not have a setter. Instead, set the 'script_path' property to the path of the script needed.")
    @script_path.setter
    def script_path(self, path : str):
        self._script_path = path
        try:
            src  = engine.loader.load(path, force_new_resource=True)
        except:
            src  = None
            path = None

        if not path or not src:
            if self._script:
                self._script.free()
            self._script       = None
            return
        
        self._script : engine.resources.Script = engine.resources.Script()

        self._script.file_path   = path
        self._script.source_code = src
        
        exec(self._script.source_code, self._script._namespace, self._script._namespace)

        self._onready()

    def __init__(self, properties=base_properties):
        self.properties  = properties
        engine.uid      += 1
        self.uid         = engine.uid
        self.signals     = properties.get("signals", {})

    def get_class_name(self) -> str: 
        """Return the name of the Object. (e.g. Object, Node...)"""
        return self.__class__.__name__

    def _free(self):
        del self
        gc.collect()
    
    def free(self):
        """Free the object from memory."""
        self._runnable = False
        self._free()
    
    def get(self, property, fallback=None):
        """Get the Object property `property`, if non-existent, return `fallback`."""
        return self.properties.get(property,fallback)
    
    def set(self, property, value):
        """Set the Object property `property` into `value`."""
        self.properties[property] = value

    def call(self, function, *args):
        """Call a function from the attached Script, if it exists."""
        if not self._script:
            return
        if not self._script._namespace:
            return
        if not function in self._script._namespace:
            raise ScriptError(f"The Script {self._script.file_path} tried to call '{function}{tuple(args)}' but failed as the function doesn't exist in the Script.")
        mobj = types.MethodType(self._script._namespace[function], self)
        if len(args) == 0:
            return mobj() 
        else:
            return mobj(*args)
    
    def call_signal(self, signal_name, *args):
        """Call an attached signal from the attached Script, if it exists."""
        if not self._script:
            return
        if not self._script._namespace:
            return
        if not self.signals.get(signal_name, None) in self._script._namespace:
            return
        mobj = types.MethodType(self._script._namespace[self.signals[signal_name]], self)
        if len(args) == 0:
            return mobj() 
        else:
            return mobj(*args)
    
    def call_deferred(self, function, *args, is_signal = False) -> None:
        """Call a function/signal from the attached Script after the Script has finished its process tick."""
        self._function_queue.append([function, args, is_signal])

    def _process(self):
        """Run the `_process()` function on the Script. This is called every frame of the Object/Node's existence."""
        if not self._script:
            return 
        try:
            self.call("_process", engine.delta)
        except:
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
        except:
            pass