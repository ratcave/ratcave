

from os import path
import copy

import numpy as np
from .mesh import Mesh, MeshData, MeshLoader, Material
from .scene import Scene


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
                    meshdata = self._build_mesh(props)
                    self.meshdata[name] = meshdata
                    self.mesh_names.append(name)

                    props['f'] = []

    def get_mesh(self, mesh_name, **kwargs):
        """
        Returns a Mesh object for directly rendering in a scene.

        :param mesh_name:
        :param kwargs: All of Mesh's keword arguments will be applied to the Mesh, for convenient Mesh creation.
        :return: Mesh
        :rtype: Mesh
        """
        meshdata = copy.deepcopy(self.meshdata[mesh_name])

        material_name = self.mesh_material_names[mesh_name] if 'material_name' not in kwargs else kwargs['material_name']
        material = copy.deepcopy(self.materials[material_name])
        return MeshLoader(mesh_name, meshdata, material).load_mesh(**kwargs)

    def get_meshes(self, mesh_names, **kwargs):
        """Returns a dictionary of meshes, with kwargs applied to all meshes identically, as in get_mesh()"""
        return {name: self.get_mesh(name, **kwargs) for name in mesh_names}

    def get_scene(self, include=[], exclude=[]):
        """
        Return a Scene object containing the Meshes in the file.

        Args:
            include (list): mesh names to only include.
            exclude (list): mesh names to exclude.

        Returns:
            :py:class:`.Scene`
        """
        names = include if include else self.mesh_names
        meshes = [self.get_mesh(name) for name in names if name not in exclude]
        return Scene(meshes)

    def _build_mesh(self, props):

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
        meshdata = MeshData(verts, inds, norms, textUVs)
        return meshdata

    def _parse_mtl(self, filename):

        def parse_property_line(data_line):
            prefix, value = data_line.lstrip().split(' ', 1)

            try:
                value = [float(num) for num in value.split(' ')]  # convert to list of floats
                value = value[0] if len(value) == 1 else value
            except ValueError:  # If not a sequence of numbers, but a string instead
                pass

            return prefix, value

        # parsing in 3 steps:
        # - read all data in [lines] list
        # - split each mesh section in {mtls} dict
        # - parse each mesh section and create material from it

        # STEP1: read all data in [lines] list
        try:
            with open(filename, 'r') as material_file:
                lines = [line for line in material_file]

        except IOError:
            print("Warning: No .mtl material file found for "
                  ".obj file. Using default material instead...")
            self.materials[None] = Material()
            return

        mtls = {}  # like {'Shape.005': ['Ns 96.078431', 'Ka 0.166667 0.166667 0.166667', ...], ...}
        mtl_name_buff = ''
        mtl_line_buff = []

        # STEP 2: split each mesh section in {mtls} dict
        # empty lines as newmtl section separators
        separators = [0] + [i for i, x in enumerate(lines) if x == "\n"] + [len(lines)]

        for i in range(len(separators) - 1):
            for line in lines[separators[i]:separators[i + 1]]:
                if line.startswith('newmtl'):
                    mtl_name_buff = line.strip('\n').split(' ')[1]

                elif len(line.strip('\n')) > 0:
                    mtl_line_buff.append(line.strip('\n'))

            if mtl_name_buff:
                mtls[mtl_name_buff] = mtl_line_buff

            mtl_name_buff = ''
            mtl_line_buff = []

        # STEP 3: parse each newmtl section into Material
        prefixes = ['#', 'newmtl', 'Ns', 'Ka', 'Kd', 'Ks', 'Ni', 'd', 'illum', 'map_Kd']

        for name, lines in mtls.items():
            props = dict.fromkeys(prefixes, None)

            for line in lines:
                p, val = parse_property_line(line)
                if p in prefixes:
                    props[p] = val

            kwargs = {
                "diffuse": props['Kd'],
                "spec_weight": props['Ns'],
                "specular": props['Ks'],
                "ambient": props['Ka'],
                "opacity": props['d'],
                "texture_file": props['map_Kd']
            }
            self.materials[name] = Material(**kwargs)
