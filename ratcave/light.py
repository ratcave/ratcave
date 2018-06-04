from .shader import HasUniformsUpdater
from .utils import mixins
from .camera import Camera
from .utils import NameLabelMixin

class Light(Camera, HasUniformsUpdater, NameLabelMixin):
    def __init__(self, **kwargs):
        super(Light, self).__init__(**kwargs)
        # self.projection.fov_y = 130
        self.reset_uniforms()

    def __repr__(self):
        return "<Light(name='{self.name}', position_rel={self.position}, position_glob={self.position_global}, rotation={self.rotation})".format(self=self)

    def __enter__(self):
        self.update()
        self.uniforms.send()
        return self

    def __exit__(self, *args):
        pass

    def reset_uniforms(self):
        self.uniforms['light_position'] = self.model_matrix_global[:3, 3]
        self.uniforms['light_projection_matrix'] = self.projection_matrix.view()
        self.uniforms['light_view_matrix'] = self.view_matrix.view()
