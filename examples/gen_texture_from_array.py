import matplotlib.pyplot as plt
import numpy as np
import pyglet
import ratcave as rc


window = pyglet.window.Window()

cube = rc.Mesh.from_primitive('Cube', position=(0, 0, -3))


# image = pyglet.image.load(rc.resources.img_colorgrid)
# data = image.get_image_data()
# arr = np.ndarray(buffer=data.data,
#            shape=(image.height, image.width, len(image.format)),
#            dtype=np.uint8)

tex = rc.Texture.from_image(rc.resources.img_colorgrid)
arr = tex.values
print("Texture Array Shape: {}".format(arr.shape))

cube.textures.append(tex)

@window.event
def on_draw():
    window.clear()
    with rc.default_shader, rc.default_camera, rc.default_states:
        cube.draw()


def rotate_cube(dt):
    cube.rotation.x += 15 * dt
    cube.rotation.y += 30 * dt
pyglet.clock.schedule(rotate_cube)

pyglet.app.run()