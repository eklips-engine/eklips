Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: AttributeError
Error: 'Resource' object has no attribute 'get_thing'

FrameSummary #1:
| Filename: D:\src\Eklips.py
| Line: engine.scene.update(engine.delta)
| Line #: 62
FrameSummary #2:
| Filename: D:\src\classes\Scene.py
| Line: raise error
| Line #: 153
FrameSummary #3:
| Filename: D:\src\classes\Scene.py
| Line: node.update(delta)
| Line #: 148
FrameSummary #4:
| Filename: D:\src\classes\node\gui\button.py
| Line: self.draw()
| Line #: 42
FrameSummary #5:
| Filename: D:\src\classes\node\gui\button.py
| Line: size   = self._draw_onto_screen(typ)
| Line #: 48
FrameSummary #6:
| Filename: D:\src\classes\node\gui\button.py
| Line: color  = engine.thm.get_thing(typ)["fontcol"]
| Line #: 60

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!