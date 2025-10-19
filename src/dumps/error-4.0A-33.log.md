Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: TypeError
Error: _process() takes 1 positional argument but 2 were given

FrameSummary #1:
| Filename: D:\src\Eklips.py
| Line: engine.scene.update(engine.delta)
| Line #: 62
FrameSummary #2:
| Filename: D:\src\classes\Scene.py
| Line: raise error
| Line #: 151
FrameSummary #3:
| Filename: D:\src\classes\Scene.py
| Line: node.update(delta)
| Line #: 146
FrameSummary #4:
| Filename: D:\src\classes\node\gui\color_rect.py
| Line: super().update(delta)
| Line #: 65
FrameSummary #5:
| Filename: D:\src\classes\node\gui\canvasitem.py
| Line: super().update(delta)
| Line #: 136
FrameSummary #6:
| Filename: D:\src\classes\node\node.py
| Line: self._process(delta)
| Line #: 48
FrameSummary #7:
| Filename: D:\src\classes\Object.py
| Line: self.call("_process", delta)
| Line #: 81
FrameSummary #8:
| Filename: D:\src\classes\Object.py
| Line: return mobj(*args)
| Line #: 58

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!