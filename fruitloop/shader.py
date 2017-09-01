import abc
from pyglet import gl
from ctypes import byref, create_string_buffer, c_char, c_char_p, c_int, c_float, c_double, cast, pointer, POINTER
import numpy as np
from .utils import gl as ugl
try:
    from UserDict import IterableUserDict# Python 2
except ImportError:
    from collections import UserDict as IterableUserDict  # Python 3
from six import iteritems


class UniformArray(np.ndarray): pass


class UniformCollection(IterableUserDict, object):
    """Dict-like that converts data to arrays and sends all data to a Shader as uniform arrays."""
    # todo: Switch all uniforms functions to array equivalents, to get pointer-passing performance benefit.
    _sendfuns = {'f': [gl.glUniform1f, gl.glUniform2f, gl.glUniform3f, gl.glUniform4f],
                'i':   [gl.glUniform1i, gl.glUniform2i, gl.glUniform3i, gl.glUniform4i]
                }

    def __init__(self, **kwargs):
        super(UniformCollection, self).__init__()
        for key, value in iteritems(kwargs):
            self[key] = value

    def __setitem__(self, key, value):
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, np.ndarray):
            if 'f' in value.dtype.str and value.dtype != np.float32:
                raise TypeError("Matrix Uniform Arrays must be 32-bit floats for rendering to work properly.")
            uniform = value  # Don't copy the data if it's already a numpy array
        else:
            uniform = np.array([value]) if not hasattr(value, '__iter__') else np.array(value)
        uniform = uniform.view(UniformArray)  # Cast as a UniformArray for 'loc' to be set as an attribute later.
        name = key.encode('ascii') if hasattr(key, 'encode') else key
        self.data[name] = uniform

    def send(self):

        for name, array in iteritems(self):

            # Attach a shader location value to the array, for quick memory lookup. (gl calls are expensive, for some reason)
            try:
                loc = array.loc
            except AttributeError:
                shader_id = c_int(0)
                gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, byref(shader_id))
                if shader_id.value == 0:
                    raise UnboundLocalError("Shader not bound to OpenGL context--uniform cannot be sent.")
                array.loc = gl.glGetUniformLocation(shader_id.value, name)
                loc = array.loc

            if array.ndim == 2:  # Assuming a 4x4 float32 matrix (common for graphics operations)
                try:
                    pointer = array.pointer
                except AttributeError:
                    array.pointer = array.ctypes.data_as(POINTER(c_float * 16)).contents
                    pointer = array.pointer
                gl.glUniformMatrix4fv(loc, 1, True, pointer)

            else:
                sendfun = self._sendfuns[array.dtype.kind][len(array) - 1]  # Find correct glUniform function
                sendfun(loc, *array)
    #
    # def update(self, other_dict):
    #     for key, value in iteritems(other_dict):
    #         self[key] = value

class HasUniforms(object):
    """Interface for drawing."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, uniforms=None, **kwargs):
        super(HasUniforms, self).__init__(**kwargs)
        self.uniforms = UniformCollection(**uniforms) if uniforms else UniformCollection()

    @abc.abstractmethod
    def reset_uniforms(self):
        pass


class Shader(ugl.BindingContextMixin, ugl.BindNoTargetMixin):

    bindfun = gl.glUseProgram

    def __init__(self, vert='', frag='', geom=''):
        """
        GLSL Shader program object for rendering in OpenGL.

        Args:
          - vert (str): The vertex shader program  string
          - frag (str): The fragment shader program string
          - geom (str): The geometry shader program
        """
        self.id = gl.glCreateProgram()  # create the program handle
 
        # create the vertex, fragment, and geometry shaders
        self.createShader(vert, gl.GL_VERTEX_SHADER)
        self.createShader(frag, gl.GL_FRAGMENT_SHADER)
        if geom:
            self.createShader(geom, gl.GL_GEOMETRY_SHADER_EXT)
 
        # attempt to link the program
        self.link()

    @classmethod
    def from_file(cls, vert_filename, frag_filename):
        vert_program = open(vert_filename).read()
        frag_program = open(frag_filename).read()
        return cls(vert=vert_program, frag=frag_program)


    def createShader(self, strings, shadertype):
 
        # create the shader handle
        shader = gl.glCreateShader(shadertype)
 
        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        strings = tuple(s.encode('ascii') for s in strings)  # Nick added, for python3
        src = (c_char_p * len(strings))(*strings)
        gl.glShaderSource(shader, len(strings), cast(pointer(src), POINTER(POINTER(c_char))), None)
        # compile the shader
        gl.glCompileShader(shader)

        # retrieve the compile status
        compile_success = c_int(0)
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, byref(compile_success))
 
        # if compilation failed, print the log
        if compile_success:
            gl.glAttachShader(self.id, shader)
        else:
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, byref(compile_success))  # retrieve the log length
            buffer = create_string_buffer(compile_success.value)  # create a buffer for the log
            gl.glGetShaderInfoLog(shader, compile_success, None, buffer)  # retrieve the log text
            print(buffer.value)  # print the log to the console
 
    def link(self):
        """link the program"""
        gl.glLinkProgram(self.id)

        # Check if linking was successful.  If not, print the log.
        link_status = c_int(0)
        gl.glGetProgramiv(self.id, gl.GL_LINK_STATUS, byref(link_status))
        if not link_status:
            gl.glGetProgramiv(self.id, gl.GL_INFO_LOG_LENGTH, byref(link_status))  # retrieve the log length
            buffer = create_string_buffer(link_status.value)  # create a buffer for the log
            gl.glGetProgramInfoLog(self.id, link_status, None, buffer)  # retrieve the log text
            print(buffer.value)  # print the log to the console
