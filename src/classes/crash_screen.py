## Import libraries
import traceback as tb, os
import classes.singleton as engine
from tkinter.messagebox import *

## Functions
def get_info(error : Exception):
    return " - ".join(tb.format_exception(error))

def report_error(error : Exception):
    if engine.savefile:
        engine.savefile.save_data()
    
    info = get_info(error)
    print(f"""Crashed with info:
 - {info}""")
    os.makedirs("tmp", exist_ok=True)
    with open(f"tmp/{len(os.listdir('tmp'))}.log","w") as f:
        f.write(info)
    
    showerror("Eklips Engine", info)

__dict__ = {"report_error": report_error, "get_info": get_info, "traceback": tb, "os": os}