# Import libraries
import traceback as tb, os
from tkinter.messagebox import *

# Functions
def get_info(error : Exception):
    return "".join(tb.format_exception(error))

def show_error(error : Exception):
    info = get_info(error)
    if askyesno(
        "Eklips Engine", 
        f"""Eklips has crashed with the traceback:

{info}

Would you like a dump to be saved?
        """
    ):
        os.makedirs("tmp", exist_ok=True)
        with open(f"tmp/{len(os.listdir('tmp'))}.log","w") as f:
            f.write(info)