import mixins
from . import Camera

class Scene:

    def __init__(self, meshes=[], camera=None, light=None, bgColor=(0., 0., 0.)):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = mixins.Physical() if not light else light
        self.bgColor = mixins.Color(*bgColor)



