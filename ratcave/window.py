from __future__ import absolute_import

from os.path import join, split
from math import ceil, log

from pyglet.window import Window as PygletWindow
import pyglet.gl as gl

from .camera import Camera
from .shader import Shader
from .mesh import fullscreen_quad
from .utils import gl as ugl

shader_path = join(split(__file__)[0], 'shaders')


# General, Normal Shader
genShader = Shader(open(join(shader_path, 'combShader.vert')).read(),
                   open(join(shader_path, 'combShader.frag')).read())

shadowShader = Shader(open(join(shader_path, 'shadowShader.vert')).read(),
                      open(join(shader_path, 'shadowShader.frag')).read())

aaShader = Shader(open(join(shader_path, 'antialiasShader.vert')).read(),
                  open(join(shader_path, 'antialiasShader.frag')).read())

drawstyle = {'fill':gl.GL_TRIANGLES, 'line':gl.GL_LINE_LOOP, 'point':gl.GL_POINTS}


class Window(PygletWindow):
    
    def __init__(self, *args, **kwargs):
    
        # Set default Window values for making sure Psychopy windows work with it.
        super(Window, self).__init__(*args, **kwargs)

        self.fbos = {'shadow': ugl.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=5, color=False, depth=True),
                     'vrshadow': ugl.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=6, color=False, depth=True),
                     'cube': ugl.create_fbo(gl.GL_TEXTURE_CUBE_MAP, texture_size*2, texture_size*2, texture_slot=0, color=True, depth=True, grayscale=self.grayscale),
                     'antialias': ugl.create_fbo(gl.GL_TEXTURE_2D, aa_texture_size, aa_texture_size, texture_slot=0, color=True, depth=True, grayscale=self.grayscale)
                     }

    def render_shadow(self, scene):
        """Update light view matrix to match the camera's, then render to the Shadow FBO depth texture."""
        #scene.light.rotation[:] = scene.camera.rotation[:]  # only works while spotlights aren't implemented, otherwise may have to be careful.
        fbo = self.fbos['shadow'] if scene == self.active_scene else self.fbos['vrshadow']
        with ugl.render_to_fbo(self, fbo):
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
            shadowShader.bind()
            shadowShader.uniform_matrixf('view_matrix', scene.light.view_matrix.T.ravel())
            shadowShader.uniform_matrixf('projection_matrix', self.shadow_cam.projection_matrix.T.ravel())

            [self.render_mesh(mesh, shadowShader) for mesh in scene.meshes if mesh.visible]
            shadowShader.unbind()

    def render_to_cubemap(self, scene):
        """Renders the scene 360-degrees about the camera's position onto a cubemap texture."""

        # TODO: Combat slowness of glUniformMat4v calls in Python by sending data to a Geometry shader to render all faces in a single pass.
        # Render the scene
        with ugl.render_to_fbo(self, self.fbos['cube']):
            for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.
                scene.camera.rotation = rotation
                gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                             gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                                             self.fbos['cube'].texture,  0)  # Select face of cube texture to render to.
                self._draw(scene, genShader, send_light_and_camera_intrinsics=(face == 0))  # Render

    def render_to_antialias(self, scene):
        """Render the scene to texture, then render the texture to screen after antialiasing it."""
        # First Render the scene to the antialias texture
        with ugl.render_to_fbo(self, self.fbos['antialias']):
            self._draw(scene, genShader)

        # Then, Render the antialias texture to the screen on a full-screen quad mesh.
        gl.glClearColor(1., .5, .5, 1.)  # Make background color gray for debugging purposes, but won't matter.
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        aaShader.bind()
        aaShader.uniformf('frameBufSize', *self.size)
        aaShader.uniformi('image_texture', 0)
        aaShader.uniformi('grayscale', int(self.grayscale))
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.fbos['antialias'].texture)

        self.render_mesh(self.fullscreen_quad, aaShader)
        aaShader.unbind()
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)