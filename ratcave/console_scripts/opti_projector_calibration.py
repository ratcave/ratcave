__author__ = 'nickdg'
import os
import cv2

import time
import numpy as np
import progressbar as pb

import ratcave
import ratcave.graphics as gg
from ratcave.devices import Optitrack
from ratcave.utils import plot_3d, timers

from psychopy import event

np.set_printoptions(precision=3, suppress=True)

vert_dist = 0.66667


def slow_draw(window, tracker, sleep_mode=False):
        """Draws the window contents to screen, then blocks until tracker data updates."""
        window.draw()
        window.flip()

        # Wait for tracker to update, just to be safe and align all data together.
        old_frame = tracker.iFrame
        while tracker.iFrame == old_frame:
            pass

        if sleep_mode:
            time.sleep(.02)


def setup_projcal_window():
    """Returns Window with everything needed for doing projector calibration."""

    # Setup graphics

    wavefront_reader = gg.WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0., 0., -1.], scale=.004)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = gg.Scene([circle])
    scene.camera.ortho_mode = True
    window = gg.Window(scene, screen=1, fullscr=True)

    time.sleep(2)

    return window


def random_scan(window, tracker, n_points=300, sleep_mode=False):

    circle = window.active_scene.meshes[0]
    screenPos, pointPos = [], []
    collect_fmt, missed_fmt, missed_cnt = ", Points Collected: ", ", Points Missed: ", 0
    pbar = pb.ProgressBar(widgets=[pb.Bar(), pb.ETA(), collect_fmt +'0', missed_fmt+'0'], maxval=n_points)
    pbar.start()
    while len(pointPos) < n_points and 'escape' not in event.getKeys():

        # Update position of circle, and draw.
        circle.visible = True
        circle.local.position[[0, 1]] = np.random.random(2) - .5
        slow_draw(window, tracker, sleep_mode=sleep_mode)

        # Try to isolate a single point.
        for _ in timers.countdown_timer(.05, stop_iteration=True):
            markers = tracker.unidentified_markers[:]
            if len(markers) == 1 and markers[0].position[1] > 0.:
                screenPos.append(circle.local.position[[0, 1]])
                # Update Progress Bar
                pointPos.append(markers[0].position)
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
        slow_draw(window, tracker)

    return screenPos, pointPos


def ray_scan(window, tracker):

    circle = window.active_scene.meshes[0]
    circle.visible = True

    # Do some non-random points to so human can change height range.
    pointPos, screenPos = [], []
    for pos in [(0, 0), (-.5, 0), (.5, 0)]:
        circle.local.position[[0, 1]] = pos
        window.draw()
        window.flip()
        old_frame = tracker.iFrame
        for _ in timers.countdown_timer(5, stop_iteration=True):
            markers = tracker.unidentified_markers[:]
            if tracker.iFrame > old_frame + 5 and len(markers) == 1:
                if markers[0].position[1] > 0.3:
                    #if abs(markers[0].position[0]) < .4 and abs(markers[0].position[2]) < .4:
                    screenPos.append(circle.local.position[[0, 1]])
                    pointPos.append(markers[0].position)
                    old_frame = tracker.iFrame

    return screenPos, pointPos


def scan(n_points=300, window=None, keep_open=False, ray_on=False, sleep_mode=False):


    # Setup Graphics
    if window is None:
        window = setup_projcal_window()

    # Check that cameras are in correct configuration (only visible light, no LEDs on, in Segment tracking mode, everything calibrated)
    optitrack_ip = "127.0.0.1"
    tracker = Optitrack(client_ip=optitrack_ip)


    screenPos, pointPos = random_scan(window, tracker, n_points=n_points, sleep_mode=sleep_mode)

    if ray_on:
        sp2, pp2 = ray_scan(window, tracker)
        screenPos.extend(sp2)
        pointPos.extend(pp2)

    # Close Window
    if not keep_open:
        window.close()

    # Early Tests
    if len(pointPos) == 0:
        raise IOError("Only {} Points collected. Please check camera settings and try for more points.".format(len(pointPos)))
    assert len(screenPos) == len(pointPos), "Length of two paired lists doesn't match."

    # Alter data to fit position on screen
    screenPos, pointPos = np.array(screenPos), np.array(pointPos)

    # Return Data
    return screenPos, pointPos, window.size


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

    # Get command line inputs
    import argparse
    parser = argparse.ArgumentParser(description='Projector Calibration script. Projects a random dot pattern and calculates projector position.')

    parser.add_argument('-i', action='store', dest='load_filename', default='',
                        help='Calibrate using this datafile instead of collecting data directly.  Should be a pickled file containing a '
                             'single dictionary with two keys: imgPoints (Nx2 array) and objPoints (Nx3 array).')

    parser.add_argument('-o', action='store', dest='save_filename', default='',
                        help='Pickle file to store point data to, if desired.')

    parser.add_argument('-t', action='store_true', dest='test_mode', default=False,
                        help='If this flag is present, calibration results will be displayed, but not saved.')

    parser.add_argument('-d', action='store_true', dest='debug_mode', default=False,
                        help='If this flag is present, no scanning will occur, but the last collected data will be used for calibration.')

    parser.add_argument('-n', action='store', type=int, dest='n_points', default=300,
                        help='Number of Data Points to Collect.')

    parser.add_argument('-v', action='store_true', dest='human_scan', default=False,
                        help='This flag adds an extra stationary step where the experimenter can add some vertical lines of points to improve the projector estimate.')

    args = parser.parse_args()

    try:
        from ratcave.devices import propixx_utils
        propixx_utils.start_frame_sync_signal()
        sleep_mode = False
    except ImportError:
        print("Warning: No frame-sync method detected (only propixx currently supported.  Using time delays between frames to ensure tracker-display synchronization (a slower method)")
        sleep_mode = True

    # Collect data and save to app directory or get data from file
    if not args.load_filename and not args.debug_mode:
        screenPos, pointPos, winSize = scan(n_points=args.n_points, ray_on=args.human_scan, sleep_mode=sleep_mode) # Collect data
        with open(os.path.join(ratcave.data_dir, 'projector_data_points.pickle'), "wb") as datafile:
            pickle.dump({'imgPoints': screenPos, 'objPoints': pointPos}, datafile)  # Save data
    else:
        filename = os.path.join(ratcave.data_dir, 'projector_data_points.pickle') if args.debug_mode else args.load_filename
        with open(filename) as datafile:
            data = pickle.load(datafile)
            assert isinstance(data, dict), "loaded datafile should contain a single dict!"
            assert 'imgPoints' in data.keys() and 'objPoints' in data.keys(), "loaded datafile's dict has wrong keys."
            screenPos, pointPos = data['imgPoints'], data['objPoints']

    # If specified, save the data.
    if args.save_filename:
        args.save_filename = args.save_filename + '.pickle' if not os.path.splitext(args.save_filename)[1] else args.save_filename
        print('Saving Acquisition data to {}'.format(args.save_filename))
        with open(args.save_filename, 'wb') as myfile:
            pickle.dump({'imgPoints': screenPos, 'objPoints': pointPos}, myfile)

    # Calibrate projector data
    position, rotation = calibrate(screenPos, pointPos)
    print('Estimated Projector Position:{}\nEstimated Projector Rotation:{}'.format(position, rotation))

    # Check that vector position and direction is generally correct, and give tips if not.
    #cam_dir = np.dot(cv2.Rodrigues(np.radians(rotation))[0], np.array([[0,0,-1]]).T).flatten()  # Rotate from -Z vector (default OpenGL camera direction)
    from ratcave.devices.trackers import eulerangles
    #cam_dir = np.dot(eulerangles.euler2mat(np.radians(rotation)), np.array([[0,0,-1]])).flatten()
    data_dir = np.mean(pointPos, axis=0) - position
    data_dir /= np.linalg.norm(data_dir)
    # if np.dot(cam_dir, data_dir) < .4 or position[1] < 0.:
    #     print("Warning: Estimated Projector Position and/or Rotation not pointing in right direction.\n\t"
    #           "Please try to change the projector's 'ceiling mount mode' to off and try again.\n"
    #           "ex) Propixx VPutil Command: cmm off\n"
    #           "Also, could be the projection front/rear mode.  Normally should be set to front projection, but if\n "
    #           "reflecting off of a mirror, should be set to rear projection.\n"
    #           "ex) Propixx VPutil Command: pm r")

    # # Plot Estimated camera position and rotation.
    ax = plot_3d(pointPos, square_axis=True)

    # rot_vec = np.vstack((position, position+cam_dir))
    # plot_3d(rot_vec, ax=ax, color='r', line=True)

    plot_3d(np.array([position]), ax=ax, color='g', show=True)

    # Save Results to application data.
    if not args.test_mode:
        print('Saving Results...')
        # Save Data in format for putting into a ratcave.graphics.Camera
        projector_data = {'position': position, 'rotation': rotation, 'fov_y': 27.35}  # TODO: Un-hardcode the fov_y
        with open(os.path.join(ratcave.data_dir, 'projector_data.pickle'), "wb") as datafile:
            pickle.dump(projector_data, datafile)

import pdb
pdb.set_trace()