import pyglet
import ratcave as rc
import numpy as np
from numpy.random import random

n_points = 5000
width, height = 0.2, 0.5
theta = random(n_points) * np.pi * 2
verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T

cylinder = rc.Mesh.from_incomplete_data(verts, drawmode=rc.POINTS, position=(0, 0, -2), point_size=2, mean_center=False)
cylinder.uniforms['diffuse'] = 1., 1., 1.
cylinder.uniforms['flat_shading'] = True
cylinder.point_size = .02
cylinder.position.x = -.3
cylinder.scale.xyz = .5
cylinder.dynamic = True

cyl2 = cylinder.copy()
cyl2.position.x = 0
# cyl2.rotation.x = 20

cyl3 = cylinder.copy()
cyl3.position.x = .3
cyl3.rotation.y = 30

win = pyglet.window.Window(fullscreen=True)

scene = rc.Scene(meshes=[cylinder, cyl2, cyl3], bgColor=(0, 0, 0), camera=rc.Camera(projection=rc.OrthoProjection(coords='relative')))

fps_label = pyglet.window.FPSDisplay(window=win)

@win.event
def on_draw():
    with rc.default_shader:
        scene.draw()
    fps_label.draw()
#
def update(dt):
    cylinder.rotation.x += 100 * dt
    cyl2.rotation.y += 100 * dt
    cyl3.rotation.z += 100 * dt
pyglet.clock.schedule(update)

def randomize_points(dt):
    theta = random(n_points) * np.pi * 2
    verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T
    cylinder.vertices = verts
    cyl2.vertices = verts
    cyl3.vertices = verts
pyglet.clock.schedule_interval(randomize_points, 1/10.)

pyglet.app.run()