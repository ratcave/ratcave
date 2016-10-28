
from .utils import gl as ugl
from . import texture as tex

import pyglet.gl as gl


class FBO(ugl.GlGenMixin, ugl.BindingContextMixin):

    genfun = gl.glGenFramebuffersEXT
    target = gl.GL_FRAMEBUFFER_EXT

    def __init__(self, texture, *args, **kwargs):
        """A Framebuffer object, which when bound redirects draws to its texture.  This is useful for deferred rendering."""

        super(FBO, self).__init__(*args, **kwargs)
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

    def bind(self):
        """Bind the FBO.  Anything drawn afterward will be stored in the FBO's texture."""
        # This is called simply to deal with anything that might be currently bound (for example, Pyglet objects),
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Store current viewport size for later
        gl.glGetIntegerv(gl.GL_VIEWPORT, self._old_viewport_size)

        # Bind the FBO, and change the viewport to fit its texture.
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.id)  # Rendering off-screen
        gl.glViewport(0, 0, self.texture.width, self.texture.height)

    def unbind(self):
        """Unbind the FBO."""
        # Unbind the FBO
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

        # Restore the old viewport size
        gl.glViewport(*self._old_viewport_size)