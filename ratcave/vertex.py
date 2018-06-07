import numpy as np
import pyglet.gl as gl
from .utils import BindingContextMixin, BindNoTargetMixin, BindTargetMixin, create_opengl_object, vec
from sys import platform

class VAO(BindingContextMixin, BindNoTargetMixin):

    bindfun = gl.glBindVertexArray if platform != 'darwin' else gl.glBindVertexArrayAPPLE

    def __init__(self, indices=None, **kwargs):
        """
        OpenGL Vertex Array Object.  Sends array data in a Vertex Buffer to the GPU.  This data can be accessed in
        the vertex shader using the 'layout(location = N)' header line, where N = the index of the array given the VAO.

        Example:  VAO(vertices, normals, texcoords):

        Fragshader:
        layout(location = 0) in vec3 vertexCoord;
        layout(location = 1) in vec2 texCoord;
        layout(location = 2) in vec3 normalCoord;
        """

        # Create Vertex Array Object and Bind it
        super(VAO, self).__init__(**kwargs)
        self.id = create_opengl_object(gl.glGenVertexArrays if platform != 'darwin' else gl.glGenVertexArraysAPPLE)
        self.n_verts = None

        self.drawfun = self._draw_arrays
        self.__element_array_buffer = None
        self.element_array_buffer = indices

    @property
    def element_array_buffer(self):
        return self.__element_array_buffer

    @element_array_buffer.setter
    def element_array_buffer(self, value):
        assert isinstance(value, (np.ndarray, type(None)))
        if isinstance(value, np.ndarray):
            self.__element_array_buffer = ElementArrayBuffer(value)
            self.drawfun = self._draw_elements
        else:
            self.__element_array_buffer = None
            self.drawfun = self._draw_arrays

    def _draw_arrays(self, mode=gl.GL_TRIANGLES):
        gl.glDrawArrays(mode, 0, self.n_verts)

    def _draw_elements(self, mode=gl.GL_TRIANGLES):
        with self.element_array_buffer as el_array:
            gl.glDrawElements(mode, el_array.data.shape[0],
                              gl.GL_UNSIGNED_INT, 0)

    def assign_vertex_attrib_location(self, vbo, location):
        """Load data into a vbo"""
        with vbo:
            if self.n_verts:
                assert vbo.data.shape[0] == self.n_verts
            else:
                self.n_verts = vbo.data.shape[0]

            # vbo.buffer_data()
            gl.glVertexAttribPointer(location, vbo.data.shape[1], gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
            gl.glEnableVertexAttribArray(location)

    def draw(self, mode=gl.GL_TRIANGLES):
        self.drawfun(mode)


class VBO(BindingContextMixin, BindTargetMixin):

    target = gl.GL_ARRAY_BUFFER
    bindfun = gl.glBindBuffer

    def __init__(self, data, *args, **kwargs):
        super(VBO, self).__init__(*args, **kwargs)
        self.id = create_opengl_object(gl.glGenBuffers)
        self.data = data
        self._buffer_data()

    def _buffer_data(self):
        with self:
            gl.glBufferData(self.target, 4 * self.data.size, vec(self.data.ravel()), gl.GL_STATIC_DRAW)

    def _buffer_subdata(self):
        with self:
            gl.glBufferSubData(self.target, 0, 4 * self.data.size, vec(self.data.ravel()))


class ElementArrayBuffer(VBO):

    target = gl.GL_ELEMENT_ARRAY_BUFFER

    def _buffer_data(self):
        with self:
            gl.glBufferData(self.target, 4 * self.data.size, vec(self.data.ravel(), int), gl.GL_STATIC_DRAW)
