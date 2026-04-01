## Import libraries
from classes.nodes.twod.collisionbox import *

## Classes
class Body(CollisionBox):
    """
    A CollisionBox which abides the laws of 2D physics.
    """

    @property
    def velocity(self):
        return self._velocity
    @velocity.setter
    def velocity(self, value):
        self._velocity = value
    @export(False, "bool", "bool")
    def noclip(self):
        return self._noclip
    @noclip.setter
    def noclip(self, value):
        self._noclip = value
    @export(195, "int", "slider")
    def gravity(self):
        """The strengh of gravity."""
        return self._gravity
    @gravity.setter
    def gravity(self, value):
        self._gravity = value
    @export(180, "int", "slider")
    def velocity_cap(self):
        """The cap on the Y velocity."""
        return self._velcap
    @velocity_cap.setter
    def velocity_cap(self, value):
        self._velcap = value
    
    @property
    def on_ground(self):
        return self._onground
    @property
    def on_wall(self):
        return self._onwall
    
    def __init__(self, properties={}, parent=None):
        self._velocity = [0,0]
        self._noclip   = False
        self._onground = False
        self._gravity  = 195
        self._velcap   = 180
        self._onwall   = False
        super().__init__(properties, parent)
    
    def update(self):
        super().update()
        if not self.processable:
            return
        
        if self.velocity[1]   > self.velocity_cap:
            self._velocity[1] = self.velocity_cap
        if not self.noclip:
            self.x += self.velocity[0] * engine.delta
            if self.world.get_collisions(self):
                self.x           -= self._velocity[0]
                self._velocity[0] = 0
                self._onwall      = True
            else:
                self._onwall      = False
            
            self.y -= self.velocity[1] * engine.delta
            if self.world.get_collisions(self):
                self.y           += self._velocity[1]
                self._velocity[1] = 0
                self._onground    = True
            else:
                self._onground    = False
        else:
            self.x += self._velocity[0] * engine.delta
            self.y -= self._velocity[1] * engine.delta
        
        self._velocity[0] += (-self.velocity[0])                / (engine.fps*0.25)
        self._velocity[1] += ((-self.gravity)-self.velocity[1]) / (engine.fps*0.25)