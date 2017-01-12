

"""
    mesh
    ~~~~

    This module contains the Mesh, MeshData, and Material classes.
    This documentation was auto-generated from the mesh.py file.
"""
import copy
import abc
from collections import Iterable
import numpy as np
from pyglet import gl
from .utils import gl as ugl
from . import physical, shader
from . import texture as texture_module


class MeshData(object):

    def __init__(self, vertices, face_indices, normals, texcoords=None):
        """
        Collects all vertex data for rendering in 3D graphics packages.

        Args:
            vertices (list): Nx3 vertex array
            face_indices (list): Nx3 Face index array (0-indexed)
            normals (list): Nx3 normals array
            texture_uv (list): Nx2 texture_uv array

        Returns:
            MeshData object
        """
        # CPU Data
        self.vertices = np.array(vertices, dtype=float).reshape((-1, 3))
        self.face_indices = np.array(face_indices, dtype=np.uint16).reshape((-1, 1))
        self.normals = np.array(normals, dtype=float).reshape((-1, 3))
        self.texcoords = np.array(texcoords, dtype=float).reshape((-1, 2))
        assert self.vertices.shape[0] == self.normals.shape[0]
        assert self.vertices.shape[0] == self.texcoords.shape[0]

        self.is_loaded = False
        self.glbuffer = False

    def load(self):
        self.reindex()
        self.glbuffer = ugl.VAO(indices=self.face_indices)
        with self.glbuffer:
            for loc, verts in enumerate([self.vertices, self.normals, self.texcoords]):
                self.glbuffer.assign_vertex_attrib_location(ugl.VBO(verts), loc)
        self.is_loaded = True

    def draw(self, mode):
        if not self.is_loaded:
            self.load()

        with self.glbuffer as vao:
            vao.draw(mode)

    def reindex(self):

        def to_joined_struct_array_view(*arrays):
            """Concatenates (columnwise) each array given as input, then returns it as a structured array."""
            array = np.hstack(arrays)
            dtype = array.dtype.descr * array.shape[1]
            return array.view(dtype)

        all_vert_combs = to_joined_struct_array_view(self.vertices, self.normals, self.texcoords)
        unique_combs = np.unique(all_vert_combs)
        unique_vert_combs_sorted = np.sort(unique_combs)

        self.face_indices = np.array([np.searchsorted(unique_vert_combs_sorted, vert) for vert in all_vert_combs],
                                     dtype=np.uint32).reshape((-1, 1))
        unique_combs_array = unique_combs.view(float).reshape((unique_combs.shape[0], -1))
        self.vertices = unique_combs_array[:, :3]
        self.normals = unique_combs_array[:, 3:6]
        self.texcoords = unique_combs_array[:, 6:]


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


class MeshLoader(object):

    def __init__(self, name, meshdata, material=None):
        """Creates various types of Meshes from MeshData and Material objects."""

        self.name = name
        self.meshdata = meshdata
        self.material = material

    def load_mesh(self, **kwargs):
        """
        Construct a Mesh object from MeshData.
        Arguments:
          - position (3-coord tuple or None):  if None, puts Mesh position at center of vertices.
        """

        # Override default position to the mean vertices position, if nothing specified.
        vertex_mean = np.mean(self.meshdata.vertices, axis=0)
        if 'position' not in kwargs:
            kwargs['position'] = vertex_mean

        # change vertices to local vertex coordinates around Mesh position.
        self.meshdata.vertices -= vertex_mean

        uniforms = shader.UniformCollection()
        texture = None

        if self.material:
            for key, val in list(self.material.__dict__.items()):
                if key == "texture_file":
                    if val is not None:
                        texture = texture_module.Texture.from_image(val)
                else:
                    newval = copy.deepcopy(val)
                    if not isinstance(newval, Iterable):
                        newval = int(val) if isinstance(val, bool) else newval
                        newval = [newval]

                    uniforms[key] = newval

        return CylinderCollisionMesh(name=self.name, meshdata=self.meshdata, uniforms=uniforms, texture=texture, **kwargs)


class Drawable(object):
    """Interface for drawing."""
    __metaclass__ = abc.ABCMeta

    def draw(self, shader=None, **kwargs):
        pass


class MeshBase(Drawable, physical.PhysicalNode):
    __metaclass__ = abc.ABCMeta


class EmptyMesh(MeshBase):
    pass


class Mesh(MeshBase):

    drawstyle = {'fill': gl.GL_TRIANGLES, 'line': gl.GL_LINE_LOOP, 'point': gl.GL_POINTS}

    def __init__(self, name, meshdata, uniforms=shader.UniformCollection(), drawstyle='fill', visible=True,
                 point_size=4, texture=None, **kwargs):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            name (str): the mesh's name.
            vertices: the Nx3 vertex coordinate data
            normals: the Nx3 normal coordinate data
            texcoords: the Nx2 texture coordinate data
            uniforms (list): a list of all Uniform objects
            drawstyle (str): 'point': only vertices, 'line': points and edges, 'fill': points, edges, and faces (full)
            visible (bool): whether the Mesh is available to be rendered.  To make hidden (invisible), set to False.
            point_size (int): How big to draw the points, when drawstyle is 'point'

        Returns:
            Mesh instance
        """

        super(Mesh, self).__init__(**kwargs)

        self.data = meshdata
        self.name = name
        self.uniforms = uniforms if type(uniforms) == shader.UniformCollection else shader.UniformCollection(uniforms)

        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        self.texture = texture or texture_module.BaseTexture()
        self.drawstyle = drawstyle
        self.point_size = point_size

        #: Bool: if the Mesh is visible for rendering. If false, will not be rendered.
        self.visible = visible
        self.vao = None

        self._update_global_vertices()

    def _update_global_vertices(self):
        vertices_local = np.vstack([self.data.vertices.T, np.ones(len(self.data.vertices))])
        self.vertices_global = np.dot(self.model_matrix_global, vertices_local).T

    def update(self):
        super(Mesh, self).update()
        self._update_global_vertices()

    def draw(self, shader=None, send_uniforms=True, *args, **kwargs):
        super(Mesh, self).draw(*args, **kwargs)

        # if not self.is_updated:
        self.update()
        #     self.is_updated = True

        if self.visible:

            # Bind the VAO and Texture, and draw.
            with self.texture as texture:

                # Change Material to Mesh's
                if send_uniforms:

                    # self.update_model_and_normal_matrix()
                    self.uniforms.send()
                    texture.uniforms.send()

                    # Send Model and Normal Matrix to shader.
                    try:
                        shader.uniform_matrixf('model_matrix', self.model_matrix_global, loc=self.modelmat_loc)
                        shader.uniform_matrixf('normal_matrix', self.normal_matrix_global, loc=self.normalmat_loc)
                    except AttributeError:
                        self.modelmat_loc = shader.get_uniform_location('model_matrix')
                        self.normalmat_loc = shader.get_uniform_location('normal_matrix')

                # Set Point Size, if drawing a point cloud
                if self.drawstyle == 'point':
                    gl.glPointSize(int(self.point_size))

                # Send in the vertex and normal data
                self.data.draw(Mesh.drawstyle[self.drawstyle])


class CollisionMeshBase(Mesh):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh."""
        pass


# class CubeCollisionMesh(CollisionMeshBase):
#     """Calculates collision by checking if a point is inside a cube around the mesh vertices."""
#
#     def __init__(self, *args, **kwargs):
#         super(CubeCollisionMesh, self).__init__(*args, **kwargs)
#         # rectangular boundaries
#         self.collision_cube_min = np.zeros(3)
#         self.collision_cube_max = np.zeros(3)
#
#     def update(self):
#         """Checks if the model matrix needs updating, and updates collision cube data if so."""
#         super(CubeCollisionMesh, self).update()
#
#         self.collision_cube_min[:] = self.vertices_global.min(axis=0)[:3]
#         self.collision_cube_max[:] = self.vertices_global.max(axis=0)[:3]
#
#     def collides_with(self, xyz):
#         """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
#         raise NotImplementedError("Doesn't properly rotate cube to fit (See AABB collision vs OOB collision)")
#         # return np.all([np.min(self.vertices_global, axis=0)[:3] < xyz, xyz < np.max(self.vertices_global, axis=0)[:3]])


class SphereCollisionMesh(CollisionMeshBase):
    """Calculates collision by checking if a point is inside a sphere around the mesh vertices."""

    def __init__(self, *args, **kwargs):
        super(SphereCollisionMesh, self).__init__(*args, **kwargs)
        self.collision_radius = np.linalg.norm(self.vertices_global, axis=1).max()

    def collides_with(self, xyz):
        """Returns True if 3-value coordinate 'xyz' is inside the mesh's collision cube."""
        return np.linalg.norm(xyz - self.position_global) < self.collision_radius


class CylinderCollisionMesh(CollisionMeshBase):

    def __init__(self, up_axis='y', *args, **kwargs):
        super(CylinderCollisionMesh, self).__init__(*args, **kwargs)
        self.up_axis = up_axis
        self._collision_columns = {'x': (1, 2), 'y': (0, 2), 'z': (1, 2)}[up_axis]
        self.collision_radius = np.linalg.norm(self.vertices_global[:, self._collision_columns], axis=1).max()

    def collides_with(self, xyz):
        cc = self._collision_columns
        return np.linalg.norm(xyz[:, cc] - self.position_global[cc]) < self.collision_radius



