

import pyglet.gl as gl
from ctypes import byref
import contextlib
import numpy as np

def create_opengl_object(gl_gen_function, n=1):
    """Returns int pointing to an OpenGL texture"""
    handle = gl.GLuint(1)
    gl_gen_function(n, byref(handle))  # Create n Empty Objects
    if n > 1:
        return [handle.value + el for el in range(n)]  # Return list of handle values
    else:
        return handle.value  # Return handle value


@contextlib.contextmanager
def enable_states(gl_states):
    """Context Manager that calls glEnable and glDisable on a list of gl states."""
    for state in gl_states:
        gl.glEnable(state)
    yield
    for state in gl_states:
        gl.glDisable(state)



def vec(floatlist, newtype='float'):
        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """

        if 'float' in newtype:
            return (gl.GLfloat * len(floatlist))(*list(floatlist))
        elif 'int' in newtype:
            return (gl.GLuint * len(floatlist))(*list(floatlist))

class GlGenMixin(object):

    genfun = None

    def __init__(self, *args, **kwargs):
        super(GlGenMixin, self).__init__(*args, **kwargs)
        self.id = create_opengl_object(self.genfun)



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

    def bind(self):
        self.bindfun(self.target, self.id)

    @classmethod
    def unbind(cls):
        cls.bindfun(cls.target, 0)


class BindNoTargetMixin(BindTargetMixin):
    """Same as BindTargetMixin, but for bind functions that don't have a specified target."""

    def bind(self):
        self.bindfun(self.id)

    @classmethod
    def unbind(cls):
        cls.bindfun(0)


class VAO(GlGenMixin, BindingContextMixin, BindNoTargetMixin):

    genfun = gl.glGenVertexArrays
    bindfun = gl.glBindVertexArray

    def __init__(self, indices=None, **kwargs):
        """
        OpenGL Vertex Array Object.  Sends array data in a Vertex Buffer to the GPU.  This data can be accessed in
        the vertex shader using the 'layout(location = N)' header line, where N = the index of the array given the VAO.

        Example:  VAO(vertices, normals, texcoords):

        Fragshader:
        layout(location = 0) in vec3 vertexCoord;
        layout(location = 1) in vec2 texCoord;
        layout(location = 2) in vec3 normalCoord;
        """

        # Create Vertex Array Object and Bind it
        super(VAO, self).__init__(**kwargs)
        self.n_verts = None

        self.drawfun = self._draw_arrays
        self.__element_array_buffer = None
        self.element_array_buffer = indices

    @property
    def element_array_buffer(self):
        return self.__element_array_buffer

    @element_array_buffer.setter
    def element_array_buffer(self, value):
        assert isinstance(value, (np.ndarray, type(None)))
        if isinstance(value, np.ndarray):
            self.__element_array_buffer = ElementArrayBuffer(value)
            self.drawfun = self._draw_elements
        else:
            self.__element_array_buffer = None
            self.drawfun = self._draw_arrays

    def _draw_arrays(self, mode=gl.GL_TRIANGLES):
        gl.glDrawArrays(mode, 0, self.n_verts)

    def _draw_elements(self, mode=gl.GL_TRIANGLES):
        with self.element_array_buffer as el_array:
            gl.glDrawElements(mode, el_array.ndarray.shape[0],
                              gl.GL_UNSIGNED_INT, 0)

    def assign_vertex_attrib_location(self, vbo, location):
        """Load data into a vbo"""
        with vbo:
            if self.n_verts:
                assert vbo.ndarray.shape[0] == self.n_verts
            else:
                self.n_verts = vbo.ndarray.shape[0]

            # vbo.buffer_data()
            gl.glVertexAttribPointer(location, vbo.ndarray.shape[1], gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
            gl.glEnableVertexAttribArray(location)

    def draw(self, mode=gl.GL_TRIANGLES):
        self.drawfun(mode)


class VBO(GlGenMixin, BindingContextMixin, BindTargetMixin):

    genfun = gl.glGenBuffers
    target = gl.GL_ARRAY_BUFFER
    bindfun = gl.glBindBuffer

    def __init__(self, ndarray, *args, **kwargs):
        super(VBO, self).__init__(*args, **kwargs)
        self.ndarray = ndarray
        self._buffer_data()

    def _buffer_data(self):
        with self:
            gl.glBufferData(self.target, 4 * self.ndarray.size, vec(self.ndarray.ravel()), gl.GL_STATIC_DRAW)


class ElementArrayBuffer(VBO):

    target = gl.GL_ELEMENT_ARRAY_BUFFER

    def __init__(self, *args, **kwargs):
        super(ElementArrayBuffer, self).__init__(*args, **kwargs)

    def _buffer_data(self):
        with self:
            gl.glBufferData(self.target, 4 * self.ndarray.size, vec(self.ndarray.ravel(), 'int'), gl.GL_STATIC_DRAW)


def setpriority(pid=None,priority=1):
    
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """
        
    import win32api,win32process,win32con
    
    priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                       win32process.BELOW_NORMAL_PRIORITY_CLASS,
                       win32process.NORMAL_PRIORITY_CLASS,
                       win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                       win32process.HIGH_PRIORITY_CLASS,
                       win32process.REALTIME_PRIORITY_CLASS]
    if pid == None:
        pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, priorityclasses[priority])	
