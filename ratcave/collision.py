import abc
import numpy as np
import pyglet.gl as gl
from . import resources
from .wavefront import WavefrontReader
from .mesh import Mesh


class CollisionCheckerBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh."""
        pass


class SphereCollisionChecker(Mesh, CollisionCheckerBase):
    """Calculates collision by checking if a point is inside a sphere around the mesh vertices."""

    def __init__(self, parent, visible=False, **kwargs):
        """
        Parameters:
        parent: Mesh instance
        kwargs

        Returns:

        """
        super(Mesh, self).__init__(**kwargs)

        self.parent = parent

        # setup of the sphere
        obj_filename = resources.obj_primitives
        obj_reader = WavefrontReader(obj_filename)

        self.collider = obj_reader.get_mesh("Sphere", visible=visible)
        self.collider.draw_mode = gl.GL_LINE_LOOP
        self.collider.position.xyz = self.find_center(self.parent)
        self.collider.position.xyz = 0, 0, 0

        # collision radius
        self.collision_radius = np.linalg.norm(parent.vertices[:, :3], axis=1).max()
        self.collider.scale = self.collision_radius

        parent.add_child(self.collider, modify=False)

    @classmethod
    def find_center(cls, mesh):
        """Returns a tuple with the center of the Mesh"""
        center_x = ((mesh.vertices[:, :1]).max() + (mesh.vertices[:, :1]).min())/2
        center_y = ((mesh.vertices[:, :2]).max() + (mesh.vertices[:, :2]).min())/2
        center_z = ((mesh.vertices[:, :3]).max() + (mesh.vertices[:, :3]).min())/2
        return (0, 0, 0)
        # return (center_x, center_y, center_z)

    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        return np.linalg.norm(np.subtract(xyz, self.parent.position_global)) < self.collision_radius


class CylinderCollisionChecker(Mesh, CollisionCheckerBase):

    _non_up_columns = {'x': (1, 2), 'y': (0, 2), 'z': (1, 2)}
    _coords = {'x': 0, 'y': 1, 'z': 2}

    def __init__(self, parent, up_axis='y', visible=False, **kwargs):
        """
        Parameters:
        parent: Mesh instance
        up_axis: ('x', 'y', 'z'): Which direction is 'up', which won't factor in the distance calculation.

        Returns:
        """
        self._parent = parent

        self.up_axis = up_axis

        obj_filename = resources.obj_primitives
        obj_reader = WavefrontReader(obj_filename)

        self.collider = obj_reader.get_mesh("Cylinder", visible=visible)

        self.collider.draw_mode = gl.GL_LINE_LOOP
        # self.collider.position.xyz = self.find_center(self.parent)
        self.collider.position.xyz = 0, 0, 0
        self.collider.scale = np.linalg.norm(self.parent.vertices[:, :3], axis=1).max()

        self.collider.rotation[self._coords[up_axis]] += 90


        parent.add_child(self.collider, modify=False)

        self._collision_columns = self._non_up_columns[up_axis]
        self.collision_radius = np.linalg.norm(self.parent.vertices[:, self._collision_columns], axis=1).max()

    @classmethod
    def find_center(cls, mesh):
        """Returns a tuple with the center of the Mesh"""
        center_x = ((mesh.vertices[:, :1]).max() + (mesh.vertices[:, :1]).min())/2
        center_y = ((mesh.vertices[:, :2]).max() + (mesh.vertices[:, :2]).min())/2
        center_z = ((mesh.vertices[:, :3]).max() + (mesh.vertices[:, :3]).min())/2
        return (center_x, center_y, center_z)

    def collides_with(self, xyz):
        cc = self._collision_columns
        xyz_new = np.take(xyz, cc)
        glob_pos = np.take(self.parent.position_global, cc)

        return np.linalg.norm(np.subtract(xyz_new, glob_pos)) < self.collision_radius
