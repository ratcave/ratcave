from .mesh import Mesh
from six import iteritems
from wavefront_reader import read_wavefront
from . import Texture

class WavefrontReader(object):

    material_property_map = {'Kd': 'diffuse',
                             'Ka': 'ambient',
                             'Ke': 'emission',
                             'Ks': 'specular',
                             'Ni': 'Ni',
                             'Ns': 'spec_weight',
                             'd': 'd',
                             'illum': 'illum',
                             'map_Kd': 'map_Kd',
                             }

    def __init__(self, file_name):
        """
        Reads Wavefront (.obj) files created in Blender to build ratcave.graphics Mesh objects.
        :param file_name: .obj file to read (assumes an accompanying .mtl file has the same base file name.)
        :type file_name: str
        :return:
        :rtype: WavefrontReader
        """
        self.file_name = file_name
        self.bodies = read_wavefront(file_name)
        self.textures = {}

    def get_mesh(self, body_name, **kwargs):
        """Builds Mesh from geom name in the wavefront file.  Takes all keyword arguments that Mesh takes."""
        body = self.bodies[body_name]
        vertices = body['v']
        normals = body['vn'] if 'vn' in body else None
        texcoords = body['vt'] if 'vt' in body else None
        mesh = Mesh.from_incomplete_data(vertices=vertices, normals=normals, texcoords=texcoords, **kwargs)

        uniforms = kwargs['uniforms'] if 'uniforms' in kwargs else {}
        if 'material' in body:
            material_props = {self.material_property_map[key]: value for key, value in iteritems(body['material'])}
            for key, value in iteritems(material_props):
                if isinstance(value, str):
                    if key == 'map_Kd':
                        if not value in self.textures:
                            self.textures[value] = Texture.from_image(value)
                        mesh.textures.append(self.textures[value])
                    else:
                        setattr(mesh, key, value)
                elif hasattr(value, '__len__'):  # iterable materials
                    mesh.uniforms[key] = value
                elif key in ['d', 'illum']:  # integer materials
                    mesh.uniforms[key] = value
                elif key in ['spec_weight', 'Ni']:  # float materials: should be specially converted to float if not already done.
                    mesh.uniforms[key] = float(value)
                else:
                    print('Warning: Not applying uniform {}: {}'.format(key, value))
        return mesh
