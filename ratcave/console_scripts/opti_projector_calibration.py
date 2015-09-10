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

def scan(start_delay=5, trial_duration=10, optitrack_ip="127.0.0.1"):
    """Start scan protocol for measuring projector position.  In this protocol, a single point if projected, and the
    experimenter must move a piece of paper along the path of the point while Optitrack (in visible light mode) records
    that point's position.  Periodically ('trial_duraction'), the point's position changes.  The data from this protocol
     saved in file_name under three lists: Proj_x, Proj_y, and Point_position3d."""


    # Check that cameras are in correct configuration (only visible light, no LEDs on, in Segment tracking mode, everything calibrated)
    tracker = Optitrack(client_ip=optitrack_ip)

    # Setup graphics
    wavefront_reader = WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0, 0, -1], scale=.006)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = Scene(circle)
    scene.camera.ortho_mode = True

    window = Window(scene, screen=1, fullscr=True)

    # Set positions
    circle.last_position = [0., 0., 0.]

    time.sleep(float(start_delay))

    x_list = [0, -.3,  .3,   0,  0, -.6, .6,   0,  0, -.9, .9]
    y_list = [0,   0,   0, -.25, .25,   0,  0, -.5, .5,   0,  0]

    # Main Loop
    data_list = []
    for x, y in zip(x_list, y_list):

        # Give a short pause between points, to keep from mixing the data between screen positions
        circle.visible = False
        window.draw()
        window.flip()
        time.sleep(.1)


        # Set mesh position
        circle.xy = x, y
        circle.visible = True

        clock = core.CountdownTimer(trial_duration)
        while clock.getTime() > 0:
            # Get tracker point position
            positions = tracker.get_unidentified_positions(1)
            if positions and (positions[0][1] < circle.last_position[1] - .01 or positions[0][1] > circle.last_position[1] + .01):
                circle.last_position = positions[0]
                data_list.append([circle.x, circle.y, positions[0]])

            window.draw()
            window.flip()

            if 'escape' in event.getKeys():
                window.close()
                sys.exit()


    # After program ends, return the collected data
    window.close()
    return data_list


def analyze(data):

    # Get data
    x_2d, y_2d, points = zip(*data)
    x_2d = np.array(x_2d)
    y_2d = np.array(y_2d)
    points = np.array(points)

    # Separate data into lists by unique x_2d and y_2d combinations (each should be a single line)
    unique_vals = np.unique(np.vstack((x_2d, y_2d)))
    unique_2d = []
    for x, y in itertools.product(unique_vals, unique_vals):
        mask = (x_2d == x) * (y_2d == y)
        if np.sum(mask) > 1:
            unique_2d.append((x, y))

    points_sep = []
    for idx, (x, y) in enumerate(unique_2d):

        mask = (x_2d == x) * (y_2d == y)

        pp = points[mask, :]
        points_sep.append(pp)

    fig = plt.figure()
    ax = fig.add_subplot(221, projection='3d')
    utils.plot3_square(ax, points)

    # Remove beginning and end of each line
    for idx, data in enumerate(points_sep):
        points_sep[idx] = data[10:-10, :]

    ax = fig.add_subplot(222, projection='3d')
    for point, color in zip(points_sep, 'rgbmcykrgbmcyk'):
        utils.plot3_square(ax, point, color=color)


    # Remove outliers using simes-hochberg regression.
    threshold = 0.9
    for idx, data in enumerate(points_sep):
        regression = ols("y ~ x + z", data=dict(x=data[:, 0], y=data[:, 1], z=data[:, 2])).fit()
        test = regression.outlier_test('simes-hochberg')
        outlier_idx = test[test.icol(1) < threshold].index.values

        points_sep[idx] = np.delete(data, outlier_idx, axis=0)

    # Fit data to a line
    wt_all, offset_all = [], []
    for data in points_sep:
        # Calculate offset
        offset = np.mean(data, axis=0, keepdims=True)
        offset_all.append(offset)

        # Calculate slope
        uu, ss, vv = np.linalg.svd(data - offset)
        slope = np.array([vv[0,:]])
        wt_all.append(slope)

    ## ESTIMATE PROJECTOR'S X,Y,Z FOCAL POINT POSITION ##
    # Infer Projector Position from Average Estimated Intersection Point.
    point_estimates = []
    for idx, (u1, o1) in enumerate(zip(wt_all[0:-1], offset_all[0:-1])):
        for u2, o2 in zip(wt_all[idx+1:], offset_all[idx+1:]):

            # Make Vector PQ, which subtracts line 1 from line 2 (while keeping each line's parameter seperate). [xyz x t,s,1]
            PQ = np.concatenate((u1, -u2, o1-o2), axis=0).transpose()

            # Find the line that is orthogonal to both PQ and each line (dot product = 0)
            n_all = np.dot(np.vstack((u1, u2)), PQ)
            A = n_all[:, :2]
            b = -n_all[:, 2]
            #try:
            t, s = np.linalg.solve(A, b)
            #except np.linalg.linalg.LinAlgError:
             #   pass
            # Get the midpoint of the orthogonal line (projector point estimate) and that line's distance (error estimate)
            p1 = (u1 * t) + o1
            p2 = (u2 * s) + o2
            midpoint = (p1 + p2) / 2.

            # Append to list of point estimates
            point_estimates.append(midpoint.flatten())

    point_estimates = np.array(point_estimates)  # Put back into matrix
    mean_position = np.mean(point_estimates, axis=0)
    std_estimate = np.std(point_estimates, axis=0)
    print("Mean Position: {0}\n STD Position: {1}".format(mean_position, std_estimate))



    # Plot Data and Position estimate
    ax = fig.add_subplot(223, projection='3d')
    for data, color in zip(points_sep, 'rgbmcykrgbmcyk'):
        utils.plot3_square(ax, data, color=color)

    #utils.plot3_square(ax, mean_position.reshape((1,3)), color='k')
    plt.show()

    ## ESTIMATE PROJECTOR'S FOCAL WIDTH ##
    # Grab a couple pairs of to measure the angle between.
    unique_2d_array = np.array(unique_2d).reshape((-1, 2))
    wt_all_array = np.array(wt_all).reshape((-1, 3))

    wt_center = wt_all_array[(unique_2d_array[:,0] == 0) * (unique_2d_array[:,1] == 0)].flatten()
    all_angle_verticals = []
    for coords, wt in zip(unique_2d_array, wt_all_array):
        if coords[0] == 0 and coords[1] == 0:
            continue
        angle_vertical = 2. * np.arccos( np.abs(np.dot(wt_center, wt))) / np.linalg.norm(coords)
        print(coords, angle_vertical)
        all_angle_verticals.append(angle_vertical)

    all_angle_verticals = np.array(all_angle_verticals)

    angle_mean = np.mean(all_angle_verticals)
    print("Mean Vertical Angle: {0} degrees".format(np.degrees(angle_mean)))
    print("STD Vertical Angle: {0} degrees".format(np.degrees(np.std(all_angle_verticals))))
    print("STE Vertical Angle: {0} degrees".format(np.degrees(np.std(all_angle_verticals) / np.sqrt(len(all_angle_verticals)))))

    throw = 1. / (2. * np.tan(angle_mean * 16. / 9. / 2.))
    print("Horizontal Throw: {0}".format(throw))

    return tuple(mean_position), float(np.degrees(angle_mean))


if __name__ == '__main__':
    # Run the specified function from the command line. Format: arena_scanner function_name file_name

    propixx_utils.start_frame_sync_signal()

    print("Beginning Scan--Please Enter the Recording Chamber!")
    data = scan()

    print("Analyzing Data...")
    position, fov_y = analyze(data)

    print("Should this be data be saved as the projector values? (y/n)")
    input_registered = False
    while not input_registered:
        response = raw_input("Save? (Y/N): ")
        if 'y' in response.lower():
            input_registered = True
            projector_data = {'position': position, 'rotation': (-90, -90, 0), 'fov_y': 41.2 / 1.47}
            pickle.dump(projector_data, open(os.path.join(ratcave.data_dir, 'projector_data.pickle'), "wb"))
            print("Response: Y. Data saved to file projector_data.pickle")
        elif 'n' in response.lower():
            input_registered = True
            print("Response: N. Data not saved.")
        else:
            print("Response not recognized.  Looking for y or n.")








