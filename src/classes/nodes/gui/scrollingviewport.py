## Import inherited
from classes.nodes.gui.extraviewport import *
from classes.ui                      import *

## Classes
class ScrollingViewport(ExtraViewport):
    """
    A Viewport Node.
    
    This Node will create a new Viewport. You can get this Viewport
    by using `engine.display.get_viewport(node.viewport_id, wid)`
    or by using `node` itself.

    You can use the scroll wheel on the mouse to move the Viewport's
    contents (or rather Camera, but that doesn't sound so magical
    now, does it?), or use the (non-existent?) scrollbar instead.
    """
    _isdisplayobject = True

    @export(700.0,"float","slider")
    def speed(self):
        """How fast the scrolling should be.

        The reason why the default value is so high
        because on 1x speed, it takes 1 second to
        move 1 pixel and scrolling isn't exactly
        smooth as of right now.

        You can make this value negative to go backwards.
        """
        return self._speed
    @speed.setter
    def speed(self, value):
        self._speed = value

    @export(False, "bool", "bool")
    def left_to_right(self):
        return self._left_to_right
    @left_to_right.setter
    def left_to_right(self, value):
        self._left_to_right = value
        if value:
            self.scrollbar_bg.image = engine.theme.get_static_widget("scrollbg_hor")
        else:
            self.scrollbar_bg.image = engine.theme.get_static_widget("scrollbg")
        self._set_scrollbar_size()
    
    @export(False, "int", "slider")
    def content_width(self):
        return self._content_width
    @content_width.setter
    def content_width(self, value):
        if value < ZDE_FIX: value = ZDE_FIX
        self._content_width = value
    
    @export(False, "int", "slider")
    def content_height(self):
        return self._content_height
    @content_height.setter
    def content_height(self, value):
        if value < ZDE_FIX: value = ZDE_FIX
        self._content_height = value
    
    def _set_scrollbar_size(self):
        if self.left_to_right:
            self.scrollbar_bg.scale_x = self._w               / self.scrollbar_bg.image.width
            self.scrollbar_bg.scale_y = self.scrollbar.height / self.scrollbar_bg.image.height
        else:
            self.scrollbar_bg.scale_x = self.scrollbar.width / self.scrollbar_bg.image.width
            self.scrollbar_bg.scale_y = self._h              / self.scrollbar_bg.image.height
    
    def _set_size(self, w, h):
        self._set_scrollbar_size()
        super()._set_size(w, h)
    
    def __init__(self, properties={}, parent=None):
        # Setup vp
        super().__init__(properties, parent)
        
        # Alias
        self.widgetman = engine.scene._widgetman
        
        # Set properties
        self._content_height   = 720
        self._content_width    = 1280
        self._speed            = 700.0
        self._left_to_right    = False
        self._vel              = 0
        self.gid               = self.widgetman.add_widget(self)
        
        # Add batch for scrollbar
        self._scrollbarbatch = self.add_batch()
        
        # Make scrollbar
        self.scrollbar_bg = pg.sprite.Sprite(
            img   = engine.theme.get_static_widget("scrollbg"),
            batch = self.batches[self._scrollbarbatch])
        self.scrollbar    = pg.sprite.Sprite(
            img   = engine.theme.get_static_widget("scrollbtn"),
            batch = self.batches[self._scrollbarbatch])
    
    def _remove_item(self):
        super()._remove_item()
        self.scrollbar.delete()
        self.scrollbar_bg.delete()
        
    def _free(self):
        self.widgetman.widgets.pop(self.gid)
        super()._free()
    
    def get_if_mouse_hovering_knob(self) -> bool:
        """Returns true if the mouse is hovering over the knob."""
        if not self.viewport:
            return
        ## Get things
        mpos   = engine.mouse.pos
        x,y,z  = self.scrollbar.position
        vx, vy = self.into_screen_coords()

        ## Apply viewport position into x and y
        x += vx - self.viewport.cam.x
        y += vy - self.viewport.cam.y

        ## Apply viewport zooming
        x *= self.viewport.cam.zoom
        y *= self.viewport.cam.zoom
        w  = self.scrollbar.width  * self.viewport.cam.zoom
        h  = self.scrollbar.height * self.viewport.cam.zoom

        ## Result
        return (
            mpos[0] >= x     and
            mpos[0] <= x + w and
            mpos[1] >= y     and
            mpos[1] <= y + h
        )
    
    def update(self):
        super().update()

        # Check if not wasting time
        if not self.visible:
            self.scrollbar.visible    = False
            self.scrollbar_bg.visible = False
            return
        elif self.content_height     == ZDE_FIX or self.content_width == ZDE_FIX:
            self.scrollbar.visible    = False
            self.scrollbar_bg.visible = False
            return
        else:
            self.scrollbar.visible    = True
            self.scrollbar_bg.visible = True
        
        # Handle the knob
        if self.get_if_mouse_hovering_knob():
            self.widgetman.hovering_widget = self.gid
        else:
            if self.widgetman.hovering_widget == self.gid:
                self.widgetman.hovering_widget = -1
        
        if engine.mouse.buttons[MOUSE_LEFT]:
            if self.get_if_mouse_hovering_knob():
                if self.widgetman.moving_widget  == -1:
                    self.widgetman.focused_widget = self.gid
                if engine.mouse.dragging and self.widgetman.focused_widget == self.gid:
                    self.widgetman.moving_widget  = self.gid
            if self.widgetman.moving_widget      == self.gid:
                self._vel = 0
                engine.set_mouse(MOUSE_DRAG, self.window_id)
                if self._left_to_right:
                    self.cam.x    += engine.mouse.dpos[0] / (self._w-self.scrollbar.width) * self.content_width
                    if self.cam.x  < 0:
                        self.cam.x = 0
                else:
                    self.cam.y    += engine.mouse.dpos[1] / (self._h-self.scrollbar.height) * self.content_height
                    if self.cam.y  > 0:
                        self.cam.y = 0
        else:
            if self.widgetman.hovering_widget == -1:
                engine.set_mouse(MOUSE_NORMAL, self.window_id)
            if self.get_if_mouse_hovering_knob() or self.widgetman.moving_widget == self.gid:
                engine.set_mouse(MOUSE_DRAGGABLE, self.window_id)
                self.widgetman.moving_widget = -1
        
        # Handle spinning the mouse wheel
        if engine.mouse.scroll != 0 and self.get_if_mouse_hovering():
            self._vel = engine.mouse.scroll * (self.speed * engine.delta)
        
        # Camera and scrollbar sprite handling
        if self._left_to_right:
            self.cam.x   -= self._vel
            if self.cam.x < 0:
                self._vel = -((-self.cam.x) / ((engine.fps+ZDE_FIX) * 0.25))
            if self.cam.x > self.content_width:
                self.cam.x = self.content_width
            
            self.scrollbar_bg.x = self.cam.x
            self.scrollbar_bg.y = self.scrollbar.y = 0
            self.scrollbar.x    = self.cam.x+((self.cam.x/self.content_width) * (self._w-self.scrollbar.width))
        else:
            self.cam.y   += self._vel
            if self.cam.y > 0:
                self._vel = (-self.cam.y) / ((engine.fps+ZDE_FIX) * 0.25)
            if self.cam.y < -self.content_height:
                self.cam.y = -self.content_height
            
            self.scrollbar_bg.y = self.cam.y
            self.scrollbar_bg.x = self._w-self.scrollbar_bg.width
            self.scrollbar.x    = self._w-self.scrollbar.width
            y                   = (self.cam.y/self.content_height) * (self._h-self.scrollbar.height)
            self.scrollbar.y    = self._h-self.scrollbar.height+self.cam.y+y
        
        # Weeeeeee
        self._vel += (-self._vel) / ((engine.fps+ZDE_FIX) * 0.25)