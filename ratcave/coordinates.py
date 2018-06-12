import numpy as np
import _transformations as trans
from abc import ABCMeta, abstractmethod
from ratcave.utils.observers import IterObservable
import itertools
from operator import setitem

class Coordinates(IterObservable):

    coords = {'x': 0, 'y': 1, 'z': 2}

    def __init__(self, *args, **kwargs):
        " Returns a Coordinates object"
        super(Coordinates, self).__init__(**kwargs)
        self._array = np.array(args, dtype=np.float32)
        self._init_coord_properties()

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('xyz', self._array)])
        return "{cls}({coords})".format(cls=self.__class__.__name__, coords=arg_str)

    def _init_coord_properties(self):
        """
        Generates combinations of named coordinate values, mapping them to the internal array.
        For Example: x, xy, xyz, y, yy, zyx, etc
        """
        def gen_getter_setter_funs(*args):
            indices = [self.coords[coord] for coord in args]

            def getter(self):
                return tuple(self._array[indices]) if len(args) > 1 else self._array[indices[0]]

            def setter(self, value):
                setitem(self._array, indices, value)
                self.notify_observers()

            return getter, setter

        for n_repeats in range(1, len(self.coords)+1):
            for args in itertools.product(self.coords.keys(), repeat=n_repeats):
                getter, setter = gen_getter_setter_funs(*args)
                setattr(self.__class__, ''.join(args), property(fget=getter, fset=setter))

    def __getitem__(self, item):
        if type(item) == slice:
            return tuple(self._array[item])
        else:
            return self._array[item]

    def __setitem__(self, idx, value):
        self._array[idx] = value
        super(Coordinates, self).__setitem__(idx, value)


class RotationBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_quaternion(self): pass

    @abstractmethod
    def to_euler(self, units='rad'): pass

    @abstractmethod
    def to_matrix(self): pass

    @classmethod
    def from_matrix(cls, matrix): pass

    def rotate(self, vector):
        """Takes a vector and returns it rotated by self."""
        return np.dot(self.to_matrix()[:3, :3], vector).flatten()


class RotationEuler(RotationBase, Coordinates):

    def __init__(self, x, y, z, axes='rxyz', **kwargs):
        super(RotationEuler, self).__init__(x, y, z, **kwargs)
        self.axes = axes


class RotationEulerRadians(RotationEuler):

    def to_radians(self):
        return self

    def to_degrees(self):
        return RotationEulerDegrees(*np.degrees(self._array), axes=self.axes)

    def to_quaternion(self):
        return RotationQuaternion(*trans.quaternion_from_euler(*self._array, axes=self.axes))

    def to_matrix(self):
        return trans.euler_matrix(*self._array, axes=self.axes)

    def to_euler(self, units='rad'):
        assert units.lower() in ['rad', 'deg']
        if units.lower() == 'rad':
            return RotationEulerRadians(*self._array, axes=self.axes)
        else:
            return RotationEulerDegrees(*np.degrees(self._array), axes=self.axes)

    @classmethod
    def from_matrix(cls, matrix, axes='rxyz'):
        # Change to 4x4 if 3x3 rotation matrix is given
        if matrix.shape[0] == 3:
            mat = np.identity(4)
            mat[:3, :3] = matrix
            matrix = mat
        coords = trans.euler_from_matrix(matrix, axes=axes)
        return cls(*coords)



class RotationEulerDegrees(RotationEuler):
    def to_radians(self):
        return RotationEulerRadians(*np.radians(self._array), axes=self.axes)

    def to_degrees(self):
        return self

    def to_quaternion(self):
        return self.to_radians().to_quaternion()

    def to_euler(self, units='rad'):
        return self.to_radians().to_euler(units=units)

    def to_matrix(self):
        return self.to_radians().to_matrix()

    @classmethod
    def from_matrix(cls, matrix, axes='rxyz'):
        # Change to 4x4 if 3x3 rotation matrix is given
        if matrix.shape[0] == 3:
            mat = np.identity(4)
            mat[:3, :3] = matrix
            matrix = mat
        coords = trans.euler_from_matrix(matrix, axes=axes)
        return cls(*np.degrees(coords))


class RotationQuaternion(RotationBase, Coordinates):

    coords = {'w': 0, 'x': 1, 'y': 2, 'z': 3}

    def __init__(self, w, x, y, z, **kwargs):
        super(RotationQuaternion, self).__init__(w, x, y, z)

    def __repr__(self):
        arg_str = ', '.join(['{}={}'.format(*el) for el in zip('wxyz', self._array)])
        return "{cls}({coords})".format(cls=self.__class__.__name__, coords=arg_str)

    def to_quaternion(self):
        return self

    def to_matrix(self):
        return trans.quaternion_matrix(self._array)

    def to_euler(self, units='rad'):
        euler_data = trans.euler_from_matrix(self.to_matrix(), axes='rxyz')
        assert units.lower() in ['rad', 'deg']
        if units.lower() == 'rad':
            return RotationEulerRadians(*euler_data)
        else:
            return RotationEulerDegrees(*np.degrees(euler_data))

    @classmethod
    def from_matrix(cls, matrix):
        # Change to 4x4 if 3x3 rotation matrix is given
        if matrix.shape[0] == 3:
            mat = np.identity(4)
            mat[:3, :3] = matrix
            matrix = mat
        coords = trans.quaternion_from_matrix(matrix)
        return cls(*coords)


class Translation(Coordinates):

    def __init__(self, *args, **kwargs):
        assert len(args) == 3, "Must be xyz coordinates"
        super(Translation, self).__init__(*args, **kwargs)

    def __add__(self, other):
        oth = other.xyz if isinstance(other, Translation) else other
        if len(oth) != 3:
            raise ValueError("Other must have length of 3")
        return Translation(*tuple(a + b for (a, b) in zip(self.xyz, oth)))

    def __sub__(self, other):
        oth = other.xyz if isinstance(other, Translation) else other
        if len(oth) != 3:
            raise ValueError("Other must have length of 3")
        return Translation(*tuple(a - b for (a, b) in zip(self.xyz, other.xyz)))

    def to_matrix(self):
        return trans.translation_matrix(self._array)


class Scale(Coordinates):

    def __init__(self, *args, **kwargs):
        vals = args * 3 if len(args) == 1 else args
        assert len(vals) == 3, "Must be xyz coordinates"
        super(self.__class__, self).__init__(*vals, **kwargs)

    def to_matrix(self):
        return np.diag((self._array[0], self._array[1], self._array[2], 1.))



def cross_product_matrix(vec):
    """Returns a 3x3 cross-product matrix from a 3-element vector."""
    return np.array([[0, -vec[2], vec[1]],
                     [vec[2], 0, -vec[0]],
                     [-vec[1], vec[0], 0]])


def rotation_matrix_between_vectors(from_vec, to_vec):
    """
    Returns a rotation matrix to rotate from 3d vector "from_vec" to 3d vector "to_vec".
    Equation from https://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
    """
    a, b = (trans.unit_vector(vec) for vec in (from_vec, to_vec))

    v = np.cross(a, b)
    cos = np.dot(a, b)
    if cos == -1.:
        raise ValueError("Orientation in complete opposite direction")
    v_cpm = cross_product_matrix(v)
    rot_mat = np.identity(3) + v_cpm + np.dot(v_cpm, v_cpm) * (1. / 1. + cos)
    return rot_mat
