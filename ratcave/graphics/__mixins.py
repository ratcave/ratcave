__author__ = 'nickdg'

import numpy as np
import transformations


class Physical(object):
    """Provides shortcut for adding position attributes and shortcut properties to objects whose xyz position
    must be specified."""

    def __init__(self, position=(0., 0., 0.), rotation=(0., 0., 0.), scale=(1., 1., 1.)):
        self.__x, self.__y, self.__z = position
        self.__rot_x, self.__rot_y, self.__rot_z = rotation
        if isinstance(scale, (int, float)):
            scale = (scale,) * 3
        self.__scale_x, self.__scale_y, self.__scale_z = scale

        self._model_matrix = None
        self._normal_matrix = None
        self._view_matrix = None

        self._set_transformation_matrix()

        self.linked_object = None  # Object whose position and rotation is automatically copied. Useful for online tracking.

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value
        self._set_transformation_matrix()

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value
        self._set_transformation_matrix()

    @property
    def z(self):
        return self.__z

    @z.setter
    def z(self, value):
        self.__z = value
        self._set_transformation_matrix()

    @property
    def position(self):
        return self.x, self.y, self.z

    @position.setter
    def position(self, value):
        self.__x, self.__y, self.__z = value
        self._set_transformation_matrix()

    @property
    def xy(self):
        return self.x, self.y

    @xy.setter
    def xy(self, value):
        self.__x, self.__y = value
        self._set_transformation_matrix()

    @property
    def scale_x(self):
        return self.__scale_x

    @scale_x.setter
    def scale_x(self, value):
        self.__scale_x = value
        self._set_transformation_matrix()

    @property
    def scale_y(self):
        return self.__scale_y

    @scale_y.setter
    def scale_y(self, value):
        self.__scale_y = value
        self._set_transformation_matrix()

    @property
    def scale_z(self):
        return self.__scale_z

    @scale_z.setter
    def scale_z(self, value):
        self.__scale_z = value
        self._set_transformation_matrix()

    @property
    def scale(self):
        return self.scale_x, self.scale_y, self.scale_z

    @scale.setter
    def scale(self, value):
        if isinstance(value, (int, float)):
            value = (value,) * 3
        self.__scale_x, self.__scale_y, self.__scale_z = value
        self._set_transformation_matrix()

    @property
    def rot_x(self):
        return self.__rot_x

    @rot_x.setter
    def rot_x(self, value):
        self.__rot_x = value
        self._set_transformation_matrix()

    @property
    def rot_y(self):
        return self.__rot_y

    @rot_y.setter
    def rot_y(self, value):
        self.__rot_y = value
        self._set_transformation_matrix()

    @property
    def rot_z(self):
        return self.__rot_z

    @rot_z.setter
    def rot_z(self, value):
        self.__rot_z = value
        self._set_transformation_matrix()

    @property
    def rotation(self):
        return self.rot_x, self.rot_y, self.rot_z

    @rotation.setter
    def rotation(self, value):
        self.__rot_x, self.__rot_y, self.__rot_z = value
        self._set_transformation_matrix()

    def distance_to(self, other_obj):
        """Full 3D (X-Y-Z) Distance from own origin to another object's origin"""
        own_position = np.array(self.position)
        other_position = np.array(other_obj.position)
        return np.sqrt(sum((own_position - other_position)**2))

    def distance2D_to(self, other_obj):
        """X-Y Distance from own origin to another object's origin"""
        own_position = np.array(self.position[:2])
        other_position = np.array(other_obj.position[:2])
        return np.sqrt(sum((own_position - other_position)**2))  # Return their distance using the distance formula

    def _set_transformation_matrix(self):
        """Operates on either Model matrix or View matrix, depending on the type specified by self._tranform_type."""
        # TODO: Make more efficient--there shouldn't need to be so many calculations, as some of these seem redundant!

        # Set View Matrix
        trans_mat = transformations.translation_matrix([-self.x, -self.y, -self.z])
        rot_x_mat = transformations.rotation_matrix(np.radians(-self.rot_x), [1, 0, 0])
        rot_y_mat = transformations.rotation_matrix(np.radians(-self.rot_y), [0, 1, 0])
        rot_z_mat = transformations.rotation_matrix(np.radians(-self.rot_z), [0, 0, 1])

        rot_mat = np.dot(np.dot(rot_x_mat,rot_y_mat), rot_z_mat)
        view_matrix = np.dot(rot_mat, trans_mat)
        self.view_matrix = view_matrix
        self._view_matrix = view_matrix.transpose().flatten()  # Transpose is to change to column-major mode, for OpenGL

        # Set Model and Normal Matrices
        trans_mat = transformations.translation_matrix([self.x, self.y, self.z])
        rot_x_mat = transformations.rotation_matrix(np.radians(self.rot_x), [1, 0, 0])
        rot_y_mat = transformations.rotation_matrix(np.radians(self.rot_y), [0, 1, 0])
        rot_z_mat = transformations.rotation_matrix(np.radians(self.rot_z), [0, 0, 1])
        scale_mat = transformations.scale_matrix(self.scale[0])

        rot_mat = np.dot(np.dot(rot_z_mat,rot_y_mat), rot_x_mat)
        model_matrix = np.dot(np.dot(trans_mat, rot_mat), scale_mat)
        self._model_matrix = model_matrix.T.flatten()  # Transpose is to change to column-major mode, for OpenGL
        self._normal_matrix = np.linalg.inv(model_matrix.T).T.flatten()  # Both transposes could cancel each other out, but don't cost much to do here..

class Color(object):

    names = {'white': (1, 1, 1), 'black': (0, 0, 0), 'red':(1, 0, 0), 'green':(0, 1, 0), 'blue':(0, 0, 1)}

    def __init__(self, r, g, b, a=1.):
        """Color object, defines rgba attributes"""
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self._textname = 'other'

    @property
    def rgb(self):
        return self.r, self.g, self.b

    @rgb.setter
    def rgb(self, value):
        self.r, self.g, self.b = value

    @property
    def rgba(self):
        return self.r, self.g, self.b, self.a

    @rgba.setter
    def rgba(self, value):
        self.r, self.g, self.b, self.a = value

    @property
    def text(self):
        return self._textname

    @text.setter
    def text(self, value):
        self.r, self.g, self.b = Color.names[value]
