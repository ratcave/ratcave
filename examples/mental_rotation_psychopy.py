import sys
from psychopy import visual
from pyglet.window import key
import ratcave as rc

win = visual.Window(color='black', waitBlanking=False)
shader = rc.Shader.from_file(*rc.resources.genShader)
keys = key.KeyStateHandler()
win.winHandle.push_handlers(keys)

player = visual.Rect(win, fillColor='yellow', lineColor='black',
                     width=.2, height=.2 * float(win.size[0]) / float(win.size[1]),
                     )
player_3d = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Cube', scale=.1, position=(0, 0, -1))
player_3d.uniforms['diffuse'] = 1., 1., 0.

scene = rc.Scene(meshes=[player_3d])

speed = .5
while True:
    dt = .016
    dist = speed * dt

    # Check Keyboard
    if key.ESCAPE in keys:
        win.close()
        sys.exit()
    if keys[key.LEFT]:
        player_3d.position.x -= dist
    if keys[key.RIGHT]:
        player_3d.position.x += dist
    if keys[key.UP]:
        player_3d.position.y += dist
    if keys[key.DOWN]:
        player_3d.position.y -= dist

    player_3d.rotation.z += 30 * dt

    # Draw
    with shader:
        scene.draw()
    win.flip()

