import pyglet.gl as gl
import numpy as np
import pdb

def create_opengl_object(gl_gen_function):
    """Returns int pointing to an OpenGL texture"""
    texture_id = gl.GLuint(1)
    gl_gen_function(1, byref(texture_id))  # Create Empty Texture
    return texture_id.value  # Use handle for rest


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
    color_type = gl.GL_R8 if grayscale else gl.GL_RGBA
    internal_format = gl.GL_DEPTH_COMPONENT if depth and not color else color_type

    color_type = gl.GL_RED if grayscale else gl.GL_RGBA
    pixel_format = gl.GL_DEPTH_COMPONENT if depth and not color else color_type

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

    return fbo, texture


def vec(floatlist,newtype='float'):

        """ Makes GLfloat or GLuint vector containing float or uint args.
        By default, newtype is 'float', but can be set to 'int' to make
        uint list. """

        if 'float' in newtype:
            return (gl.GLfloat * len(floatlist))(*list(floatlist))
        elif 'int' in newtype:
            return (gl.GLuint * len(floatlist))(*list(floatlist))

def plot3_square(axis_object, data, color='b', limits=None):
    """Convenience function for plotting a plot3 scatterplot with square axes."""
    # Set axis limits, if not already set.

    if limits == None:
        tot_range = (data.max(axis=0) - data.min(axis=0)).max() * .55
        mn = data.mean(axis=0, keepdims=True) - tot_range
        mx = data.mean(axis=0, keepdims=True) + tot_range
        limits = np.vstack([mn, mx]).transpose()

    # apply limits to the axis
    for coord, idx in zip('xyz', range(3)):
        getattr(axis_object, 'set_{0}lim3d'.format(coord))(limits[idx])

    # Plot
    axis_object.plot3D(data[:, 0], data[:, 1], data[:, 2], color+'o', zdir='y')

    return limits

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
