Oops! Eklips just crashed;
Here's this crash log!

Quick Fix for users: N/A (Not Available)
Cause of error: bad coding skillz


Error Type: pyvidplayer2.error.OpenCVError
Error: Failed to open file.
    
FrameSummary #1:
| Filename: D:\src\Eklips.py
| Line: engine.scene.update(engine.delta)
| Line #: 59
    
FrameSummary #2:
| Filename: D:\src\classes\Scene.py
| Line: raise error
| Line #: 148
    
FrameSummary #3:
| Filename: D:\src\classes\Scene.py
| Line: node.update(delta)
| Line #: 145
    
FrameSummary #4:
| Filename: D:\src\classes\node\gui\media\video_player.py
| Line: self.play()
| Line #: 101
    
FrameSummary #5:
| Filename: D:\src\classes\node\gui\media\video_player.py
| Line: self.vid        = vid.VideoPyglet(tmp_file_path)
| Line #: 66
    
FrameSummary #6:
| Filename: C:\Users\ZeeAy\AppData\Local\Programs\Python\Python313\Lib\site-packages\pyvidplayer2\video_pyglet.py
| Line: Video.__init__(self, path, chunk_size, max_threads, max_chunks, None, post_process, interp, use_pygame_audio, reverse, no_audio, speed, youtube, max_res,
| Line #: 17
    
FrameSummary #7:
| Filename: C:\Users\ZeeAy\AppData\Local\Programs\Python\Python313\Lib\site-packages\pyvidplayer2\video.py
| Line: raise OpenCVError("Failed to open file.")
| Line #: 118
    

Please send this file to the developers of Eklips at https://github.com/Za9-118/Eklips/issues. 
Your feedback is important!