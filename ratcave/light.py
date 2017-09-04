from .physical import PhysicalGraph
from .shader import HasUniforms
from .utils import mixins


class Light(PhysicalGraph, HasUniforms, mixins.NameLabelMixin, mixins.ObservableVisibleMixin):

    def __init__(self, **kwargs):
        super(Light, self).__init__(**kwargs)
        self.reset_uniforms()

    def __repr__(self):
        return "<Light(name='{self.name}', position_rel={self.position}, position_glob={self.position_global}, rotation={self.rotation})".format(self=self)

    def reset_uniforms(self):
        self.uniforms['light_position'] = self.model_matrix_global[:3, 3]