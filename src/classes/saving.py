## Import all the libraries
import json, os
from functools import reduce
import operator
import classes.singleton as engine

## Savefile class
class Savefile:
    """
    A class to store a project's save information.
    """
    print(" ~ Initialize Savefile")
    
    def __init__(self):
        self.save_dir  = engine.game.save_dir                        # Save file directory
        self.savefpath = f"{self.save_dir}/save.json"                # Save file path
        self.base_save = f"{engine.game.project_dir}/base_save.json" # Empty save file path
        self.savefile  = {}
        self.load_data()
    
    def load_data(self):
        """Load the save data from the savefile."""
        try:
            self.savefile = json.loads(open(self.savefpath).read())
        except:
            self.savefile = json.loads(open(self.base_save).read())
    
    def save_data(self):
        """Save the loaded data to the savefile."""
        try:
            with open(self.savefpath, "w") as f:
                f.write(json.dumps(self.savefile))
        except:
            pass
    
    def get(self, key, fallback=0):
        """Get a value (e.g. `settings/anti_aliasing`) from the savefile.

        Args:
            key: The key to get.
            fallback: The value to use as a fallback."""
        try:
            return reduce(operator.getitem, key.split('/'), self.savefile)
        except:
            self.set(key, fallback)
            return fallback

    def set(self, key, value):
        """Set a value (e.g. `settings/anti_aliasing`) from the savefile.
        
        Args:
            key: The key to modify.
            value: The value to use."""
        try:
            keys = key.split('/')
            d = self.savefile
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = value
        except:
            pass