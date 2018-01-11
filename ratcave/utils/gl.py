

import pyglet.gl as gl
from ctypes import byref
import numpy as np

POINTS = gl.GL_POINTS
TRIANGLES = gl.GL_TRIANGLES
LINE_LOOP = gl.GL_LINE_LOOP
LINES = gl.GL_LINES


def create_opengl_object(gl_gen_function, n=1):
    """Returns int pointing to an OpenGL texture"""
    handle = gl.GLuint(1)
    gl_gen_function(n, byref(handle))  # Create n Empty Objects
    if n > 1:
        return [handle.value + el for el in range(n)]  # Return list of handle values
    else:
        return handle.value  # Return handle value


def vec(data, dtype=float):
        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """
        gl_types = {float: gl.GLfloat, int: gl.GLuint}
        try:
            gl_dtype = gl_types[dtype]
        except KeyError:
            raise TypeError('dtype not recognized.  Recognized types are int and float')

        if gl_dtype == gl.GLuint:
            for el in data:
                if el < 0:
                    raise ValueError("integer ratcave.vec arrays are unsigned--negative values are not supported.")

        return (gl_dtype * len(data))(*data)



class BindingContextMixin(object):
    """Mixin that calls self.bind() and self.unbind() when used in a context manager."""

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()


class BindTargetMixin(object):
    """Mixin that speifices a bind() and unbind() interface by taking advantage of the OpenGL bind format:
    bind: bindfun(target, id)
    unbind: bindfun(target, 0)
    """

    bindfun = None
    _bound = None

    def bind(self):
        self.bindfun(self.target, self.id)
        self.__class__._bound = self

    @classmethod
    def unbind(cls):
        cls.bindfun(cls.target, 0)
        cls._bound = None


class BindNoTargetMixin(BindTargetMixin):
    """Same as BindTargetMixin, but for bind functions that don't have a specified target."""

    _bound = None

    def bind(self):
        self.bindfun(self.id)
        self.__class__._bound = self

    @classmethod
    def unbind(cls):
        cls.bindfun(0)
        cls._bound = None
