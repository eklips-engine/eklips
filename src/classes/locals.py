USE_GAME_PARENT = "UseFileParent"
USE_GAME_CV_DIR = "UseFileCVar"

BDATE   = [14, 11, 2025] # DMY
MAJOR   = "4"           # Major [4].1 A 
MINOR   = "1"           # Minor  4.[1]A 
HOTFIX  = "A"           # Hotfix 4. 1[A]
VERSION = f"{MAJOR}.{MINOR}{HOTFIX}"
print(f"Eklips Engine v{VERSION} ({BDATE[0]}/{BDATE[1]}/{BDATE[2]})")

MAIN_WINDOW   = 0
MAIN_BATCH    = 0
MAIN_VIEWPORT = 0

DEFAULT_NAME = "Window"

VIEWPORT_EQUAL_WINDOW = 10

ZDE_FIX = 0.00000001

ERROR_ICON = "_assets/error.png"
EKL_ICON   = "_assets/icon.png"

MOUSE_LEFT    = 1
MOUSE_MIDDLE  = 2
MOUSE_RIGHT   = 3
MOUSE_BUTTONS = [MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT]

DEFAULT_FONT_SIZE = 14