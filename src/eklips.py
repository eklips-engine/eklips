## Import libraries
import pyglet as pg, time

## Import components
from classes.locals      import *
from classes.customprops import *
import classes.singleton as engine

## Load the engine components
engine.load_engine()
main_window = engine.display.get_window()

## Create event loop
@main_window.event
def on_close():
    engine.handle_closing()

@main_window.event
def on_draw():
    # Stop if not running
    if not engine.running:
        return
    
    try:
        # Calculate sped up delta
        engine.delta   = engine.speed * engine.tdelta
        engine.uptime += engine.tdelta
        
        # Update scene
        engine.scene.update()

        # Check if fullscreen is wanted
        if engine.keyboard.pressed.get(pg.window.key.F11) and engine.game.win.resizable:
            main_window.toggle_fullscreen()
        if engine.keyboard.pressed.get(pg.window.key.F12):
            main_window.screenshot()

        # Clear the list of temporary actions
        engine.keyboard.pressed.clear()
        engine.mouse.scroll       = 0
        engine.mouse.dragging     = False
        engine.mouse.dpos         = [0,0]
        engine.mouse.just_clicked = MOUSE_DEFAULT_STATE.copy()
        engine.keyboard.text      = ""
        engine.keyboard.motion    = None
    except Exception as error:
        engine.error_handler.report_error(error)
        engine.quit(1)

## Start the engine
interval     = 1/MAXFPS
if interval == 0:
    interval = ZDE_FIX
pg.app.run(interval)