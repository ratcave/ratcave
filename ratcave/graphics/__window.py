__author__ = 'nickdg'

from psychopy import visual
import pyglet.gl as gl
from __scene import Scene
from __camera import Camera
from __shader import Shader
from __mesh import fullscreen_quad
from utils import *
from os.path import join, split


shader_path = join(split(__file__)[0], 'shaders')


class Window(visual.Window):
    """Subclass of Pyglet window, with some defaults set to simplify ratCAVE script creation."""

    # General, Normal Shader
    genShader = Shader(open(join(shader_path, 'combShader.vert')).read(),
                       open(join(shader_path, 'combShader.frag')).read())

    shadowShader = Shader(open(join(shader_path, 'shadowShader.vert')).read(),
                          open(join(shader_path, 'shadowShader.frag')).read())

    aaShader = Shader(open(join(shader_path, 'antialiasShader.vert')).read(),
                      open(join(shader_path, 'antialiasShader.frag')).read())

    def __init__(self, active_scene, grayscale=False, shadow_rendering=True, *args, **kwargs):

        # Set default Window values for making sure Psychopy windows work with it.
        kwargs['allowStencil'] = False
        super(Window, self).__init__(*args, **kwargs)
        assert self.winType == 'pyglet', "Window Type must be 'pyglet' for ratCAVE to work."

        # Assign data to window after OpenGL context initialization
        self.active_scene = active_scene  # For normal rendering.
        self.virtual_scene = None  # For dynamic cubemapping.
        self.grayscale = grayscale
        self.fbos = {'shadow': FBO(create_fbo(gl.GL_TEXTURE_2D, 2048, 2048, texture_slot=5, color=False, depth=True)),
                     'cube': FBO(create_fbo(gl.GL_TEXTURE_CUBE_MAP, 2048, 2048, texture_slot=0, color=True, depth=True, grayscale=self.grayscale)),
                     'antialias': FBO(create_fbo(gl.GL_TEXTURE_2D, 1280, 720, texture_slot=0, color=True, depth=True, grayscale=self.grayscale))
                     }
        self.texture_size = 2048
        self.player = None
        self.shadow_rendering = shadow_rendering

        self.fullscreen_quad = fullscreen_quad

    def set_virtual_scene(self, scene, from_viewpoint, to_mesh):
        """Set scene to render to cubemap, as well as the object whose position will be used as viewpoint and what mesh
        will be given the cubemap texture."""
        self.virtual_scene, self.player = scene, from_viewpoint
        to_mesh.cubemap = True

    def render_shadow(self, scene):
        scene.light.rotation = scene.camera.rotation  # only works while spotlights aren't implemented, otherwise may have to be careful.
        with render_to_fbo(self, self.fbos['shadow']):
            self._draw(scene, Window.shadowShader, camera=Camera(fov_y=60., aspect=1., position=scene.light.position, rotation=scene.camera.rotation))

    def render_to_cubemap(self, scene):
        # Render to Each Face of Cubemap texture, rotating the camera in the correct direction before each shot.
        with render_to_fbo(self, self.fbos['cube']):
            cube_camera = Camera(fov_y=90., aspect=1., position=self.player.position)
            for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.
                cube_camera.rotation = rotation
                gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                             gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                                             self.fbos['cube'].texture,  0)  # Select face of cube texture to render to.
                self._draw(cube_camera, Window.genShader)  # Render

    def render_to_antialias(self):
        """Render the scene to texture, then render the texture to screen after antialiasing it."""
        with render_to_fbo(self, self.fbos['antialias']):
            self._draw(self.camera, Window.genShader)

        gl.glClearColor(.5, .5, .5, 1.)  # Make background color gray for debugging purposes, but won't matter.
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        Window.aaShader.bind()

        Window.aaShader.uniformf('frameBufSize', *self.size)
        Window.aaShader.uniformi('image_texture', 0)
        Window.aaShader.uniformi('grayscale', int(self.grayscale))

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.fbos['antialias'].texture)

        self.fullscreen_quad.render()

        Window.aaShader.unbind()

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def on_draw(self):
        """Active scene drawn, virtual scene is rendered to a cubemap."""

        if self.virtual_scene:
            self.virtual_scene.render_shadow()
            self.virtual_scene.render_to_cubemap()
            Scene.light.position = self.active_scene.camera.position  # Comes after rendering to allow flexible behavior.
        else:
            self.active_scene.render_shadow()

        #self.active_scene.render_to_antialias()
        self.active_scene.draw()

    def draw(self):
        self.on_draw()


    def _draw(self, scene, shader, camera=None):

        camera = camera if camera else scene.camera

        # Enable 3D OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)
        #gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP)
        gl.glEnable(gl.GL_TEXTURE_2D)

        # Clear and Refresh Screen
        gl.glClearColor(scene.bgColor.r, scene.bgColor.g, scene.bgColor.b, 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Bind Shader
        shader.bind()

        # Send Uniforms that are constant across meshes.
        shader.uniform_matrixf('view_matrix', camera._view_matrix)
        shader.uniform_matrixf('projection_matrix', camera._projection_matrix)

        if shader == Window.genShader:
            shader.uniform_matrixf('shadow_view_matrix', scene.light._view_matrix)

            shader.uniformf('light_position', *scene.light.position)
            shader.uniformf('camera_position', *camera.position)

            shader.uniformi('hasShadow', int(self.shadow_rendering))
            shader.uniformi('ShadowMap', self.fbos['shadow'].texture)
            shader.uniformi('grayscale', int(self.grayscale))

        # Draw each visible mesh in the scene.
        for mesh in scene.meshes:

            if mesh.visible:

                # Send Model and Normal Matrix to shader.
                shader.uniform_matrixf('model_matrix_global', mesh.world._model_matrix)
                shader.uniform_matrixf('model_matrix_local', mesh.local._model_matrix)
                shader.uniform_matrixf('normal_matrix_global', mesh.world._normal_matrix)
                shader.uniform_matrixf('normal_matrix_local', mesh.local._normal_matrix)


                if shader == Window.genShader:
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
                        shader.uniformf('playerPos', *vec(self.player.position))
                        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.fbos['cube'].texture)  # No ActiveTexture needed, because only one Cubemap.

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
