import itertools
from .utils import BindTargetMixin, BindingContextMixin, create_opengl_object
import pyglet
import pyglet.gl as gl
from .shader import HasUniforms


class Texture(HasUniforms, BindTargetMixin):

    target = gl.GL_TEXTURE_2D
    target0 = gl.GL_TEXTURE_2D
    attachment_point = gl.GL_COLOR_ATTACHMENT0_EXT
    internal_fmt = gl.GL_RGBA
    pixel_fmt=gl.GL_RGBA
    _slot_counter = itertools.count(start=1)
    bindfun = gl.glBindTexture

    def __init__(self, id=None, name='TextureMap', width=1024, height=1024, data=None, mipmap=False, **kwargs):
        """2D Color Texture class. Width and height can be set, and will generate a new OpenGL texture if no id is given."""
        super(Texture, self).__init__(**kwargs)

        self._slot = next(self._slot_counter)
        if self._slot >= self.max_texture_limit:
            raise MemoryError("More Textures have been created than your graphics Hardware can handle.")
        self.name = name
        self.mipmap = mipmap

        if id != None:
            self.id = id
            self.data = data  # This is used for anything that might be garbage collected (i.e. pyglet textures)
        else:
            self.id = create_opengl_object(gl.glGenTextures)
            self.width = width
            self.height = height
            self.bind()
            self._genTex2D()
            self._apply_filter_settings()

        self.unbind()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if hasattr(self, '_name'):
            del self.uniforms.data[self._name]
            del self.uniforms.data[self._name + '_isBound']
            print('replaced name')

        self.uniforms[name] = self._slot
        self.uniforms[name + '_isBound'] = False
        self._name = name


    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        super(Texture, self).bind()
        self.uniforms['{}_isBound'.format(self.name)] = True
        try:
            self.uniforms.send()
        except UnboundLocalError:  # TODO: Find a way to make binding and uniform-sending simple without requiring a bound shader.
            pass

    def unbind(self):
        super(Texture, self).unbind()
        self.uniforms['{}_isBound'.format(self.name)] = False
        try:
            self.uniforms.send()
        except UnboundLocalError:  # TODO: Find a way to make binding and uniform-sending simple without requiring a bound shader.
            pass

        gl.glActiveTexture(gl.GL_TEXTURE0)

    @property
    def slot(self):
        """The texture's ActiveTexture slot."""
        return self._slot

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    @property
    def max_texture_limit(self):
        """The maximum number of textures available for this graphic card's fragment shader."""
        max_unit_array = (gl.GLint * 1)()
        gl.glGetIntegerv(gl.GL_MAX_TEXTURE_IMAGE_UNITS, max_unit_array)
        return max_unit_array[0]

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

    def reset_uniforms(self):
        pass

class TextureCube(Texture):

    target = gl.GL_TEXTURE_CUBE_MAP
    target0 = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X

    def __init__(self, name='CubeMap', *args, **kwargs):
        """the Color Cube Texture class."""
        try:
            super(TextureCube, self).__init__(name=name, *args, **kwargs)
        except gl.lib.GLException as exception:
            if self.height != self.width:
                raise ValueError("TextureCube's height and width must match each other.")
            else:
                raise exception

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

    def __init__(self, name='DepthMap', *args, **kwargs):
        """the Color Cube Texture class."""
        super(DepthTexture, self).__init__(name=name, *args, **kwargs)

    def _apply_filter_settings(self):
        super(DepthTexture, self)._apply_filter_settings()
        gl.glTexParameterf(self.target, gl.GL_TEXTURE_COMPARE_MODE, gl.GL_COMPARE_REF_TO_TEXTURE)


class GrayscaleTexture(Texture):
    internal_fmt = gl.GL_R8
    pixel_fmt = gl.GL_RED


class GrayscaleTextureCube(TextureCube):
    internal_fmt = gl.GL_R8
    pixel_fmt = gl.GL_RED


class RenderBuffer(BindingContextMixin, BindTargetMixin):

    target = gl.GL_RENDERBUFFER_EXT
    attachment_point = gl.GL_DEPTH_ATTACHMENT
    internal_fmt = gl.GL_DEPTH_COMPONENT24
    bindfun = gl.glBindRenderbufferEXT

    def __init__(self, width, height):

        self.id = create_opengl_object(gl.glGenRenderbuffersEXT)
        self.width = width
        self.height = height
        self.bind()
        self._gen()

    def _gen(self):
        gl.glRenderbufferStorageEXT(self.target, self.internal_fmt, self.width, self.height)

    def attach_to_fbo(self):
        gl.glFramebufferRenderbufferEXT(gl.GL_FRAMEBUFFER_EXT, self.attachment_point, self.target, self.id)
