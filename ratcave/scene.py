import pyglet.gl as gl

from . import Camera, Light, resources, mesh
from .utils import gl as glutils
from .texture import TextureCube
from .draw import HasUniforms


class Scene(HasUniforms):

    def __init__(self, meshes=None, camera=None, light=None, bgColor=(0.4, 0.4, 0.4), **kwargs):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""
        super(Scene, self).__init__(**kwargs)
        # Initialize List of all Meshes to draw

        self.meshes = meshes
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = Light() if not light else light
        self.bgColor = bgColor

    @property
    def meshes(self):
        return self._meshes

    @meshes.setter
    def meshes(self, value):
        if not hasattr(value, '__iter__'):
            raise TypeError("Scene.meshes must be iterable.")
        for el in value:
            if not isinstance(el, mesh.Mesh):
                raise TypeError("All elements in Scene.meshes must be a Mesh.")
        self._meshes = value

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, value):
        if not isinstance(value, Camera):
            raise TypeError("Scene.camera must be a Camera instance.")
        self._camera = value
        self.uniforms.update(self._camera.uniforms)

    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, value):
        if not isinstance(value, Light):
            raise TypeError("Scene.light must be a Light instance.")
        self._light = value
        self.uniforms.update(self._light.uniforms)

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

            if clear:
                self.clear()

            self.camera.update()
            self.light.update()
            self.uniforms.send()

            for mesh in self.meshes:
                mesh.draw(send_uniforms=send_mesh_uniforms)


    def draw360_to_texture(self, cubetexture, userdata={},
             gl_states=(gl.GL_DEPTH_TEST, gl.GL_POINT_SMOOTH, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D)):#, gl.GL_BLEND)):
        """
        Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light, and
        applies it to each face of cubetexture, which should be currently bound to an FBO.
        """

        assert self.camera.lens.aspect == 1. and self.camera.lens.fov_y == 90  # todo: fix aspect property, which currently reads from viewport.
        assert type(cubetexture) == TextureCube, "Must render to TextureCube"

        # Enable 3D OpenGL states (glEnable, then later glDisable)
        with glutils.enable_states(gl_states):
            # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            self.light.update()

            for mesh_idx, mesh in enumerate(self.meshes):
                for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):
                    cubetexture.attach_to_fbo(face)
                    if not mesh_idx:
                        self.clear()

                    self.camera.rotation.xyz = rotation
                    self.camera.update()
                    self.uniforms.send()

                    mesh.draw(send_uniforms=not face)


