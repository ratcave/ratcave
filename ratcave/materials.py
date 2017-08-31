
class Material(object):

    def __init__(self, diffuse=[.8, .8, .8], spec_weight=0., specular=[0., 0., 0.],
                 ambient=[0., 0., 0.], opacity=1., flat_shading=False, texture_file=None):
        self.diffuse = diffuse
        self.spec_weight = spec_weight
        self.specular = specular
        self.ambient = ambient
        self.opacity = opacity
        self.flat_shading = flat_shading
        self.texture_file = texture_file

