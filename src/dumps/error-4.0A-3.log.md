Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: UnboundLocalError
    Error: cannot access local variable 'rotation' where it is not associated with a value
    
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
    | Filename: D:\src\classes\node\twod\sprite2d.py
    | Line: super().update(delta)
    | Line #: 44
    
    FrameSummary #5:
    | Filename: D:\src\classes\node\twod\node2d.py
    | Line: super().update(delta)
    | Line #: 28
    
    FrameSummary #6:
    | Filename: D:\src\classes\node\gui\canvasitem.py
    | Line: super().update(delta)
    | Line #: 126
    
    FrameSummary #7:
    | Filename: D:\src\classes\node\node.py
    | Line: self._process(delta)
    | Line #: 46
    
    FrameSummary #8:
    | Filename: D:\src\classes\Object.py
    | Line: self.call("_process", delta)
    | Line #: 81
    
    FrameSummary #9:
    | Filename: D:\src\classes\Object.py
    | Line: return mobj(*args)
    | Line #: 58
    
    FrameSummary #10:
    | Filename: <string>
    | Line: 
    | Line #: 5
    

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!