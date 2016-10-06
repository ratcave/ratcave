__author__ = 'ratcave'

import numpy as np
import _transformations as transformations


def calculate_model_matrix(position, rotation, scale):
    """Returns 4x4 model matrix from the (x.y,z) position and XYZ Euler rotation, in degrees."""

    # Set Model and Normal Matrices
    trans_mat = transformations.translation_matrix(position)

    rotation = tuple(np.radians(coord) for coord in rotation)
    rot_mat = transformations.euler_matrix(rotation[0], rotation[1], rotation[2])
    scale_mat = transformations.scale_matrix(scale)

    return np.dot(np.dot(trans_mat, rot_mat), scale_mat)


def calculate_view_matrix(position, rotation):
    """TReturns 4x4 view matrix from the (x.y,z) position and XYZ Euler rotation, in degrees."""
    # Set View Matrix

    trans_mat = transformations.translation_matrix((-position[0], -position[1], -position[2]))

    rotation = tuple(-np.radians(coord) for coord in rotation)
    rot_mat = transformations.euler_matrix(rotation[0], rotation[1], rotation[2], 'rxyz')

    return np.dot(rot_mat, trans_mat)
