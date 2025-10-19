Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: TypeError
    Error: can only concatenate tuple (not "float") to tuple
    
    FrameSummary #1:
    | Filename: D:\src\Eklips.py
    | Line: engine.scene.update(engine.delta)
    | Line #: 58
    
    FrameSummary #2:
    | Filename: D:\src\classes\Scene.py
    | Line: raise error
    | Line #: 148
    
    FrameSummary #3:
    | Filename: D:\src\classes\Scene.py
    | Line: node.update(delta)
    | Line #: 145
    
    FrameSummary #4:
    | Filename: D:\src\classes\node\gui\label.py
    | Line: super().update(delta)
    | Line #: 59
    
    FrameSummary #5:
    | Filename: D:\src\classes\node\gui\canvasitem.py
    | Line: if self.get_if_mouse_hovering():
    | Line #: 121
    
    FrameSummary #6:
    | Filename: D:\src\classes\node\gui\canvasitem.py
    | Line: mpos[0] < x + self.w and
    | Line #: 96
    

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!