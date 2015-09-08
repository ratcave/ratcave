import types
import ctypes

from pyglet import image
from utils import *
import numpy as np
import mixins as mixins


def create_opengl_object(gl_gen_function, n=1):
    """Returns int pointing to an OpenGL texture"""
    handle = gl.GLuint(1)
    gl_gen_function(n, ctypes.byref(handle))  # Create n Empty Objects
    if n > 1:
        return [handle.value + el for el in range(n)]  # Return list of handle values
    else:
        return handle.value  # Return handle value

class MeshData(object):

    def __init__(self, vertices, face_indices, normals, texture_uv):
        """Contains NumPy Arrayed Mesh Data (vertices, normals, face_indices, etc) for generating an OpenGL mesh.
        Assumes data's shape is (N_Points x Coords) and that face_indices represent triangulated faces.
        Optitional arguments:
            -bool centered: whether to mean-center the vertices, so the position is equal to the vertex center
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

    def __init__(self, name='DefaultGray', diffuse=(.8,.8,.8), spec_weight=0, spec_color=(0,0,0), ambient=(0,0,0), dissolve=0):

        name = name.split('\n')
        self.name = name[0]
        self.diffuse = mixins.Color(*diffuse)
        self.spec_weight = spec_weight
        self.spec_color = mixins.Color(*spec_color)
        self.ambient = mixins.Color(*ambient)
        if dissolve != 0:
            raise NotImplementedError("Material.dissolve not yet implemented.  Please see Mesh.visible for hiding Meshes.")

    def __repr__(self):
        return "Material: self.name. Diffuse: {0}".format(self.diffuse.rgba)


class Mesh(object):

    drawstyle = {'fill':gl.GL_TRIANGLES, 'line':gl.GL_LINE_LOOP, 'point':gl.GL_POINTS}

    def __init__(self, mesh_data, material=None, scale=1.0, centered=False, lighting=True,
                 drawstyle='fill', cubemap=False, position=(0,0,0), rotation=(0,0,0), visible=True):
        """
        Returns a Mesh object, containing the position, rotation, and color info of an OpenGL Mesh.

        Meshes have two coordinate system, the "local" and "world" systems, on which the transforms are performed
        sequentially.  This allows them to be placed in the scene while maintaining a relative position to one another.

        .. note:: Meshes are not usually instantiated directly, but from a 3D file, like the WavefrontReader .obj and .mtl files.

        :param mesh_data: MeshData object containing the vertex data to be displayed.
        :type mesh_data: MeshData
        :param material: Material object containing the color data for how the Mesh should be lit.
        :type material: Material
        :param scale: local size scaling factor (1.0 is normal size)
        :param centered: if True, sets local position to 0 after mean-centering the vertices. If false, sets it to the mean.
        :type centered: bool
        :param lighting: Whether 3D shading should be done when rendering the mesh. If not, will be rendered with flat shading in its diffuse color.
        :type lighting: bool
        :param drawstyle: 'point': only vertices, 'line': points and edges, 'fill': points, edges, and faces (full)
        :type drawstyle: str
        :param cubemap: whether the cubemap texture will be applied to this Mesh.
        :type cubemap: bool
        :param position: the local xyz position of the Mesh (default 0,0,0)
        :type position: tuple
        :param rotation: the local xyz rotation of the Mesh, in degrees (default 0,0,0)
        :type rotation: tuple
        :param visible: whether the Mesh is available to be rendered.  To make hidden (invisible), set to False.
        :type visible: bool
        """

        # Mesh Data
        assert isinstance(mesh_data, MeshData), "Mesh object requires a MeshData object as input."
        self.data = mesh_data
        vertex_mean = np.mean(self.data.vertices, axis=0)
        self.data.vertices -= vertex_mean

        # Convert Mean position into Global Coordinates. If "centered" is True, though, simply leave global position to 0
        world_position = (0., 0., 0.) if centered else tuple(vertex_mean)
        #: World Mesh coordinates (Physical type)
        self.world = mixins.Physical(position=world_position)
        #: Local Mesh coordinates (Physical type)
        self.local = mixins.Physical(position=position, rotation=rotation, scale=scale)

        #: Material object that describes how the Mesh is lit.
        self.material = material if isinstance(material, Material) else Material()
        #: Pyglet texture object for mapping an image file to the vertices (set using Mesh.load_texture())
        self.texture = None
        #: Bool, whether the cubemap texture is applied to this Mesh.
        self.cubemap = cubemap
        #: Bool, whether 3D shading (described in Material) is applied.  Else flat diffuse color will be used.
        self.lighting = lighting
        #: 'fill', 'line', or 'point'
        self.drawstyle = drawstyle
        #: Bool: if the Mesh is visible for rendering. If false, will not be rendered.
        self.visible = visible
        self.__loaded = False  # If mesh data is loaded into OpenGL yet.

    def __repr__(self):
        """Called when print() or str() commands are used on object."""
        return "Mesh: {0}".format(self.data.name)

    def load_texture(self, file_name):
        """Loads a texture from an image file into OpenGL and applies it to the Mesh for rendering.

        :param file_name: the filename of the image file. Support jpg, png, and more.
        :type file_name: str
        :rtype: None
        """
        self.texture = image.load(file_name).get_texture()

    def _create_vao(self):
        """Puts the MeshData into a Vertex Array Object for OpenGl, saving it in the GPU to be rendered later."""

        # Create Vertex Array Object and Bind it
        self.vao = create_opengl_object(gl.glGenVertexArrays)
        gl.glBindVertexArray(self.vao)

        # Create Vertex Buffer Object and Bind it (Vertices)
        self.vbo = create_opengl_object(gl.glGenBuffers, 3)

        # Upload Vertex Coordinates
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 4 * self.data.vertices.size,
                        vec(self.data.vertices.flatten()), gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(0)

        # Upload Normal Coordinates
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 4 * self.data.normals.size,
                        vec(self.data.normals.flatten()), gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(1)

        # Upload Texture UV Coordinates
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo[2])
        gl.glBufferData(gl.GL_ARRAY_BUFFER, 4 * self.data.texture_uv.size,
                        vec(self.data.texture_uv.flatten()), gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(2)

        # Everything is now assigned and all data passed to the GPU.  Can unbind VAO and VBO now.
        gl.glBindVertexArray(0)

        self.__loaded = True

    def render(self, shader):
        """Sends the Mesh's Model and Normal matrices to an already-bound Shader, and bind and render the Mesh's VAO."""

        # Send Model and Normal Matrix to shader.
        shader.uniform_matrixf('model_matrix_global', self.world.model_matrix)
        shader.uniform_matrixf('model_matrix_local', self.local.model_matrix)
        shader.uniform_matrixf('normal_matrix_global', self.world.normal_matrix)
        shader.uniform_matrixf('normal_matrix_local', self.local.normal_matrix)

        # Bind VAO data for rendering each vertex.
        if not self.__loaded:
            self._create_vao()
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(Mesh.drawstyle[self.drawstyle], 0, self.data.vertices.size)
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
