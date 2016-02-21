from __future__ import absolute_import
import numpy as np
import pickle
from . import utils


class Physical(object):

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), scale=1., *args, **kwargs):
        """XYZ Position, Scale and XYZEuler Rotation Class.

        Args:
            position (list): (x, y, z) translation values.
            rotation (list): (x, y, z) rotation values
            scale (float): uniform scale factor. 1 = no scaling.
        """
        super(Physical, self).__init__(*args, **kwargs)
        self.x, self.y, self.z = position
        self.rot_x, self.rot_y, self.rot_z = rotation
        self._rot_matrix = None
        self.scale = scale
        self.model_matrix = np.zeros((4,4))
        self.normal_matrix = np.zeros((4,4))
        self.view_matrix = np.zeros((4,4))
        self.model_matrix_global = np.zeros((4,4))
        self.normal_matrix_global = np.zeros((4,4))
        self.view_matrix_global = np.zeros((4,4))

        self.update_matrices()

    @property
    def position(self):
        """xyz position"""
        return self.x, self.y, self.z

    @position.setter
    def position(self, value):
        self.x, self.y, self.z = value

    @property
    def rotation(self):
        """XYZ Euler rotation, in degrees"""
        return self.rot_x, self.rot_y, self.rot_z

    @rotation.setter
    def rotation(self, value):
        self.rot_x, self.rot_y, self.rot_z = value

    def update_matrices(self):
        self.model_matrix = utils.orienting.calculate_model_matrix(self.position, self.rotation, self.scale)
        self.normal_matrix = np.linalg.inv(self.model_matrix.T)
        self.view_matrix = utils.orienting.calculate_view_matrix(self.position, self.rotation)

    def update_matrices_global(self):
        self.model_matrix_global = self.model_matrix.copy()
        self.normal_matrix_global = self.normal_matrix.copy()
        self.view_matrix_global = self.view_matrix.copy()

    def start(self, *args, **kwargs):
        """Interface for implementing physics. Subclassed Physical objects can take advantage of this."""
        raise NotImplementedError()

    def update(self, dt):
        """Interface for implementing physics. Subclassed Physical objects can take advantage of this."""
        raise NotImplementedError()


root = Physical()

class PhysicalNode(Physical):

    def __init__(self, *args, **kwargs):
        super(PhysicalNode, self).__init__(*args, **kwargs)
        self.update_matrices()

    def update_matrices_global(self):
        self.model_matrix_global = np.dot(self.parent.model_matrix_global, self.model_matrix)
        self.normal_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
        self.view_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)

    @property
    def position_global(self):
        self.update_matrices()
        return tuple(self.model_matrix_global[:3, -1].tolist())


class Picklable(object):

    def save(self, filename):
        """Save the object to a file.  Will be Pickled in the process, but can be loaded easily with Class.load()"""
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filename):
        with open(filename) as f:
            obj = pickle.load(f)
        return obj
