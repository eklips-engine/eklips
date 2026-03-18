# Import libraries
from classes.nodes.gui.ninepatchrect import *

# Classes
class Button(BaseNinePatchRect, Color):
    """
    A themed Button.
    """
    _isblittable = True

    ## Exported properties
    @export("dolorem ipsum","str","str")
    def text(self) -> str: return self._text
    @text.setter
    def text(self, value):
        self._text = value
        if self.label:
            self.label.text = value
    @export(None,"str","file_path/img")
    def icon_path(self):
        """Filepath of the attached Icon. Setting this value loads and sets the iconpath as the Button's icon."""
        return self._iconpath
    @icon_path.setter
    def icon_path(self, value):
        if not value: return
        self._iconpath = value
        self.icon      = engine.loader.load(value)
        if self._iconspr:
            self._iconspr.image = self.icon
            self._iconspr.scale = (self.h-self.corner_size[0]*2) / self.icon.height

    @export(DEFAULT_FONT_NAME,"str","font")
    def font(self) -> str: return self._fname
    @font.setter
    def font(self, value):
        self._fname = value
        if self.label:
            self.label.font_name = value

    @export(DEFAULT_FONT_SIZE,"float/int","float/int")
    def font_size(self) -> float | int: return self._fsize
    @font_size.setter
    def font_size(self, value):
        self._fsize = value
        if self.label:
            self.label.font_size = value

    @export(WHITE,"list","color")
    def color(self) -> tuple[int, int, int]:
        """RGBA Color value of the text. Modifying a single item will do nothing."""
        return self.color_as_tuple()
    @color.setter
    def color(self, rgb : tuple[int, int, int] | list[int]):
        self.rgb = rgb
    def _update_color(self, r, g, b, a):
        if self.label:
            self.label.color = (r,g,b,a)
    
    ## CItem Management
    def _remove_item(self):
        for s in [
            self.citem,   self._citemtr, self._citembl, self._citembr,
            self._citemt, self._citeml,  self._citemr,  self._citemb,  self._citemc,
            self.label,   self._iconspr
        ]:
            if s:
                s.delete()
                s = None
    def _make_new_item(self):
        super()._make_new_item()
        self.label    = pg.text.Label(batch=self.batch)
        self._iconspr = pg.sprite.Sprite(self.icon, batch=self.batch)
        
        self.label.color     = self.color
        self.label.text      = self.text
        self.label.font_name = self.font
        self.label.font_size = self.font_size

        self.label.visible    = False
        self._iconspr.visible = False
    
    ## Transform related
    def _set_anchors(self):
        super()._set_anchors()
        self.icon.anchor_x = self.icon.width  // 2
        self.icon.anchor_y = self.icon.height // 2
    def _set_size(self, w, h):
        super()._set_size(w, h)
        self._iconspr.scale = (self.h-self.corner_size[0]*2) / self.icon.height
    def _set_alpha(self, deg):
        super()._set_alpha(deg)
        self.label.opacity = self.icon.opacity = deg
    def _set_visible(self, val):
        super()._set_visible(val)
        if self.label:
            self.label.visible = val
        
        if self._iconspr:
            if self._iconpath:
                self._iconspr.visible = val
            else:
                self._iconspr.visible = False
    
    ## Updating
    def draw(self):
        super().draw()
        if self.visible and self.viewport.is_onscreen(self) and self.citem:
            x,   y        = self.into_screen_coords()
            tx,  ty       = self.into_screen_coords(drawing=True)
            self.label.x = x + (self.w//2-self.label.content_width //2)
            self.label.y = y + (self.h//2-self.label.content_height//2)

            if self._iconpath:
                self._iconspr.x = tx-self.label.content_width
                self._iconspr.y = ty
    def update(self):
        super().update()
        
        ## Handle cursor
        if self.get_if_mouse_hovering():
            self.widgetman.hovering_widget = self.gid
        else:
            if self.widgetman.hovering_widget == self.gid:
                self.widgetman.hovering_widget = -1
        
        if engine.mouse.buttons[MOUSE_LEFT]:
            if self.get_if_mouse_hovering():
                if self.widgetman.moving_widget == -1:
                    self.widgetman.focused_widget = self.gid
                if engine.mouse.dragging and self.widgetman.focused_widget == self.gid:
                    self.widgetman.moving_widget  = self.gid
                self.image = engine.theme.get_static_widget("pressed_btn")
        else:
            self.image = engine.theme.get_static_widget("button")
            if self.widgetman.hovering_widget == -1:
                engine.set_mouse(MOUSE_NORMAL, self.window_id)
            if self.get_if_mouse_hovering() or self.widgetman.moving_widget == self.gid:
                engine.set_mouse(MOUSE_POINT, self.window_id)
                self.widgetman.moving_widget = -1
        
        ## Draw it
        self.draw()
    
    ## Init
    def _free(self):
        self.widgetman.widgets.pop(self.gid)
        super()._free()
    def __init__(self, properties={}, parent=None):
        # Init color
        Color.__init__(self, *WHITE)
        
        # Make widget
        self.widgetman = engine.scene._widgetman
        self.gid       = self.widgetman.add_widget(self)

        # Set properties
        self._text     : str                    = "dolorem ipsum"
        self._fsize    : int | float            = DEFAULT_FONT_SIZE
        self._fname    : str                    = DEFAULT_FONT_NAME
        self.label     : pg.text.Label          = None                                           # The label object
        self._iconpath : str | None             = None                                           # The icon path
        self.icon      : pg.image.AbstractImage = engine.loader.load("root://_assets/error.png") # The icon image
        self._iconspr  : pg.sprite.Sprite       = None                                           # The icon sprite

        # Init CItem
        super().__init__(properties, parent)

        # Make image theme
        self._corner_size = engine.theme.get_widget_data("button")["corner_size"]
        self._edge_size   = engine.theme.get_widget_data("button")["side_size"]
        self.image        = engine.theme.get_static_widget("button")