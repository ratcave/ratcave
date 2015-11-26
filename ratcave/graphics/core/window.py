__author__ = 'nickdg'

from os.path import join, split
from math import ceil, log

from psychopy import visual
import pyglet.gl as gl

from .camera import Camera
from .shader import Shader
from .mesh import fullscreen_quad
from . import utils

shader_path = join(split(__file__)[0], 'shaders')


    # General, Normal Shader
genShader = Shader(open(join(shader_path, 'combShader.vert')).read(),
                   open(join(shader_path, 'combShader.frag')).read())

shadowShader = Shader(open(join(shader_path, 'shadowShader.vert')).read(),
                      open(join(shader_path, 'shadowShader.frag')).read())

aaShader = Shader(open(join(shader_path, 'antialiasShader.vert')).read(),
                  open(join(shader_path, 'antialiasShader.frag')).read())

class Window(visual.Window):
    
    def __init__(self, active_scene, virtual_scene=None, grayscale=False, shadow_rendering=True, shadow_fov_y=80., texture_size=2048, autoCam=False, *args, **kwargs):
        """
        The Window that everything gets drawn in.  

        Args:
            active_scene (:py:class:`.Scene`): The scene that is rendered onto the Window.
            virtual_scene (:py:class:`.Scene`): Used for VR, the scene that gets rendered onto :py:class:`.Mesh` objects that have :py:attr:`.Mesh.cubemap` set to True (usually the 3d-modeled arena).
            grayscale (bool): Whether to render in grayscale or not--has some slight performance advantages, with more being planned in the future.
            shadow_rendering (bool): Whether to render shadows from the Scenes' :py:class:`.Light` position.
            shadow_fov_y (float): How wide an area to render shadows--too small and their may be weird squares projected, but larger numbers result in lower quality shadows.
            texture_size (int): How big the shadow and cube textures should be on a side.  For performance reasons, should be set to a value that is a power of two.
            autoCam (bool):
            fullscr (bool): Defaults to False, allows a full screen to be used.
            screen (int): Which number screen to place the window on.
            size (tuple): Size of the window in pixels (X, Y). Defaults to (800, 600)
            pos (None or (x,y)): 
        """
    
        # Set default Window values for making sure Psychopy windows work with it.
        kwargs['allowStencil'] = False
        super(Window, self).__init__(*args, **kwargs)
        assert self.winType == 'pyglet', "Window Type must be 'pyglet' for ratCAVE to work."

        # Assign data to window after OpenGL context initialization
        self.active_scene = active_scene  # For normal rendering.
        self.active_scene.camera.aspect = float(self.size[0]) / self.size[1]  # Camera aspect ratio should match screen size, at least for the active scene.
        self.virtual_scene = virtual_scene  # For dynamic cubemapping.
        if self.virtual_scene:
            self.virtual_scene.camera.fov_y = 90.
            self.virtual_scene.camera.aspect = 1.
        self.autoCam = autoCam  # Convenience attribute for moving virtual scene's light to the active scene's position.


        if grayscale:
            raise NotImplementedError("Grayscale not quite properly working yet.  To be fixed!")
        self.grayscale = grayscale
        aa_texture_size = int(pow(2, ceil(log(max(self.size), 2))))  # Automatically get next power-of-2 size of monitor edge
        self.fbos = {'shadow': utils.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=5, color=False, depth=True),
                     'vrshadow': utils.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=6, color=False, depth=True),
                     'cube': utils.create_fbo(gl.GL_TEXTURE_CUBE_MAP, texture_size, texture_size, texture_slot=0, color=True, depth=True, grayscale=self.grayscale),
                     'antialias': utils.create_fbo(gl.GL_TEXTURE_2D, aa_texture_size, aa_texture_size, texture_slot=0, color=True, depth=True, grayscale=self.grayscale)
                     }
        self.texture_size = 2048

        # Antialiasing attributes
        self.fullscreen_quad = fullscreen_quad

        # Shadow Rendering attributes
        self.shadow_rendering = shadow_rendering
        self.__shadow_fov_y = shadow_fov_y
        self.shadow_projection_matrix = Camera(fov_y=shadow_fov_y, aspect=1.).projection_matrix.T.ravel()

    @property
    def shadow_fov_y(self):
        """Fov_y for calculating shadow area.  Automatically updates shadow_projection_matrix when set."""
        return self.__shadow_fov_y

    @shadow_fov_y.setter
    def shadow_fov_y(self, value):
        self.shadow_projection_matrix = Camera(fov_y=value, aspect=1.).projection_matrix
        self.__shadow_fov_y = value

    def render_shadow(self, scene):
        """Update light view matrix to match the camera's, then render to the Shadow FBO depth texture."""
        #scene.light.rotation[:] = scene.camera.rotation[:]  # only works while spotlights aren't implemented, otherwise may have to be careful.
        fbo = self.fbos['shadow'] if scene == self.active_scene else self.fbos['vrshadow']
        with utils.render_to_fbo(self, fbo):
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
            shadowShader.bind()
            shadowShader.uniform_matrixf('view_matrix', scene.light.view_matrix.T.ravel())
            shadowShader.uniform_matrixf('projection_matrix', self.shadow_projection_matrix)
            [mesh.render(shadowShader) for mesh in scene.meshes if mesh.visible]
            shadowShader.unbind()


    def render_to_cubemap(self, scene):
        """Renders the scene 360-degrees about the camera's position onto a cubemap texture."""

        # TODO: Combat slowness of glUniformMat4v calls in Python by sending data to a Geometry shader to render all faces in a single pass.
        # Render the scene
        with utils.render_to_fbo(self, self.fbos['cube']):
            for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.
                scene.camera.rotation = rotation
                gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                             gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                                             self.fbos['cube'].texture,  0)  # Select face of cube texture to render to.
                self._draw(scene, genShader, send_light_and_camera_intrinsics=(face==0))  # Render

    def render_to_antialias(self, scene):
        """Render the scene to texture, then render the texture to screen after antialiasing it."""
        # First Render the scene to the antialias texture
        with utils.render_to_fbo(self, self.fbos['antialias']):
            self._draw(scene, genShader)

        #Then, Render the antialias texture to the screen on a fullscreen quad mesh.
        gl.glClearColor(.5, .5, .5, 1.)  # Make background color gray for debugging purposes, but won't matter.
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        aaShader.bind()
        aaShader.uniformf('frameBufSize', *self.size)
        aaShader.uniformi('image_texture', 0)
        aaShader.uniformi('grayscale', int(self.grayscale))
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.fbos['antialias'].texture)

        self.fullscreen_quad.render(aaShader)
        aaShader.unbind()
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def draw(self):
        """Active scene drawn, virtual scene is rendered to a cubemap. iF auto_light_position is True, then automatically
        put the lights for the active and virtual scene to the active scene's camera position (useful for convenient CAVE
        api.)"""

        # Pre-set model and normal matrices to increase draw time performance
        self.active_scene.camera.preset_mats()
        for mesh in self.active_scene.meshes:
            mesh._manually_set_mats()

        if self.virtual_scene:

            # Pre-set model and normal matrices to increase draw time performance
            self.virtual_scene.camera.preset_mats()
            for mesh in self.virtual_scene.meshes:
                mesh._manually_set_mats()

            if self.autoCam:
                # Put virtual scene's light in active scene's camera position before rendering.
                self.virtual_scene.light.position[:] = self.active_scene.camera.position[:]
                self.active_scene.light.position[:] = self.active_scene.camera.position[:]

            # Render shadow and cubemap from virtual camera's position.
            if self.shadow_rendering:
                self.render_shadow(self.active_scene)
                self.render_shadow(self.virtual_scene)

            # Render to cubemap texture.
            self.render_to_cubemap(self.virtual_scene)

        elif self.shadow_rendering:
            self.render_shadow(self.active_scene)

        self.render_to_antialias(self.active_scene)
        #self._draw(self.active_scene, genShader)


    def _draw(self, scene, shader, send_light_and_camera_intrinsics=True):

        # Enable 3D OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)
        #gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP)
        gl.glEnable(gl.GL_TEXTURE_2D)

        # Clear and Refresh Screen
        gl.glClearColor(*scene.bgColor.rgba)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Bind Shader
        shader.bind()

        # Send Uniforms that are constant across meshes.
        shader.uniform_matrixf('view_matrix', scene.camera.view_matrix.T.ravel())

        if send_light_and_camera_intrinsics:
            shader.uniform_matrixf('projection_matrix', scene.camera._projmat_preset)

            shader.uniform_matrixf('shadow_projection_matrix', self.shadow_projection_matrix.T.ravel())
            shader.uniform_matrixf('shadow_view_matrix', scene.light.view_matrix.T.ravel())

            shader.uniformf('light_position', *scene.light.position)
            shader.uniformf('camera_position', *scene.camera.position)

            shader.uniformi('hasShadow', int(self.shadow_rendering))
            shadow_slot = self.fbos['shadow'].texture_slot if scene == self.active_scene else self.fbos['vrshadow'].texture_slot
            shader.uniformi('ShadowMap', shadow_slot)
            shader.uniformi('grayscale', int(self.grayscale))

        # Draw each visible mesh in the scene.
        for mesh in scene.meshes:

            if mesh.visible:

                # Change Material to Mesh's
                shader.uniformf('ambient', *mesh.material.ambient.rgb)
                shader.uniformf('diffuse', *mesh.material.diffuse.rgb)
                shader.uniformf('spec_color', *mesh.material.spec_color.rgb)
                shader.uniformf('spec_weight', mesh.material.spec_weight)
                shader.uniformf('opacity', mesh.material.diffuse.a)
                shader.uniformi('hasLighting', mesh.lighting)

                # Bind Cubemap if mesh is to be rendered with the cubemap.
                shader.uniformi('hasCubeMap', int(mesh.cubemap))
                if mesh.cubemap:
                    assert self.virtual_scene, "Window.virtual_scene must be set for cubemap to render!"
                    shader.uniformf('playerPos', *utils.vec(self.virtual_scene.camera.position))
                    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.fbos['cube'].texture)  # No ActiveTexture needed, because only one Cubemap.

                # Bind Textures and apply Material
                shader.uniformi('hasTexture', int(bool(mesh.texture)))
                shader.uniformi('ImageTextureMap', 2)
                if mesh.texture:
                    gl.glActiveTexture(gl.GL_TEXTURE2)
                    gl.glBindTexture(gl.GL_TEXTURE_2D, mesh.texture.id)
                    gl.glActiveTexture(gl.GL_TEXTURE0)

                # Draw the Mesh
                mesh.render(shader)  # Bind VAO.

        # Unbind Shader
        shader.unbind()

    def flip(self, *args, **kwargs):
        """Sends the framebuffer contents to the display.  Call each frame after the draw method!"""
        super(Window, self).flip(*args, **kwargs)

    def close(self):
        """Closes the window."""
        super(Window, self).close()
