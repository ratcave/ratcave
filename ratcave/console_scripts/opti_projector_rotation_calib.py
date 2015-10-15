__author__ = 'ratcave'

from psychopy import event
import ratcave
from ratcave.graphics import *
import numpy as np

np.set_printoptions(precision=2, suppress=True)

def display(optitrack_ip="127.0.0.1"):

    # Connect to Optitrack
    tracker = ratcave.devices.Optitrack(client_ip=optitrack_ip)

    # Create Arena and cube
    reader = WavefrontReader(ratcave.graphics.resources.obj_arena)
    arena = reader.get_mesh('Arena', lighting=True, centered=False)
    arena.load_texture(ratcave.graphics.resources.img_colorgrid)

    reader = WavefrontReader(ratcave.graphics.resources.obj_primitives)
    cube = reader.get_mesh('Sphere', lighting=True, scale=.02, centered=True)

    # Create Scene and Window
    scene = Scene([arena, cube])
    scene.camera = projector
    scene.camera.fov_y = 27.25

    scene.light.position = scene.camera.position

    window = Window(scene, screen=1, fullscr=True)

    # Print the Following every time a key is detected:
    print "Camera settings:\n -shift: {0}, {1}\n -position: {2}\n -fov_y(xz): {3}\n -rotation: {4}\n\n".format(
        scene.camera.x_shift, scene.camera.y_shift, scene.camera.position, scene.camera.fov_y, scene.camera.rotation)
    print "Arena settings:\n -local\n\tPosition: {}\n\tRotation: {}\n -world\n\tPosition: {}\n\tRotation: {}".format(
        arena.local.position, arena.local.rotation, arena.world.position, arena.world.rotation)

    while True:

        # Update Everything's Position
        arena.world.position = tracker.rigid_bodies['Arena'].position
        arena.world.rotation = tracker.rigid_bodies['Arena'].rotation_pca_y
        cube.local.position = tracker.rigid_bodies['CalibWand'].position

        # Re-Draw Everything
        window.draw()
        window.flip()

        keys = event.getKeys()
        if 'escape' in keys:
            window.close()
            break
        elif 'up' in keys:
            scene.camera.fov_y += .1
            print('fov_y: {}'.format(scene.camera.fov_y))
        elif 'down' in keys:
            scene.camera.fov_y -= .1
            print('fov_y: {}'.format(scene.camera.fov_y))



if __name__ == '__main__':
    display()