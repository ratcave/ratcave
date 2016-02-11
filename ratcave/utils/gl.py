from __future__ import absolute_import

import pyglet.gl as gl
import numpy as np
from collections import namedtuple
from ctypes import byref
import contextlib
from .texture import Texture, TextureCube, RenderBuffer

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

    def __init__(self, texture=None, renderbuffer=None, slot=0, internal_fmt=gl.GL_RGBA, pixel_fmt=gl.gl.GL_RGBA,
                 attachment_point=gl.GL_COLOR_ATTACHMENT0_EXT):
        self.texture = texture
        self.renderbuffer = renderbuffer
        self.slot = slot

        self.internal_fmt = internal_fmt
        self.pixel_fmt = pixel_fmt
        self.attachment_point = attachment_point


    @classmethod
    def create_color(cls, slot, width, height):
        texture = Texture.create_empty(texture_type, slot=slot, width=width, height=height,
                                           internal_fmt=gl.GL_RGBA, pixel_fmt=gl.gl.GL_RGBA,
                                           attachment_point=gl.GL_COLOR_ATTACHMENT0_EXT)



class FBODepth(FBO):

    def __init__(self, *args, **kwargs):

        assert not kwargs['texture']
        kwargs['internal_fmt'] = gl.GL_DEPTH_COMPONENT
        kwargs['pixel_fmt'] = gl.GL_DEPTH_COMPONENT
        kwargs['attachment_point'] = gl.GL_DEPTH_ATTACHMENT_EXT
        super(FBODepth, self).__init__(*args, **kwargs)



class OldFBO(object):

    def __init__(self, texture_type, width, height, texture_slot=0, color=True, depth=True, grayscale=False):

        assert color or depth, "at least one of the two data types, color or depth, must be set to True."

        # Generate empty texture(s)
        internal_format = gl.GL_DEPTH_COMPONENT if depth and not color else (gl.GL_R8 if grayscale else gl.GL_RGBA)
        pixel_format = gl.GL_DEPTH_COMPONENT if depth and not color else (gl.GL_RED if grayscale else gl.GL_RGBA)
        attachment_point = gl.GL_DEPTH_ATTACHMENT_EXT if depth and not color else gl.GL_COLOR_ATTACHMENT0_EXT

        if texture_type == gl.GL_TEXTURE_2D:
            texture = Texture.create_empty(texture_type, slot=texture_slot, width=width, height=height,
                                           internal_fmt=internal_format, pixel_fmt=pixel_format,
                                           attachment_point=attachment_point)
        elif texture_type == gl.GL_TEXTURE_CUBE_MAP:
            texture = TextureCube.create_empty(texture_type, slot=texture_slot, width=width, height=height,
                                           internal_fmt=internal_format, pixel_fmt=pixel_format,
                                            attachment_point=attachment_point)

        texture.bind()

        # Create FBO and bind it.
        self.target = gl.GL_FRAMEBUFFER_EXT
        self.id = create_opengl_object(gl.glGenFramebuffersEXT)
        self.texture_slot = texture_slot
        self.width = width
        self.height = height

        self.bind()

        # Set Draw and Read locations for the FBO (mostly, turn off if not doing any color stuff)
        if depth and not color:
            gl.glDrawBuffer(gl.GL_NONE)  # No color in this buffer
            gl.glReadBuffer(gl.GL_NONE)

        # Bind texture to FBO.
        gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, texture.attachment_point, texture.target0, texture.id, 0)

        # create a render buffer as our temporary depth buffer, bind it, and attach it to the fbo
        if color and depth:
            renderbuffer = RenderBuffer.create_empty(width, height)
            gl.glFramebufferRenderbufferEXT(self.target, gl.GL_DEPTH_ATTACHMENT_EXT, gl.GL_RENDERBUFFER_EXT,
                                            renderbuffer)

        # check FBO status (warning appears for debugging)
        FBOstatus = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
        if FBOstatus != gl.GL_FRAMEBUFFER_COMPLETE_EXT:
            raise BufferError("GL_FRAMEBUFFER_COMPLETE failed, CANNOT use FBO.\n{0}\n".format(FBOstatus))

        #Unbind FBO and return it and its texture
        self.unbind()

        return FBO(fbo, texture, texture_slot, (width, height))

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.id)

    def unbind(self):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)


@contextlib.contextmanager
def render_to_fbo(window, fbo):
    """A context manager that sets the framebuffer target and resizes the viewport before and after the draw commands."""
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fbo.id)  # Rendering off-screen
    gl.glViewport(0, 0, fbo.width, fbo.height)
    yield
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
    gl.glViewport(0, 0, self.window.width, self.window.height)


def vec(floatlist, newtype='float'):
        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """

        if 'float' in newtype:
            return (gl.GLfloat * len(floatlist))(*list(floatlist))
        elif 'int' in newtype:
            return (gl.GLuint * len(floatlist))(*list(floatlist))



class VAO(object):

    def __init__(self, vertices, normals, texture_uvs):

        # Create Vertex Array Object and Bind it
        self.id = create_opengl_object(gl.glGenVertexArrays)
        gl.glBindVertexArray(self.id)

        # Create Vertex Buffer Object and Bind it (Vertices)
        vbo = create_opengl_object(gl.glGenBuffers, 3)

        # Upload Data to the VBO
        self._buffer_data(0, vbo[0], vertices)  # Vertex Coordinates
        self._buffer_data(1, vbo[1], normals)  # Normal Coordinates
        self._buffer_data(1, vbo[2], texture_uvs)  # Texture UV Coordinates

        # Everything is now assigned and all data passed to the GPU.  Can unbind VAO and VBO now.
        gl.glBindVertexArray(0)

    def __enter__(self):
        gl.glBindVertexArray(self.id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        gl.glBindVertexArray(0)

    def _buffer_data(self, el, vbo_id, array):
        """Load data into a vbo"""
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 4 * array.size,
                        vec(array.ravel()), gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(el, array.shape[1], gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(el)


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
