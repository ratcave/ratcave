import pyglet
import ratcave as rc

win = pyglet.window.Window(resizable=True)
pyglet.clock.schedule(lambda dt: dt)

reader = rc.WavefrontReader(rc.resources.obj_primitives)
stars = reader.get_mesh('Torus', drawmode=rc.POINTS)
stars.point_size = .4
stars.uniforms['diffuse'] = 1., 1., 1.
stars.position.xyz = 0, 0, -2
stars.scale.xyz = .5

monkey = reader.get_mesh('Monkey', position=(0, 0, -2))
fbo = rc.FBO(texture=rc.Texture)

@win.event
def on_draw():
    with rc.default_shader:
        with fbo:
            stars.draw()
        with fbo.texture:
            monkey.draw()


pyglet.app.run()