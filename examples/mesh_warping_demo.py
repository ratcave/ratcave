import pyglet
import ratcave as rc
import numpy as np
from numpy.random import random
import itertools

def lerp(vecA, vecB, time):
    '''
    Linear interpolation between two vectors.
    Function from pyGameMath: https://github.com/explosiveduck/pyGameMath
    '''
    return (vecA * time) + (vecB * (1.0 - time))

reader = rc.WavefrontReader(rc.resources.obj_primitives)
mesh = reader.get_mesh('MonkeySmooth', position=(0, 0, -2), scale=.2, dynamic=True)

scene = rc.Scene(meshes=[mesh], bgColor=(0.5, 0, 0), camera=rc.Camera(projection=rc.OrthoProjection()))

win = pyglet.window.Window()
fps_label = pyglet.window.FPSDisplay(window=win)

@win.event
def on_draw():
    with rc.default_shader:
        scene.draw()
    fps_label.draw()

def animation_sequence(mesh, nframes=50):
    verts_orig = mesh.arrays[0][:, :3].copy()
    verts_normed = (verts_orig.T / np.linalg.norm(verts_orig, axis=1)).T
    norms_orig = mesh.arrays[1][:, :3].copy()
    norms_normed = verts_normed

    for t in itertools.cycle(itertools.chain(np.linspace(0, 1, nframes), np.ones(nframes), np.linspace(0, 1, nframes)[::-1], np.zeros(nframes))):
        vv = lerp(verts_orig, verts_normed, t)
        nn = lerp(norms_orig, norms_normed, t)
        mesh.arrays[0][:, :3] = vv
        mesh.arrays[1][:, :3] = nn
        yield


anim = animation_sequence(mesh)

def update(dt):
    mesh.rotation.y += 120 * dt
    next(anim)
pyglet.clock.schedule(update)

pyglet.app.run()