## Import libraries
import pyglet as pg, os

##import components
import classes.singleton as engine
from classes.locals      import *
from classes.types       import *
from pyglet.gl           import *

## Cast some fucking OpenGL spells i don't know
glEnable(GL_BLEND)
glEnable(GL_CULL_FACE)

## Variables
groups = {}

## Classes
class EklBaseWindow(pg.window.BaseWindow):
    """A Window to handle with Eklips viewports and NOT display them in one Window."""
    is_basewindow = True

    ## Composition
    def composite(self):
        ## Make Viewports draw to their colorbuffer/texture
        self.switch_to()
        for vp in self.viewports.values():
            vp.draw()
        
        ## Presentation
        for vp in self.viewports.values():
            if vp._vpparent:
                return
            if not (vp.framebuffer and vp):
                return
            
            self.switch_to()
            self._present(vp)
    def _present(self, vp):
        if not (vp.framebuffer or vp):
            return
        x,y        = vp.into_viewport_coords(self.size, drawing=True)
        vp.citem.x = x
        vp.citem.y = y
        
        if len(vp._vpchildren):
            for child in vp._vpchildren:
                vp.framebuffer.bind()
                self._present(child)
                vp.framebuffer.unbind()
                
        vp.citem.draw()
        
    ## Getters
    @property
    def width(self): return self.get_size()[0]
    @property
    def height(self): return self.get_size()[1]
    @property
    def size(self): return self.get_size()
    @property
    def caption(self): return self._caption
    @property
    def minimum_size(self): return self._minimum_size
    @property
    def maximum_size(self): return self._maximum_size
    @property
    def visible(self): return self._visible
    @property
    def cam(self):
        vp = self.viewports.get(MAIN_VIEWPORT)
        if vp:
            return vp.cam
        return

    # Make into_viewport_coords not kill itself by adding this
    # Making these actually return the coords of the window is a bad idea for sakes of the function
    @property
    def x(self): return 0
    @property
    def y(self): return 0
    @property
    def position(self): return [0,0]

    ## Setters
    @caption.setter
    def caption(self, val):
        self._caption = val
        self.set_caption(val)
    @width.setter
    def width(self, val):
        self._width = val
        self.set_size(*self.size)
    @height.setter
    def height(self, val):
        self._height = val
        self.set_size(*self.size)
    @size.setter
    def size(self, val):
        self.set_size(*val)
    @maximum_size.setter
    def maximum_size(self, val):
        if val == None:
            self.set_maximum_size(engine.display.width, engine.display.height)
            return
        self.set_maximum_size(*val)
    @minimum_size.setter
    def minimum_size(self, val):
        if val == None:
            self.set_minimum_size(1, 1)
            return
        self.set_minimum_size(*val)
    @visible.setter
    def visible(self, val):
        self.set_visible(val)
    
    ## Init
    def _refresh_viewports(self):
        self.switch_to()
        for viewport in self.viewports.values():
            ## Remove framebuffer
            viewport._refreshing = True
            viewport._delete_buffer()

            viewport.window = self
            viewport._make_framebuffer()

            ## Remake all batches
            _revive = []
            for bid in viewport.batches:
                batch : pg.graphics.Batch = viewport.batches[bid]
                batch.invalid = True
                
                _revive.append(bid)
            viewport._lastbid = MAIN_BATCH

            for bid in _revive:
                viewport.batches.pop(bid)
                viewport.add_batch()
            viewport._refreshing = False
    def __init__(self, wid : int,
                width      : int | None                        = 1152,
                height     : int | None                        = 648,
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
                mode       : pg.display.base.ScreenMode | None = None
    ) -> None:
        """Create a lazy Window."""

        # Setup variables
        self.closed       = False
        self.viewports    = {}
        self.id           = wid
        self.render_graph = []
        self._lastvid     = MAIN_VIEWPORT

        ## Init
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
        self.switch_to()
        pg.image.get_buffer_manager().get_color_buffer().save(f"screenshots/{engine.get_date()}.png")
    
    ## Closing the window
    def on_close(self):
        engine.display._doomed.append(self.id) 
    def close(self, with_viewports=True):
        """Close the window.
        
        Args:
            with_viewports: If True, close the viewports too."""
        if self.closed:
            return
        
        self.switch_to()
        self.closed = True
        if with_viewports:
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
            viewport._set_pos(*viewport.position)
    
    ## Add Viewport
    def add_viewport(
        self,
        size  : list[int] = [640,480],
        color : list[int] = BLACK,
        flags : list[int] = [VIEWPORT_EQUAL_WINDOW],
        pos   : list[int] = [0,0],
        parent            = MAIN_WINDOW
    ):
        """
        Add a viewport to Window `wid`. Returns its ID.

        Args:
            size: Size of the window's viewport. Using the flag `VIEWPORT_EQUAL_WINDOW` nullifies this.
            color: Background color of the viewport.
            flags: List of Viewport flags. Ex (`NO_CLEAR, NO_CLEAR_BACKGROUND`..)
            pos: Viewport position.
            parent: The ID of the parent of the viewport.
        """
        vid            = self._lastvid
        self._lastvid += 1

        if parent == vid:
            parent = None
        else:
            parent = self.viewports.get(parent)

        viewport          = Viewport(vid, self, flags, parent)
        viewport.position = pos
        viewport.size     = size
        viewport.set_background(*color)
        viewport.add_batch()

        self.viewports[vid] = viewport

        return vid
class EklWindow(EklBaseWindow, pg.window.Window):
    """A modified Window to handle with Eklips viewports and display them in one Window."""
    is_basewindow = False
    
    ## Transform related
    def _set_size(self, w, h):
        self.set_size(w, h)
    
    ## Drawing
    def flip(self):
        if self.closed:
            return
        
        self.composite()
        super().flip()
    
    ## Mouse Events
    def on_mouse_motion(self, x, y, dx, dy):
        engine.mouse.position = [x, self.height - y - 10]
        engine.mouse.dpos     = [dx,dy]
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # Who gives a fuck about some "Apple Mighty Mouse" like just put the fries in the bag cuh
        engine.mouse.position = [x, self.height - y - 10]
        engine.mouse.scroll   = scroll_y
    def on_mouse_press(self, x, y, button, modifiers):
        engine.mouse.position             = [x, self.height - y - 10]
        engine.mouse.buttons[button]      = True
        engine.mouse.just_clicked[button] = True
    def on_mouse_release(self, x, y, button, modifiers):
        engine.mouse.position             = [x, self.height - y - 10]
        engine.mouse.buttons[button]      = False
        engine.mouse.just_clicked[button] = False
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        engine.mouse.position = [x, self.height - y - 10]
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
    def on_text(self, text):
        engine.keyboard.text = text
    def on_text_motion(self, motion):
        engine.keyboard.motion = motion
    
    ## Misc. Events
    def on_file_drop(self, x, y, paths):
        engine.mouse.position   = [x, y]
        engine.mouse.paths = paths
class Viewport(Transform, Color):
    """A class to manage a portion of a Window."""
    _isdisplayobject = True
    _is_viewport     = True
    
    ## Parent
    @property
    def _vpparent(self) -> Self: return self._vpppr
    @_vpparent.setter
    def _vpparent(self, val : Self):
        # Remove connection
        if self._vpppr and self in self._vpppr._vpchildren:
            self._vpppr._vpchildren.remove(self)
        
        # Connect to other parent
        if val:
            val._vpchildren.append(self)
        
        # Set parent
        self._vpppr = val
        if self.framebuffer:
            self._delete_buffer()
            self._make_framebuffer()
    @property
    def _parentvalid(self): return (self._vpparent and
                                    getattr(self._vpparent, "_is_viewport", True))

    ## Init
    def __init__(self, vid : int, window : EklWindow, flags : list = [], parent : Self = None):
        """Initialize a Viewport.
        
        Args:
            vid: ID of the Viewport.
            window: Window that the Viewport is attached to.
            flags: List of Viewport flags. Ex (`NO_CLEAR, NO_CLEAR_BACKGROUND`..)
            parent: The parent of the Viewport."""
        super().__init__()
        Color.__init__(self)
        
        self.cam = CameraTransform()

        self.flags = flags

        self.batches : dict[int, pg.graphics.Batch] = {}
        self.framebuffer                            = None
        self.color_buffer                           = None
        self.depth_buffer                           = None
        self.citem                                  = None
        
        ## Viewport node-like system to not interfere with Scenes if ExtraViewport
        self._vpchildren      = []
        self._vpppr           = None
        self._vpparent : Self = parent

        ## Source of truth
        # If batches are being refreshed
        self._refreshing = False
        # Am i created? Or am i destroyed?
        self._state = "uninitialized"
        # Do i need a new Batch?
        self._batch_pending = False
        
        ## ID
        self.id = self._drawing_vid = vid
        
        ## Add self to window's viewport registry
        self.window                = window
        self.window.viewports[vid] = self

        ## Make the framebuffer
        self._make_framebuffer()
        
        ## Track available batch id
        self._lastbid = MAIN_BATCH
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.w}x{self.h}, id={self.id}, wid={self.window})"
    
    ## Add Batch
    def add_batch(self):
        """Add a batch to the Viewport. Returns its ID."""
        bid            = self._lastbid
        batch          = pg.graphics.Batch()
        
        self.batches[bid] = batch
        self._lastbid    += 1
        return bid

    ## Convenience functions
    def is_onscreen(self, transform : Transform):
        """Get if a Transform is visible in the Viewport."""
        if engine.debug.sprite_always_visible:
            return True
        
        x,y = transform.into_viewport_coords(viewport=self)
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
        if self._state != "uninitialized":
            return
        self._state = "created"

        if self.window:
            self.window.switch_to()
        self.framebuffer  = pg.image.Framebuffer()
        self.color_buffer = pg.image.Texture.create(
            self._w, self._h,
            min_filter=GL_NEAREST, mag_filter=GL_NEAREST,
            internalformat=GL_RGBA
        )
        self.framebuffer.attach_texture(self.color_buffer, attachment=GL_COLOR_ATTACHMENT0)
        self._make_sprite()
        self._set_anchors()
    def _make_sprite(self):
        if self.citem:
            self.citem.batch = None
            self.citem.delete()
            self.citem       = None
        
        self.citem          = pg.sprite.Sprite(self.color_buffer, z=self.id)
        self._batch_pending = True
    def _resize_framebuffer(self):
        if self._state in ("destroyed", "uninitialized"):
            return
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
        if not self.framebuffer and not self.color_buffer and not self.citem:
            return
        if self.window:
            self.window.switch_to()
        self.citem.batch = None
        
        if self.citem:
            self.citem.delete()
            self.citem = None
        if self.framebuffer:
            self.framebuffer.delete()
            self.framebuffer = None
        if self.color_buffer:
            self.color_buffer.delete()
            self.color_buffer = None

    ## Transform related
    def _set_anchors(self):
        self.citem.image.anchor_x = self._w // 2
        self.citem.image.anchor_y = self._h // 2
        self.citem._update_position()
    def into_viewport_coords(self, viewport=None, drawing : bool = False, parent_rect=None):
        if self._vpparent:
            return super().into_viewport_coords(self._vpparent, drawing, parent_rect)
        else:
            return super().into_viewport_coords(self.window, drawing, parent_rect)
    def _set_alpha(self, deg):
        self.citem.opacity = deg
    def _set_rot(self, deg):
        self.citem.rotation = deg
    def _set_scale(self, x, y):
        self.citem.scale_x = x
        self.citem.scale_y = y
    def _set_size(self, w, h):
        self._resize_framebuffer()
    def _set_visible(self, val):
        self.citem.visible = val
    
    ## Drawing related
    def _finalize_batch(self):
        if not self._batch_pending:
            return
        if not self.color_buffer or self.color_buffer.id is None:
            return

        self._batch_pending = False
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
        Draw viewport contents to the colorbuffer texture.
        """
        ## If you or the window is closed, don't bother
        if not self.window:
            return
        if self.window.closed or not self.window.visible:
            return
        if not self.framebuffer:
            return
        
        ## Fix batch if needed
        if self._batch_pending:
            self._finalize_batch()
        
        ## Init viewport
        self.framebuffer.bind()
        if not NO_CLEAR_BACKGROUND in self.flags:
            glClearColor(*self.rgb)
        if not NO_CLEAR in self.flags:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        ## Move camera
        self._move_camera()

        ## Draw batches for this Viewport
        for bid in self.batches:
            batch = self.batches[bid]
            batch.draw()
        
        ## Unbind viewport
        self.framebuffer.unbind()
        
        ## Reset camera
        self._reset_camera()
    
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
            -self.cam.altrotation,
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
            self.cam.altrotation,
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
        if self._state == "destroyed":
            return
        self._state = "destroyed"

        self.window.viewports.pop(self.id)
        self._closing  = True
        self._runnable = False
        
        self._delete_buffer()
        self._vpparent = None
class Display:
    """A class to manage `EklWindow`'s."""
    windows        : dict[int, EklWindow] = {}          # Dict of windows
    _doomed        : int                  = []          # List of windows to run through remove_window
    _merciless     : int                  = []          # List of windows to run through window.close
    main_window_id : int | None           = None        # Name
    _displayobj    : pg.display.Display   = pg.display.get_display()
    _windid        : int                  = MAIN_WINDOW # Next ID
    print(" ~ Initialize Display")
    
    ## Size
    @property
    def primary_screen(self):
        return self._displayobj.get_default_screen()
    @property
    def primary_scr_info(self):
        return self.primary_screen.get_mode()
    
    @property
    def width(self):
        return self.primary_scr_info.width
    @property
    def height(self):
        return self.primary_scr_info.height
    @property
    def size(self):
        return [self.width, self.height]
    
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
        viewport_color                          = BLACK,
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
        
        Attributes:
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
        window.add_viewport(color=TRANSPARENT,    flags=[VIEWPORT_EQUAL_WINDOW])            # UI_VIEWPORT

        # Add FPS Display
        if fpsvisible or engine.debug.show_fps:
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
        """Closes every open Window."""
        for wid in self.windows:
            window = self.get_window(wid)
            if window:
                window.close()
        self.windows.clear()
    
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

## Functions
def request_group(order     : int):
    """Get a group with the order `order`.
    
    Args:
        order: The order of the group."""
    if not order in groups:
        groups[order] = pg.graphics.Group(order)
    return groups[order]
def set_anti_aliasing(value : bool):
    """Turn on/off anti-aliasing.
    
    Args:
        value: True for on, False for off."""
    aliasval = GL_LINEAR if value else GL_NEAREST

    engine._image_filter                = aliasval
    pg.image.Texture.default_mag_filter = pg.image.Texture.default_min_filter = aliasval

def _rebase_window(window : EklWindow):
    """EklWindow -> EklBaseWindow"""
    
    new_window           = EklBaseWindow(window.id,
        window.width,       window.height,
        window.caption,     window.resizeable,
        window.style,       window.fullscreen,
        window.visible,     window.vsync,
        window._file_drops, window.display,
        window.screen,      window.config
    )
    new_window._lastvid  = window._lastvid
    new_window.viewports = window.viewports
    new_window.on_close = window.on_close
    new_window._refresh_viewports()

    window.viewports = {}
    window.close(False)
    del window

    engine.display.windows[new_window.id] = new_window
    return new_window
def _unbase_window(window : EklBaseWindow):
    """EklBaseWindow -> EklWindow"""

    new_window           = EklWindow(window.id,
        window.width,       window.height,
        window.caption,     window.resizeable,
        window.style,       window.fullscreen,
        window.visible,     window.vsync,
        window._file_drops, window.display,
        window.screen,      window.config
    )
    new_window._lastvid  = window._lastvid
    new_window.viewports = window.viewports
    new_window.on_close = window.on_close
    new_window._refresh_viewports()

    window.viewports = {}
    window.close(False)
    del window

    engine.display.windows[new_window.id] = new_window
    return new_window