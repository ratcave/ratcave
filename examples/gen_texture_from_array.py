import matplotlib.pyplot as plt
import numpy as np
import pyglet
import ratcave as rc
from pyglet.extlibs import png
import pyglet.gl as gl



window = pyglet.window.Window()

cube = rc.Mesh.from_primitive('Cube', position=(0, 0, -3), rotation=(45, 45, 0))

arr = np.random.randint(0, 255, size=(128, 128, 4))

tex2 = rc.Texture(values=arr)

cube.textures.append(tex2)

@window.event
def on_draw():
    window.clear()
    with rc.default_shader, rc.default_camera, rc.default_states:
        cube.draw()


def randomize_texture(dt):
    tex2.values = np.random.randint(0, 255, size=(128, 128, 4))
pyglet.clock.schedule(randomize_texture)

pyglet.app.run()