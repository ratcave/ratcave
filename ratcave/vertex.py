import numpy as np
import pyglet.gl as gl
from .utils import BindingContextMixin, BindTargetMixin, BindNoTargetMixin, create_opengl_object, vec
from sys import platform


class VertexArray(BindingContextMixin, BindNoTargetMixin):

    bindfun = gl.glBindVertexArray if platform != 'darwin' else gl.glBindVertexArrayAPPLE

    def __init__(self, arrays, indices=None, drawmode=gl.GL_TRIANGLES, **kwargs):
        super(VertexArray, self).__init__(**kwargs)
        self.id = None
        self.arrays = [np.array(vert, dtype=np.float32) for vert in arrays]
        self.indices = np.array(indices, dtype=np.uint32).view(type=ElementArrayBuffer) if not indices is None else indices
        self._loaded = False
        self.drawmode = drawmode


    def load_vertex_array(self):
        self.id = create_opengl_object(gl.glGenVertexArrays if platform != 'darwin' else gl.glGenVertexArraysAPPLE)
        with self:
            for loc, verts in enumerate(self.arrays):
                vbo = verts.view(type=VertexBuffer)
                with vbo:
                    gl.glVertexAttribPointer(loc, verts.shape[1], gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
                    gl.glEnableVertexAttribArray(loc)
                self.arrays[loc] = vbo
        self._loaded = True

    def draw(self):
        if not self._loaded:
            self.load_vertex_array()

        with self:
            if self.indices is None:
                gl.glDrawArrays(self.drawmode, 0, self.arrays[0].shape[0])
            else:
                with self.indices as indices:
                    gl.glDrawElements(self.drawmode, indices.shape[0], gl.GL_UNSIGNED_INT, 0)


class VertexBuffer(BindingContextMixin, BindTargetMixin, np.ndarray):

    target = gl.GL_ARRAY_BUFFER
    bindfun = gl.glBindBuffer

    def __array_finalize__(self, obj):
        if not isinstance(obj, VertexBuffer):  # only do this when creating from arrays (e.g. array.view(type=VBO))
            self.id = create_opengl_object(gl.glGenBuffers)
            with self:
                gl.glBufferData(self.target, 4 * self.size, vec(self.ravel()), gl.GL_STATIC_DRAW)
        return self

    def __setitem__(self, key, value):
        super(VertexBuffer, self).__setitem__(key, value)
        with self:
            gl.glBufferSubData(self.target, 0, 4 * self.size, vec(self.ravel()))


class ElementArrayBuffer(VertexBuffer):
    target = gl.GL_ELEMENT_ARRAY_BUFFER
