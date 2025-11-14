# Import libraries
import pyglet as pg, gc

# Import components
import classes.singleton as engine
from classes.locals      import *
from classes.customprops import *
from pyglet.gl           import *

# Colors
_r    = [0,0,0]
_rs   = [1,1,1]
red   = [255,0,0]
green = [255,0,0]
blue  = [0,0,255]
black = [0,0,0]
white = [255,255,255]
def rainbow():
    global _rs
    _r[0] += 15.5  * _rs[0]
    _r[1] += 7.75  * _rs[1]
    _r[2] += 3.875 * _rs[2]
    if _r[0] > 255 or _r[0] < 0:
        _rs[0] = -_rs[0]
    if _r[1] > 255 or _r[2] < 0:
        _rs[1] = -_rs[2]
    if _r[2] > 255 or _r[2] < 0:
        _rs[2] = -_rs[2]
    return _r

# Classes
class EklipsWindow(pg.window.Window):
    def on_close(self):
        engine.display.close_window(self.wid)
        self.eklips_viewport.close()
    
    def on_mouse_motion(self, x, y, dx, dy):
        engine.mouse.pos  = [x, y]
        engine.mouse.dpos = [dx,dy]
    
    def on_mouse_press(self, x, y, button, modifiers):
        engine.mouse.pos           = [x, y]
        engine.mouse.clk[button-1] = True

    def on_mouse_release(self, x, y, button, modifiers):
        engine.mouse.pos           = [x, y]
        engine.mouse.clk[button-1] = False
    
    def on_key_press(self, symbol, modifiers):
        engine.keyboard.modifiers       = modifiers
        engine.keyboard.held[symbol]    = True
        engine.keyboard.pressed[symbol] = True
        
    def on_key_release(self, symbol, modifiers):
        engine.keyboard.modifiers    = modifiers
        engine.keyboard.held[symbol] = False

class Viewport:
    _window_is_slave = False
    _width           = 0
    _height          = 0
    _background      = [0,0,0,1]

    def __init__(self, batches : dict = {}, size : list[int,int] = [640,480], position : list[int,int] = [0,0]):
        self.window : EklipsWindow = None
        self.batches               = {}
        self.width                 = size[0]
        self.height                = size[1]

        self._sprite   = pg.sprite.Sprite(self.color_buffer, x=0, y=0)

        self.sprites : list[pg.sprite.Sprite] = []
        self.used_sprites                     = []
        self._base_img                        = engine.loader.load("root://_assets/error.png")
    
    def _make_framebuffer(self):
        self.color_buffer = pg.image.Texture.create(self.width,      self.height, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
        self.depth_buffer = pg.image.buffer.Renderbuffer(self.width, self.height, GL_DEPTH_COMPONENT)

        self.framebuffer = pg.image.Framebuffer()
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
        self.framebuffer.attach_renderbuffer(self.depth_buffer, attachment=GL_DEPTH_ATTACHMENT)
    
    @property
    def width(self): return self._width
    @property
    def height(self): return self._height
    
    @property
    def x(self): return self._sprite.x
    @property
    def y(self): return self._sprite.y

    @property
    def size(self): return [self.width,self.height]

    @size.setter
    def size(self, value):
        self._width = value[0]
        self._height = value[1]
        self._make_framebuffer()

    @x.setter
    def x(self, value): self._sprite.x = value
    @y.setter
    def y(self, value): self._sprite.y = value
    
    @width.setter
    def width(self, value):
        self._width = value
        self._make_framebuffer()
    @height.setter
    def height(self, value):
        self._height = value
        self._make_framebuffer()

    def _make_new_sprite(self, batch_id=MAIN_BATCH):
        sprite = pg.sprite.Sprite(self._base_img, batch = self.batches[batch_id])
        i      = len(self.sprites)
        self.sprites.append(sprite)
        return sprite, i
    def delete_sprite(self, sprite_id : int):
        if not sprite_id in self.sprites:
            return
        self.sprites[sprite_id].delete()
        self.sprites.pop(sprite_id)
        gc.collect()
    def _allocate_sprite(self, batch_id=MAIN_BATCH):
        i = 0
        for sprite in self.sprites:
            if not i in self.used_sprites:
                self.used_sprites.append(i)
                return sprite, i
            i += 1
        
        sprite, i = self._make_new_sprite(batch_id)
        self.used_sprites.append(i)
        return sprite, i
    
    def set_background(self, r=0,g=0,b=0, a=1):
        """
        Set the background color of the Viewport.

        .. r:: Red value of the background color (0-255).
        .. g:: Green value of the background color (0-255).
        .. b:: Blue value of the background color (0-255).
        .. a:: Alpha of the background color (0-255).
        """
        self._background = [
            (r+ZDE_FIX) / 255,
            (g+ZDE_FIX) / 255,
            (b+ZDE_FIX) / 255,
            (a+ZDE_FIX) / 255
        ]
    
    def clear(self):
        for sprite in self.sprites:
            sprite.visible = False
        self.used_sprites.clear()
    
    @property
    def x(self):        return self._sprite.x
    @property
    def y(self):        return self._sprite.y
    @x.setter
    def x(self, value): self._sprite.x = value
    @y.setter
    def y(self, value): self._sprite.y = value
    
    def flip(self):
        """
        Draw viewport contents to the window and flip it if the viewport is its master.
        """
        # Window-only 1
        if self.window and self._window_is_slave:
            self.window.switch_to()
            self.window.clear()
            if self.color_buffer.width != self.window.width:
                self.width = self.window.width
            if self.color_buffer.height != self.window.height:
                self.height = self.window.height
        
        # Bind buffer
        self.framebuffer.bind()
        glViewport(self.x, self.y, self.width, self.height)
        glEnable(GL_CULL_FACE)
        glClearColor(*self._background)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw batches for this Window and unbind buffer
        for batch in self.batches:
            batch.draw()
        self.used_sprites.clear()
        self.framebuffer.unbind()

        # Window-only 2
        if self.window:
            self.window.switch_to()
            self._sprite.image = self.color_buffer
            self._sprite.draw()
            if self._window_is_slave:
                self.window.flip()
    
    def provide_window(self, window, master=False):
        """
        Provide the window `window` to the Viewport to draw to.

        .. window:: Window object (engine.ui.EklipsWindow).
        .. master:: If the viewport is the master.
        """
        self.window           = window
        self._window_is_slave = master
    
    def close(self):
        """
        Free the viewport (and window if the viewport is the master.)
        """
        if self.window and self._window_is_slave:
            self.window.close()
        self.framebuffer.delete()
        self.color_buffer.delete()
        self.depth_buffer.delete()
    
class Display:
    print(" ~ Initialize Display")
    windows            = {}
    main_window_id     = None

    def add_window(self,
        name           = DEFAULT_NAME,
        size           = [640,480],
        viewport_size  = VIEWPORT_EQUAL_WINDOW,
        viewport_color = black,
        icon           = None,
        resizable      = True,
        minimum_size   = [648,648],
        maximum_size   = None,
    ) -> int:
        """
        Add a new Window, returns its Window ID.

        .. name:: Title of the window.
        .. size:: Size of the window.
        .. viewport_size:: Size of the window's viewport. Use constant `VIEWPORT_EQUAL_WINDOW` to make the Viewport size equal the Window size.
        .. viewport_color:: Background color of the viewport.
        .. icon:: Image resource of the Window Icon, or None.
        .. resizable:: Allow the window to be resizable if True.
        .. minimum_size:: List of the minimum size the window can be, or None if you dont want a limit.
        .. maximum_size:: List of the maximum size the window can be, or None if you dont want a limit.
        """
        wid = len(self.windows)
        print(f" ~ Initialize Window '{name}'")

        if viewport_size == VIEWPORT_EQUAL_WINDOW:
            viewport_size = size
        if self.main_window_id == None:
            self.main_window_id = wid
        
        window   = EklipsWindow(
            width     = size[0],
            height    = size[1],
            caption   = name,
            resizable = resizable
        )
        if minimum_size:
            window.set_minimum_size(*minimum_size)
        if maximum_size:
            window.set_maximum_size(*maximum_size)
        if icon:
            window.set_icon(icon)
        viewport = Viewport({}, viewport_size, [0,0])
        viewport.set_background(*viewport_color)
        viewport.provide_window(window, master=True)

        self.windows[wid] = {
            "name": name,

            "window":     window,
            "viewport":   viewport,

            "batches":    [],
            "main_batch": None
        }
        self.add_batch(wid)
        viewport.batches = self.windows[wid]["batches"]

        window.eklips_viewport = viewport
        window.wid             = wid

        return wid
    
    def clear_window(self, wid):
        window_data           = self.windows[wid]
        if window_data.get("viewport",None):
            window_data["viewport"].clear()
    
    def clear_windows(self):
        """
        Clear all windows and their viewports.
        """
        for wid in self.windows:
            self.clear_window(wid)
        
    def flip_window(self, wid):
        window_data           = self.windows[wid]
        if window_data.get("viewport",None):
            window_data["viewport"].flip()
    
    def flip_windows(self):
        """
        Flip all windows and their viewports.
        """
        for wid in self.windows:
            self.flip_window(wid)
    
    def close_window(self, wid):
        """
        Close the window `wid`.

        .. wid:: ID of Window.
        """
        window_data = self.windows[wid]
        window_data["window"].close()

        window_data["window"]     = None
        window_data["viewport"]   = None
        window_data["batches"]    = None
        window_data["main_batch"] = None
        
        window_data = None
        del window_data

        if wid == self.main_window_id:
            self.main_window_id = None
        
        gc.collect()
    
    def close_windows(self):
        """
        Close all windows and their viewports.
        """
        for wid in self.windows:
            self.close_window(wid)
    
    def dispatch_events(self):
        """
        Dispatch the events of all windows.
        """
        for wid in self.windows:
            window_data                   = self.windows[wid]
            window : pg.window.BaseWindow = window_data["window"]
            if window:
                window.switch_to()
                window.dispatch_events()
    
    def add_batch(self, wid):
        """
        Add a batch to Window `wid`.

        .. wid:: ID of Window.
        """
        window_data = self.windows[wid]

        bid = len(window_data["batches"])
        if window_data["main_batch"] == None:
            window_data["main_batch"] = bid
        
        window_data["batches"].append(pg.graphics.Batch())

        self.windows[wid] = window_data
        return bid

    def get_window(self, wid : int = MAIN_WINDOW) -> EklipsWindow:
        """
        Get the window `wid`.

        .. wid:: ID of Window. Defaults to MAIN_WINDOW.
        """
        return self.windows[wid]["window"]

    def get_viewport_from_window(self, wid : int = MAIN_WINDOW, vid : int = MAIN_VIEWPORT) -> Viewport:
        """
        Get the viewport `vid` from the window `wid`.

        .. wid:: ID of Window. Defaults to MAIN_WINDOW.
        .. vid:: ID of Viewport (Unused since Windows can't have multiple viewports for now)
        """
        return self.windows[wid]["viewport"]

    def get_batch_from_window(self, wid : int = MAIN_WINDOW, bid : int = MAIN_BATCH) -> pg.graphics.Batch:
        """
        Get the batch `bid` from the window `wid`.

        .. wid:: ID of Window.
        .. bid:: ID of Batch.
        """
        return self.windows[wid]["batches"][bid]
    
    def blit(
        self,
        surface        : pg.image.AbstractImage,
        transform      : Transform,
        sprite         : pg.sprite.Sprite,
        window_id      : int               = MAIN_WINDOW,
        group          : pg.graphics.Group = None,
        ignore_scaling : bool              = False
    ) -> None:
        """
        Draw an Image to a Window's main viewport.
        
        The batch must be manually set, you can get this batch by running `get_batch_from_window()` and setting that as your sprites batch.
        If you don't have a Sprite, you can call `viewport._allocate_sprite()`, you can get `viewport` by running `get_viewport_from_window()`.
        
        You must also pass a Transform object, you can get this by either manually creating one yourself or running `Transform.new(...)`.

        .. surface:: Pyglet image.
        .. transform:: Transform object to tell where the image is drawn.
        .. sprite:: Pyglet Sprite with the Batch set properly.
        .. window_id:: ID of Window to draw. Defaults to MAIN_WINDOW.
        .. group:: Pyglet Group. Defaults to None.
        .. ignore_scaling:: Ignore scale properties in transform.
        """
        if not surface:
            return
        if not transform.visible:
            return
        if not (transform.scale_x or transform.scale_y):
            return
        if not sprite:
            return
        if not (self.windows and self.windows.get(window_id, None)):
            return
        
        windata             = self.windows[window_id]
        viewport : Viewport = windata["viewport"]
        if not viewport:
            return

        x, y = transform.into_screen_coords(viewport.size)
        
        # Set properties for sprite
        if sprite.image != surface:
            sprite.image = surface
        
        # Adjustments
        if ignore_scaling:
            w,h             = surface.width,surface.height
            scale_x,scale_y = 1,1
        else:
            w,h             = transform.w,transform.h
            scale_x,scale_y = transform.scale
        
        # Make the sprite center
        if transform.rotation:
            sprite.image.anchor_x = w/4
            sprite.image.anchor_y = h/4
            x += w/2
            y += h/2

        if sprite.rotation != transform.rotation:
            sprite.rotation = transform.rotation
        if sprite.x != x:
            sprite.x = x
        if sprite.y != y:
            sprite.y = y
        if sprite.group != group:
            sprite.group = group
        if sprite.scale_x != scale_x:
            sprite.scale_x = scale_x
        if sprite.scale_y != scale_y:
            sprite.scale_y = scale_y
        if sprite.opacity != int(transform.alpha):
            sprite.opacity = int(transform.alpha)
        sprite.visible = True