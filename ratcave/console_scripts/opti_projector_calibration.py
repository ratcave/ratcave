__author__ = 'nickdg'

import numpy as np
import os

from psychopy import event, core

import ratcave
from ratcave.devices import Optitrack
import ratcave.graphics as gg

np.set_printoptions(precision=3, suppress=True)

vert_dist = 0.66667



def scan(optitrack_ip="127.0.0.1"):

    import progressbar as pb

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
    wavefront_reader = gg.WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0., 0., -1.], scale=.01)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = gg.Scene([circle])
    scene.camera.ortho_mode = True

    window = gg.Window(scene, screen=1, fullscr=True)

    # Main Loop
    screenPos, pointPos = [], []
    clock = core.CountdownTimer(60)
    max_markers = 300
    collect_fmt, missed_fmt, missed_cnt = ", Points Collected: ", ", Points Missed: ", 0
    pbar = pb.ProgressBar(widgets=[pb.Bar(), pb.ETA(), collect_fmt +'0', missed_fmt+'0'], maxval=max_markers)
    pbar.start()
    while clock.getTime() > 0. and len(pointPos) < max_markers and 'escape' not in event.getKeys():

        # Update position of circle, and draw.
        circle.visible = True
        circle.local.position[[0, 1]] = np.random.random(2) - .5
        slow_draw(window, tracker)

        # Try to isolate a single point.
        search_clock = core.CountdownTimer(.05)
        while search_clock.getTime() > 0.:
            markers = tracker.unidentified_markers
            if len(markers) == 1:
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
        #window.draw()
        #window.flip()
        slow_draw(window, tracker)

    # Close Window
    window.close()

    # Early Tests
    if len(pointPos) == 0:
        raise IOError("Only {} Points collected. Please check camera settings and try for more points.".format(len(pointPos)))
    assert len(screenPos) == len(pointPos), "Length of two paired lists doesn't match."

    # Return Data
    return np.array(screenPos), np.array(pointPos), window.size


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
    import cv2

    img_points, obj_points = img_points.astype('float32'), obj_points.astype('float32')
    window_size = (1000,1000)  # Currently a false size. # TODO: Get cv2.calibrateCamera to return correct intrinsic parameters.

    retVal, cameraMatrix, distortion_coeffs, rotVec, posVec = cv2.calibrateCamera([obj_points],
                                                                                  [img_points],
                                                                                  window_size,
                                                                                  flags=cv2.CALIB_USE_INTRINSIC_GUESS |  # Estimates camera matrix without a guess given.
                                                                                        cv2.CALIB_FIX_PRINCIPAL_POINT |  # Assumes 0 lens shift
                                                                                        cv2.CALIB_FIX_ASPECT_RATIO  # Assumees equal height/width aspect ratio
                                                                                  )

    # Change order of coordinates from cv2's camera-centered coordinates to Optitrack y-up coords.
    coord_order = [0,2,1]
    posVec, rotVec = posVec[0][coord_order], rotVec[0][coord_order]
    assert posVec[1] > 0, "Projector height estimated to be below floor.  Please make sure projector is set to front-projection mode and try again."
    rotVec = np.degrees(rotVec)  # TODO: Check what the rotation order is.
    print("cameraMatrix is: {}".format(cameraMatrix))
    # Return the position and rotation arrays for the camera.
    return posVec.flatten(), rotVec.flatten()

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

    args = parser.parse_args()

    # Collect data or get data from file
    if not args.load_filename:
        screenPos, pointPos, winSize = scan()
    else:
        with open(args.load_filename) as datafile:
            data = pickle.load(datafile)
            assert isinstance(data, dict), "loaded datafile should contain a single dict!"
            assert 'imgPoints' in data.keys() and 'objPoints' in data.keys(), "loaded datafile's dict has wrong keys."
            screenPos, pointPos = data['imgPoints'], data['objPoints']

    # If specified, save the data.
    if args.save_filename:
        print('Saving Acquisition data to {}'.format(args.save_filename))
        with open(args.save_filename, 'wb') as myfile:
            pickle.dump({'imgPoints': screenPos, 'objPoints': pointPos}, myfile)

    # Filter out points below floor surface (happens with reflections sometimes)
    reflect_mask = np.where(pointPos[:, 1] > 0.)[0]
    pointPos, screenPos = pointPos[reflect_mask, :], screenPos[reflect_mask, :]

    # Calibrate projector data
    print('Estimating Extrinsic Camera Parameters...')
    position, rotation = calibrate(screenPos, pointPos)
    print('Estimated Projector Position:{}'.format(position))
    print('Estimated Projector Rotation:{}'.format(rotation))

    # Estimate vector direction camera is pointing when rotated from -Z vector (default OpenGL direction)
    rot_vec, rot_fun = np.array([[0,0,-1]]).T, gg._transformations.rotation_matrix
    rot_vec = np.dot(rot_fun(np.radians(rotation[2]), [0, 0, 1])[:3,:3], rot_vec)
    rot_vec = np.dot(rot_fun(np.radians(rotation[1]), [0, 1, 0])[:3,:3], rot_vec)
    rot_vec = np.dot(rot_fun(np.radians(rotation[0]), [1, 0, 0])[:3,:3], rot_vec)

    # Check that vector direction is generally correct, and give a tip if not to change ceiling-mount mode on the projector.
    cam_dir = rot_vec.flatten() / np.linalg.norm(rot_vec.flatten())
    data_dir = np.mean(pointPos, axis=0) - position
    data_dir /= np.linalg.norm(data_dir)
    if np.dot(cam_dir, data_dir) < .5:
        print("Warning: Estimated Projector Rotation not pointing in right direction.\n\t"
              "Please try to change the projector's 'ceiling mount mode' and try again.")


    rot_vec = np.vstack((position, position+rot_vec.flatten()))

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

    print('Calibration Complete!')


