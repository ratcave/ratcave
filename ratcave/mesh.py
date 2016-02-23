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
from . import mixins
from . import shader


class MeshData(object):

    def __init__(self, vertices, face_indices, normals, texcoords):
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
        self.texcoords = np.array(texcoords, dtype=float).reshape((-1, 2))


class Material(object):

    def __init__(self, diffuse=[.8, .8, .8], spec_weight=0., specular=[0., 0., 0.],
                 ambient=[0., 0., 0.], opacity=1., flat_shading=False):
        self.diffuse = diffuse
        self.spec_weight = spec_weight
        self.specular = specular
        self.ambient = ambient
        self.opacity = opacity
        self.flat_shading = flat_shading


class MeshLoader(object):

    def __init__(self, name, meshdata, material=None):
        """Creates various types of Meshes from MeshData and Material objects."""

        self.name = name
        self.meshdata = meshdata
        self.material = material

    def load_mesh(self, **kwargs):
        from collections import Iterable

        """Construct a Mesh object"""
        uniforms = []
        if self.material:
            for key, val in self.material.__dict__.items():
                if not isinstance(val, Iterable):
                    val = int(val) if isinstance(val, bool) else val
                    val = [val]
                uniforms.append(shader.Uniform(key, *val))

        return Mesh(self.name, self.meshdata.vertices, self.meshdata.normals, self.meshdata.texcoords, uniforms=uniforms, **kwargs)


class EmptyMesh(mixins.PhysicalNode):

    def __init__(self, *args, **kwargs):
        super(EmptyMesh, self).__init__(*args, **kwargs)

    def _draw(self, shader=None):
        self.update()


class Mesh(EmptyMesh, mixins.Picklable):

    drawstyle = {'fill': gl.GL_TRIANGLES, 'line': gl.GL_LINE_LOOP, 'point': gl.GL_POINTS}

    def __init__(self, name, vertices, normals, texcoords, uniforms=list(), drawstyle='fill', visible=True, point_size=4,
                 **kwargs):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        Args:
            mesh_data (MeshData): MeshData object containing the vertex data to be displayed.
            uniforms (list): List of Uniform or UniformGroup instances, containing data to send to shader when drawing the Mesh.
            drawstyle (str): 'point': only vertices, 'line': points and edges, 'fill': points, edges, and faces (full)
            visible (bool): whether the Mesh is available to be rendered.  To make hidden (invisible), set to False.

        Attributes:
            local (:py:class:`.Physical`): The local position and rotation of the Mesh.  This shift is done first, so should be used for general positioning.  If *centered* is set to False, the local position will be set as the mean vertex coordinates from :py:class:`.MeshData`, so Mesh will appear in the same location as the Mesh's original position in its file.
            world (:py:class:`.Physical`): The world position and rotation of the Mesh.  World position is used for moving an object about another point, so that multiple objects can be moved at once and retain their inter-object distances and orientations.  By default, set to the origin.
        Returns:
            Mesh instance
        """
        super(Mesh, self).__init__(**kwargs)

        self.name = name

        # Mesh Data
        self.vertices = np.array(vertices, dtype=float)
        self.normals = np.array(normals, dtype=float)
        self.texcoords = np.array(texcoords, dtype=float)

        # Convert Mean position into Global Coordinates. If "centered" is True, though, simply leave global position to 0
        vertex_mean = np.mean(self.vertices, axis=0)
        self.vertices -= vertex_mean
        self.position = vertex_mean if 'position' not in kwargs else kwargs['position']

        #: :py:class:`.Physical`, World Mesh coordinates
        #: Local Mesh coordinates (Physical type)
        self.uniforms = uniforms

        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        self.texture = None
        self.drawstyle = drawstyle
        self.point_size = point_size

        #: Bool: if the Mesh is visible for rendering. If false, will not be rendered.
        self.visible = visible
        self.vao = None

    def _draw(self, shader=None, *args, **kwargs):
        super(Mesh, self)._draw(*args, **kwargs)

        if not self.vao:
            self.vao = ugl.VAO(self.vertices, self.normals, self.texcoords)

        self.update()

        if self.visible:

            # Change Material to Mesh's
            for uniform in self.uniforms:
                uniform.send_to(shader)

            # Send Model and Normal Matrix to shader.
            shader.uniform_matrixf('model_matrix', self.model_matrix_global.T.ravel())
            shader.uniform_matrixf('normal_matrix', self.normal_matrix_global.T.ravel())

            # Set Point Size, if drawing a point cloud
            if self.drawstyle == 'point':
                gl.glPointSize(int(self.point_size))

            # Bind the VAO and Texture, and draw.
            with self.vao:
                shader.uniformi('hasTexture', bool(self.texture))  # TODO: Replace hardcoded uniform with more elegant solution!
                if self.texture:
                    with self.texture as texture:
                        texture.uniform.send_to(shader)
                        gl.glDrawArrays(Mesh.drawstyle[self.drawstyle], 0, self.vertices.size)
                else:

                    gl.glDrawArrays(Mesh.drawstyle[self.drawstyle], 0, self.vertices.size)
