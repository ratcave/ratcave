from os.path import split, join
from ctypes import byref
from utils import *
import __mixins as mixins
from __camera import Camera
from __shader import Shader
from __mesh import fullscreen_quad


class Scene:
    """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

    # Lights
    light = mixins.Physical()

    def __init__(self, *meshes):
        """Initialize the Scene object using Meshes as input../s"""

        self.camera = Camera()  # create a default Camera object
        self.bgColor = mixins.Color(0, 0, 0)

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)


    def draw(self):
        """General draw method."""
        self._draw(self.camera, Scene.genShader)

    def _draw(self, camera, shader):
        """Draws the scene. Call this method in your Window's Draw Loop."""

        # Enable 3D OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)
        #gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP)
        gl.glEnable(gl.GL_TEXTURE_2D)

        # Clear and Refresh Screen
        gl.glClearColor(self.bgColor.r, self.bgColor.g, self.bgColor.b, 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Bind Shader
        shader.bind()

        # Send Uniforms that are constant across meshes.
        shader.uniform_matrixf('view_matrix', camera._view_matrix)
        shader.uniform_matrixf('projection_matrix', camera._projection_matrix)
        shader.uniform_matrixf('shadow_projection_matrix', Scene.__shadowCamera._projection_matrix)
        shader.uniform_matrixf('shadow_view_matrix', Scene.__shadowCamera._view_matrix)

        shader.uniformf('light_position', *Scene.light.position)
        shader.uniformf('camera_position', *camera.position)

        shader.uniformi('hasShadow', int(Scene._shadowFboID is not False))
        shader.uniformi('ShadowMap', 5)


        shader.uniformi('grayscale', int(Scene.grayscale))

        # Draw each visible mesh in the scene.
        for mesh in self.meshes:

            if mesh.visible:

                # Send Model and Normal Matrix to shader.
                shader.uniform_matrixf('model_matrix_global', mesh.world._model_matrix)
                shader.uniform_matrixf('model_matrix_local', mesh.local._model_matrix)
                shader.uniform_matrixf('normal_matrix_global', mesh.world._normal_matrix)
                shader.uniform_matrixf('normal_matrix_local', mesh.local._normal_matrix)


                if shader == Scene.genShader:
                    # Change Material to Mesh's
                    shader.uniformf('ambient', *mesh.material.ambient.rgb)
                    shader.uniformf('diffuse', *mesh.material.diffuse.rgb)
                    shader.uniformf('spec_color', *mesh.material.spec_color.rgb)
                    shader.uniformf('spec_weight', mesh.material.spec_weight)
                    shader.uniformf('opacity', mesh.material.diffuse.a)
                    shader.uniformi('hasLighting', mesh.lighting)

                    # Bind Cubemap if mesh is to be rendered with the cubemap.
                    shader.uniformi('hasCubeMap', int(bool(mesh.cubemap)))
                    if mesh.cubemap:
                        shader.uniformf('playerPos', *vec(Scene.player.position))
                        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, Scene._cubeTexture)  # No ActiveTexture needed, because only one Cubemap.

                    # Bind Textures and apply Material
                    shader.uniformi('hasTexture', int(bool(mesh.texture)))
                    if mesh.texture:
                        gl.glActiveTexture(gl.GL_TEXTURE2)
                        gl.glBindTexture(gl.GL_TEXTURE_2D, mesh.texture.id)
                        shader.uniformi('ImageTextureMap', 2)
                        gl.glActiveTexture(gl.GL_TEXTURE0)

                # Draw the Mesh
                mesh.render()  # Bind VAO.

        # Unbind Shader
        shader.unbind()