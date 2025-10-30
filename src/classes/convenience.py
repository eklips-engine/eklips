## I feel like YandereDev rn
def strtotype(text):
    """Turn a text input into a type at first glance."""
    try:
        return float(text)
    except ValueError:
        try:
            return int(text)
        except:
            if text.lower() in ["true", "yes", "1", "1.0","y","t","affirmative","ofcourse", "yay", "sure", "ok", "okay"]:
                return True
            elif text.lower() in ["false", "no", "0", "0.0", "none", "nan", "n", "nay", "nope", "nah", "negative"]:
                return False
            else:
                return text

def boollike_to_word(obj):
    if obj:
        return "Yes"
    return "No"

def shift_key(key):
    nk = key.upper()
    if nk == "1": nk = "!"
    if nk == "2": nk = "@"
    if nk == "3": nk = "#"
    if nk == "4": nk = "$"
    if nk == "5": nk = "%"
    if nk == "6": nk = "^"
    if nk == "7": nk = "&"
    if nk == "8": nk = "*"
    if nk == "9": nk = "("
    if nk == "0": nk = ")"
    if nk == "-": nk = "_"
    if nk == "=": nk = "+"
    if nk == "/": nk = "?"
    if nk == "\\": nk = "|"
    if nk == "]": nk = "}"
    if nk == "[": nk = "{"
    if nk == "'": nk = "\""
    if nk == ".": nk = ">"
    if nk == ",": nk = "<"
    if nk == "`": nk = "~"
    if nk == ";": nk = ":"
    return nk

class Transform:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._w = 0
        self._h = 0

        self.layer    = 0
        self.rotation = 0
        self.alpha    = 1
        self.anchor   = "top left"
        self.scroll   = [0,0]
        self.visible  = True
        
        self._scale_x = 0
        self._scale_y = 0

    # Getters
    @property
    def x(self): return self._x
    @property
    def y(self): return self._y

    @property
    def scale_x(self): return self._scale_x
    @property
    def scale_y(self): return self._scale_y
    @property
    def scale(self):   return [self._scale_x, self._scale_y]
    
    @property
    def w(self): return self._w * self._scale_y
    @property
    def h(self): return self._h * self._scale_y
    
    @property
    def rect(self): return [self._x,self._y,self._w*self._scale_y,self._h*self._scale_y]
    @property
    def pos(self):  return [self._x,self._y]
    
    # Setters
    @x.setter
    def x(self, value): self._x = value
    @y.setter
    def y(self, value): self._y = value

    @scale_x.setter
    def scale_x(self, value):
        self._scale_x = value
    @scale_y.setter
    def scale_y(self, value):
        self._scale_y = value
    @scale.setter
    def scale(self, value):
        self._scale_x, self._scale_y = value
    
    @w.setter
    def w(self, value): self._w = value
    @h.setter
    def h(self, value): self._h = value
    
    @rect.setter
    def rect(self, value):
        self._x,self._y,self._w,self._h = value