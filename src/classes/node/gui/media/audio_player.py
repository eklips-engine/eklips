## Import inherited
from classes.node.node import Node

## Import engine singleton and others
import pyglet as pg
import pygame as pyg
import classes.Singleton as engine

## Node
class AudioPlayer(Node):
    """
    ## A Media Node to play audio.
     
    Self-explanatory.
    """
    
    node_base_data = {
        "prop":   {
            "media":       "res://media/load.mp3",
            "loop":        False,
            "autostart":   False
        },
        "data":   {},
        "meta":   {
            "kind": "Node",
            "name": "Node"
        },
        "script": None
    }

    node_signals = [
        "_player_started",
        "_player_paused",
        "_player_resumed",
        "_player_stopped"
    ]

    def __init__(self, data=node_base_data, parent=None):
        global player_global
        super().__init__(data,parent)

        self.audio_data               = None
        self._autoplay_has_played_yet = False
        self.channel                  = None
    
    def get_master_volume(self):
        return engine.savefile.get("sound/master", 0.75)
    
    def play(self, volume=1):
        self.call_signal("_player_started")
        if not self.audio_data:
            self.audio_data : pyg.Sound = self.resourceman.load(self.properties["media"]).get()
        self.audio_data.set_volume(volume * self.get_master_volume())
        self.channel = self.audio_data.play()

    def pause(self):
        if not self.channel:
            return
        self.call_signal("_player_paused")
        self.channel.pause()
    
    def resume(self):
        if not self.channel:
            return
        self.call_signal("_player_resumed")
        self.channel.unpause()
    
    def stop(self):
        if not self.channel:
            return
        self.call_signal("_player_stopped")
        self.channel.stop()
        self.audio_data.stop()
    
    def update(self, delta):
        if not self._autoplay_has_played_yet and self.properties["autostart"]:
            self.play()
            self._autoplay_has_played_yet = True
        
        super().update(delta)