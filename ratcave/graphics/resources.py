from __future__ import absolute_import
from os import path as __path
from appdirs import user_data_dir as __data_dir

"""
Here are some sample obj files for prototyping your app!
"""

# This is an easy way to get the filepaths of some oft-used resources for displaying simple scenes.

resource_path = __path.join(__path.split(__file__)[0],'assets')

# Images
img_uvgrid = __path.join(resource_path,'uvgrid.png')
img_colorgrid = __path.join(resource_path, 'colorgrid.png')

# Meshes
obj_primitives = __path.join(resource_path, 'primitives.obj')
obj_grid3D = __path.join(resource_path, 'grid3D.obj')

# Arena .obj file
obj_arena = __path.join(__data_dir("ratCAVE"), 'arena.obj')
