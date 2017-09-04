

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
from .utils import mixins
from . import physical, shader
from . import texture as texture_module
import pyglet.gl as gl


# Meshes
def gen_fullscreen_quad(name='FullScreenQuad'):
    verts = np.array([[-1, -1, -.5], [-1, 1, -.5], [1, 1, -.5], [-1, -1, -.5], [1, 1, -.5], [1, -1, -.5]], dtype=np.float32)
    normals=np.array([[0, 0, 1]] * 6, dtype=np.float32)
    texcoords=np.array([[0, 0], [0, 1], [1, 1], [0, 0], [1, 1], [1, 0]], dtype=np.float32)
    return Mesh(name=name, arrays=(verts, normals, texcoords), mean_center=False)


class EmptyEntity(shader.HasUniforms, physical.PhysicalGraph):
    """An object that occupies physical space and uniforms, but doesn't actually draw anything when draw() is called."""

    def draw(self, *args, **kwargs):
        pass

    def reset_uniforms(self):
        pass


class Mesh(shader.HasUniforms, physical.PhysicalGraph, mixins.NameLabelMixin, mixins.ObservableVisibleMixin):

    def __init__(self, arrays, texture=None, mean_center=True,
                 gl_states=(), drawmode=gl.GL_TRIANGLES, **kwargs):
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
        self.reset_uniforms()

        arrays = tuple(np.array(array, dtype=np.float32) for array in arrays)
        self.arrays, self.array_indices = vertutils.reindex_vertices(arrays)

        # Mean-center vertices and move position to vertex mean.
        vertex_mean = self.arrays[0][self.array_indices, :].mean(axis=0)
        if mean_center:
            self.arrays[0][:] -= vertex_mean
        if 'position' in kwargs:
            self.position.xyz = kwargs['position']
        elif mean_center:
            self.position.xyz = vertex_mean
        # self.position.xyz = vertex_mean if not 'position' in kwargs else kwargs['position']

        # Change vertices from an Nx3 to an Nx4 array by appending ones.  This makes some calculations more efficient.
        arrays = list(self.arrays)
        arrays[0] = np.append(self.arrays[0], np.ones((self.arrays[0].shape[0], 1), dtype=np.float32), axis=1)
        self.arrays = tuple(arrays)

        self.texture = texture if texture else texture_module.BaseTexture()
        self.vao = None  # Will be created upon first draw, when OpenGL context is available.
        self.gl_states = gl_states
        self.drawmode = drawmode

    def __repr__(self):
        return "<Mesh(name='{self.name}', position_rel={self.position}, position_glob={self.position_global}, rotation={self.rotation})".format(self=self)

    def reset_uniforms(self):
        self.uniforms['model_matrix'] = self.model_matrix_global.view()
        self.uniforms['normal_matrix'] = self.normal_matrix_global.view()

    @property
    def vertices(self):
        """Mesh vertices, centered around 0,0,0"""
        return self.arrays[0].view()

    @vertices.setter
    def vertices(self, value):
        self.arrays[0][:] = value

    @property
    def vertices_local(self):
        """Vertex position, in local coordinate space (modified by model_matrix)"""
        return np.dot(self.model_matrix, self.vertices)

    @property
    def vertices_global(self):
        """Vertex position, in world coordinate space (modified by model_matrix)"""
        return np.dot(self.model_matrix_global, self.vertices)

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, value):
        if isinstance(value, str):
            tex = texture_module.Texture.from_image(value)
        elif isinstance(value, texture_module.BaseTexture):
            tex = value
        else:
            raise TypeError("Texture must be given a filename or a ratcave.Texture instance.")
        self._texture = tex
        self.uniforms.update(tex.uniforms)

    @classmethod
    def from_incomplete_data(cls, vertices, normals=None, texcoords=None, name=None, **kwargs):
        """Return a Mesh with (vertices, normals, texcoords) as arrays, in that order.
           Useful for when you want a standardized array location format across different amounts of info in each mesh."""
        normals = normals if type(normals) != type(None) else vertutils.calculate_normals(vertices)
        texcoords = texcoords if type(texcoords) != type(None) else np.zeros((vertices.shape[0], 2), dtype=np.float32)
        return cls(name=name, arrays=(vertices, normals, texcoords), **kwargs)

    def _fill_vao(self):
        """Put array location in VAO for shader in same order as arrays given to Mesh."""
        with self.vao:
            for loc, verts in enumerate(self.arrays):
                self.vao.assign_vertex_attrib_location(ugl.VBO(verts), loc)

    def draw(self):
        if not self.vao:
            self.vao = ugl.VAO(indices=self.array_indices)
            self._fill_vao()

        self.update()
        if self.visible:
            with ugl.enable_states(self.gl_states):
                # with self.texture, self.vao as vao:
                with self.vao as vao, self.texture:
                    self.uniforms.send()
                    vao.draw(mode=self.drawmode)



