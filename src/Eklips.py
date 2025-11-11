# Import libraries
import pygame, pyglet as pg, time

# Import components
from classes.locals      import *
from classes.customprops import *
import classes.singleton as engine

# Variables
_old_delta     = time.time()
_current_delta = None

# Game loop
while engine.running:
    try:
        # Clear and dispatch windows
        engine.display.clear_windows()
        engine.display.dispatch_events()

        # Calculate delta
        _current_delta = time.time()
        engine.delta   = _current_delta - _old_delta
        engine.uptime += engine.delta
        _old_delta     = _current_delta

        # Update scene
        engine.scene.update()
        
        # Flip windows
        engine.display.flip_windows()

        # Close if there is no Main Window
        if engine.display.main_window_id == None:
            engine.running = False
    except Exception as error:
        engine.error_handler.show_error(error)
        engine.running = False
        engine.display.close_windows()