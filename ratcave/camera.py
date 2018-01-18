import abc
import numpy as np
from .physical import PhysicalGraph
import pyglet.gl as gl
from collections import namedtuple
from .shader import HasUniforms
from .utils import NameLabelMixin, get_viewport

Viewport = namedtuple('Viewport', 'x y width height')


class ProjectionBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, z_near=0.1, z_far=12., **kwargs):
        super(ProjectionBase, self).__init__(**kwargs)
        self._projection_matrix = np.identity(4, dtype=np.float32)
        if z_near >= z_far or z_near <= 0. or z_far <= 0.:
            raise ValueError("z_near must be less than z_far, and both must be positive.")
        self._z_near = z_near
        self._z_far = z_far
        self._update_projection_matrix()

    @property
    def projection_matrix(self):
        return self._projection_matrix.view()

    @projection_matrix.setter
    def projection_matrix(self, value):
        self._projection_matrix[:] = value

    @property
    def z_near(self):
        return self._z_near

    @z_near.setter
    def z_near(self, value):
        if value < 0:
            raise ValueError("Camera.z_near must be positive.")
        elif value >= self.z_far:
            raise ValueError("Camera.z_near must be less than z_far.")
        self._z_near = float(value)
        self._update_projection_matrix()

    @property
    def z_far(self):
        return self._z_far

    @z_far.setter
    def z_far(self, value):
        if value < 0:
            raise ValueError("Camera.z_far must be positive.")
        elif value <= self.z_near:
            raise ValueError("Camera.z_far must be greater than z_near.")
        self._z_far = float(value)
        self._update_projection_matrix()

    @abc.abstractmethod
    def _update_projection_matrix(self): pass

    def update(self):
        self._update_projection_matrix()

    @property
    def viewport(self):
        return get_viewport()


ScreenEdges = namedtuple('ScreenEdges', 'left right bottom top')


class OrthoProjection(ProjectionBase):

    def __init__(self, origin='center', coords='relative', **kwargs):
        """
        Parameters
        ----------
        origin: 'center', 'corner',
        coords: 'relative', 'absolute'
        """
        self._origin = origin
        self._coords = coords
        super(OrthoProjection, self).__init__(**kwargs)

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        if value.lower() not in ['center', 'corner']:
            raise ValueError()
        self._origin = value.lower()
        self._update_projection_matrix()

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, value):
        if value.lower() not in ['relative', 'absolute']:
            raise ValueError()
        self._coords = value.lower()
        self._update_projection_matrix()

    def _get_screen_edges(self):
        vp = self.viewport

        if 'corner' in self.origin:
            se = ScreenEdges(left=0, right=vp.width, bottom=0, top=vp.height)
        else:
            se = ScreenEdges(left=-vp.width / 2., right=vp.width / 2., bottom=-vp.height / 2., top=vp.height / 2.)

        if 'relative' in self.coords:
            se = ScreenEdges(*(el / float(vp.width) for el in se))

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

    def __init__(self, fov_y=60., aspect=1.25, x_shift=0., y_shift=0., **kwargs):
        self._fov_y = fov_y
        self._x_shift = x_shift
        self._y_shift = y_shift
        self._aspect = aspect
        super(PerspectiveProjection, self).__init__(**kwargs)

    @property
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, value):
        self._aspect = value
        self._update_projection_matrix()

    def match_aspect_to_viewport(self):
        """Updates Camera.aspect to match the viewport's aspect ratio."""
        viewport = self.viewport
        self.aspect = float(viewport.width) / viewport.height

    @property
    def fov_y(self):
        return self._fov_y

    @fov_y.setter
    def fov_y(self, value):
        if value <= 0:
            raise ValueError("Camera.fov_y should be positive.")
        self._fov_y = value
        self._update_projection_matrix()

    @property
    def x_shift(self):
        return self._x_shift

    @x_shift.setter
    def x_shift(self, value):
        self._x_shift = value
        self._update_projection_matrix()

    @property
    def y_shift(self):
        return self._y_shift

    @y_shift.setter
    def y_shift(self, value):
        self._y_shift = value
        self._update_projection_matrix()

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



class Camera(PhysicalGraph, HasUniforms, NameLabelMixin):

    def __init__(self, projection=None, orientation0=(0, 0, -1), **kwargs):
        kwargs['orientation0'] = orientation0
        super(Camera, self).__init__(**kwargs)
        self.projection = PerspectiveProjection() if not projection else projection
        self.reset_uniforms()

    def __repr__(self):
        return "<Camera(name='{self.name}', position_rel={self.position}, position_glob={self.position_global}, rotation={self.rotation})".format(self=self)

    def __enter__(self):
        self.uniforms.send()
        return self

    def __exit__(self, *args):
        pass

    @property
    def projection(self):
        return self._projection

    @projection.setter
    def projection(self, value):
        if not issubclass(value.__class__, ProjectionBase):
            raise TypeError("Camera.projection must be a Projection.")
        if not hasattr(self, '_projection'):
            self._projection = value
            self.reset_uniforms()
        else:
            raise NotImplementedError("Setting a new projection on an existing Camera is not currently working.  Please create a new Camera.")

    def reset_uniforms(self):
        self.uniforms['projection_matrix'] = self.projection_matrix.view()
        self.uniforms['model_matrix'] = self.model_matrix.view()
        self.uniforms['view_matrix'] = self.view_matrix_global.view()
        self.uniforms['camera_position'] = self.model_matrix_global[:3, 3]

    @property
    def projection_matrix(self):
        return self.projection.projection_matrix.view()

