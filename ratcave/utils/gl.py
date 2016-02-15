from __future__ import absolute_import

import pyglet.gl as gl
import numpy as np
from collections import namedtuple
from ctypes import byref
import contextlib
from . import texture as tex

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



class FBO(object):

    target = gl.GL_FRAMEBUFFER_EXT

    def __init__(self, texture):

        self._old_viewport_size = (gl.GLint * 4)()
        self.texture = texture
        with self.texture:

            self.id = create_opengl_object(gl.glGenFramebuffersEXT)

            with self:

                # Set Draw and Read locations for the FBO (currently, just turn it off if not doing any color stuff)
                texture.attach_to_fbo()

                if isinstance(texture, tex.DepthTexture):
                    gl.glDrawBuffer(gl.GL_NONE)  # No color in this buffer
                    gl.glReadBuffer(gl.GL_NONE)
                else:
                     # create a render buffer as our temporary depth buffer, bind it, and attach.
                    renderbuffer = tex.RenderBuffer(texture.width, texture.height)
                    renderbuffer.attach_to_fbo()


            # check FBO status (warning appears for debugging)
            FBOstatus = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
            if FBOstatus != gl.GL_FRAMEBUFFER_COMPLETE_EXT:
                raise BufferError("GL_FRAMEBUFFER_COMPLETE failed, CANNOT use FBO.\n{0}\n".format(FBOstatus))



    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        # Store current viewport size
        gl.glGetIntegerv(gl.GL_VIEWPORT, self._old_viewport_size)

        # Bind the FBO
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.id)  # Rendering off-screen

        # Change the Viewport to the texture's viewport size, to make it full-screen.
        gl.glViewport(0, 0, self.texture.width, self.texture.height)

    def unbind(self):
        # Unbind the FBO
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

        # Restore the old viewport size
        gl.glViewport(*self._old_viewport_size)



def vec(floatlist, newtype='float'):
        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """

        if 'float' in newtype:
            return (gl.GLfloat * len(floatlist))(*list(floatlist))
        elif 'int' in newtype:
            return (gl.GLuint * len(floatlist))(*list(floatlist))



class VAO(object):

    def __init__(self, *ndarrays):

        # Create Vertex Array Object and Bind it
        self.id = create_opengl_object(gl.glGenVertexArrays)

        # Create Vertex Buffer Objects and Upload data to them (Vertices)
        with self:
            for idx, ndarray in enumerate(ndarrays):
                self._buffer_data(idx, ndarray)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        gl.glBindVertexArray(self.id)

    def unbind(self):
        gl.glBindVertexArray(0)

    def _buffer_data(self, el, ndarray):
        """Load data into a vbo"""
        with VBO() as vbo:
            vbo.buffer_data(ndarray)
            gl.glVertexAttribPointer(el, ndarray.shape[1], gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
            gl.glEnableVertexAttribArray(el)


class VBO(object):

    target = gl.GL_ARRAY_BUFFER

    def __init__(self):

        self.id = create_opengl_object(gl.glGenBuffers, 1)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        gl.glBindBuffer(self.target, self.id)

    def unbind(self):
        gl.glBindBuffer(self.target, 0)

    def buffer_data(self, ndarray):
        """Sends 2D array (rows for each vertex, column for each coordinate) to the currently-bound VBO"""
        gl.glBufferData(self.target, 4 * ndarray.size,
                        vec(ndarray.ravel()), gl.GL_STATIC_DRAW)



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
