from __future__ import absolute_import

import warnings

from . import mixins, Camera


class Scene(object):

    def __init__(self, meshes=[], camera=None, light=None, bgColor=(0., 0., 0., 1.)):
        """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)
        if len(set(mesh.data.name for mesh in self.meshes)) != len(self.meshes):
            warnings.warn('Warning: Mesh.data.names not all unique--log data will overwrite some meshes!')
        self.camera = Camera() if not camera else camera # create a default Camera object
        self.light = mixins.Physical() if not light else light
        self.bgColor = mixins.Color(*bgColor)

    def update_matrices(self):
        """calls the "update_matrices" method on all meshes and camera, so that all data is current."""
        for obj in self.meshes + [self.camera]:
            obj.update_matrices()