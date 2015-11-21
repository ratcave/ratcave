from . import mixins
from .camera import Camera
import warnings
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
    """Only grabs the data that is expected to change frame to frame"""
    try:
        d = obj.__dict__
        dd = {key: d[key] for key in d if key in ['light', 'camera', 'local', 'world']}
        dd.update({key: d[key] for key in d if key in physical_keys})
        try:
            dd.update({'meshes': obj.mesh_dict})
        except:
            pass
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
        if len(set(mesh.data.name for mesh in self.meshes)) != len(self.meshes):
            warnings.warn('Warning: Mesh.data.names not all unique--log data will overwrite some meshes!')
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = mixins.Physical() if not light else light
        self.bgColor = mixins.Color(*bgColor)

    @property
    def mesh_dict(self):
        return {mesh.data.name:mesh for mesh in self.meshes}

    def to_json_header(self):
        return json.dumps(self, default=encode_obj)

    def to_json_tracker(self):
        return json.dumps(self, default=encode_phys)



