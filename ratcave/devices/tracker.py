__author__ = 'nickdg'

import math
import pdb
import numpy as np
from sklearn.decomposition import PCA
from types import NoneType



class PositionMixin(object):

    def __init__(self):
        super(PositionMixin, self).__init__()
        self.x, self.y, self.z = (0, 0, 0)

    @property
    def position(self):
        return (self.x, self.y, self.z)

    @position.setter
    def position(self, value):
        if value is not None:
            self.x, self.y, self.z = value


class Marker(PositionMixin):

    def __init__(self, position=(0,0,0), name='', id=None, size=None):
        super(Marker, self).__init__()
        self.name = name
        self.id = id
        self.size = size
        self.position = position

        # Optitrack-Provided attributes for labelled markers.
        self.occluded = None
        self.pc_solved = None
        self.model_solved = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Marker at [{:3.2f}, {:3.2f}, {:3.2f}]".format(self.position[0], self.position[1], self.position[2])


class MarkerSet(object):

    def __init__(self, name='', id=None):
        self.name = name
        self.id = id
        self.markers = []


class RigidBody(PositionMixin):

    def __init__(self, name='', markers=[], id=None, parent_id=None, offset=(0., 0., 0.)):
        super(RigidBody, self).__init__()
        self.name = name
        self.id = id
        self.markers = markers
        self.error = None  # Mean marker error
        self.seen = True  # Indicates that Tracking was successful this frame.
        self.offset = offset  # (x, y, z) offset

        self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw = 0., 0., 0., 0.
        self._global_to_local_rotation_matrix = None

    @property
    def rot_x(self):
        return self.quaternion_to_euclid(self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw)[0]

    @property
    def rot_y(self):
        return self.quaternion_to_euclid(self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw)[1]

    @property
    def rot_z(self):
        return self.quaternion_to_euclid(self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw)[2]

    @property
    def rotation(self):
        return self.quaternion_to_euclid(self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw)

    @property
    def rotation_quaternion(self):
        return self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw

    @rotation_quaternion.setter
    def rotation_quaternion(self, value):
        self.rot_qx, self.rot_qy, self.rot_qz, self.rot_qw = np.array(value)/ np.linalg.norm(value)  # Normalized

    @property
    def rotation_local(self):
        """Performs the global-to-local rotation before giving local rotation"""
        if isinstance(self._global_to_local_rotation_matrix, NoneType):
            self._calc_local_y_orientation_transform()

        rot_quat = np.dot(self._global_to_local_rotation_matrix, np.array([self.rotation_quaternion[:3]]).T, ).flatten()

        return self.quaternion_to_euclid(rot_quat[0], rot_quat[1], rot_quat[2], 1.0)


    def quaternion_to_euclid(self, qx, qy, qz, qw):
        """Convert quaternion (qx, qy, qz, qw) angle to euclidean (x, y, z) angles, in degrees.
        Equation from http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/"""

        heading = math.atan2(2*qy*qw-2*qx*qz , 1 - 2*qy**2 - 2*qz**2)
        attitude = math.asin(2*qx*qy + 2*qz*qw)
        bank = math.atan2(2*qx*qw-2*qy*qz , 1 - 2*qx**2 - 2*qz**2)

        return [math.degrees(angle) for angle in [attitude, heading, bank]]  # TODO: May need to change some things to negative to deal with left-handed coordinate system.


    def _calc_local_y_orientation_transform(self):
        """
        Calculate which direction the rigid body is facing, based on a PCA of the markers, rather than the Optitrack's
        orientation report.  Useful for making a consistent orientation estimate when re-creating the same rigid body over
        multiple sessions. By default, only performs PCA in two dimensions (x and z).
        Returns nothing, but sets RigidBody._global_to_local_rotation_matrix
        """

        # Make an Nx3 array of marker positions
        marker_positions = []
        for marker in self.markers:
            marker_positions.append(marker.position)
        marker_positions = np.array(marker_positions)

        # Get PCA Coefficients (Represent Quaternion directions)
        coeffs = PCA(n_components=2).fit(marker_positions[:, (0, 2)]).components_[0]
        coeffs = -coeffs if coeffs[0] < 0 else coeffs  # Flip so that the first coord is always in positive direction

        # Normalize Vectors
        ll = np.array((coeffs[0], 0, coeffs[1]), dtype=float)
        gg = np.array((self.rot_qx,  0, self.rot_qz), dtype=float)

        for vec in [ll, gg]:
            vec /= np.linalg.norm(vec)

        # Calculate Rotation Matrix about the Y Axis
        ct, st = np.dot(ll, gg), np.cross(ll, gg)[1]
        rot_matrix = np.array([[ct, 0, st], [0, 1, 0], [-st, 0, ct]])

        # Set Matrix
        pdb.set_trace()
        self._global_to_local_rotation_matrix = rot_matrix



