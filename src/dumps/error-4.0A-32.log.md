Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz

Error Type: SyntaxError
Error: invalid syntax (<string>, line 55)

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
| Filename: D:\src\classes\node\twod\sprite2d.py
| Line: super().update(delta)
| Line #: 44
FrameSummary #5:
| Filename: D:\src\classes\node\twod\node2d.py
| Line: super().update(delta)
| Line #: 27
FrameSummary #6:
| Filename: D:\src\classes\node\gui\canvasitem.py
| Line: super().update(delta)
| Line #: 136
FrameSummary #7:
| Filename: D:\src\classes\node\node.py
| Line: self._process(delta)
| Line #: 48
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
| Line #: 13
FrameSummary #11:
| Filename: D:\src\classes\Singleton.py
| Line: scene.load()
| Line #: 148
FrameSummary #12:
| Filename: D:\src\classes\Scene.py
| Line: self.add_node(node_data)
| Line #: 132
FrameSummary #13:
| Filename: D:\src\classes\Scene.py
| Line: object.__init__(node_obj_data, parent)
| Line #: 113
FrameSummary #14:
| Filename: D:\src\classes\node\gui\color_rect.py
| Line: super().__init__(data,parent)
| Line #: 40
FrameSummary #15:
| Filename: D:\src\classes\node\gui\canvasitem.py
| Line: super().__init__(data,parent)
| Line #: 43
FrameSummary #16:
| Filename: D:\src\classes\node\node.py
| Line: super().__init__(data)
| Line #: 39
FrameSummary #17:
| Filename: D:\src\classes\Object.py
| Line: self._init_script()
| Line #: 46
FrameSummary #18:
| Filename: D:\src\classes\Object.py
| Line: self.script.init_param(self.properties)
| Line #: 68
FrameSummary #19:
| Filename: D:\src\classes\Resources.py
| Line: exec(script_contents, globals=script_glb,locals=script_glb)
| Line #: 162
SyntaxError related:
| Filename: <string>
| Message: invalid syntax
| Offset: 11
| EndOffset: 16
| Text:         })scene.add_node({
| Line#: 55
| End Line#: 55

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!