from . import mixins
from .camera import Camera

import json

def encode_obj(obj):
    """Handles json obj and numpy array encoding."""
    try:
        return obj.__dict__
    except AttributeError:
        try:
            return obj.tolist()
        except AttributeError:
            return str(obj)


physical_keys = mixins.Physical().__dict__
def encode_phys(obj):
    try:
        d = obj.__dict__
        dd = {key: d[key] for key in d if key in ['light', 'camera', 'meshes', 'local', 'world']}
        dd.update({key: d[key] for key in d if key in physical_keys})
        try:
            dd['visible'] = d['visible']
        except:
            pass
        return dd
    except:
        return




class Scene(object):

    def __init__(self, meshes=[], camera=None, light=None, bgColor=(0., 0., 0.)):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = mixins.Physical() if not light else light
        self.bgColor = mixins.Color(*bgColor)

    def to_json_header(self):
        return json.dumps(self, default=encode_obj)


