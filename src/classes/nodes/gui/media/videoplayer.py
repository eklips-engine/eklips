# Import libraries
import pyglet as pg
from pygame import Sound, Channel

# Import inherited
from classes.nodes.gui.canvasitem import *

# Classes
class VideoError(Exception):
    pass

class VideoPlayer(CanvasItem):
    """
    ## A Video Player.

    This is a Node that can play video and display it on the screen.
    For playing Audio, see AudioPlayer.
    """
    base_properties  = {
        "name":       "VideoPlauer",
        "transform":  base_transform,
        "media":      "root://_assets/error.mp4",
        "loops":      0,
        "volume":     0.5,
        "script":     None,
        "auto_start": False,
    }
    _playcounter : int                    = 0
    _playing     : bool                   = False
    _video       : engine.pvd.VideoPyglet = None
    _media       : str                    = ""
    _ogsize      : list[int]              = [100,100]
    _tmpfilepath : str                    = None
    _ignore_size_if_drawing               = True
    
    def __init__(self, properties=base_properties, parent=None):
        self.media = properties["media"]
        super().__init__(properties, parent)
        self._make_new_sprite()
        if properties["auto_start"]:
            self.play()
    
    def update(self):
        super().update()
        if self._video.active:
            self._video._update()
            self.draw(self._video.frame_surf)
        else:
            if self._playing:
                self._playcounter += 1
                self.playing       = False
                if self._playcounter < self.get("loops",0) or self.get("loops", 0) == -1:
                    self.restart()
    
    def draw(self, image):
        if image:
            self.w, self.h = self._ogsize
            self._draw(image)
    
    def _draw(self, image):
        return engine.display.blit(
            surface        = image,
            transform      = self,
            window_id      = self.window_id,
            sprite         = self.sprite,
            group          = self._canvas_layer,
            ignore_scaling = True
        )
    
    def _set_size(self,w,h):
        self._video.resize([round(w),round(h)])
    
    @property
    def video(self) -> engine.pvd.VideoPyglet:
        """Video object. Read-only."""
        return self._video
    @video.setter
    def video(self,_): raise VideoError("Please replace the video using `self.media` instead.")
    
    @property
    def media(self) -> str:
        """Filepath of video. Read-write."""
        return self._media
    @media.setter
    def media(self, value):
        self._media  = value
        self._video  = engine.pvd.VideoPyglet(engine.loader._get_true_path(self._media))
        self._ogsize = self._video.current_size
        self._video.stop()
    
    def play(self):
        """
        Play the Video using the Node's properties.
        """
        self._playing     = True
        self._playcounter = 0
        self.volume       = None
        self._video.play()
    
    def restart(self):
        """
        Restart the Video.
        """
        self._video.restart()
    
    def stop(self):
        """
        Stop the Video.
        """
        self._playing     = False
        self._video.stop()
    
    def pause(self):
        """
        Pause the Video.
        """
        self._video.pause()
    
    def resume(self):
        """
        Resume the Video.
        """
        self._video.resume()
    
    def set_volume(self, volume=None):
        """
        Set the Video volume. Set volume to None to use Node's properties.
        """
        if volume != None:
            self._video.set_volume(volume)
            return
        self._video.set_volume(self.get("volume", 0.5))
    
    @property
    def busy(self):
        """
        True if Video is playing. Read-only
        """
        return self._video.active

    @property
    def volume(self) -> int:                      return self._video.volume
    @volume.setter
    def volume(self, value : int | float | None): self.set_volume(value)