#import pyglet
#pyglet.options['debug_gl'] = False

from ratcave import graphics
from psychopy import event
import math
import pdb
import time

reader = graphics.WavefrontReader(graphics.resources.obj_primitives)

monkey = reader.get_mesh("Monkey", position=(0, 0, -2), scale = .5, centered=True)
#monkey.load_texture(graphics.resources.img_colorgrid)
monkey.material.diffuse.rgba = (.5, 1., 1., 1.)

monkey2 = reader.get_mesh("Monkey", position=(0,0, -1), scale = .7, centered=True)
monkey2.cubemap = True


plane = reader.get_mesh("Grid", position=(0, 0, -3), scale = 2, centered=True, drawstyle='point')
plane.material.diffuse.rgba = 0, 0, 0, 0

plane2 = reader.get_mesh("Plane", position=(0, 0, -3), scale = 2, centered=True)
plane2.material.diffuse.rgba = .7, .5, .2, 1.

scene = graphics.Scene([monkey2, plane])
scene.bgColor.rgb = 1., 1., 0.
scene.light.x = 1
scene.camera.fov_y  = 90

virScene = graphics.Scene([monkey, plane2])
virScene.bgColor.rgba = 1., 0., 1., 1.

win = graphics.Window(scene, virtual_scene=virScene,
grayscale=False, fullscr=False, shadow_rendering=True, shadow_fov_y = 80, autoCam=False)


aa = 0.
while 'escape' not in event.getKeys():
    currtime = time.time() * 1000
    scene.camera.x = 2 * math.sin(math.radians(aa))
    virScene.camera.position = scene.camera.position
    monkey.local.rot_y += 1.
    scene.light.x = 2 * math.sin(math.radians(aa))
    monkey2.local.rot_z += 1
    virScene.light.y = math.sin(math.radians(aa) + 1)
    aa += 5.
    predrawtime = time.time()  *1000
    win.draw()
    postdrawtime = time.time() * 1000
    win.flip()

    print("Time (msecs) to update data: {0}, and to draw: {1}".format(predrawtime-currtime, postdrawtime-predrawtime))

win.close()
