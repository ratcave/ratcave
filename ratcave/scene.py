

import warnings
import pyglet.gl as gl

from . import mixins, Camera, Light, resources, mesh
from .utils import gl as glutils
from .utils import orienting
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

    def draw(self, shader=resources.genShader, autoclear=True, send_mesh_uniforms=True, userdata={},
             gl_states=(gl.GL_DEPTH_TEST, gl.GL_POINT_SMOOTH, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D)):#, gl.GL_BLEND)):
        """Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light."""

        self.camera.update()
        self.light.update_model_matrix()

        # Enable 3D OpenGL states (glEnable, then later glDisable)
        with glutils.enable_states(gl_states):
            # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            # Bind Shader
            with shader:

                if autoclear:
                    self.clear()

                # Send Uniforms that are constant across meshes.
                shader.uniform_matrixf('view_matrix', self.camera.view_matrix.T.ravel())
                shader.uniform_matrixf('projection_matrix', self.camera.projection_matrix.T.ravel())
                #
                # # if self.shadow_rendering:
                # #     shader.uniform_matrixf('shadow_projection_matrix', self.shadow_cam.projection_matrix.T.ravel())
                # #     shader.uniform_matrixf('shadow_view_matrix', scene.light.view_matrix.T.ravel())
                #

                shader.uniformf('light_position', *self.light.position)
                shader.uniformf('camera_position', *self.camera.position)

                # shader.uniformi('hasShadow', int(self.shadow_rendering))
                # shadow_slot = self.fbos['shadow'].texture_slot if scene == self.active_scene else self.fbos['vrshadow'].texture_slot
                # shader.uniformi('ShadowMap', shadow_slot)
                # shader.uniformi('grayscale', int(self.grayscale))

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

                self.light.update_model_matrix()
                self.camera.update()

                shader.uniformf('light_position', *self.light.position)
                shader.uniform_matrixf('projection_matrix', self.camera.projection_matrix.T.ravel())
                shader.uniformf('camera_position', *self.camera.position)

                for mesh_idx, mesh in enumerate(self.root):

                    for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.

                        cubetexture.attach_to_fbo(face)
                        if autoclear and not mesh_idx:
                            self.clear()

                        # Update camera and send new rotation data as a view matrix
                        self.camera.rotation = rotation
                        self.camera.update_view_matrix()
                        shader.uniform_matrixf('view_matrix', self.camera.view_matrix.T.ravel())

                        mesh._draw(shader=shader, send_uniforms=not face)


