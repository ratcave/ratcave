import abc
import numpy as np
import pyglet.gl as gl
from . import resources
from .wavefront import WavefrontReader
from .mesh import Mesh


class CollisionCheckerBase(Mesh):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh."""
        pass


class SphereCollisionChecker(CollisionCheckerBase):
    """Calculates collision by checking if a point is inside a sphere around the mesh vertices."""

    def __init__(self, mesh, **kwargs):
        """
        Parameters
        ----------
        mesh: Mesh instance
        kwargs

        Returns
        -------
        """
        super(Mesh, self).__init__(**kwargs)
        self.draw_mode = gl.GL_POINTS
        self.visible = False

        self.mesh = mesh



        obj_filename = resources.obj_primitives
        obj_reader = WavefrontReader(obj_filename)
        sphere = obj_reader.get_mesh("Sphere")
        mesh.add_child(sphere)


        self.collision_radius = np.linalg.norm(mesh.vertices[:, :3], axis=1).max()

    # def draw(self):
        # super(Mesh, self).draw(self)

    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        print(xyz, self.mesh.position_global)
        print(np.subtract(xyz, self.mesh.position_global))
        return np.linalg.norm(np.subtract(xyz, self.mesh.position_global)) < self.collision_radius


class CylinderCollisionChecker(CollisionCheckerBase):

    _non_up_columns = {'x': (1, 2), 'y': (0, 2), 'z': (1, 2)}

    def __init__(self, mesh, up_axis='y'):
        """

        Parameters
        ----------
        mesh: Mesh instance
        up_axis: ('x', 'y', 'z'): Which direction is 'up', which won't factor in the distance calculation.

        Returns
        -------

        """
        self.mesh = mesh
        self.up_axis = up_axis
        self._collision_columns = self._non_up_columns[up_axis]
        self.collision_radius = np.linalg.norm(self.mesh.vertices[:, self._collision_columns], axis=1).max()

    def collides_with(self, xyz):
        cc = self._collision_columns
        return np.linalg.norm(xyz[:, cc] - self.mesh.position_global[cc]) < self.collision_radius
