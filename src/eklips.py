# Import libraries
import pyglet as pg, time

# Import components
from classes.locals      import *
from classes.customprops import *
import classes.singleton as engine

# Load the engine components
engine.load_engine()
main_window = engine.display.get_window()

# Create event loop
@main_window.event
def on_close():
    engine.handle_closing()
    engine.display.close_windows()

def update(dt):
    # Stop right there criminal scum
    if not engine.running:
        return
    
    try:
        # Calculate FPS
        engine.fps    = 1 / dt
        if engine.fps  < ZDE_FIX:
            engine.fps = ZDE_FIX
        
        # Calculate delta
        engine.tdelta = dt
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
        engine.error_handler.show_error(error)
        engine.quit()

# Start the engine
pg.clock.schedule_interval(update, 1/MAXFPS)
pg.app.run(1 / MAXFPS)