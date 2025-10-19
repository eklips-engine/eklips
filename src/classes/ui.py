## Import all the libraries
import pyglet as pg
import classes.Singleton as engine
from classes.Constants import *

## UI Class.
class Interface:
    def add_screen(self, screen, batch):
        id                  = len(self.surfaces)+1
        self.making_surface = 1
        self.surfaces[id]   = {
            "screen": screen,
            "batch":  batch,
            "tbatch": pg.graphics.Batch()
        }
        self.making_surface = 0
        return id

    def __init__(self):
        self.mpos            = [0,0]
        self.mclk            = [0,0,0]
        self.cvars           = engine.cvars
        self.screen          = engine.display
        self.batch           = engine.batch
        self.delta           = 0
        self.surfaces        = {}
        self.making_surface  = False
        self.main_surf_id    = self.add_screen(self.screen, self.batch)
        self.is_doublebuffer = True
        self.area_cache      = {}
        self.boilerimg       = pg.image.ImageData(1,1,"RGB", bytes([0,0,0]))
        self.label_pool      = {i: pg.text.Label("", font_size=15, batch=self.batch) for i in range(self.cvars.get("ui_labelpoolamount"))}
        self.sprite_pool     = {i: pg.sprite.Sprite(self.boilerimg, batch=self.batch) for i in range(self.cvars.get("ui_labelpoolamount"))}
        self.label_used      = []
        self.sprite_used     = []
        self.draw_queue      = {}
        self.anchors         = {}
        self.label_queue     = {}
        self.layers          = {}
        self.layer_amount    = self.cvars.get("ui_layers") # -X ... X

        for i in range(-self.layer_amount,self.layer_amount):
            self.layers[i] = pg.graphics.Group(order=i)
    
    def get_anchor(self,pos,blit_in,anchor,surf_w,surf_h,can_cache,rot,no_y_flip=False):
        pos         = list(pos)
        if blit_in == MAIN_SCREEN:
            blit_in = self.main_surf_id
        screen = self.surfaces[blit_in]["screen"]
        win_w, win_h = screen.get_size()
        anchor_id   = f"{anchor},win{win_w}x{win_h},surf{surf_w}x{surf_h},pos{pos},rot{True if rot else False}{no_y_flip}"

        new_pos = pos.copy()
        if can_cache:
            if not anchor_id in self.anchors:
                if not "bottom" in anchor and not no_y_flip:
                    new_pos[1] = (win_h - surf_h) - pos[1] # Pyglet uses bottom-left for 0,0 while pygame uses top-left. I'm more familliar with pygame
                if "right" in anchor:
                    new_pos[0] = (win_w - surf_w) - pos[0]
                if "centerX" in anchor:
                    new_pos[0] = (win_w/2 - surf_w/2) + pos[0]
                if "centerY" in anchor:
                    new_pos[1] = (win_h/2 - surf_h/2) + pos[1]
                if "center" in anchor:
                    new_pos[0] = (win_w/2 - surf_w/2) + pos[0]
                    new_pos[1] = (win_h/2 - surf_h/2) + pos[1]
                if rot:
                    new_pos[0]+=surf_w/2
                    new_pos[1]+=surf_h/2
                new_pos=[round(new_pos[0]),round(new_pos[1])]
                self.anchors[anchor_id]=new_pos
            else:
                new_pos = self.anchors[anchor_id]
        return new_pos

    def blit(self, surface, pos, clip=0, anchor="", opacity = 1, layer = 0, scroll=[0,0], scale=[1,1], blit_in=MAIN_SCREEN, can_cache = 1, rot = 0, use_pyglet_resource_directly = False, custom_id = None, return_obj=False, batchxt=None, sprite=None):
        pos         = list(pos)
        new_pos     = list(pos)[:]
        if use_pyglet_resource_directly:
            path    = custom_id
            img     = surface
        else:
            path    = surface.get_path()
            img     = surface.get()
        img.subpixel = True
        new_opacity  = int(opacity * 255)
        new_clip     = clip

        if clip:
            ## Clipping
            cx, cy, cw, ch = clip
            cy = surface.height - cy - ch

            if can_cache:
                id = f"{path}{cx}{cy}{cw}{ch}"
                if not id in self.area_cache:
                    img = img.get_region(cx, cy, cw, ch)
                    self.area_cache[id] = img
                else:
                    img = self.area_cache[id]
        
        ## Anchoring
        if blit_in  == MAIN_SCREEN:
            blit_in =  self.main_surf_id
        
        batch        = self.surfaces[blit_in]["batch"]
        if batchxt:
            batch    = batchxt
        new_pos      = self.get_anchor(
            pos,
            blit_in,
            anchor,
            img.width*scale[0],
            img.height*scale[1],
            1,
            rot,
            False
        )
        
        ## Detect if i'm even visible and change position
        if not self.cull(img.width, img.height, new_pos, blit_in, scale=scale):
            if not layer in self.layers: layer = 0
            if scroll != [0, 0]:
                img = img.get_region(
                    int(scroll[0] % img.width), 
                    int(scroll[1] % img.height),
                    img.width,                  
                    img.height                  
                )

            spr_id       = -1
            hsize        = [img.width//2,img.height//2]
            sprite       = None
            if sprite:
                spr                      = sprite
                spr_id                   = len(self.sprite_pool)
                self.sprite_pool[spr_id] = spr
            else:
                for i in self.sprite_pool:
                    if not i in self.sprite_used:     
                        spr      = self.sprite_pool[i]
                        spr_id   = i                  
                        break                         
                if spr_id == -1:
                    spr = pg.sprite.Sprite(
                        self.boilerimg,
                        batch    = batch,
                        subpixel = True
                    )
                    spr_id                   = len(self.sprite_pool)
                    self.sprite_pool[spr_id] = spr
            if spr.x        != new_pos[0]:
                spr.x        = new_pos[0]
            if spr.y        != new_pos[1]:
                spr.y        = new_pos[1]
            if spr.image    != img:
                if img != None:
                    try:
                        if img.get_texture() == None:
                            print("Warning; Image texture is None")
                        else:
                            spr.image = img
                    except Exception as e:
                        print(f"Failed to assign sprite image: {e}")
            if spr.z        != layer:
                spr.z        = layer
                spr.group    = self.layers[layer]
            if spr.rotation != rot:
                spr.rotation = rot
            if spr.opacity  != new_opacity:
                spr.opacity  = new_opacity
            if spr.scale_x  != scale[0]:
                spr.scale_x  = scale[0]
            if spr.scale_y  != scale[1]:
                spr.scale_y  = scale[1]
            if rot:
                if spr.image.anchor_x != hsize[0]:
                    spr.image.anchor_x = hsize[0]
                if spr.image.anchor_y != hsize[1]:
                    spr.image.anchor_y = hsize[1]
            spr.visible = True
            self.draw_queue[spr_id] = spr
            self.sprite_used.append(spr_id)
            if return_obj:
                return img.width*scale[0], img.height*scale[1], spr
        if return_obj:
            return img.width*scale[0], img.height*scale[1], None
        return img.width*scale[0], img.height*scale[1]
    
    def cull(self, w, h, pos, blit_in, scale=[1,1]):
        if blit_in  == MAIN_SCREEN:
            blit_in  =  self.main_surf_id
        scr          = self.surfaces[blit_in]["screen"]
        win_w, win_h = scr.width, scr.height
        w           *= scale[0]
        h           *= scale[1]

        return (
            pos[0] > win_w or
            pos[1] > win_h or
            pos[0] < -w    or
            pos[1] < -h
        )

    def render(self, text, pos, blit_in=MAIN_SCREEN, layer=5, anchor="", size=15, rot=0, alpha=1, color=[255,255,255], return_obj=False, batchxt=None):
        id           = len(self.label_queue)
        if blit_in  == MAIN_SCREEN:
            blit_in  =  self.main_surf_id
        
        screen       = self.surfaces[blit_in]["screen"]
        batch        = self.surfaces[blit_in]["tbatch"]
        if batchxt:
            batch    = batchxt
        lbl_id       = -1
        for i in self.label_pool:
            if not i in self.label_used:
                lbl      = self.label_pool[i]
                lbl_id   = i                 
                id       = i                 
                break
        if lbl_id == -1:
            lbl = pg.text.Label(
                text,
                font_size=15,
                z=layer,
                batch=batch
            )
            self.label_pool[id] = lbl
            lbl_id              = id
        new_pos = self.get_anchor(
            list(pos),
            blit_in,
            anchor,
            lbl.content_width,
            lbl.content_height,
            True,
            rot
        )
        color_new = [color[0],color[1],color[2],255]

        if not lbl.text == text:
            lbl.text = text
        
        if self.cull(lbl.content_width, lbl.content_height, new_pos, blit_in):
            self.label_pool[id].visible = False
            return lbl.content_width, lbl.content_height

        if not lbl.z    == layer:
            if not layer in self.layers: layer = 0
            lbl.z       = layer
            lbl.group   = self.layers[layer]
        if not lbl.x == new_pos[0]:
            lbl.x = new_pos[0]
        if not lbl.y == new_pos[1]:
            lbl.y = new_pos[1]
        if not lbl.font_size == size:
            lbl.font_size = size
        if not lbl.rotation == rot:
            lbl.rotation = rot
            hsize        = [lbl.content_width//2, lbl.content_height//2]
            if lbl.anchor_x != hsize[0]:
                lbl.anchor_x = hsize[0]
            if lbl.anchor_y != hsize[1]:
                lbl.anchor_y = hsize[1]
        if not lbl.color == color_new:
            lbl.color = color_new
        if not lbl.opacity == alpha*255:
            lbl.opacity = alpha*255

        self.label_pool[id].visible = True
        self.label_used.append(id)
        self.label_queue[id] = lbl

        if return_obj:
            return round(lbl.content_width), round(lbl.content_height), lbl
        else:
            return round(lbl.content_width), round(lbl.content_height)
    
    def flip(self):
        ## === 1. Draw batches ===
        if not self.making_surface:
            for surf in self.surfaces.values():
                surf["batch"].draw() 
                surf["tbatch"].draw()
        self.making_surface = False

        ## === 2. Flip/update window ===
        for i in self.surfaces:
            screen = self.surfaces[i]["screen"]
            if self.is_doublebuffer:
                self.screen.flip()
            else:
                self.screen.update()
    
    def fill(self, delta, color="black"):
        self.delta = delta      
        for i in self.surfaces: 
            screen = self.surfaces[i]["screen"]
            screen.clear()      
        for lbl in self.label_used:
            self.label_pool[lbl].visible  = False
        for spr in self.sprite_used:
            self.sprite_pool[spr].visible = False
        self.label_used.clear() 
        self.draw_queue.clear() 
        self.label_queue.clear()
        self.sprite_used.clear()
    
    def close(self):
        for i in self.surfaces:
            screen = self.surfaces[i]["screen"]
            screen.close()
        self.surfaces = {}