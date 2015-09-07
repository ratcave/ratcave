__author__ = 'nickdg'

from psychopy import visual
import pyglet.gl as gl
from __scene import Scene
from __camera import Camera
from __shader import Shader
from __mesh import fullscreen_quad
from __mixins import Physical
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

    def __init__(self, active_scene, virtual_scene=None, grayscale=False, shadow_rendering=True, shadow_fov_y=60., *args, **kwargs):

        # Set default Window values for making sure Psychopy windows work with it.
        kwargs['allowStencil'] = False
        super(Window, self).__init__(*args, **kwargs)
        assert self.winType == 'pyglet', "Window Type must be 'pyglet' for ratCAVE to work."

        # Assign data to window after OpenGL context initialization
        self.active_scene = active_scene  # For normal rendering.
        self.virtual_scene = virtual_scene  # For dynamic cubemapping.
        self.grayscale = grayscale
        self.fbos = {'shadow': FBO(create_fbo(gl.GL_TEXTURE_2D, 2048, 2048, texture_slot=5, color=False, depth=True)),
                     'cube': FBO(create_fbo(gl.GL_TEXTURE_CUBE_MAP, 2048, 2048, texture_slot=0, color=True, depth=True, grayscale=self.grayscale)),
                     'antialias': FBO(create_fbo(gl.GL_TEXTURE_2D, 1280, 720, texture_slot=0, color=True, depth=True, grayscale=self.grayscale))
                     }
        self.texture_size = 2048

        # Antialiasing attributes
        self.fullscreen_quad = fullscreen_quad

        # Shadow Rendering attributes
        self.shadow_rendering = shadow_rendering
        self.__shadow_fov_y = shadow_fov_y
        self.shadow_projection_matrix = Camera(fov_y=shadow_fov_y., aspect=1.)._projection_matrix

        # Cubemap attributes
        self.player = Physical()
        self.cubemap_camera = Camera(fov_y=90., aspect=1., position=self.player.position)


    @property
    def shadow_fov_y(self):
        """Fov_y for calculating shadow area.  Automatically updates shadow_projection_matrix when set."""
        return self.__shadow_fov_y

    @shadow_fov_y.setter
    def shadow_fov_y(self, value):
        self.shadow_projection_matrix = Camera(fov_y=value, aspect=1.)._projection_matrix
        self.__shadow_fov_y = value


    def set_virtual_scene(self, scene, from_viewpoint, to_mesh):
        """Set scene to render to cubemap, as well as the object whose position will be used as viewpoint and what mesh
        will be given the cubemap texture."""
        self.virtual_scene, self.player = scene, from_viewpoint
        to_mesh.cubemap = True

    def render_shadow(self, scene):
        """Update light view matrix to match the camera's, then render to the Shadow FBO depth texture."""
        scene.light.rotation = scene.camera.rotation  # only works while spotlights aren't implemented, otherwise may have to be careful.
        with render_to_fbo(self, self.fbos['shadow']):
            gl.glClearColor(scene.bgColor.r, scene.bgColor.g, scene.bgColor.b, 1.)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            Window.shadowShader.bind()
            Window.shadowShader.uniform_matrixf('view_matrix', scene.light._view_matrix)
            Window.shadowShader.uniform_matrixf('projection_matrix', self.shadow_projection_matrix)
            [mesh.render(Window.shadowShader) for mesh in scene if mesh.visible]
            Window.shadowShader.unbind()

    def render_to_cubemap(self, scene):
        """Renders the scene 360-degrees about the player's position onto a cubemap texture."""
        # Center cubemap camera on the player
        self.cubemap_camera.position = self.player.position

        # Render the scene
        with render_to_fbo(self, self.fbos['cube']):
            for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.
                self.cubemap_camera.rotation = rotation
                gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                             gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                                             self.fbos['cube'].texture,  0)  # Select face of cube texture to render to.
                self._draw(scene, Window.genShader, self.cubemap_camera)  # Render

    def render_to_antialias(self):
        """Render the scene to texture, then render the texture to screen after antialiasing it."""
        with render_to_fbo(self, self.fbos['antialias']):
            gl.glClearColor(.5, .5, .5, 1.)  # Make background color gray for debugging purposes, but won't matter.
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            Window.aaShader.bind()
            Window.aaShader.uniformf('frameBufSize', *self.size)
            Window.aaShader.uniformi('image_texture', 0)
            Window.aaShader.uniformi('grayscale', int(self.grayscale))
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.fbos['antialias'].texture)
            self.fullscreen_quad.render(Window.aaShader)
            Window.aaShader.unbind()
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def draw(self):
        """Active scene drawn, virtual scene is rendered to a cubemap. iF auto_light_position is True, then automatically
        put the lights for the active and virtual scene to the active scene's camera position (useful for convenient CAVE
        api.)"""

        if self.virtual_scene:
            # Put light in camera's position before rendering.
            self.virtual_scene.light.position = self.active_scene.camera.position
            self.active_scene.light.position = self.active_scene.camera.position

            # Render shadow and cubemap from virtual camera's position.
            if self.shadow_rendering:
                self.virtual_scene.render_shadow()
            self.virtual_scene.render_to_cubemap()
        elif self.shadow_rendering:
            self.active_scene.render_shadow()

        #self.active_scene.render_to_antialias()
        self._draw(self.active_scene, Window.genShader, self.active_scene.camera)


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
            shader.uniform_matrixf('shadow_projection_matrix', self.shadow_projection_matrix)
            shader.uniform_matrixf('shadow_view_matrix', scene.light._view_matrix)

            shader.uniformf('light_position', *scene.light.position)
            shader.uniformf('camera_position', *camera.position)

            shader.uniformi('hasShadow', int(self.shadow_rendering))
            shader.uniformi('ShadowMap', self.fbos['shadow'].texture)
            shader.uniformi('grayscale', int(self.grayscale))

        # Draw each visible mesh in the scene.
        for mesh in scene.meshes:

            if mesh.visible:

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
                mesh.render(shader)  # Bind VAO.

        # Unbind Shader
        shader.unbind()
