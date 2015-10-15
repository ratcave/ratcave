__author__ = 'ratcave'

from psychopy import event
import ratcave
from ratcave.graphics import *
import pdb
import appdirs
import pickle
import copy
from os import path
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
    scene.camera.fov_y = 41.2 / 1.47

    #scene.camera.rotation = -90, 0, 0
    # scene.camera.rotation[0] *= -1
    #scene.camera.rotation[1], scene.camera.rotation[2] = scene.camera.rotation[2], scene.camera.rotation[1]
    #scene.camera.rotation[2] = 0

    scene.light.position = scene.camera.position

    window = Window(scene, screen=1, fullscr=True)

    aa = 0
    while True:

        # Update Everything's Position
        rot_mod = tracker.rigid_bodies['Arena'].rotation[1] - tracker.rigid_bodies['Arena'].rotation_pca_y[1]

        arena.world.position = tracker.rigid_bodies['Arena'].position
        arena.world.rotation = tracker.rigid_bodies['Arena'].rotation_pca_y
        arena.world.rotation[1] += aa

        #arena.local.rotation[1] = tracker.rigid_bodies['Arena'].rotation_pca_y[1]
        #arena.local.rotation[1] += 180

        cube.local.position = tracker.rigid_bodies['CalibWand'].position

        # Re-Draw Everything
        window.draw()
        window.flip()

        # Check if keyboard pressed, and update camera parameters according to key pressed.
        key_dict = {'up': [scene.camera.position[2], .003],
                    'down': [scene.camera.position[2], -.003],
                    'left': [scene.camera.position[0], .003],
                    'right': [scene.camera.position[0], -.003],
                    'pageup': [scene.camera.position[1], .003],
                    'pagedown': [scene.camera.position[1], -.003],
                    'x': [scene.camera.fov_y, .05],
                    'z': [scene.camera.fov_y, -.05],
                    'w': [scene.camera.rotation[0], .1],
                    's': [scene.camera.rotation[0], -.1],
                    'd': [scene.camera.rotation[2], .1],
                    'a': [scene.camera.rotation[2], -.1],
                    'f': [scene.camera.rotation[1], .1],
                    'r': [scene.camera.rotation[1], -.1],
                    'j': [aa, .1],
                    'k': [aa, -.1]}

        keylist = event.getKeys()
        for key in keylist:
            if key == 'escape':
                window.close()
                break
            elif key in key_dict:
                key_dict[key][0] += key_dict[key][1]


            # Print the Following every time a key is detected:
            print "Camera settings:\n -shift: {0}, {1}\n -position: {2}\n -fov_y(xz): {3}\n -rotation: {4}\n\n".format(
                scene.camera.x_shift, scene.camera.y_shift, scene.camera.position, scene.camera.fov_y, scene.camera.rotation)
            print "Arena settings:\n -local\n\tPosition: {}\n\tRotation: {}\n -world\n\tPosition: {}\n\tRotation: {}".format(
                arena.local.position, arena.local.rotation, arena.world.position, arena.world.rotation)

            print("(Press Spacebar to update to new projector parameters")

            # If spacebar was pressed, save all.
            if 'space' in keylist:
                confirm = raw_input("Are you sure you want to save? (y/n)")
                if 'y' in confirm.lower():
                    proj_file = path.join(appdirs.user_data_dir("ratCAVE"), "projector_data.pickle")  # TODO: Use relative import to get data_dir from ratCAVE.__init__.py
                    data = {'position': scene.camera.position, 'rotation': scene.camera.rotation, 'fov_y': scene.camera.fov_y}
                    pickle.dump(data, open(proj_file, 'wb'))
                    print("New Data Saved.  Projector Values Overwritten.")
                else:
                    print("Nothing saved. Exiting...")
                window.close()
                break


if __name__ == '__main__':
    display()