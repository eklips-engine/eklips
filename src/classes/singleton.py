# Import libraries
import pygame, pyglet as pg, json, gc
import pyvidplayer2   as pvd

# Import components
from classes             import cvar, ui, resources, nodes, commons_subprchook, crash_screen as error_handler
from classes.customprops import *
from classes.locals      import *

# Init mixer
pygame.mixer.init()

# Functions
def load_engine():
    global running,game,cvars,display,mouse,loader,keyboard,scene

    # Initialize metadata
    game  = GameData()

    cvars = cvar.CvarCollection()
    cvars.init_from(game.project_data["cvars"])
    
    # Initialize resource loader
    loader = resources.Loader()

    # Initialize display and windows
    display = ui.Display()
    display.add_window(game.name, game.viewport_size, game.viewport_size, game.viewport_color)

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

    # Set running flag to true
    running = True

# Variables
display   : ui.Display          = None
cvars     : cvar.CvarCollection = None
game      : GameData            = None
loader    : resources.Loader    = None
running   : bool                = False
mouse     : Mouse               = None
keyboard  : Keyboard            = None
uid       : int                 = 0
sid       : int                 = 0
scene     : resources.Scene     = None
delta     : float               = 0.0
uptime    : float               = 0.0

_screenc_cache = {}

# Load the engine components
load_engine()