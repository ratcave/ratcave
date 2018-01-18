
from .utils import BindingContextMixin, create_opengl_object, get_viewport, Viewport
from .texture import DepthTexture, RenderBuffer

import pyglet.gl as gl


class FBO(BindingContextMixin):

    target = gl.GL_FRAMEBUFFER_EXT

    def __init__(self, texture, *args, **kwargs):
        """A Framebuffer object, which when bound redirects draws to its texture.  This is useful for deferred rendering."""

        super(FBO, self).__init__(*args, **kwargs)
        self.id = create_opengl_object(gl.glGenFramebuffersEXT)
        self._old_viewport = get_viewport()
        self.texture = texture
        self.renderbuffer = RenderBuffer(texture.width, texture.height) if not isinstance(texture, DepthTexture) else None

        with self:

            # Attach the textures to the FBO
            self.texture.attach_to_fbo()
            if self.renderbuffer:
                self.renderbuffer.attach_to_fbo()

            # Set Draw and Read locations for the FBO (currently, just turn it off if not doing any color stuff)
            if isinstance(texture, DepthTexture):
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
        self._old_viewport = get_viewport()

        # Bind the FBO, and change the viewport to fit its texture.
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.id)  # Rendering off-screen
        gl.glViewport(0, 0, self.texture.width, self.texture.height)

    def unbind(self):
        """Unbind the FBO."""
        # Unbind the FBO
        if self.texture.mipmap:
            with self.texture:
                self.texture.generate_mipmap()

        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

        # Restore the old viewport size
        gl.glViewport(*self._old_viewport)