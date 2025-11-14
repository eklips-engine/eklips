# Import libraries
import traceback as tb, os
from tkinter.messagebox import *

# Functions
def get_info(error : Exception):
    return "".join(tb.format_exception(error))

def show_error(error : Exception):
    info = get_info(error)
    if askyesno("Eklips Engine", f"Eklips has crashed with the traceback:\n\n{info}\n\nWould you like a dump to be saved?"):
        os.makedirs("tmp", exist_ok=True)
        with open(f"tmps/{len(os.listdir('tmps'))}.log","w") as f:
            f.write(info)