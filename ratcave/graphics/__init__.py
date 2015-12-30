from __future__ import absolute_import

__author__ = 'ratcave'

"""The grapihcs module."""



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


# Create the projector
def __build_projector():
    import pickle
    import appdirs
    from os import path

    proj_file = path.join(appdirs.user_data_dir("ratCAVE"), "projector_data.pickle")  # TODO: Use relative import to get data_dir from ratCAVE.__init__.py
    if path.exists(proj_file):
        projector_data = pickle.load(open(proj_file))
        projector = Camera(position=projector_data['position'],
                           #rotation=projector_data['rotation'],
                           fov_y=projector_data['fov_y'])
        projector._rot_matrix = projector_data['rotation']
    else:
        print("Cannot auto-create projector until opti_projector_calibration script is run.  projector object will be set to None.")
        projector = None

    return projector

projector = __build_projector()



__all__ = ['Camera', 'Logger', 'Mesh', 'MeshData', 'Material', 'Physical', 'Scene', 'Window', 'WavefrontReader', 'projector', 'resources']

