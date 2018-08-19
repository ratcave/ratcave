import pyglet
import ratcave as rc
from pyglet.gl import gl
from pyglet.window import key

window = pyglet.window.Window(resizable=True)
keys = key.KeyStateHandler()
window.push_handlers(keys)

# get an object
model_file = rc.resources.obj_primitives
monkey = rc.WavefrontReader(model_file).get_mesh('Monkey')
monkey.position.xyz = 0, 0, -2.5

camera = rc.StereoCameraGroup()

@window.event
def on_draw():
    gl.glColorMask(True, True, True, True)
    window.clear()

    with rc.default_shader, rc.default_states:
        with camera.right:
            gl.glColorMask(False, True, True, True)
            monkey.draw()

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        with camera.left:
            gl.glColorMask(True, False, False, True)
            monkey.draw()

t = 0
def update(dt):
    if keys[key.UP]:
        monkey.position.z -= .01
    elif keys[key.DOWN]:
        monkey.position.z += .01
    
    global t
    t += .5
    monkey.rotation.y = t
    for cam in camera.cameras:
        cam.uniforms['projection_matrix'] = cam.projection_matrix

pyglet.clock.schedule(update)

pyglet.app.run()
