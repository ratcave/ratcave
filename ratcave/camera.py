import pickle
import abc
import numpy as np
from .physical import PhysicalGraph
import pyglet.gl as gl
from collections import namedtuple
from .shader import HasUniformsUpdater
from .utils import NameLabelMixin, get_viewport

Viewport = namedtuple('Viewport', 'x y width height')


class ProjectionBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, z_near=0.1, z_far=12., **kwargs):
        """
        Abstract Base Class for the Projections. Used to create projectoin matrix that later represents Camera Space.
        Vertex with position=(0,0,0), should be located in the middle of the scene. Projection matrix has defined z - distance to the camera.

        Args:
            z_near (float): the nearest distance to the camera, has to be positive
            z_far (float): the furthest point from the  camera that is visible, has to be positive and bigger then z_near

        Returns:
            ProjectionBase instance


        """
        super(ProjectionBase, self).__init__(**kwargs)
        self._projection_matrix = np.identity(4, dtype=np.float32)
        if z_near >= z_far or z_near <= 0. or z_far <= 0.:
            raise ValueError("z_near must be less than z_far, and both must be positive.")
        self._z_near = z_near
        self._z_far = z_far
        self._update_projection_matrix()

    @property
    def projection_matrix(self):
        """Return projection_matrix"""
        return self._projection_matrix.view()

    @projection_matrix.setter
    def projection_matrix(self, value):
        self._projection_matrix[:] = value

    @property
    def z_near(self):
        """Return z_near value"""
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
        """Return z_far value"""
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
        """ Updates projection matrix"""
        self._update_projection_matrix()

    @property
    def viewport(self):
        """returns the viewport"""
        return get_viewport()

    def copy(self):
        """Returns a copy of the projection matrix"""
        params = {}
        for key, val in self.__dict__.items():
            if 'matrix' not in key:
                k = key[1:] if key[0] == '_' else key
                params[k] = val
        # params = {param: params[param] for param in params}
        return self.__class__(**params)


ScreenEdges = namedtuple('ScreenEdges', 'left right bottom top')


class OrthoProjection(ProjectionBase):

    def __init__(self, origin='center', coords='relative', **kwargs):
        """
        Orthogonal Projection Object cretes projection Object that can be used in Camera

        Args:
            origin (str): 'center' or 'corner'
            coords (str): 'relative' or 'absolute'

        Returns:
            OrthoProjection instance
        """
        self._origin = origin
        self._coords = coords
        super(OrthoProjection, self).__init__(**kwargs)

    @property
    def origin(self):
        """Returns origin of the Projection """
        return self._origin

    @origin.setter
    def origin(self, value):
        if value.lower() not in ['center', 'corner']:
            raise ValueError()
        self._origin = value.lower()
        self._update_projection_matrix()

    @property
    def coords(self):
        """Returns coordinates"""
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



class Camera(PhysicalGraph, HasUniformsUpdater, NameLabelMixin):

    def __init__(self, projection=None, orientation0=(0, 0, -1), **kwargs):
        """Returns a camera object

        Args:
            projection (obj): the projection type for the camera. It can either be an instance of OrthoProjection or PerspeectiveProjection
            orientation0 (tuple): 

        Returns:
            Camera instance
        """
        kwargs['orientation0'] = orientation0
        super(Camera, self).__init__(**kwargs)
        self.projection = PerspectiveProjection() if not projection else projection
        self.reset_uniforms()

    def __repr__(self):
        return "<Camera(name='{self.name}', position_rel={self.position}, position_glob={self.position_global}, rotation={self.rotation})".format(self=self)

    def __enter__(self):
        self.update()
        self.uniforms.send()
        return self

    def __exit__(self, *args):
        pass

    def to_pickle(self, filename):
        """Save Camera to a pickle file, given a filename."""
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle(cls, filename):
        """Loads and Returns a Camera from a pickle file, given a filename."""
        with open(filename, 'rb') as f:
            cam = pickle.load(f)

        projection = cam.projection.copy()
        return cls(projection=projection, position=cam.position.xyz, rotation=cam.rotation.__class__(*cam.rotation[:]))

    @property
    def projection(self):
        """Returns the Camera's Projection """
        return self._projection

    @projection.setter
    def projection(self, value):
        if not issubclass(value.__class__, ProjectionBase):
            raise TypeError("Camera.projection must be a Projection.")

        self._projection = value
        self.reset_uniforms()

    def reset_uniforms(self):
        self.uniforms['projection_matrix'] = self.projection_matrix.view()
        self.uniforms['model_matrix'] = self.model_matrix.view()
        self.uniforms['view_matrix'] = self.view_matrix_global.view()
        self.uniforms['camera_position'] = self.model_matrix_global[:3, 3]

    @property
    def projection_matrix(self):
        """Returns projection matrix of the Camera"""
        return self.projection.projection_matrix.view()


class CameraGroup(PhysicalGraph):

    def __init__(self, cameras=None, *args, **kwargs):
        """ Creates a group of cameras that behave dependently"""
        super(CameraGroup, self).__init__(*args, **kwargs)
        self.cameras = cameras
        self.add_children(*self.cameras)

    def look_at(self, x, y, z):
        """Converges the two cameras to look at the specific point"""
        for camera in self.cameras:
            camera.look_at(x, y, z)


class StereoCameraGroup(CameraGroup):

    def __init__(self, distance=.1, projection=None, convergence=0., *args, **kwargs):
        """ Creates a group of cameras that behave dependently"""
        cameras = [Camera(projection=projection) for _ in range(2)]
        super(StereoCameraGroup, self).__init__(cameras=cameras, *args, **kwargs)
        for camera, x in zip(self.cameras, [-distance / 2, distance / 2]):
            project = projection.copy() if isinstance(projection, ProjectionBase) else PerspectiveProjection()
            camera.projection = project
            camera.position.x = x

        self.left, self.right = self.cameras
        self.distance = distance
        self.convergence = convergence
        
    @property
    def distance(self):
        return self.right.position.x - self.left.position.x

    @distance.setter
    def distance(self, value):
        self.left.position.x = -value / 2
        self.right.position.x = value / 2

    @property
    def convergence(self):
        return self._convergence

    @convergence.setter
    def convergence(self, value):
        self.left.projection.x_shift = value
        self.right.projection.x_shift = -value
        self._convergence = value

