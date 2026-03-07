# Import libraries
import pyglet as pg, time

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
        engine.debug.start_timer("Delta")
        _current_delta = time.time()
        engine.delta   = engine.speed * engine.tdelta
        engine.uptime += engine.tdelta
        _old_delta     = _current_delta
        engine.debug.end_timer("Delta")
        
        # Update scene
        engine.debug.start_timer("Scn")
        engine.scene.update()
        engine.debug.end_timer("Scn")

        # Check if fullscreen is wanted
        if engine.keyboard.pressed.get(pg.window.key.F11) and engine.game.win.resizable:
            engine.debug.start_timer("FS")
            main_window.toggle_fullscreen()
            engine.debug.end_timer("FS")
        if engine.keyboard.pressed.get(pg.window.key.F12):
            engine.debug.start_timer("Screenie")
            main_window.screenshot()
            engine.debug.end_timer("Screenie")

        # Clear the list of temporary actions
        engine.keyboard.pressed.clear()
        engine.mouse.scroll       = 0
        engine.mouse.dragging     = False
        engine.mouse.dpos         = [0,0]
        engine.mouse.just_clicked = [0,0,0,0,0]
    except Exception as error:
        engine.error_handler.show_error(error)
        engine.quit()
    main_window.invalid = True

# Start the engine
pg.app.run(1 / MAXFPS)