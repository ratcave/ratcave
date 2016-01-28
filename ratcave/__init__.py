from __future__ import absolute_import

from . import utils

# First import pyglet and turn off the debug_gl option.  This is great for performance!
import pyglet
pyglet.options['debug_gl'] = False

from . import _transformations
from . import resources
from .camera import Camera
from .mesh import Mesh, MeshData, Material
from .scene import Scene
from .wavefront import WavefrontReader
from .mixins import Physical
from .logger import Logger


__all__ = ['Camera', 'Logger', 'Mesh', 'MeshData', 'Material', 'Physical', 'Scene', 'WavefrontReader', 'resources']
