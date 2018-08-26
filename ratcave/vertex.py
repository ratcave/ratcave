import numpy as np
import pyglet.gl as gl
from .utils import BindingContextMixin, BindTargetMixin, create_opengl_object, vec


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
