import numpy as np
import pyglet.gl as gl
from .utils import BindingContextMixin, BindNoTargetMixin, BindTargetMixin, create_opengl_object, vec
from sys import platform

class VAO(BindingContextMixin, BindNoTargetMixin):

    bindfun = gl.glBindVertexArray if platform != 'darwin' else gl.glBindVertexArrayAPPLE

    def __init__(self, *arrays, indices=None, **kwargs):
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
        if not indices is None:
            raise NotImplementedError("ElementArrays have been temporarily removed for refactoring.")  # TODO: re-implement ElementArrays and indexing


        super(VAO, self).__init__(**kwargs)
        self.id = create_opengl_object(gl.glGenVertexArrays if platform != 'darwin' else gl.glGenVertexArraysAPPLE)

        self.drawfun = self._draw_arrays

        with self:
            self.vbos = []
            for loc, verts in enumerate(arrays):
                vbo = verts.view(type=VBO)
                with vbo:
                    gl.glVertexAttribPointer(loc, verts.shape[1], gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
                    gl.glEnableVertexAttribArray(loc)
                self.vbos.append(vbo)

    def draw(self, mode=gl.GL_TRIANGLES):
        gl.glDrawArrays(mode, 0, self.vbos[0].shape[0])


class VBO(BindingContextMixin, BindTargetMixin, np.ndarray):

    target = gl.GL_ARRAY_BUFFER
    bindfun = gl.glBindBuffer

    def __array_finalize__(self, obj):
        if not isinstance(obj, VBO):
            self.id = create_opengl_object(gl.glGenBuffers)
            with self:
                gl.glBufferData(self.target, 4 * self.size, vec(self.ravel()), gl.GL_STATIC_DRAW)
        return self

    # def _buffer_subdata(self):
    #     with self:
    #         gl.glBufferSubData(self.target, 0, 4 * self.data.size,
    #                            vec(self.data.ravel()))