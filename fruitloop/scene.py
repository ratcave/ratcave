import pyglet.gl as gl

from . import Camera, Light
from .utils import gl as glutils
from .texture import TextureCube
from .utils import mixins

class Scene(mixins.NameLabelMixin):

    def __init__(self, meshes=None, camera=None, light=None, bgColor=(0.4, 0.4, 0.4),
                 gl_states=(gl.GL_DEPTH_TEST, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D, gl.GL_CULL_FACE), **kwargs):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""
        super(Scene, self).__init__(**kwargs)
        # Initialize List of all Meshes to draw

        self.meshes = meshes
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = Light() if not light else light
        self.bgColor = bgColor
        self.gl_states = gl_states

    def __repr__(self):
        return "<Scene(name='{self.name}'), meshes={self.meshes}, light={self.light}, camera={self.camera}>".format(self=self)

    @property
    def meshes(self):
        return self._meshes

    @meshes.setter
    def meshes(self, value):
        if not hasattr(value, '__iter__'):
            raise TypeError("Scene.meshes must be iterable.")
        for el in value:
            if not hasattr(el, 'draw'):
                raise TypeError("All elements in Scene.meshes must have a draw() method.")
        self._meshes = value

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, value):
        if not isinstance(value, Camera):
            raise TypeError("Scene.camera must be a Camera instance.")
        self._camera = value

    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, value):
        if not isinstance(value, Light):
            raise TypeError("Scene.light must be a Light instance.")
        self._light = value

    def clear(self):
        """Clear Screen and Apply Background Color"""
        gl.glClearColor(*(self.bgColor + (1.,)))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def draw(self, clear=True):
        """Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light."""

        if clear:
            self.clear()

        with glutils.enable_states(self.gl_states):

            self.camera.update()
            self.camera.uniforms.send()
            self.light.update()
            self.light.uniforms.send()

            for mesh in self.meshes:
                mesh.draw()

    def draw360_to_texture(self, cubetexture):
        """
        Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light, and
        applies it to each face of cubetexture, which should be currently bound to an FBO.
        """

        assert self.camera.projection.aspect == 1. and self.camera.projection.fov_y == 90  # todo: fix aspect property, which currently reads from viewport.
        assert type(cubetexture) == TextureCube, "Must render to TextureCube"

        # for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):
        old_rotation = self.camera.rotation
        self.camera.rotation = self.camera.rotation.to_euler(units='deg')
        for face, rotation in enumerate([[180, -90, 0], [180, 90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  #first 2 switched
            self.camera.rotation.xyz = rotation
            cubetexture.attach_to_fbo(face)
            self.draw(clear=True)
        self.camera.rotation = old_rotation



