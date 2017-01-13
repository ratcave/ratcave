import abc
from . import shader
from .physical import PhysicalGraph

class Drawable(object):
    """Interface for drawing."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, uniforms=shader.UniformCollection(), **kwargs):
        super(Drawable, self).__init__(**kwargs)
        self.uniforms = uniforms if type(uniforms) == shader.UniformCollection else shader.UniformCollection(uniforms)

    def draw(self, **kwargs):
        pass



class EmptyEntity(Drawable, PhysicalGraph):
    """An object that occupies physical space and uniforms, but doesn't actually draw anything when draw() is called."""
    pass