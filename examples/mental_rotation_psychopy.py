import sys
import pyglet
from psychopy import visual, event
from pyglet.window import key

win = visual.Window(color='black')

player = visual.Rect(win, fillColor='yellow', lineColor='black',
                     width=.2, height=.2 * float(win.size[0]) / float(win.size[1]),
                     )

@win.winHandle.event
def on_draw():
    win.winHandle.clear()
    player.ori += 1
    player.draw()

keys = key.KeyStateHandler()
win.winHandle.push_handlers(keys)

def detect_keys(dt):
    print(dt, keys)
    speed = .5
    dist = speed * dt
    if key.ESCAPE in keys:
        win.close()
        sys.exit()
    if keys[key.LEFT]:
        player.pos[0] -= dist
    if keys[key.RIGHT]:
        player.pos[0] += dist
    if keys[key.UP]:
        player.pos[1] += dist
    if keys[key.DOWN]:
        player.pos[1] -= dist
pyglet.clock.schedule(detect_keys)

pyglet.app.run()
