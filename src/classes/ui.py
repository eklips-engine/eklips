# Import libraries
import pyglet as pg, gc, time, pygame, os

# Import components
import classes.singleton     as engine
from classes.locals          import *
from classes.customprops     import *
from pyglet.gl               import *

# Functions
def set_anti_aliasing(yn : bool):
    if yn: value = GL_LINEAR
    else:  value = GL_NEAREST
    pg.image.Texture.default_mag_filter = pg.image.Texture.default_min_filter = value

glEnable(GL_CULL_FACE)

# Colors
_r    = [0,0,0]
_rs   = [1,1,1]
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

red   = [255,0,0]
green = [255,0,0]
blue  = [0,0,255]
black = [0,0,0]
white = [255,255,255]
f = 1

# Classes
class EklWindow(pg.window.Window):
    def __init__(
        self,
        width      : int | None                   = None,
        height     : int | None                   = None,
        caption    : str | None                   = None,
        resizable  : bool                         = False,
        style      : str | None                   = None,
        fullscreen : bool                         = False,
        visible    : bool                         = True,
        vsync      : bool                         = True,
        file_drops : bool                         = False,
        display    : pg.display.Display    | None = None,
        screen     : pg.display.Screen     | None = None,
        config     : Config                | None = None,
        context    : pg.gl.Context         | None = None,

        mode       : pg.display.base.ScreenMode | None = None
    ) -> None:

        # Setup variables
        self._focused  = False
        self.closed    = True
        self.viewports = []
        self.wid       = -1
        
        # Init
        ## Code taken from pyglet/window/base/__init__.py line 508-546
        if not display:
            display = pg.display.get_display()
        if not screen:
            screen  = display.get_default_screen()
        if not config:
            alpha_size = None
            transparent_fb = False
            if style in ('transparent', 'overlay'):
                alpha_size = 8
                transparent_fb = True
            for template_config in [
                Config(double_buffer=True, depth_size=24, major_version=3, minor_version=3,
                       alpha_size=alpha_size, transparent_framebuffer=transparent_fb),
                Config(double_buffer=True, depth_size=16, major_version=3, minor_version=3,
                       alpha_size=alpha_size, transparent_framebuffer=transparent_fb),
                None,
            ]:
                try:
                    config = screen.get_best_config(template_config)
                    break
                except pg.window.NoSuchConfigException:
                    pass
            if not config:
                raise pg.window.NoSuchConfigException('No standard config is available.')
        else:
            style : str
            if style in ('transparent', 'overlay'):
                config.alpha_size = 8
                config.transparent_framebuffer = True
        
        if not context:
            context = config.create_context(None)

        super().__init__(
            width,      height,
            caption,    resizable,
            style,      fullscreen,
            visible,    vsync,
            file_drops, display,
            screen,     config,
            context,    mode
        )

        # Set validity to true
        self.closed = False

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.set_fullscreen(not self.fullscreen)

    @property
    def focused(self):
        """If the Window is focused. Read-write."""
        return self._focused
    
    @focused.setter
    def focused(self, value):
        if value:
            self.activate()
        else:
            self.minimize()
    
    def on_close(self):
        if self.closed: return
        for viewport in self.viewports:
            viewport.close()
        self.closed = True
        engine.display._close_window(self.wid)
    
    def close(self):
        super().close()
        self.closed = True
    
    def on_context_lost(self):
        self._focused = False
    
    def on_activate(self):
        self._focused = True
    
    def on_deactivate(self):
        self._focused = False

    def on_resize(self, width, height):
        self._focused = True

        for viewport in self.viewports:
            if VIEWPORT_EQUAL_WINDOW in viewport.flags:
                viewport.width  = width
                viewport.height = height
    
    def on_draw(self):
        self.switch_to()
        self.clear()
        
    def flip(self):
        if not self.invalid:
            return

        for viewport in self.viewports:
            viewport.flip()
        engine.spronscr = 0
        super().flip()
    
    def on_mouse_motion(self, x, y, dx, dy):
        engine.mouse.pos  = [x, y]
        engine.mouse.dpos = [dx,dy]
    
    def on_mouse_press(self, x, y, button, modifiers):
        engine.mouse.pos             = [x, y]
        engine.mouse.buttons[button] = True

    def on_mouse_release(self, x, y, button, modifiers):
        engine.mouse.pos             = [x, y]
        engine.mouse.buttons[button] = False
    
    def on_key_press(self, symbol, modifiers):
        engine.keyboard.modifiers       = modifiers
        engine.keyboard.held[symbol]    = True
        engine.keyboard.pressed[symbol] = True
        
    def on_key_release(self, symbol, modifiers):
        engine.keyboard.modifiers       = modifiers
        engine.keyboard.held[symbol]    = False
        engine.keyboard.pressed[symbol] = False
    
    def on_file_drop(self, x, y, paths):
        engine.mouse.pos   = [x, y]
        engine.mouse.paths = paths

class CameraTransform(Transform):
    def __init__(self):
        super().__init__()
        self._zoom = 1
    
    @property
    def zoom(self):      return self._zoom
    @zoom.setter
    def zoom(self, val): self._zoom = val

class Viewport:
    def __init__(
            self,
            vid,
            flags    : list          = [],
            batches  : list          = [],
            size     : list[int,int] = [640,480],
            position : list[int,int] = [0,0]
        ):
        self.flags            = flags
        self.id               = vid
        self.cam              = CameraTransform()
        self._width           = size[1]
        self._height          = size[0]
        self._x               = position[0]
        self._y               = position[1]
        self._background      = [0,0,0,1]

        self.framebuffer        = None
        self.color_buffer       = None
        self.depth_buffer       = None
        self.window : EklWindow = None
        self._closing           = False
        self.batches            = batches

        self.sprites : list[pg.sprite.Sprite] = []
        self.labels  : list[pg.text.Label]    = []
        self.used_labels                      = {}
        self.used_sprites                     = {}
        self._base_img                        = engine.loader.load("root://_assets/error.png")

    def get_screen_pos(self, transform : Transform):
        x,y = transform.into_screen_coords(self.size)
        return x - self.cam.x, y - self.cam.y
    
    def is_onscreen(self, transform : Transform):
        if engine.debug.sprite_always_visible:
            return True
        
        x,y = transform.into_screen_coords(self.size)
        if not (
            ((x - self.cam.x) * self.cam.zoom) + (transform.w * self.cam.zoom) < 0 or
            ((x - self.cam.x) * self.cam.zoom) > self.width                       or
            ((y - self.cam.y) * self.cam.zoom) + (transform.h * self.cam.zoom) < 0 or
            ((y - self.cam.y) * self.cam.zoom) > self.height
        ):  
            if engine.debug.track_visible_sprites:
                engine.spronscr += 1
            return True
        return False
    
    def add_batch(self):
        bid      = len(self.batches)
        batch    = pg.graphics.Batch()

        self.batches.append(batch)
        return bid
    def _make_framebuffer(self):
        if self.window:
            self.window.switch_to()
        self.framebuffer  = pg.image.Framebuffer()
        self.color_buffer = pg.image.Texture.create(
            self.width, self.height,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST
        )
        self.depth_buffer = pg.image.buffer.Renderbuffer(self.width, self.height, GL_DEPTH_COMPONENT)
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
        self.framebuffer.attach_renderbuffer(self.depth_buffer, attachment=GL_DEPTH_ATTACHMENT)
    def _resize_framebuffer(self):
        if self.window:
            self.window.switch_to()
        self.color_buffer = pg.image.Texture.create(
            self.width, self.height,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST
        )
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
    def provide_window(self, window, master=False):
        """
        Provide the window `window` to the Viewport to draw to.

        .. note:: This takes a while since the framebuffer has to be remade to be
        apart of the windows context.

        Args:
            window: Window object (engine.ui.EklWindow).
        """
        # Set variables
        self.window           = window

        # Remake framebuffer to be happy
        self._delete_buffer()
        self._make_framebuffer()
    def _delete_buffer(self):
        if not self.framebuffer:
            return
        self.framebuffer.delete()
        self.color_buffer.delete()
        self.depth_buffer.delete()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.width}x{self.height})"
    
    @property
    def width(self):  return int(self._width)
    @property
    def height(self): return int(self._height)
    
    @property
    def x(self): return int(self._x)
    @property
    def y(self): return int(self._y)

    @property
    def size(self): return [self.width,self.height]

    @size.setter
    def size(self, value):
        self._width  = int(value[0])
        self._height = int(value[1])
        self._resize_framebuffer()

    @x.setter
    def x(self, value): self._x = int(value)
    @y.setter
    def y(self, value): self._y = int(value)
    
    @width.setter
    def width(self, value):
        self._width = int(value)
        self._resize_framebuffer()
    @height.setter
    def height(self, value):
        self._height = int(value)
        self._resize_framebuffer()

    def _make_new_sprite(self, batch_id=MAIN_BATCH):
        sprite         = pg.sprite.Sprite(self._base_img, batch = self.batches[batch_id])
        sprite.visible = False
        i              = len(self.sprites)
        self.sprites.append(sprite)
        self.used_sprites[i] = False
        return sprite, i
    def _make_new_label(self, batch_id=MAIN_BATCH):
        label         = pg.text.Label(batch = self.batches[batch_id])
        label.visible = False
        i             = len(self.labels)
        self.labels.append(label)
        self.used_labels[i] = False
        return label, i

    def delete_label(self, label_id : int):
        if not label_id in self.labels:
            return
        self.labels[label_id].delete()
        self.used_labels[sprite_id] = False
        gc.collect()
    def delete_sprite(self, sprite_id : int):
        if not sprite_id in self.sprites:
            return
        self.sprites[sprite_id].delete()
        self.used_sprites.pop(sprite_id)
        self.used_sprites[sprite_id] = False
        gc.collect()
    
    def _allocate_label(self, batch_id=MAIN_BATCH):
        i = 0
        for label in self.labels:
            if not self.used_labels[i]:
                self.used_labels[i] = True
                return label, i
            i += 1
        
        label, i = self._make_new_label(batch_id)
        self.used_labels[i] = True
        return label, i
    def _allocate_sprite(self, batch_id=MAIN_BATCH):
        i = 0
        for sprite in self.sprites:
            if not self.used_sprites[i]:
                self.used_sprites[i] = True
                return sprite, i
            i += 1
        
        sprite, i = self._make_new_sprite(batch_id)
        self.used_sprites[i] = True
        return sprite, i
    
    def _deallocate_sprite(self, sprite_id):
        self.sprites[sprite_id].visible = False
        self.used_sprites[sprite_id] = False
    def _deallocate_label(self, label_id):
        self.labels[label_id].visible = False
        self.used_labels[label_id] = False
    
    def screenshot(self):
        """Say cheese!"""
        os.makedirs("screenshots", exist_ok=True)
        self.color_buffer.save(f"screenshots/Screenshot {time.strftime('%d %m %Y %H %M %S')}.png")
    
    def set_background(self, r=0,g=0,b=0, a=1):
        """
        Set the background color of the Viewport.

        Args:
            r: Red value of the background color (0-255).
            g: Green value of the background color (0-255).
            b: Blue value of the background color (0-255).
            a: Alpha of the background color (0-255).
        """
        self._background = [
            r / 255,
            g / 255,
            b / 255,
            a / 255
        ]
    def flip(self):
        """
        Draw viewport contents to the window.
        """
        # If you or the window is closed, don't bother
        if self._closing:
            return
        if not self.window:
            return
        if self.window.closed:
            return
        if not self.window.visible:
            return
        
        # Init viewport
        self.window.switch_to()
        self.framebuffer.bind()
        if self._background[:3] != [0,0,0] and not NO_CLEAR_BACKGROUND in self.flags:
            glClearColor(*self._background)
        if not NO_CLEAR in self.flags:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Move camera
        self._move_camera()

        # Draw batches for this Viewport and unbind buffer
        for batch in self.batches:
            batch.draw()
        
        # Unbind viewport
        self.framebuffer.unbind()
        
        # Reset camera
        self._reset_camera()

        # Draw Viewport to Window
        self.color_buffer.blit(self.x, self.y, self.id)
    
    def _reset_camera(self):
        view_matrix = self.window.view.scale(
            (
                1 / self.cam.zoom,
                1 / self.cam.zoom,
                1
            )
        )
        view_matrix = view_matrix.translate(
            (
                self.cam.x * self.cam.zoom,
                self.cam.y * self.cam.zoom,
                0
            )
        )
        self.window.view = view_matrix
    def _move_camera(self):
        view_matrix = self.window.view.translate(
            (
                -self.cam.x * self.cam.zoom,
                -self.cam.y * self.cam.zoom,
                0
            )
        )
        view_matrix = view_matrix.scale(
            (
                self.cam.zoom,
                self.cam.zoom,
                1
            )
        )
        self.window.view = view_matrix
    
    def close(self):
        """
        Delete the framebuffer and close the Viewport.
        """
        self._closing = True
        self._delete_buffer()
        gc.collect()
    
class Display:
    print(" ~ Initialize Display")
    _doomed = []
    windows                 = {}
    main_window_id          = None
    _fontsizecache          = {}
    display_id              = 0
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(display_id={self.display_id})"

    def get_size(self):
        """Returns the size of the screen in pixels."""
        return pygame.display.get_desktop_sizes()[0]

    def add_window(self,
        name           : str                    = DEFAULT_NAME,
        size           : list[int]              = [640,480],
        viewport_flags : list                   = [],
        viewport_size  : list[int] | int        = VIEWPORT_EQUAL_WINDOW,
        viewport_color                          = black,
        icon           : pg.image.AbstractImage = None,
        resizable      : bool                   = True,
        minimum_size   : None | list[int]       = [648,648],
        maximum_size   : None | list[int]       = None,
        wid            : int                    = AUTOMATICALLY_CREATE,
        visible        : bool                   = True,
        fpsvisible     : bool                   = False
    ) -> int:
        """
        Add a new Window, returns its Window ID.

        Args:
            name: Title of the window.
            size: Size of the window.
            viewport_size: Size of the window's viewport. This can be replaced with the flag `VIEWPORT_EQUAL_WINDOW`.
            viewport_flags: Flags to be passed to the viewport.
            viewport_color: Background color of the viewport.
            icon: Image resource of the Window Icon, or None.
            resizable: Allow the window to be resizable if True.
            minimum_size: List of the minimum size the window can be, or None if you dont want a limit.
            maximum_size: List of the maximum size the window can be, or None if you dont want a limit.
            wid: Create the window in a predetermined window ID if the argument is not AUTOMATICALLY_CREATE.
            visible: Make the window visible if True. Defaults to True.
            fpsvisible: Show the FPS if True.
        
        Flags:
            VIEWPORT_EQUAL_WINDOW: Used to make the Viewport size equal the Window size.
            NO_CLEAR: Do not clear the Viewport before rendering.
            NO_CLEAR_BACKGROUND: Ignore the set background color.
        """

        # Fix properties
        if wid == AUTOMATICALLY_CREATE:
            wid = len(self.windows)

        print(f" ~ Initialize Window '{name}'")

        if viewport_size == VIEWPORT_EQUAL_WINDOW:
            viewport_flags.append(VIEWPORT_EQUAL_WINDOW)
            viewport_size = size
        
        if self.main_window_id == None:
            self.main_window_id = wid
        
        # Create Window
        window        = EklWindow(
            width     = size[0],
            height    = size[1],
            caption   = name,
            resizable = resizable,
            visible   = False
        )

        # Create viewport
        viewport = Viewport(MAIN_VIEWPORT, viewport_flags, [], viewport_size, [0,0])
        viewport.set_background(*viewport_color)
        viewport.provide_window(window)
        viewport.add_batch()
        
        # Make the Window entry
        self.windows[wid] = {
            "name":       name,
            "window":     window,
            "fpsd":       None
        }
        
        # Set Window's viewport to the one we just made
        window.viewports.append(viewport)

        # Add FPS Display
        if fpsvisible or engine.debug.fps_visible:
            fpsd = engine.hooks.HookFPSDisplay(window, [255,255,255,127])
            self.windows[wid]["fpsd"] = fpsd

        # Set Window properties
        if minimum_size:
            window.set_minimum_size(*minimum_size)
        if maximum_size:
            window.set_maximum_size(*maximum_size)
        if icon:
            window.set_icon(icon)
        if visible:
            window.set_visible()
        window.wid = wid

        # Return Window ID
        return wid
    
    def add_viewport(
        self,
        wid            : int             = MAIN_WINDOW,
        viewport_size  : list[int] | int = VIEWPORT_EQUAL_WINDOW,
        viewport_color                   = black,
        flags          : int             = 0
    ):
        """
        Add a viewport to Window `wid`. Returns its ID.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
            viewport_size: Size of the window's viewport. Use constant `VIEWPORT_EQUAL_WINDOW` to make the Viewport size equal the Window size.
            viewport_color: Background color of the viewport.
            flags: Viewport flags. Ex (`NO_CLEAR | NO_CLEAR_BACKGROUND`..)
        """

        window   = self.get_window(wid)
        if viewport_size == VIEWPORT_EQUAL_WINDOW:
            flags.append(VIEWPORT_EQUAL_WINDOW)
            viewport_size = window.size

        vid = len(window.viewports)

        viewport = Viewport(vid, flags, [], viewport_size, [0,0])
        viewport.set_background(*viewport_color)
        viewport.provide_window(window)
        viewport.add_batch()

        window.viewports.append(viewport)

        return vid

    def add_batch(self, wid : int = MAIN_WINDOW, vid : int = MAIN_VIEWPORT):
        """
        Add a batch to Window `wid`. Returns its ID.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
            vid: ID of Window's viewport. Defaults to MAIN_VIEWPORT.
        """
        if not (self.windows and self.windows.get(wid, None)):
            return
        
        viewport = self.get_viewport_from_window(wid, vid)
        return viewport.add_batch()

    def clear_window(self, wid : int = MAIN_WINDOW):
        """
        Clear the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
        """
        if not (self.windows and self.windows.get(wid, None)):
            return
        
        window_data           = self.windows[wid]
        if window_data.get("viewport",None):
            window_data["viewport"].clear()
    
    def clear_windows(self):
        """
        Clear all windows and their viewports.
        """
        self._delete_in_queue()
        for wid in self.windows.copy():
            self.clear_window(wid)
        
    def flip_window(self, wid : int = MAIN_WINDOW):
        """
        Flip the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
        """
        if not (self.windows and self.windows.get(wid, None)):
            return
        
        window_data           = self.windows[wid]
        if window_data.get("viewport",None):
            window_data["viewport"].flip()
    
    def _delete_in_queue(self):
        for wid in self._doomed:
            self._close_window(wid)
        self._doomed.clear()
    
    def flip_windows(self):
        """
        Flip all windows and their viewports.
        """
        self._delete_in_queue()
        for wid in self.windows.copy():
            self.flip_window(wid)
        self._delete_in_queue()
    
    def close_window(self, wid : int = MAIN_WINDOW):
        """
        Close the window `wid` after updating.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
        """
        self._doomed.append(wid)
    
    def _close_window(self, wid):
        """
        Close the window `wid` immediately.

        Args:
            wid: ID of Window.
        """
        if not (self.windows and self.windows.get(wid, None)):
            return
        
        window_data = self.windows[wid]
        window_data["window"].close()
        window_data["window"]     = None
        if wid == self.main_window_id:
            self.main_window_id = None
        self.windows.pop(wid)
        gc.collect()
    
    def close_windows(self, forced : bool = False, blacklist : list = []):
        """
        Close all windows and their viewports.

        Args:
            forced: If true, close the window immediately. This may cause issues.
            blacklist: List of Window IDs to NOT. CLOSE.
        """
        for wid in self.windows.copy():
            if wid in blacklist:
                continue
            if forced:
                self._close_window(wid)
            else:
                self.close_window(wid)

    def get_window(self, wid : int = MAIN_WINDOW) -> EklWindow:
        """
        Get the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
        """
        return self.windows.get(wid, {"window": None})["window"]

    def get_viewport_from_window(self, wid : int = MAIN_WINDOW, vid : int = MAIN_VIEWPORT) -> Viewport:
        """
        Get the viewport `vid` from the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
            vid: ID of Viewport. Defaults to MAIN_VIEWPORT.
        """
        return self.get_window(wid).viewports[vid]

    def get_batch_from_window(self, wid : int = MAIN_WINDOW, vid: int = MAIN_VIEWPORT, bid : int = MAIN_BATCH) -> pg.graphics.Batch:
        """
        Get the batch `bid` from the viewport `vid` which is from the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
            vid: ID of Window's viewport. Defaults to MAIN_VIEWPORT.
            bid: ID of Batch from viewport. Defaults to MAIN_BATCH.
        """
        return self.get_viewport_from_window(wid, vid).batches[bid]
    
    def blit(
        self,
        transform      : Transform,
        sprite         : pg.sprite.Sprite,
        window_id      : int               = MAIN_WINDOW,
        group          : pg.graphics.Group = None,
        region         : list | None       = None
    ) -> None:
        global f
        """
        Draw a Sprite to a Window's main viewport.
        
        The batch must be manually set, you can get this batch by running `get_batch_from_window()` and setting that as your sprites batch.
        If you don't have a Sprite, you can call `viewport._allocate_sprite()`, you can get `viewport` by running `get_viewport_from_window()`.
        
        You must also pass a Transform object, you can get this by either manually creating one yourself or running `Transform.new(...)`.

        Args:
            transform:
                `Transform` object to tell where the image is drawn.
            sprite:
                `EklImage` Sprite with the Batch set properly.
            window_id:
                ID of Window to draw. Defaults to `MAIN_WINDOW`.
            group:
                Pyglet `Group`. Defaults to `None`.
        """
        if not transform.visible:
            return
        if not (transform.scale_x or transform.scale_y):
            return
        if not sprite:
            return
        window = self.get_window(window_id)
        if not window:
            return
        if window.closed:
            return
        if not window.visible:
            return
        
        viewport : Viewport = self.get_viewport_from_window(window_id)
        if not viewport:
            return

        x, y = transform.into_screen_coords(viewport.size)
        
        # Get sprite's dimensions
        w,h             = transform.tsize
        scale_x,scale_y = transform.scale

        # Set image's flip values properly
        if transform.flip_w or transform.flip_h:
            sprite.image = sprite.image.flip(transform.flip_w, transform.flip_h)
        
        # Set image's region (if it isn't None)
        if region != None:
            cropped      = sprite.image.get_region(*region)
            sprite.image = cropped
        
        # Set sprite's properites
        if transform.rotation:
            sprite.image.anchor_x = w / 4
            sprite.image.anchor_y = h / 4
            x += w / 2
            y += h / 2
        else:
            sprite.image.anchor_x = 0
            sprite.image.anchor_y = 0
        
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
        if sprite.opacity != transform.alpha:
            sprite.opacity = transform.alpha
        sprite.visible = viewport.is_onscreen(transform)
    
    def blit_label(
        self,
        text           : str,
        transform      : Transform,
        label          : pg.text.Label,
        window_id      : int               = MAIN_WINDOW,
        group          : pg.graphics.Group = None,
        font_name      : str               = DEFAULT_FONT_NAME,
        font_size      : int               = DEFAULT_FONT_SIZE
    ) -> list[int,int]:
        """
        Draw a Label to a Window's main viewport.
        
        The batch must be manually set, you can get this batch by running `get_batch_from_window()` and setting that as your labels batch.
        If you don't have a Label, you can call `viewport._allocate_label()`, you can get `viewport` by running `get_viewport_from_window()`.
        
        You must also pass a Transform object, you can get this by either manually creating one yourself or running `Transform.new(...)`.

        Args:
            text: Read the property silly
            transform: Transform object to tell where the image is drawn.
            label: Pyglet Label with the Batch set properly.
            window_id: ID of Window to draw. Defaults to MAIN_WINDOW.
            group: Pyglet Group. Defaults to None.
            font_name: Read the property silly. Defaults to DEFAULT_FONT_NAME ("Arial")
            font_size: Read the property silly. Defaults to DEFAULT_FONT_SIZE (12.5)
        """
        if not text:
            return 0,0
        if not transform.visible:
            return 0,0
        if not (transform.scale_x or transform.scale_y):
            return 0,0
        if not label:
            return 0,0
        window = self.get_window(window_id)
        if not window:
            return 0,0
        if window.closed:
            return 0,0
        if not window.visible:
            return 0,0
        
        viewport : Viewport = self.get_viewport_from_window(window_id)
        if not viewport:
            return 0,0
        
        # Set properties for label
        if label.text != text:
            label.text = text
        if label.font_name != font_name:
            label.font_name = font_name
        if label.font_size != font_size:
            label.font_size = font_size
        
        # | Adjustments
        w,h = label.content_width, label.content_height

        # | Fix transform
        transform.w = w
        transform.h = h
        
        # | Get XY position
        x,y = transform.into_screen_coords(viewport.size)

        # | Set the others
        if label.rotation != transform.rotation:
            label.rotation = transform.rotation
        if label.x != x:
            label.x = x
        if label.y != y:
            label.y = y
        if label.group != group:
            label.group = group
        if label.opacity != transform.alpha:
            label.opacity = transform.alpha
        label.visible = viewport.is_onscreen(transform)
        return w,h