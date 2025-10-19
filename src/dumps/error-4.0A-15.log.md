Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: Exception
    Error: what the fuck
    
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
    | Filename: D:\src\classes\node\gui\button.py
    | Line: super().update(delta)
    | Line #: 39
    
    FrameSummary #5:
    | Filename: D:\src\classes\node\gui\canvasitem.py
    | Line: self.call("_hover")
    | Line #: 122
    
    FrameSummary #6:
    | Filename: D:\src\classes\Object.py
    | Line: return mobj()
    | Line #: 56
    
    FrameSummary #7:
    | Filename: <string>
    | Line: 
    | Line #: 61
    
    FrameSummary #8:
    | Filename: D:\src\classes\Convenience.py
    | Line: raise Exception("what the fuck")
    | Line #: 92
    

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!