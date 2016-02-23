from __future__ import absolute_import
from __future__ import print_function

#
# Copyright Tristam Macdonald 2008
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#

from pyglet.gl import *
from ctypes import *
# from six.moves import range
import numpy as np


class Uniform(object):

    _sendfuns = {'f': [glUniform1f, glUniform2f, glUniform3f, glUniform4f],
                'i':   [glUniform1i, glUniform2i, glUniform3i, glUniform4i]
                }

    def __init__(self, name, *vals):
        """An array with a paired glUniform function, for quick shader data sending."""
        self.name = name
        assert len(vals) > 0 and len(vals) <= 4
        self._value = np.array(vals)  # A semi-mutable array, in that its length can't be modified.
        self.sendfun = Uniform._sendfuns[self._value.dtype.kind][len(self._value) - 1]

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
        uniform_loc = glGetUniformLocation(shader.handle, self.name)
        self.sendfun(uniform_loc, *self.value)
        return uniform_loc

    @classmethod
    def from_dict(cls, data_dict):
        """A factory function that can build multiple uniforms from a name: val dictionary"""
        # Change all kwarg values to a sequence, to be put into Uniform
        for key, val in data_dict.items():
            if not isinstance(val, (list, tuple)):
                data_dict[key] = [val]

        return [cls(key, *val) for key, val in data_dict.items()]


# class UniformCollection(object):
#
#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             setattr(self, key, Uniform(key, *value))
#
#     def __setattr__(self, name, value):
#         if name not in self.__dict__:
#             self.setclassattr(name, value)  # Create a class attribute
#         else:
#             self.__dict__[name].value[:] = value  # Insert new value into Uniform.value
#
#         self.__dict__[name] = value
#
#     @classmethod
#     def setclassattr(cls, name, value):
#         setattr(cls, name, value)  # Create a class attribute
#
#     def __getattr__(self, name):
#         if name in self.__dict__:
#             return self.__dict__[name].value







class Shader:
    # vert, frag and geom take arrays of source strings
    # the arrays will be concattenated into one string by OpenGL
    def __init__(self, vert = [], frag = [], geom = []):
        # create the program handle
        self.handle = glCreateProgram()
        # we are not linked yet
        self.linked = False
 
        # create the vertex shader
        self.createShader(vert, GL_VERTEX_SHADER)
        # create the fragment shader
        self.createShader(frag, GL_FRAGMENT_SHADER)
        # the geometry shader will be the same, once pyglet supports the extension
        # self.createShader(frag, GL_GEOMETRY_SHADER_EXT)
 
        # attempt to link the program
        self.link()

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()
 
    def createShader(self, strings, type):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return
 
        # create the shader handle
        shader = glCreateShader(type)
 
        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        strings = [s.encode('ascii') for s in strings]  # Nick added, for python3
        src = (c_char_p * count)(*strings)
        glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)
 
        # compile the shader
        glCompileShader(shader)
 
        temp = c_int(0)
        # retrieve the compile status
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))
 
        # if compilation failed, print the log
        if not temp:
            # retrieve the log length
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            glGetShaderInfoLog(shader, temp, None, buffer)
            # print the log to the console
            print(buffer.value)
        else:
            # all is well, so attach the shader to the program
            glAttachShader(self.handle, shader);
 
    def link(self):
        # link the program
        glLinkProgram(self.handle)
 
        temp = c_int(0)
        # retrieve the link status
        glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))
 
        # if linking failed, print the log
        if not temp:
            #   retrieve the log length
            glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            glGetProgramInfoLog(self.handle, temp, None, buffer)
            # print the log to the console
            print(buffer.value)
        else:
            # all is well, so we are linked
            self.linked = True
 
    def bind(self):
        # bind the program
        glUseProgram(self.handle)
 
    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        glUseProgram(0)
 
    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1f,
                2 : glUniform2f,
                3 : glUniform3f,
                4 : glUniform4f
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)
            # }[len(vals)](glGetUniformLocation(self.handle, name.encode('ascii')), *vals)

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : glUniform1i,
                2 : glUniform2i,
                3 : glUniform3i,
                4 : glUniform4i
                # retrieve the uniform location, and set
            }[len(vals)](glGetUniformLocation(self.handle, name), *vals)
            # }[len(vals)](glGetUniformLocation(self.handle, name.encode('ascii')), *vals)

    # upload a uniform matrix
    # works with matrices stored as lists,
    # as well as euclid matrices
    def uniform_matrixf(self, name, mat):
        # obtian the uniform location
        loc = glGetUniformLocation(self.handle, name)
        # uplaod the 4x4 floating point matrix
        glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))

    def uniform_gen(self, uniform):
        """Sends the data in a Uniform object"""
        uniform.sendfun(glGetUniformLocation(self.handle, uniform.name), uniform.value)