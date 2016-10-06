

import warnings
import pyglet.gl as gl

from . import mixins, Camera, Light, resources, mesh
from .utils import gl as glutils
from .texture import TextureCube


class Scene(object):

    def __init__(self, meshes=(), camera=None, light=None, bgColor=(0.4, 0.4, 0.4)):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""
        # TODO: provide help to make camera aspect and fov_y for cubemapped scenes!
        # Initialize List of all Meshes to draw

        self.root = mesh.EmptyMesh()
        self.root.add_children(meshes)
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = Light() if not light else light
        self.bgColor = bgColor

    def clear(self):
        """Clear Screen and Apply Background Color"""
        gl.glClearColor(*(self.bgColor + (1.,)))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def draw(self, shader=resources.genShader, clear=True,
             send_mesh_uniforms=True, send_camera_uniforms=True, send_light_uniforms=True, userdata={},
             gl_states=(gl.GL_DEPTH_TEST, gl.GL_POINT_SMOOTH, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D)):#, gl.GL_BLEND)):
        """Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light."""

        # Enable 3D OpenGL states (glEnable, then later glDisable)
        with glutils.enable_states(gl_states):
            # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            # Bind Shader
            with shader:

                if clear:
                    self.clear()

                # Send Uniforms that are constant across meshes.
                if send_camera_uniforms:
                    self.camera.update()
                    shader.uniform_matrixf('view_matrix', self.camera.view_matrix.T.ravel())
                    shader.uniform_matrixf('projection_matrix', self.camera.projection_matrix.T.ravel())
                    shader.uniformf('camera_position', *self.camera.position)

                if send_light_uniforms:
                    shader.uniformf('light_position', *self.light.position)

                for mesh in self.root:
                    mesh._draw(shader=shader, send_uniforms=send_mesh_uniforms)


    def draw360_to_texture(self, cubetexture, shader=resources.genShader, autoclear=True, userdata={},
             gl_states=(gl.GL_DEPTH_TEST, gl.GL_POINT_SMOOTH, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D)):#, gl.GL_BLEND)):
        """
        Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light, and
        applies it to each face of cubetexture, which should be currently bound to an FBO.
        """

        assert self.camera.aspect == 1. and self.camera.fov_y == 90
        assert type(cubetexture) == TextureCube, "Must render to TextureCube"

        # Enable 3D OpenGL states (glEnable, then later glDisable)
        with glutils.enable_states(gl_states):
            # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            # Bind Shader
            with shader:

                self.camera.update()

                shader.uniformf('light_position', *self.light.position)
                shader.uniform_matrixf('projection_matrix', self.camera.projection_matrix.T.ravel())
                shader.uniformf('camera_position', *self.camera.position)

                # Pre-Calculate all 6 view matrices
                view_matrices = []
                view_matrix_loc = shader.get_uniform_location('view_matrix')
                for rotation in [[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]:
                    self.camera.rotation = rotation
                    self.camera.update_view_matrix()
                    view_matrices.append(self.camera.view_matrix.T.ravel())

                for mesh_idx, mesh in enumerate(self.root):
                    for face, view_matrix in enumerate(view_matrices):
                        cubetexture.attach_to_fbo(face)
                        if autoclear and not mesh_idx:
                            self.clear()
                        shader.uniform_matrixf('view_matrix', view_matrix, loc=view_matrix_loc)
                        mesh._draw(shader=shader, send_uniforms=not face)


