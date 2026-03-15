# Import libraries
import pyglet       as pg, pygame
import pyvidplayer2 as pvd, time

# Import components
from classes.customprops import *
from classes             import hooks, profiling, resources, nodes, ui
from classes             import crash_screen as error_handler
from classes             import saving, networking
from classes.locals      import *

# Init mixer
pygame.mixer.init(channels=2)

# Functions
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
    return time.strftime('%d %m %Y %H %M %S')

def load_engine():
    global running,game,display,debug,mouse,loader,keyboard,scene,savefile,lang,icon,clock,theme

    # Make debug config
    debug = DebugConfig()

    # Initialize metadata
    game   = GameData()
    
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

    # See if anti-aliasing should be on
    ui.set_anti_aliasing(game.win.antialiasing)

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
    if os.path.exists(loader._get_true_path(str(name))):
        cursor = loader.load(name)
    else:
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
                if mouse.buttons[action]: return True
    return False

def is_anything_pressed() -> bool:
    """Returns true if any key is pressed or held down."""
    for i in keyboard.pressed:
        if keyboard.pressed[i]: return True
    for i in keyboard.held:
        if keyboard.held[i]: return True
    return False

def handle_closing():
    """
    Saves the game, frees the scene and sets `running` to False.

    Only call this function when you are closing the game engine.
    """
    global running, savefile, scene
    
    running = False
    savefile.save_data()
    scene.free()

def set_mouse(cursor, wid = MAIN_WINDOW):
    """Set the mouse cursor.
    
    Args:
        cursor: One of the pre-defined system mouse cursors (`MOUSE_NORMAL`, `MOUSE_POINT`...)
        wid: The ID of the Window that should have this cursor. Defaults to `MAIN_WINDOW`.
    """
    window = display.get_window(wid)
    
    window.set_mouse_cursor(cursors[cursor])

def quit():
    display.get_window().on_close()
    
# Variables
_inpyinstaller : bool                   = getattr(sys, "frozen", False)  and hasattr(sys, "_MEIPASS")
_pyinstallpath : str                    = getattr(sys, "_MEIPASS", None)
cursors        : int                    = {}    #: Dict of cursor images
clock          : pg.clock.Clock         = None  #: Pyglet clock
display        : ui.Display             = None  #: Display object. See `classes.ui.Display`
game           : GameData               = None  #: GameData object.
loader         : resources.Loader       = None  #: Loader object.
lang           : Language               = None  #: Language type.
debug          : DebugConfig            = None  #: Debug configuration
savefile       : saving.Savefile        = None  #: Savefile
mouse          : Mouse                  = None  #: Mouse type.
theme          : resources.Theme        = None  #: Theme.
icon           : pg.image.AbstractImage = None  #: Icon image.
keyboard       : Keyboard               = None  #: Keyboard type.
scene          : resources.Scene        = None  #: Scene object.
running        : bool                   = False #: If the engine is running
uid            : int                    = 0     #: amount of Objects
sid            : int                    = 0     #: amount of pygame Channels
delta          : float                  = 0.0   #: deltaTime
tdelta         : float                  = 0.0   #: `engine.delta` but not multiplied by speed
fps            : float                  = 0.0   #: Framerate according to `engine.tdelta`
uptime         : float                  = 0.0   #: This value is how many seconds you have been running the engine.
speed          : int                    = 1     #: This value is the multiplier of `engine.delta`.

_screenc_cache : dict = {}