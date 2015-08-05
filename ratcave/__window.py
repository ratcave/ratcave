__author__ = 'nickdg'

from psychopy import visual

from __scene import Scene


class Window(visual.Window):
    """Subclass of Pyglet window, with some defaults set to simplify ratCAVE script creation."""

    def __init__(self, active_scene, autoUpdate=False, *args, **kwargs):
        kwargs['winType'] = 'pyglet'
        kwargs['allowStencil'] = False

        super(Window, self).__init__(*args, **kwargs)

        self.active_scene = active_scene  # For normal rendering.
        self.virtual_scene = None  # For dynamic cubemapping.

        self.autoUpdate = autoUpdate  # Will automatically call Scene.update_positions() before each on_draw call if True.

    def set_virtual_scene(self, scene, from_viewpoint, to_mesh):
        """Set scene to render to cubemap, as well as the object whose position will be used as viewpoint and what mesh
        will be given the cubemap texture."""
        self.virtual_scene = scene
        Scene.player = from_viewpoint
        to_mesh.cubemap = True

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

