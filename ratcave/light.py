from .physical import PhysicalGraph
from .shader import HasUniforms

class Light(PhysicalGraph, HasUniforms):

    def __init__(self, **kwargs):
        super(Light, self).__init__(**kwargs)
        self.uniforms['light_position'] = self.model_matrix_global[:3, 3]