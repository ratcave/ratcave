import abc
import numpy as np
import pyglet.gl as gl
from . import resources
from .wavefront import WavefrontReader
from .mesh import Mesh


class CollisionCheckerMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh."""
        pass


class CollisionCheckerBase(Mesh, CollisionCheckerMixin):
    def __init__(self, primitive, parent, visible=False, *args, **kwargs):
        self._parent = parent

        self.reader = WavefrontReader(resources.obj_primitives)
        self.collider_mesh = self.reader.get_mesh(primitive, visible=visible)
        self.collider_mesh.draw_mode = gl.GL_LINE_LOOP
        self.collider_mesh.position.xyz = parent.vertices.mean(axis=0)

        self.parent.add_child(self.collider_mesh, modify=False)


class SphereCollisionChecker(CollisionCheckerBase):
    def __init__(self, parent, visible=False,  **kwargs):
        """
        Returns a SphereCollisionChecker instance, that is responsible for checking whether the parented object has collided with anything.
        Collision is occuring if a point is inside a sphere around the mesh vertices.

        Args:
            parent (Mesh): Mesh instance, that is going to be checked for collisions.
            visible (bool): defines whether the CollissionChecker is available to be rendered. To make visible, set to False.

        Returns:
            SphereCollisionInstance
        """
        super(SphereCollisionChecker, self).__init__(parent=parent, primitive='Sphere', visible=visible, **kwargs)

        self.collision_radius = np.linalg.norm(parent.vertices[:, :3], axis=1).max()
        self.collider_mesh.scale = self.collision_radius


    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        return np.linalg.norm(np.subtract(xyz, self.parent.position_global)) < self.collision_radius


class CylinderCollisionChecker(CollisionCheckerBase):

    _non_up_columns = {'x': (1, 2), 'y': (0, 2), 'z': (0, 1)}
    _coords = {'x': 0, 'y': 1, 'z': 2}

    def __init__(self, parent, up_axis='y', visible=False, **kwargs):
        """
        Returns a CylinderCollisionChecker instance, that is responsible for checking whether the parented object has collided with anything.
        Collision is occuring if a point is inside a cylinder around the mesh vertices.

        Args:
            parent (Mesh): Mesh instance, that is going to be checked for collisions.
            visible (bool): defines whether the CollissionChecker is available to be rendered. To make visible, set to False.
            up_axis (str):  ('x', 'y', 'z'): Which direction is 'up', which won't factor in the distance calculation.
        Returns:
            CylinderCollisionChecker
        """
        super(CylinderCollisionChecker, self).__init__(parent=parent, primitive='Cylinder',visible=visible, **kwargs)

        self._collision_columns = self._non_up_columns[up_axis]
        self.collider_mesh.rotation[self._coords[up_axis]] += 90
        self.collision_radius = np.linalg.norm(self.parent.vertices[:, self._collision_columns], axis=1).max()

    def collides_with(self, xyz):
        cc = self._collision_columns
        xyz_new = np.take(xyz, cc)
        glob_pos = np.take(self.parent.position_global, cc)

        return np.linalg.norm(np.subtract(xyz_new, glob_pos)) < self.collision_radius
