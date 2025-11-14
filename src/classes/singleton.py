# Import libraries
import pygame, pyglet as pg, json, gc
import pyvidplayer2   as pvd

# Import components
from classes             import cvar, ui, resources, nodes, commons_subprchook
from classes             import crash_screen as error_handler
from classes             import saving
from classes.customprops import *
from classes.locals      import *

# Init mixer
pygame.mixer.init()

# Functions
def load_engine():
    global running,game,cvars,display,mouse,loader,keyboard,scene,savefile,lang,icon,clock

    # Initialize metadata
    game  = GameData()

    cvars = cvar.CvarCollection()
    cvars.init_from(game.project_data["cvars"])
    
    # Initialize resource loader
    loader = resources.Loader()

    # Initialize display and windows
    icon    = loader.load(cvars.get("icon_file"))
    display = ui.Display()
    clock   = pg.clock.Clock()
    display.add_window(
        name           = game.name, 
        size           = game.viewport_size, 
        viewport_size  = game.viewport_size, 
        viewport_color = game.viewport_color,
        icon           = icon,
        resizable      = game.winresizable,
        minimum_size   = game.winminsize,
        maximum_size   = game.winmaxsize
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
    lang    = Language(f'{cvars.get("lang_dir", "res://lang")}/{savefile.get("lang", "en")}.json')

    # Set running flag to true
    running = True

def is_action_pressed(entry) -> bool:
    """Returns true if action `entry` is pressed. Might return False if the entry's settings have `holdable` disabled."""
    action_entries = game.project_data.get("actions",{})
    if entry in action_entries:
        action_data = action_entries[entry]
        for action in action_data["actions"]:
            # Get action ID (pyglet.window.key.X, MOUSE_X)
            action_id     = action
            
            # See if action is not just mouse input and handle it
            action_is_key = (not action in MOUSE_BUTTONS)
            if action_is_key:
                if (action_id in keyboard.held and action_data["holdable"]
                    or 
                    action_id in keyboard.pressed and not action_data["holdable"]):
                    return True
            else:
                if mouse.buttons[action_id]: return True
    return False

def is_anything_pressed() -> bool:
    """Returns true if any key is pressed or held down."""
    for i in keyboard.pressed:
        if keyboard.pressed[i]: return True
    for i in keyboard.held:
        if keyboard.held[i]: return True
    return False

def handle_closing():
    savefile.save_data()

# Variables
clock     : pg.clock.Clock         = None
display   : ui.Display             = None
cvars     : cvar.CvarCollection    = None
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

_screenc_cache = {}

# Load the engine components
load_engine()