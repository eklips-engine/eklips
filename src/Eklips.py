## Import all the libraries
import pyglet as pg
import ErrorHandler, json, Data, shutil, time, os
import classes.Singleton as engine
from classes.ConHost import printf
from classes.Constants import *

## No initialization code is here. Look at classes/engine.py

## Make Temp dir
os.makedirs("tmp", exist_ok=True)

## Editor values
held_down = -1

## Run the engine
last_dt = time.time()
while (engine.im_running):
    engine.events = []
    try:
        # fill the interface if allowed
        if engine.cvars.get("screen_fillable"):
            try:
                # empty screen if allowed to
                engine.interface.fill(engine.delta)
            except Exception as error:
                ErrorHandler.error  = error
                ErrorHandler.reason = "UI (clearing screen)"
                engine.events.append(PREMATURE_DEATH)
        
        # calculate delta time
        engine.clock.get_delta() # Delta time variables
                                 #  engine.truedelta = can't be manipulated by game speed, good for ui
                                 #  engine.delta     = can

        # get events
        try:
            engine.display.dispatch_events()
            engine.events                                                = engine.event.get_and_handle()
            engine.mpos, engine.mpressed, engine.modifiers, engine.dmpos = engine.event.get_mouse()
            engine.keys_pressed                                          = engine.event.key_once_map
            engine.keys_held_dict                                        = engine.event.key_map
            engine.keys_held                                             = []

        except Exception as error:
            ErrorHandler.error  = error
            ErrorHandler.reason = "Reading User input"
            engine.events.append(PREMATURE_DEATH)

        # add key presses from dictionary to a list that only shows currently pressed keys
        try:
            for i in engine.keys_held_dict:
                if engine.keys_held_dict[i]:
                    engine.keys_held.append(i)
        except Exception as error:
            ErrorHandler.error  = error
            ErrorHandler.reason = "Key parsing"
            engine.events.append(PREMATURE_DEATH)
        
        # handle scene                                                        
        try:
            engine.scene.update(engine.delta)
            if EDITORMODE in engine.flags:
                for nodeid in engine.scene.nodes:
                    node : engine.Scene.CanvasItem = engine.scene.nodes[nodeid]["object"]
                    try:
                        if node.get_if_mouse_hovering() and held_down == -1:
                            held_down = nodeid
                    except:
                        pass
                if engine.mpressed[0]:
                    if held_down != -1:
                        node : engine.Scene.CanvasItem = engine.scene.nodes[held_down]["object"]
                        if CAN_DESTROY_NODES in engine.flags:
                            node.free()
                        if CAN_GRAB_NODES in engine.flags:
                            node.x += engine.dmpos[0]
                            node.y -= engine.dmpos[1]
                else:
                    held_down = -1
        except (BaseException, Exception) as error:
            ErrorHandler.error  = error     
            ErrorHandler.reason = f"Scene {engine.scene.file_path}"
            engine.events.append(PREMATURE_DEATH)  
        
        # handle events (most of them)                                                    
        if SOFT_QUIT in engine.events:
            engine.suicide()
            engine.savefile.save_data()
            break
        
        # handle console                                                                  
        if engine.is_key_pressed("eng_cheats"):
            engine.console.toggle()

        # flip the screen
        try:
            if engine.savefile.get("display/showfps", True) or engine.cvars.get("showfps", False):
                engine.fps_display.draw()
            engine.console.update(engine.keys_pressed, engine.keys_held, globals(), engine.modifiers)
            engine.interface.flip()
        except Exception as error:
            ErrorHandler.error  = error
            ErrorHandler.reason = "UI (updating window)"
            engine.events.append(PREMATURE_DEATH)

        engine.event.key_once_map = []
    except Exception as error:
        ErrorHandler.error  = error
        ErrorHandler.reason = "Engine, probably"
        engine.events.append(PREMATURE_DEATH)
    
    # handle crashes
    if PREMATURE_DEATH in engine.events:
        ErrorHandler.raise_error(ErrorHandler.error, ErrorHandler.reason, "bad coding skillz")
        engine.suicide()
        break

## Temp folder removal
shutil.rmtree("tmp", ignore_errors = True)
if "tmp" in os.listdir():
    shutil.rmtree("tmp", ignore_errors = True)
engine.scene.empty()