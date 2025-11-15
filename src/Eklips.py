# Import libraries
import pygame, pyglet as pg, time

# Import components
from classes.locals      import *
from classes.customprops import *
import classes.singleton as engine

# Variables
_old_delta     = time.time()
_current_delta = None
main_window    = engine.display.get_window()

# Create event loop
@main_window.event
def on_close():
    engine.running = False
    engine.display.close_windows(forced=True)
    engine.handle_closing()

@main_window.event
def on_draw():
    global _old_delta, _current_delta
    try:
        # Clear and dispatch self
        engine.display.clear_window()
        
        # Calculate delta
        _current_delta = time.time()
        engine.delta   = _current_delta - _old_delta
        engine.uptime += engine.delta
        _old_delta     = _current_delta

        # Update scene
        engine.scene.update()
        
        # Flip window
        engine.display.flip_window()

        # Clear the list of pressed keys
        engine.keyboard.pressed.clear()
    except Exception as error:
        engine.error_handler.show_error(error)
        engine.running = False
        engine.handle_closing()
        
        # This will close the app by crashing it lul. Atleast we save beforehand.
        # Why? Because i dunno how to close a window in this kind of event loop
        # without begging the user to with a picture of a cute golden retriever.
        #
        # What? No, i'm not like Cyn- oh, shut up.
        main_window.close()

# Start the engine
pg.app.run()