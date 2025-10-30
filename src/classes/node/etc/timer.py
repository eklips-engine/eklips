## Import inherited
from classes.node.node import Node

## Import engine singleton and others
import pyglet as pg
import time
import classes.singleton as engine
from classes import resources

## Node
class Timer(Node):
    """
    ## A Timer.

    It's a fucking timer??
    """

    node_base_data = {
        "prop":   {
            "duration_ep": 0,          # in seconds
            "only_once":   False,
            "autostart":   False,
            "play_global": False
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    def __init__(self, data=node_base_data, parent=None):
        global player_global
        super().__init__(data,parent)
        self.is_playedyet  = False
        self.playing       = False       #... is timing?
        self.start_epoch   = engine.clock.time() #what the epoch was when timer started
        self.current_epoch = engine.clock.time() #current time
    
    def start(self):
        self.start_epoch = engine.clock.time()
        self.playing     = True
    
    def get_time_since_start(self):
        return self.current_epoch-self.start_epoch
    
    def format_time(self, epoch_time):
        """Format an epoch timestamp in seconds"""
        return float(f"{epoch_time:.6f}".lstrip("-"))
    
    def stop(self): self.playing = False

    def update(self, delta):
        super().update(delta)
        self.current_epoch = engine.clock.time()
        if not self.is_playedyet and self.properties["autostart"]:
            self.start()
            self.is_playedyet=True
        if self.playing:
            if self.get_time_since_start()>self.properties["duration"]:
                self.stop()