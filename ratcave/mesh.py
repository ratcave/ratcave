

"""
    mesh
    ~~~~

    This module contains the Mesh, MeshData, and Material classes.
    This documentation was auto-generated from the mesh.py file.
"""
import abc
import numpy as np
from pyglet import gl
from .utils import gl as ugl
from .utils import vertices as vertutils
from . import physical
from . import texture as texture_module
from .draw import Drawable


class MeshBase(Drawable, physical.PhysicalGraph):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        super(MeshBase, self).__init__(**kwargs)
        self.uniforms['model_matrix'] = self.model_matrix_global.view()
        self.uniforms['normal_matrix'] = self.normal_matrix_global.view()




class Mesh(MeshBase):

    drawstyle = {'fill': gl.GL_TRIANGLES, 'line': gl.GL_LINE_LOOP, 'point': gl.GL_POINTS}

    def __init__(self, name, arrays, drawstyle='fill', visible=True, point_size=4, texture=None,
                 mean_center=True, **kwargs):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            name (str): the mesh's name.
            arrays (tuple): a list of 2D arrays to be rendered.  Arrays will be accessible in shader in same attrib location order.
            uniforms (list): a list of all Uniform objects
            drawstyle (str): 'point': only vertices, 'line': points and edges, 'fill': points, edges, and faces (full)
            visible (bool): whether the Mesh is available to be rendered.  To make hidden (invisible), set to False.
            point_size (int): How big to draw the points, when drawstyle is 'point'

        Returns:
            Mesh instance
        """

        super(Mesh, self).__init__(**kwargs)
        self.name = name
        arrays = (np.array(array, dtype=np.float32) for array in arrays)
        self.arrays, self.array_indices = vertutils.reindex_vertices(arrays)

        # Mean-center vertices, if specified.  Assume first array is vertices.
        if mean_center:
            vertex_mean = self.arrays[0].mean(axis=0)
            self.arrays[0] -= vertex_mean  # assume
            self.position = vertex_mean if not 'position' in kwargs else kwargs['position']


        self.vao = None

        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        if texture and not isinstance(texture, texture_module.BaseTexture):
            raise TypeError("Mesh.texture should be a Texture instance.")
        self.texture = texture
        self.drawstyle = drawstyle
        self.point_size = point_size
        self.visible = visible

    @classmethod
    def from_incomplete_data(cls, name, vertices, normals=None, texcoords=None, **kwargs):
        """Return a Mesh with (vertices, normals, texcoords) as arrays, in that order.
           Useful for when you want a standardized array location format across different amounts of info in each mesh."""
        normals = normals if normals else vertutils.calculate_normals(vertices)
        texcoords = texcoords if texcoords else np.zeros((vertices.shape[0], 2), dtype=np.float32)
        return cls(name=name, arrays=(vertices, normals, texcoords), **kwargs)


    def load(self):
        """Put array location in VAO for shader in same order as arrays given to Mesh."""
        self.vao = ugl.VAO(indices=self.array_indices)
        with self.vao:
            for loc, verts in enumerate(self.arrays):
                self.vao.assign_vertex_attrib_location(ugl.VBO(verts), loc)

    def draw(self, send_uniforms=True,**kwargs):
        super(Mesh, self).draw(**kwargs)

        if not self.vao:
            self.load()

        self.update()

        if self.visible:

            # Bind the VAO and Texture, and draw.
            if self.texture:
                self.texture.bind()

            # Change Material to Mesh's
            if send_uniforms:
                self.uniforms.send()
                self.texture.uniforms.send()

            # Set Point Size, if drawing a point cloud
            if self.drawstyle == 'point':
                gl.glPointSize(int(self.point_size))

            # Send in the vertex and normal data
            with self.vao as vao:
                vao.draw(Mesh.drawstyle[self.drawstyle])

            if self.texture:
                self.texture.unbind()


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



