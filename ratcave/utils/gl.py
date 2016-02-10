from __future__ import absolute_import

import pyglet.gl as gl
import numpy as np
from collections import namedtuple
from ctypes import byref
import contextlib

class TextureBase(object):
    def __init__(self):
        """Does nothing but solve missing conditional contex manager feature in Python 2.7"""
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Texture(TextureBase):

    def __init__(self, target, id, slot=2, uniform_name='TextureMap'):
        super(Texture, self).__init__()
        self.target = target
        self.id = id
        self.slot = slot
        self.uniform_name = uniform_name

    def __enter__(self):
        super(Texture, self).__enter__()
        gl.glBindTexture(self.target, self.id)
        gl.glActiveTexture(getattr(gl, 'GL_TEXTURE{}'.format(self.slot)))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Texture, self).__exit__()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self.target, 0)

    def send_to(self, shaderHandle):
           gl.glUniform1i(gl.glGetUniformLocation(shaderHandle, self.uniform_name), self.slot)



class TextureCube(Texture):
    def __init__(self, *args, **kwargs):
        super(TextureCube, self).__init__(*args, target=gl.GL_TEXTURE_CUBE_MAP, **kwargs)


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

FBO = namedtuple('FBO', 'id texture texture_slot size')
def create_fbo(texture_type, width, height, texture_slot=0, color=True, depth=True, grayscale=False):

    assert color or depth, "at least one of the two data types, color or depth, must be set to True."

    # Make a texture and bind it.
    gl.glActiveTexture(gl.GL_TEXTURE0 + texture_slot)
    texture = create_opengl_object(gl.glGenTextures)  # Create a general texture
    gl.glBindTexture(texture_type, texture)  # Bind it.

    # Apply texture settings for interpolation behavior (Required)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    if texture_type == gl.GL_TEXTURE_CUBE_MAP:
        gl.glTexParameterf(texture_type, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    # Generate empty texture(s)
    internal_format = gl.GL_DEPTH_COMPONENT if depth and not color else (gl.GL_R8 if grayscale else gl.GL_RGBA)
    pixel_format = gl.GL_DEPTH_COMPONENT if depth and not color else (gl.GL_RED if grayscale else gl.GL_RGBA)

    if texture_type == gl.GL_TEXTURE_2D:
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal_format, width, height, 0,
                pixel_format, gl.GL_UNSIGNED_BYTE, 0)
    elif texture_type == gl.GL_TEXTURE_CUBE_MAP:
        # Generate blank textures, one for each cube face.
        for face in range(0, 6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face, 0, internal_format,
                            width, height, 0, pixel_format, gl.GL_UNSIGNED_BYTE, 0)

    # Create FBO and bind it.
    fbo = create_opengl_object(gl.glGenFramebuffersEXT)
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fbo)

    # Set Draw and Read locations for the FBO (mostly, turn off if not doing any color stuff)
    if depth and not color:
        gl.glDrawBuffer(gl.GL_NONE)  # No color in this buffer
        gl.glReadBuffer(gl.GL_NONE)

    # Bind texture to FBO.
    attachment_point = gl.GL_DEPTH_ATTACHMENT_EXT if depth and not color else gl.GL_COLOR_ATTACHMENT0_EXT
    attached_texture2D_type = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X if texture_type==gl.GL_TEXTURE_CUBE_MAP else gl.GL_TEXTURE_2D
    gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, attachment_point, attached_texture2D_type, texture, 0)

    # create a render buffer as our temporary depth buffer, bind it, and attach it to the fbo
    if color and depth:
        renderbuffer = create_opengl_object(gl.glGenRenderbuffersEXT)
        gl.glBindRenderbufferEXT(gl.GL_RENDERBUFFER_EXT, renderbuffer)
        gl.glRenderbufferStorageEXT(gl.GL_RENDERBUFFER_EXT, gl.GL_DEPTH_COMPONENT24, width, height)
        gl.glFramebufferRenderbufferEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_DEPTH_ATTACHMENT_EXT, gl.GL_RENDERBUFFER_EXT,
                                        renderbuffer)

    # check FBO status (warning appears for debugging)
    FBOstatus = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
    if FBOstatus != gl.GL_FRAMEBUFFER_COMPLETE_EXT:
        raise BufferError("GL_FRAMEBUFFER_COMPLETE failed, CANNOT use FBO.\n{0}\n".format(FBOstatus))

    #Unbind FBO and return it and its texture
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    return FBO(fbo, texture, texture_slot, (width, height))


class render_to_fbo(object):
    def __init__(self, window, fbo):
        """A context manager that sets the framebuffer target and resizes the viewport before and after the draw commands."""
        self.window = window
        self.fbo = fbo

    def __enter__(self):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.fbo.id)  # Rendering off-screen
        gl.glViewport(0, 0, self.fbo.size[0], self.fbo.size[1])

    def __exit__(self, *exc_info):
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
        gl.glViewport(0, 0, self.window.size[0], self.window.size[1])


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
