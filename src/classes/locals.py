import pyglet as pg, socket as sock, math, sys
from typing        import *
from pyglet.window import key

USE_GAME_PARENT = "UseFileParent" #: Use the game.json file's parent as the project dir
USE_GAME_CV_DIR = "UseFileCVar"   #: Use the specified project dir in the game.json file

NAME         = "Eklips Engine" #: Name of the engine
BDATE        = [13, 3, 2026]  #:  Uses DD/MM/YYYY format
MAJOR        = "5"            #: Major; [5].0 A 
MINOR        = "0"            #: Minor;  5.[0]A 
HOTFIX       = "A"            #: Hotfix; 5. 0[A]
BUILD        = 30             #: Increment every time a major feature has been added/completely overhauled
VERSION      = f"{MAJOR}.{MINOR}{HOTFIX}"
VERSION_FULL = f"v{VERSION}.build{BUILD}"
print(f"{NAME} {VERSION_FULL}")

AUTOMATICALLY_CREATE = 50152971
DETECT               = 50152972

MAIN_WINDOW           = 0 # Main Window ID
MAIN_BATCH            = 0 # Main Batch ID
MAIN_VIEWPORT         = 0 # Main Viewport ID
UI_VIEWPORT           = 1 # Viewport ID for UI
DEFAULT_NAME          = "Eklips Engine" # Default window name
VIEWPORT_EQUAL_WINDOW = 50151 #: Viewport size = Window size
NO_CLEAR_BACKGROUND   = 50152 #: Don't clear the Viewport
NO_CLEAR              = 50153 #: Ignore Viewport's color background
DEFAULT_FONT_SIZE     = 12.5 #: Default font size
DEFAULT_FONT_NAME     = "Arial" #: Default font name

USE_SCENE_TREE = 5474

ZDE_FIX = 0.00000001

ERROR_ICON = "root://_assets/error.png"
EKL_ICON   = "root://_assets/icon.png"

MOUSE_LEFT    = 1 #: Left mouse button
MOUSE_MIDDLE  = 2 #: Scrollwheel button
MOUSE_RIGHT   = 4 #: Right mouse button
MOUSE_BUTTONS = [MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT] #: Mouse buttons

MOUSE_POINT     = pg.window.Window.CURSOR_HAND #: Pointing mouse cursor
MOUSE_HELP      = pg.window.Window.CURSOR_HELP #: "?" mouse cursor
MOUSE_CROSS     = pg.window.Window.CURSOR_CROSSHAIR #: Crosshair mouse cursor
MOUSE_NO        = pg.window.Window.CURSOR_NO #: Forbidden mouse cursor
MOUSE_WAIT      = pg.window.Window.CURSOR_WAIT #: Waiting mouse cursor
MOUSE_IBEAM     = pg.window.Window.CURSOR_TEXT #: I-beam mouse cursor
MOUSE_DRAGGABLE = "root://_assets/grab.cur" #: Grabbing mouse cursor
MOUSE_DRAG      = "root://_assets/grabbing.cur" #: Grabbing mouse cursor
MOUSE_NORMAL    = pg.window.Window.CURSOR_DEFAULT #: Default mouse cursor
#: List of cursors
CURSORS         = [MOUSE_IBEAM, MOUSE_POINT, MOUSE_HELP, MOUSE_CROSS, MOUSE_NO, MOUSE_WAIT, MOUSE_NORMAL, MOUSE_DRAG, MOUSE_DRAGGABLE]

MOUSE_DEFAULT_STATE = {MOUSE_LEFT: 0, MOUSE_RIGHT: 0, MOUSE_MIDDLE: 0}

INTERNET_ABORTED   = 253132 #: Internet connection was aborted.
INTERNET_CONNECTED = 253133 #: Client connected successfully.
INTERNET_SERVER    = 253123 #: The entity is a server.
INTERNET_CLIENT    = 253122 #: The entity is a client.

if getattr(sys, 'is_pyglet_doc_run', False) or getattr(sys, "is_doc_running", False):
    INTERNET_IP    = "???" #: The IP of this device.
else:
    INTERNET_IP    = sock.gethostbyname(sock.gethostname()) #: The IP of this device.
INTERNET_PORT      = 9283 #: The default port for netwowrking.
INTERNET_ADDRESS   = (INTERNET_IP, INTERNET_PORT) #: The address of this device.
PACKET_BASIC       = "hB"

inf = math.inf
pi  = math.pi

EMPTY_SCENE = {"": {"type": "Node", "children": {}}}

AXIS_X  = 128225 #: Reference X axis for collision
AXIS_XY = 128226 #: Reference X and Y axis for collision
AXIS_Y  = 128227 #: Reference y axis for collision

MAXFPS = 520 #: Maximum FPS

NEIGHBOUR_TOPLEFT  = 83850
NEIGHBOUR_TOPRIGHT = 83854
NEIGHBOUR_TOPMID   = 83858
NEIGHBOUR_BOTLEFT  = 83860
NEIGHBOUR_BOTRIGHT = 83864
NEIGHBOUR_BOTMID   = 83868
NEIGHBOUR_LEFT     = 83800
NEIGHBOUR_RIGHT    = 83844

RED         = [255, 0,   0,   255]
GREEN       = [0,   255, 0,   255]
BLUE        = [0,   0,   255, 255]
BLACK       = [0,   0,   0,   255]
WHITE       = [255, 255, 255, 255]
TRANSPARENT = [0,   0,   0,     1]