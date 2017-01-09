import abc
import numpy as np
import _transformations as trans
from .utils import rotations as rotutils
from .utils import SceneNode, AutoRegisterObserver


class Physical(AutoRegisterObserver):

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), scale=1.,
                 **kwargs):
        """XYZ Position, Scale and XYZEuler Rotation Class.

        Args:
            position: (x, y, z) translation values.
            rotation: (x, y, z) rotation values
            scale (float): uniform scale factor. 1 = no scaling.
        """
        super(Physical, self).__init__(**kwargs)

        self.rotation = rotutils.RotationEulerDegrees(*rotation)
        self.position = rotutils.Translation(*position)
        self.scale = rotutils.Scale(scale)

        self.model_matrix = np.zeros((4, 4))
        self.normal_matrix = np.zeros((4, 4))
        self.view_matrix = np.zeros((4, 4))

        self.update()

    def update(self):
        """Calculate model, normal, and view matrices from position, rotation, and scale data."""
        super(Physical, self).update()

        # Update Model, View, and Normal Matrices
        self.model_matrix[:] = np.dot(self.position.to_matrix(), self.rotation.to_matrix())
        self.view_matrix[:] = trans.inverse_matrix(self.model_matrix)
        self.model_matrix[:] = np.dot(self.model_matrix, self.scale.to_matrix())
        self.normal_matrix[:] = trans.inverse_matrix(self.model_matrix.T)


class PhysicalNode(Physical, SceneNode):

    def __init__(self, **kwargs):
        """Object with xyz position and rotation properties that are relative to its parent."""
        self.model_matrix_global = np.zeros((4, 4))
        self.normal_matrix_global = np.zeros((4, 4))
        self.view_matrix_global = np.zeros((4, 4))
        super(PhysicalNode, self).__init__(**kwargs)

    def update(self):
        super(PhysicalNode, self).update()

        """Calculate world matrix values from the dot product of the parent."""
        if self.parent:
            self.model_matrix_global[:] = np.dot(self.parent.model_matrix_global, self.model_matrix)
            self.normal_matrix_global[:] = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
            self.view_matrix_global[:] = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
        else:
            self.model_matrix_global[:] = self.model_matrix
            self.normal_matrix_global[:] = self.normal_matrix
            self.view_matrix_global[:] = self.view_matrix

    @property
    def position_global(self):
        return tuple(self.model_matrix_global[:3, -1].tolist())


class PhysicalCompositeBase(object):
    """
    An object that is composed of a Physical object, with the Physical object as an 'obj' attribute.
    Provides shortcut properties to position, rotation, and scale methods to reduce apparant nesting in the interface.
    """
    __metaclass__ = abc.ABCMeta

    def update(self):
        self.obj.update()

    @property
    def position(self):
        return self.obj.position.xyz

    @position.setter
    def position(self, value):
        self.obj.position.xyz = value

    @property
    def x(self):
        return self.obj.position.x

    @x.setter
    def x(self, value):
        self.obj.position.x = value

    @property
    def y(self):
        return self.obj.position.y

    @y.setter
    def y(self, value):
        self.obj.position.y = value

    @property
    def z(self):
        return self.obj.position.z

    @z.setter
    def z(self, value):
        self.obj.position.z = value

    @property
    def rotation(self):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        return self.obj.rotation.xyz

    @rotation.setter
    def rotation(self, value):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        self.obj.rotation.xyz = value

    @property
    def rot_x(self):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        return self.obj.rotation.x

    @rot_x.setter
    def rot_x(self, value):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        self.obj.rotation.x = value

    @property
    def rot_y(self):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        return self.obj.rotation.y

    @rot_y.setter
    def rot_y(self, value):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        self.obj.rotation.y = value

    @property
    def rot_z(self):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        return self.obj.rotation.z

    @rot_z.setter
    def rot_z(self, value):
        assert isinstance(self.obj.rotation, rotutils.RotationEulerDegrees)
        self.obj.rotation.z = value

    @property
    def scale(self):
        return self.obj.scale[0]

    @scale.setter
    def scale(self, value):
        self.obj.scale[0] = value


class PhysicalComposite(PhysicalCompositeBase):

    def __init__(self, **kwargs):
        self.obj = Physical(**kwargs)


class PhysicalNodeComposite(PhysicalCompositeBase):

    def __init__(self, **kwargs):
        self.obj = PhysicalNode(**kwargs)