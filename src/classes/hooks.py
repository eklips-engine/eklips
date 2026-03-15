## Hook Subprocess.Popen as i am too lazy to hook every single call in pyvidplayer2
## and also hook Pyglet to not commit suicide when a new window is made at runtime
## You can use this code in any project if you want :D
# Subprocess related
import subprocess
import errno
import io
import os
import sys
import threading
import warnings

# Engine related
import pyglet            as pg
from classes.ui          import *
from classes.locals      import *
import classes.singleton as engine

## Pyglet event loop
print(" ~ Modify pyglet.app.eventloop._redraw_windows")
def newrwd(dt: float) -> None:
    # Redraw all windows
    for wid in engine.display.windows.copy():
        if wid in engine.display.windows:
            window : EklBaseWindow = engine.display.windows.get(wid)
            
            if window and not window.is_basewindow:
                window.draw(dt)
        else:
            continue
    
    # Update display
    engine.display.update()
pg.app.event_loop._redraw_windows = newrwd
print(" ~ Modify pyglet.app.eventloop.idle")
def newidle():
    clock = pg.app.event_loop.clock
    dt    = clock.update_time()
    clock.call_scheduled_functions(dt)

    # Update timeout
    clock.get_sleep_time(True)

    # SUNLIGHT YELLOW OVADRIVAAAAAAAAAAAAAA
    return 0
pg.app.event_loop.idle = newidle

## FPS Display
class HookFPSDisplay(pg.window.FPSDisplay):
    def __init__(self, window : EklWindow, color = [255,255,255,255], samples = 70):
        super().__init__(window, color, samples)

        self.window   : EklWindow = window
        self.viewport : Viewport  = window.viewports[UI_VIEWPORT]
        self.label                = pg.text.Label(
            x                     = 5,
            y                     = 5,
            text                  = "0 FPS",
            font_name             = DEFAULT_FONT_NAME,
            font_size             = DEFAULT_FONT_SIZE * 1.25,
            batch                 = self.viewport.batches[MAIN_BATCH],
            color                 = color,
            group                 = engine.ui.request_group(999))
        
    def update(self) -> None:
        """Records a new data point at the current time.

        This method is called automatically when the window buffer is flipped.
        """
        self.label.text = f"{round(engine.fps)}/{MAXFPS} FPS"
        self.label.y    = self.viewport.h-self.label.content_height
    
    def _hook_flip(self) -> None:
        self.update()
        self._window_flip()

## Subprocess
print(" ~ Modify subprocess.Popen")
print(" | ~ Save original Popen")
ogpopen = subprocess.Popen
print(" | ~ Make hook function")
print(" | | ~ Import everything")

_can_fork_exec = sys.platform not in {"emscripten", "wasi", "ios", "tvos", "watchos"}

def _cleanup(): return subprocess._cleanup()

class HookPopen(ogpopen):
    def __init__(self, args, bufsize=-1, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=True,
                 shell=False, cwd=None, env=None, universal_newlines=None,
                 startupinfo=None, creationflags=0,
                 restore_signals=True, start_new_session=False,
                 pass_fds=(), *, user=None, group=None, extra_groups=None,
                 encoding=None, errors=None, text=None, umask=-1, pipesize=-1,
                 process_group=None):
        """Create new Popen instance (but modified)."""
        shell = True
        if args[0].startswith("ff"):
            args[0] = args[0].replace("ff", ".\\bin\\ff")
        
        if not _can_fork_exec:
            raise OSError(
                errno.ENOTSUP, f"{sys.platform} does not support processes."
            )
        _cleanup()
        self._waitpid_lock = threading.Lock()
        self._input = None
        self._communication_started = False
        if bufsize is None:
            bufsize = -1
        if not isinstance(bufsize, int):
            raise TypeError("bufsize must be an integer")
        if stdout is subprocess.STDOUT:
            raise ValueError("STDOUT can only be used for stderr")
        if pipesize is None:
            pipesize = -1
        if not isinstance(pipesize, int):
            raise TypeError("pipesize must be an integer")
        if subprocess._mswindows:
            if preexec_fn is not None:
                raise ValueError("preexec_fn is not supported on Windows "
                                 "platforms")
        else:
            if pass_fds and not close_fds:
                warnings.warn("pass_fds overriding close_fds.", RuntimeWarning)
                close_fds = True
            if startupinfo is not None:
                raise ValueError("startupinfo is only supported on Windows "
                                 "platforms")
            if creationflags != 0:
                raise ValueError("creationflags is only supported on Windows "
                                 "platforms")
        self.args = args
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.encoding = encoding
        self.errors = errors
        self.pipesize = pipesize
        if (text is not None and universal_newlines is not None
            and bool(universal_newlines) != bool(text)):
            raise subprocess.SubprocessError('Cannot disambiguate when both text '
                                  'and universal_newlines are supplied but '
                                  'different. Pass one or the other.')
        self.text_mode = encoding or errors or text or universal_newlines
        if self.text_mode and encoding is None:
            self.encoding = encoding = subprocess._text_encoding()
        self._sigint_wait_secs = 0.25
        self._closed_child_pipe_fds = False
        if self.text_mode:
            if bufsize == 1:
                line_buffering = True
                bufsize = -1
            else:
                line_buffering = False
        if process_group is None:
            process_group = -1
        gid = None
        if group is not None:
            if not hasattr(os, 'setregid'):
                raise ValueError("The 'group' parameter is not supported on the "
                                 "current platform")
            elif isinstance(group, str):
                try:
                    import grp
                except ImportError:
                    raise ValueError("The group parameter cannot be a string "
                                     "on systems without the grp module")
                gid = grp.getgrnam(group).gr_gid
            elif isinstance(group, int):
                gid = group
            else:
                raise TypeError("Group must be a string or an integer, not {}"
                                .format(type(group)))
            if gid < 0:
                raise ValueError(f"Group ID cannot be negative, got {gid}")
        gids = None
        if extra_groups is not None:
            if not hasattr(os, 'setgroups'):
                raise ValueError("The 'extra_groups' parameter is not "
                                 "supported on the current platform")
            elif isinstance(extra_groups, str):
                raise ValueError("Groups must be a list, not a string")
            gids = []
            for extra_group in extra_groups:
                if isinstance(extra_group, str):
                    try:
                        import grp
                    except ImportError:
                        raise ValueError("Items in extra_groups cannot be "
                                         "strings on systems without the "
                                         "grp module")
                    gids.append(grp.getgrnam(extra_group).gr_gid)
                elif isinstance(extra_group, int):
                    gids.append(extra_group)
                else:
                    raise TypeError("Items in extra_groups must be a string "
                                    "or integer, not {}"
                                    .format(type(extra_group)))
            for gid_check in gids:
                if gid_check < 0:
                    raise ValueError(f"Group ID cannot be negative, got {gid_check}")
        uid = None
        if user is not None:
            if not hasattr(os, 'setreuid'):
                raise ValueError("The 'user' parameter is not supported on "
                                 "the current platform")
            elif isinstance(user, str):
                try:
                    import pwd
                except ImportError:
                    raise ValueError("The user parameter cannot be a string "
                                     "on systems without the pwd module")
                uid = pwd.getpwnam(user).pw_uid
            elif isinstance(user, int):
                uid = user
            else:
                raise TypeError("User must be a string or an integer")

            if uid < 0:
                raise ValueError(f"User ID cannot be negative, got {uid}")
        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)
        if subprocess._mswindows:
            if p2cwrite != -1:
                p2cwrite = subprocess.msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            if c2pread != -1:
                c2pread = subprocess.msvcrt.open_osfhandle(c2pread.Detach(), 0)
            if errread != -1:
                errread = subprocess.msvcrt.open_osfhandle(errread.Detach(), 0)
        try:
            if p2cwrite != -1:
                self.stdin = io.open(p2cwrite, 'wb', bufsize)
                if self.text_mode:
                    self.stdin = io.TextIOWrapper(self.stdin, write_through=True,
                            line_buffering=line_buffering,
                            encoding=encoding, errors=errors)
            if c2pread != -1:
                self.stdout = io.open(c2pread, 'rb', bufsize)
                if self.text_mode:
                    self.stdout = io.TextIOWrapper(self.stdout,
                            encoding=encoding, errors=errors)
            if errread != -1:
                self.stderr = io.open(errread, 'rb', bufsize)
                if self.text_mode:
                    self.stderr = io.TextIOWrapper(self.stderr,
                            encoding=encoding, errors=errors)
            self._execute_child(args, executable, preexec_fn, close_fds,
                                pass_fds, cwd, env,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite,
                                restore_signals,
                                gid, gids, uid, umask,
                                start_new_session, process_group)
        except:
            for f in filter(None, (self.stdin, self.stdout, self.stderr)):
                try:
                    f.close()
                except OSError:
                    pass
            if not self._closed_child_pipe_fds:
                to_close = []
                if stdin == subprocess.PIPE:
                    to_close.append(p2cread)
                if stdout == subprocess.PIPE:
                    to_close.append(c2pwrite)
                if stderr == subprocess.PIPE:
                    to_close.append(errwrite)
                if hasattr(self, '_devnull'):
                    to_close.append(self._devnull)
                for fd in to_close:
                    try:
                        if subprocess._mswindows and isinstance(fd, subprocess.Handle):
                            fd.Close()
                        else:
                            os.close(fd)
                    except OSError:
                        pass
            raise

print(f" | ~ Hook Popen")
subprocess.Popen = HookPopen