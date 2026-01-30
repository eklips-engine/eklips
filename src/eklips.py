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
    engine.handle_closing()
    engine.display.close_windows()

@main_window.event
def on_draw():
    global _old_delta, _current_delta
    if not engine.running:
        return
    
    try:
        # Calculate delta
        _current_delta = time.time()
        engine.tdelta  = (_current_delta - _old_delta)
        engine.delta   = engine.tdelta * engine.speed
        engine.uptime += engine.tdelta
        _old_delta     = _current_delta

        # Update scene
        engine.scene.update()

        # Check if fullscreen is wanted
        if engine.keyboard.pressed.get(pg.window.key.F11) and engine.game.win.resizable:
            main_window.toggle_fullscreen()
        if engine.keyboard.pressed.get(pg.window.key.F12):
            main_window.screenshot()

        # Clear the list of pressed keys
        engine.keyboard.pressed.clear()
        engine.mouse.scroll = 0
    except Exception as error:
        engine.error_handler.show_error(error)
        engine.quit()

# Start the engine
pg.app.run()