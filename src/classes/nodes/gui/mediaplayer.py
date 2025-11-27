# Import libraries
import pyglet as pg
from pygame import Sound, Channel

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class PlayerError(Exception):
    """Exception class for problems caused in the `MediaPlayer` Node."""

class MediaPlayer(CanvasItem):
    """
    ## A Media Player.

    This is a Node that can play video and audio globally.
    """
    def __init__(self, properties={}, parent=None, children=None):
        self._media  : str                    = ""
        self._playcounter : int               = 0
        self._playing : bool                  = True
        self._ogsize : list[int]              = [320,240]
        self._volume : float | int            = 0
        self._sound  : Sound                  = None
        self._video  : engine.pvd.VideoPyglet = None
        self.channel : Channel                = None
        self._autostart : bool                = False
        self._loops  : int                    = 0

        super().__init__(properties, parent, children)
        self._make_new_sprite()
        
        self.media_id = engine.sid
        engine.sid   += 1
        self.channel  = Channel(self.media_id)
    
    def _setup_properties(self):
        super()._setup_properties()
        if self.auto_start:
            self.play()
    
    @export(0,    "int",   "int")
    def loops(self) -> int: return self._loops
    @loops.setter
    def loops(self, value): self._loops = value

    @export(None, "str",   "file_path/med")
    def media(self) -> str:
        """Filepath of media. Read-write."""
        return self._media
    
    @media.setter
    def media(self, value):
        self._media = value
        extensions  = engine.loader.extensions
        extension   = value.split(".")[-1]

        if extension in extensions["vid"]:
            self._sound  = None
            self._video  = engine.pvd.VideoPyglet(engine.loader._get_true_path(self._media))
            self._ogsize = self._video.current_size
            self._video.stop()
        elif extension in extensions["sfx"]:
            if self._video:
                self.stop()
            self._video = None
            self._sound = engine.loader.load(value)
        else:
            raise PlayerError(f"what the hell is an .{extension} file")

    def play(self, keep_play_counter=False):
        """
        Play the Media using the Node's properties.

        .. keep_play_counter:: Internal argument to decide if the Node should play the Media while keeping the `self._playcounter` value and not reset it.
        """
        self._playing     = True
        if not keep_play_counter:
            self._playcounter = 0
        if self._sound:
            self.channel.play(self._sound)
        if self._video:
            self._video.play()
        
    def restart(self):
        """
        Restart the Media.
        """
        if self._sound:
            self.channel.stop()
            self.channel.play()
        if self._video:
            self._video.restart()
    
    def stop(self):
        """
        Stop the Media.
        """
        self._playing = False
        if self._sound:
            self.channel.stop()
        if self._video:
            self._video.stop()
    
    def pause(self):
        """
        Pause the Media.
        """
        if self._sound:
            self.channel.pause()
        if self._video:
            self._video.pause()
    
    def resume(self):
        """
        Resume the Media.
        """
        if self._sound:
            self.channel.unpause()
        if self._video:
            self._video.resume()
    
    @property
    def busy(self) -> bool:
        """
        True if media is playing. Read-only
        """
        if self._sound:
            return self.channel.get_busy()
        if self._video:
            return self._video.active
    
    def update(self):
        super().update()
        if self._video:
            if self._video.active:
                self._video._update()
                self.draw()
        else:
            if self._playing:
                self._playcounter += 1
                self.playing       = False
                if self._playcounter < self.loops or self.loops < 0:
                    self.restart()
    
    def draw(self):
        if self._video.frame_surf:
            self.w, self.h    = self._ogsize
            self.sprite.image = self._video.frame_surf
            self._draw()
    
    def _draw(self, image):
        return engine.display.blit(
            surface        = image,
            transform      = self,
            window_id      = self._drawing_wid,
            sprite         = self.sprite,
            ignore_scaling = True
        )
    
    def _set_size(self,w,h):
        size = [round(w),round(h)]
        if self._video:
            self._video.resize(size)

    @export(1.0, "float", "float")
    def volume(self) -> int:
        return self._volume
    @volume.setter
    def volume(self, value : int | float | None):
        self._volume = value
        if self._sound:
            self.channel.set_volume(value)
        if self._video:
            self._video.set_volume(value)
    
    @export(False, "bool", "bool")
    def auto_start(self):
        return self._autostart
    @auto_start.setter
    def auto_start(self, value):
        self._autostart = value