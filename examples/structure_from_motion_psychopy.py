from psychopy import visual, event
import ratcave as rc
import numpy as np
from numpy.random import random

n_points = 200
width, height = 0.2, 0.5
theta = random(n_points) * np.pi * 2
verts = np.vstack((np.sin(theta) * width, (random(n_points) - .5) * height, np.cos(theta) * width)).T

cylinder = rc.Mesh.from_incomplete_data(verts, drawmode=rc.POINTS, position=(0, 0, -2), point_size=2, mean_center=False)
cylinder.uniforms['diffuse'] = 1., 1., 1.
cylinder.uniforms['flat_shading'] = True

scene = rc.Scene(meshes=[cylinder], bgColor=(0., 0, 0))
shader = rc.Shader.from_file(*rc.resources.genShader)
scene.camera.projection = rc.OrthoProjection()

win = visual.Window()

while 'escape' not in event.getKeys():
    cylinder.rotation.y += 100 * .02
    with shader:
        scene.draw()
    win.flip()


