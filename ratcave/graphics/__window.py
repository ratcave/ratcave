__author__ = 'nickdg'

from psychopy import visual
import pyglet.gl as gl
from __scene import Scene
from __camera import Camera
from __shader import Shader
from utils import *
from collections import namedtuple

FBO = namedtuple('FBO', 'id texture')
shader_path = join(split(__file__)[0], 'shaders')

def render_to_texture(draw_fun, win):
    # render to Frame Buffer Object (FBO) (depth values only)
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, win.fbos['shadow'].id)  # Rendering off-screen
    gl.glViewport(0, 0, win.texture_size, win.texture_size)

    draw_fun(*args, **kwargs)

    # Reset Render settings to normal and unbind FBO
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
    gl.glViewport(0, 0, win.size[0], win.size[1])


class Window(visual.Window):
    """Subclass of Pyglet window, with some defaults set to simplify ratCAVE script creation."""

    # General, Normal Shader
    genShader = Shader(open(join(shader_path, 'combShader.vert')).read(),
                    open(join(shader_path, 'combShader.frag')).read())

    shadowShader = Shader(open(join(shader_path, 'shadowShader.vert')).read(),
                        open(join(shader_path, 'shadowShader.frag')).read())

    aaShader = Shader(open(join(shader_path, 'antialiasShader.vert')).read(),
                        open(join(shader_path, 'antialiasShader.frag')).read())

    def __init__(self, active_scene, grayscale=False, *args, **kwargs):
        kwargs['allowStencil'] = False

        super(Window, self).__init__(*args, **kwargs)
        assert self.winType == 'pyglet', "Window Type must be 'pyglet' for ratCAVE to work."

        self.active_scene = active_scene  # For normal rendering.
        self.virtual_scene = None  # For dynamic cubemapping.
        self.grayscale = grayscale
        self.fbos = {'shadow': FBO(create_fbo(gl.GL_TEXTURE_2D, 2048, 2048, texture_slot=5, color=False, depth=True)),
                     'cube': FBO(create_fbo(gl.GL_TEXTURE_CUBE_MAP, 2048, 2048, texture_slot=0, color=True, depth=True, grayscale=self.grayscale)),
                     'antialias': FBO(create_fbo(gl.GL_TEXTURE_2D, 1280, 720, texture_slot=0, color=True, depth=True, grayscale=self.grayscale))
                     }
        self.texture_size = 2048
        self.player = None

    def set_virtual_scene(self, scene, from_viewpoint, to_mesh):
        """Set scene to render to cubemap, as well as the object whose position will be used as viewpoint and what mesh
        will be given the cubemap texture."""
        self.virtual_scene, self.player = scene, from_viewpoint
        to_mesh.cubemap = True


    def render_shadow(self, scene):

        # render to Frame Buffer Object (FBO) (depth values only)
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.fbos['shadow'].id)  # Rendering off-screen
        gl.glViewport(0, 0, self.texture_size , self.texture_size )

        # Render Scene
        scene._draw(Camera(fov_y=60., aspect=1., position=scene.light.position, rotation=scene.camera.rotation), Window.shadowShader)

        # Reset Render settings to normal and unbind FBO
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
        gl.glViewport(0, 0, self.size[0], self.size[1])

    def render_to_cubemap(self, scene):
        """
        Renders the scene, 360 degrees around a camera, to a mesh "toMesh" from the perspective of "fromObject".
        Currently, window width and height must also be supplied.
        """

        # Bind to Cubemap Framebuffer to render directly to the cubemap texture.
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.fbos['cube'].id)
        gl.glViewport(0, 0, self.texture_size, self.texture_size )  # Change viewport to square texture, as big as possible.


        # Render to Each Face of Cubemap texture, rotating the camera in the correct direction before each shot.
        cube_camera = Camera(fov_y=90., aspect=1., position=self.player.position)
        for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  # Created as class variable for performance reasons.
            cube_camera.rotation = rotation
            gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                         gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                                         self.fbos['cube'].texture,  0)  # Select face of cube texture to render to.
            self._draw(cube_camera, Window.genShader)  # Render

        # Restore previous camera position and lens settings
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)  # Unbind cubemap Framebuffer (so rendering to screen can be done)
        gl.glViewport(0, 0, self.size[0], self.size[1])  # Reset Viewport

    def render_to_antialias(self):

        # Bind to Cubemap Framebuffer to render directly to the cubemap texture.
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.fbos['antialias'].id)
        self._draw(self.camera, Window.genShader)
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)  # Unbind cubemap Framebuffer (so rendering to screen can be done)

        # Render Scene onto a fullscreen quad, after antialiasing.
        gl.glViewport(0, 0, self.size[0], self.size[1])  # Reset Viewport
        self._render_to_fullscreen_quad(Window.aaShader, self.fbos['antialias'].texture)



    def _render_to_fullscreen_quad(self, shader, texture):
        """Fairly general method, to be converted to more general deferred shading rendering method."""
        gl.glClearColor(self.bgColor.r, self.bgColor.g, self.bgColor.b, 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        shader.bind()
        shader.uniformf('frameBufSize', *self.size)
        shader.uniformi('image_texture', 0)
        shader.uniformi('grayscale', int(self.grayscale))
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        fullscreen_quad.render()
        shader.unbind()
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

