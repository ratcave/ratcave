import pyglet.gl as gl


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
