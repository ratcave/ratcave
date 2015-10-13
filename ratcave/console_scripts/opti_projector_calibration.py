__author__ = 'nickdg'

import numpy as np
import os

from psychopy import event, core

import ratcave
from ratcave.devices import Optitrack
import ratcave.graphics as gg
import cv2
from ratcave.devices import propixx_utils

np.set_printoptions(precision=3, suppress=True)
import time
import progressbar as pb
import copy

vert_dist = 0.66667

def slow_draw(window, tracker):
        """Draws the window contents to screen, then blocks until tracker data updates."""
        window.draw()
        window.flip()

        # Wait for tracker to update, just to be safe and align all data together.
        old_frame = tracker.iFrame
        while tracker.iFrame == old_frame:
            pass

        #time.sleep(.02)

def setup_projcal_window():
    """Returns Window with everything needed for doing projector calibration."""

    # Setup graphics
    propixx_utils.start_frame_sync_signal()
    wavefront_reader = gg.WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0., 0., -1.], scale=.004)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = gg.Scene([circle])
    scene.camera.ortho_mode = True
    window = gg.Window(scene, screen=1, fullscr=True)

    time.sleep(2)

    return window

def random_scan(window, tracker, n_points=300):

    circle = window.active_scene.meshes[0]
    screenPos, pointPos = [], []
    collect_fmt, missed_fmt, missed_cnt = ", Points Collected: ", ", Points Missed: ", 0
    pbar = pb.ProgressBar(widgets=[pb.Bar(), pb.ETA(), collect_fmt +'0', missed_fmt+'0'], maxval=n_points)
    pbar.start()
    while len(pointPos) < n_points and 'escape' not in event.getKeys():

        # Update position of circle, and draw.
        circle.visible = True
        circle.local.position[[0, 1]] = np.random.random(2) - .5
        slow_draw(window, tracker)

        # Try to isolate a single point.
        search_clock = core.CountdownTimer(.05)
        while search_clock.getTime() > 0.:
            markers = copy.deepcopy(tracker.unidentified_markers)
            if len(markers) == 1 and markers[0].position[1] > 0.:
                screenPos.append(circle.local.position[[0, 1]])
                # Updatae Progress Bar
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
    pointPos, screenPos = [], []

    # Do some non-random points to so human can change height range.
    point_positions = [(0,0)]#, (.8, 0), (-.8, 0), (0, .4), (0, -.4)]
    circle.visible = True

    for pp in point_positions:
        circle.local.position[[0, 1]] = pp
        window.draw()
        window.flip()
        old_frame = tracker.iFrame
        clock = core.CountdownTimer(5)
        while clock.getTime() > 0.:
            markers = copy.deepcopy(tracker.unidentified_markers)
            if tracker.iFrame > old_frame + 5 and len(markers) == 1:
                if markers[0].position[1] > 0.3:
                    if abs(markers[0].position[0]) < .4 and abs(markers[0].position[2]) < .4:
                        screenPos.append(circle.local.position[[0, 1]])
                        pointPos.append(markers[0].position)
                        old_frame = tracker.iFrame

    return screenPos, pointPos

def scan(n_points=300, window=None, keep_open=False):


    # Setup Graphics
    if window is None:
        window = setup_projcal_window()

    # Check that cameras are in correct configuration (only visible light, no LEDs on, in Segment tracking mode, everything calibrated)
    optitrack_ip = "127.0.0.1"
    tracker = Optitrack(client_ip=optitrack_ip)

    screenPos, pointPos = random_scan(window, tracker, n_points=n_points)
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


def plot_3d(array3d, title='', ax=None, line=False, color='', square_axis=False, show=False):
    """
    Make 3D scatterplot that plots the x, y, and z columns in a dataframe. Returns figure.

    Args:
        -array3d (Nx3 Numpy Array): data to plot.
        -ax (PyPlot Axis Object=None): Axis object to use.
        -line (bool=True):Whether to plot with lines instead of just points
        -color (str=''): the color to set.
        -square_axis (bool=False): Whether to square the axes to fit the data.
        -show (bool=False): Whether to immediately show the figure.  This is a blocking operation.

    Returns:
        -ax (PyPlot Axis Object): The Axis the data is plotted on.
    """

    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    if square_axis:
        tot_range = (array3d.max(axis=0) - array3d.min(axis=0)).max() * .55
        mn = array3d.mean(axis=0, keepdims=True) - tot_range
        mx = array3d.mean(axis=0, keepdims=True) + tot_range
        limits = np.vstack([mn, mx]).transpose()
        for coord, idx in zip('xyz', range(3)):
            getattr(ax, 'set_{0}lim3d'.format(coord))(limits[idx])

    plot_fun = ax.plot if line else ax.scatter
    if color:
        plot_fun(array3d[:,0], array3d[:,2], array3d[:,1], color=color)
    else:
        plot_fun(array3d[:,0], array3d[:,2], array3d[:,1])
    plt.title(title)
    plt.xlabel('x'), plt.ylabel('z')

    # Immediately display figure is show is True
    if show:
        plt.show()

    return ax



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

    retVal, cameraMatrix, distortion_coeffs, rotVec, posVec = cv2.calibrateCamera([obj_points.astype('float32')],
                                                                                  [-img_points.astype('float32')],  # V-axis is downward in image coordinates.  Maybe U axisu should be, too?
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
                                                                                        cv2.CALIB_FIX_K6
                                                                                  )


    # Change order of coordinates from cv2's camera-centered coordinates to Optitrack y-up coords.
    position = -np.dot(posVec[0].T, cv2.Rodrigues(rotVec[0])[0])  # Invert the position by the rotation to be back in world coordinates
    rotation = np.degrees(-np.dot(cv2.Rodrigues(rotVec[0])[0], rotVec[0]))

    # Return the position and rotation arrays for the camera.
    return position.flatten(), rotation.flatten()



if __name__ == '__main__':

    import pickle

    # Get command line inputs
    import argparse
    parser = argparse.ArgumentParser(description='Projector Calibration script. Projects a random dot pattern and calculates projector position.')

    parser.add_argument('-i',
                        action='store',
                        dest='load_filename',
                        default='',
                        help='Calibrate using this datafile instead of collecting data directly.  Should be a pickled file containing a '
                             'single dictionary with two keys: imgPoints (Nx2 array) and objPoints (Nx3 array).')

    parser.add_argument('-o',
                        action='store',
                        dest='save_filename',
                        default='',
                        help='Pickle file to store point data to, if desired.')

    parser.add_argument('-t',
                        action='store_true',
                        dest='test_mode',
                        default=False,
                        help='If this flag is present, calibration results will be displayed, but not saved.')

    parser.add_argument('-d',
                        action='store_true',
                        dest='debug_mode',
                        default=False,
                        help='If this flag is present, no scanning will occur, but the last collected data will be used for calibration.')

    parser.add_argument('-n',
                        action='store',
                        type=int,
                        dest='n_points',
                        default=300,
                        help='Number of Data Points to Collect.')

    args = parser.parse_args()

    # Collect data and save to app directory or get data from file
    if not args.load_filename and not args.debug_mode:
        screenPos, pointPos, winSize = scan(n_points=args.n_points) # Collect data
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
    cam_dir = np.dot(cv2.Rodrigues(np.radians(rotation))[0], np.array([[0,0,-1]]).T).flatten()  # Rotate from -Z vector (default OpenGL camera direction)
    data_dir = np.mean(pointPos, axis=0) - position
    data_dir /= np.linalg.norm(data_dir)
    if np.dot(cam_dir, data_dir) < .4 or position[1] < 0.:
        print("Warning: Estimated Projector Position and/or Rotation not pointing in right direction.\n\t"
              "Please try to change the projector's 'ceiling mount mode' to off and try again.\n"
              "ex) Propixx VPutil Command: cmm off\n"
              "Also, could be the projection front/rear mode.  Normally should be set to front projection, but if\n "
              "reflecting off of a mirror, should be set to rear projection.\n"
              "ex) Propixx VPutil Command: pm r")

    # Plot Estimated camera position and rotation.
    rot_vec = np.vstack((position, position+cam_dir))
    ax = plot_3d(pointPos, square_axis=True)
    plot_3d(rot_vec, ax=ax, color='r', line=True)

    plot_3d(np.array([position]), ax=ax, color='g', show=True)

    # Save Results to application data.
    if not args.test_mode:
        print('Saving Results...')
        # Save Data in format for putting into a ratcave.graphics.Camera
        projector_data = {'position': position, 'rotation': rotation, 'fov_y': 41.2 / 1.47}
        with open(os.path.join(ratcave.data_dir, 'projector_data.pickle'), "wb") as datafile:
            pickle.dump(projector_data, datafile)

