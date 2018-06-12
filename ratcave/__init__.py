from __future__ import absolute_import

from .coordinates import RotationEulerDegrees, RotationQuaternion, RotationEulerRadians, Translation, Scale

try:
    from . import resources
    from .resources import default_shader, default_camera, default_light
except ImportError:
    pass
from . import utils
from .camera import Camera, PerspectiveProjection, OrthoProjection, CameraGroup, StereoCameraGroup
from .collision import CylinderCollisionChecker, SphereCollisionChecker
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
from .utils.gl import POINTS, LINE_LOOP, LINES, TRIANGLES, clear_color
from . import experimental
from .wavefront import WavefrontReader


import pkg_resources
__version__ = pkg_resources.get_distribution('ratcave').version
__all__ = ['Camera', 'Mesh', 'Material', 'Physical', 'Scene', 'Light', 'WavefrontReader']
