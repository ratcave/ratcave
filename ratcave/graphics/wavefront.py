from os import path
import copy
import numpy as np
from .mesh import MeshData, Mesh, Material


class WavefrontReader(object):

    def __init__(self, file_name):
        """
        Reads Wavefront (.obj) files created in Blender to build ratCAVE.graphics Mesh objects.

        :param file_name: .obj file to read (assumes an accompanying .mtl file has the same base file name.)
        :type file_name: str
        :return:
        :rtype: WavefrontReader
        """
        self.file_name = file_name
        self.meshdata = {}
        self.materials = {}
        self.mesh_material_names = {}
        self.mesh_names = []

        file_name, _ = path.splitext(file_name)
        self._parse_obj(file_name + '.obj')
        self._parse_mtl(file_name + '.mtl')

    def get_mesh(self, mesh_name, **kwargs):
        """
        Returns a Mesh object for directly rendering in a scene.

        :param mesh_name:
        :param kwargs: All of Mesh's keword arguments will be applied to the Mesh, for convenient Mesh creation.
        :return: Mesh
        :rtype: Mesh
        """
        meshdata = self.meshdata[mesh_name]
        material_name = self.mesh_material_names[mesh_name] if 'material_name' not in kwargs else kwargs['material_name']
        material = self.materials[material_name]
        return copy.deepcopy(Mesh(meshdata, material, **kwargs))  # TODO: Make Wavefront.get_mesh() automatically make new version of object.

    def _parse_obj(self, file_name):

        with open(file_name, 'r') as wavefront_file:
            lines = wavefront_file.readlines()
            total_lines = len(lines)

            obj_idx = 0
            list_prefixes = ['#', 'mtllib', 'o', 'v', 'vt', 'vn', 'usemtl', 's', 'f', 'l']  # TODO: Find out what 'l' is for
            single_prefixes = ['mtllib', 'o', 's', 'usemtl']
            props = {pre: [] for pre in list_prefixes}
            s_props = {pre: None for pre in single_prefixes}
            props.update(s_props)

            for line_num, line in enumerate(lines):

                name = props['o']

                # Add data to corresponding list in dictionary.
                prefix, rest = line.split(' ', 1)
                if isinstance(props[prefix], list):
                    props[prefix].append(rest[:-1])
                else:
                    props[prefix] = rest[:-1]

                # Reset property dictionary for each object
                if (prefix == 'o' and props['f']) or line_num == total_lines - 1:
                    self.mesh_material_names[name] = props['usemtl']  #
                    # Build mesh from props dictionary
                    meshdata = self._build_mesh(props, name)
                    self.meshdata[name] = meshdata
                    self.mesh_names.append(name)

                    props['f'] = []



    def _build_mesh(self, props, name):

        # Handle the face indices.  Need separate arrays for each mesh object.
        tmp = [line.split(' ') for line in props['f']]
        num_coords = len(tmp[0][0].split('/'))
        tmp = [line.replace('/', ' ').split(' ') for line in props['f']]
        face_indices = np.array([int(number) for inner in tmp for number in inner]).reshape((-1, num_coords)) - 1
        inds = np.arange(face_indices.shape[0])

        # Get the float data into NumPy arrays
        vertices = np.array([float(number) for inner in props['v'] for number in inner.split(' ')]).reshape((-1, 3))
        textureUVs = np.array([float(number) for inner in props['vt'] for number in inner.split(' ')]).reshape((-1, 2))
        normals = np.array([float(number) for inner in props['vn'] for number in inner.split(' ')]).reshape((-1, 3))

        # Reorder float data, so they all match the "inds" list
        verts = vertices[face_indices[:, 0]]
        textUVs = textureUVs[face_indices[:, 1]] if np.any(textureUVs) else None
        norms = normals[face_indices[:, 2]] if np.any(normals) else None

        # Build MeshData object
        mesh = MeshData(verts, inds, norms, textUVs)
        mesh.name = name
        return mesh


    def _parse_mtl(self, filename):

        # Get filename (same as .obj filename, but different extension)
        with open(filename, 'r') as material_file:
            lines = [line for line in material_file]  # Loop through each line

        prefixes = ['#', 'newmtl', 'Ns', 'Ka', 'Kd', 'Ks', 'Ni', 'd', 'illum']
        props = dict.fromkeys(prefixes, None)
        for line in lines:
            if len(line) > 2:
                prefix, rest = line.split(' ', 1)
            else:
                continue

            try:
                rest = [float(num) for num in rest.split(' ')]  # convert to list of floats
                rest = rest[0] if len(rest) == 1 else rest
            except ValueError:  # If not a sequence of numbers, but a string instead
                rest = rest[:-1]
                print rest

            props[prefix] = rest

            if prefix == 'illum':  # Last property listed in .mtl material
                # Make Material object and add to list of materials
                name = props['newmtl']
                material = Material(name=name,
                                    diffuse=props['Kd'],
                                    spec_weight=props['Ns'],
                                    spec_color=props['Ks'],
                                    ambient=props['Ka'])
                                    #dissolve=props['d'])

                self.materials[name] = material
                props = dict.fromkeys(prefixes, None)
