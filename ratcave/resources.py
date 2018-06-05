import os
from os import path, environ
from glob import glob
from .shader import Shader
from .camera import Camera
from .light import Light

"""
Here are some sample obj files for prototyping your app!
"""

# This is an easy way to get the filepaths of some oft-used resources for displaying simple scenes.

resource_path = path.join(path.split(__file__)[0], '..', 'assets')

# Images
img_uvgrid = path.join(resource_path,'uvgrid.png')
img_colorgrid = path.join(resource_path, 'colorgrid.png')
img_white = path.join(resource_path, 'white.png')

# Meshes
obj_primitives = path.join(resource_path, 'primitives.obj')
obj_grid3D = path.join(resource_path, 'grid3D.obj')


# Shaders
shader_path = path.join(path.split(__file__)[0], '..', 'shaders')

if 'APPVEYOR' not in environ:
    for dirname in os.listdir(shader_path):
        if path.isdir(path.join(shader_path, dirname)):
            vertname = glob(path.join(shader_path, dirname, '*.vert'))[0]
            fragname = glob(path.join(shader_path, dirname, '*.frag'))[0]
            globals()[dirname + '_shader'] = Shader.from_file(vert=path.join(shader_path, vertname),
                                                              frag=path.join(shader_path, fragname),
                                                              lazy=True)



default_camera = Camera()
default_light = Light()
