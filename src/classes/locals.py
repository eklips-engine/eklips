import pyglet as pg, socket as sock, math
from typing import *

USE_GAME_PARENT = "UseFileParent"
USE_GAME_CV_DIR = "UseFileCVar"

NAME         = "Eklips Engine"
BDATE        = [6, 3, 2026]  # DMY
MAJOR        = "5"           # Major [5].0 A 
MINOR        = "0"           # Minor  5.[0]A 
HOTFIX       = "A"           # Hotfix 5. 0[A]
BUILD        = 25            # Increment every time a major feature has been added
VERSION      = f"{MAJOR}.{MINOR}{HOTFIX}"
VERSION_FULL = f"v{VERSION} ({BDATE[0]}/{BDATE[1]}/{BDATE[2]})"
print(f"{NAME} {VERSION_FULL}")

AUTOMATICALLY_CREATE = 50152971
DETECT               = 50152972

MAIN_WINDOW           = 0
MAIN_BATCH            = 0
MAIN_VIEWPORT         = 0
UI_VIEWPORT           = 1
DEFAULT_NAME          = "Window" # Don't listen to whoever wrote that rant they're just stupid. Who would even leave window.switch_to and close a viewport on a random context and be mad that it didnt work. Stupid. Wait, im the only one that's working on this repository-
VIEWPORT_EQUAL_WINDOW = 50151
NO_CLEAR_BACKGROUND   = 50152
NO_CLEAR              = 50153
DEFAULT_FONT_SIZE     = 12.5
DEFAULT_FONT_NAME     = "Arial"

USE_SCENE_TREE = 5474

ZDE_FIX = 0.00000001

ERROR_ICON = "_assets/error.png"
EKL_ICON   = "_assets/icon.png"

MOUSE_LEFT    = 1
MOUSE_MIDDLE  = 2
MOUSE_RIGHT   = 4
MOUSE_BUTTONS = [MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT]

MOUSE_POINT     = pg.window.Window.CURSOR_HAND
MOUSE_HELP      = pg.window.Window.CURSOR_HELP
MOUSE_CROSS     = pg.window.Window.CURSOR_CROSSHAIR
MOUSE_NO        = pg.window.Window.CURSOR_NO
MOUSE_WAIT      = pg.window.Window.CURSOR_WAIT
MOUSE_DRAGGABLE = "root://_assets/grab.cur"
MOUSE_DRAG      = "root://_assets/grabbing.cur"
MOUSE_NORMAL    = pg.window.Window.CURSOR_DEFAULT
CURSORS         = [MOUSE_POINT, MOUSE_HELP, MOUSE_CROSS, MOUSE_NO, MOUSE_WAIT, MOUSE_NORMAL, MOUSE_DRAG, MOUSE_DRAGGABLE]

INTERNET_ABORTED   = 253132
INTERNET_CONNECTED = 253133
INTERNET_SERVER    = 253123
INTERNET_CLIENT    = 253122
INTERNET_IP        = sock.gethostbyname(sock.gethostname())
INTERNET_PORT      = 9283
INTERNET_ADDRESS   = (INTERNET_IP, INTERNET_PORT)
PACKET_BASIC       = "hB"

inf = math.inf
pi  = math.pi

ITEM_INDEX  = 0
ITEM_AVAIL  = 1
ITEM_BATCH  = 2
ITEM_KIND   = 3
ITEM_MASTER = 4
ITEM_SPRITE = 657
ITEM_LABEL  = 656
ITEMKIND : TypeAlias = Literal[657, 656]

EMPTY_SCENE = {"": {"type": "Node", "children": {}}}

AXIS_X  = 128225
AXIS_XY = 128226
AXIS_Y  = 128227

MAXFPS = 60