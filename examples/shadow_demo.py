import pyglet
import ratcave as rc
import itertools as it
import numpy as np
try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

# Create Window
window = pyglet.window.Window(resizable=True, vsync=False)

# Create Mesh
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)
monkey = obj_reader.get_mesh("Monkey")

monkey.position.xyz = 0, 0, -4
monkey.scale.xyz = .25
monkey.point_size = .1

plane = obj_reader.get_mesh('Plane')
plane.position.xyz = 0, 0, -5
plane.rotation.x = 0
plane.scale.xyz = 8
plane.uniforms['spec_weight'] = 0


fps_display = pyglet.window.FPSDisplay(window)

light = rc.Light()
light.projection.fov_y = 75.
light.position.z = 3
light.time = 0.

fbo_shadow = rc.FBO(texture=rc.DepthTexture(width=2048, height=2048))
plane.textures.append(fbo_shadow.texture)
plane.textures.append(rc.Texture.from_image(rc.resources.img_colorgrid))
monkey.textures.append(fbo_shadow.texture)

@window.event
def on_draw():
    window.clear()
    with ExitStack() as stack:
        for shader in [rc.resources.shadow_shader, rc.default_shader]:
            with shader, rc.default_states, light, rc.default_camera:
                if shader == rc.resources.shadow_shader:
                    stack.enter_context(fbo_shadow)
                    window.clear()
                else:
                    stack.close()

                for x, y in it.product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]):
                    monkey.position.x = x
                    monkey.position.y = y
                    monkey.drawmode = rc.POINTS if x % 2 and y % 2 else rc.TRIANGLES
                    monkey.uniforms['diffuse'][0] = (x + 1) / 4.
                    monkey.uniforms['diffuse'][1:] = (y + 1) / 4.
                    monkey.scale.z = np.linalg.norm((x, y)) / 10. + .03
                    monkey.draw()

                plane.draw()

    fps_display.draw()

def update(dt):
    monkey.rotation.y += dt * 40.
    light.time += dt
    light.position.x = np.sin(light.time * .5) * 3
    light.position.y = np.cos(light.time * .5) * 3
pyglet.clock.schedule(update)

pyglet.app.run()