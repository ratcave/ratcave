__author__ = 'nickdg'
import os
import cv2

import time
import numpy as np
import progressbar as pb

import ratcave
import ratcave.graphics as gg
import ratcave.utils as utils

import motive

from ratcave.utils import plot_3d, timers

from psychopy import event

np.set_printoptions(precision=3, suppress=True)


def setup_projcal_window():
    """Returns Window with everything needed for doing projector calibration."""

    # Setup graphics

    wavefront_reader = gg.WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0., 0., -1.], scale=.008)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = gg.Scene([circle])
    scene.camera.ortho_mode = True
    window = gg.Window(scene, screen=1, fullscr=True)

    return window

def slow_draw(window, sleep_time=.05):
        """Draws the window contents to screen, then blocks until tracker data updates."""
        window.draw()
        window.flip()
        time.sleep(sleep_time)


def random_scan(window, n_points=300):

    circle = window.active_scene.meshes[0]
    screenPos, pointPos = [], []
    collect_fmt, missed_fmt, missed_cnt = ", Points Collected: ", ", Points Missed: ", 0
    pbar = pb.ProgressBar(widgets=[pb.Bar(), pb.ETA(), collect_fmt +'0', missed_fmt+'0'], maxval=n_points)
    pbar.start()
    while len(pointPos) < n_points and 'escape' not in event.getKeys():

        # Update position of circle, and draw.
        circle.visible = True
        homogenous_pos = np.random.random(2) - .5
        circle.local.x, circle.local.y = homogenous_pos * [1.8, 1]
        slow_draw(window)
        motive.update()

        # Try to isolate a single point.
        for _ in timers.countdown_timer(.2, stop_iteration=True):
            motive.update()
            markers = motive.get_unident_markers()
            if markers and markers[0][1] > 0.:
                screenPos.append(circle.local.position[:2])
                # Update Progress Bar
                pointPos.append(markers[0])
                pbar.widgets[2] = collect_fmt + str(len(pointPos))
                pbar.update(len(pointPos))
                break
        else:
            # Update Progress bar
            missed_cnt += 1
            pbar.widgets[3] = missed_fmt + str(missed_cnt)
            pbar.update(len(pointPos))

        # Hide circle, and wait again for a new update.
        circle.visible = False
        slow_draw(window)
        motive.update()
        while len(motive.get_unident_markers()) > 0:
            motive.update()

    return np.array(screenPos), np.array(pointPos)


def ray_scan(window):

    circle = window.active_scene.meshes[0]
    circle.visible = True

    # Do some non-random points to so human can change height range.
    pointPos, screenPos = [], []
    for pos in [(0, 0), (-.5, 0), (.5, 0)]:
        circle.local.x, circle.local.y = pos
        window.draw()
        window.flip()
        for _ in timers.countdown_timer(5, stop_iteration=True):
            motive.update()
            markers = motive.get_unident_markers()
            old_time = motive.frame_time_stamp()
            if motive.frame_time_stamp() > old_time + .3 and len(markers) == 1:
                if markers[0][1] > 0.1:
                    screenPos.append(circle.local.position[:2])
                    pointPos.append(markers[0])
                    old_time = motive.frame_time_stamp()

    return screenPos, pointPos


def calibrate(img_points, obj_points):
    """
    Returns position and rotation arrays by using OpenCV's camera calibration function on image calibration data.

    Args:
        -img_points (Nx2 NumPy Array): the location (-.5 - .5) of the center of the point that was projected on the
            projected image.
        -obj_points (Nx3 NumPy Array): the location (x,y,z) in real space where the projected point was measured.
            Note: Y-axis is currently hardcoded to represent the 'up' direction.

    Returns:
        -posVec (NumPy Array): The X,Y,Z position of the projector
        -rotVec (NumPy Array): The Euler3D rotation of the projector (in degrees).
    """
    img_points *= -1
    _, cam_mat, _, rotVec, posVec = cv2.calibrateCamera([obj_points.astype('float32')],
                                                                            [img_points.astype('float32')],  # V-axis is downward in image coordinates.  Maybe U axisu should be, too?
                                                                            (1,1),  # Currently a false window size. # TODO: Get cv2.calibrateCamera to return correct intrinsic parameters.
                                                                            flags=cv2.CALIB_USE_INTRINSIC_GUESS |  # Estimates camera matrix without a guess given.
                                                                                  cv2.CALIB_FIX_PRINCIPAL_POINT |  # Assumes 0 lens shift
                                                                                  cv2.CALIB_FIX_ASPECT_RATIO | # Assumes equal height/width aspect ratio
                                                                                  cv2.CALIB_ZERO_TANGENT_DIST | # Assumes zero tangential distortion
                                                                                  cv2.CALIB_FIX_K1 |  # Assumes 0 radial distortion for each K coefficient (6 in total)
                                                                                  cv2.CALIB_FIX_K2 |
                                                                                  cv2.CALIB_FIX_K3 |
                                                                                  cv2.CALIB_FIX_K4 |
                                                                                  cv2.CALIB_FIX_K5 |
                                                                                  cv2.CALIB_FIX_K6)

    # Change order of coordinates from cv2's camera-centered coordinates to Optitrack y-up coords.
    pV, rV = posVec[0], rotVec[0]

    # Return the position array and rotation matrix for the camera.
    position = -np.dot(pV.T, cv2.Rodrigues(rV)[0]).flatten()  # Invert the position by the rotation to be back in world coordinates
    rotation_matrix = cv2.Rodrigues(rV)[0]

    return position, rotation_matrix


if __name__ == '__main__':

    import pickle
    import argparse

    app_data_file = os.path.join(ratcave.data_dir, 'projector_data_points')

    # Get command line inputs
    parser = argparse.ArgumentParser(description='Projector Calibration script. Projects a random dot pattern and calculates projector position.')

    parser.add_argument('-i', action='store', dest='load_filename', default=app_data_file,
                        help='Calibrate using this datafile instead of collecting data directly.  Should be a pickled file containing a '
                             'single dictionary with two keys: imgPoints (Nx2 array) and objPoints (Nx3 array).')

    parser.add_argument('-o', action='store', dest='save_filename', default='',
                        help='Pickle file to store point data to, if desired.')

    parser.add_argument('-m', action='store', dest='motive_projectfile', default=motive.utils.backup_project_filename,
                        help='Name of the motive project file to load.  If not used, will load most recent Project file loaded in MotivePy.')

    parser.add_argument('-t', action='store_true', dest='test_mode', default=False,
                        help='If this flag is present, calibration results will be displayed, but not saved.')

    parser.add_argument('-d', action='store_true', dest='debug_mode', default=False,
                        help='If this flag is present, scanning will be skipped.')

    parser.add_argument('-n', action='store', type=int, dest='n_points', default=250,
                        help='Number of Data Points to Collect.')

    parser.add_argument('-v', action='store_true', dest='human_scan', default=False,
                        help='This flag adds an extra stationary step where the experimenter can add some vertical lines of points to improve the projector estimate.')

    parser.add_argument('--fov_y', action='store', type=float, dest='fov_y', default=27.8,
                        help='Vertical field of view for the projector.  If known, please specify. (currently defaults with assumption of 1080x720 mode for ProPixx projector.')

    parser.add_argument('--silent', action='store_true', dest='silent_mode', default=False,
                        help='Silent mode.  Suppresses console output.')

    parser.add_argument('--noplot', action='store_true', dest='no_plotting', default=False,
                        help='This flag turns off result plotting, which normally blocks further code execution.')

    args = parser.parse_args()

    # Get Data from Tracker scanning or from a pickled file.
    if not args.debug_mode:

        # Setup Graphics
        window = setup_projcal_window()

        # If the experimenter needs to enter the room, give them a bit of time to get inside.
        if args.human_scan:
            time.sleep(5)

        # Collect random points for calibration.
        motive.load_project(args.motive_projectfile)
        utils.motive_camera_vislight_configure()

        screenPos, pointPos = random_scan(window, n_points=args.n_points)

        print("Size of Point Data: {}".format(pointPos.shape))

        # Remove Obviously Bad Points according to how far away from main cluster they are
        histmask = np.ones(pointPos.shape[0], dtype=bool)  # Initializing mask with all True values
        for coord in range(3):
            histmask &= utils.hist_mask(pointPos[:, coord], keep='middle')
        pointPos = pointPos[histmask, :]
        screenPos = screenPos[histmask, :]

        print("Size of Point Data after hist_mask: {}".format(pointPos.shape))

        # Project a few points that the experimenter can make rays from (by moving a piece of paper up and down along them.
        # Don't include human data, because its non-gaussian distribution can screw things up a bit.
        # TODO: Figure out how to properly get human-scanned projector calibration data in so OpenCV gets better estimate.
        if args.human_scan:
            ray_scan(window)

        # Close Window
        window.close()

        # Early Tests
        if len(pointPos) == 0:
            raise IOError("Only {} Points collected. Please check camera settings and try for more points.".format(len(pointPos)))
        assert len(screenPos) == len(pointPos), "Length of two paired lists doesn't match."

        # If specified, save the data.
        save_files = []
        save_files = save_files + [app_data_file] if not args.test_mode else save_files
        save_files = save_files + [args.save_filename] if args.save_filename else save_files
        for filename in save_files:
            with open(filename, 'wb') as myfile:
                pickle.dump({'imgPoints': screenPos, 'objPoints': pointPos}, myfile)
                if not args.silent_mode:
                    print('Saved to: {}'.format(os.path.splitext(filename)[0] + '.pickle'))

    # Else, get the data from file.
    else:
        with open(args.load_filename) as datafile:
            data = pickle.load(datafile)
            assert isinstance(data, dict) and 'imgPoints' in data.keys() and 'objPoints' in data.keys(), "Loaded Datafile in wrong format. See help for more info."
            screenPos, pointPos = data['imgPoints'], data['objPoints']

    # Calibrate projector data
    position, rotation = calibrate(screenPos, pointPos)
    if not args.silent_mode:
        print('\nEstimated Projector Position:\n\t{}\nEstimated Projector Rotation:\n{}\n'.format(position, rotation))

    # Save Results to application data.
    if not args.test_mode:
        # Save Data in format for putting into a ratcave.graphics.Camera
        projector_data = {'position': position, 'rotation': rotation, 'fov_y': args.fov_y}
        with open(os.path.join(ratcave.data_dir, 'projector_data.pickle'), "wb") as datafile:
            pickle.dump(projector_data, datafile)

    ## Plot Data
    if not args.no_plotting:
        ax = plot_3d(pointPos, square_axis=True)

        # Plot and Check that vector position and direction is generally correct, and give tips if not.
        cam_dir = np.dot([0, 0, -1], rotation) # Rotate from -Z vector (default OpenGL camera direction)
        data_dir = np.mean(pointPos, axis=0) - position
        data_dir /= np.linalg.norm(data_dir)
        if not args.silent_mode:
            if np.dot(cam_dir, data_dir) < .4 or position[1] < 0.:
                print("Warning: Estimated Projector Position and/or Rotation not pointing in right direction.\n\t"
                      "Please try to change the projector's 'ceiling mount mode' to off and try again.\n\t"
                      "ex) Propixx VPutil Command: cmm off\n\t"
                      "Also, could be the projection front/rear mode.  Normally should be set to front projection, but if\n\t "
                      "reflecting off of a mirror, should be set to rear projection.\n\t"
                      "ex) Propixx VPutil Command: pm r")

        rot_vec = np.vstack((position, position+cam_dir))
        plot_3d(rot_vec, ax=ax, color='r', line=True)
        plot_3d(np.array([position]), ax=ax, color='g', show=True)