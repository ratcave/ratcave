__author__ = 'ratcave'

import numpy as np
from sklearn.decomposition import PCA

def rotate_to_var(markers):
    """Returns degrees to rotate about y axis so greatest marker variance points in +X direction"""

    # Mean-Center
    markers -= np.mean(markers, axis=0)

    # Vector in direction of greatest variance
    pca = PCA(n_components=1).fit(markers[:, [0, 2]])
    coeff_vec = pca.components_[0]


    # # Flip coeff_vec in direction of max variance along the vector.
    # marker_var = markers[markers[:,2].argsort(), 2]  # Check variance along component to determine whether to flip.
    # winlen = int(len(marker_var)/2+1)  # Window length for moving mean (two steps, with slight overlap)
    # var_means = np.array([marker_var[:winlen], marker_var[-winlen:]]).mean(axis=1)
    # coeff_vec = coeff_vec * -1 if np.diff(var_means)[0] < 0 else coeff_vec

    # Rotation amount, in radians
    base_vec = np.array([1, 0])  # Vector in +X direction
    msin, mcos = np.cross(coeff_vec, base_vec), np.dot(coeff_vec, base_vec)
    angle = np.degrees(np.arctan2(msin, mcos))
    print("Angle within function: {}".format(angle))
    return angle

# def get_pca_rotation(markers):
#
#     markers_2d = markers[:, [0, 2]]
#     pca = PCA(n_components=1).fit(markers[:, [0, 2]])
#
#     coeff = pca.components_[0]



