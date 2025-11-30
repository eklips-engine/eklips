# Import inherited
import time
from classes.nodes.node import *

# Classes
class Timer(Node):
    def __init__(
            self,
            properties : dict                   = {}, 
            parent     : NodeMixin       | None = None,
            children   : list[NodeMixin] | None = None
        ):
        super().__init__(properties, parent, children)
        self._start_time : int   = 0
        self._duration   : float = 0.0
        self._timespan   : float = 0.0
        self._paused     : bool  = False
        self._autostart  : bool  = False
        self._started    : bool  = False
    
    def start(self):
        """Start the timer."""
        if self._started:
            self.stop()
            return
        self._timespan   = 0.0
        self._started    = True
        self._start_time = time.time()
        self._paused     = False
    def stop(self):
        """Stop the timer."""
        self._timespan   = 0.0
        self._started    = False
        self._start_time = time.time()
        self._paused     = False
    def pause(self):
        """Pause the timer."""
        if not self._started:
            return
        self._paused = True
    def resume(self):
        """Unpause the timer."""
        if not self._started:
            return
        self._paused = False
    
    def update(self):
        # Update script
        super().update()

        # Add seconds to the Timer if the Timer has started.
        if self.started:
            if self.paused:
                return
            self._timespan += engine.delta
    
    @property
    def paused(self):
        """Returns True if the Timer is paused."""
        if self._started:
            return self._paused
        return False
    @property
    def started(self):
        """Returns True if the Timer has started."""
        return self._started
    @property
    def timespan(self):
        """How much time has passed since the timer has started. Returns 0 if timer hasn't started."""
        if self._started:
            return self._timespan
        return 0

    @export(10, "float", "time")
    def duration(self):
        """How many seconds the timer should last."""
        return self._duration
    @duration.setter
    def duration(self, value):
        self._duration = value
    @export(False, "bool", "bool")
    def auto_start(self):
        """If the Timer should automatically start when created."""
        return self._autostart
    @auto_start.setter
    def auto_start(self, value):
        self._autostart = value
    
