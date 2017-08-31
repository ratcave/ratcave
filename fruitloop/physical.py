import abc
import numpy as np
import _transformations as trans
from fruitloop.utils import coordinates as rotutils
from fruitloop.utils import SceneGraph, AutoRegisterObserver, Observable
from fruitloop.utils import mixins

class Physical(AutoRegisterObserver, Observable, mixins.PickleableMixin):

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), scale=1., orientation0=(1., 0., 0.),
                 **kwargs):
        """XYZ Position, Scale and XYZEuler Rotation Class.

        Args:
            position: (x, y, z) translation values.
            rotation: (x, y, z) rotation values
            scale (float): uniform scale factor. 1 = no scaling.
        """
        super(Physical, self).__init__(**kwargs)

        self.orientation0 = np.array(orientation0, dtype=np.float32)
        self.rotation = rotutils.RotationEulerDegrees(*rotation)
        self.position = rotutils.Translation(*position)
        self.scale = rotutils.Scale(scale)

        self._model_matrix = np.identity(4, dtype=np.float32)
        self._normal_matrix = np.identity(4, dtype=np.float32)
        self._view_matrix = np.identity(4, dtype=np.float32)

    @property
    def model_matrix(self):
        if self._requires_update:
            self.update()
        return self._model_matrix

    @model_matrix.setter
    def model_matrix(self, value):
        self._model_matrix[:] = value

    @property
    def normal_matrix(self):
        if self._requires_update:
            self.update()
        return self._normal_matrix

    @normal_matrix.setter
    def normal_matrix(self, value):
        self._normal_matrix[:] = value

    @property
    def view_matrix(self):
        if self._requires_update:
            self.update()
        return self._view_matrix

    @view_matrix.setter
    def view_matrix(self, value):
        self._view_matrix[:] = value

    @property
    def orientation0(self):
        """Starting orientation (3-element unit vector). New orientations are calculated by rotating from this vector."""
        return self._orientation0

    @orientation0.setter
    def orientation0(self, vector):
        assert len(vector) == 3
        self._orientation0 = trans.unit_vector(vector)

    @property
    def orientation(self):
        """The object's orientation as a vector, calculated by rotation from orientation0, the starting orientation."""
        if self._requires_update:
            self.update()
        return self.rotation.rotate(self.orientation0)

    @orientation.setter
    def orientation(self, vec):
        # From algorithm at http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d/897677#897677
        rot_mat = rotutils.rotation_matrix_between_vectors(self.orientation0, vec)
        self.rotation = self.rotation.from_matrix(rot_mat)

    def update(self):
        """Calculate model, normal, and view matrices from position, rotation, and scale data."""
        to_update = super(Physical, self).update()
        if to_update:
            # Update Model, View, and Normal Matrices
            self.model_matrix = np.dot(self.position.to_matrix(), self.rotation.to_matrix())
            self.view_matrix = trans.inverse_matrix(self.model_matrix)
            self.model_matrix = np.dot(self.model_matrix, self.scale.to_matrix())
            self.normal_matrix = trans.inverse_matrix(self.model_matrix.T)

            self.notify_observers()
        return to_update


class PhysicalGraph(Physical, SceneGraph):

    def __init__(self, **kwargs):
        """Object with xyz position and rotation properties that are relative to its parent."""
        super(PhysicalGraph, self).__init__(**kwargs)

        self._model_matrix_global = np.identity(4, dtype=np.float32)
        self._normal_matrix_global = np.identity(4, dtype=np.float32)
        self._view_matrix_global = np.identity(4, dtype=np.float32)

    @property
    def model_matrix_global(self):
        if self._requires_update:
            self.update()
        return self._model_matrix_global

    @model_matrix_global.setter
    def model_matrix_global(self, value):
        self._model_matrix_global[:] = value

    @property
    def normal_matrix_global(self):
        if self._requires_update:
            self.update()
        return self._normal_matrix_global

    @normal_matrix_global.setter
    def normal_matrix_global(self, value):
        self._normal_matrix_global[:] = value

    @property
    def view_matrix_global(self):
        if self._requires_update:
            self.update()
        return self._view_matrix_global

    @view_matrix_global.setter
    def view_matrix_global(self, value):
        self._view_matrix_global[:] = value

    def update(self):
        to_update = super(PhysicalGraph, self).update()

        """Calculate world matrix values from the dot product of the parent."""
        if to_update:
            if self.parent:
                self.model_matrix_global = np.dot(self.parent.model_matrix_global, self.model_matrix)
                self.normal_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
                self.view_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
            else:
                self.model_matrix_global = self.model_matrix
                self.normal_matrix_global = self.normal_matrix
                self.view_matrix_global = self.view_matrix
        return to_update

    @property
    def position_global(self):
        if self._requires_update:
            self.update()
        return tuple(self.model_matrix_global[:3, -1])

    @property
    def rotation_global(self):
        if self._requires_update:
            self.update()
        return self.rotation.from_matrix(self.model_matrix_global)

    @property
    def orientation_global(self):
        """Orientation vector, in world coordinates."""
        if self._requires_update:
            self.update()
        return self.rotation_global.rotate(self.orientation0)