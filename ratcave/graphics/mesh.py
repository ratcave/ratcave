from __future__ import absolute_import

"""
    mesh
    ~~~~

    This module contains the Mesh, MeshData, and Material classes.
    This documentation was auto-generated from the mesh.py file.
"""
import numpy as np
from pyglet import gl, image

from . import utils, mixins


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


class Material(object):

    """Contains material settings that it gets from a .mtl file
    (must be same filename as .obj file). Currently requires all
    material settings to create object, and relies on defaults to be set
    in the object initialization!"""

    def __init__(self, name='DefaultGray', diffuse=(.8, .8, .8, 1.), spec_weight=0, spec_color=(0, 0, 0, 1.), ambient=(0, 0, 0, 1.),
                 dissolve=0):
        """
        Returns a Material object containing various Color properties for 3D shading in graphics packages.

        Args:
            name: (str): The name of the material
            diffuse (tuple): (r,g,b) values for diffuse reflections.  Also used as color if flat shading is used.
            spec_weight (float): falloff exponent for specular shading. if <= 1, specular lighting is not performed.
            spec_color (tuple): (r,g,b) values for specular reflections
            ambient (tuple): (r,g,b) values for ambient reflections.
            dissolve (float): Dissolve transparancy level (0-1).  Not implemented for shading yet, though.

        Returns:
            Material instance

        .. warning:: Transparancy hasn't been fully implemented yet.  If alpha values are changed from 1., unexpected outputs may occur.
        """
        self.name = name.split('\n')[0]
        self.diffuse = mixins.Color(*diffuse)
        self.spec_weight = spec_weight
        self.spec_color = mixins.Color(*spec_color)
        self.ambient = mixins.Color(*ambient)
        if dissolve != 0:
            raise NotImplementedError("Material.dissolve not yet implemented.  Please see Mesh.visible for hiding Meshes.")


drawstyle = {'fill':gl.GL_TRIANGLES, 'line':gl.GL_LINE_LOOP, 'point':gl.GL_POINTS
        }
class Mesh(object):

    def __init__(self, mesh_data, material=Material(), scale=1.0, centered=False, lighting=True,
                 drawstyle='fill', cubemap=False, position=(0,0,0), rotation=(0,0,0), visible=True, point_size=4):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            mesh_data (MeshData): MeshData object containing the vertex data to be displayed.
            material (Material): Material object containing the color data for how the Mesh should be lit.
            scale (float): local size scaling factor (1.0 is normal size)
            centered (bool): if True, sets local position to 0 after mean-centering the vertices. If false, sets it to the mean.
            lighting (bool):Whether 3D shading should be done when rendering the mesh. If not, will be rendered with flat shading in its diffuse color.
            drawstyle (str): 'point': only vertices, 'line': points and edges, 'fill': points, edges, and faces (full)
            cubemap (bool): whether the cubemap texture will be applied to this Mesh.
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

        self.material = material

        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        self.texture = None
        self.texture_filename = None
        self.cubemap = cubemap
        self.lighting = lighting
        self.drawstyle = drawstyle
        self.point_size = point_size

        #: Bool: if the Mesh is visible for rendering. If false, will not be rendered.
        self.visible = visible
        self.vao = None
        self.normal_matrix = None
        self.model_matrix = None

    def __repr__(self):
        return "Mesh: {0}".format(self.data.name)

    def load_texture(self, file_name):
        """Loads a texture from an image file into OpenGL and applies it to the Mesh for rendering."""
        self.texture_filename = file_name
        self.texture = image.load(file_name).get_texture()
    
    def update_matrices(self):
        """Resets the model and normal matrices used internally for positioning and shading."""

        # Local then world
        self.model_matrix = np.dot(self.world.model_matrix, self.local.model_matrix).T.ravel()
        self.normal_matrix = np.dot(self.world.normal_matrix, self.local.normal_matrix).T.ravel()

    @property
    def position(self):
        return np.dot(self.world.model_matrix, self.local.model_matrix)[:3, -1].tolist()

    def render(self, shader):
        """Sends the Mesh's Model and Normal matrices to an already-bound Shader, and bind and render the Mesh's VAO."""

        # Send Model and Normal Matrix to shader.
        shader.uniform_matrixf('model_matrix', self.model_matrix)
        shader.uniform_matrixf('normal_matrix', self.normal_matrix)

        # Bind VAO data for rendering each vertex.
        if not self.vao is None:
            self.vao = utils.create_vao(self.data.vertices, self.data.normals, self.data.texture_uv)

        if self.drawstyle == 'point':
            gl.glEnable(gl.GL_POINT_SMOOTH)
            gl.glPointSize(int(self.point_size))

        gl.glBindVertexArray(self.vao)

        gl.glDrawArrays(drawstyle[self.drawstyle], 0, self.data.vertices.size)

        if self.drawstyle == 'point':
            gl.glDisable(gl.GL_POINT_SMOOTH)

        gl.glBindVertexArray(0)


fullscreen_quad = None

# Some default objects
fullscreen_quad_data = MeshData([-1, -1, 0, -1, 1, 0, 1, 1, 0,
                                 -1, -1, 0,  1, 1, 0, 1, -1, 0],
                                [0, 1, 2, 0, 2, 3],
                                normals=[0, 0, -1]*6,
                                # NEED NORMALS TO RENDER PROPERLY NOW!!
                                texture_uv=[0, 0, 0, 1, 1, 1,
                                            0, 0, 1, 1, 1, 0])
fullscreen_quad = Mesh(fullscreen_quad_data)
