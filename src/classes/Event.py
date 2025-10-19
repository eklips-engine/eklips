## Import all the libraries
import pyglet as pg
import classes.Singleton as engine
from classes.Constants import *

## Event class
class Event:
    def __init__(self):
        self.dmpos         = [0,0]
        self.screen        = engine.display
        self.key_map       = {}
        self.key_once_map  = []
        self.events        = []
        self.screen.push_handlers(self)
        self.modifiers     = None
        self.mouse_pos     = [0, 0]
        self.mouse_buttons = [0, 0, 0]  # Left, Middle, Right
        self.mouse_scroll  = 0
    
    def on_close(self):
        self.events.append(('quit', None))
    
    # Keyboard
    def on_key_press(self,symbol, modifiers):
        self.events.append(('keydown', symbol, modifiers))
        if symbol == pg.window.key.ESCAPE: # Stop the app from closing
            return pg.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        self.events.append(('keyup', symbol, modifiers))
    
    # Savefile
    def on_saved(self, successfully):
        self.events.append(('save', successfully))
    
    # Mouse
    def on_mouse_motion(self, x, y, dx, dy):
        self.events.append(('mousemotion', [x,y],[dx,dy]))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.events.append(('mousemotion', [x,y],[dx,dy]))

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1: self.mouse_buttons[0] = 1
        if button == 2: self.mouse_buttons[1] = 1
        if button == 4: self.mouse_buttons[2] = 1
        self.events.append(('mouse', True))

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1: self.mouse_buttons[0] = 0
        if button == 2: self.mouse_buttons[1] = 0
        if button == 4: self.mouse_buttons[2] = 0
        self.events.append(('mouse', False))
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.events.append(('scroll', scroll_y, scroll_x))
    
    # Etc
    def on_abnormal_time(self, gap):
        self.events.append(('abnormal', gap))
    
    def get(self):
        # Return and clear the queue
        events_copy = self.events[:]
        self.events.clear()
        return events_copy

    def get_and_handle(self):
        ## Events:
        # 0 - quit. 1 - keydown. 2 - keyup.
        events = self.get()
        code = []
        self.dmpos        = [0,0]
        self.mouse_scroll = 0
        self.modifiers    = None
        for i in events:
            if i[0] == 'quit':
                code.append(SOFT_QUIT)
            elif i[0] == 'keydown':
                code.append(KEYDOWN)
                self.key_map[i[1]] = 1
                self.modifiers     = i[2]
                self.key_once_map.append(i[1])
            elif i[0] == 'keyup':
                code.append(KEYUP)
                self.modifiers     = i[2]
                try:
                    self.key_map.pop(i[1])
                except:
                    self.key_map[i[1]] = 0
            elif i[0] == 'mousemotion':
                self.mouse_pos = i[1]
                self.dmpos     = i[2]
            elif i[0] == 'scroll':
                self.mouse_scroll = i[1]
            elif i[0] == 'save':
                code.append(SAVE_EVENT)
                if i[1]:
                    code.append(SAVE_SUCESS)
                else:
                    code.append(SAVE_FAILED)
            elif i[0] == 'abnormal':
                code.append(ABNORMAL_TIME)
            elif i[0] == 'mouse':
                if i[1]:
                    code.append(MOUSEDOWN)
                else:
                    code.append(MOUSEUP)
        return code

    def get_mouse(self):
        return [self.mouse_pos[0],self.screen.get_size()[1]-self.mouse_pos[1]], list(self.mouse_buttons), self.modifiers, self.dmpos