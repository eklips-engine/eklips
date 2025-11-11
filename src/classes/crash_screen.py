# Import libraries
import traceback as tb
from tkinter.messagebox import *

# Variables
background_color = "#14141E"
foreground_color = "#EBEBE1"

# Functions
def get_info(error : Exception):
    return "".join(tb.format_exception(error))

def show_error(error : Exception):
    info = get_info(error)
    showerror("Eklips Engine", f"Eklips has crashed with the traceback:\n\n{info}")