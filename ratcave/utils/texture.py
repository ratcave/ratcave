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

    def send_to(self, shaderHandle):
           gl.glUniform1i(gl.glGetUniformLocation(shaderHandle, self.uniform_name), self.slot)

    @staticmethod
    def _generate_id():
        return ugl.create_opengl_object(gl.glGenTextures)

    @classmethod
    def _genTex2D(cls, width, height):
        gl.glTexImage2D(cls.target0, 0, cls.internal_fmt, width, height, 0, cls.pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)

    def _apply_filter_settings(self):
        with self:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)



class TextureCube(Texture):

    target = gl.GL_TEXTURE_CUBE_MAP
    target0 = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X

    def __init__(self, *args, **kwargs):
        super(TextureCube, self).__init__(*args, **kwargs)

    def _apply_filter_settings(self, *args, **kwargs):
        super(TextureCube, self)._apply_filter_settings()
        with self:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    @classmethod
    def _genTex2D(cls, width, height):
        assert width == height, "Cubes must have square faces."
        for face in range(6):
            gl.glTexImage2D(cls.target0 + face, 0, cls.internal_fmt, width, height, 0,
                            cls.pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)


class RenderBuffer(object):

    def __init__(self, target, id, width, height):

        self.target = target
        self.id = id
        self.width = width
        self.height = height
        self.attachment_point = gl.GL_DEPTH_ATTACHMENT_EXT

    def bind(self):
        gl.glBindRenderbufferEXT(self.target, self.id)

    @classmethod
    def create_empty(cls, width, height):
        target = gl.GL_RENDERBUFFER_EXT
        id = ugl.create_opengl_object(gl.glGenRenderbuffersEXT)
        gl.glRenderbufferStorageEXT(target, gl.GL_DEPTH_COMPONENT24, width, height)
        return cls(target, id, width, height)