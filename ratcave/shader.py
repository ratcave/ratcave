from pyglet.gl import *
from ctypes import *
import numpy as np
from .utils import gl as ugl

class Uniform(object):

    _sendfuns = {'f': [glUniform1f, glUniform2f, glUniform3f, glUniform4f],
                'i':   [glUniform1i, glUniform2i, glUniform3i, glUniform4i]
                }

    def __init__(self, name, *vals):
        """A fixed-length, fixed-type array with a pre-assigned glUniform function for quick shader data sending."""
        self.name = name.encode('ascii')
        assert len(vals) > 0 and len(vals) <= 4
        self._value = np.array(vals)  # A semi-mutable array, in that its length can't be modified.
        self.sendfun = Uniform._sendfuns[self._value.dtype.kind][len(self._value) - 1]
        self._uniform_loc = None

    def __repr__(self):
        return '{}{}'.format(self.name, tuple(self.value.tolist()))

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, item, value):
        self.value[item] = value

    @property
    def value(self):
        return self._value

    def send_to(self, shader):
        """Sends uniform to a currently-bound shader, returning its location (-1 means not sent)"""
        # glGetUniformLocation only needs to be called once, when the shader is linked.  Not a big performance boost, though.
        if type(self._uniform_loc) == type(None):
            self._uniform_loc = glGetUniformLocation(shader.id, self.name)

        self.sendfun(self._uniform_loc, *self.value)
        return self._uniform_loc


    @classmethod
    def from_dict(cls, data_dict):
        """A factory function that can build multiple uniforms from a name: val dictionary"""
        # Change all kwarg values to a sequence, to be put into Uniform
        for key, val in list(data_dict.items()):
            if not isinstance(val, (list, tuple)):
                data_dict[key] = [val]

        return [cls(key, *val) for key, val in list(data_dict.items())]


class UniformCollection(object):

    def __init__(self, uniform_dict={}):
        self._uniforms = {}
        for key, value in uniform_dict.items():
            self[key] = value

    def __setitem__(self, key, value):

        if type(value) == Uniform:
            self._uniforms[key] = value

        elif type(value) != Uniform:
            # try:
            # if key in self._uniforms:
            try:
                self._uniforms[key].value[:] = value
            except KeyError:
                value = Uniform(key, *value)
                self._uniforms[key] = value
            except:
                raise TypeError("Attempt to add uniform {} to UniformCollection failed.".format(key))

    def __getitem__(self, key):
        return self._uniforms[key]

    def __str__(self):
        return "UniformCollection: {}".format(self._uniforms)

    def __repr__(self):
        return self.__str__()

    def send_to(self, shader):
        for uniform in self._uniforms.values():
            uniform.send_to(shader)


#
# Copyright Tristam Macdonald 2008
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#


class Shader(ugl.BindingContextMixin, ugl.BindNoTargetMixin):

    bindfun = glUseProgram
    uniformf_funs = (glUniform1f, glUniform2f, glUniform3f, glUniform4f)
    uniformi_funs = (glUniform1i, glUniform2i, glUniform3i, glUniform4i)

    def __init__(self, vert='', frag='', geom=''):
        """
        GLSL Shader program object for rendering in OpenGL.

        Args:
          - vert (str): The vertex shader program  string
          - frag (str): The fragment shader program string
          - geom (str): The geometry shader program
        """
        self.id = glCreateProgram()  # create the program handle
 
        # create the vertex, fragment, and geometry shaders
        self.createShader(vert, GL_VERTEX_SHADER)
        self.createShader(frag, GL_FRAGMENT_SHADER)
        if geom:
            self.createShader(geom, GL_GEOMETRY_SHADER_EXT)
 
        # attempt to link the program
        self.link()
 
    def createShader(self, strings, shadertype):
 
        # create the shader handle
        shader = glCreateShader(shadertype)
 
        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        strings = tuple(s.encode('ascii') for s in strings)  # Nick added, for python3
        src = (c_char_p * len(strings))(*strings)
        glShaderSource(shader, len(strings), cast(pointer(src), POINTER(POINTER(c_char))), None)
 
        # compile the shader
        glCompileShader(shader)

        # retrieve the compile status
        compile_success = c_int(0)
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(compile_success))
 
        # if compilation failed, print the log
        if compile_success:
            glAttachShader(self.id, shader)
        else:
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(compile_success))  # retrieve the log length
            buffer = create_string_buffer(compile_success.value)  # create a buffer for the log
            glGetShaderInfoLog(shader, compile_success, None, buffer)  # retrieve the log text
            print(buffer.value)  # print the log to the console
 
    def link(self):
        """link the program"""
        glLinkProgram(self.id)

        # Check if linking was successful.  If not, print the log.
        link_status = c_int(0)
        glGetProgramiv(self.id, GL_LINK_STATUS, byref(link_status))
        if not link_status:
            glGetProgramiv(self.id, GL_INFO_LOG_LENGTH, byref(link_status))  # retrieve the log length
            buffer = create_string_buffer(link_status.value)  # create a buffer for the log
            glGetProgramInfoLog(self.id, link_status, None, buffer)  # retrieve the log text
            print(buffer.value)  # print the log to the console

    def uniformf(self, name, *vals):
        """Send data as a float uniform, named 'name'.  Shader must be already bound."""
        self.uniformf_funs[len(vals)-1](glGetUniformLocation(self.id, name.encode('ascii')), *vals)

    def uniformi(self, name, *vals):
        """Send data as an integer uniform, named 'name'.  Shader must be already bound."""
        self.uniformi_funs[len(vals)-1](glGetUniformLocation(self.id, name.encode('ascii')), *vals)

    def uniform_matrixf(self, name, mat):
        """Send 4x4 NumPy matrix data as a uniform to the shader, named 'name'. Shader must be already bound."""
        # obtain the uniform location
        loc = glGetUniformLocation(self.id, name.encode('ascii'))
        glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))  # uplaod the 4x4 floating point matrix
