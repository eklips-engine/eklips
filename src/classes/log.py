import classes.singleton as engine
from classes.customprops import *

def info(text):
    """Log some text as info."""
    print(f"INFO: {text}")
def warn(text):
    """Log some text as a warning."""
    print(f"WARN: {text}")
def error(text):
    """Log some text as an error and display it on a dialog."""
    print(f"ERROR: {text}")
    engine.error_handler.report_erroror(LogError(text))