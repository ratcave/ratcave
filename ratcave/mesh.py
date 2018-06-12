"""
This module contains the Mesh and EmptyEntity classes.
"""

import pickle
import numpy as np
from .utils import vertices as vertutils
from .utils import NameLabelMixin
from . import physical, shader
from .texture import Texture
from .vertex import VAO, VBO
import pyglet.gl as gl
from copy import deepcopy
from warnings import warn


def gen_fullscreen_quad(name='FullScreenQuad'):
    verts = np.array([[-1, -1, -.5], [-1, 1, -.5], [1, 1, -.5], [-1, -1, -.5], [1, 1, -.5], [1, -1, -.5]], dtype=np.float32)
    normals=np.array([[0, 0, 1]] * 6, dtype=np.float32)
    texcoords=np.array([[0, 0], [0, 1], [1, 1], [0, 0], [1, 1], [1, 0]], dtype=np.float32)
    return Mesh(name=name, arrays=(verts, normals, texcoords), mean_center=False)


class EmptyEntity(shader.HasUniformsUpdater, physical.PhysicalGraph, NameLabelMixin):
    """Returns an EmptyEntity object that occupies physical space and uniforms, but doesn't draw anything when draw() is called."""

    def draw(self, *args, **kwargs):
        """Passes all given arguments"""
        pass

    def reset_uniforms(self):
        """Passes alll given arguments"""
        pass


class Mesh(shader.HasUniformsUpdater, physical.PhysicalGraph, NameLabelMixin):

    triangles = gl.GL_TRIANGLES
    points = gl.GL_POINTS


    def __init__(self, arrays, textures=(), mean_center=True,
                 gl_states=(), drawmode=gl.GL_TRIANGLES, point_size=15, dynamic=False, visible=True, **kwargs):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            arrays (tuple): a list of 2D arrays to be rendered.  All arrays should have same number of rows. Arrays will be accessible in shader in same attrib location order.
            mean_center (bool):
            texture (Texture): a Texture instance, which is linked when the Mesh is rendered.
            gl_states:
            drawmode: specifies the OpenGL draw mode
            point_size (int): 
            dynamic (bool): enables dynamic manipulation of vertices
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
        self._mean_center = mean_center
        # self.position.xyz = vertex_mean if not 'position' in kwargs else kwargs['position']

        # Change vertices from an Nx3 to an Nx4 array by appending ones.  This makes some calculations more efficient.
        arrays = list(self.arrays)
        arrays[0] = np.append(self.arrays[0], np.ones((self.arrays[0].shape[0], 1), dtype=np.float32), axis=1)
        self.arrays = tuple(arrays)

        self.textures = list(textures)
        self.vao = None  # Will be created upon first draw, when OpenGL context is available.
        self.gl_states = gl_states
        self.drawmode = drawmode
        self.point_size = point_size
        self.dynamic = dynamic
        self.visible = visible
        self.vbos = []


    def __repr__(self):
        return "<Mesh(name='{self.name}', position_rel={self.position}, position_glob={self.position_global}, rotation={self.rotation})".format(self=self)

    def copy(self):
        """Returns a copy of the Mesh."""
        return Mesh(arrays=deepcopy([arr.copy() for arr in [self.vertices, self.normals, self.texcoords]]), texture=self.textures, mean_center=deepcopy(self._mean_center),
                    position=self.position.xyz, rotation=self.rotation.__class__(*self.rotation[:]), scale=self.scale.xyz,
                    drawmode=self.drawmode, point_size=self.point_size, dynamic=self.dynamic, visible=self.visible,
                    gl_states=deepcopy(self.gl_states))

    def to_pickle(self, filename):
        """Save Mesh to a pickle file, given a filename."""
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle(cls, filename):
        """Loads and Returns a Mesh from a pickle file, given a filename."""
        with open(filename, 'rb') as f:
            mesh = pickle.load(f).copy()
        return mesh

    def reset_uniforms(self):
        """ Resets the uniforms to the Mesh object to the ""global"" coordinate system"""
        self.uniforms['model_matrix'] = self.model_matrix_global.view()
        self.uniforms['normal_matrix'] = self.normal_matrix_global.view()


    @property
    def dynamic(self):
        """dynamic property of the mesh. If set to True, enables the user to modify vertices dynamically."""
        return self._dynamic

    @dynamic.setter
    def dynamic(self, value):
        for array in self.arrays:
            array.setflags(write=True if value else False)
        self._dynamic = value


    @property
    def vertices(self):
        """Mesh vertices, centered around 0,0,0."""
        return self.arrays[0][:, :3].view()

    @vertices.setter
    def vertices(self, value):
        self.arrays[0][:, :3] = value

    @property
    def normals(self):
        """Mesh normals array."""
        return self.arrays[1][:, :3].view()

    @normals.setter
    def normals(self, value):
        self.arrays[1][:, :3] = value

    @property
    def texcoords(self):
        """UV coordinates"""
        return self.arrays[2][:, :2].view()

    @texcoords.setter
    def texcoords(self, value):
        self.arrays[2][:, :2] = value

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
        raise DeprecationWarning("Mesh.texture no longer exists.  Instead, please append textures to the Mesh.textures list.")

    @texture.setter
    def texture(self, value):
        raise DeprecationWarning("Mesh.texture no longer exists.  Instead, please append textures to the Mesh.textures list.")

    @classmethod
    def from_incomplete_data(cls, vertices, normals=(), texcoords=(), **kwargs):
        """Return a Mesh with (vertices, normals, texcoords) as arrays, in that order.
           Useful for when you want a standardized array location format across different amounts of info in each mesh."""
        normals = normals if hasattr(texcoords, '__iter__') and len(normals) else vertutils.calculate_normals(vertices)
        texcoords = texcoords if hasattr(texcoords, '__iter__') and len(texcoords) else np.zeros((vertices.shape[0], 2), dtype=np.float32)
        return cls(arrays=(vertices, normals, texcoords), **kwargs)

    def _fill_vao(self):
        """Put array location in VAO for shader in same order as arrays given to Mesh."""
        with self.vao:
            self.vbos = []
            for loc, verts in enumerate(self.arrays):
                vbo = VBO(verts)
                self.vbos.append(vbo)
                self.vao.assign_vertex_attrib_location(vbo, loc)

    def draw(self):
        """ Draw the Mesh if it's visible, from the perspective of the camera and lit by the light. The function sends the uniforms"""
        if not self.vao:
            self.vao = VAO(indices=self.array_indices)
            self._fill_vao()

        if self.visible:
            if self.dynamic:
                for vbo in self.vbos:
                    vbo._buffer_subdata()

            if self.drawmode == gl.GL_POINTS:
                gl.glPointSize(self.point_size)

            for texture in self.textures:
                texture.bind()

            with self.vao as vao:
                self.uniforms.send()
                vao.draw(mode=self.drawmode)

            for texture in self.textures:
                texture.unbind()
