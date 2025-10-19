from tkinter.messagebox import *
import traceback, os, webbrowser, requests
from classes.Constants import *

class Preview(Exception): #Preview Error Class
    def __none__(self): return None

error  = None
reason = None

def get_info(error, running, save_logs):
    global VER
    try:
        os.mkdir("dumps")
    except:
        pass

    fn = f"dumps/error-{VER}-{len(os.listdir('dumps'))+1}.log.md"
    quick_fix = "N/A (Not Available)"
    if error:
        try:
            error_obj=traceback.TracebackException.from_exception(error)
            error_info=f"Error Type: {error_obj.exc_type_str}\nError: {error_obj}\n"
        
            fsid=1
            for i in error_obj.stack:
                error_info+=f"""
FrameSummary #{fsid}:
| Filename: {i.filename}
| Line: {i.line}
| Line #: {i.lineno}"""
                fsid+=1
        
            try:
                error_info+=f"""
SyntaxError related:
| Filename: {error_obj.filename}
| Message: {error_obj.msg}
| Offset: {error_obj.offset}
| EndOffset: {error_obj.end_offset}
| Text: {error_obj.text}
| Line#: {error_obj.lineno}
| End Line#: {error_obj.end_lineno}"""
            except:
                pass
        
            quick_fix = "N/A (Not Available)"
            if error_obj.exc_type_str == "Preview" or len(" ".join(error_info.split())) == 0:
                quick_fix = f"The {ENGINE_NAME} Error handler recieved no data, so you got this error."
            elif (error_obj.exc_type_str == "pygame.error" and error_obj == "Out of memory") or error_obj.exc_type_str == "MemoryError":
                quick_fix = f"{ENGINE_NAME} ran out of memory! Try giving the app more memory to work with."
            elif error_obj.exc_type_str in ["ImportError", "ModuleNotFoundError"]:
                quick_fix = f"Core {ENGINE_NAME} Modules were removed/not found, try reinstalling them through {ENGINE_NAME}'{'' if ENGINE_NAME.endswith('s') else 's'} github repo."
            elif error_obj.exc_type_str == "KeyboardInterrupt":
                quick_fix = "You pressed Ctrl+C. Don't do that next time okay?"
            else:
                quick_fix  = "N/A (Not Available)"
        except:
            quick_fix  = "N/A (Not Available)"
            error_info = f"The Traceback data could not be found. Attached value: {error}"
            error_obj  = None
            return error_info, quick_fix, error_obj

    if save_logs:
        with open(fn, "w") as f:
            f.write(f"Oops! {ENGINE_NAME} just crashed;\nHere's this crash log!\n\n")
            f.write(f"Quick Fix for users: {quick_fix}\nCause of error: {running}\n\n")
            f.write(error_info)
            f.write(f"\n\nPlease send this file to the developers of {ENGINE_NAME} at https://github.com/Za9-118/Eklips/issues. \nYour feedback is important!")
    
    return error_info, quick_fix, error_obj

def raise_error(error, event="unknown", cause_of_event=None, save_logs=True):
    error_info, quick_fix, error_obj = get_info(error, running=cause_of_event, save_logs=save_logs)
    showerror(
        f"{ENGINE_NAME}",
        f"{ENGINE_NAME} has crashed!\n\n{error_info}\n\nFix (if available): {quick_fix}\nAlleged suspect: {event}\nCause of suspicion: {cause_of_event}"
    )

if __name__ == "__main__":
    raise_error(Preview("Preview"), event="User", cause_of_event="You opened ErrorHandler.py", save_logs=False)