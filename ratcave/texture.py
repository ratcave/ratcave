import itertools
from.utils import gl as ugl
import pyglet
import pyglet.gl as gl
from .shader import HasUniforms


class BaseTexture(HasUniforms):

    int_flag = 0
    tex_name = 'TextureMap'
    cube_name = 'CubeMap'

    def __init__(self, **kwargs):
        super(BaseTexture, self).__init__(**kwargs)
        self.reset_uniforms()

    def reset_uniforms(self):
        self.uniforms['textype'] = self.int_flag
        self.uniforms[self.tex_name] = 0
        self.uniforms[self.cube_name] = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Texture(BaseTexture, ugl.BindTargetMixin):

    target = gl.GL_TEXTURE_2D
    target0 = gl.GL_TEXTURE_2D
    attachment_point = gl.GL_COLOR_ATTACHMENT0_EXT
    internal_fmt = gl.GL_RGBA
    pixel_fmt=gl.GL_RGBA
    _slot_counter = itertools.count(start=1)
    int_flag = 1
    bindfun = gl.glBindTexture

    def __init__(self, id=None, width=1024, height=1024, data=None, mipmap=False, **kwargs):
        """2D Color Texture class. Width and height can be set, and will generate a new OpenGL texture if no id is given."""
        super(Texture, self).__init__(**kwargs)

        self._slot = next(self._slot_counter)
        self.uniforms[self.tex_name] = self._slot
        self.mipmap = mipmap

        if id != None:
            self.id = id
            self.data = data  # This is used for anything that might be garbage collected (i.e. pyglet textures)
        else:
            self.id = ugl.create_opengl_object(gl.glGenTextures)
            self.width = width
            self.height = height
            self.bind()
            self._genTex2D()
            self._apply_filter_settings()


        self.unbind()

    @property
    def slot(self):
        """The texture's ActiveTexture slot."""
        return self._slot

    def __enter__(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        pass

    def _genTex2D(self):
        """Creates an empty texture in OpenGL."""
        gl.glTexImage2D(self.target0, 0, self.internal_fmt, self.width, self.height, 0, self.pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)

    def generate_mipmap(self):
        if self.mipmap:
            gl.glGenerateMipmap(self.target)


    def _apply_filter_settings(self):
        """Applies some hard-coded texture filtering settings."""
        # TODO: Allow easy customization of filters
        if self.mipmap:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        else:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    def attach_to_fbo(self):
        """Attach the texture to a bound FBO object, for rendering to texture."""
        gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, self.attachment_point, self.target0, self.id, 0)

    @classmethod
    def from_image(cls, img_filename, mipmap=False, **kwargs):
        """Uses Pyglet's image.load function to generate a Texture from an image file. If 'mipmap', then texture will
        have mipmap layers calculated."""
        img = pyglet.image.load(img_filename)
        tex = img.get_mipmapped_texture() if mipmap else img.get_texture()
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return cls(id=tex.id, data=tex, mipmap=mipmap, **kwargs)


class TextureCube(Texture):

    target = gl.GL_TEXTURE_CUBE_MAP
    target0 = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X
    int_flag = 2

    def __init__(self, *args, **kwargs):
        """the Color Cube Texture class."""
        # TODO: check that width == height!
        super(TextureCube, self).__init__(*args, **kwargs)
        self.uniforms[self.cube_name] = self._slot

    def _apply_filter_settings(self, *args, **kwargs):
        super(TextureCube, self)._apply_filter_settings()
        with self:
            gl.glTexParameterf(self.target, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    def _genTex2D(self):
        """Generate an empty texture in OpenGL"""
        for face in range(6):
            gl.glTexImage2D(self.target0 + face, 0, self.internal_fmt, self.width, self.height, 0,
                            self.pixel_fmt, gl.GL_UNSIGNED_BYTE, 0)

    @classmethod
    def from_image(cls, img_filename):
        raise NotImplementedError()

    def attach_to_fbo(self, face=0):
        gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, self.attachment_point,
                                     self.target0 + face,
                                     self.id,  0)  # Select face of cube texture to render to.

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


class RenderBuffer(ugl.BindingContextMixin, ugl.BindTargetMixin):

    target = gl.GL_RENDERBUFFER_EXT
    attachment_point = gl.GL_DEPTH_ATTACHMENT
    internal_fmt = gl.GL_DEPTH_COMPONENT24
    bindfun = gl.glBindRenderbufferEXT

    def __init__(self, width, height):

        self.id = ugl.create_opengl_object(gl.glGenRenderbuffersEXT)
        self.width = width
        self.height = height
        self.bind()
        self._gen()

    def _gen(self):
        gl.glRenderbufferStorageEXT(self.target, self.internal_fmt, self.width, self.height)

    def attach_to_fbo(self):
        gl.glFramebufferRenderbufferEXT(gl.GL_FRAMEBUFFER_EXT, self.attachment_point, self.target, self.id)
