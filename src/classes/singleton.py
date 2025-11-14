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
    global running,game,cvars,display,mouse,loader,keyboard,scene,savefile,lang

    # Initialize metadata
    game  = GameData()

    cvars = cvar.CvarCollection()
    cvars.init_from(game.project_data["cvars"])
    
    # Initialize resource loader
    loader = resources.Loader()

    # Initialize display and windows
    display = ui.Display()
    display.add_window(
        game.name, 
        game.viewport_size, 
        game.viewport_size, 
        game.viewport_color,
        loader.load(cvars.get("icon_file")),
        game.winresizable,
        game.winminsize,
        game.winmaxsize
    )

    # Initialize garbage collection
    gc.enable()

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
    return False

def is_anything_pressed() -> bool:
    """Returns true if any key is pressed or held down."""
    return False

# Variables
display   : ui.Display          = None
cvars     : cvar.CvarCollection = None
game      : GameData            = None
loader    : resources.Loader    = None
lang      : Language            = None
savefile  : saving.Savefile     = None
mouse     : Mouse               = None
keyboard  : Keyboard            = None
scene     : resources.Scene     = None
running   : bool                = False
uid       : int                 = 0
sid       : int                 = 0
delta     : float               = 0.0
uptime    : float               = 0.0

_screenc_cache = {}

# Load the engine components
load_engine()