## Import inherited
from classes.node.gui.canvasitem         import CanvasItem
from classes.node.gui.media.audio_player import AudioPlayer

## Import engine singleton and others
import pyglet as pg, pyvidplayer2 as vid
import classes.Singleton as engine, io, os
from classes import Resources

## Node
class VideoPlayer(CanvasItem):
    """
    ## A Media Node to render video and play it's audio.
     
    Self-explanatory.
    """

    node_base_data = {
        "prop":   {
            "media":       "res://media/load.mp4",
            "loop":        False,
            "where":       0,
            "rot":         0,
            "autostart":   False,

            "transform":  {
                "scale":  [1,1],
                "pos":    [0,0],
                "anchor": "top left",
                "layer":  0,
                "alpha":  1,
                "scroll": [0,0]
            }
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

        self.old_size     = [0,0]
        self.og_px_size   = [0,0]
        self.vid          = None
        self.is_playedyet = 0
        self.media_id     = None
        self.playing      = False
    
    def play(self, volume=1):
        self.call("_player_started")
        if not self.vid:
            # XXX this sucks. Find way to not use temporary file

            tmp_bytes, id = self.resourceman.load(self.properties["media"], force_type="bin", return_identifier = 1)
            tmp_file_path = f"tmp/{id}"
            self.media_id = id

            with open(tmp_file_path, "wb") as f:
                f.write(tmp_bytes)
            
            self.vid        = vid.VideoPyglet(tmp_file_path)
            self.og_px_size = self.vid.current_size

        self.vid.set_volume(volume)
        self.vid.seek(0)
        self.vid.play()
        self.playing = True

    def pause(self):
        self.call("_player_paused")
        self.vid.pause()
    
    def seek(self, index):
        self.vid.seek(index)
    
    def seek_frame(self, index):
        self.vid.seek_frame(index)
    
    def resume(self):
        self.call("_player_resumed")
        self.vid.resume()
    
    def stop(self):
        self.call("_player_stopped")
        self.vid.stop()
        self.playing = False
    
    def _free(self):
        if self.vid:
            self.vid.close()
        super()._free(self)
    
    def update(self, delta):
        global camera_pos
        if not self.is_playedyet and self.properties["autostart"]:
            self.play()
            self.is_playedyet = 1
        
        if self.vid:
            if self.vid.active:
                self.vid._update()
                if self.vid.frame_surf:
                    self.draw()
            else:
                if self.playing:
                    self.playing = False
                    if self.properties["loop"]:
                        self.play()
                    
        super().update(delta)
    
    def draw(self):
        c_size = [
            round(self.og_px_size[0] * self.scale_x),
            round(self.og_px_size[1] * self.scale_y)
        ]
        if self.old_size != c_size:
            self.vid.resize(c_size)
            self.old_size = c_size
        
        use_img = self.vid.frame_surf
        if self.visible:
            self.w,self.h=use_img.width,use_img.height
            self._draw_onto_screen(use_img)
    
    def _draw_onto_screen(self, img):
        return self.screen.blit(
            img,                                   
            self.runtime_data["rendererpos"],             
            anchor                       = self.anchor,
            scale                        = [1, 1],
            layer                        = self.layer,
            rot                          = self.rot,
            opacity                      = self.alpha,
            scroll                       = self.scroll,
            use_pyglet_resource_directly = True,
            custom_id                    = self.media_id,
            sprite                       = self.sprite
        )