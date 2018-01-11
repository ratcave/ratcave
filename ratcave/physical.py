import _transformations as trans

import numpy as np
import pyglet.gl as gl

from . import coordinates
from .utils import AutoRegisterObserver
from .utils import mixins
from .scenegraph import SceneGraph


class Physical(AutoRegisterObserver):

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
        self.rotation = coordinates.RotationEulerDegrees(*rotation)
        self.position = coordinates.Translation(*position)
        if hasattr(scale, '__iter__'):
            self.scale = coordinates.Scale(*scale)
        else:
            self.scale = coordinates.Scale(scale)

        self._model_matrix = np.identity(4, dtype=np.float32)
        self._normal_matrix = np.identity(4, dtype=np.float32)
        self._view_matrix = np.identity(4, dtype=np.float32)
        self.update()

    @property
    def model_matrix(self):
        return self._model_matrix

    @model_matrix.setter
    def model_matrix(self, value):
        self._model_matrix[:] = value

    @property
    def normal_matrix(self):
        return self._normal_matrix

    @normal_matrix.setter
    def normal_matrix(self, value):
        self._normal_matrix[:] = value

    @property
    def view_matrix(self):
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
        return self.rotation.rotate(self.orientation0)

    @orientation.setter
    def orientation(self, vec):
        mat = (gl.GLfloat * 16)()
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.gluLookAt(0., 0., 0., vec[0], vec[1], vec[2], 0, 1, 0)
        gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, mat)
        gl.glPopMatrix()
        mat = np.array(mat).reshape(4, 4)
        # rot_mat = rotutils.rotation_matrix_between_vectors(self.orientation0, vec)
        self.rotation = self.rotation.from_matrix(mat[:3, :3])

    def look_at(self, x, y, z):
        """Rotate so orientation is toward (x, y, z) coordinates."""
        new_ori = x - self.position.x, y - self.position.y, z - self.position.z
        self.orientation = new_ori / np.linalg.norm(new_ori)

    def on_change(self):
        self.model_matrix = np.dot(self.position.to_matrix(), self.rotation.to_matrix())
        self.view_matrix = trans.inverse_matrix(self.model_matrix)
        self.model_matrix = np.dot(self.model_matrix, self.scale.to_matrix())
        self.normal_matrix = trans.inverse_matrix(self.model_matrix.T)


class PhysicalGraph(Physical, SceneGraph):

    def __init__(self, **kwargs):
        """Object with xyz position and rotation properties that are relative to its parent."""
        self._model_matrix_global = np.identity(4, dtype=np.float32)
        self._normal_matrix_global = np.identity(4, dtype=np.float32)
        self._view_matrix_global = np.identity(4, dtype=np.float32)
        super(PhysicalGraph, self).__init__(**kwargs)


    @property
    def model_matrix_global(self):
        return self._model_matrix_global

    @model_matrix_global.setter
    def model_matrix_global(self, value):
        self._model_matrix_global[:] = value

    @property
    def normal_matrix_global(self):
        return self._normal_matrix_global

    @normal_matrix_global.setter
    def normal_matrix_global(self, value):
        self._normal_matrix_global[:] = value

    @property
    def view_matrix_global(self):
        return self._view_matrix_global

    @view_matrix_global.setter
    def view_matrix_global(self, value):
        self._view_matrix_global[:] = value

    def on_change(self):
        Physical.on_change(self)
        if self.parent:
            self.model_matrix_global = np.dot(self.parent.model_matrix_global, self.model_matrix)
            self.normal_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
            self.view_matrix_global = np.dot(self.parent.normal_matrix_global, self.normal_matrix)
        else:
            self.model_matrix_global = self.model_matrix
            self.normal_matrix_global = self.normal_matrix
            self.view_matrix_global = self.view_matrix

    @property
    def position_global(self):
        return tuple(self.model_matrix_global[:3, -1])

    @property
    def rotation_global(self):
        return self.rotation.from_matrix(self.model_matrix_global)

    @property
    def orientation_global(self):
        """Orientation vector, in world coordinates."""
        return self.rotation_global.rotate(self.orientation0)