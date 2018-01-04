import pyglet
import ratcave as rc
import itertools as it
import numpy as np

# Create Window
window = pyglet.window.Window(resizable=True, vsync=False)

# Create Mesh
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)
monkey = obj_reader.get_mesh("Monkey")

monkey.position.xyz = 0, 0, -4
monkey.scale.xyz = .25
monkey.point_size = .1

fps_display = pyglet.window.FPSDisplay(window)

light = rc.Light()
light.time = 0.

@window.event
def on_draw():
    window.clear()
    with rc.default_shader, rc.default_states, light:
        for x, y in it.product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]):
            monkey.position.x = x
            monkey.position.y = y

            monkey.drawmode = rc.POINTS if x % 2 and y % 2 else rc.TRIANGLES
            monkey.uniforms['diffuse'][0] = (x + 1) / 4.
            monkey.uniforms['diffuse'][1:] = (y + 1) / 4.
            monkey.scale.z = np.linalg.norm((x, y)) / 10. + .03

            monkey.draw()

    fps_display.draw()

def update(dt):
    monkey.rotation.y += dt * 20.
    light.time += dt
    light.position.x = np.sin(light.time * 3) * 5
    light.position.y = np.cos(light.time * 3) * 5
    # light.update()
pyglet.clock.schedule(update)

pyglet.app.run()