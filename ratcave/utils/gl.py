import pyglet.gl as pyglet_gl
from ctypes import byref
from collections import namedtuple
import itertools as it


class Enum(int):
    """Prints enum name, instead of the int value.  Makes working with OpenGL easier."""
    def __new__(cls, name_value, *args, **kwargs):
        if isinstance(name_value, int) and name_value == 4:  # Because of some not-understood behavior during pickle.load()
            return super(Enum, cls).__new__(cls, name_value)
        name, value = name_value
        obj = super(Enum, cls).__new__(cls, value)
        obj.name = name
        return obj

    def __repr__(self):
        return self.name

for module in [pyglet_gl, pyglet_gl.gl]:
    for name in dir(module):
        attr = getattr(module, name)
        if isinstance(getattr(module, name), int):
            locals()[name] = Enum((name, attr))
        elif not name.startswith('_') and name not in ['pyglet', 'gl']:
            locals()[name] = attr


def create_opengl_object(gl_gen_function, n=1):
    """Returns int pointing to an OpenGL texture"""
    handle = pyglet_gl.GLuint(1)
    gl_gen_function(n, byref(handle))  # Create n Empty Objects
    if n > 1:
        return [handle.value + el for el in range(n)]  # Return list of handle values
    else:
        return handle.value  # Return handle value


def vec(data, dtype=float):
        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """
        gl_types = {float: pyglet_gl.GLfloat, int: pyglet_gl.GLuint}
        try:
            gl_dtype = gl_types[dtype]
        except KeyError:
            raise TypeError('dtype not recognized.  Recognized types are int and float')

        if gl_dtype == pyglet_gl.GLuint:
            for el in data:
                if el < 0:
                    raise ValueError("integer ratcave.vec arrays are unsigned--negative values are not supported.")

        return (gl_dtype * len(data))(*data)


Viewport = namedtuple('Viewport', 'x y width height')

def get_viewport():
    data = (pyglet_gl.GLint * 4)()
    pyglet_gl.glGetIntegerv(pyglet_gl.GL_VIEWPORT, data)
    return Viewport(*data)


def clear_color(r, g, b):
    pyglet_gl.glClearColor(r, g, b, 1.)
    pyglet_gl.glClear(pyglet_gl.GL_COLOR_BUFFER_BIT | pyglet_gl.GL_DEPTH_BUFFER_BIT)