## Import all the libraries
import pyglet as pg, gc, struct, types
from anytree import NodeMixin
from SpecialIsResourceDataLoadable import IS_IT as IS_EXECUTABLE
import classes.Singleton as engine

## Object class
class Object:
    """
    This is the class that is inherited by every Node, and Resource.
    This class is pretty simple, it stores data, the class name and properties.
    It comes with no default data, so everything has to be specified on its own.

    Properties commented "virtual" must be edited to have any effect.
    """

    obj_base_data = {
        "prop":   {},
        "data":   {
            "object": None,
            "path":   "res://"
        },
        "meta":   {
            "kind": None,
            "name": "Object"
        },
        "script": None
    }

    def __init__(self, data=obj_base_data):
        global obj_ids

        self.scene            = engine.scene
        self._data_all        = data
        self.data             = data["data"]
        self.metadata         = data["meta"]
        self.properties       = data["prop"]
        self.scriptpath       = data["script"]
        self.stop_running     = False
        self.hook_script      = {}
        self.call_deferr_list = []
        self._obj_id          = engine.obj_ids
        self.runtime_data     = {}
        engine.obj_ids    += 1
        self.script           = None
        self._init_script()
        self._onready()
    
    ## Script related
    def call(self, method, *args):
        """Call a method from the script"""
        if self.script:
            if method in self.script.namespace:
                mobj = types.MethodType(self.script.namespace[method], self)
                if len(args) == 0:
                    return mobj() 
                else:             
                    return mobj(*args)

    def call_deferred(self, method, args):
        """Call a method from the script after the object is done updating"""
        self.call_deferr_list.append([method, args])
    
    def _init_script(self):
        """Initialize the script attached to the Object"""
        if self.scriptpath:
            self.script = engine.resource_loader.load(self.scriptpath, force_new_resource=True)
            self.script.init_param(self.properties)
    
    def _onready(self):
        """Call _onready function in script"""
        self.call("_onready")
    
    def _process(self, delta):
        """Call _process function in script"""
        # Whoops!
        if self.stop_running:
            return
        
        # Call the process function
        self.call("_process", delta)

        # Call any deferred functions
        for i in self.call_deferr_list:
            self.call(i[0], i[1])
        self.call_deferr_list.clear()
    
    ## Other
    def _free(self):
        del self
        gc.collect()
    
    def free(self):
        """Free object from memory"""
        self.stop_running = True
        self._free()
        
    def get_class(self):
        """Get name of Object class."""
        return self.__class__.__name__
    
    def get_instance_id(self):
        """Get UID of Object."""
        return self._obj_id

    ## Get/Set
    def to_string(self):
        """Get string data of name and UID."""
        return f"<{self.get_class()}:{self.get_instance_id()}>"
    
    def get(self, property, default=None):
        """Get a property, returns default if not found."""
        return self.properties.get(property, default)
    
    def set(self, property, value):
        """Set a property."""
        self.properties[property] = value
    
    ## Get engine singleton
    def get_engine_singleton(self):
        """Get engine singleton"""
        return engine

    ## Virtual
    def serialize(self, path):
        """Save the object into a file"""
        with open(path, "wb") as f:
            f.write(b"OBJ")