# Import libraries
import pyglet as pg
from pygame import Sound, Channel

# Import inherited
from classes.nodes.node  import *

# Classes
class AudioError(Exception):
    pass

class AudioPlayer(Node):
    """
    ## An Audio Player.

    This is a Node that can play audio globally.
    For playing Video, see VideoPlayer.
    """
    base_properties = {
        "name":       "AudioPlayer",
        "media":      "root://_assets/error.mp3",
        "loops":      0,
        "volume":     0.5,
        "script":     None,
        "auto_start": False,
    }
    sound   : Sound   = None
    channel : Channel = None
    _media  : str     = ""
    
    def __init__(self, properties=base_properties, parent=None):
        super().__init__(properties, parent)
        self._media   = properties["media"]
        self._sound   = engine.loader.load(self._media)
        self.sound_id = engine.sid
        engine.sid   += 1
        self.channel  = Channel(self.sound_id)
        if properties["auto_start"]:
            self.play()
    
    @property
    def sound(self):
        """Sound object. Read-only."""
        return self._sound
    @sound.setter
    def sound(self,_): raise AudioError("Please replace the audio using `self.media` instead")
    
    @property
    def media(self):
        """Filepath of sound. Read-write."""
        return self._media
    @media.setter
    def media(self, value):
        self._media = value
        self._sound = engine.loader.load(value)

    def play(self):
        """
        Play the Sound using the Node's properties.
        """
        self.volume = None
        self.channel.play(self.sound, self.get("loops",0))
    
    def stop(self):
        """
        Stop the Sound.
        """
        self.channel.stop()
    
    def pause(self):
        """
        Pause the Sound.
        """
        self.channel.pause()
    
    def resume(self):
        """
        Resume the Sound.
        """
        self.channel.unpause()
    
    def set_volume(self, volume=None):
        """
        Set the Sound volume. Set volume to None to use Node's properties.
        """
        if volume != None:
            self.channel.set_volume(volume)
            return
        self.channel.set_volume(self.get("volume", 0.5))
    
    @property
    def busy(self):
        """
        True if sound is playing. Read-only
        """
        return self.channel.get_busy()

    @property
    def volume(self):                             return self.channel.get_volume()
    @volume.setter
    def volume(self, value : int | float | None): self.set_volume(value)