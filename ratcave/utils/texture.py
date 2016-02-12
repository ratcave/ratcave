import pyglet
import pyglet.gl as gl
from . import gl as ugl

class Texture(object):

    target = gl.GL_TEXTURE_2D
    target0 = gl.GL_TEXTURE_2D
    attachment_point = gl.GL_COLOR_ATTACHMENT0_EXT
    internal_fmt = gl.GL_RGBA
    pixel_fmt=gl.GL_RGBA

    def __init__(self, id=None, slot=1, uniform_name='TextureMap', width=1024, height=1024):
        """Does nothing but solve missing conditional context manager feature in Python 2.7"""

        if id:
            self.id = id
        else:
            self.id = ugl.create_opengl_object(gl.glGenTextures)
            self._genTex2D(width, height)
            self._apply_filter_settings()
            self.width = width
            self.height = height

        self.slot = slot
        self.uniform_name = uniform_name

    def __enter__(self):
        self.bind()
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        gl.glActiveTexture(gl.GL_TEXTURE0)
        self.unbind()

    def bind(self):
        gl.glBindTexture(self.target, self.id)

    @classmethod
    def unbind(cls):
        gl.glBindTexture(cls.target, 0)

    @staticmethod
    def _generate_id():
        return ugl.create_opengl_object(gl.glGenTextures)

    def _genTex2D(self):
        gl.glTexImage2D(self.target0, 0, self.internal_fmt, self.width, self.height, 0, self.pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)

    def _apply_filter_settings(self):
        with self:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    def send_to(self, shaderHandle):
           gl.glUniform1i(gl.glGetUniformLocation(shaderHandle, self.uniform_name), self.slot)

    def attach_to_fbo(self):
        gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, self.attachment_point, self.target0, self.id, 0)




class TextureCube(Texture):

    target = gl.GL_TEXTURE_CUBE_MAP
    target0 = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X

    def __init__(self, *args, **kwargs):
        super(TextureCube, self).__init__(*args, **kwargs)
        assert self.width == self.height, "Cubes must have square faces."

    def _apply_filter_settings(self, *args, **kwargs):
        super(TextureCube, self)._apply_filter_settings()
        with self:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    def _genTex2D(self):
        for face in range(6):
            gl.glTexImage2D(self.target0 + face, 0, self.internal_fmt, self.width, self.height, 0,
                            self.pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)


class DepthTexture(Texture):
    internal_fmt = gl.GL_DEPTH_COMPONENT
    pixel_fmt = gl.GL_DEPTH_COMPONENT
    attachment_point = gl.GL_DEPTH_ATTACHMENT_EXT


class GrayscaleTexture(Texture):
    internal_fmt = gl.GL_R8
    pixel_fmt = gl.GL_RED


class GrayscaleTextureCube(TextureCube):
    internal_fmt = gl.GL_R8
    pixel_fmt = gl.GL_RED


class RenderBuffer(object):

    target = gl.GL_RENDERBUFFER_EXT
    attachment_point = gl.GL_DEPTH_ATTACHMENT_EXT
    internal_fmt = gl.GL_DEPTH_COMPONENT24

    def __init__(self, width, height):

        self.id = ugl.create_opengl_object(gl.glGenRenderbuffersEXT)
        self.width = width
        self.height = height
        self._gen()

    def bind(self):
        gl.glBindRenderbufferEXT(self.target, self.id)

    def _gen(self):
        gl.glRenderbufferStorageEXT(self.target, self.internal_fmt, self.width, self.height)

    def attach_to_fbo(self):
        gl.glFramebufferRenderbufferEXT(gl.GL_FRAMEBUFFER_EXT, self.attachment_point, self.target, self.id)