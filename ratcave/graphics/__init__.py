__author__ = 'ratcave'


import transformations
import resources
import utils
from __camera import Camera
from __mesh import Mesh
from __scene import Scene
from __window import Window
from __wavefront import WavefrontReader
from __mixins import Physical


# Create the projector
def __build_projector():
    import pickle
    import appdirs
    from os import path

    proj_file = path.join(appdirs.user_data_dir("ratCAVE"), "projector_data.pickle")  # TODO: Use relative import to get data_dir from ratCAVE.__init__.py
    if path.exists(proj_file):
        projector_data = pickle.load(open(proj_file))
        projector = Camera(position=projector_data['position'],
                           rotation=projector_data['rotation'],
                           fov_y=projector_data['fov_y'])
    else:
        print("Cannot auto-create projector until opti_projector_calibration script is run.  projector object will be set to None.")
        projector = None

    return projector

projector = __build_projector()



__all__ = ['Camera', 'Mesh', 'Physical', 'Scene', 'Window', 'WavefrontReader', 'projector']

