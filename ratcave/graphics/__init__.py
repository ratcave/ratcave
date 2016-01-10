from __future__ import absolute_import

"""The graphics module."""

# First import pyglet and turn off the debug_gl option.  This is great for performance!
import pyglet
pyglet.options['debug_gl'] = False

from . import _transformations
from . import resources
from . import utils
from .camera import Camera
from .mesh import Mesh, MeshData, Material
from .scene import Scene
from .window import Window
from .wavefront import WavefrontReader
from .mixins import Physical
from .logger import Logger


__all__ = ['Camera', 'Logger', 'Mesh', 'MeshData', 'Material', 'Physical', 'Scene', 'Window', 'WavefrontReader', 'resources']
