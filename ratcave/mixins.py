from __future__ import absolute_import
import numpy as np
import pickle
from . import utils
import collections

Color = collections.namedtuple('Color', 'r g b a')
Color.__new__.__defaults__ = (0., 0., 0., 1.)

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

    @property
    def model_matrix(self):
        """The 4x4 model matrix."""
        return utils.orienting.calculate_model_matrix(self.position, self.rotation, self.scale)

    @property
    def normal_matrix(self):
        """The 4x4 normal matrix, which is the inverse of the transpose of the model matrix."""
        return np.linalg.inv(self.model_matrix.T)

    @property
    def view_matrix(self):
        """The 4x4 view matrix."""
        return utils.orienting.calculate_view_matrix(self.position, self.rotation)

    def start(self, *args, **kwargs):
        """Interface for implementing physics. Subclassed Physical objects can take advantage of this."""
        raise NotImplementedError()

    def update(self, dt):
        """Interface for implementing physics. Subclassed Physical objects can take advantage of this."""
        raise NotImplementedError()


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
