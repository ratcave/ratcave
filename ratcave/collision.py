import abc
import numpy as np
from . import gl
from .mesh import Mesh


class ColliderBase(Mesh):
    __metaclass__ = abc.ABCMeta
    primitive_shape = 'Sphere'

    def __init__(self, parent=None, visible=True, drawmode=gl.GL_LINES, position=(0, 0, 0), **kwargs):
        """Calculates collision by checking if a point is inside a sphere around the mesh vertices."""
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

    @staticmethod
    def _extract_coord(obj):
        try:
            x, y, z = obj.position_global
        except AttributeError:
            x, y, z = np.array(obj, dtype=np.float32)
        return x, y, z

    @abc.abstractmethod
    def collides_with(self, other):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        pass



class ColliderSphere(ColliderBase):
    primitive_shape = 'Sphere'

    def _fit_to_parent_vertices(self, vertices):
        return np.ptp(vertices, axis=0) / 2

    def collides_with(self, other):
        """Returns True/False if 'other' (a PhysicalGraph or 3-tuple) is inside the collider."""
        x, y, z = self._extract_coord(other)
        return np.linalg.norm(self.view_matrix_global.dot((x, y, z, 1))[:3]) <= 1.


class ColliderCube(ColliderBase):
    primitive_shape = 'Cube'

    def _fit_to_parent_vertices(self, vertices):
        return np.ptp(vertices, axis=0) / 2

    def collides_with(self, other):
        """Returns True/False if 'other' (a PhysicalGraph or 3-tuple) is inside the collider."""
        x, y, z = self._extract_coord(other)
        return np.all(self.view_matrix_global.dot((x, y, z, 1))[:3] <= 1.)


class ColliderCylinder(ColliderBase):
    primitive_shape = 'Cylinder'

    def __init__(self, ignore_axis=1, **kwargs):
        self.ignore_axis = ignore_axis
        super(ColliderCylinder, self).__init__(**kwargs)
        if self.ignore_axis == 0:
            self.rotation.z = 90
        elif self.ignore_axis == 2:
            self.rotation.x = 90

    def _fit_to_parent_vertices(self, vertices, scale_gain=1e5):
        axes = [a for a in range(3) if a != self.ignore_axis]
        x, z = np.ptp(vertices[:, axes], axis=0) / 2
        return x, scale_gain, z  # scale_gain makes it clear in the display that one dimension is being ignored.

    def collides_with(self, other):
        """Returns True/False if 'other' (a PhysicalGraph or 3-tuple) is inside the collider."""
        x, y, z = self._extract_coord(other)
        return np.linalg.norm(self.view_matrix_global.dot((x, y, z, 1))[[0, 2]]) <= 1.
