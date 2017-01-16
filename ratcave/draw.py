import abc
from . import shader
from .physical import PhysicalGraph

class HasUniforms(object):
    """Interface for drawing."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, uniforms=None, **kwargs):
        super(HasUniforms, self).__init__(**kwargs)
        self.uniforms = shader.UniformCollection(uniforms) if uniforms else shader.UniformCollection()



class EmptyEntity(HasUniforms, PhysicalGraph):
    """An object that occupies physical space and uniforms, but doesn't actually draw anything when draw() is called."""
    pass