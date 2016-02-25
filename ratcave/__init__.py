

from . import utils

# First import pyglet and turn off the debug_gl option.  This is great for performance!
import pyglet
pyglet.options['debug_gl'] = False

from . import resources
from .shader import Shader, Uniform
from .fbo import FBO
from.texture import Texture
from .mixins import Physical
from .camera import Camera
from .light import Light
from .scene import Scene
from .wavefront import WavefrontReader
from .mesh import Mesh, MeshData, Material

__all__ = ['Camera', 'Mesh', 'MeshData', 'Material', 'Physical', 'Scene', 'WavefrontReader', 'resources']
