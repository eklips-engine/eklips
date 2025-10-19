## Import all the libraries
import pyglet as pg
from classes import UI, CV, Convenience
from classes.KeyEntries import key_entries
from classes.Constants import *
import classes.Singleton as engine

shared_console_text            = []
shared_console_history         = []
shared_console_history_pointer = 0
def printf(*args):
    args_str = []
    for i in args:
        args_str.append(str(i))
    arg=" ".join(args_str)
    print(arg)
    shared_console_text.append(arg)

class ConHost:
    """ConHost class. Used to handle console output and input."""

    def __init__(self):
        global shared_console_text
        self.cvars        = engine.cvars
        self.data         = engine.Data
        self.console_text = shared_console_text
        self.shown        = False
        self.ui           = engine.interface
        self.input_text   = ""
        self.h            = "df"
        self.w            = self.ui.screen.width
        self.y            = None
        self.showing      = False
        self.hiding       = False
        self.blink_timer  = 0
        self.eng_gl       = {}
        self.is_upper     = False
        self.hold_timer   = 0
        self.hold_timer_t = 0
        self.cmd_historyp = shared_console_history_pointer
        self.cmd_history  = shared_console_history
        self.klp          = None
        self.curpos       = 0
        self.speed        = self.cvars.get("con_speed")
        self.bl_rate      = self.cvars.get("con_rate")
        self.shifted      = False
        self.ll           = (len(self.ui.layers)//2)-1
        self.contxtbatch  = pg.graphics.Batch()
        self.mk_panel()
    
    def mk_panel(self):
        self.h     = self.cvars.get("con_size", "df")
        if self.h == "df":
            self.h = self.ui.screen.height // 2
        if self.y == None:
            self.y = -self.h
        self.con_panel    = pg.shapes.Rectangle(
            x=0,
            y=self.y,
            width=self.w,
            height=self.h,
            color=(0,0,0,197),
            group=self.ui.layers[self.ll-1],
            batch=self.ui.batch
        )
    
    def toggle(self):
        """Toggle the console visibility."""
        self.speed   = self.cvars.get("con_speed")
        self.bl_rate = self.cvars.get("con_rate")
        if self.cvars.get("con_size", self.con_panel.width) != self.con_panel.width:
            self.mk_panel()
        
        self.con_panel.visible = True

        if not (self.showing or self.hiding):
            self.shown = not self.shown

            if self.shown:
                self.show()
            else:
                self.hide()
    
    def show(self):
        """Show the console."""
        self.showing = True
    
    def hide(self):
        """Hide the console."""
        self.hiding  = True
    
    def update(self, keys_pressed, keys_held, eng_gl, modifiers):
        self.eng_gl = eng_gl
        """Update the console."""
        if self.showing:
            if self.y < 0:
                self.y += self.ui.delta * self.speed
            else:
                self.showing = False
        elif self.hiding:
            if self.y > -self.h:
                self.y -= self.ui.delta * self.speed
            else:
                self.hiding = False
                self.con_panel.visible = False
        
        if self.y > 0:
            self.y = 0
        elif self.y < -self.h:
            self.y = -self.h
        
        if self.y > -self.h:
            self.con_panel.y = self.ui.screen.get_size()[1] - self.h - self.y
            self.con_panel.draw()
            
            amchirncon=(self.h//25)-1
            if len(self.console_text) > amchirncon:
                for i in range(int(len(self.console_text)-amchirncon)):
                    self.console_text.pop(0)
        
            con_y = self.y
            for i in self.console_text:
                self.ui.render(
                    i,
                    [10,con_y],
                    "main",
                    self.ll,
                    "",
                    batchxt=self.contxtbatch
                )
                con_y += 25
            
            blk_g = " "
            if self.blink_timer > 1:
                blk_g = "_"
            if self.blink_timer > 2:
                self.blink_timer = 0
            self.blink_timer += engine.delta * self.bl_rate

            if self.hold_timer > 0.5 and self.klp and self.klp in keys_held:
                self.hold_timer_t += engine.delta
                if self.hold_timer_t > engine.delta * 450:
                    self._prockey(self.klp, modifiers)
            
            if len(keys_pressed) > 0:
                for char in keys_pressed:
                    if char == pg.window.key.RETURN:    # Enter
                        self.input(self.input_text)
                    self._prockey(char, modifiers)
                    self.hold_timer = 0
            
            if len(keys_held) == 0:
                self.hold_timer = 0
            
            self.hold_timer += engine.delta

            self.ui.render(f"] {self.input_text}{blk_g}", [10,self.y+self.h-35], "main", self.ll, batchxt=self.contxtbatch)
    
    def _prockey(self, key, modifier=None):
        """Process a key input."""
        shifted = False
        if key == pg.window.key.CAPSLOCK:
            self.is_upper = not self.is_upper
        if modifier == pg.window.key.MOD_SHIFT:
            shifted = True
        
        if key == pg.window.key.BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif key == pg.window.key.RETURN:
            self.input(self.input_text)
            self.cmd_historyp = 0
        elif key == pg.window.key.UP:
            self.cmd_historyp += 1
            try:
                self.input_text = self.cmd_history[-self.cmd_historyp]
            except:
                self.cmd_historyp -= 1
        elif key == pg.window.key.DOWN:
            self.cmd_historyp -= 1
            try:
                self.input_text = self.cmd_history[-self.cmd_historyp]
            except:
                self.cmd_historyp += 1
        elif key in key_entries:
            self.input_text += key_entries[key]
        else:
            nk = "?"
            if shifted: # or self.is_upper:
                nk = Convenience.shift_key(chr(key)) if 0 <= key < 256 else ""
            elif self.is_upper:
                nk = chr(key).upper() if 0 <= key < 256 else ""
            else:
                nk = chr(key) if 0 <= key < 256 else ""
            self.input_text += nk
        self.klp = key
    
    def list_cvar(self, name):
        """List a cvar's data."""
        data = self.cvars.get(name, "Undefined")
        desc = self.cvars.get_description(name, "No description")
        printf(f"{name} = {data} :: {desc}")
    
    def _proccmd(self, text):
        """Process a command input."""
        data         = text.split(" ")
        if len(data) < 1:
            return
        opc          = data[0].lower()
        try: args    = data[1:]
        except: args = [None]
        if opc.startswith("sv_"):
            cvar = opc.removeprefix("sv_")
            if cvar == "list":
                for cvar_name in self.cvars.cvars:
                    self.list_cvar(cvar_name)
            else:
                if len(args) > 0:
                    self.cvars.set(cvar, Convenience.strtotype(args[0]))
                self.list_cvar(cvar)
        elif opc == "eng_chproj":
            exec(f"engine.Data.project_file = '{args[0]}/game.json'", self.eng_gl, self.eng_gl)
            exec(f"engine.Data.directory = '{args[0]}'", self.eng_gl, self.eng_gl)
            exec(f"engine.reload_engine('{args[0]}')", self.eng_gl, self.eng_gl)
        else:
            try:
                g           = self.eng_gl.copy()
                g["args"]   = args
                g["engine"] = engine
                pline       = self.data.game_bdata["cmd"][opc].splitlines()[0]
                if pline.startswith("@pointer="):
                    pointer_file = pline[9:]
                    exec(engine.resource_loader.load(pointer_file).get(), g,g)
                else:
                    exec(self.data.game_bdata["cmd"][opc], g,g)
            except Exception as error:
                if opc in self.data.game_bdata["cmd"]:
                    printf(f"Command error: {error}")
                else:
                    printf(f"Illegal command: {opc}")
    
    def input(self, text):
        """Input text to the console."""
        if text:
            printf(f"] {text}")
            self.input_text = ""
            self.curpos     = 0
            self.klp        = None
            self.hold_timer = 0
            self.cmd_history.append(text)
            try:
                for i in text.split("&&"):
                    self._proccmd(i.strip())
            except Exception as error:
                printf(f"Error processing command '{text}': {error}")
                raise error