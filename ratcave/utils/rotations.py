import numpy as np
import _transformations as trans
from abc import ABCMeta, abstractmethod

class ChangeTracker(object):

    def __init__(self, *args, **kwargs):
        super(ChangeTracker, self).__init__()
        self._has_changed = False

    def __setitem__(self, *args, **kwargs):
        self._has_changed = True

    def ping_change(self):
        """Returns self.has_changed, then immediately sets it to False"""
        status, self._has_changed = self._has_changed, False
        return status



class Coordinates(ChangeTracker):

    def __init__(self, *args):
        super(Coordinates, self).__init__(*args)
        self._data = np.array(args, dtype=float)

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('xyzw', self._data)])
        return "{cls}({coords})".format(cls=self.__class__.__name__, coords=arg_str)

    def __getitem__(self, item):
        if type(item) == slice:
            return tuple(self._data[item])
        else:
            return self._data[item]

    def __setitem__(self, idx, value):
        super(Coordinates, self).__setitem__(idx, value)
        self._data[idx] = value

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    @property
    def xyz(self):
        return self[:3]

    @xyz.setter
    def xyz(self, value):
        self[:3] = value


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
        return self[3]

    @w.setter
    def w(self, value):
        self[3] = value

    @property
    def xyzw(self):
        return self[:4]

    @xyzw.setter
    def xyzw(self, value):
        self[:4] = value


class Translation(Coordinates):

    def to_matrix(self):
        return trans.translation_matrix(self._data)


class Scale(Coordinates):

    def to_matrix(self):
        return trans.scale_matrix(self._data[0])

    @property
    def y(self):
        return self[0]

    @y.setter
    def y(self, value):
        self[0] = value

    @property
    def z(self):
        return self[0]

    @z.setter
    def z(self, value):
        self[0] = value

    @property
    def xyz(self):
        return self[0]

    @xyz.setter
    def xyz(self, value):
        if hasattr(value, '__iter__'):
            assert value[0] == value[1] == value[2], "Scale doesn't yet support differing dimension values."
            self[0] = value[0]
        else:
            self[0] = value


