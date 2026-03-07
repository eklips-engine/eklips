"""
Module for debug settings and also profiling.

To make a profile, use `make_timer`, to mark a profile as finished for this frame, use `end_timer`.
To remove a profile, use `remove_timer`.

"But ZeeAy, why is the profile rendering in pygame?" Uhhh i dont feel like drawing graphs using pyglet
so yeah deal with it plus it doesn't hurt FPS that much
"""

## Imports
import time, pygame, random, pyglet as pg
import classes.singleton as engine
from classes.locals import *

## Values
enabled               = True

shapes_visible        = True  and enabled
fps_visible           = True  and enabled
path_visible          = True  and enabled
sprite_always_visible = False and enabled
avoid_error_mercy     = True  and enabled
skip_load             = True  and enabled
freeze_load           = False and enabled
show_graph            = True  and enabled

## Profiling
def _init_graph():
    global _pglspr, _timers, _peak, _oldpeak, graphsurf, _pygafont, ovrlysurf, _peaktxt, _0pktxt
    graphsurf = pygame.Surface((350, 200))
    graphsurf.fill("white")
    ovrlysurf = pygame.Surface(graphsurf.get_size(), pygame.SRCALPHA)
    _timers   = {}
    _peak     = ZDE_FIX
    _oldpeak  = ZDE_FIX
    _pygafont = pygame.font.Font(None, 25)
    _peaktxt  = _pygafont.render(str(_peak), True, "black")
    _0pktxt   = _pygafont.render("0", True, "black")
    _pglspr   = pg.sprite.Sprite(engine.resources.cnvsrfekl(graphsurf))

def start_timer(name):
    global _timers

    if name in _timers:
        _timers[name][0] = time.time()
        _timers[name][1] = -1
        _timers[name][2] = False
        return

    color         = [random.randint(25,255), random.randint(25,255), random.randint(25,255)]
    _timers[name] = [
        time.time(), -1, False,
        color,
        0,
        _pygafont.render(name, True, color),
        0
    ]

def end_timer(name):
    if not name in _timers: return
    _timers[name][1] = time.time()
    _timers[name][2] = True

def remove_timer(name):
    if not name in _timers: return
    _timers.pop(name)

def _draw():
    global graphsurf, ovrlysurf, _pglspr
    fullsrf = pygame.Surface(graphsurf.get_size())
    fullsrf.blit(graphsurf)
    fullsrf.blit(ovrlysurf)

    _pglspr.image = engine.resources.cnvsrfekl(fullsrf)
    _pglspr.image.blit(0,0)

def draw_debug_graph():
    global graphsurf, _timers, _peak, _oldpeak, _pglspr, ovrlysurf, _peaktxt, _0pktxt

    # What
    start_timer("DebugGraphDraw")

    # Dimensions
    w  = 3
    gw = graphsurf.get_width()
    gh = graphsurf.get_height()

    # Empty overlay
    ovrlysurf.fill([0,0,0,0])

    # Scroll graph left
    graphsurf.blit(graphsurf, (-w, 0))
    pygame.draw.rect(graphsurf, "white", (gw-w, 0, w, gh))

    _oldpeak = _peak

    _doomed = []
    for name in _timers:
        timer = _timers[name]
        start = timer[0]
        end   = timer[1]
        if timer[1] == -1:
            end = time.time()
        
        elapsed = end - start
        
        if elapsed > _peak:
            _peak = elapsed
            _peaktxt  = _pygafont.render(str(_peak), True, "black")
            if _peak <= 0:
                _peak = ZDE_FIX
        
        if timer[2]:
            timer[1] -= elapsed / 2
            if elapsed / 2 <= ZDE_FIX:
                _doomed.append(name)

        y = gh - w - int((elapsed / _peak) * gh)

        pygame.draw.line(
            graphsurf,
            timer[3],
            (gw - w - w, timer[4]),
            (gw - w, y),
            w
        )
        ovrlysurf.blit(timer[5], [gw-(w*3)-timer[5].width, y-w*2-timer[5].height])

        timer[4] = y
    for name in _doomed:
        _timers.pop(name)
    ovrlysurf.blit(_peaktxt,             [gw-_peaktxt.width,                 0])
    ovrlysurf.blit(_0pktxt,              [gw-_0pktxt.width,  gh-_0pktxt.height])
    ovrlysurf.blit(_pygafont.render(time.strftime("%H:%M:%S"),0,"red"),  [0, 0])

    _draw()

    # Still.... What
    end_timer("DebugGraphDraw")