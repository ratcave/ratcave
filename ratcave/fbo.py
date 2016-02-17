from __future__ import absolute_import

from .utils import gl as ugl
from . import texture as tex

import pyglet.gl as gl

class FBO(object):

    target = gl.GL_FRAMEBUFFER_EXT

    def __init__(self, texture):

        self.id = ugl.create_opengl_object(gl.glGenFramebuffersEXT)
        self._old_viewport_size = (gl.GLint * 4)()
        self.texture = texture
        self.renderbuffer = tex.RenderBuffer(texture.width, texture.height) if not isinstance(texture, tex.DepthTexture) else None

        with self: #, self.texture:  # TODO: Figure out whether texture should also be bound here.

            # Attach the textures to the FBO
            for texture in [self.texture, self.renderbuffer] if self.renderbuffer else [self.texture]:
                texture.attach_to_fbo()

            # Set Draw and Read locations for the FBO (currently, just turn it off if not doing any color stuff)
            if isinstance(texture, tex.DepthTexture):
                gl.glDrawBuffer(gl.GL_NONE)  # No color in this buffer
                gl.glReadBuffer(gl.GL_NONE)

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

    @classmethod
    def create_color_fbo(cls, **kwargs):
        color_tex = tex.Texture(**kwargs)
        return cls(color_tex)

    @classmethod
    def create_shadow_fbo(cls, **kwargs):
        depth_tex = tex.DepthTexture(**kwargs)
        return cls(depth_tex)

    @classmethod
    def create_cube_fbo(cls, **kwargs):
        cube_tex = tex.TextureCube(**kwargs)
        return cls(cube_tex)