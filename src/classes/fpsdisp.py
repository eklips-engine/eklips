import classes.singleton as engine
import pyglet as pg
from pyglet.text import Label

class FPSDisplay:
    """Display of a window's framerate. (Eklips remix)

    This is a convenience class to aid in profiling and debugging.  Typical
    usage is to create an `FPSDisplay` for each window, and draw the display
    at the end of the windows' :py:meth:`~pyglet.window.Window.on_draw` event handler::

        from pyglet.window import Window, FPSDisplay

        window = Window()
        fps_display = FPSDisplay(window)

        @window.event
        def on_draw():
            # ... perform ordinary window drawing operations ...

            fps_display.draw()

    The style and position of the display can be modified via the ``label`` attribute. The display can be set to
    update more or less often by setting the `update_period` attribute.

    .. note: Setting the `update_period` to a value smaller than your Window refresh rate will cause
             inaccurate readings.
    """

    #: Time in seconds between updates.
    update_period = 0.25

    #: The text label displaying the framerate.
    label: Label

    def __init__(self, window: pg.window.Window, color: tuple[int, int, int, int] = (127, 127, 127, 127),
                 samples: int = 240) -> None:
        """Create an FPS Display.

        Args:
            window:
                The Window you wish to display frame rate for.
            color:
                The RGBA color of the text display. Each channel represented as 0-255.
            samples:
                How many delta samples are used to calculate the mean FPS.
        """
        from collections import deque
        from statistics import mean

        from pyglet.text import Label
        self._time = engine.clock.time
        self._mean = mean

        # Hook into the Window.flip method:
        self._window_flip, window.flip = window.flip, self._hook_flip
        self.layer                     = engine.interface.layer_amount-1
        self.text                      = ""

        self._elapsed     = 0.0
        self._last_time   = self._time()
        self._delta_times = deque(maxlen=samples)

    def update(self) -> None:
        """Records a new data point at the current time.

        This method is called automatically when the window buffer is flipped.
        """
        t = self._time()
        delta = t - self._last_time
        self._elapsed += delta
        self._delta_times.append(delta)
        self._last_time = t

        if self._elapsed >= self.update_period:
            self._elapsed = 0
            self.text = f'{1 / self._mean(self._delta_times):.2f}'

    def draw(self) -> None:
        """Draw the label."""
        engine.interface.render(self.text, [10,10], layer=self.layer, anchor='bottom', size=24, alpha=127)

    def _hook_flip(self) -> None:
        self.update()
        self._window_flip()