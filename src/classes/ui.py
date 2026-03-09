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

# Cast some fucking OpenGL spells i don't know
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
        vsync      : bool                              = False,
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
        self._lastvid   = MAIN_VIEWPORT
        
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
        engine.display._doomed.append(self.id) 
    
    def close(self):
        if self.closed:
            return
        
        self.switch_to()
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
    def flip(self):
        if self.closed:
            return
        
        self.switch_to()
        for vid in self.viewports:
            viewport    = self.viewports[vid]
            viewport.draw()
        
        if engine.debug.show_graph:
            engine.debug.draw_debug_graph()
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
        engine.mouse.pos                  = [x, y]
        engine.mouse.buttons[button]      = True
        engine.mouse.just_clicked[button] = True
    def on_mouse_release(self, x, y, button, modifiers):
        engine.mouse.pos                  = [x, y]
        engine.mouse.buttons[button]      = False
        engine.mouse.just_clicked[button] = False
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        engine.mouse.pos      = [x, y]
        engine.mouse.dpos     = [dx,dy]
        engine.mouse.dragging = True
    
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

        vid            = self._lastvid
        self._lastvid += 1

        viewport          = Viewport(vid, self, flags)
        viewport.position = pos
        viewport.tsize    = size
        viewport.set_background(*color)
        viewport.add_batch()

        self.viewports[vid] = viewport

        return vid

class Viewport(Transform, Color):
    """A class to manage a portion of a Window."""
    _supports_tsize = True

    def __init__(self, vid : int, window : EklWindow, flags : list = []):
        """Initialize a Viewport.
        
        Args:
            vid: ID of the Viewport.
            window: Window that the Viewport is attached to.
            flags: List of Viewport flags. Ex (`NO_CLEAR, NO_CLEAR_BACKGROUND`..)"""
        super().__init__()
        Color.__init__(self)
        
        self.cam = CameraTransform()

        self.flags = flags

        self.batches      = []
        self.framebuffer  = None
        self.color_buffer = None
        self.depth_buffer = None
        self.citem      = None

        self._closing = False

        self.id = vid

        self.window                = window
        self.window.viewports[vid] = self

        self._make_framebuffer()
        
        self._lastbid = MAIN_BATCH

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.w}x{self.h}, id={self.id})"
    
    ## Add Batch
    def add_batch(self):
        """Add a batch to the Viewport. Returns its ID."""
        bid            = self._lastbid
        batch          = pg.graphics.Batch()
        self._lastbid += 1
        
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
            return True
        return False

    ## Framebuffer related
    def _make_framebuffer(self):
        if self.window:
            self.window.switch_to()
        self.framebuffer  = pg.image.Framebuffer()
        self.color_buffer = pg.image.Texture.create(
            self._w, self._h,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST,
            internalformat=GL_RGBA
        )
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
        self.citem = pg.sprite.Sprite(self.color_buffer, z=self.id)
        self._set_anchors()
    def _resize_framebuffer(self):
        if self.window:
            self.window.switch_to()
        if not self.framebuffer:
            return
        self.color_buffer.delete()
        self.color_buffer = pg.image.Texture.create(
            self._w, self._h,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST,
            internalformat=GL_RGBA8
        )
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
        self.citem.image = self.color_buffer
        self._set_anchors()
        
    def _delete_buffer(self):
        if not self.framebuffer:
            return
        if self.window:
            self.window.switch_to()
        self.framebuffer.delete()
        self.color_buffer.delete()
        self.citem.delete()

    ## Transform related
    def _set_anchors(self):
        # For some reason when rotating the anchors dont anchor anchoringly and rotate around the bottom left of the image (????)
        self.citem.image.anchor_x = self.citem.image.width  // 2
        self.citem.image.anchor_y = self.citem.image.height // 2
        self.citem._update_position()
    def into_screen_coords(self, do_flip : bool = True):
        return super().into_screen_coords(self.window.size, do_flip)
    def _set_alpha(self, deg):
        self.citem.opacity = deg
    def _set_rot(self, deg):
        self.citem.rotation = deg
    def _set_scale(self, x, y):
        self.citem.scale_x = x
        self.citem.scale_y = y
        self._set_anchors()
    def _set_size(self, w, h):
        self._resize_framebuffer()
    def _set_visible(self, val):
        self.citem.visible = val

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
        self.rgb = [
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
            glClearColor(*self.rgb)
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
        x, y         = self.into_screen_coords()
        self.citem.x = x + (self.color_buffer.anchor_x * self.scale_x)
        self.citem.y = y + (self.color_buffer.anchor_y * self.scale_y)
        self.citem.draw()

    ## Camera functions    
    def _reset_camera(self):
        view_matrix = self.window.view.scale(
            (
                1 / self.cam.zoom,
                1 / self.cam.zoom,
                1
            )
        )
        view_matrix = view_matrix.rotate(
            -self.cam.rotation * (math.pi/180),
            (
                0,
                0,
                1
            )
        )
        view_matrix = view_matrix.translate(
            (
                self.cam.x * self.cam.zoom,
                self.cam.y * self.cam.zoom,
                self.cam.z * self.cam.zoom
            )
        )
        self.window.view = view_matrix
    def _move_camera(self):
        view_matrix = self.window.view.translate(
            (
                -self.cam.x * self.cam.zoom,
                -self.cam.y * self.cam.zoom,
                -self.cam.z * self.cam.zoom
            )
        )
        view_matrix = view_matrix.rotate(
            self.cam.rotation * (math.pi/180),
            (
                0,
                0,
                1
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
    windows        : dict[int, EklWindow] = {}          # Dict of windows
    _doomed        : int                  = []          # List of windows to run through remove_window
    _merciless     : int                  = []          # List of windows to run through window.close
    main_window_id : int | None           = None        # Name
    _windid        : int                  = MAIN_WINDOW # Next ID
    print(" ~ Initialize Display")
    
    ## Update
    def update(self):
        for doomedid in self._doomed.copy():
            self.remove_window(doomedid)
        for doomedid in self._merciless.copy():
            self.get_window(doomedid).close()
            self.windows[doomedid] = None
        
        self._doomed.clear()
        self._merciless.clear()
    
    ## Add/Remove
    def _add_window_entry(self):
        wid               = self._windid
        self.windows[wid] = None
        self._windid     += 1
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
        vsync          : bool                   = False,
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
            vsync: If True, turns on V-Sync.
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
        window         = EklWindow(
            wid        = wid,

            width      = size[0],
            height     = size[1],
            caption    = name,
            resizable  = resizable,
            
            visible    = False,
            
            vsync      = vsync,
            file_drops = True,
        )
        
        # Fill in information for the Window slot
        self.windows[wid] = window

        # Create viewports
        window.add_viewport(color=viewport_color, flags=viewport_flags, size=viewport_size) # MAIN_VIEWPORT
        window.add_viewport(color=transparent,    flags=[VIEWPORT_EQUAL_WINDOW])            # UI_VIEWPORT

        # Add FPS Display
        if fpsvisible or engine.debug.fps_visible:
            fpsd = engine.hooks.HookFPSDisplay(window, [255,255,255,255])
        
        # Finishing up
        if minimum_size:
            window.set_minimum_size(*minimum_size)
        if maximum_size:
            window.set_maximum_size(*maximum_size)
        if icon:
            window.set_icon(icon)
        window.set_visible(visible)

        # Return Window ID
        return wid
    def remove_window(self, wid=MAIN_WINDOW):
        """Close and remove a Window from the Display.
        
        Args:
            wid: ID of the Window."""
        if not wid in self.windows:
            print(f"??? {wid}")
            return
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