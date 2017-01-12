import abc
from . import shader

class Drawable(object):
    """Interface for drawing."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, uniforms=shader.UniformCollection(), **kwargs):
        super(Drawable, self).__init__(**kwargs)
        self.uniforms = uniforms if type(uniforms) == shader.UniformCollection else shader.UniformCollection(uniforms)

    def draw(self, **kwargs):
        pass
