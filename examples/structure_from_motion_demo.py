import pyglet
import ratcave as rc
import numpy as np
from numpy.random import random

n_points = 10000
width, height = 0.2, 0.5
theta = random(n_points) * np.pi * 2
verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T

cylinder = rc.Mesh.from_incomplete_data(verts, position=(0, 0, -2), mean_center=False, drawmode=rc.POINTS, point_size=.02)
cylinder.uniforms['diffuse'] = 1., 1., 1.
cylinder.uniforms['flat_shading'] = True
cylinder.rotation.x = 20

scene = rc.Scene(meshes=[cylinder], bgColor=(0., 0, 0), camera=rc.Camera(projection=rc.OrthoProjection()))

win = pyglet.window.Window(fullscreen=True)
fps_label = pyglet.window.FPSDisplay(window=win)

@win.event
def on_draw():
    with rc.default_shader:
        scene.draw()
    fps_label.draw()

def update(dt):
    cylinder.rotation.y += 100 * dt
pyglet.clock.schedule(update)

pyglet.app.run()