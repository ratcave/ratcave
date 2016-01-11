__author__ = 'ratcave'

import numpy as np
from sklearn.decomposition import PCA
from .. import _transformations as transformations

def rotate_to_var(markers):
    """Returns degrees to rotate about y axis so greatest marker variance points in +X direction"""

    # Mean-Center
    markers -= np.mean(markers, axis=0)

    # Vector in direction of greatest variance
    pca = PCA(n_components=2).fit(markers[:, [0, 2]])
    coeff_vec = pca.components_[0]

    # Flip coeff_vec in direction of max variance along the vector.
    markers_rotated = pca.fit_transform(markers)  # Rotate data to PCA axes.
    markers_reordered = markers_rotated[markers_rotated[:,0].argsort(), :]  # Reorder Markers to go along first component
    winlen = int(markers_reordered.shape[0]/2+1)  # Window length for moving mean (two steps, with slight overlap)
    var_means = [np.var(markers_reordered[:winlen, 1]), np.var(markers_reordered[-winlen:, 1])] # Compute variance for each half
    coeff_vec = coeff_vec * -1 if np.diff(var_means)[0] < 0 else coeff_vec  # Flip or not depending on which half if bigger.

    # Rotation amount, in radians
    base_vec = np.array([1, 0])  # Vector in +X direction
    msin, mcos = np.cross(coeff_vec, base_vec), np.dot(coeff_vec, base_vec)
    angle = np.degrees(np.arctan2(msin, mcos))
    print("Angle within function: {}".format(angle))
    return angle


def calculate_model_matrix(position, rotation, scale):
    """Returns 4x4 model matrix from the (x.y,z) position and XYZ Euler rotation, in degrees."""

    # Set Model and Normal Matrices
    trans_mat = transformations.translation_matrix(position)

    rot_x_mat = transformations.rotation_matrix(np.radians(rotation[0]), [1, 0, 0])
    rot_y_mat = transformations.rotation_matrix(np.radians(rotation[1]), [0, 1, 0])
    rot_z_mat = transformations.rotation_matrix(np.radians(rotation[2]), [0, 0, 1])
    rot_mat = np.dot(np.dot(rot_z_mat,rot_y_mat), rot_x_mat)

    scale_mat = transformations.scale_matrix(scale)

    return np.dot(np.dot(trans_mat, rot_mat), scale_mat)


def calculate_view_matrix(position, rotation):
    """TReturns 4x4 view matrix from the (x.y,z) position and XYZ Euler rotation, in degrees."""
    # Set View Matrix

    trans_mat = transformations.translation_matrix((-position[0], -position[1], -position[2]))

    rot_x_mat = transformations.rotation_matrix(np.radians(-rotation[0]), [1, 0, 0])
    rot_y_mat = transformations.rotation_matrix(np.radians(-rotation[1]), [0, 1, 0])
    rot_z_mat = transformations.rotation_matrix(np.radians(-rotation[2]), [0, 0, 1])
    rot_mat = np.dot(np.dot(rot_x_mat, rot_y_mat), rot_z_mat)

    return np.dot(rot_mat, trans_mat)
