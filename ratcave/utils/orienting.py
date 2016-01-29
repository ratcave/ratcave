__author__ = 'ratcave'

import numpy as np
from .. import _transformations as transformations


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
