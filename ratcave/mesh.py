

"""
    mesh
    ~~~~

    This module contains the Mesh, MeshData, and Material classes.
    This documentation was auto-generated from the mesh.py file.
"""
import abc
import numpy as np
from .utils import gl as ugl
from .utils import vertices as vertutils
from . import physical
from . import texture as texture_module
from .draw import Drawable


class Mesh(Drawable, physical.PhysicalGraph):

    def __init__(self, name, arrays, texture=None, visible=True, **kwargs):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            name (str): the mesh's name.
            arrays (tuple): a list of 2D arrays to be rendered.  All arrays should have same number of rows. Arrays will be accessible in shader in same attrib location order.
            texture (Texture): a Texture instance, which is linked when the Mesh is rendered.
            visible (bool): whether the Mesh is available to be rendered.  To make hidden (invisible), set to False.

        Returns:
            Mesh instance
        """

        super(Mesh, self).__init__(**kwargs)
        self.uniforms['model_matrix'] = self.model_matrix_global.view()
        self.uniforms['normal_matrix'] = self.normal_matrix_global.view()

        self.name = name
        arrays = tuple(np.array(array, dtype=np.float32) for array in arrays)
        self.arrays, self.array_indices = vertutils.reindex_vertices(arrays)

        # Mean-center vertices and move position to vertex mean.
        vertex_mean = self.arrays[0].mean(axis=0)
        self.arrays[0] -= vertex_mean
        self.position = vertex_mean if not 'position' in kwargs else kwargs['position']

        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        texture = texture if texture else texture_module.BaseTexture()
        if texture and not isinstance(texture, texture_module.BaseTexture):
            raise TypeError("Mesh.texture should be a Texture instance.")
        self.texture = texture
        self.uniforms.update(self.texture.uniforms)

        self.visible = visible

        self.vao = ugl.VAO(indices=self.array_indices)
        self._fill_vao()

    @property
    def vertices(self):
        return self.arrays[0].view()

    @vertices.setter
    def vertices(self, value):
        self.arrays[0][:] = value

    @classmethod
    def from_incomplete_data(cls, name, vertices, normals=None, texcoords=None, **kwargs):
        """Return a Mesh with (vertices, normals, texcoords) as arrays, in that order.
           Useful for when you want a standardized array location format across different amounts of info in each mesh."""
        normals = normals if normals else vertutils.calculate_normals(vertices)
        texcoords = texcoords if texcoords else np.zeros((vertices.shape[0], 2), dtype=np.float32)
        return cls(name=name, arrays=(vertices, normals, texcoords), **kwargs)

    def _fill_vao(self):
        """Put array location in VAO for shader in same order as arrays given to Mesh."""
        with self.vao:
            for loc, verts in enumerate(self.arrays):
                self.vao.assign_vertex_attrib_location(ugl.VBO(verts), loc)

    def draw(self, send_uniforms=True, **kwargs):
        super(Mesh, self).draw(**kwargs)

        if self.visible:
            self.update()
            with self.texture, self.vao as vao:
                self.uniforms.send()
                vao.draw()


class CollisionMeshBase(Mesh):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh."""
        pass


class SphereCollisionMesh(CollisionMeshBase):
    """Calculates collision by checking if a point is inside a sphere around the mesh vertices."""

    def __init__(self, *args, **kwargs):
        super(SphereCollisionMesh, self).__init__(*args, **kwargs)
        self.collision_radius = np.linalg.norm(self.vertices_global, axis=1).max()

    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        return np.linalg.norm(xyz - self.position_global) < self.collision_radius


class CylinderCollisionMesh(CollisionMeshBase):

    def __init__(self, up_axis='y', *args, **kwargs):
        super(CylinderCollisionMesh, self).__init__(*args, **kwargs)
        self.up_axis = up_axis
        self._collision_columns = {'x': (1, 2), 'y': (0, 2), 'z': (1, 2)}[up_axis]
        self.collision_radius = np.linalg.norm(self.vertices_global[:, self._collision_columns], axis=1).max()

    def collides_with(self, xyz):
        cc = self._collision_columns
        return np.linalg.norm(xyz[:, cc] - self.position_global[cc]) < self.collision_radius



