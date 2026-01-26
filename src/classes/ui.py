# Import libraries
import pyglet as pg, os

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

glEnable(GL_BLEND)
glEnable(GL_CULL_FACE)

# Colors
red         = [255, 0,   0,   255]
green       = [255, 0,   0,   255]
blue        = [0,   0,   255, 255]
black       = [0,   0,   0,   255]
white       = [255, 255, 255, 255]
transparent = [0,   0,   0,     1]

# Classes
class EklWindow(pg.window.Window):
    def __init__(
        self,
        wid        : int,
        
        width      : int | None                        = None,
        height     : int | None                        = None,
        caption    : str | None                        = None,
        resizable  : bool                              = False,
        style      : str | None                        = None,
        fullscreen : bool                              = False,
        visible    : bool                              = True,
        vsync      : bool                              = True,
        file_drops : bool                              = False,
        display    : pg.display.Display         | None = None,
        screen     : pg.display.Screen          | None = None,
        config     : Config                     | None = None,
        context    : pg.gl.Context              | None = None,
        mode       : pg.display.base.ScreenMode | None = None,
    ) -> None:
        # Setup variables
        self.closed     = False
        self.viewports  = {}
        self.id         = wid
        
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

    def __repr__(self):
        return f"{self.__class__.__name__}(size={self.width}x{self.height}, id={self.id})"

    ## Say cheese!
    def screenshot(self):
        """Say cheese!"""
        os.makedirs("screenshots", exist_ok=True)
        pg.image.get_buffer_manager().get_color_buffer().save(f"screenshots/{engine.get_date()}.png")
    
    ## Closing the window
    def on_close(self):
        engine.display.remove_window(self.id) 
    def close(self):
        if self.closed:
            return
        self.closed = True
        for vid in self.viewports.copy():
            viewport = self.viewports[vid]
            viewport.close()
        super().close()

    ## Size related    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.set_fullscreen(not self.fullscreen)
    def on_resize(self, width, height):
        for vid in self.viewports:
            viewport = self.viewports[vid]
            if VIEWPORT_EQUAL_WINDOW in viewport.flags:
                viewport.w = width
                viewport.h = height
    
    ## Drawing
    def on_draw(self):
        self.switch_to()
        self.clear()
    def flip(self):
        if self.closed:
            return

        for vid in self.viewports:
            viewport    = self.viewports[vid]
            viewport.draw()
        engine.spronscr = 0
        super().flip()
    
    ## Mouse Events
    def on_mouse_motion(self, x, y, dx, dy):
        engine.mouse.pos  = [x, y]
        engine.mouse.dpos = [dx,dy]
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # Who gives a fuck about some "Apple Mighty Mouse" like just put the fries in the bag cuh
        engine.mouse.pos    = [x, y]
        engine.mouse.scroll = scroll_y
    def on_mouse_press(self, x, y, button, modifiers):
        engine.mouse.pos             = [x, y]
        engine.mouse.buttons[button] = True
    def on_mouse_release(self, x, y, button, modifiers):
        engine.mouse.pos             = [x, y]
        engine.mouse.buttons[button] = False
    
    ## Keyboard Events
    def on_key_press(self, symbol, modifiers):
        engine.keyboard.modifiers       = modifiers
        engine.keyboard.held[symbol]    = True
        engine.keyboard.pressed[symbol] = True     
    def on_key_release(self, symbol, modifiers):
        engine.keyboard.modifiers       = modifiers
        engine.keyboard.held[symbol]    = False
        engine.keyboard.pressed[symbol] = False
    
    ## Misc. Events
    def on_file_drop(self, x, y, paths):
        engine.mouse.pos   = [x, y]
        engine.mouse.paths = paths

    ## Add Viewport
    def add_viewport(
        self,
        size  : list[int] = [640,480],
        color : list[int] = black,
        flags : list[int] = [VIEWPORT_EQUAL_WINDOW],
        pos   : list[int] = [0,0]
    ):
        """
        Add a viewport to Window `wid`. Returns its ID.

        Args:
            size: Size of the window's viewport. Using the flag `VIEWPORT_EQUAL_WINDOW` nullifies this.
            color: Background color of the viewport.
            flags: List of Viewport flags. Ex (`NO_CLEAR, NO_CLEAR_BACKGROUND`..)
            pos: Viewport position.
        """

        vid = len(self.viewports)

        viewport          = Viewport(vid, self, flags)
        viewport.position = pos
        viewport.tsize    = size
        viewport.set_background(*color)
        viewport.add_batch()

        self.viewports[vid] = viewport

        return vid

class Viewport(Transform):
    """A class to manage a portion of a Window."""
    def __init__(self, vid : int, window : EklWindow, flags : list = []):
        """Initialize a Viewport.
        
        Args:
            vid: ID of the Viewport.
            window: Window that the Viewport is attached to.
            flags: List of Viewport flags. Ex (`NO_CLEAR, NO_CLEAR_BACKGROUND`..)"""
        super().__init__()
        
        self.cam         = CameraTransform()
        self._background = [0,0,0,1]

        self.flags = flags

        self.batches      = []
        self.framebuffer  = None
        self.color_buffer = None
        self.depth_buffer = None

        self._closing = False

        self.id = vid

        self.window                = window
        self.window.viewports[vid] = self

        self._make_framebuffer()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.w}x{self.h}, id={self.id})"
    
    ## def get_screen_pos(self, transform : Transform):
        x,y = transform.into_screen_coords(self.size)
        return x - self.cam.x, y - self.cam.y
    
    ## Add Batch
    def add_batch(self):
        """Add a batch to Window `wid`. Returns its ID."""
        bid      = len(self.batches)
        batch    = pg.graphics.Batch()

        self.batches.append(batch)
        return bid

    ## Convenience functions
    def get_screen_pos(self, transform : Transform):
        """Get the position of a Transform in the Window."""
        x,y = transform.into_screen_coords(self.size)
        return x - self.cam.x, y - self.cam.y
    def is_onscreen(self, transform : Transform):
        """Get if a Transform is visible in the Viewport."""
        if engine.debug.sprite_always_visible:
            return True
        
        x,y = transform.into_screen_coords(self.tsize)
        if not (
            ((x - self.cam.x) * self.cam.zoom) + (transform.w * self.cam.zoom) < 0 or
            ((x - self.cam.x) * self.cam.zoom) > self.w                       or
            ((y - self.cam.y) * self.cam.zoom) + (transform.h * self.cam.zoom) < 0 or
            ((y - self.cam.y) * self.cam.zoom) > self.h
        ):  
            if engine.debug.track_visible_sprites:
                engine.spronscr += 1
            return True
        return False
    
    ## Framebuffer related
    def _make_framebuffer(self):
        if self.window:
            self.window.switch_to()
        self.framebuffer  = pg.image.Framebuffer()
        self.color_buffer = pg.image.Texture.create(
            self.w, self.h,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST,
            internalformat=GL_RGBA
        )
        self.depth_buffer = pg.image.buffer.Renderbuffer(self.w, self.h, GL_DEPTH_COMPONENT)
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
        self.framebuffer.attach_renderbuffer(self.depth_buffer, attachment=GL_DEPTH_ATTACHMENT)
    def _resize_framebuffer(self):
        if self.window:
            self.window.switch_to()
        self.color_buffer = pg.image.Texture.create(
            self.w, self.h,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST,
            internalformat=GL_RGBA8
        )
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
    def _delete_buffer(self):
        if not self.framebuffer:
            return
        if self.window:
            self.window.switch_to()
        self.framebuffer.delete()
        self.color_buffer.delete()
        self.depth_buffer.delete()
    
    ## Transform related
    def into_screen_coords(self):
        return super().into_screen_coords(self.window.size)
    def _set_size(self, w, h):
        self._resize_framebuffer()    
    
    ## Drawing related
    def set_background(self, r=0,g=0,b=0,a=255):
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
    def draw(self):
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
        glDisable(GL_BLEND)
        self.framebuffer.bind()
        if not NO_CLEAR_BACKGROUND in self.flags:
            glClearColor(*self._background)
        if not NO_CLEAR in self.flags:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Move camera
        self._move_camera()

        # Draw batches for this Viewport
        for batch in self.batches:
            batch.draw()
        
        # Unbind viewport
        self.framebuffer.unbind()
        
        # Reset camera
        self._reset_camera()

        # Draw Viewport to Window
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        x, y = self.into_screen_coords()
        self.color_buffer.blit(x, y, self.id)
    
    ## Camera functions    
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
    
    ## Closing
    def close(self):
        """
        Delete the framebuffer and close the Viewport.
        """
        self._closing = True
        self._delete_buffer()
        self.window.viewports.pop(self.id)

class Display:
    """A class to manage `EklWindow`'s."""
    windows        = {}
    main_window_id = None

    ## Spoof. To be removed
    def blit(
        self,
        transform      : Transform,
        sprite         : pg.sprite.Sprite,
        window_id      : int               = MAIN_WINDOW,
        viewport_id    : int               = MAIN_VIEWPORT,
        group          : pg.graphics.Group = None,
        region         : list | None       = None,
        ignore_scaling : bool              = False,
    ) -> None:
        """
        Draw a Sprite to a Window's main viewport.
        
        The batch must be manually set, you can get this batch by running `get_batch_from_window()` and setting that as your sprites batch.
        If you don't have a Sprite, you can call `viewport._allocate_sprite()`, you can get `viewport` by running `get_viewport_from_window()`.
        
        You must also pass a Transform object, you can get this by either manually creating one yourself or running `Transform.new(...)`.

        Args:
            transform:
                `Transform` object to tell where the image is drawn.
            sprite:
                Sprite with the Batch set properly and `EklImage` for the image.
            window_id:
                ID of Window to draw. Defaults to `MAIN_WINDOW`.
            viewport_id:
                ID of Viewport. Used for information about viewport width and height, etc. Defaults to `MAIN_VIEWPORT`.
            group:
                Pyglet `Group`. Defaults to `None`.
            ignore_scaling:
                Read, silly.
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
        
        viewport : Viewport = self.get_viewport_from_window(window_id, viewport_id)
        if not viewport:
            return

        # Fix dimensions
        transform.w = sprite.image.width
        transform.h = sprite.image.height

        # Get sprite's scaling
        scale_x,scale_y = transform.scale
        if ignore_scaling:
            scale_x,scale_y=1,1

        # Get XY position
        x, y = transform.into_screen_coords(viewport.tsize)

        # Set image's flip values properly
        if transform.flip_w or transform.flip_h:
            sprite.image = sprite.image.flip(transform.flip_w, transform.flip_h)
        
        # Set image's region (if it isn't None)
        if region != None:
            cropped      = sprite.image.get_region(*region)
            sprite.image = cropped
        
        # Set sprite's properites
        if transform.rotation:
            sprite.image.anchor_x = sprite.image.width  // 2
            sprite.image.anchor_y = sprite.image.height // 2
            x += (sprite.image.anchor_x) * scale_x
            y += (sprite.image.anchor_y) * scale_y
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
        viewport_id    : int               = MAIN_VIEWPORT,
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
            viewport_id: ID of Viewport. Used for information about viewport width and height, etc. Defaults to `MAIN_VIEWPORT`.
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
        
        viewport : Viewport = self.get_viewport_from_window(window_id, viewport_id)
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
        x,y = transform.into_screen_coords(viewport.tsize)

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

    ## Add/Remove
    def _add_window_entry(self):
        wid               = len(self.windows)
        self.windows[wid] = None
        return wid
    def add_window(self,
        name           : str                    = DEFAULT_NAME,
        size           : list[int]              = [640,480],
        viewport_flags : list                   = [],
        viewport_size  : list[int] | int        = [640,480],
        viewport_color                          = black,
        icon           : pg.image.AbstractImage = None,
        resizable      : bool                   = True,
        minimum_size   : None | list[int]       = [640,480],
        maximum_size   : None | list[int]       = None,
        visible        : bool                   = True,
        fpsvisible     : bool                   = False,
        wid            : None | int             = None
    ) -> int:
        """
        Add a new Window, returns its Window ID.

        Args:
            name: Title of the window.
            size: Size of the window.
            viewport_size: Size of the window's viewport. Using the flag `VIEWPORT_EQUAL_WINDOW` nullifies this.
            viewport_flags: Flags to be passed to the viewport.
            viewport_color: Background color of the viewport.
            icon: Image resource of the Window Icon, or None.
            resizable: Allow the window to be resizable if True.
            minimum_size: List of the minimum size the window can be, or None if you dont want a limit.
            maximum_size: List of the maximum size the window can be, or None if you dont want a limit.
            visible: Make the window visible if True. Defaults to True.
            fpsvisible: Show the FPS if True.
            wid: Create the window in a predetermined window ID if the argument is not None.
        
        Flags:
            VIEWPORT_EQUAL_WINDOW: Used to make the Viewport size equal the Window size.
            NO_CLEAR: Do not clear the Viewport before rendering.
            NO_CLEAR_BACKGROUND: Ignore the set background color.
        """
        print(f" ~ Initialize Window '{name}'")
        
        # Reserve window slot
        if wid == None:
            wid = self._add_window_entry()
        if self.main_window_id == None:
            self.main_window_id = wid
        
        # Create Window
        window        = EklWindow(
            wid       = wid,

            width     = size[0],
            height    = size[1],
            caption   = name,
            resizable = resizable
        )

        # Set Window properties
        if minimum_size:
            window.set_minimum_size(*minimum_size)
        if maximum_size:
            window.set_maximum_size(*maximum_size)
        if icon:
            window.set_icon(icon)
        
        # Fill in information for the Window slot
        self.windows[wid] = window

        # Create viewports
        window.add_viewport(color=viewport_color, flags=viewport_flags, size=viewport_size) # MAIN_VIEWPORT
        window.add_viewport(color=transparent,    flags=[VIEWPORT_EQUAL_WINDOW])            # UI_VIEWPORT

        # Add FPS Display
        if fpsvisible or engine.debug.fps_visible:
            fpsd = engine.hooks.HookFPSDisplay(window, [255,255,255,127])

        # Return Window ID
        return wid
    def remove_window(self, wid=MAIN_WINDOW):
        """Close and remove a Window from the Display.
        
        Args:
            wid: ID of the Window."""
        window = self.get_window(wid)
        
        window.close()
        self.windows.pop(wid)
    
    ## Close
    def close_windows(self):
        for wid in self.windows:
            window = self.get_window(wid)
            if window:
                window.close()
    
    ## Get
    def get_window(self, wid=MAIN_WINDOW) -> EklWindow:
        """Get a Window from the Display.
        
        Args:
            wid: ID of the Window."""
        return self.windows[wid]  
    def get_viewport_from_window(self, wid : int = MAIN_WINDOW, vid : int = MAIN_VIEWPORT) -> Viewport:
        """
        Get the viewport `vid` from the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
            vid: ID of Viewport. Defaults to MAIN_VIEWPORT.
        """
        if not wid in self.windows:
            return
        
        try:
            return self.get_window(wid).viewports.get(vid)
        except:
            return
    def get_batch_from_window(self, wid : int = MAIN_WINDOW, vid: int = MAIN_VIEWPORT, bid : int = MAIN_BATCH) -> pg.graphics.Batch:
        """
        Get the batch `bid` from the viewport `vid` which is from the window `wid`.

        Args:
            wid: ID of Window. Defaults to MAIN_WINDOW.
            vid: ID of Window's viewport. Defaults to MAIN_VIEWPORT.
            bid: ID of Batch from viewport. Defaults to MAIN_BATCH.
        """
        if not wid in self.windows:
            return
        
        try:
            return self.get_viewport_from_window(wid, vid).batches[bid]
        except:
            return