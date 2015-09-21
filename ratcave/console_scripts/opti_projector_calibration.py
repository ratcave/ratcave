__author__ = 'nickdg'

import itertools
import numpy as np
import time
import os
import pickle
import sys

from psychopy import event, core
from matplotlib import pyplot as plt
from statsmodels.formula.api import ols

import ratcave
from ratcave.devices import Optitrack
from ratcave.devices.displays import propixx_utils
from ratcave.graphics.core import utils
from ratcave.graphics import *

np.set_printoptions(precision=3, suppress=True)

vert_dist = 0.66667



def scan(optitrack_ip="127.0.0.1"):

    def slow_draw(window, tracker):
        """Draws the window contents to screen, then blocks until tracker data updates."""
        window.draw()
        window.flip()

        # Wait for tracker to update, just to be safe and align all data together.
        old_frame = tracker.iFrame
        while tracker.iFrame == old_frame:
            pass

    # Check that cameras are in correct configuration (only visible light, no LEDs on, in Segment tracking mode, everything calibrated)
    tracker = Optitrack(client_ip=optitrack_ip)

    # Setup graphics
    wavefront_reader = WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0, 0, -1], scale=.006)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = Scene(circle)
    scene.camera.ortho_mode = True

    window = Window(scene, screen=1, fullscr=True)

    # Main Loop
    screenPos, pointPos = [], []
    clock = core.CountdownTimer(15)
    while (clock.getTime() > 0.) or (len(pointPos) > 100) or 'escape' in event.getKeys():

        # Update position of circle, and draw.
        circle.visible = True
        circle.local.position[[0, 1]] = np.random.random(2)
        slow_draw(window, tracker)

        # Try to isolate a single point.
        search_clock = .1
        while search_clock.getTime() > 0.:
            markers = tracker.unidentified_markers
            if len(markers) == 1:
                screenPos.append(circle.local.position)
                pointPos.append(markers[0])
                break
            print("Warning: No marker found for screen position {}".format(circle.local.position[[0, 1]]))

        # Hide circle, and wait again for a new update.
        circle.visible = False
        slow_draw(window, tracker)

    # Close Window
    window.close()

    # Early Tests
    if len(pointPos) == 0:
        raise IOError("Only {} Points collected. Please check camera settings and try for more points.".format(len(pointPos)))
    assert len(screenPos) == len(pointPos), "Length of two paired lists doesn't match."

    # Return Data
    return np.array(screenPos), np.array(pointPos), window.size


def calibrate(screenPos, pointPos):
    """Does camera cliabration using OpenCV's camera calibration function."""
    raise NotImplementedError("Still Figuring out how to get data into correct format for OpenCV")
    import cv2
    retVal, cameraMatrix, distortion_coeffs, rotVec, posVec = cv2.calibrateCamera(pointPos, screenPos, winSize)


if __name__ == '__main__':

    import pickle

    # Get command line inputs
    import argparse
    parser = argparse.ArgumentParser(description='Projector Calibration script. Projects a random dot pattern and calculates projector position.')

    parser.add_argument('-f',
                        action='store',
                        dest='filename'
                        default=None
                        help='Pickle file to store point data to.  Optional, as normally not needed.')

    args = parser.parse_args()

    # Collect data
    screenPos, pointPos, winSize = scan()

    # Either save the data or perform calibration
    if args.filename:
        with open(args.filename, 'wb') as myfile:
            pickle.dump({'imgPoints': screenPos, 'objPoints': pointPos}, myfile)

    else:
        calibrate(screenPos, pointPos)

        # Save Data in format for putting into a ratcave.graphics.Camera









