import pyglet
import ratcave as rc
import numpy as np
from numpy.random import random

n_points = 200
width, height = 0.2, 0.5
theta = random(n_points) * np.pi * 2
verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T

cylinder = rc.Mesh.from_incomplete_data(verts, drawmode=rc.Mesh.points, position=(0, 0, -2), point_size=2, dynamic=True,
                                        mean_center=False)
cylinder.uniforms['diffuse'] = 1., 1., 1.
cylinder.uniforms['flat_shading'] = True

scene = rc.Scene(meshes=[cylinder], bgColor=(0., 0, 0), camera=rc.Camera(projection=rc.OrthoProjection()))

win = pyglet.window.Window()

@win.event
def on_draw():
    with rc.default_shader:
        scene.draw()



turn = 0
def update(dt):
    global turn
    turn += 1
    if not turn % 1:
        theta = random(n_points) * np.pi * 2
        verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T
        cylinder.vertices = verts

    # print(cylinder.arrays[0][0, :])
    cylinder.rotation.z += 100 * dt
pyglet.clock.schedule(update)

pyglet.app.run()