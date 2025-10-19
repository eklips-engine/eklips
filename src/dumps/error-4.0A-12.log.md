Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: TypeError
    Error: type tuple doesn't define __round__ method
    
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
    | Line: x,y  = self.screen.get_anchor(
    | Line #: 86
    
    FrameSummary #7:
    | Filename: D:\src\classes\UI.py
    | Line: new_pos=[round(new_pos[0]),round(new_pos[1])]
    | Line #: 71
    

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!