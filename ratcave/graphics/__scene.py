import __mixins as mixins
from __camera import Camera

class Scene:

    def __init__(self, camera=Camera(), light=mixins.Physical(), bgColor=mixins.Color(0,0,0), *meshes):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

        # Initialize List of all Meshes to draw
        assert meshes, "Scene initialization requires meshes as input."
        self.meshes = list(meshes)
        self.camera = camera  # create a default Camera object
        self.light = light
        self.bgColor = bgColor



