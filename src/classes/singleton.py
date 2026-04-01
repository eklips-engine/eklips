## Import libraries
import pyglet       as pg, pymunk
import pyvidplayer2 as pvd, time

## Import components
from classes.customprops import *
from classes             import hooks, resources, nodes, ui
from classes             import crash_screen as error_handler
from classes             import saving, networking
from classes.locals      import *

## Functions
def rgbtohex(rgb: list) -> str:
    """Turn a hex color into an RGB color."""
    r,g,b = rgb
    return "#{:02x}{:02x}{:02x}".format(round(r),round(g),round(b))
def invertrgb(rgb: list) -> list:
    """Invert an RGB color."""
    r,g,b = rgb
    return [255-r,255-g,255-b]

def get_date():
    """Returns the date and time."""
    return time.strftime("%d %m %Y %H %M %S")

def load_engine():
    global running,game,display,debug,mouse,loader,keyboard,scene,savefile,lang,icon,clock,theme

    # Make debug config
    debug = DebugConfig()

    # Initialize metadata
    game   = GameData()

    # See if anti-aliasing should be on
    ui.set_anti_aliasing(game.win.antialiasing)

    # Initialize resource loader
    loader = resources.Loader()

    # Initialize display and windows
    icon    = loader.load(game.win.icofile)
    
    if not running:
        display = ui.Display()
        clock   = pg.clock.Clock()
        display.add_window(
            name           = game.name,
            
            size           = game.win.vsize,
            viewport_size  = game.win.vsize,
            viewport_flags = [VIEWPORT_EQUAL_WINDOW],
            viewport_color = game.win.color,
            resizable      = game.win.resizable,
            minimum_size   = game.win.minsize,
            maximum_size   = game.win.maxsize,
            
            vsync          = False,

            icon           = icon
        )
    else:
        for wid in display.windows:
            if wid != MAIN_WINDOW:
                window = display.windows[wid]
                
                if window:
                    window.close()
                    display.windows.pop(wid)
    
    # Initialize user input sections
    mouse    = Mouse()
    keyboard = Keyboard()

    # Initialize Scene
    scene = resources.Scene()
    if game.loading_scene:
        scene.load(game.loading_scene)
    else:
        scene.load(game.master_scene)
    
    # Initialize savefile
    savefile = saving.Savefile()

    # Initialize localization
    lang = Language(f'{game.langdir}/{savefile.get("lang", "en")}.json')

    # Load custom fonts
    for i in game.fonts:
        name, path = i
        loader.load(path)
        pg.font.load(name)
    
    # Load theme
    theme = resources.Theme.load("root://_assets/theme.rc")
    
    # Load cursors
    for i in CURSORS:
        load_cursor(i)

    # Set running flag to true
    running = True

def load_cursor(name) -> pg.window.MouseCursor | pg.window.ImageMouseCursor:
    """
    Load a mouse cursor from its name.

    Args:
        name: The mouse cursor to load. Can either be a path or constant (e.g. `MOUSE_NORMAL`..)
    """ 
    try:
        cursor = loader.load(name)
    except:
        cursor = display.get_window().get_system_mouse_cursor(name)
    
    cursors[name] = cursor
    return cursor

def is_action_pressed(entry) -> bool:
    """Returns true if action `entry` is pressed. Might return False if the entry's settings have `holdable` disabled."""
    action_entries = game.actions
    if entry in action_entries:
        action_data = action_entries[entry]
        for action in action_data["actions"]:
            # action = pyglet.window.key.X, MOUSE_LEFT, ...
            # See if action is not just mouse input and handle it
            action_is_key = (not action in MOUSE_BUTTONS)

            if action_is_key:
                if (
                    (action in keyboard.held and action_data["holdable"])
                    or
                    (action in keyboard.pressed and not action_data["holdable"])
                   ):
                    if keyboard.held[action]: return True
            else:
                if (
                    (action in mouse.buttons      and action_data["holdable"])
                    or
                    (action in mouse.just_clicked and not action_data["holdable"])
                   ):
                    if mouse.buttons[action]: return True
    return False

def is_anything_pressed() -> bool:
    """Returns true if any key or button is pressed or held down."""
    for i in keyboard.pressed:
        if keyboard.pressed[i]: return True
    for i in keyboard.held:
        if keyboard.held[i]: return True
    for i in mouse.just_clicked:
        if mouse.just_clicked[i]: return True
    for i in mouse.buttons:
        if mouse.buttons[i]: return True
    return False

def handle_closing():
    """
    Saves the savefile, closes every window besides ID main, frees the scene and sets `running` to False.

    Only call this function when you are closing the game engine.
    """
    global running, savefile, scene
    
    running = False
    savefile.save_data()
    scene.free()
    
    for wid in display.windows:
        window = display.get_window(wid)
        if not window:
            continue
        if window.id != MAIN_WINDOW:
            window.close()

def set_mouse(cursor, wid = MAIN_WINDOW):
    """Set the mouse cursor.
    
    Args:
        cursor: One of the pre-defined system mouse cursors (`MOUSE_NORMAL`, `MOUSE_POINT`...)
        wid: The ID of the Window that should have this cursor. Defaults to `MAIN_WINDOW`.
    """
    window = display.get_window(wid)
    
    if not window.is_basewindow:
        window.set_mouse_cursor(cursors[cursor])

def quit(error_code=0):
    handle_closing()
    display.windows[MAIN_WINDOW].close()
    sys.exit(error_code)
    
## Variables
#: If the engine is in Pyinstaller?
_inpyinstaller : bool = getattr(sys, "frozen", False)
#: The directory of Pyinstaller if in Pyinstaller.
_pyinstallpath : str  = pg.resource.get_script_home()

#: OpenGL Filter to apply to images
_image_filter : int = pg.gl.GL_NEAREST

#: The ID of the Viewport all Nodes are displayed in when in the editor.
_editor_viewport_id : int = 0
#: If you are in the Eklips Editor. Only tool Nodes can have their scripts updated.
#: see Object.processable for more.
ineditor : bool = False

#: A dictionary of cursor images.
cursors : int                    = {}
clock   : pg.clock.Clock         = None

#: Display object. See `classes.ui.Display` for more info.
display : ui.Display             = None

#: Data about the currently running project.
game : GameData = None

#: A class to load the currently running project's resources.
loader : resources.Loader = None

#: A class storing Language information.
lang  : Language    = None

#: Debug configuration.
debug : DebugConfig = None

#: The project's savefile.
savefile : saving.Savefile = None

#: A class storing information about mouse input.
mouse    : Mouse    = None
#: A class storing information about keyboard input.
keyboard : Keyboard = None

#: A class storing a Theme used by some widgets.
theme : resources.Theme = None

#: The icon of the main window.
icon : pg.image.AbstractImage = None

#: A class of the main scene.
scene : resources.Scene = None

#: True, if the engine is running
running : bool = False
uid     : int  = 0

#: The current deltaTime, sped up by the `speed` variable.
delta  : float = 0.0
#: The true current deltaTime.
tdelta : float = 0.0
#: The framerate of the engine.
fps    : float = 0.0
#: How many seconds the engine has been running. Useful for tracking playtime.
uptime : float = 0.0
#: How fast the engine should be.
speed  : int   = 1

#: Space
world = pymunk.Space()