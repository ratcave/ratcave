from os.path import split, join
from ctypes import byref
from utils import *
import __mixins as mixins
from __camera import Camera
from __shader import Shader
from __mesh import fullscreen_quad


class Scene:
    """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

    # Lights
    light = mixins.Physical()

    def __init__(self, *meshes):
        """Initialize the Scene object using Meshes as input../s"""

        self.camera = Camera()  # create a default Camera object
        self.bgColor = mixins.Color(0, 0, 0)

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)

