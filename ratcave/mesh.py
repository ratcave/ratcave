from __future__ import absolute_import

"""
    mesh
    ~~~~

    This module contains the Mesh, MeshData, and Material classes.
    This documentation was auto-generated from the mesh.py file.
"""
import numpy as np
from pyglet import gl
from .utils import gl as ugl
from .utils.texture import MockTexture
from . import mixins
from .utils import shader


class MeshData(object):

    def __init__(self, vertices, face_indices, normals, texture_uv):
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
        self.face_indices = np.array(face_indices, dtype=int)
        self.normals = np.array(normals, dtype=float).reshape((-1, 3))
        self.texture_uv = np.array(texture_uv, dtype=float).reshape((-1, 2))


gray_material = shader.UniformGroup.from_dict(dict(diffuse=[.8, .8, .8], spec_weight=0.,
                                            spec_color=[0., 0., 0.], ambient=[0., 0., 0.],
                                            opacity=1., hasLighting=1))

class Mesh(mixins.Picklable):

    drawstyle = {'fill': gl.GL_TRIANGLES, 'line': gl.GL_LINE_LOOP, 'point': gl.GL_POINTS}

    def __init__(self, mesh_data, uniforms=[gray_material], scale=1.0, centered=False,
                 drawstyle='fill', position=(0,0,0), rotation=(0,0,0), visible=True, point_size=4):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            mesh_data (MeshData): MeshData object containing the vertex data to be displayed.
            uniforms (list): List of Uniform or UniformGroup instances, containing data to send to shader when drawing the Mesh.
            scale (float): local size scaling factor (1.0 is normal size)
            centered (bool): if True, sets local position to 0 after mean-centering the vertices. If false, sets it to the mean.
            drawstyle (str): 'point': only vertices, 'line': points and edges, 'fill': points, edges, and faces (full)
            position (tuple): the local (x,y,z) position of the Mesh (default 0,0,0)
            rotation (tuple): the local (x,y,z) rotation of the Mesh, in degrees (default 0,0,0)
            visible (bool): whether the Mesh is available to be rendered.  To make hidden (invisible), set to False.

        Attributes:
            local (:py:class:`.Physical`): The local position and rotation of the Mesh.  This shift is done first, so should be used for general positioning.  If *centered* is set to False, the local position will be set as the mean vertex coordinates from :py:class:`.MeshData`, so Mesh will appear in the same location as the Mesh's original position in its file.
            world (:py:class:`.Physical`): The world position and rotation of the Mesh.  World position is used for moving an object about another point, so that multiple objects can be moved at once and retain their inter-object distances and orientations.  By default, set to the origin.
        Returns:
            Mesh instance
        """

        # Mesh Data
        assert isinstance(mesh_data, MeshData), "Mesh object requires a MeshData object as input."
        self.data = mesh_data

        # Convert Mean position into Global Coordinates. If "centered" is True, though, simply leave global position to 0
        vertex_mean = np.mean(self.data.vertices, axis=0)
        self.data.vertices -= vertex_mean
        local_position = position if centered else tuple(vertex_mean)
        #: :py:class:`.Physical`, World Mesh coordinates
        self.world = mixins.Physical(position=(0., 0., 0.))
        #: Local Mesh coordinates (Physical type)
        self.local = mixins.Physical(position=local_position, rotation=rotation, scale=scale)

        self.uniforms = uniforms

        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        self.texture = MockTexture()
        self.drawstyle = drawstyle
        self.point_size = point_size

        #: Bool: if the Mesh is visible for rendering. If false, will not be rendered.
        self.visible = visible
        self.vao = None
        self.normal_matrix = None
        self.model_matrix = None
    
    def update_matrices(self):
        """Resets the model and normal matrices used internally for positioning and shading."""

        # Local then world
        self.model_matrix = np.dot(self.world.model_matrix, self.local.model_matrix).T.ravel()
        self.normal_matrix = np.dot(self.world.normal_matrix, self.local.normal_matrix).T.ravel()

    @property
    def position(self):
        return tuple(np.dot(self.world.model_matrix, self.local.model_matrix)[:3, -1].tolist())

    def _draw(self, shader=None):
        if not self.vao:
            self.vao = ugl.VAO(self.data.vertices, self.data.normals, self.data.texture_uv)

        if self.visible:

            # Change Material to Mesh's
            for uniform in self.uniforms:
                uniform.send_to(shader)

            # Send Model and Normal Matrix to shader.
            shader.uniform_matrixf('model_matrix', self.model_matrix)
            shader.uniform_matrixf('normal_matrix', self.normal_matrix)

            # Set Point Size, if drawing a point cloud
            if self.drawstyle == 'point':
                gl.glPointSize(int(self.point_size))

            # Bind the VAO and Texture, and draw.
            with self.vao, self.texture as texture:
                texture.send_to(shader)
                gl.glDrawArrays(Mesh.drawstyle[self.drawstyle], 0, self.data.vertices.size)