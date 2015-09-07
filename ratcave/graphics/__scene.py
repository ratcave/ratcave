import __mixins as mixins
from __camera import Camera

class Scene:

    def __init__(self, meshes, camera=Camera(), light=mixins.Physical(), bgColor=mixins.Color(0,0,0)):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)
        self.camera = camera  # create a default Camera object
        self.light = light
        self.bgColor = bgColor



