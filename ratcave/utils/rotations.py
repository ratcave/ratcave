import numpy as np
import _transformations as trans
from abc import ABCMeta, abstractmethod

class RotationBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __repr__(self): pass

    @abstractmethod
    def to_quaternion(self): pass

    @abstractmethod
    def to_euler(self, order='zyx', units='rad'): pass

    @abstractmethod
    def to_matrix(self): pass


class RotationEuler(RotationBase):

    def __init__(self, x, y, z, order='xyz'):
        self.data = np.array((x, y, z), dtype=float)
        self.order = order

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('xyz', self.data)])
        return "{cls}({coords}, order='{order}')".format(cls=self.__class__.__name__, coords=arg_str, order=self.order)


class RotationEulerRadians(RotationEuler):

    def to_degrees(self):
        return RotationEulerDegrees(*np.degrees(self.data), order=self.order)

    def to_quaternion(self):
        quatdata = trans.quaternion_from_euler(*self.data, axes='r' + self.order)
        return RotationQuaternion(*quatdata)

    def to_euler(self, order='zyx', units='rad'):
        assert units.lower() in ['rad', 'deg']

        if units.lower() == 'rad':
            return RotationEulerRadians(*self.data, order=order)
        else:
            return RotationEulerDegrees(*np.degrees(self.data), order=order)

    def to_matrix(self):
        return trans.euler_matrix(*self.data, axes='r' + self.order)


class RotationEulerDegrees(RotationEuler):

    def to_radians(self):
        return RotationEulerRadians(*np.radians(self.data), order=self.order)

    def to_quaternion(self):
        return self.to_radians().to_quaternion()

    def to_euler(self, order='zyx', units='rad'):
        return self.to_radians().to_euler(order=order, units=units)

    def to_matrix(self):
        return self.to_radians().to_matrix()


class RotationQuaternion(RotationBase):

    def __init__(self, x, y, z, w):
        self.data = np.array((x, y, z, w), dtype=float)

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('xyzw', self.data)])
        return self.__class__.__name__ + '(' + arg_str + ')'

    def to_quaternion(self):
        return self

    def to_euler(self, order='rzyx', units='rad'):
        euler_data = trans.euler_from_matrix(self.to_matrix(), axes='r' + order)
        assert units.lower() in ['rad', 'deg']
        if units.lower() == 'rad':
            return RotationEulerRadians(*euler_data, order=order)
        else:
            return RotationEulerDegrees(*np.degrees(euler_data), order=order)

    def to_matrix(self):
        return trans.quaternion_matrix(self.data)
    


class Translation(object):

    def __init__(self, x, y, z):
        self.data = np.array((x, y, z), dtype=float)

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('xyz', self.data)])
        return self.__class__.__name__ + '(' + arg_str + ')'

    def to_matrix(self):
        return trans.translation_matrix(self.data)

