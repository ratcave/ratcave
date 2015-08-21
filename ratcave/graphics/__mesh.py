import types
import ctypes

from pyglet import image
from utils import *
import numpy as np
import __mixins as mixins


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


class Material:

    """Contains material settings that it gets from a .mtl file
    (must be same filename as .obj file). Currently requires all
    material settings to create object, and relies on defaults to be set
    in the object initialization!"""

    def __init__(self, material_name='DefaultGray', diffuse=(.8,.8,.8), spec_weight=0, spec_color=(0,0,0), ambient=(0,0,0), dissolve=0, illum=2):

        material_name = material_name.split('\n')
        self.name = material_name[0]
        self.diffuse = mixins.Color(*diffuse)
        self.diffuse_weight = 1.
        self.spec_weight = spec_weight
        self.spec_color = mixins.Color(*spec_color)
        self.ambient = mixins.Color(*ambient)
        self.dissolve = dissolve
        self.illum = illum

    def __repr__(self):

        """This function is called when str() or print() is used on the object."""
        return "Material Object: self.name"

class Empty(mixins.Physical):

    def __init__(self, position=(0,0,0), rotation=(0,0,0)):
        """Only contains Physical information.  Useful for tracking an object that you're not interested in rendering."""
        mixins.Physical.__init__(self, position, rotation)


class Mesh(object):

    drawstyle = {'fill':gl.GL_TRIANGLES, 'line':gl.GL_LINE_LOOP, 'point':gl.GL_POINTS}

    def __init__(self, mesh_data, material=None, mesh=None, scale=1.0, centered=False, lighting=True,
                 drawstyle='fill', position=(0,0,0), rotation=(0,0,0)):

        """Returns a Mesh object.
        Required Inputs:
            -string objfile: the .obj filename to load the mesh data from.
        Optional Keyword Inputs:
            -bool cubemap: whether to link a cubemap texture to the mesh.
            -string mesh: if multiple meshes are in the objfile, which mesh to use.
            -bool centered:
            -[x,y,z] position: origin point of mesh in 3D space.
            -bool lighting: whether to perform diffuse and specular shading on the model.

        Note: faces in the objfile must have triangle faces, normals,
              and UV texture coords.
        """

        # Mesh Data
        assert isinstance(mesh_data, MeshData), "Mesh object requires a MeshData object as input."
        self.data = mesh_data
        vertex_mean = np.mean(self.data.vertices, axis=0)
        self.data.vertices -= vertex_mean

        # Convert Mean position into Global Coordinates. If "centered" is True, though, simply leave global position to 0
        world_position = (0., 0., 0.) if centered else tuple(vertex_mean)
        self.world = mixins.Physical(position=world_position)  # Couldn't use "global" as name of property--reserved in python.
        self.local = mixins.Physical(position=position, rotation=rotation, scale=scale)

        self.material = material if isinstance(material, Material) else Material()
        self.texture = None  # will be changed to pyglet texture object if texture is set.
        self.cubemap = None
        self.meshObj = mesh
        self.lighting = lighting
        self.drawstyle = drawstyle

        self.visible = True
        self.loaded = False  # If mesh data is loaded into OpenGL yet.

    def __repr__(self):
        """Called when print() or str() commands are used on object."""
        return "Mesh: {0}".format(self.data.name)

    def load_texture(self, texture_source):
        """Loads a texture from an image file."""
        self.texture = image.load(texture_source).get_texture()

    def create_vao(self):

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


        # Everything is now assigned and all data passed to the GPU.  Can disable VAO and VBO now.
        gl.glBindVertexArray(0)

        self.loaded = True

    def render(self):
        if not self.loaded:
            self.create_vao()
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
