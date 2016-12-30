import numpy as np
import _transformations as trans
from abc import ABCMeta, abstractmethod


class Coordinates(object):

    def __init__(self, *args):
        self._data = np.array(args, dtype=float)

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('xyzw', self._data)])
        return "{cls}({coords})".format(cls=self.__class__.__name__, coords=arg_str)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, idx, value):
        self._data[idx] = value

    @property
    def x(self):
        return self._data[0]

    @x.setter
    def x(self, value):
        self._data[0] = value

    @property
    def y(self):
        return self._data[1]

    @y.setter
    def y(self, value):
        self._data[1] = value

    @property
    def z(self):
        return self._data[2]

    @z.setter
    def z(self, value):
        self._data[2] = value


class RotationBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_quaternion(self): pass

    @abstractmethod
    def to_euler(self, units='rad'): pass

    @abstractmethod
    def to_matrix(self): pass



class RotationEuler(RotationBase, Coordinates):

    axes = 'rxyz'

    def __init__(self, x, y, z, **kwargs):
        super(RotationEuler, self).__init__(x, y, z, **kwargs)


class RotationEulerRadians(RotationEuler):

    def to_radians(self):
        return self

    def to_degrees(self):
        return RotationEulerDegrees(*np.degrees(self._data))

    def to_quaternion(self):
        return RotationQuaternion(*trans.quaternion_from_euler(*self._data, axes=self.axes))

    def to_matrix(self):
        return trans.euler_matrix(*self._data, axes=self.axes)

    def to_euler(self, units='rad'):
        assert units.lower() in ['rad', 'deg']
        if units.lower() == 'rad':
            return RotationEulerRadians(*self._data)
        else:
            return RotationEulerDegrees(*np.degrees(self._data))


class RotationEulerDegrees(RotationEuler):
    def to_radians(self):
        return RotationEulerRadians(*np.radians(self._data))

    def to_degrees(self):
        return self

    def to_quaternion(self):
        return self.to_radians().to_quaternion()

    def to_euler(self, units='rad'):
        return self.to_radians().to_euler(units=units)

    def to_matrix(self):
        return self.to_radians().to_matrix()


class RotationQuaternion(RotationBase, Coordinates):

    def __init__(self, x, y, z, w, **kwargs):
        super(RotationQuaternion, self).__init__(x, y, z, w)

    def to_quaternion(self):
        return self

    def to_matrix(self):
        return trans.quaternion_matrix(self._data)

    def to_euler(self, units='rad'):
        euler_data = trans.euler_from_matrix(self.to_matrix(), axes=RotationEuler.axes)
        assert units.lower() in ['rad', 'deg']
        if units.lower() == 'rad':
            return RotationEulerRadians(*euler_data)
        else:
            return RotationEulerDegrees(*np.degrees(euler_data))

    @property
    def w(self):
        return self._data[3]

    @w.setter
    def w(self, value):
        self._data[3] = value


class Translation(Coordinates):

    def to_matrix(self):
        return trans.translation_matrix(self._data)

