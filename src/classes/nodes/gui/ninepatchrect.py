# Import libraries
from classes.nodes.gui.canvasitem import *

# Classes
class BaseNinePatchRect(CanvasItem):
    """
    A CanvasItem with an spliced image.
    """
    _isblittable = True

    ## Exports
    @export([0,0], "list", "9patch")
    def corner_size(self):
        return self._corner_size
    @corner_size.setter
    def corner_size(self, value):
        self._corner_size = value
        self._remake_corners()
        self._remake_center()
    @export([0,0], "list", "9patch")
    def edge_size(self):
        return self._edge_size
    @edge_size.setter
    def edge_size(self, value):
        self._edge_size = value
        self._remake_edges()
        self._remake_center()

    ## CItem & Transform related
    def _make_new_item(self):
        if self.citem:
            self._remove_item()
        if not self.image:
            self._image    = engine.loader.load("root://_assets/error.png")
        
        ## Make CItems
        for s in [
            "citem", "_citemtr", "_citembl", "_citembr",
            "_citemt", "_citeml", "_citemr", "_citemb", "_citemc"
        ]:
            self.set(s, pg.sprite.Sprite(self.image, batch=self.batch))
            self.get(s).visible = False
        
        ## Splicing things
        self._remake_images()
        self._resize_images()
        self._set_anchors()
    def _remove_item(self):
        for s in [
            self.citem, self._citemtr, self._citembl, self._citembr,
            self._citemt, self._citeml, self._citemr, self._citemb, self._citemc
        ]:
            if s:
                s.delete()
                s = None
    
    def _remake_center(self):
        x = self.corner_size[0]
        y = self.corner_size[1]
        w = self.image.width  - self.corner_size[0]*2
        h = self.image.height - self.corner_size[1]*2
        self._citemc.image = self.image.get_region(x,y, w,h)
    def _remake_corners(self):
        ## Dimensions
        ty = self.image.height - self.corner_size[1]
        rx = self.image.width  - self.corner_size[0]
        cw = self.corner_size[0]
        ch = self.corner_size[1]
        lx = 0
        by = 0

        ## Make images
        self.citem.image    = self.image.get_region(lx,ty, cw,ch)
        self._citemtr.image = self.image.get_region(rx,ty, cw,ch)
        self._citembl.image = self.image.get_region(lx,by, cw,ch)
        self._citembr.image = self.image.get_region(rx,by, cw,ch)
        self._set_anchors()
    def _remake_edges(self):
        ## Top and bottom dimensions
        tw = self.image.width - self.edge_size[0]*2
        th = self.edge_size[1]
        tx = self.corner_size[0]
        ty = self.image.height - self.edge_size[1]
        by = 0

        ## Left and right dimensions
        lw = self.edge_size[0]
        lh = self.image.height - self.edge_size[1]*2
        lx = 0
        rx = self.image.width  - self.edge_size[0]
        ly = self.corner_size[1]

        ## Make images
        self._citemt.image = self.image.get_region(tx,ty, tw, th)
        self._citemb.image = self.image.get_region(tx,by, tw, th)
        self._citeml.image = self.image.get_region(lx,ly, lw, lh)
        self._citemr.image = self.image.get_region(rx,ly, lw, lh)
        self._set_anchors()
    def _remake_images(self):
        self._remake_corners()
        self._remake_edges()
        self._remake_center()
    
    def _resize_images(self):
        self._resize_edges()
        self._resize_center()
    def _resize_center(self):
        w = self.w-self.corner_size[0]*2
        h = self.h-self.corner_size[1]*2
        self._citemc.scale_x = w / self._citemc.image.width
        self._citemc.scale_y = h / self._citemc.image.height
    def _resize_edges(self):
        w = self.w-self.corner_size[0]*2
        h = self.h-self.corner_size[1]*2
        self._citemt.scale_x = self._citemb.scale_x = w / self._citemb.image.width
        self._citeml.scale_y = self._citemr.scale_y = h / self._citeml.image.height
    
    def _set_anchors(self):
        for s in [
            self.citem, self._citemtr, self._citembl, self._citembr,
            self._citemt, self._citeml, self._citemr, self._citemb, self._citemc
        ]:
            s.image.anchor_x = s.image.width  // 2
            s.image.anchor_y = s.image.height // 2
    def _set_size(self, w, h):
        self._resize_images()
    def _set_rot(self, deg):
        return
    def _set_visible(self, val):
        for s in [
            self.citem, self._citemtr, self._citembl, self._citembr,
            self._citemt, self._citeml, self._citemr, self._citemb, self._citemc
        ]:
            if s:
                s.visible = val
    def _set_alpha(self, deg):
        for s in [
            self.citem, self._citemtr, self._citembl, self._citembr,
            self._citemt, self._citeml, self._citemr, self._citemb, self._citemc
        ]:
            if s:
                s.opacity = deg
    def _set_layer(self, val):
        for s in [
            self.citem, self._citemtr, self._citembl, self._citembr,
            self._citemt, self._citeml, self._citemr, self._citemb, self._citemc
        ]:
            if s:
                s.group = engine.ui.request_group(val)
    def _set_flip(self, w, h):
        return
    
    ## Modify image property
    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        if self._image is value:
            return
        
        self._image = value
        self._remake_images()
        self._resize_images()
        self._set_anchors()

    ## Init
    def __init__(self, properties={}, parent=None):
        self._edge_size = self._corner_size = [12,12]
        
        self._imagepath = "root://_assets/error.png"
        super().__init__(properties, parent)
        self._make_new_item()
    def draw(self):
        """Draw the NinePatchRect. This is usually called automatically."""
        if self.visible and self.viewport.is_onscreen(self) and self.citem:
            x, y   = self.into_screen_coords()
            cw, ch = self.corner_size
            w, h   = self.w, self.h

            ## Helpers
            def hw(s): return (s.image.width  * s.scale_x) / 2
            def hh(s): return (s.image.height * s.scale_y) / 2

            ## Corners
            self.citem.x    = self._citembl.x = x + cw / 2
            self.citem.y    = self._citemtr.y = y + h - ch / 2
            self._citembl.y = self._citembr.y = y + ch / 2

            self._citemtr.x = self._citembr.x = x + w - cw / 2

            ## Edges
            self._citemt.x = self._citemb.x = x + cw + (w - 2 * cw) / 2
            self._citemt.y = y + h - hh(self._citemt)
            self._citemb.y = y + hh(self._citemb)

            self._citeml.x = x + hw(self._citeml)
            self._citeml.y = self._citemr.y = y + ch + (h - 2 * ch) / 2

            self._citemr.x = x + w - hw(self._citemr)

            ## Center
            self._citemc.x = x + cw + (w - 2 * cw) / 2
            self._citemc.y = y + ch + (h - 2 * ch) / 2
            
            self._set_visible(True)
        else:
            self._set_visible(False)
    def update(self):
        super().update()
        self.draw()

class NinePatchRect(BaseNinePatchRect):
    @export("root://_assets/error.png","str","file_path/img")
    def image_path(self):
        """Filepath of the attached Image. Setting this value loads and sets the imagepath as the Sprite's image."""
        return self._imagepath
    @image_path.setter
    def image_path(self, value):
        if not value: return
        self._imagepath = value
        self.image      = engine.loader.load(value)