## Import libraries
from classes.nodes.gui.canvasitem import *

## Classes
class MediaPlayer(CanvasItem):
    """
    A Media Player.

    This is a Node that can play video and audio globally.
    """
    _isblittable = True
    
    def __init__(self, properties={}, parent=None):
        self._media       : str                    = ""
        self._playcounter : int                    = 0
        self._rpop        : bool                   = True
        self._playing     : bool                   = True
        self._ogsize      : list[int]              = [320,240]
        self._volume      : float | int            = 0
        self._sound       : pg.media.Player        = None
        self._video       : engine.pvd.VideoPyglet = None
        self._autostart   : bool                   = False
        self._loops       : int                    = 0

        super().__init__(properties, parent)
    
    def _setup_properties(self, scene=None):
        super()._setup_properties(scene)
        if self.auto_start:
            self.play()
    
    @export(0,     "int",   "int")
    def loops(self) -> int:
        """How many times the Media should loop. Set to -1 for infinite."""
        return self._loops
    @loops.setter
    def loops(self, value): self._loops = value

    @export(True, "bool",  "bool")
    def reset_playback_on_play(self) -> bool:
        """If the playback should restart if the `play()` function is called.

        If False, `play()` will return if `busy` is true.
        If True, the playback will restart. This may lead to noise if `play()` is spammed."""
        return self._rpop
    @reset_playback_on_play.setter
    def reset_playback_on_play(self, value): self._rpop = value

    @export(None,  "str",   "file_path/med")
    def media(self) -> str:
        """Filepath of the attached media file. Read-write."""
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
            self._sound = pg.media.Player()
            self._sound.queue(engine.loader.load(self.media))
        else:
            raise PlayerError(f"File format {extension} unknown")

    def play(self, keep_play_counter=False):
        """
        Play the attached Media file using the Node's properties.

        Args:
            keep_play_counter:
                Internal argument to decide if the Node should play the attached Media file while keeping the `self._playcounter` value and not resetting it. This is manually used by the `loops` property.
        """

        if self.busy and not self.reset_playback_on_play:
            return

        self._playing     = True
        if not keep_play_counter:
            self._playcounter = 0
        
        if self._video:
            self._video.play()
            if not self.citem:
                self._make_new_item()
            self._set_visible(self.visible)
        else:
            self._sound.play()
            self._set_visible(False)
        
    def restart(self):
        """Restart the attached Media file."""
        if self._video:
            self._video.restart()
        else:
            self.channel.stop()
            self.channel.play(self._sound)
    
    def stop(self):
        """Stop the attached Media file."""
        self._playing = False
        if self._video:
            self._video.stop()
        else:
            self._sound.pause()
    
    def pause(self):
        """Pause the attached Media file."""
        if self._video:
            self._video.pause()
        else:
            self._sound.pause()
    
    def resume(self):
        """Resume the attached Media file."""
        if self._video:
            self._video.resume()
        else:
            self._video.resume()
    
    @property
    def busy(self) -> bool:
        """True if media is playing. Read-only"""
        if self._video:
            return self._video.active
        else:
            return self._sound.playing
    
    def update(self):
        super().update()
        
        ## Handle playback
        if self.busy:
            if self._video:
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
            self.citem.image = self._video.frame_surf
            self._set_anchors()
            super().draw()
    
    def _set_size(self,w,h):
        if self._video:
            self._w, self._h = self._ogsize
            self._video.resize(self.size)

    @export(1.0, "float", "float")
    def volume(self) -> int:
        """Volume of the attached Media file."""
        return self._volume
    @volume.setter
    def volume(self, value : int | float | None):
        self._volume = value
        if self._video:
            self._video.set_volume(value)
        else:
            self._sound.volume = value
    
    @export(False, "bool", "bool")
    def auto_start(self):
        """If the Media should automatically start when created."""
        return self._autostart
    @auto_start.setter
    def auto_start(self, value):
        self._autostart = value
    
    def _free(self):
        self.stop()
        if self._video:
            self._video.close()
        self._sound.delete()
        super()._free()