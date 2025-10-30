import time
import pyglet as pg
import classes.singleton as engine

pg.clock.Clock
class Time:
    """A basic time module to do time like stuff"""
    def __init__(self):
        self.is_stopped = False
        self.init_time  = time.time()
        self.first      = True
        self._time      = time.time()
        self._timeg     = time.time()
        self.last_dt    = time.time()
        self.ldg        = time.time()
        self.playingvfx = False
        self.plvfxsec   = 0
        self.framec     = 1
        self.ftimer     = 0
        self.frames     = {}
        for i in range(1,17):
            self.frames[i] = engine.resource_loader.load(f"root://internal/anim/{i}.png")

    def time(self):
        return self._time
    
    def get_time_gap(self, past, present):
        return abs(present-past)
    
    def _get_m_s(self, seconds): # Seconds (180) -> 3, 0 (Minute, Second)
        mins, secs = 0, 0
        for i in range(seconds):
            secs += 1
            if secs < 59:
                secs  = 0
                mins += 1
        return mins, secs
    
    def format_time(self, seconds):
        minutes, secs = self._get_m_s(seconds)
        return f"{'0' if minutes < 10 else ''}{minutes}:{'0' if secs < 10 else ''}{secs}"
    
    def _play(self):
        sound = engine.resource_loader.load("root://internal/sfx/dswrld.mp3").get()
        sound.play()
        self.playingvfx = True
        self.framec     = 1
        self.ftimer     = 0
    
    def skip(self, seconds):
        self._play()
        self.plvfxsec += seconds
    
    def time_toggle(self):
        self.is_stopped   = not self.is_stopped
        if self.is_stopped:
            self._play()
            engine.pacing = 0
        else:
            engine.pacing = engine.old_pacing
    
    def get_delta(self):
        current_dtt      = time.time()
        current_dt       = self.time()

        gap              = self.get_time_gap(self.last_dt, current_dtt)
        tzgap            = self.get_time_gap(gap,          self.get_time_gap(self.ldg, current_dt))

        if round(tzgap) > 0:
            engine.event.on_abnormal_time(tzgap)
        
        engine.delta     = gap * engine.pacing + tzgap # <- Delta time variable (0.1....)
        engine.truedelta = gap                 + tzgap # <- True deltaTime variable (not affected by things like pacing, etc)
        
        self._time      += gap * engine.pacing
        self.last_dt     = current_dtt        
        self.ldg         = current_dt         

        if self.playingvfx:
            self.ftimer += gap * engine.pacing
            if self.ftimer > 1 / 20:
                self.ftimer  = 0
                self.framec += 1
            if self.framec > 15:
                self.playingvfx = False
                self.plvfxsec   = 0
                self.framec     = 16
            if self.framec == 11:
                self._time += self.plvfxsec
            engine.interface.blit(self.frames[self.framec], [0,0], anchor="center", layer=engine.interface.layer_amount-1)
    
    @property
    def elapsed_time(self):
        return self.get_time_gap(self.init_time, self.time())