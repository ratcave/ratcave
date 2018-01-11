

import pyglet.gl as gl
from ctypes import byref

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
