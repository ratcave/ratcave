import abc
import numpy as np
from . import physical
import pyglet.gl as gl
from collections import namedtuple
import warnings

Viewport = namedtuple('Viewport', 'x y width height')

class CameraBase(physical.PhysicalNode):
    __metaclass__ = abc.ABCMeta

    def __init__(self, z_near=0.1, z_far=4.5, **kwargs):
        super(CameraBase, self).__init__(**kwargs)
        self.z_near = z_near
        self.z_far = z_far
        self.projection_matrix = np.identity(4, dtype=float)

    @abc.abstractmethod
    def _update_projection_matrix(self): pass

    def update(self):
        super(CameraBase, self).update()
        self._update_projection_matrix()

    @property
    def viewport(self):
        viewport_array = (gl.GLint * 4)()
        gl.glGetIntegerv(gl.GL_VIEWPORT, viewport_array)
        return Viewport(*viewport_array)

    @property
    def aspect(self):
        viewport = self.viewport
        return float(viewport.width) / viewport.height


class OrthoCamera(CameraBase):

    def __init__(self, origin='center', coords='relative', **kwargs):
        """
        Parameters
        ----------
        origin: 'center', 'corner',
        coords
        """
        super(OrthoCamera, self).__init__(**kwargs)
        self._screen_edges = {'left': 0, 'right': 0, 'bottom': 0, 'top': 0}
        self.origin = origin
        self.coords = coords

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        if value.lower() not in ['center', 'corner']:
            raise ValueError("OrthoCamera.origin must be 'center' or 'corner'.")
        self._origin = value.lower()
        self._update_screen_edges()

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, value):
        if value.lower() not in ['relative', 'absolute']:
            raise ValueError("OrthoCamera.coords must be 'relative' or 'absolute'.")
        self._coords = value.lower()
        self._update_screen_edges()

    @property
    def screen_edges(self):
        return self._screen_edges

    def _update_screen_edges(self):
        vp = self.viewport
        se = self.screen_edges
        se['left'], se['right'] = (0, vp.width) if 'corner' in self.origin else (-vp.width / 2., vp.width / 2.)
        se['bottom'], se['top'] = (0, vp.height) if 'corner' in self.origin else (-vp.height / 2., vp.height / 2.)
        for side in se:
            se[side] /= float(vp.width)  # all by width keeps distance square.
        self._update_projection_matrix()

    def _update_projection_matrix(self):
        se = self.screen_edges
        left, right, bott, top = se['left'], se['right'], se['bottom'], se['top']
        zn, zf = self.z_near, self.z_far

        tx = -(right + left) / (right - left)
        ty = -(top + bott) / (top - bott)
        tz = -(zf + zn) - (zf - zn)

        self.projection_matrix[:] = np.array([[2./(right - left),               0,           0, tx],
                                              [                0, 2./(top - bott),           0, ty],
                                              [                0,               0, -2./(zf-zn), tz],
                                              [                0,               0,           0,  1]])


class PerspectiveCamera(CameraBase):

    def __init__(self, fov_y=60., x_shift=0., y_shift=0., **kwargs):
        super(PerspectiveCamera, self).__init__(**kwargs)
        self.fov_y = fov_y
        self.x_shift = x_shift
        self.y_shift = y_shift



    def _update_shift_matrix(self):
        """np.array: The Camera's lens-shift matrix."""
        self.shift_matrix =  np.array([[1., 0., self.x_shift, 0.],
                                       [0., 1., self.y_shift, 0.],
                                       [0., 0.,           1., 0.],
                                       [0., 0.,           0., 1.]])

    def _update_projection_matrix(self):
        """np.array: The Camera's Projection Matrix.  Will be an Orthographic matrix if ortho_mode is set to True."""

        # replace gluPerspective (https://www.opengl.org/sdk/docs/man2/xhtml/gluPerspective.xml)
        ff = 1./np.tan(np.radians(self.fov_y / 2.)) # cotangent(fovy/2)
        zn, zf = self.z_near, self.z_far

        persp_mat =  np.array([[ff/self.aspect,    0.,              0.,                 0.],
                              [             0.,    ff,              0.,                 0.],
                              [             0.,    0., (zf+zn)/(zn-zf), (2.*zf*zn)/(zn-zf)],
                              [             0.,    0.,             -1.,                 0.]])

        self._update_shift_matrix()
        persp_mat = np.dot(persp_mat, self.shift_matrix)  # Apply lens shift

        self.projection_matrix = persp_mat


class Camera(PerspectiveCamera):

    def __init__(self, ortho_mode=False, **kwargs):
        if ortho_mode:
            raise DeprecationWarning("Camera class deprecated and not usable for ortho_mode anymore. Use OrthoCamera instead")
        else:
            warnings.warn("Camera class deprecated. Use PerspectiveCamera instead", DeprecationWarning)
        super(Camera, self).__init__(**kwargs)


