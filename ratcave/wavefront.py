from .mesh import Mesh
from six import iteritems
from wavefront_reader import read_wavefront


class WavefrontReader(object):

    material_property_map = {'Kd': 'diffuse',
                             'Ka': 'ambient',
                             'Ke': 'emission',
                             'Ks': 'specular',
                             'Ni': 'Ni',
                             'Ns': 'spec_weight',
                             'd': 'd',
                             'illum': 'illum'
                             }

    def __init__(self, file_name):
        """
        Reads Wavefront (.obj) files created in Blender to build ratCAVE.graphics Mesh objects.

        :param file_name: .obj file to read (assumes an accompanying .mtl file has the same base file name.)
        :type file_name: str
        :return:
        :rtype: WavefrontReader
        """
        self.file_name = file_name
        self.bodies = read_wavefront(file_name)

    def get_mesh(self, name, **kwargs):
        """Builds Mesh from geom name in the wavefront file.  Takes all keyword arguments that Mesh takes."""
        body = self.bodies[name]
        vertices = body['v']
        normals = body['vn'] if 'vn' in body else None
        texcoords = body['vt'] if 'vt' in body else None

        uniforms = kwargs['uniforms'] if 'uniforms' in kwargs else {}
        material_props = {self.material_property_map[key]: value for key, value in iteritems(body['material'])}
        uniforms.update(material_props)

        mesh = Mesh.from_incomplete_data(name=name, vertices=vertices, normals=normals, texcoords=texcoords,
                                         uniforms=uniforms, **kwargs)
        return mesh