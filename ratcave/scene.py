

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

    def draw(self, shader=resources.genShader, autoclear=True, userdata={},
             gl_states=(gl.GL_DEPTH_TEST, gl.GL_POINT_SMOOTH, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D)):#, gl.GL_BLEND)):
        """Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light."""

        self.camera.update()
        self.light.update()

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
                    mesh._draw(shader=shader)


    def draw360_to_texture(self, cubetexture, **kwargs):
        """For dynamic environment mapping.  Draws the scene 6 times, once to each face of a cube texture."""
        # TODO: Solve provlem: FBO should be bound before glFramebufferTexture2DEXT is called.  How to solve?
        assert self.camera.aspect == 1. and self.camera.fov_y == 90
        assert type(cubetexture) == TextureCube, "Must render to TextureCube"

        for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.
            self.camera.rotation = rotation
            cubetexture.attach_to_fbo(face)
            self.draw(**kwargs)

