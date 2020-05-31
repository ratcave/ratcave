import pyglet
import ratcave as rc

win = pyglet.window.Window(resizable=True)

reader = rc.WavefrontReader(rc.resources.obj_primitives)
stars = reader.get_mesh('Torus', drawmode=rc.GL_POINTS)
stars.point_size = 3
stars.uniforms['diffuse'] = 1., 1., 1.
stars.position.xyz = 0, 0, -2
stars.scale.xyz = 1.2

monkey = reader.get_mesh('Monkey', position=(0, 0.1, -2))
monkey.uniforms['flat_shading'] = True
monkey.uniforms['diffuse'] = 1., 1., 1.
monkey.uniforms['spec_weight'] = 0.

fbo = rc.FBO(texture=rc.Texture(width=win.width, height=win.height))

def update(dt):
    stars.rotation.z += 10. * dt
pyglet.clock.schedule(update)


@win.event
def on_draw():

    with rc.default_shader:
        with fbo:
            rc.clear_color(0, 0, 0)
            win.clear()
            stars.draw()
        with fbo.texture:
            rc.clear_color(.5, .5, .5)
            win.clear()
            monkey.draw()


pyglet.app.run()