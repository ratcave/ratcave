from .physical import PhysicalGraph
from .shader import HasUniforms
from .utils import mixins


class Light(PhysicalGraph, HasUniforms, mixins.NameLabelMixin, mixins.ObservableVisibleMixin):

    def __init__(self, **kwargs):
        super(Light, self).__init__(**kwargs)
        self.uniforms['light_position'] = self.model_matrix_global[:3, 3]