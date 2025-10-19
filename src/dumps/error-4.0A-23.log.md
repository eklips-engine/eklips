Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: You pressed Ctrl+C. Don't do that next time okay?
Cause of error: bad coding skillz

Error Type: KeyboardInterrupt
Error: 

FrameSummary #1:
| Filename: D:\src\Eklips.py
| Line: engine.scene.update(engine.delta)
| Line #: 62
FrameSummary #2:
| Filename: D:\src\classes\Scene.py
| Line: node.update(delta)
| Line #: 145
FrameSummary #3:
| Filename: D:\src\classes\node\gui\button.py
| Line: self.draw()
| Line #: 42
FrameSummary #4:
| Filename: D:\src\classes\node\gui\button.py
| Line: size          = self._draw_onto_screen(typ)
| Line #: 48
FrameSummary #5:
| Filename: D:\src\classes\node\gui\button.py
| Line: thmobj = engine.thm.draw_marginable_thing(typ, self.runtime_data["rendererpos"], sz, self.window_id, self.anchor, self.layer)
| Line #: 70
FrameSummary #6:
| Filename: D:\src\classes\Resources.py
| Line: rs = engine.interface.blit(
| Line #: 330
FrameSummary #7:
| Filename: D:\src\classes\UI.py
| Line: spr.image = img
| Line #: 162
FrameSummary #8:
| Filename: C:\Users\ZeeAy\AppData\Local\Programs\Python\Python313\Lib\site-packages\pyglet\sprite.py
| Line: self._set_texture(img.get_texture())
| Line #: 489
FrameSummary #9:
| Filename: C:\Users\ZeeAy\AppData\Local\Programs\Python\Python313\Lib\site-packages\pyglet\sprite.py
| Line: def _set_texture(self, texture: Texture) -> None:
| Line #: 492

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!