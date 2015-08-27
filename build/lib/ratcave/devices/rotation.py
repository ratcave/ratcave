import numpy as np
import transformations

class Euler(object):

    def __init__(self, angles, order='XYZ'):
        if order != 'XYZ':
            raise NotImplementedError("Currently only support XYZ order for Euler Angles, Sorry!")
        self.x, self.y, self.z = angles
        self._order = order

    def to_matrix(self):
        transformations.euler_matrix(self.x, self.y, self.z, axes='sxyz')

    def to_quaternion(self):
        transformations.quaternion_from_euler(self.x, self.y, self.z, axes='sxyz')


