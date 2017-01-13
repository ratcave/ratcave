import abc
import numpy as np
from .utils import AutoRegisterObserver, Observer, SetterObserver, Observable, IterObservable
from .physical import Physical, PhysicalGraph
import pyglet.gl as gl
from collections import namedtuple
import warnings
from .draw import Drawable


Viewport = namedtuple('Viewport', 'x y width height')


class ProjectionBase(SetterObserver):
    __metaclass__ = abc.ABCMeta

    _observables = ['z_near', 'z_far']

    def __init__(self, z_near=0.1, z_far=4.5, **kwargs):
        super(ProjectionBase, self).__init__(**kwargs)
        self.__dict__['z_near'] = z_near
        self.__dict__['z_far'] = z_far
        assert 'z_near' in self._observables and 'z_far' in self._observables

        self.__dict__['projection_matrix'] = np.identity(4, dtype=np.float32)

    @abc.abstractmethod
    def _update_projection_matrix(self): pass

    def update(self):
        super(ProjectionBase, self).update()
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


ScreenEdges = namedtuple('ScreenEdges', 'left right bottom top')


class OrthoProjection(ProjectionBase):

    _observables = ['origin', 'coords', 'z_near', 'z_far']

    def __init__(self, origin='center', coords='relative', **kwargs):
        """
        Parameters
        ----------
        origin: 'center', 'corner',
        coords: 'relative', 'absolute'
        """
        super(OrthoProjection, self).__init__(**kwargs)
        self.__dict__['origin'] = origin
        self.__dict__['coords'] = coords

    def _get_screen_edges(self):
        vp = self.viewport

        if 'corner' in self.origin:
            se = ScreenEdges(left=0, right=vp.width, bottom=0, top=vp.height)
        else:
            se = ScreenEdges(left=-vp.width / 2., right=vp.width / 2., bottom=-vp.height / 2., top=vp.height / 2.)

        if 'relative' in self.coords:
            se = ScreenEdges(*(el / vp.width for el in se))

        return se

    def _update_projection_matrix(self):

        se = self._get_screen_edges()
        zn, zf = self.z_near, self.z_far

        tx = -(se.right + se.left) / (se.right - se.left)
        ty = -(se.top + se.bottom) / (se.top - se.bottom)
        tz = -(zf + zn) / (zf - zn)

        self.projection_matrix[:] = np.array([[2./(se.right - se.left),                       0,           0, tx],
                                              [                      0, 2./(se.top - se.bottom),           0, ty],
                                              [                      0,                       0, -2./(zf-zn), tz],
                                              [                      0,                       0,           0,  1]])


class PerspectiveProjection(ProjectionBase):

    _observables = ['fov_y', 'x_shift', 'y_shift', 'z_near', 'z_far']

    def __init__(self, fov_y=60., x_shift=0., y_shift=0., **kwargs):
        super(PerspectiveProjection, self).__init__(**kwargs)
        self.__dict__['fov_y'] = fov_y
        self.__dict__['x_shift'] = x_shift
        self.__dict__['y_shift'] = y_shift

    def _get_shift_matrix(self):
        """np.array: The Camera's lens-shift matrix."""
        return np.array([[1., 0., self.x_shift, 0.],
                         [0., 1., self.y_shift, 0.],
                         [0., 0.,           1., 0.],
                         [0., 0.,           0., 1.]], dtype=np.float32)

    def _update_projection_matrix(self):
        """np.array: The Camera's Projection Matrix.  Will be an Orthographic matrix if ortho_mode is set to True."""

        # replace gluPerspective (https://www.opengl.org/sdk/docs/man2/xhtml/gluPerspective.xml)
        ff = 1./np.tan(np.radians(self.fov_y / 2.)) # cotangent(fovy/2)
        zn, zf = self.z_near, self.z_far

        persp_mat =  np.array([[ff/self.aspect,    0.,              0.,                 0.],
                              [             0.,    ff,              0.,                 0.],
                              [             0.,    0., (zf+zn)/(zn-zf), (2.*zf*zn)/(zn-zf)],
                              [             0.,    0.,             -1.,                 0.]], dtype=np.float32)

        self.projection_matrix[:] = np.dot(persp_mat, self._get_shift_matrix())  # Apply lens shift



class Camera(PhysicalGraph, Drawable):

    def __init__(self, ortho_mode=False, **kwargs):
        super(Camera, self).__init__(**kwargs)
        self.lens = OrthoProjection(**kwargs) if ortho_mode else PerspectiveProjection(**kwargs)
        self.uniforms['projection_matrix'] = self.projection_matrix.view()

        self.uniforms['view_matrix'] = self.view_matrix_global.view()
        self.uniforms['camera_position'] = self.model_matrix_global[:3, 3]

    def update(self):
        super(Camera, self).update()
        self.lens.update()

    @property
    def projection_matrix(self):
        return self.lens.projection_matrix


