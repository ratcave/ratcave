import ratcave as rc
import pyglet


window = pyglet.window.Window(resizable=True, width=400, height=800)
pyglet.clock.schedule(lambda dt: dt)

cube = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Cube', scale=.02)
cube.position.xyz = .5, .5, -2
cam = rc.Camera()
cam.projection = rc.OrthoProjection(coords='relative', origin='corner')

@window.event
def on_draw():
    with rc.default_shader, rc.default_states, cam:
        cube.draw()

@window.event
def on_resize(width, height):
    # cam.projection.match_aspect_to_viewport()

    cam.projection.aspect = width / height
    # cam.reset_uniforms()
    # cam.projection.projection_matrix[0, 0] += .01
    print(cam.projection.viewport)
    print(cam.projection_matrix)
    print(cam.uniforms['projection_matrix'])


pyglet.app.run()

