import pyglet as pg, socket as sock, math

USE_GAME_PARENT = "UseFileParent"
USE_GAME_CV_DIR = "UseFileCVar"

NAME         = "Eklips Engine"
BDATE        = [20, 1, 2026]  # DMY
MAJOR        = "5"            # Major [5].0 A 
MINOR        = "0"            # Minor  5.[0]A 
HOTFIX       = "A"            # Hotfix 5. 0[A]
VERSION      = f"{MAJOR}.{MINOR}{HOTFIX}"
VERSION_FULL = f"v{VERSION} ({BDATE[0]}/{BDATE[1]}/{BDATE[2]})"
print(f"{NAME} {VERSION_FULL}")

AUTOMATICALLY_CREATE = 1
DETECT               = 2

MAIN_WINDOW           = 0
MAIN_BATCH            = 0
MAIN_VIEWPORT         = 0
UI_VIEWPORT           = 1
DEFAULT_NAME          = "Window"
VIEWPORT_EQUAL_WINDOW = 8346
NO_CLEAR_BACKGROUND   = 641
NO_CLEAR              = 215
DEFAULT_FONT_SIZE     = 12.5
DEFAULT_FONT_NAME     = "Arial"

USE_SCENE_TREE = 4

ZDE_FIX = 0.00000001

ERROR_ICON = "_assets/error.png"
EKL_ICON   = "_assets/icon.png"

MOUSE_LEFT    = 1
MOUSE_MIDDLE  = 2
MOUSE_RIGHT   = 4
MOUSE_BUTTONS = [MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT]

MOUSE_POINT   = pg.window.Window.CURSOR_HAND
MOUSE_HELP    = pg.window.Window.CURSOR_HELP
MOUSE_CROSS   = pg.window.Window.CURSOR_CROSSHAIR
MOUSE_NO      = pg.window.Window.CURSOR_NO
MOUSE_WAIT    = pg.window.Window.CURSOR_WAIT
MOUSE_NORMAL  = pg.window.Window.CURSOR_DEFAULT
CURSORS       = [MOUSE_POINT, MOUSE_HELP, MOUSE_CROSS, MOUSE_NO, MOUSE_WAIT, MOUSE_NORMAL]

INTERNET_ABORTED   = 253132
INTERNET_CONNECTED = 253133
INTERNET_SERVER    = 253123
INTERNET_CLIENT    = 253122
INTERNET_IP        = sock.gethostname()
INTERNET_PORT      = 9283
INTERNET_ADDRESS   = (INTERNET_IP, INTERNET_PORT)
PACKET_BASIC       = "hB"

inf = math.inf
pi  = math.pi