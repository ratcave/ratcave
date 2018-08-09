import abc
import numpy as np
import pyglet.gl as gl
from .mesh import Mesh


class ColliderBase(Mesh):
    __metaclass__ = abc.ABCMeta
    primitive_shape = 'Sphere'

    def __init__(self, parent=None, visible=True, drawmode=gl.GL_LINES, position=(0, 0, 0), **kwargs):
        """
        Calculates collision by checking if a point is inside a sphere around the mesh vertices.
        """
        # kwargs['scale'] = np.ptp(parent.vertices, axis=0).max() / 2 if 'scale' not in kwargs else kwargs['scale']
        # kwargs['']

        from .wavefront import WavefrontReader
        from .resources import obj_primitives
        reader = WavefrontReader(obj_primitives)
        body = reader.bodies[self.primitive_shape]
        vertices, normals, texcoords = body['v'], body['vn'], body['vt']

        super(ColliderBase, self).__init__(arrays=[vertices, normals, texcoords],
                                           drawmode=drawmode, visible=visible, position=position,
                                           **kwargs)
        self.uniforms['diffuse'] = 1., 0, 0

        # Changes Scenegraph.parent execution order so self.scale can occur in the CollisionChecker parent property.
        if parent:
            self.parent = parent

    @property
    def parent(self):
        return super(Mesh, self).parent

    @parent.setter
    def parent(self, value):
        Mesh.parent.__set__(self, value)
        self.scale.xyz = self._fit_to_parent_vertices(value.vertices)


    @staticmethod
    def _fit_to_parent_vertices(self, vertices):
        pass
        """An algorithm to return a 3-element estimate for setting the scale to a parent Mesh's vertices."""

    @abc.abstractmethod
    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        pass



class ColliderSphere(ColliderBase):
    primitive_shape = 'Sphere'

    def _fit_to_parent_vertices(self, vertices):
        return np.ptp(vertices, axis=0) / 2

    def collides_with(self, other):
        """Returns True/False if 'other' (a PhysicalGraph or 3-tuple) is inside the collider."""
        try:
            x, y, z = other.position_global
        except AttributeError:
            x, y, z = np.array(other, dtype=np.float32)

        return np.linalg.norm(self.view_matrix_global.dot((x, y, z, 1))[:3]) <= 1.





# class CylinderCollisionChecker(CollisionCheckerMixin):
#
#     _non_up_columns = {'x': (1, 2), 'y': (0, 2), 'z': (1, 2)}
#
#     def __init__(self, mesh, up_axis='y'):
#         """
#
#         Parameters
#         ----------
#         mesh: Mesh instance
#         up_axis: ('x', 'y', 'z'): Which direction is 'up', which won't factor in the distance calculation.
#
#         Returns
#         -------
#
#         """
#         self.mesh = mesh
#         self.up_axis = up_axis
#         self._collision_columns = self._non_up_columns[up_axis]
#         self.collision_radius = np.linalg.norm(self.mesh.vertices[:, self._collision_columns], axis=1).max()
#
#     def collides_with(self, xyz):
#         cc = self._collision_columns
#         return np.linalg.norm(xyz[:, cc] - self.mesh.position_global[cc]) < self.collision_radius
