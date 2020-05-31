import itertools
import numpy as np
from . import gl
from .utils import BindingContextMixin, BindNoTargetMixin, BindTargetMixin, create_opengl_object, vec
from sys import platform


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def reindex_vertices(arrays=None):
    all_arrays = np.hstack(arrays)
    array_ncols = tuple(array.shape[1] for array in arrays)

    # Build a new array list, composed of only the unique combinations  (no redundant data)
    row_searchable_array = all_arrays.view(all_arrays.dtype.descr * all_arrays.shape[1])
    unique_combs = np.sort(np.unique(row_searchable_array))

    new_indices = np.array([np.searchsorted(unique_combs, vert) for vert in row_searchable_array]).flatten().astype(np.uint32)

    ucombs = unique_combs.view(unique_combs.dtype[0]).reshape((unique_combs.shape[0], -1))
    new_arrays = tuple(ucombs[:, start:end] for start, end in pairwise(np.append(0, np.cumsum(array_ncols))))
    new_arrays = tuple(np.array(array, dtype=np.float32) for array in new_arrays)
    return new_arrays, new_indices


class VertexArray(BindingContextMixin, BindNoTargetMixin):

    bindfun = gl.glBindVertexArray if platform != 'darwin' else gl.glBindVertexArrayAPPLE

    def __init__(self, arrays, indices=None, drawmode=gl.GL_TRIANGLES, reindex=True, **kwargs):
        super(VertexArray, self).__init__(**kwargs)
        if indices is None and reindex:
            arrays, indices = reindex_vertices(arrays)  # Indexing
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
