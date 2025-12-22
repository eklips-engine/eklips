# Import libraries
import pygame, pyglet as pg, json, gc
import pyvidplayer2   as pvd

# Import components
from classes             import hooks, ui, resources, nodes
from classes             import crash_screen as error_handler, debug
from classes             import saving
from classes.customprops import *
from classes.locals      import *

# Init mixer
pygame.mixer.init()

# Functions
def load_engine():
    global running,game,display,mouse,loader,keyboard,scene,savefile,lang,icon,clock

    # Initialize metadata
    game = GameData()
    
    # Initialize resource loader
    loader = resources.Loader()

    # Initialize display and windows
    icon    = loader.load(game.win.icofile)
    display = ui.Display()
    clock   = pg.clock.Clock()
    display.add_window(
        name           = game.name, 
        
        size           = game.win.vsize, 
        viewport_size  = game.win.vsize, 
        viewport_color = game.win.color,
        resizable      = game.win.resizable,
        minimum_size   = game.win.minsize,
        maximum_size   = game.win.maxsize,

        icon           = icon
    )

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
    
    # Load cursors
    for i in CURSORS:
        cursors[i] = display.get_window().get_system_mouse_cursor(i)
    
    # Set running flag to true
    running = True

def is_action_pressed(entry) -> bool:
    """Returns true if action `entry` is pressed. Might return False if the entry's settings have `holdable` disabled."""
    action_entries = game.project_data.get("actions",{})
    if entry in action_entries:
        action_data = action_entries[entry]
        for action in action_data["actions"]:
            # action = pyglet.window.key.X, MOUSE_LEFT, ...
            # See if action is not just mouse input and handle it
            action_is_key = (not action in MOUSE_BUTTONS)
            if action_is_key:
                if (action in keyboard.held and action_data["holdable"]
                    or 
                    action in keyboard.pressed and not action_data["holdable"]):
                    return True
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
    
    .. cursor:: One of the pre-defined system mouse cursors (`MOUSE_NORMAL`, `MOUSE_POINT`...)
    .. wid:: The ID of the Window that should have this cursor. Defaults to `MAIN_WINDOW`.
    """
    window = display.get_window(wid)
    window.set_mouse_cursor(cursors[cursor])

def quit():
    display.get_window().on_close()
    
# Variables
cursors   : int                    = {}
clock     : pg.clock.Clock         = None
display   : ui.Display             = None
game      : GameData               = None
loader    : resources.Loader       = None
lang      : Language               = None
savefile  : saving.Savefile        = None
mouse     : Mouse                  = None
icon      : pg.image.AbstractImage = None
keyboard  : Keyboard               = None
scene     : resources.Scene        = None
running   : bool                   = False
uid       : int                    = 0
sid       : int                    = 0
delta     : float                  = 0.0
uptime    : float                  = 0.0

_wincloseblacklist : list = [MAIN_WINDOW]
_screenc_cache     : dict = {}

# Load the engine components
load_engine()