__author__ = 'nickdg'

import os
import time
import ratcave
from ratcave.devices.optitrack import Optitrack
from ratcave.graphics import *
from ratcave.graphics import utils
import numpy as np
import sys
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from scipy import stats
import pdb
from psychopy import event, core



np.set_printoptions(precision=3, suppress=True)

def scan(optitrack_ip="127.0.0.1"):
    """Project a series of points onto the arena, collect their 3d position, and save them and the associated
    rigid body data into a pickled file."""


    # Check that cameras are in correct configuration (only visible light, no LEDs on, in Segment tracking mode, everything calibrated)
    tracker = Optitrack(client_ip=optitrack_ip)
    assert "Arena" in tracker.rigid_bodies, "Must Add Arena Rigid Body in Motive!"
    wavefront_reader = WavefrontReader(ratcave.graphics.resources.obj_primitives)
    circle = wavefront_reader.get_mesh('Sphere', centered=True, lighting=False, position=[0, 0, -1], scale=.007)
    circle.material.diffuse.rgb = 1, 1, 1  # Make white

    scene = Scene(circle)
    scene.camera.ortho_mode = True

    window = Window(scene, screen=1, fullscr=True)

    #start drawing.
    data = {'markerPos': [], 'bodyPos': [], 'bodyRot': [], 'screenPos': []}
    clock = core.CountdownTimer(5 * 60)
    while ('escape' not in event.getKeys()) and clock.getTime() > 0:

        # Draw Circle
        circle.visible = False if circle.visible == True else True  # Switch visible to True and False alternately.
        circle.xy = np.random.uniform(-1.2, 1.2), np.random.uniform(-.85, .85)  # Change circle position to a random one.
        window.draw()
        window.flip()

        time.sleep(.032)

        new_position = tracker.get_unidentified_positions(1)
        if new_position:

            # Try to get Arena rigid body and a single unidentified marker
            body = tracker.get_rigid_body('Arena')

            # If successful, add the new position to the list.
            feedback = bool(new_position and body)
            if feedback:
                data['markerPos'].append(new_position[0])
                data['bodyPos'].append(body.position)
                data['bodyRot'].append(body.rotation)
                data['screenPos'].append(circle.xy)
        else:
            print("No point detected.")

    window.close()
    return data


def normal_nearest_neighbors(data, n_neighbors=40, min_dist_filter=.04):
    """Find the normal direction of a hopefully-planar cluster of n_neighbors"""

    # K-Nearest neighbors on whole dataset
    nbrs = NearestNeighbors(n_neighbors).fit(data)
    distances, indices = nbrs.kneighbors(data)

    # PCA on each cluster of k-nearest neighbors
    latent_all, normal_all = [], []
    for dist_array, idx_array in zip(distances, indices):

        # Filter out huge distances for outliers:
        if np.min(dist_array) > min_dist_filter:
            continue

        pp = PCA(n_components=3).fit(data[idx_array, :]) # Perform PCA

         # Get the percent variance of each component
        latent_all.append(pp.explained_variance_ratio_)

        # Get the normal of the plane along the third component (flip if pointing in -y direction)
        normal = pp.components_[2] if pp.components_[2][1] > 0 else -pp.components_[2]
        normal_all.append(normal)

    # Convert to NumPy Array and return
    return np.array(normal_all), np.array(latent_all)


def meshify(data, filename):

    ## IMPORT DATA ##
    # Put values of data dictionary into numpy arrays.
    body_positions, body_rotations = np.array(data['bodyPos']), np.array(data['bodyRot'])
    data = np.array(data['markerPos'])

    # Assume normally-ish distributed position and rotation data, and get mean body data after removing outliers.
    fig = plt.figure()
    plt.hist(body_positions - np.mean(body_positions, axis=0), bins=40)

    # Plot raw marker data as 3D Scatterplot
    fig = plt.figure()
    ax = fig.add_subplot(221, projection='3d')
    lims = utils.plot3_square(ax, data)


    ## REMOVE OUTLIERS ##
    # Remove Obviously Bad Points according to Height
    data = data[(-.02 < data[:, 1]) * (data[:, 1] < .52), :]  # 1.2

    # Filter out data that's not within a clear plane (mainly corners and outliers)
    planarity_threshold = .005  # 1 is 100%.  Let's take all below 0.5% (super planar)
    normals, explained_variances = normal_nearest_neighbors(data)
    data =       data[explained_variances[:, 2] < planarity_threshold, :]
    normals = normals[explained_variances[:, 2] < planarity_threshold, :]


    ## CLUSTER INTO SEPARATE WALL PLANES ##
    # Label Markers by Clustering of their normals
    radius = .3
    distance = lambda dd, cent: np.sqrt(np.sum((dd-cent)**2, axis=1))
    data_clustered = []  # List of clustered data
    for wall in range(5):
        # Cluster from a random point
        print(normals.shape)
        center = normals[np.random.randint(0, len(normals)), :]
        mask = distance(normals, center) < radius
        data_clustered.append(data[mask, :])  # Position, normal

        # Remove already-clustered data from the list to be clustered
        normals = normals[mask == False, :]  # Normals
        data = data[mask == False, :]  # Positional coordinates

    # Plot Box with labeled Sides
    ax = fig.add_subplot(222, projection='3d')
    for data, color in zip(data_clustered, 'rgybm'):
        utils.plot3_square(ax, data, color, lims=lims)

    ## CALCULATE WALL NORMAL AND CENTER ##
    normals, offsets = [], []
    ax = fig.add_subplot(223, projection='3d')
    for data in data_clustered:
        # First, Remove outliers in plane to get more robust fit
        rotate = lambda dd: PCA(n_components=3).fit(dd).transform(dd)
        rotated_data = rotate(data)
        rd = rotated_data[:,2]
        mean, std, threshold = np.mean(rd), np.std(rd), 1.5
        mask = (mean - (threshold * std) < rd) * (rd < (mean + (threshold *std)))
        data = data[mask, :]

        # Plot residual map
        cmhot = plt.cm.get_cmap("bwr")
        ax.scatter(data[:,0], data[:,1], data[:,2], zdir='y', c=rotate(data)[:,2], cmap=cmhot, vmin=-.002, vmax=.002)

        # Repeat PCA on remaining data, get normal from coeffs and offset from mean.
        nn = PCA(n_components=3).fit(data).components_[2]
        nn = nn if nn[1] > 0 else -nn
        normals.append(nn)
        offsets.append(np.mean(data, axis=0))

    normals, offsets = np.array(normals), np.array(offsets)

    ## CALCULATE PLANE INTERSECTIONS TO GET VERTICES ##
    # Want equation in form ax + by + cz = d.  So, get d from norm and offsets
    d = np.sum(normals * offsets, axis=1)

    # Find floor plane
    floor_mask = normals[:,1] == normals[:,1].max()
    floor_normal, floor_dd = normals[floor_mask, :], d[floor_mask]
    wall_mask = floor_mask == False
    wall_normals, wall_dd = normals[wall_mask, :], d[wall_mask]

    ceiling_norm, ceiling_dd = np.array([0., 1., 0.]), .6  # TODO: Have it auto-find highest point.

    #
    num_walls = 4
    floor_verts, ceiling_verts = np.zeros((num_walls, 3)), np.zeros((num_walls, 3))
    floor_vertnorms = np.zeros((num_walls, 3))
    ceil_vertnorms = np.zeros((num_walls, 3))
    idx = 0
    wn, wd = wall_normals[0], wall_dd[0]
    while idx < 4:
        # Find nearest wall to the left by finding two nearest wall normals (distance), and the positive y cross product
        distance = lambda x, xx: np.sqrt(np.sum((x-xx)**2, axis=1))
        yy = distance(wn, wall_normals)
        mask = (stats.rankdata(yy) > 1) * (stats.rankdata(yy) < 4)
        cross_prod = np.cross(wn, wall_normals[mask])
        adj_wall_idx = np.where(mask)[0][np.where(cross_prod[:,1]>0)[0]]  # Complicated, but works.  Fix later.
        adj_wall_norm, adj_wall_dd = wall_normals[adj_wall_idx], wall_dd[adj_wall_idx]

        # Calculate intersection of this wall with adjacent wall and floor.
        def find_intersection((wn1, wn2, wn3), (d1, d2, d3)):
            """Solve system of 3 Equations to get intersection point between three planes."""
            abc_mat, d_mat = np.vstack((wn1, wn2, wn3)), np.vstack((d1, d2, d3))
            return np.linalg.solve(abc_mat, d_mat).transpose()

        print (wn, adj_wall_norm, floor_normal)
        floor_intersection = find_intersection((wn, adj_wall_norm, floor_normal), (wd, adj_wall_dd, floor_dd))

        ceil_intersection = find_intersection((wn, adj_wall_norm, ceiling_norm), (wd, adj_wall_dd, ceiling_dd))

        floor_verts[idx, :] = floor_intersection
        ceiling_verts[idx, :] = ceil_intersection

        # Find average direction of the intersecting planes for the vertex (essential for a short normal list)
        normalize = lambda x: x/ np.sqrt(np.sum(x**2))
        fvn = normalize(wn + adj_wall_norm + floor_normal)
        cvn = normalize(wn + adj_wall_norm)
        floor_vertnorms[idx, :] = fvn
        ceil_vertnorms[idx, :] = cvn

        wn, wd = adj_wall_norm, adj_wall_dd
        idx +=1

    ## BUILD VERTEX, NORMAL, AND FACE INDICES FROM VERTEX DATA ##

    # Build quad face index list
    quad_faces = []
    quad_faces.append([0, 1, 2, 3])  # Add the floor first, to match normals order!
    for idx in range(len(floor_verts)):  # Add all the walls
        idx2 = idx+1 if idx<len(floor_verts)-1 else 0
        quad_faces.append([idx, idx2, len(floor_verts)+idx2, len(floor_verts)+idx])


    # Make new vertex and normals lists, so they match the face_indices order (will be unncecessaryily long
    vertices = np.vstack((floor_verts, ceiling_verts)) - np.mean(body_positions, axis=0)
    normals = np.vstack((floor_normal, wall_normals))

    ## WRITE WAVEFRONT .OBJ FILE FOR IMPORTING INTO BLENDER ##
    with open(filename, 'wb') as wavfile:

        header = "# Blender v2.69 (sub 5) OBJ File: ''\n" + "# www.blender.org\n" + "o Arena\n"
        wavfile.write(header)

        for vert in vertices:
            vertline = "v {0} {1} {2} \n".format(*vert)
            wavfile.write(vertline)

        for norm in normals:
            normline = "vn {0} {1} {2}\n".format(norm[0], norm[1], norm[2])
            wavfile.write(normline)

        for idx, face in enumerate(quad_faces):
            faceline = 'f'
            for f in face:
                faceline += r" {f}//{n}".format(f=f+1, n=idx+1)
            faceline += '\n'
            wavfile.write(faceline)


    # Make final plot with drawing of reconstructed object.
    ax = fig.add_subplot(224, projection='3d')
    for face_inds, color in zip(quad_faces, 'rgybm'):
        data = np.vstack((vertices[face_inds, :], vertices[face_inds[0], :]))
        utils.plot3_square(ax, data, color+':', lims=lims)

    plt.show()


if __name__ == '__main__':
    # Run the specified function from the command line. Format: arena_scanner function_name file_name
    print("Starting the Scan Process...")
    data = scan()
    pdb.set_trace()
    print("Analyzing and Saving to {0}".format(ratcave.data_dir))
    meshify(data, filename=os.path.join(ratcave.data_dir, 'arena_unprocessed.obj'))
    print("Save done.  Please import file into blender and export as arena.obj before using in experiments!")

