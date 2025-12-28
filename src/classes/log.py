import classes.singleton as engine

class LogError(BaseException):
    """Class for `error()`"""

def info(text):
    print(f"INFO: {text}")
def warn(text):
    print(f"WARN: {text}")
def error(text):
    print(f"ERROR: {text}")
    engine.error_handler.show_error(LogError(text))