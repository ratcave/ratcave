import pyglet.gl as gl
from . import Camera, Light, Mesh, EmptyEntity
from .texture import TextureCube
from .utils import mixins, clear_color
from .gl_states import GLStateManager



class Scene(mixins.NameLabelMixin):

    def __init__(self, meshes=(), camera=None, light=None, bgColor=(0.4, 0.4, 0.4),
                 gl_states=(gl.GL_DEPTH_TEST, gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_2D, gl.GL_CULL_FACE), **kwargs):
        """
        Returns a Scene object, that manages the creation of the scene needed to view the projection of the Objects.
        Class manages rendering of Meshes, Lights and Cameras.

        Args:
            meshes (Mesh): all of Mesh instances that you want to view in the Scene
            camera (Camera): a Camera instance, if not provided created automatically
            light (Light): a Light instance, if not provided created automatically
            bgColor (float):  defines the color of the background

        Returns:
            Scene instance

        """
        super(Scene, self).__init__(**kwargs)

        self.meshes = meshes
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = Light() if not light else light
        self.bgColor = bgColor

        self.gl_states = GLStateManager(gl_states)

    def __repr__(self):
        return "<Scene(name='{self.name}'), meshes={self.meshes}, light={self.light}, camera={self.camera}>".format(self=self)

    def clear(self):
        """Clear Screen and Apply Background Color"""
        clear_color(*self.bgColor)

    def draw(self, clear=True):
        """Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light."""
        if clear:
            self.clear()

        with self.gl_states, self.camera, self.light:
            for mesh in self.meshes:
                try:
                    mesh.draw()
                except AttributeError:
                    pass

    def draw_anaglyph(self, clear=True, inter_eye_distance=.08):
        cam = self.camera
        orig_cam_position = cam.uniforms['view_matrix'][0, 3]
        gl.glColorMask(True, False, False, True)
        cam.uniforms['view_matrix'][0, 3] += inter_eye_distance / 2.
        self.draw(clear=clear)

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glColorMask(False, True, True, True)
        cam.uniforms['view_matrix'][0, 3] -= inter_eye_distance
        self.draw(clear=clear)

        gl.glColorMask(True, True, True, True)
        cam.uniforms['view_matrix'][0, 3] = orig_cam_position


    def draw360_to_texture(self, cubetexture, **kwargs):
        """
        Draw each visible mesh in the scene from the perspective of the scene's camera and lit by its light, and
        applies it to each face of cubetexture, which should be currently bound to an FBO.
        """

        assert self.camera.projection.aspect == 1. and self.camera.projection.fov_y == 90  # todo: fix aspect property, which currently reads from viewport.
        if not isinstance(cubetexture, TextureCube):
            raise ValueError("Must render to TextureCube")

        # for face, rotation in enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):
        old_rotation = self.camera.rotation
        self.camera.rotation = self.camera.rotation.to_euler(units='deg')
        for face, rotation in enumerate([[180, -90, 0], [180, 90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]):  #first 2 switched
            self.camera.rotation.xyz = rotation
            cubetexture.attach_to_fbo(face)
            self.draw(**kwargs)
        self.camera.rotation = old_rotation
