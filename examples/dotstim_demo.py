import pyglet
import ratcave as rc
import numpy as np
from numpy.random import random

n_points = 2000
width, height = 0.2, 0.5
theta = random(n_points) * np.pi * 2
verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T

cylinder = rc.Mesh.from_incomplete_data(verts, drawmode=rc.Mesh.points, position=(0, 0, -2),
                                        point_size=1, dynamic=True,
                                        mean_center=False)
cylinder.uniforms['diffuse'] = 1., 1., 1.
cylinder.uniforms['flat_shading'] = True

scene = rc.Scene(meshes=[cylinder], bgColor=(0., 0, 0), camera=rc.Camera(projection=rc.OrthoProjection()))

win = pyglet.window.Window()

@win.event
def on_draw():
    with rc.default_shader:
        scene.draw()


def update(dt):
    theta = random(n_points) * np.pi * 2
    verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T
    cylinder.vertices = verts
pyglet.clock.schedule_interval(update, 1/60.)

pyglet.app.run()