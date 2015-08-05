__author__ = 'ratcave'

from psychopy import event
from devices.optitrack import Optitrack
from graphics import *
import pdb

# Connect to Optitrack
optitrack_ip="10.153.170.85"
tracker = Optitrack(client_ip=optitrack_ip)


# Create Arena
#reader = Wavefront('../resources/ESMI_NOP_Positions.obj')
reader = Wavefront('../CliffAvoidance/Objects/CliffAvoidance.obj')
arena = reader.get_mesh('Arena', lighting=True)
arena.load_texture('../resources/colorGrid.png')

# Create Cube
reader = Wavefront('../resources/multipleprimitives.obj')
cube = reader.get_mesh('Sphere', lighting=True, scale=.02, centered=True)


scene = Scene(arena, cube)
scene.camera = projector
scene.camera.position = projector_position
#scene.camera.rot_y += 180

window = PsychWindow(scene, screen=1, fullscr=True)

def tracker_update():
    arena.position = tracker.rigid_bodies['Arena'].position
    arena.rotation = tracker.rigid_bodies['Arena'].rotation
    #arena.rot_y += 180
    cube.position = tracker.rigid_bodies['CalibWand'].position

    scene.light.position = scene.camera.position


while True:

    # Check if keyboard pressed, and update camera parameters according to key pressed.
    keylist = event.getKeys()
    if len(keylist) > 0:
        if 'up' in keylist:
            scene.camera.z += .003
        elif 'down' in keylist:
            scene.camera.z -= .003
        elif 'left' in keylist:
            scene.camera.x += .003
        elif 'right' in keylist:
            scene.camera.x -= .003
        elif 'pageup' in keylist:
            scene.camera.y += .003
        elif 'pagedown' in keylist:
            scene.camera.y -= .01
        elif 'x' in keylist:
            scene.camera.fov_y += .01
        elif 'z' in keylist:
            scene.camera.fov_y -= .01
        elif 'w' in keylist:
            scene.camera.rot_x += .1
        elif 's' in keylist:
            scene.camera.rot_x -= .1
        elif 'd' in keylist:
            scene.camera.rot_z += .1
        elif 'a' in keylist:
            scene.camera.rot_z -= .1
        elif 'f' in keylist:
            scene.camera.rot_y += .1
        elif 'r' in keylist:
            scene.camera.rot_y -= .1
        elif 'escape' in keylist:
            window.close()
            break

        print "Camera settings:\n -shift: {0}, {1}\n -position: {2}\n -fov_y: {3}\n -rotation: {4}\n\n".format(scene.camera.x_shift, scene.camera.y_shift, scene.camera.position, scene.camera.fov_y, scene.camera.rotation)

    # Update positions through Optitrack
    tracker_update()

    # Re-Draw Everything
    window.draw()
    window.flip()