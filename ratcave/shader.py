import abc
from pyglet import gl
from ctypes import byref, create_string_buffer, c_char, c_char_p, c_int, c_float, c_double, cast, pointer, POINTER
import numpy as np
from .utils import BindingContextMixin, BindNoTargetMixin
try:
    from UserDict import IterableUserDict  # Python 2
except ImportError:
    from collections import UserDict as IterableUserDict  # Python 3
from six import iteritems


class UniformArray(np.ndarray): pass


class UniformCollection(IterableUserDict, object):
    # todo: Switch all uniforms functions to array equivalents, to get pointer-passing performance benefit.
    _sendfuns = {'f': [gl.glUniform1f, gl.glUniform2f, gl.glUniform3f, gl.glUniform4f],
                'i':   [gl.glUniform1i, gl.glUniform2i, gl.glUniform3i, gl.glUniform4i]
                }

    def __init__(self, **kwargs):
        """Returns a dict-like collection of arrays that can copy itself to shader programs as GLSL Uniforms.

        Uniforms can be thought of as pipes to the program on the graphics card.  Variables set in UniformCollection can
          be directly used in the grpahics card.


        Example::

            uniforms = UniformCollection()
            uniforms['diffuse'] = 1., 1., 0.
            uniforms['model_matrix'] = numpyp.eye(4)

        In the shader, this would be used by initializing the uniform variable, for example::

            uniform vec3 diffuse;
            uniform mat4 model_matrix;

        Any key-value pairs are sent to a bound shader program when UniformCollection.send() is called.

        More information about GLSL Uniforms can be found at https://www.khronos.org/opengl/wiki/Uniform_(GLSL)

        .. note:: This class isn't usually constructed directly.  It can be found as 'uniforms' attributes
        of Meshes and Cameras.
        """

        super(UniformCollection, self).__init__()
        for key, value in iteritems(kwargs):
            self.data[key] = value

    def __setitem__(self, key, value):

        # name = key.encode('ascii') if hasattr(key, 'encode') else key
        if key in self.data:
            self.data[key][:] = value
            return

        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, np.ndarray):
            if 'f' in value.dtype.str and value.dtype != np.float32:
                raise TypeError("Matrix Uniform Arrays must be 32-bit floats for rendering to work properly.")
            uniform = value  # Don't copy the data if it's already a numpy array
        else:
            uniform = np.array([value]) if not hasattr(value, '__iter__') else np.array(value)

        uniform_view = uniform.view(UniformArray)  # Cast as a UniformArray for 'loc' to be set as an attribute later.
        self.data[key] = uniform_view

    def __delitem__(self, key):
        del self.data[key]

    def send(self):
        """
        Sends all the key-value pairs to the graphics card.
        These uniform variables will be available in the currently-bound shader.
        """

        for name, array in iteritems(self):

            shader_id = c_int(0)
            gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM, byref(shader_id))
            if shader_id.value == 0:
                raise UnboundLocalError("""Shader not bound to OpenGL context--uniform cannot be sent.
                ------------ Tip -------------
                with ratcave.default_shader:
                    mesh.draw()
                ------------------------------
                """)

            # Attach a shader location value to the array, for quick memory lookup. (gl calls are expensive, for some reason)
            try:
                loc, shader_id_for_array = array.loc
                if shader_id.value != shader_id_for_array:
                    raise Exception('Uniform location bound to a different shader')
            except (AttributeError, Exception) as e:
                array.loc = (gl.glGetUniformLocation(shader_id.value, name.encode('ascii')), shader_id.value)

            if array.ndim == 2:  # Assuming a 4x4 float32 matrix (common for graphics operations)
                try:
                    pointer = array.pointer
                except AttributeError:
                    array.pointer = array.ctypes.data_as(POINTER(c_float * 16)).contents
                    pointer = array.pointer
                gl.glUniformMatrix4fv(array.loc[0], 1, True, pointer)

            else:
                sendfun = self._sendfuns[array.dtype.kind][len(array) - 1]  # Find correct glUniform function
                sendfun(array.loc[0], *array)
    #
    # def update(self, other_dict):
    #     for key, value in iteritems(other_dict):
    #         self[key] = value

class HasUniforms(object):
    """Interface for drawing.  Ensures that there is a uniforms attribute to the class, which can be reset upond demand."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, uniforms=None, **kwargs):
        super(HasUniforms, self).__init__(**kwargs)
        self.uniforms = UniformCollection(**uniforms) if uniforms else UniformCollection()

    @abc.abstractmethod
    def reset_uniforms(self):
        pass


class HasUniformsUpdater(HasUniforms):
    """HasUniforms can not inherit from Observer, we need something on the level of Mesh, that can update the uniforms"""
    def __init__(self, **kwargs):
        self._uniforms = None
        super(HasUniformsUpdater, self).__init__(**kwargs)
        if not hasattr(self, 'update'):
            raise AttributeError("HasUniformsUpdater needs update() method to work.")

    @property
    def uniforms(self):
        """
        The dict-like collection of uniform values.  To send data to the graphics card, simply add it as a key-value pair.

        Example::

            mesh.uniforms['diffuse'] = 1., 1., 0.  # Will sends a 3-value vector of floats to the graphics card, when drawn.
        """
        self.update()
        return self._uniforms

    @uniforms.setter
    def uniforms(self, value):
        self._uniforms = value


class Shader(BindingContextMixin, BindNoTargetMixin):

    bindfun = gl.glUseProgram

    def __init__(self, vert='', frag='', geom='', lazy=False):
        """
        GLSL Shader program object for rendering in OpenGL.
        To activate, call the Shader.bind() method, or pass it to a context manager (the 'with' statement).

        Examples and inspiration for shader programs can found at https://www.shadertoy.com/.

        Args:
          - vert (str): The vertex shader program  string
          - frag (str): The fragment shader program string
          - geom (str): The geometry shader program

        Example::

            shader = Shader.from_file(vert='vertshader.vert', frag='fragshader.frag')
            with shader:
                mesh.draw()

        """
        self.id = gl.glCreateProgram()  # create the program handle
        self.is_linked = False
        self.is_compiled = False
        self.vert = vert
        self.frag = frag
        self.geom = geom
        self.lazy = lazy

        if not self.lazy:
            self.compile()


    def compile(self):
        # create the vertex, fragment, and geometry shaders
        self._createShader(self.vert, gl.GL_VERTEX_SHADER)
        self._createShader(self.frag, gl.GL_FRAGMENT_SHADER)
        if self.geom:
            self._createShader(self.geom, gl.GL_GEOMETRY_SHADER_EXT)
        self.is_compiled = True

    def bind(self):
        """Activate this Shader, making it the currently-bound program.

        Any Mesh.draw() calls after bind() will have their data processed by this Shader.  To unbind, call Shader.unbind().

        Example::

           shader.bind()
           mesh.draw()
           shader.unbind()

        .. note:: Shader.bind() and Shader.unbind() can be also be called implicitly by using the 'with' statement.

        Example of with statement with Shader::
            with shader:
                mesh.draw()
        """
        if not self.is_linked:
            if not self.is_compiled:
                self.compile()
            self.link()
        super(self.__class__, self).bind()

    @classmethod
    def from_file(cls, vert, frag, **kwargs):
        """
        Reads the shader programs, given the vert and frag filenames

        Arguments:
            - vert (str): The filename of the vertex shader program (ex: 'vertshader.vert')
            - frag (str): The filename of the fragment shader program (ex: 'fragshader.frag')

        Returns:
            - shader (Shader): The Shader using these files.
        """
        vert_program = open(vert).read()
        frag_program = open(frag).read()
        return cls(vert=vert_program, frag=frag_program, **kwargs)


    def _createShader(self, strings, shadertype):

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
        """link the program, making it the active shader.

        .. note:: Shader.bind() is preferred here, because link() Requires the Shader to be compiled already.
        """
        gl.glLinkProgram(self.id)

        # Check if linking was successful.  If not, print the log.
        link_status = c_int(0)
        gl.glGetProgramiv(self.id, gl.GL_LINK_STATUS, byref(link_status))
        if not link_status:
            gl.glGetProgramiv(self.id, gl.GL_INFO_LOG_LENGTH, byref(link_status))  # retrieve the log length
            buffer = create_string_buffer(link_status.value)  # create a buffer for the log
            gl.glGetProgramInfoLog(self.id, link_status, None, buffer)  # retrieve the log text
            print(buffer.value)  # print the log to the console

        self.is_linked = True
