import pyglet
import pyglet.gl as gl
from . import gl as ugl

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

        # Apply texture settings for interpolation behavior (Required)
        self.bind()
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        self.unbind()


    def __enter__(self):
        super(Texture, self).__enter__()
        self.bind()
        gl.glActiveTexture(getattr(gl, 'GL_TEXTURE{}'.format(self.slot)))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Texture, self).__exit__()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        self.unbind()

    def bind(self):
        gl.glBindTexture(self.target, self.id)

    def unbind(self):
        gl.glBindTexture(self.target, 0)

    def send_to(self, shaderHandle):
           gl.glUniform1i(gl.glGetUniformLocation(shaderHandle, self.uniform_name), self.slot)

    @classmethod
    def from_image_file(cls, filename, **kwargs):
        img = pyglet.image.load(filename)
        texture = img.get_texture()
        return cls(target=texture.target, id=texture.id, **kwargs)

    @classmethod
    def create_empty(cls, target, slot, width, height, internal_fmt, pixel_fmt, **kwargs):
        gl.glActiveTexture(gl.GL_TEXTURE0 + slot)
        id = ugl.create_opengl_object(gl.glGenTextures)
        texture = cls(target=target, id=id, slot=slot, **kwargs)

        # Generate blank textures
        with texture as tex:
            if tex.target == gl.GL_TEXTURE_2D:
                gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal_fmt, width, height, 0,
                    pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)
            elif tex.target == gl.GL_TEXTURE_CUBE_MAP:
                for face in range(6):
                    gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face, 0, internal_fmt,
                                    width, height, 0, pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)

        return texture


class TextureCube(Texture):

    def __init__(self, *args, **kwargs):
        super(TextureCube, self).__init__(*args, target=gl.GL_TEXTURE_CUBE_MAP, **kwargs)

        self.bind()
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        self.unbind()