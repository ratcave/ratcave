from __future__ import absolute_import

from . import utils
from .utils import gl as gl
from .utils.gl import clear_color
try:
    from . import resources
    from .resources import default_shader, default_camera, default_light
except ImportError:
    pass
from .coordinates import RotationEulerDegrees, RotationQuaternion, RotationEulerRadians, Translation, Scale
from .camera import Camera, PerspectiveProjection, OrthoProjection, CameraGroup, StereoCameraGroup
from .collision import ColliderSphere, ColliderCube, ColliderCylinder
from .fbo import FBO
from .gl_states import GLStateManager, default_states
from .light import Light
from .materials import Material
from .mesh import Mesh, EmptyEntity, gen_fullscreen_quad
from .physical import Physical, PhysicalGraph
from .scene import Scene
from .shader import Shader, UniformCollection
from .texture import Texture, TextureCube, DepthTexture
from .scenegraph import SceneGraph
from . import experimental
from .wavefront import WavefrontReader


import pkg_resources
__version__ = pkg_resources.get_distribution('ratcave').version
__all__ = ['Camera', 'Mesh', 'Material', 'Physical', 'Scene', 'Light', 'WavefrontReader']
